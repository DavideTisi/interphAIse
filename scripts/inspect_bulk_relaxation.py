#!/usr/bin/env python3
"""Inspect a relax_bulk.py output: lattice change, convergence, and what the symmetry-free
stability check changed (cell, per-element displacement, coordination of framework units)."""
import argparse
import json
from pathlib import Path
import numpy as np
from ase.io import read
from ase.neighborlist import neighbor_list

# Coordination checks: (centre, ligand, cutoff Å) per material.
CHECKS={'LiCoO2':[('Co','O',2.2),('Li','O',2.4)],'Li6PS5Cl':[('P','S',2.4),('Li','S',3.0),('Li','Cl',3.0)],
        'LiNbF6':[('Nb','F',2.2),('Li','F',2.3)],'LiCaAlF6':[('Al','F',2.1),('Li','F',2.3)],
        'LiZr2(PO4)3':[('P','O',1.8),('Zr','O',2.4),('Li','O',2.6)]}


def coordination(atoms,centre,ligand,cutoff):
    i,j=neighbor_list('ij',atoms,cutoff)
    symbols=np.array(atoms.get_chemical_symbols())
    counts=[int(np.sum((i==a)&(symbols[j]==ligand))) for a in np.where(symbols==centre)[0]]
    return {str(n):counts.count(n) for n in sorted(set(counts))}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('root',type=Path)
    root=ap.parse_args().root
    summary=json.loads((root/'summary.json').read_text())
    report={}
    for name,m in summary['materials'].items():
        sym=read(root/name/'symmetric/final.extxyz');check=read(root/name/'stability_check/final.extxyz')
        delta=check.get_scaled_positions(wrap=False)-sym.get_scaled_positions(wrap=False);delta-=np.round(delta)
        disp=np.linalg.norm(delta@check.cell.array,axis=1)
        symbols=np.array(sym.get_chemical_symbols())
        report[name]={'material_id':m['material_id'],'converged':m['symmetric']['converged'],
            'steps':m['symmetric']['steps'],'mp_cellpar':m['mp_cellpar'],'relaxed_cellpar':m['relaxed_cellpar'],
            'lattice_change_percent':m['lattice_change_percent'],'volume_change_percent':m['volume_change_percent'],
            'max_force_eV_A':m['symmetric']['final']['max_force_eV_A'],
            'max_raw_force_eV_A':m['symmetric']['final']['max_raw_force_eV_A'],
            'max_abs_stress_GPa':m['symmetric']['final']['max_abs_stress_GPa'],
            'symmetric_space_group':m['symmetric']['final']['space_group'],
            'stability_check':{'converged':m['stability_check']['converged'],'steps':m['stability_check']['steps'],
                'dE_meV_per_atom':m['stability_dE_meV_per_atom'],
                'space_group':m['stability_check']['final']['space_group'],
                'cellpar':check.cell.cellpar().tolist(),
                'volume_change_vs_symmetric_percent':100*(check.get_volume()/sym.get_volume()-1),
                'displacement_A':{e:{'max':float(disp[symbols==e].max()),'rms':float(np.sqrt((disp[symbols==e]**2).mean()))}
                                  for e in sorted(set(symbols))},
                'coordination':{f'{c}-{l}<{cut}':{'symmetric':coordination(sym,c,l,cut),'check':coordination(check,c,l,cut)}
                                for c,l,cut in CHECKS.get(name,[])}}}
    (root/'inspection.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f"{'material':12s} {'dV% vs MP':>9s} {'conv':>5s} {'stab dE meV/at':>14s} {'SG after check (0.1)':>21s}")
    for name,r in report.items():
        print(f"{name:12s} {r['volume_change_percent']:9.2f} {str(r['converged']):>5s} "
              f"{r['stability_check']['dE_meV_per_atom']:14.3f} {r['stability_check']['space_group']['0.1']:>21s}")

if __name__=='__main__':main()
