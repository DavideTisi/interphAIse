#!/usr/bin/env python3
"""List valid coherent interfaces between two structure files (e.g. relaxed bulk cells).

Matching only: no MLIP. Uses the pilot's ZSL and validation gates; the area cap, atom cap
and substrate facets are arguments so a shared two-contact protocol can be chosen.
"""
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from ase.io import read
from pymatgen.io.ase import AseAtomsAdaptor
from interphaise.tools.matcher import enumerate_interfaces,MatchSettings,low_index_millers
from interphaise.tools.validation import validate,oxidation_map,slab_charge_and_dipole


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('substrate',type=Path);ap.add_argument('film',type=Path)
    ap.add_argument('--names',nargs=2,required=True,metavar=('SUBSTRATE','FILM'),help='Formulas, for oxidation states')
    ap.add_argument('--substrate-miller',type=int,nargs=3,help='Default: all symmetry-distinct low-index facets')
    ap.add_argument('--max-area',type=float,default=300);ap.add_argument('--max-atoms',type=int,default=256)
    ap.add_argument('--max-strain',type=float,default=.06);ap.add_argument('--output',type=Path)
    args=ap.parse_args()
    s=AseAtomsAdaptor.get_structure(read(args.substrate));f=AseAtomsAdaptor.get_structure(read(args.film))
    sname,fname=args.names
    settings=MatchSettings(max_area=args.max_area,max_length_tol=.05,max_angle_tol=.03,film_thickness=2,substrate_thickness=2,max_candidates=60)
    valid=[]
    for sm in [tuple(args.substrate_miller)] if args.substrate_miller else low_index_millers(s):
        for fm in low_index_millers(f):
            for c,i in enumerate_interfaces(s,f,sm,fm,(sname,fname),settings):
                ok,_,warn=validate(c,i,max_atoms=args.max_atoms,max_strain=args.max_strain,film_oxi=oxidation_map(f),
                                   substrate_oxi=oxidation_map(s),film_formula=fname,substrate_formula=sname)
                if ok:
                    polarity=[abs(slab_charge_and_dipole(slab,oxidation_map(formula))[1])/c.area
                              for slab,formula in ((i.film,fname),(i.substrate,sname))]
                    valid.append({'n_atoms':c.n_atoms,'strain':c.von_mises_strain,'polarity_e_per_A':polarity,
                                  'area_A2':c.area,'substrate_miller':sm,'film_miller':fm,'termination':c.termination,'warnings':warn})
    # Same order as the pilot selection rule: fewest atoms, then strain, then total formal polarity.
    valid.sort(key=lambda v:(v['n_atoms'],v['strain'],sum(v['polarity_e_per_A'])))
    print(f'{sname} | {fname}: {len(valid)} valid (area <= {args.max_area} Å², atoms <= {args.max_atoms})')
    for v in valid[:5]:
        print(f"  {v['n_atoms']} atoms, strain {v['strain']:.4f}, area {v['area_A2']:.1f}, {v['substrate_miller']}|{v['film_miller']}, "
              f"{v['termination']}, |p|/A {[round(p,2) for p in v['polarity_e_per_A']]}")
    if args.output:args.output.write_text(json.dumps({'settings':vars(args)|{'substrate':str(args.substrate),'film':str(args.film),'output':str(args.output)},
                                                     'valid':valid},indent=2,default=list)+'\n')

if __name__=='__main__':main()
