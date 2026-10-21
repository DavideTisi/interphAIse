#!/usr/bin/env python3
"""Plot evaluator diagnostics only; no LLM strategy outcomes."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]

def main():
    old=json.loads((ROOT/'data/benchmarks/coating_v2_diagnostic.json').read_text())
    new=json.loads((ROOT/'data/benchmarks/coating_v3.json').read_text())
    values=sorted(r['penalty'] for r in new['results'] if r['status']=='ok' and r['insulating'])
    plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,2,figsize=(11,4.8),layout='constrained')
    axes[0].plot(range(1,len(values)+1),values,'o-',color='#147d92',markersize=4)
    axes[0].axhline(.05,color='#a85030',linestyle='--',label='Coating threshold: 0.05')
    axes[0].set(yscale='log',xlabel='Eligible candidate, sorted by penalty',
                ylabel='V3 penalty (eV/non-Li atom)',title='V3: 47 eligible, 24 score bins')
    axes[0].legend(loc='upper left',frameon=False,fontsize=9)
    for data,label,color in [(old,'V2: 41 candidates tie for best','#9e6c4f'),
                             (new,'V3: 1 candidate in best bin','#147d92')]:
        curve=data['diagnostics']['random_best_bin_success'][:11]
        axes[1].plot([r['evaluations'] for r in curve],
                     [100*r['probability_find_best_bin'] for r in curve],
                     'o-',label=label,color=color,markersize=4)
    axes[1].set(xlabel='Uniform random evaluations (without replacement)',
                ylabel='Probability of finding best bin (%)',ylim=(-2,104),
                title='Exact random baseline, full 50-candidate pool')
    axes[1].legend(loc='center right',frameon=False,fontsize=9)
    for ax in axes:ax.grid(alpha=.18)
    fig.suptitle('Evaluator validation before LLM experiments',fontsize=15)
    fig.savefig(ROOT/'data/benchmarks/validation.png',dpi=180)

if __name__=='__main__':main()
