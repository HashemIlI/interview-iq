"""LLM-authored Corpus v2 generation, auditing, sharding, and validation.

Dataset engineering only: no training/runtime calls; simulated ASR remains paired.
"""
from __future__ import annotations

import hashlib, json, math, os, random, re, shutil, statistics, subprocess
from collections import Counter, defaultdict
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from interview_iq.decomposition.dataset_builder import build_gold_validation_set, build_kd_dataset
from interview_iq.decomposition.trainer import split_by_question_ids
from interview_iq.decomposition.types import AnnotationRules, CorpusV2AnswerCase, GenerationSource, HumanReview

SEED=42; TARGET_COUNT=1500; SHARD_COUNT=10
REVIEW_STATUS='DRAFT_UNREVIEWED'; PROMPT_VERSION='corpus_v2_codex_1500_v1'
PROVIDER='codex_interactive_generation'; MODEL='not_exposed'
REFDOC_RELATIVE='data/refdocs/reference_docs_250_FINAL_v1.json'
OUTPUT_RELATIVE='results/decomposition_corpus_v2_codex_1500'
CASE_TYPES={'A01':'complete_correct','A02':'concise_correct','A03':'partial_correct','A04':'mixed_correctness','A05':'plausible_misconception','A06':'natural_egyptian_spoken','A07':'long_noisy_multi_claim'}
BASE_SUFFIXES=tuple(f'A{i:02d}' for i in range(1,7))
SECRET_RE=re.compile(r'(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*[\'\"]?[A-Za-z0-9_\-]{12,}')
LATIN_RE=re.compile(r'(?<![\w])(?:[A-Za-z][A-Za-z0-9+#]*(?:[./-][A-Za-z0-9+#]+)*)(?:\s+[A-Za-z][A-Za-z0-9+#]*(?:[./-][A-Za-z0-9+#]+)*)*')
DIACRITICS_RE=re.compile(r'[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]')

class CorpusGenerationError(RuntimeError): pass

