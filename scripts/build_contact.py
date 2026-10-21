#!/usr/bin/env python3
"""Build one sharp contact with an explicitly chosen termination and record full provenance.

Output is compatible with run_petmad_interface.py (interface.json, selected.json) plus
build.json: input hashes, ZSL transformations and strain, cut shifts, slab composition,
surface chemistry, cut framework polyhedra, formal polarity and the fixed-atom count.
With --parent (the symmetric bulk the substrate was relaxed from, same atom order), each
surface is also described by the parent Miller heights of its framework layers, which is
how equivalent cuts are matched across different relaxed minima.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import numpy as np
from ase.io import read,write
from monty.json import MontyEncoder
from pymatgen.io.ase import AseAtomsAdaptor
from interphaise.tools.energetics import to_atoms,bottom_fixed_indices
from interphaise.tools.matcher import enumerate_interfaces,MatchSettings
from interphaise.tools.validation import validate,oxidation_map,slab_charge_and_dipole

# Framework polyhedra whose cutting is reported: (centre, ligand, cutoff Å, bulk coordination).
POLYHEDRA={'Li6PS5Cl':[('P','S',2.4,4)],'LiCoO2':[('Co','O',2.2,6)],'LiNbF6':[('Nb','F',2.2,6)],
           'LiCaAlF6':[('Al','F',2.1,6)],'LiZr2(PO4)3':[('P','O',1.8,4),('Zr','O',2.4,6)]}


def sha256(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def cut_polyhedra(slab,formula):
    out={}
    for centre,ligand,cutoff,bulk in POLYHEDRA.get(formula,[]):
        counts=[sum(1 for n in slab.get_neighbors(site,cutoff) if n.specie.symbol==ligand)
                for site in slab if site.specie.symbol==centre]
        out[f'{centre}{ligand}{bulk}']=sum(c<bulk for c in counts)
    return out


def z_layers(slab,side,n=3,gap=.5):
    """All-species atomic layers (z clusters split at gaps > ``gap`` Å), counted from one surface."""
    order=np.argsort([-s.coords[2] for s in slab]) if side=='top' else np.argsort([s.coords[2] for s in slab])
    out=[];last=None
    for k in order:
        z=slab[k].coords[2]
        if last is None or abs(z-last)>gap:
            if len(out)==n:break
            out.append(collections.Counter())
        out[-1][slab[k].specie.symbol]+=1;last=z
    return [dict(sorted(c.items())) for c in out]


def framework_layers(slab,heights,side,n=3):
    """Framework (non-Li) groups by (species, parent Miller height), ranked by mean z from one surface.

    Window-free, so the same cut of the parent framework gives the same signature even when
    the relaxed minima differ in strain and Li/Cl positions.
    """
    groups=collections.defaultdict(list)
    for site in slab:
        if site.specie.symbol!='Li':
            groups[(site.specie.symbol,round(float(heights[site.properties['bulk_index']]),2))].append(site.coords[2])
    ranked=sorted(groups.items(),key=lambda kv:np.mean(kv[1]),reverse=(side=='top'))
    return [{'species':k[0],'parent_height':k[1],'count':len(z)} for k,z in ranked[:n]]


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('substrate',type=Path);ap.add_argument('film',type=Path)
    ap.add_argument('--names',nargs=2,required=True,metavar=('SUBSTRATE','FILM'))
    ap.add_argument('--substrate-miller',type=int,nargs=3,required=True)
    ap.add_argument('--film-miller',type=int,nargs=3,required=True)
    ap.add_argument('--termination',nargs=2,required=True,metavar=('FILM','SUBSTRATE'),help='pymatgen termination labels')
    ap.add_argument('--parent',type=Path,help='Symmetric parent bulk of the substrate (same atom order)')
    ap.add_argument('--max-area',type=float,default=300);ap.add_argument('--max-atoms',type=int,default=512)
    ap.add_argument('--film-layers',type=int,default=2);ap.add_argument('--substrate-layers',type=int,default=2)
    ap.add_argument('--label',required=True);ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    if args.output.exists():ap.error('Use a fresh output directory')
    sname,fname=args.names
    s=AseAtomsAdaptor.get_structure(read(args.substrate));f=AseAtomsAdaptor.get_structure(read(args.film))
    s.add_site_property('bulk_index',list(range(len(s))));f.add_site_property('bulk_index',[-1]*len(f))
    heights=None
    if args.parent:
        parent=read(args.parent)
        if parent.get_chemical_symbols()!=[site.specie.symbol for site in s]:raise SystemExit('Parent atom order differs')
        # Height of each parent site along the substrate Miller direction, modulo one interplanar period.
        heights=np.round((parent.get_scaled_positions()@np.array(args.substrate_miller))%1,3)%1
    settings=MatchSettings(max_area=args.max_area,max_length_tol=.05,max_angle_tol=.03,film_thickness=args.film_layers,substrate_thickness=args.substrate_layers,max_candidates=60)
    report={}
    pairs=enumerate_interfaces(s,f,tuple(args.substrate_miller),tuple(args.film_miller),(sname,fname),settings,
                               terminations=[tuple(args.termination)],report=report)
    valid=[]
    for c,i in pairs:
        ok,reject,warn=validate(c,i,max_atoms=args.max_atoms,max_strain=.06,film_oxi=oxidation_map(f),substrate_oxi=oxidation_map(s),
                                film_formula=fname,substrate_formula=sname)
        if ok:valid.append((c,i,warn))
    if not valid:raise SystemExit(f'No valid interface for {args.termination}; enumeration report {report}')
    c,i,warn=min(valid,key=lambda v:(v[0].n_atoms,v[0].von_mises_strain))
    film=i.film;sub=i.substrate
    sides={}
    for name,slab,formula in (('film',film,fname),('substrate',sub,sname)):
        charge,dipole=slab_charge_and_dipole(slab,oxidation_map(formula))
        contact,far=('top','bottom') if name=='substrate' else ('bottom','top')
        sides[name]={'formula':slab.composition.formula,'n_atoms':len(slab),'formal_charge':charge,
                     'formal_dipole_per_area_e_per_A':abs(dipole)/c.area,'cut_polyhedra':cut_polyhedra(slab,formula),
                     'contact_side_layers':z_layers(slab,contact),'far_side_layers':z_layers(slab,far)}
        if name=='substrate' and heights is not None:
            sides[name]['contact_side_framework']=framework_layers(slab,heights,contact)
            sides[name]['far_side_framework']=framework_layers(slab,heights,far)
    atoms=to_atoms(i)
    fixed=bottom_fixed_indices(atoms,i.substrate_indices)
    props=i.interface_properties
    build={'label':args.label,'contact':f'{sname}{tuple(args.substrate_miller)} | {fname}{tuple(args.film_miller)}',
        'inputs':{'substrate':str(args.substrate),'substrate_sha256':sha256(args.substrate),'film':str(args.film),
                  'film_sha256':sha256(args.film),'parent':str(args.parent) if args.parent else None,
                  'parent_sha256':sha256(args.parent) if args.parent else None},
        'settings':{'max_area_A2':args.max_area,'max_atoms':args.max_atoms,'max_length_tol':.05,'max_angle_tol':.03,
                    'film_layers':args.film_layers,'substrate_layers':args.substrate_layers,'max_strain':.06,'candidate_cap':60},
        'enumeration':{**report,'termination_requested':list(args.termination),'valid_for_termination':len(valid)},
        'termination':list(c.termination),'n_atoms':c.n_atoms,'area_A2':c.area,'von_mises_strain':c.von_mises_strain,
        'strain_tensor':np.asarray(props['strain']).tolist(),
        'film_transformation':np.asarray(props['film_transformation']).tolist(),
        'substrate_transformation':np.asarray(props['substrate_transformation']).tolist(),
        'cut_shifts':{'film':None,'substrate':None},'warnings':warn,'sides':sides,
        'fixed_atoms':{'rule':'bottom 34% of the substrate z span (energetics.bottom_fixed_indices)','count':len(fixed)}}
    from pymatgen.analysis.interfaces.coherent_interfaces import CoherentInterfaceBuilder
    from pymatgen.analysis.interfaces.zsl import ZSLGenerator
    builder=CoherentInterfaceBuilder(substrate_structure=s,film_structure=f,film_miller=tuple(args.film_miller),
        substrate_miller=tuple(args.substrate_miller),zslgen=ZSLGenerator(max_area=args.max_area,max_length_tol=.05,max_angle_tol=.03,max_area_ratio_tol=.1))
    build['cut_shifts']=dict(zip(('film','substrate'),map(float,builder._terminations[tuple(c.termination)])))
    args.output.mkdir(parents=True)
    from dataclasses import asdict
    (args.output/'interface.json').write_text(json.dumps(i.as_dict(),cls=MontyEncoder))
    (args.output/'selected.json').write_text(json.dumps({'candidate':asdict(c),'warnings':warn,'contact':args.label,
        'purpose':'explicit-termination contact build; not yet relaxed','substrate_file':str(args.substrate),'film_file':str(args.film)},indent=2))
    (args.output/'build.json').write_text(json.dumps(build,indent=2,default=float)+'\n')
    write(args.output/'initial.extxyz',atoms)  # as built: offset (0,0), gap 2 Å, before any registry scan
    sub_side=sides['substrate'];film_side=sides['film']
    print(f"{args.label}: {c.n_atoms} atoms, area {c.area:.3f} Å², strain {c.von_mises_strain:.4f}, termination {c.termination}, "
          f"truncated={report['truncated']}, fixed {len(fixed)}")
    for name,side in (('substrate',sub_side),('film',film_side)):
        print(f"  {name} {side['formula']}: |p|/A {side['formal_dipole_per_area_e_per_A']:.3f}, cut {side['cut_polyhedra']}, "
              f"contact layers {side['contact_side_layers']}, far layers {side['far_side_layers']}")
        if 'contact_side_framework' in side:
            for k in ('contact_side_framework','far_side_framework'):
                print(f"    {k}: {[(l['species'],l['parent_height'],l['count']) for l in side[k]]}")

if __name__=='__main__':main()
