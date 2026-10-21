#!/usr/bin/env python3
"""Plot audited production acceptance, Wilson intervals and exact random references.

No API calls. Input is the independent review JSON; original production archives
remain on the experiment branch until integration. Run from the repo root:
  python scripts/plot_environment_review.py
"""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
ARMS=['iterative','sequential','shuffled','upfront','random']
COLORS=['#2a78d6','#1baf7a','#cc63a4','#d69a00','#eb6834']
ENVIRONMENTS=[('Li6PS5Cl','Sulfide · Li₆PS₅Cl'),('Li3InCl6','Chloride · Li₃InCl₆'),('Li7La3Zr2O12','LLZO · Li₇La₃Zr₂O₁₂')]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,default=ROOT/'data/reviews/environment_results_review_20261021.json')
    parser.add_argument('--output',type=Path,default=ROOT/'figures/environment_acceptance_review_20261021')
    args=parser.parse_args()
    data=json.loads(args.input.read_text())
    assert data['complete_runs']==450 and data['holm_family_size']==6 and data['production_check']==[]
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.fonttype':'none'})
    fig,axes=plt.subplots(1,3,figsize=(14,5.5),sharey=True)
    fig.subplots_adjust(left=.07,right=.985,top=.74,bottom=.25,wspace=.18)
    fig.suptitle('Feedback helps in sulfide; random search leads in LLZO',x=.07,ha='left',y=.97,fontsize=19,fontweight='bold')
    fig.text(.07,.89,'Acceptable coating found within 10 queries · 30 runs per arm and environment',fontsize=12,color='#4b5563')
    for ax,(env,title) in zip(axes,ENVIRONMENTS):
        e=data['environments'][env];rates=np.array([e['arms'][a]['acceptable_rate']*100 for a in ARMS])
        bounds=np.array([e['arms'][a]['acceptable_wilson95'] for a in ARMS])*100
        ax.bar(range(5),rates,color=COLORS,width=.65,zorder=3)
        ax.errorbar(range(5),rates,yerr=[rates-bounds[:,0],bounds[:,1]-rates],fmt='none',ecolor='#374151',capsize=3,linewidth=1,zorder=4)
        for i,arm in enumerate(ARMS):
            ax.text(i,max(bounds[i,1]+3,7),f"{e['arms'][arm]['acceptable']}/30",ha='center',va='bottom',fontsize=10,fontweight='bold')
        ax.axhline(e['random_exact_by_10']*100,color='#2d3748',linestyle=(0,(4,3)),linewidth=1.3,zorder=2)
        ax.set_title(title,loc='left',fontsize=13,fontweight='bold',pad=16)
        ax.set_xticks(range(5),['Iterative','Sequential','Shuffled','Upfront','Random'],rotation=32,ha='right')
        ax.set_ylim(0,116);ax.set_yticks([0,25,50,75,100]);ax.set_axisbelow(True);ax.yaxis.grid(color='#e5e7eb',linewidth=.7)
        for side in ('top','right','left'):ax.spines[side].set_visible(False)
        ax.spines['bottom'].set_color('#cbd5e1');ax.tick_params(axis='both',length=0)
        ax.text(0,-.26,f"Exact random: {e['random_exact_by_10']:.1%}  ·  {e['acceptable_candidates']}/{e['pool_size']} acceptable",transform=ax.transAxes,fontsize=10,color='#4b5563')
    axes[0].set_ylabel('Success rate (%)',labelpad=10)
    fig.text(.07,.06,'Whiskers: 95% Wilson intervals. Dashed lines: exact random success without replacement.',fontsize=10,color='#4b5563')
    fig.text(.07,.015,'Primary Holm tests: sulfide iterative > sequential and shuffled; LLZO iterative > sequential only. Random comparisons are descriptive.',fontsize=9.5,color='#4b5563')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    for extension in ('png','svg'):
        path=args.output.with_suffix('.'+extension);fig.savefig(path,dpi=180,facecolor='white')
        if extension=='svg':
            path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
        print(path)
    plt.close(fig)


if __name__=='__main__':main()