def utc_now(): return datetime.now(timezone.utc).isoformat()
def dump_json(path,value):
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def write_jsonl(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(''.join(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n' for r in rows),encoding='utf-8')
def append_jsonl(path,row):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('a',encoding='utf-8',newline='\n') as h: h.write(json.dumps(row,ensure_ascii=False,separators=(',',':'))+'\n')
def load_jsonl(path):
    return [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()] if path.exists() else []
def sha256(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def extract_latin_terms(text):
    seen=set(); out=[]
    for m in LATIN_RE.finditer(text):
        v=m.group(0).strip()
        if v and v not in seen: seen.add(v); out.append(v)
    return out

def rules(): return AnnotationRules(True,True,True,True)

def load_project_state(root):
    examples=build_kd_dataset(root/'results',rules())
    train,val=split_by_question_ids(examples,0.15,SEED)
    qids=sorted({x.question_id for x in examples}); train_ids={x.question_id for x in train}; val_ids={x.question_id for x in val}
    o9={x.question_id for x in build_gold_validation_set(root/'results')}
    docs=json.loads((root/REFDOC_RELATIVE).read_text(encoding='utf-8'))['documents']; by={d['question_id']:d for d in docs}
    if set(qids)-set(by): raise CorpusGenerationError('Eligible D70 IDs missing reference docs')
    if set(qids)&o9 or 'GN-050' in qids: raise CorpusGenerationError('O9 or GN-050 leakage in D70 IDs')
    if train_ids&val_ids or train_ids|val_ids!=set(qids): raise CorpusGenerationError('Invalid grouped D70 split')
    return {'eligible_ids':qids,'train_ids':train_ids,'validation_ids':val_ids,'o9_ids':o9,'docs_by_id':by}

def allocate_plan(root,seed=SEED):
    state=load_project_state(root); qids=state['eligible_ids']; base,extra=divmod(TARGET_COUNT,len(qids))
    if base!=6 or extra>len(qids): raise CorpusGenerationError(f'Unsupported allocation: questions={len(qids)}, base={base}, extra={extra}')
    shuffled=qids[:]; random.Random(seed).shuffle(shuffled); bonus=set(shuffled[:extra]); plan=[]
    for qid in qids:
        d=state['docs_by_id'][qid]; blob=json.dumps([d['question'],d['chunks'],d.get('key_points',[])],ensure_ascii=False)
        for suffix in [*BASE_SUFFIXES,*(['A07'] if qid in bonus else [])]:
            plan.append({'question_id':qid,'track':d['track'],'split':'train' if qid in state['train_ids'] else 'validation','question_text':d['question'],'reference_source':f'{REFDOC_RELATIVE}#{qid}','reference_chunks':d['chunks'],'key_points':d.get('key_points',[]),'technical_terms':extract_latin_terms(blob),'answer_case_id':f'{qid}-{suffix}','case_type':CASE_TYPES[suffix]})
    if len(plan)!=TARGET_COUNT: raise CorpusGenerationError(f'Allocation produced {len(plan)}')
    allocation={'seed':seed,'algorithm':'sort IDs; random.Random(seed).shuffle(copy); first remainder IDs receive A07','eligible_question_count':len(qids),'base_cases_per_question':base,'bonus_question_count':extra,'bonus_case_type':CASE_TYPES['A07'],'bonus_question_ids':sorted(bonus),'expected_total':TARGET_COUNT}
    return plan,allocation

def shard_plan(plan): return [plan[i:i+TARGET_COUNT//SHARD_COUNT] for i in range(0,TARGET_COUNT,TARGET_COUNT//SHARD_COUNT)]

def obj(properties): return {'type':'object','properties':properties,'required':list(properties),'additionalProperties':False}
def pass1_schema(): return obj({'cases':{'type':'array','items':obj({'answer_case_id':{'type':'string'},'answer_original':{'type':'string'},'intended_errors':{'type':'array','items':{'type':'string'}}})}})
def pass2_schema(): return obj({'cases':{'type':'array','items':obj({'answer_case_id':{'type':'string'},'claims':{'type':'array','items':{'type':'string'}},'answer_asr_simulated':{'type':'string'},'asr_simulation_events':{'type':'array','items':{'type':'string'}}})}})
def pass3_schema(): return obj({'audits':{'type':'array','items':obj({'answer_case_id':{'type':'string'},'verdict':{'type':'string','enum':['PASS','FAIL']},'issue_codes':{'type':'array','items':{'type':'string'}},'notes':{'type':'string'}})}})

ANSWER_PROMPT='''# Answer authoring — corpus_v2_codex_1500_v1
You are the LLM author of synthetic Egyptian-Arabic candidate answers from authorized project references. Return exactly every requested answer_case_id.
Rules: natural Egyptian Arabic; preserve English technical terms in Latin script byte-for-byte; never copy reference text or claim human authorship. Cases for one question must differ materially, not be paraphrases. A01 mostly complete/correct. A02 concise/correct and not A01 first claim. A03 correct but clearly incomplete. A04 combines correct and specifically wrong propositions, with varied error position. A05 focused realistic technical misconception. A06 natural varied limited hesitation/filler/self-correction/code-switching without stock openings. A07 long/noisy with 7-8 extractable propositions and correct or mixed detail. Rarely use stock openings بص/باختصار/يعني هو/أنا فاكر إن. intended_errors is [] for A01/A02/A03/A06; describe deliberate errors for A04/A05 and any A07 error. Do not output claims or ASR.'''
CLAIM_PROMPT='''# Claim extraction — corpus_v2_codex_1500_v1
Use answer_original ONLY; no reference is supplied and candidate errors must not be corrected. One atomic self-contained proposition per claim in simplified MSA. Preserve every proposition, error, negation, hedge, uncertainty, and opinion status. Add nothing, omit nothing, add no causal bridge, and deduplicate. Preserve meaningful Latin technical terms byte-for-byte in at least one claim. JSON claims list is authoritative. Corpus must span 1-8 claims; A07 normally 7-8; A02 may be 1-2 and A03 is not always one. Also create meaning-preserving answer_asr_simulated using only limited punctuation removal, hamza normalization, short repetition, word merge/split, or filler deletion; preserve English terms and log events actually applied.'''
AUDIT_PROMPT='''# automated_same_model_audit — corpus_v2_codex_1500_v1
This is separate automated audit, not human review. Audit every record. PASS unless a clear substantive violation exists. FAIL unsupported/missing propositions, non-atomic/non-self-contained claims, term corruption, duplicate claims/answers, case mismatch, implausible misconception, answer/claims mismatch, ASR meaning change, malformed fields, or stock templating. Preserve candidate factual errors; reference is only for case compliance. Concise notes.'''

class CodexCLIProvider:
    def __init__(self,root,out,timeout=1800):
        self.exe=shutil.which('codex'); self.root=root; self.out=out; self.timeout=timeout
        if not self.exe: raise CorpusGenerationError('codex CLI unavailable; cannot claim LLM authoring')
    def generate(self,prompt,schema,name,shard,attempt=0):
        schema_path=self.out/'_work'/'schemas'/f'{name}.json'; dump_json(schema_path,schema)
        raw=self.out/'raw_responses'/f'shard_{shard:03d}_{name}_attempt_{attempt}.json'; raw.parent.mkdir(parents=True,exist_ok=True)
        started=utc_now(); cmd=[self.exe,'exec','--ephemeral','--sandbox','read-only','--cd',str(self.root),'-c','model_reasoning_effort="low"','--color','never','--output-schema',str(schema_path),'-']
        try: cp=subprocess.run(cmd,input=prompt,text=True,encoding='utf-8',errors='replace',capture_output=True,timeout=self.timeout,check=False,env=os.environ.copy())
        except (OSError,subprocess.TimeoutExpired) as exc:
            append_jsonl(self.out/'corpus_v2_codex_1500_generation_log.jsonl',{'timestamp':utc_now(),'pass':name,'shard':shard,'attempt':attempt,'status':'ERROR','error_type':type(exc).__name__}); raise CorpusGenerationError(f'{name} shard {shard} failed safely: {exc}') from exc
        raw.write_text(cp.stdout,encoding='utf-8')
        append_jsonl(self.out/'corpus_v2_codex_1500_generation_log.jsonl',{'started_at':started,'finished_at':utc_now(),'pass':name,'shard':shard,'attempt':attempt,'status':'OK' if cp.returncode==0 else 'ERROR','return_code':cp.returncode,'raw_response':raw.relative_to(self.out).as_posix(),'stderr_sha256':hashlib.sha256(cp.stderr.encode()).hexdigest()})
        if cp.returncode: raise CorpusGenerationError(f'{name} shard {shard} Codex error; see log')
        try: return json.loads(cp.stdout)
        except json.JSONDecodeError as exc: raise CorpusGenerationError(f'{name} shard {shard} malformed JSON') from exc
def rows_by_id(payload,key,expected):
    rows=payload.get(key)
    if not isinstance(rows,list): raise CorpusGenerationError(f'{key} is not a list')
    out={}
    for row in rows:
        if not isinstance(row,dict) or not isinstance(row.get('answer_case_id'),str): raise CorpusGenerationError(f'Malformed {key} row')
        if row['answer_case_id'] in out: raise CorpusGenerationError('Duplicate response ID '+row['answer_case_id'])
        out[row['answer_case_id']]=row
    if set(out)!=expected: raise CorpusGenerationError(f'Response IDs mismatch missing={sorted(expected-set(out))} extra={sorted(set(out)-expected)}')
    return out

def compact_packets(items):
    grouped={}
    for x in items:
        p=grouped.setdefault(x['question_id'],{'question_id':x['question_id'],'track':x['track'],'question_text':x['question_text'],'reference_chunks':x['reference_chunks'],'key_points':x['key_points'],'technical_terms':x['technical_terms'],'requested_cases':[]})
        p['requested_cases'].append({'answer_case_id':x['answer_case_id'],'case_type':x['case_type']})
    return list(grouped.values())
def answer_prompt(items): return ANSWER_PROMPT+'\nINPUT:\n'+json.dumps(compact_packets(items),ensure_ascii=False)
def claim_prompt(answer_rows,item_by_id):
    payload=[{'answer_case_id':r['answer_case_id'],'case_type':item_by_id[r['answer_case_id']]['case_type'],'answer_original':r['answer_original']} for r in answer_rows]
    return CLAIM_PROMPT+'\nINPUT (NO REFERENCE):\n'+json.dumps(payload,ensure_ascii=False)
def audit_prompt(records,item_by_id):
    payload=[]
    for r in records:
        x=item_by_id[r['answer_case_id']]
        payload.append({'answer_case_id':r['answer_case_id'],'case_type':r['case_type'],'question_text':r['question_text'],'reference_chunks':x['reference_chunks'],'answer_original':r['answer_original'],'answer_asr_simulated':r['answer_asr_simulated'],'claims':r['claims'],'intended_errors':r['intended_errors']})
    return AUDIT_PROMPT+'\nINPUT:\n'+json.dumps(payload,ensure_ascii=False)

def compose_records(items,answers,claims,generated_at):
    out=[]
    for x in items:
        cid=x['answer_case_id']; a=answers[cid]; c=claims[cid]
        out.append(CorpusV2AnswerCase(question_id=x['question_id'],track=x['track'],split=x['split'],question_text=x['question_text'],reference_source=x['reference_source'],answer_case_id=cid,case_type=x['case_type'],generation_source=GenerationSource(PROVIDER,MODEL,PROMPT_VERSION,generated_at),answer_original=a['answer_original'].strip(),answer_asr_simulated=c['answer_asr_simulated'].strip(),asr_simulation_events=c['asr_simulation_events'],claims=[v.strip() for v in c['claims']],latin_terms_in_answer=extract_latin_terms(a['answer_original']),latin_terms_in_claims=extract_latin_terms('\n'.join(c['claims'])),intended_errors=a['intended_errors'],automated_audit={},review_status=REVIEW_STATUS,human_review=HumanReview()).to_dict())
    return out

def structural_issues(r):
    issues=[]; claims=r.get('claims')
    if not r.get('answer_original','').strip(): issues.append('empty_answer')
    if not isinstance(claims,list) or not claims or not all(isinstance(c,str) and c.strip() for c in claims): issues.append('malformed_claims'); claims=[]
    if len(claims)!=len(set(claims)): issues.append('duplicate_claims')
    terms=extract_latin_terms(r.get('answer_original','')); asr=r.get('answer_asr_simulated',''); joined='\n'.join(claims)
    ma=[t for t in terms if t not in asr]; mc=[t for t in terms if t not in joined]
    if ma: issues.append('term_corruption_asr:'+'|'.join(ma))
    if mc: issues.append('term_corruption_claims:'+'|'.join(mc))
    if r.get('review_status')!=REVIEW_STATUS: issues.append('invalid_review_status')
    if r.get('generation_source',{}).get('provider')!=PROVIDER: issues.append('invalid_generation_provider')
    if SECRET_RE.search(json.dumps(r,ensure_ascii=False)): issues.append('secret_detected')
    return issues

def _chunks(rows,size=50):
    return [rows[i:i+size] for i in range(0,len(rows),size)]

def generate_shard(provider,items,shard,out,max_repairs=2):
    work=out/'_work'/f'shard_{shard:03d}'; work.mkdir(parents=True,exist_ok=True); expected={x['answer_case_id'] for x in items}; by={x['answer_case_id']:x for x in items}
    p1=work/'pass1_answers.jsonl'; answer_map={r['answer_case_id']:r for r in load_jsonl(p1)}
    for chunk_no,chunk in enumerate(_chunks(items),1):
        chunk_ids={x['answer_case_id'] for x in chunk}
        if chunk_ids<=set(answer_map): continue
        payload=provider.generate(answer_prompt(chunk),pass1_schema(),f'pass1_answers_chunk{chunk_no:02d}',shard)
        answer_map.update(rows_by_id(payload,'cases',chunk_ids)); write_jsonl(p1,[answer_map[x['answer_case_id']] for x in items if x['answer_case_id'] in answer_map])
    if set(answer_map)!=expected: raise CorpusGenerationError(f'Pass1 shard {shard} incomplete after chunks')
    answer_rows=[answer_map[x['answer_case_id']] for x in items]
    p2=work/'pass2_claims.jsonl'; claim_map={r['answer_case_id']:r for r in load_jsonl(p2)}
    for chunk_no,chunk in enumerate(_chunks(items),1):
        chunk_ids={x['answer_case_id'] for x in chunk}
        if chunk_ids<=set(claim_map): continue
        answers=[answer_map[x['answer_case_id']] for x in chunk]
        payload=provider.generate(claim_prompt(answers,by),pass2_schema(),f'pass2_claims_chunk{chunk_no:02d}',shard)
        claim_map.update(rows_by_id(payload,'cases',chunk_ids)); write_jsonl(p2,[claim_map[x['answer_case_id']] for x in items if x['answer_case_id'] in claim_map])
    if set(claim_map)!=expected: raise CorpusGenerationError(f'Pass2 shard {shard} incomplete after chunks')
    records=compose_records(items,answer_map,claim_map,utc_now()); record_map={r['answer_case_id']:r for r in records}
    p3=work/'pass3_audits.jsonl'; audit_map={r['answer_case_id']:r for r in load_jsonl(p3)}
    for chunk_no,chunk in enumerate(_chunks(items),1):
        chunk_ids={x['answer_case_id'] for x in chunk}
        if chunk_ids<=set(audit_map): continue
        subset=[record_map[x['answer_case_id']] for x in chunk]
        payload=provider.generate(audit_prompt(subset,by),pass3_schema(),f'pass3_audit_chunk{chunk_no:02d}',shard)
        audit_map.update(rows_by_id({'rows':payload.get('audits')},'rows',chunk_ids)); write_jsonl(p3,[audit_map[x['answer_case_id']] for x in items if x['answer_case_id'] in audit_map])
    if set(audit_map)!=expected: raise CorpusGenerationError(f'Pass3 shard {shard} incomplete after chunks')
    failing=[]
    for r in records:
        a=audit_map[r['answer_case_id']]; issues=[*a['issue_codes'],*structural_issues(r)]; verdict='PASS' if a['verdict']=='PASS' and not issues else 'FAIL'
        r['automated_audit']={'audit_type':'automated_same_model_audit','verdict':verdict,'issue_codes':issues,'notes':a['notes'],'repair_attempts':a.get('pipeline_repair_attempts',0),'replacement_attempts':a.get('pipeline_replacement_attempts',0)}
        if verdict=='FAIL': failing.append(r['answer_case_id'])
    repairs=0; rejected=0; rejected_path=out/'corpus_v2_codex_1500_rejected.jsonl'
    prior=max((audit_map[c].get('pipeline_repair_attempts',0) for c in failing),default=0)
    for attempt in range(prior+1,max_repairs+1):
        if not failing: break
        failed_items=[by[c] for c in failing]; old={r['answer_case_id']:r for r in records if r['answer_case_id'] in failing}
        for cid in failing: append_jsonl(rejected_path,{'rejected_at':utc_now(),'shard':shard,'repair_attempt':attempt-1,'record':old[cid],'reason':old[cid]['automated_audit']['issue_codes']}); rejected+=1
        na={}
        for chunk_no,chunk in enumerate(_chunks(failed_items,20),1):
            ids={x['answer_case_id'] for x in chunk}; payload=provider.generate(answer_prompt(chunk)+'\nRegenerate failed IDs with materially different content.',pass1_schema(),f'repair{attempt}_answers_chunk{chunk_no:02d}',shard,attempt); na.update(rows_by_id(payload,'cases',ids))
        nar=[na[c] for c in failing]; nc={}
        for chunk_no,chunk in enumerate(_chunks(nar,20),1):
            ids={x['answer_case_id'] for x in chunk}; payload=provider.generate(claim_prompt(chunk,by),pass2_schema(),f'repair{attempt}_claims_chunk{chunk_no:02d}',shard,attempt); nc.update(rows_by_id(payload,'cases',ids))
        replacement=compose_records(failed_items,na,nc,utc_now()); rb={r['answer_case_id']:r for r in replacement}; au={}
        for chunk_no,chunk in enumerate(_chunks(replacement,20),1):
            ids={x['answer_case_id'] for x in chunk}; payload=provider.generate(audit_prompt(chunk,by),pass3_schema(),f'repair{attempt}_audit_chunk{chunk_no:02d}',shard,attempt); au.update(rows_by_id({'rows':payload.get('audits')},'rows',ids))
        for cid in au: au[cid]['pipeline_repair_attempts']=attempt
        nxt=[]
        for cid in failing:
            r=rb[cid]; a=au[cid]; issues=[*a['issue_codes'],*structural_issues(r)]; verdict='PASS' if a['verdict']=='PASS' and not issues else 'FAIL'; r['automated_audit']={'audit_type':'automated_same_model_audit','verdict':verdict,'issue_codes':issues,'notes':a['notes'],'repair_attempts':attempt,'replacement_attempts':0}; repairs+=1
            if verdict=='FAIL': nxt.append(cid)
        records=[rb.get(r['answer_case_id'],r) for r in records]; failing=nxt
        for cid in rb: answer_map[cid]=na[cid]; claim_map[cid]=nc[cid]; audit_map[cid]=au[cid]
        write_jsonl(p1,[answer_map[x['answer_case_id']] for x in items]); write_jsonl(p2,[claim_map[x['answer_case_id']] for x in items]); write_jsonl(p3,[audit_map[x['answer_case_id']] for x in items])
    # Two repair attempts are the hard cap. Persist the terminal failed attempt,
    # then author a genuinely new alternative under the same required ID.
    prior_replacement=max((audit_map[c].get('pipeline_replacement_attempts',0) for c in failing),default=0)
    for cycle in range(prior_replacement+1,6):
        if not failing: break
        failed_items=[by[c] for c in failing]; old={r['answer_case_id']:r for r in records if r['answer_case_id'] in failing}
        feedback=json.dumps([{'answer_case_id':c,'issue_codes':old[c]['automated_audit']['issue_codes'],'notes':old[c]['automated_audit']['notes']} for c in failing],ensure_ascii=False)
        for cid in failing: append_jsonl(rejected_path,{'rejected_at':utc_now(),'shard':shard,'replacement_cycle':cycle,'record':old[cid],'reason':old[cid]['automated_audit']['issue_codes']}); rejected+=1
        na={}
        for chunk_no,chunk in enumerate(_chunks(failed_items,20),1):
            ids={x['answer_case_id'] for x in chunk}; payload=provider.generate(answer_prompt(chunk)+'\nAuthor a brand-new alternative after two failed repairs; keep IDs exactly. Avoid these prior audit failures:\n'+feedback,pass1_schema(),f'replacement{cycle}_answers_chunk{chunk_no:02d}',shard,cycle); na.update(rows_by_id(payload,'cases',ids))
        nar=[na[c] for c in failing]; nc={}
        for chunk_no,chunk in enumerate(_chunks(nar,20),1):
            ids={x['answer_case_id'] for x in chunk}; payload=provider.generate(claim_prompt(chunk,by)+'\nPrior audit feedback about claim extraction to avoid:\n'+feedback,pass2_schema(),f'replacement{cycle}_claims_chunk{chunk_no:02d}',shard,cycle); nc.update(rows_by_id(payload,'cases',ids))
        replacement=compose_records(failed_items,na,nc,utc_now()); rb={r['answer_case_id']:r for r in replacement}; au={}
        for chunk_no,chunk in enumerate(_chunks(replacement,20),1):
            ids={x['answer_case_id'] for x in chunk}; payload=provider.generate(audit_prompt(chunk,by),pass3_schema(),f'replacement{cycle}_audit_chunk{chunk_no:02d}',shard,cycle); au.update(rows_by_id({'rows':payload.get('audits')},'rows',ids))
        nxt=[]
        for cid in failing:
            r=rb[cid]; a=au[cid]; issues=[*a['issue_codes'],*structural_issues(r)]; verdict='PASS' if a['verdict']=='PASS' and not issues else 'FAIL'; r['automated_audit']={'audit_type':'automated_same_model_audit','verdict':verdict,'issue_codes':issues,'notes':a['notes'],'repair_attempts':max_repairs,'replacement_attempts':cycle}; au[cid]['pipeline_repair_attempts']=max_repairs; au[cid]['pipeline_replacement_attempts']=cycle
            if verdict=='FAIL': nxt.append(cid)
        records=[rb.get(r['answer_case_id'],r) for r in records]; failing=nxt
        for cid in rb: answer_map[cid]=na[cid]; claim_map[cid]=nc[cid]; audit_map[cid]=au[cid]
        write_jsonl(p1,[answer_map[x['answer_case_id']] for x in items]); write_jsonl(p2,[claim_map[x['answer_case_id']] for x in items]); write_jsonl(p3,[audit_map[x['answer_case_id']] for x in items])
    if failing: raise CorpusGenerationError(f'Shard {shard} alternatives failed safely: {failing}')
    return records,repairs,rejected
def normalize(text):
    text=DIACRITICS_RE.sub('',text.lower()); text=re.sub(r'[^\w\s]',' ',text,flags=re.UNICODE); return re.sub(r'\s+',' ',text).strip()
def trigram_similarity(a,b):
    def grams(x):
        x='  '+normalize(x)+'  '; return {x[i:i+3] for i in range(max(0,len(x)-2))}
    x,y=grams(a),grams(b); return len(x&y)/len(x|y) if x or y else 1.0
def percentile(values,q):
    if not values:return 0.0
    o=sorted(values); pos=(len(o)-1)*q; lo=math.floor(pos); hi=math.ceil(pos)
    return o[lo] if lo==hi else o[lo]*(hi-pos)+o[hi]*(pos-lo)
def similarity_audit(records):
    groups=defaultdict(list); pairs=[]
    for r in records: groups[r['question_id']].append(r)
    for qid,g in groups.items():
        for i,left in enumerate(g):
            for right in g[i+1:]: pairs.append({'question_id':qid,'left':left['answer_case_id'],'right':right['answer_case_id'],'score':round(trigram_similarity(left['answer_original'],right['answer_original']),6)})
    scores=[p['score'] for p in pairs]; threshold=percentile(scores,.99); near=[p for p in pairs if p['score']>=threshold]
    return {'metric':'character_trigram_jaccard_after_arabic_normalization','threshold_method':'empirical_99th_percentile_of_all_within_question_case_pairs','threshold':round(threshold,6),'pair_count':len(pairs),'distribution':{'min':round(min(scores),6),'p25':round(percentile(scores,.25),6),'median':round(percentile(scores,.5),6),'p75':round(percentile(scores,.75),6),'p90':round(percentile(scores,.9),6),'p95':round(percentile(scores,.95),6),'p99':round(percentile(scores,.99),6),'max':round(max(scores),6)},'near_duplicate_review_tail':near,'near_duplicate_count':len(near)}

def protected_hashes(root,out):
    result={}
    for p in sorted((root/'results').rglob('*')):
        if p.is_file() and out not in p.parents: result[p.relative_to(root).as_posix()]=sha256(p)
    result['decisions.md']=sha256(root/'decisions.md'); return result

def base_manifest(root,out,allocation,plan):
    return {'status':'INCOMPLETE_RESUMABLE','review_status':REVIEW_STATUS,'provenance':'SYNTHETIC','training_approval':'NOT TRAINING-APPROVED','created_at':utc_now(),'updated_at':utc_now(),'target_count':TARGET_COUNT,'shard_count':SHARD_COUNT,'shard_size':TARGET_COUNT//SHARD_COUNT,'allocation':allocation,'question_ids':sorted({x['question_id'] for x in plan}),'generation_source':{'provider':PROVIDER,'model':MODEL,'prompt_version':PROMPT_VERSION},'split_source':'D70 build_kd_dataset + split_by_question_ids(0.15,42)','asr_variant_policy':'paired diagnostic field; never a separate training example','target_rendering_decision':'OPEN; claims JSON list authoritative','similarity_threshold_policy':'empirical p99 after full distribution','protected_file_hashes':protected_hashes(root,out),'completed_shards':[],'resume_command':'py -3.11 scripts/generate_decomposition_corpus_v2_codex_1500.py --resume'}

def validate_corpus(records,plan,state):
    errors=[]; expected={x['answer_case_id']:x for x in plan}; ids=[r.get('answer_case_id') for r in records]
    if len(records)!=TARGET_COUNT: errors.append(f'record_count={len(records)}')
    if len(ids)!=len(set(ids)): errors.append('duplicate_answer_case_id')
    if set(ids)!=set(expected): errors.append('case_id_plan_mismatch')
    if Counter(r['question_id'] for r in records)!=Counter(x['question_id'] for x in plan): errors.append('per_question_allocation_mismatch')
    if {r['question_id'] for r in records}&state['o9_ids']: errors.append('o9_leakage')
    if any(r['question_id']=='GN-050' for r in records): errors.append('gn050_present')
    seen=defaultdict(set); splits=defaultdict(set)
    for r in records:
        qid=r['question_id']; answer=r['answer_original']; splits[qid].add(r['split'])
        if answer in seen[qid]: errors.append('duplicate_answer:'+qid)
        seen[qid].add(answer)
        wanted='train' if qid in state['train_ids'] else 'validation'
        if r['split']!=wanted: errors.append('split_mismatch:'+r['answer_case_id'])
        errors.extend(r['answer_case_id']+':'+x for x in structural_issues(r))
        if r.get('automated_audit',{}).get('verdict')!='PASS': errors.append('audit_not_pass:'+r['answer_case_id'])
        if r.get('human_review')!=asdict(HumanReview()): errors.append('human_review_not_empty:'+r['answer_case_id'])
        if 'example_id' in r or 'variant' in r: errors.append('asr_separate_shape:'+r['answer_case_id'])
    if any(len(x)!=1 for x in splits.values()): errors.append('question_split_leakage')
    if any('local_deterministic' in json.dumps(r) for r in records): errors.append('local_deterministic_source')
    openings=Counter(' '.join(normalize(r['answer_original']).split()[:3]) for r in records)
    if max(openings.values(),default=0)>TARGET_COUNT*.02: errors.append('opening_phrase_over_2_percent')
    sentences=Counter(normalize(re.split(r'[.!؟\n]',r['answer_original'])[0]) for r in records)
    if max(sentences.values(),default=0)>TARGET_COUNT*.01: errors.append('exact_sentence_pattern_over_1_percent')
    cc=[len(r['claims']) for r in records]
    if not cc or min(cc)>1 or max(cc)<8: errors.append('claim_count_range_missing_1_to_8')
    return sorted(set(errors))

def audit_summary(records,similarity,repairs,rejected,unchanged):
    cc=[len(r['claims']) for r in records]; lengths=[len(r['answer_original'].split()) for r in records]; openings=Counter(' '.join(normalize(r['answer_original']).split()[:3]) for r in records); sentences=Counter(normalize(re.split(r'[.!؟\n]',r['answer_original'])[0]) for r in records)
    return {'verdict':'DATASET GENERATION PIPELINE PASS','status':REVIEW_STATUS,'provenance':'SYNTHETIC','training_approval':'NOT TRAINING-APPROVED','record_count':len(records),'question_count':len({r['question_id'] for r in records}),'by_track':dict(sorted(Counter(r['track'] for r in records).items())),'by_split':dict(sorted(Counter(r['split'] for r in records).items())),'by_case_type':dict(sorted(Counter(r['case_type'] for r in records).items())),'claim_count_distribution':dict(sorted(Counter(cc).items())),'claims_total':sum(cc),'claims_mean':statistics.mean(cc),'claims_median':statistics.median(cc),'answer_word_length_distribution':{'short_le_20':sum(v<=20 for v in lengths),'medium_21_50':sum(21<=v<=50 for v in lengths),'long_gt_50':sum(v>50 for v in lengths)},'latin_term_occurrences_in_answers':sum(len(r['latin_terms_in_answer']) for r in records),'latin_term_occurrences_in_claims':sum(len(r['latin_terms_in_claims']) for r in records),'term_corruption_count':sum(any(c.startswith('term_corruption') for c in r['automated_audit']['issue_codes']) for r in records),'automated_repairs':repairs,'rejected_attempts':rejected,'exact_duplicate_answer_count':0,'similarity':similarity,'opening_phrase_max_count':max(openings.values(),default=0),'opening_phrase_max_fraction':max(openings.values(),default=0)/len(records),'exact_first_sentence_max_count':max(sentences.values(),default=0),'exact_first_sentence_max_fraction':max(sentences.values(),default=0)/len(records),'protected_old_files_unchanged':unchanged,'audit_type':'automated_same_model_audit','human_review_performed':False}

def write_static_files(out):
    prompts=out/'prompts'; prompts.mkdir(parents=True,exist_ok=True)
    (prompts/'answer_generation_v1.md').write_text(ANSWER_PROMPT,encoding='utf-8'); (prompts/'claim_extraction_v1.md').write_text(CLAIM_PROMPT,encoding='utf-8'); (prompts/'automated_audit_v1.md').write_text(AUDIT_PROMPT,encoding='utf-8')
    (out/'README.md').write_text('# Decomposition Corpus v2 — Codex 1500\n\nExactly 1,500 canonical synthetic cases from D70-eligible questions. ASR is paired diagnostic data; claims are authoritative JSON lists.\n\nStatus: `DRAFT_UNREVIEWED / SYNTHETIC / NOT TRAINING-APPROVED`.\n\nResume: `py -3.11 scripts/generate_decomposition_corpus_v2_codex_1500.py --resume`.\n',encoding='utf-8')
def write_audit_md(path,a):
    path.write_text(f"# Corpus v2 Codex 1500 — automated audit\n\n- Verdict: {a['verdict']}\n- Status: {a['status']} / {a['provenance']} / {a['training_approval']}\n- Records: {a['record_count']}\n- Questions: {a['question_count']}\n- Claims: {a['claims_total']} (mean {a['claims_mean']:.3f}, median {a['claims_median']})\n- Automated repairs: {a['automated_repairs']}\n- Rejected attempts: {a['rejected_attempts']}\n- Near-duplicate review-tail: {a['similarity']['near_duplicate_count']} at empirical p99={a['similarity']['threshold']}\n- Term corruptions accepted: {a['term_corruption_count']}\n- Protected old files unchanged: {a['protected_old_files_unchanged']}\n\nSame-model automated audit only; no human review or training approval.\n",encoding='utf-8')

def build_corpus(repo_root,output_dir=None,resume=True):
    root=repo_root.resolve(); out=(output_dir or root/OUTPUT_RELATIVE).resolve(); out.mkdir(parents=True,exist_ok=True); (out/'shards').mkdir(exist_ok=True); write_static_files(out)
    rejected_path=out/'corpus_v2_codex_1500_rejected.jsonl'
    if not rejected_path.exists(): rejected_path.write_text('',encoding='utf-8')
    plan,allocation=allocate_plan(root); state=load_project_state(root); manifest_path=out/'corpus_v2_codex_1500_manifest.json'
    if manifest_path.exists() and resume:
        manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
        if manifest.get('allocation')!=allocation: raise CorpusGenerationError('Unsafe resume: allocation differs')
    else: manifest=base_manifest(root,out,allocation,plan); dump_json(manifest_path,manifest)
    provider=CodexCLIProvider(root,out); all_records=[]; total_repairs=0; initial_rejected=len(load_jsonl(rejected_path))
    try:
        for number,items in enumerate(shard_plan(plan),1):
            path=out/'shards'/f'corpus_v2_shard_{number:03d}_DRAFT_UNREVIEWED.jsonl'; existing=load_jsonl(path) if resume else []; expected={x['answer_case_id'] for x in items}
            if len(existing)==len(items) and {r.get('answer_case_id') for r in existing}==expected: records=existing
            else:
                records,repairs,_=generate_shard(provider,items,number,out); write_jsonl(path,records); total_repairs+=repairs
            all_records.extend(records); manifest.update({'status':'INCOMPLETE_RESUMABLE','updated_at':utc_now(),'completed_shards':list(range(1,number+1)),'completed_record_count':len(all_records)}); dump_json(manifest_path,manifest)
    except Exception:
        manifest.update({'status':'INCOMPLETE_RESUMABLE','updated_at':utc_now(),'completed_record_count':len(all_records)}); dump_json(manifest_path,manifest); raise
    final=out/'corpus_v2_codex_1500_DRAFT_UNREVIEWED.jsonl'; write_jsonl(final,all_records); errors=validate_corpus(all_records,plan,state); similarity=similarity_audit(all_records); unchanged=manifest['protected_file_hashes']==protected_hashes(root,out)
    if not unchanged: errors.append('protected_old_file_mutation')
    if errors:
        manifest.update({'status':'INCOMPLETE_RESUMABLE','updated_at':utc_now(),'validation_errors':sorted(set(errors))}); dump_json(manifest_path,manifest); raise CorpusGenerationError('Final guards failed: '+', '.join(sorted(set(errors))))
    rejected=len(load_jsonl(rejected_path)); total_repairs=sum(r['automated_audit']['repair_attempts'] for r in all_records); audit=audit_summary(all_records,similarity,total_repairs,rejected,unchanged); dump_json(out/'corpus_v2_codex_1500_audit.json',audit); write_audit_md(out/'corpus_v2_codex_1500_audit.md',audit)
    manifest.update({'status':'COMPLETE_DRAFT_UNREVIEWED','updated_at':utc_now(),'completed_record_count':len(all_records),'completed_shards':list(range(1,11)),'final_corpus_sha256':sha256(final),'similarity_threshold':similarity['threshold'],'similarity_threshold_method':similarity['threshold_method'],'audit_file':'corpus_v2_codex_1500_audit.json'}); dump_json(manifest_path,manifest); return audit
