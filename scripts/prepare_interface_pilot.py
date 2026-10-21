"""Prepare one LiCoO2(001)/LiNbF6 pilot from pinned thermodynamic structures.
Enumerate five low-index film facets; select a small neutral interface below 6% strain.
This is not an exhaustive termination/facet study.
"""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=Path,default=ROOT/'runs/petmad_interface_pilot')
args=parser.parse_args()
args.output.mkdir(parents=True,exist_ok=True)
from dataclasses import asdict
from monty.json import MontyEncoder
from interphaise.tools.thermo_dataset import load_entries,resolve_entry
from interphaise.tools.matcher import enumerate_interfaces, MatchSettings,low_index_millers
from interphaise.tools.validation import validate,oxidation_map,slab_charge_and_dipole
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
from pathlib import Path
p=json.load(open(ROOT/'data/pools/mp_candidates_v2.json'));d,es=load_entries(ROOT/'data/thermo/mp_gga_v2.json.gz')
mid=next(c['material_id'] for c in p['candidates'] if c['formula']=='LiNbF6')
s=SpacegroupAnalyzer(resolve_entry(es,d['endpoints']['electrode']['material_id']).structure).get_conventional_standard_structure()
f=SpacegroupAnalyzer(resolve_entry(es,mid).structure).get_conventional_standard_structure()
settings=MatchSettings(max_area=160,max_length_tol=.05,max_angle_tol=.03,film_thickness=2,substrate_thickness=2,max_candidates=30)
options=[];logs=[]
for fm in low_index_millers(f):
 pairs=enumerate_interfaces(s,f,(0,0,1),fm,('LiCoO2','LiNbF6'),settings)
 print('facet',fm,'candidates',len(pairs),flush=True)
 for c,i in pairs:
  valid,reject,warn=validate(c,i,max_atoms=256,max_strain=.06,film_oxi=oxidation_map(f),substrate_oxi=oxidation_map(s),film_formula='LiNbF6',substrate_formula='LiCoO2')
  logs.append({'candidate':asdict(c),'valid':valid,'reject':reject,'warnings':warn})
  if valid:options.append((c,i,warn))
(args.output/'construction.json').write_text(json.dumps({'settings':asdict(settings),'max_atoms':256,'dataset_sha256':d['sha256'],'attempts':logs},indent=2))
print('valid',len(options),flush=True)
if options:
 def polarity(item):
  cand,iface,_=item
  return sum(abs(slab_charge_and_dipole(slab,oxidation_map(formula))[1])/cand.area
             for slab,formula in [(iface.film,'LiNbF6'),(iface.substrate,'LiCoO2')])
 c,i,w=min(options,key=lambda item:(item[0].n_atoms,item[0].von_mises_strain,polarity(item)))
 print('selected',asdict(c),w,flush=True)
 (args.output/'interface.json').write_text(json.dumps(i.as_dict(),cls=MontyEncoder))
 (args.output/'selected.json').write_text(json.dumps({'candidate':asdict(c),'warnings':w,'purpose':'finite-cell sharp-interface software/MLIP pilot, not coating ranking','dataset_sha256':d['sha256'],'film_material_id':mid,'substrate_material_id':str(d['endpoints']['electrode']['material_id'])},indent=2))

else:
 raise SystemExit('No valid interface found within pilot constraints')
