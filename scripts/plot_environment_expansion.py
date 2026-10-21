#!/usr/bin/env python3
"""Plot audited exploratory results; no LLM runs or invented uncertainty bars."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from interphaise.tools.thermo_dataset import verify_hash


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--results', type=Path, default=ROOT/'data/exploration/environment_expansion_v2/evaluation')
    ap.add_argument('--output', type=Path, default=ROOT/'data/exploration/environment_expansion_v2/landscape.png')
    args = ap.parse_args()
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.colors import Normalize
    names = [('lco_lpscl_4v','Sulfide'),('lco_lic_4v','Chloride'),('lco_llzo_4v','LLZO')]
    packages = []
    summary = json.loads((args.results/'summary.json').read_text()); verify_hash(summary)
    for name, label in names:
        package = json.loads((args.results/(name+'.json')).read_text()); verify_hash(package)
        if package['sha256'] != summary['results_sha256'][name]:
            raise ValueError('Plot inputs differ from audited results')
        packages.append(package)
    fig, (ax, heat) = plt.subplots(1,2,figsize=(12,5.7),gridspec_kw={'width_ratios':[1.15,1]})
    colors = ['#1e6d91','#e39b27','#8054a8']
    for package, (_,label), color in zip(packages,names,colors):
        diag = package['diagnostics']; curve = diag['exact_random_without_replacement'][:11]
        ax.plot([r['evaluations'] for r in curve], [r['probability_acceptable'] for r in curve],
                color=color,lw=2.5,label=f"{label}: {diag['acceptable']}/141 acceptable")
    ax.set(xlabel='Evaluations without replacement',ylabel='Probability of at least one acceptable coating',
           title='The same threshold gives different task difficulty',xlim=(0,10),ylim=(-.02,1.03))
    ax.grid(alpha=.18); ax.legend(loc='lower right',frameon=False,fontsize=9)
    # Illustrative examples selected after exhaustive inspection; not a new ranking.
    formulas = ['LiNbF6','LiTaF6','LiF','Li3PO4','LiAlSiO4','LiClO4']
    values = np.array([[next(r['penalty_bin'] for r in sorted(p['results'],key=lambda r:r['candidate_id'])
                            if r['formula']==f) for p in packages] for f in formulas])
    img = heat.imshow(values,cmap='magma_r',norm=Normalize(0,20),aspect='auto')
    heat.set_xticks(range(3),[label for _,label in names]); heat.set_yticks(range(len(formulas)),formulas)
    heat.set_title('Which chemistry works depends on the electrolyte')
    for i in range(len(formulas)):
        for j in range(3):
            heat.text(j,i,str(values[i,j]),ha='center',va='center',fontsize=12,
                      color='white' if values[i,j]>=9 else '#222222')
    bar = fig.colorbar(img,ax=heat,pad=.03,shrink=.8)
    bar.set_label('Penalty bin (lower is better; color capped at 20)')
    fig.suptitle('Expanded computational screen · LiCoO2 at 4 V · 141 structures per electrolyte',fontsize=14,y=.98)
    fig.text(.5,.065,'Exact random curves, no LLM experiments. Heatmap: illustrative formulas; lowest-ID polymorph for each.',
             ha='center',fontsize=9)
    fig.text(.5,.025,'All three environments retained. Ordered 0 K MP models; no Li-transport, synthesis or interface validation.',
             ha='center',fontsize=9,color='#555555')
    fig.subplots_adjust(top=.85,bottom=.19,wspace=.45)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(args.output,dpi=180)
    print(args.output)


if __name__ == '__main__':
    main()
