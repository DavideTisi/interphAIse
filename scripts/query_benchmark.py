#!/usr/bin/env python3
"""Small offline integration run; uses frozen data and no LLM/API calls."""
import argparse
import json
from pathlib import Path
import random
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from interphaise.benchmark import BenchmarkQueries
from interphaise.discovery_evaluator import ranking_key


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--pool',type=Path,default=ROOT/'data/pools/mp_candidates_v2.json')
    ap.add_argument('--benchmark',type=Path,default=ROOT/'data/benchmarks/coating_v3.json')
    ap.add_argument('--budget',type=int,default=3)
    ap.add_argument('--seed',type=int,default=0)
    ap.add_argument('--output',type=Path,default=ROOT/'runs/v3_query_smoke.json')
    args=ap.parse_args()
    if args.output.exists():ap.error('Output exists; choose a new path')
    query=BenchmarkQueries(args.pool,args.benchmark,budget=args.budget)
    rng=random.Random(args.seed)
    trace=[];best=None
    while query.remaining:
        candidate=rng.choice(query.available())
        result=query.query(candidate['candidate_id'])
        if best is None or ranking_key(result)>ranking_key(best):best=result
        trace.append({'evaluation':len(trace)+1,'candidate_id':candidate['candidate_id'],
                      'best_candidate_id':best['candidate_id'],'best_rank':ranking_key(best)})
    state={'strategy':'random','seed':args.seed,'budget':args.budget,'task':query.task(),
           'history':query.history(),'trace':trace,'status':'complete'}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(state,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'status':state['status'],'evaluations':len(trace),'output':str(args.output)}))

if __name__=='__main__':main()
