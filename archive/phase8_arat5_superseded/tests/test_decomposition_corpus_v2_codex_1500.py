from __future__ import annotations
import json
from collections import Counter,defaultdict
from pathlib import Path
from types import SimpleNamespace
import pytest
from interview_iq.decomposition import corpus_v2_codex as c

ROOT=Path(__file__).parents[1]; OUT=ROOT/'results'/'decomposition_corpus_v2_codex_1500'; CORPUS=OUT/'corpus_v2_codex_1500_DRAFT_UNREVIEWED.jsonl'

@pytest.fixture(scope='module')
def records(): return c.load_jsonl(CORPUS)

def test_deterministic_1500_allocation_seed_42():
    one,a=c.allocate_plan(ROOT,42); two,b=c.allocate_plan(ROOT,42)
    assert one==two and a==b; assert len(one)==1500; assert a['eligible_question_count']==222; assert a['bonus_question_count']==168
    counts=Counter(x['question_id'] for x in one); assert Counter(counts.values())=={7:168,6:54}
    assert [len(x) for x in c.shard_plan(one)]==[150]*10

def test_final_counts_uniqueness_and_case_types(records):
    assert len(records)==1500; assert len({r['answer_case_id'] for r in records})==1500; assert len({r['question_id'] for r in records})==222
    assert Counter(r['case_type'] for r in records)=={'complete_correct':222,'concise_correct':222,'partial_correct':222,'mixed_correctness':222,'plausible_misconception':222,'natural_egyptian_spoken':222,'long_noisy_multi_claim':168}
    grouped=defaultdict(list)
    for r in records: grouped[r['question_id']].append(r)
    assert Counter(map(len,grouped.values()))=={7:168,6:54}
    assert all(len({r['answer_original'] for r in rows})==len(rows) for rows in grouped.values())

def test_question_track_balance_grouped_split_and_exclusions(records):
    qtrack={r['question_id']:r['track'] for r in records}; assert Counter(qtrack.values())=={'CS':45,'DA':45,'DS':44,'GN':44,'SE':44}
    state=c.load_project_state(ROOT); qids=set(qtrack); assert qids.isdisjoint(state['o9_ids']); assert 'GN-050' not in qids
    splits=defaultdict(set)
    for r in records: splits[r['question_id']].add(r['split'])
    assert all(len(v)==1 for v in splits.values()); assert all(next(iter(v))==('train' if q in state['train_ids'] else 'validation') for q,v in splits.items())

def test_claims_terms_status_and_provenance(records):
    for r in records:
        assert r['review_status']=='DRAFT_UNREVIEWED'
        assert r['generation_source']['provider']=='codex_interactive_generation'; assert r['generation_source']['model']=='not_exposed'; assert 'local_deterministic' not in json.dumps(r)
        assert isinstance(r['claims'],list) and r['claims'] and all(isinstance(x,str) and x for x in r['claims'])
        assert r['latin_terms_in_answer']==c.extract_latin_terms(r['answer_original']); assert r['latin_terms_in_claims']==c.extract_latin_terms('\n'.join(r['claims']))
        assert all(t in r['answer_asr_simulated'] for t in r['latin_terms_in_answer']); assert all(t in '\n'.join(r['claims']) for t in r['latin_terms_in_answer'])
        assert r['automated_audit']['audit_type']=='automated_same_model_audit'; assert r['automated_audit']['verdict']=='PASS'; assert all(v is None for v in r['human_review'].values())
        assert 'example_id' not in r and 'variant' not in r

def test_claim_range_and_exact_ten_shard_merge(records):
    counts=[len(r['claims']) for r in records]; assert min(counts)==1 and max(counts)>=8
    shards=sorted((OUT/'shards').glob('corpus_v2_shard_*_DRAFT_UNREVIEWED.jsonl')); assert len(shards)==10
    merged=[]
    for p in shards: rows=c.load_jsonl(p); assert len(rows)==150; merged.extend(rows)
    assert merged==records

def test_manifest_audit_and_old_files_unchanged():
    m=json.loads((OUT/'corpus_v2_codex_1500_manifest.json').read_text(encoding='utf-8')); a=json.loads((OUT/'corpus_v2_codex_1500_audit.json').read_text(encoding='utf-8'))
    assert m['status']=='COMPLETE_DRAFT_UNREVIEWED'; assert m['completed_shards']==list(range(1,11)); assert m['asr_variant_policy'].startswith('paired diagnostic')
    assert a['verdict']=='DATASET GENERATION PIPELINE PASS'; assert a['record_count']==1500; assert a['protected_old_files_unchanged'] is True; assert a['term_corruption_count']==0
    assert m['protected_file_hashes']==c.protected_hashes(ROOT,OUT); assert a['similarity']['threshold_method'].startswith('empirical_99th')

def test_safe_failure_on_codex_error(tmp_path,monkeypatch):
    monkeypatch.setattr(c.shutil,'which',lambda _: 'codex')
    monkeypatch.setattr(c.subprocess,'run',lambda *a,**k: SimpleNamespace(returncode=1,stdout='',stderr='simulated'))
    provider=c.CodexCLIProvider(ROOT,tmp_path)
    with pytest.raises(c.CorpusGenerationError,match='Codex error'): provider.generate('x',c.pass1_schema(),'pass1',1)
    assert c.load_jsonl(tmp_path/'corpus_v2_codex_1500_generation_log.jsonl')[0]['status']=='ERROR'

def test_repair_rejection_and_resume_without_duplicate_calls(tmp_path):
    item={'question_id':'DA-999','track':'DA','split':'train','question_text':'سؤال','reference_source':'ref','reference_chunks':['مرجع'],'key_points':[],'technical_terms':[],'answer_case_id':'DA-999-A01','case_type':'complete_correct'}
    class Fake:
        def __init__(self): self.calls=[]
        def generate(self,prompt,schema,name,shard,attempt=0):
            self.calls.append(name)
            if name.startswith('pass1_answers') or name.startswith('repair1_answers'): return {'cases':[{'answer_case_id':'DA-999-A01','answer_original':'الإجابة فيها معلومة واضحة.','intended_errors':[]}]}
            if name.startswith('pass2_claims') or name.startswith('repair1_claims'): return {'cases':[{'answer_case_id':'DA-999-A01','claims':['تحتوي الإجابة على معلومة واضحة.'],'answer_asr_simulated':'الاجابة فيها معلومة واضحة','asr_simulation_events':['punctuation_removed','hamza_normalized']}]}
            verdict='FAIL' if name.startswith('pass3_audit') else 'PASS'; return {'audits':[{'answer_case_id':'DA-999-A01','verdict':verdict,'issue_codes':['forced_test_failure'] if verdict=='FAIL' else [],'notes':'test'}]}
    fake=Fake(); rows,repairs,rejected=c.generate_shard(fake,[item],1,tmp_path); assert len(rows)==1 and repairs==1 and rejected==1; assert len(c.load_jsonl(tmp_path/'corpus_v2_codex_1500_rejected.jsonl'))==1
    before=len(fake.calls); rows2,repairs2,rejected2=c.generate_shard(fake,[item],1,tmp_path); assert len(fake.calls)==before; assert len(rows2)==1 and repairs2==0 and rejected2==0