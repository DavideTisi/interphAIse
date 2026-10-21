#!/usr/bin/env python3
"""Inspect a completed PET-MAD pilot and save numerical/visual diagnostics."""
import argparse
import json
from pathlib import Path
import numpy as np
from ase.io import read
from ase.data import covalent_radii,chemical_symbols
from ase.data.colors import jmol_colors
from ase.geometry import find_mic
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('calculation',type=Path)
    args=ap.parse_args();root=args.calculation
    initial=read(root/'initial.extxyz');final=read(root/'interface/final.extxyz')
    result=json.loads((root/'result.json').read_text())
    # Labels are inherited from the pymatgen interface in the extxyz arrays.
    labels=initial.arrays['interface_label']
    film=np.where(labels=='film')[0];substrate=np.where(labels=='substrate')[0]
    displacement,lengths=find_mic(final.positions-initial.positions,initial.cell,initial.pbc)
    distances={}
    for name,atoms in [('initial',initial),('final',final)]:
        matrix=atoms.get_all_distances(mic=True)
        cross=matrix[np.ix_(substrate,film)]
        distances[name]={'minimum_cross_contact_distance_A':float(cross.min()),
                         'film_z_span_A':float(np.ptp(atoms.positions[film,2])),
                         'substrate_z_span_A':float(np.ptp(atoms.positions[substrate,2]))}
    inspection={'same_atom_count':len(initial)==len(final),
        'same_cell':bool(np.allclose(initial.cell,final.cell)),
        'same_element_order':bool(np.array_equal(initial.numbers,final.numbers)),
        'max_displacement_A':float(lengths.max()),'rms_displacement_A':float(np.sqrt(np.mean(lengths**2))),
        'geometry':distances,
        'accounting_matches':result['calculator_calls']==sum(r['calculator_calls'] for r in result['relaxations'].values())+
                              sum(r['status']=='ok' for r in json.loads((root/'registry_scan.json').read_text()))}
    (root/'inspection.json').write_text(json.dumps(inspection,indent=2)+'\n')
    fig,axes=plt.subplots(1,3,figsize=(12,6),layout='constrained')
    # Wrapped copies for plotting only: non-orthogonal in-plane cells otherwise put atoms outside the x window.
    shown=[atoms.copy() for atoms in (initial,final)]
    for atoms in shown:atoms.wrap()
    xmax=max(float(atoms.positions[:,0].max()) for atoms in shown)
    for ax,atoms,title in zip(axes[:2],shown,['Initial interface','Relaxed interface']):
        ax.scatter(atoms.positions[:,0],atoms.positions[:,2],c=jmol_colors[atoms.numbers],
                   s=55*covalent_radii[atoms.numbers]**2,edgecolors='#333333',linewidths=.4)
        ax.set(title=title,xlabel='x (Å)',ylabel='z (Å)',aspect='equal')
        ax.set_xlim(-1,xmax+1)
        ax.set_ylim(initial.positions[:,2].min()-2,max(initial.positions[:,2].max(),final.positions[:,2].max())+2)
    handles=[Line2D([0],[0],marker='o',color='w',markerfacecolor=jmol_colors[z],markeredgecolor='#333333',
                    label=chemical_symbols[z]) for z in sorted(set(initial.numbers))]
    axes[0].legend(handles=handles,loc='upper left',bbox_to_anchor=(1.04,1),fontsize=9,frameon=False)
    for name,color in [('interface','#147d92'),('film','#a85030'),('substrate','#7863a0')]:
        rows=[]
        log=root/name/'fire.log'
        if not log.exists():log=root/name/'fire.txt'
        for line in log.read_text().splitlines():
            if line.startswith('FIRE:'):
                fields=line.split();rows.append((int(fields[1]),float(fields[-1])))
        axes[2].plot([r[0] for r in rows],[r[1] for r in rows],label=name,color=color)
    axes[2].axhline(.05,color='black',linestyle='--',linewidth=.8,label='Target 0.05 eV/Å')
    axes[2].set(yscale='log',xlabel='FIRE step',ylabel='Maximum free-atom force (eV/Å)',title='Numerical convergence')
    axes[2].legend(frameon=False,fontsize=9);axes[2].grid(alpha=.2)
    cand=result['selected']['candidate'];miller=lambda m:'('+''.join(str(i) for i in m)+')'
    fig.suptitle(f"PET-MAD S 1.6.0 pilot: {cand['pair'][0]}{miller(cand['substrate_miller'])} | "
                 f"{cand['pair'][1]}{miller(cand['film_miller'])}",fontsize=14)
    fig.savefig(root/'inspection.png',dpi=170)
    print(json.dumps(inspection,indent=2))

if __name__=='__main__':main()
