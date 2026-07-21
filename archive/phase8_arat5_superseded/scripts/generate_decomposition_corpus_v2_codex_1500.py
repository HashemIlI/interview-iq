"""Generate/resume the DRAFT_UNREVIEWED 1,500-case Codex-authored corpus."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from interview_iq.decomposition.corpus_v2_codex import CorpusGenerationError, build_corpus

def main():
    p=argparse.ArgumentParser(); p.add_argument('--output-dir',type=Path,default=ROOT/'results'/'decomposition_corpus_v2_codex_1500'); p.add_argument('--resume',action=argparse.BooleanOptionalAction,default=True); args=p.parse_args()
    try: audit=build_corpus(ROOT,args.output_dir,args.resume)
    except (CorpusGenerationError,OSError,ValueError) as exc:
        print(f'INCOMPLETE_RESUMABLE: {exc}',file=sys.stderr); print(f'Resume: py -3.11 {Path(__file__).name} --resume',file=sys.stderr); return 1
    print(json.dumps(audit,ensure_ascii=False,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())