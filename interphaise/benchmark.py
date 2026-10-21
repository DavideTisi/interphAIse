"""Budgeted query boundary for Adem's agent; never exposes unqueried outcomes.

This is an application-level information boundary, not a security sandbox. The
experiment runner must keep benchmark files and diagnostic reports out of prompts.
"""
from copy import deepcopy
import json
from pathlib import Path

from .tools.thermo_dataset import digest, verify_hash


class BenchmarkQueries:
    def __init__(self, pool_path, benchmark_path, *, budget, allow_draft=False):
        pool=json.loads(Path(pool_path).read_text())
        benchmark=json.loads(Path(benchmark_path).read_text())
        verify_hash(pool); verify_hash(benchmark)
        if benchmark['objective_sha256'] != digest(benchmark['objective']):
            raise ValueError('Objective hash mismatch')
        if benchmark['pool_sha256']!=pool['sha256']:
            raise ValueError('Pool/benchmark mismatch')
        if benchmark['status']!='frozen' and not allow_draft:
            raise ValueError('Draft benchmark: scientific review required before experiments')
        candidates={c['candidate_id']:c for c in pool['candidates']}
        results={r['candidate_id']:r for r in benchmark['results']}
        if len(candidates)!=len(pool['candidates']) or len(results)!=len(benchmark['results']) or set(candidates)!=set(results):
            raise ValueError('Benchmark must contain exactly one result per candidate')
        if not isinstance(budget,int) or isinstance(budget,bool) or not 1<=budget<=len(candidates):
            raise ValueError('Invalid query budget')
        self._results=results
        self._public=[{key:c[key] for key in ('candidate_id','formula','family')} for c in candidates.values()]
        self._task={key:deepcopy(benchmark[key]) for key in
                    ('objective','objective_sha256','pool_sha256','endpoints','voltage_V')}
        self._task['benchmark_sha256']=benchmark['sha256']
        self._task['instructions'] = (
            'Require status ok and insulation. Minimize nonnegative penalty_bin; '
            'candidates in the same bin tie. Penalty is measured in eV/non-Li atom. '
            'Acceptability describes the coating criterion, not whole-stack stability. '
            'Each query consumes one evaluation, including failed or repeated candidates.')
        self._budget=budget
        self._history=[]

    @property
    def remaining(self):
        return self._budget-len(self._history)

    def task(self):
        return deepcopy(self._task)

    def available(self):
        seen={item['candidate_id'] for item in self._history}
        return deepcopy([c for c in self._public if c['candidate_id'] not in seen])

    def history(self):
        return deepcopy(self._history)

    def query(self,candidate_id):
        if self.remaining<=0:
            raise ValueError('Query budget exhausted')
        if not isinstance(candidate_id,str):
            result={'candidate_id':None,'status':'failed','error':'Candidate ID must be a string'}
        elif candidate_id not in self._results:
            result={'candidate_id':candidate_id,'status':'failed','error':'Unknown candidate ID'}
        elif any(r['candidate_id']==candidate_id for r in self._history):
            result={'candidate_id':candidate_id,'status':'failed','error':'Candidate already queried'}
        else:
            result=deepcopy(self._results[candidate_id])
        # Calculation failures and invalid/repeated IDs consume an attempt.
        self._history.append(deepcopy(result))
        return result
