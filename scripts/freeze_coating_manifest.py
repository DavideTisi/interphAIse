#!/usr/bin/env python3
"""Freeze the coating-pilot manifest and the initial campaign index (all planned jobs pending).

Copies the frozen input builds into data/petmad/coating_comparison_v1/inputs/, computes every
manifest field from those files (hashes, atom counts, areas, compositions, physical fixed masks
under the declared depth rules, geometric registries), joins the frozen sulfide thermodynamic
values by exact ID, and writes manifest.json (+ .sha256) and index.json. No energies.
"""
import argparse,hashlib,json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from pymatgen.core.interface import Interface
from interphaise.tools.energetics import to_atoms,bottom_fixed_indices

CHECKPOINT='3f52e97c459b2a28a94fc49b8a2f9a92551231a0ea4f5b5db2396f12d8ffa1e9'
DEPTH={'cathode':9.10044154,'electrolyte':3.257602}           # physical frozen depths (Å)
VARIED_DEPTH={'cathode':13.385,'electrolyte':6.515204}         # fixed-depth variation (LiNbF6 bracket endpoints)
COATINGS={'mp-aaacjmqp':('LiTaF6','(001) F2_P-6_3, 4 layers'),'mp-aaaaajby':('LiCaAlF6','(100) LiAlF4_P2_6, 10 layers'),
          'mp-aaaaabru':('LiF','(110) LiF_Pmmm_2, 15 layers')}
REFERENCE={'candidate_id':'mp-aaacjjwh','formula':'LiNbF6'}
EXCLUDED={'mp-aaabevhd':('LiZr2(PO4)3','no admissible two-contact construction within 600 Å² and 1,250 atoms '
                         '(electrolyte: only (001), >= 2,456 atoms; cathode cells over the cap; most facets cut PO4)')}


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def expected(build_dir,contact):
    b=json.loads((build_dir/'build.json').read_text())
    iface=Interface.from_dict(json.loads((build_dir/'interface.json').read_text()))
    iface.in_plane_offset=(0,0);iface.gap=2.0;atoms=to_atoms(iface)
    fixed=bottom_fixed_indices(atoms,iface.substrate_indices,depth=DEPTH[contact])
    species=sorted({atoms[i].symbol for i in fixed})
    return {'candidate':{'pair':list(iface_pair(b)),'film_miller':None,'substrate_miller':None,'termination':b['termination']},
            'n_atoms':len(atoms),'area_A2':b['area_A2'],'formula':atoms.get_chemical_formula(),'n_fixed':len(fixed),
            'fixed_species':{s:[atoms[i].symbol for i in fixed].count(s) for s in species},
            'von_mises_strain':b['von_mises_strain'],'film_transformation':b['film_transformation'],
            'substrate_transformation':b['substrate_transformation'],'build_sha256':sha(build_dir/'interface.json'),
            'build_json_sha256':sha(build_dir/'build.json'),'termination':b['termination'],
            'formal_polarity_e_per_A':{s:b['sides'][s]['formal_dipole_per_area_e_per_A'] for s in ('film','substrate')},
            'cut_polyhedra':{s:b['sides'][s]['cut_polyhedra'] for s in ('film','substrate')}}


def iface_pair(b):
    sub,film=b['contact'].split(' | ');return sub.split('(')[0],film.split('(')[0]


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--inputs',type=Path,default=ROOT/'runs/coating_inputs_v2')
    ap.add_argument('--out',type=Path,default=ROOT/'data/petmad/coating_comparison_v1')
    args=ap.parse_args()
    dest=args.out/'inputs';dest.mkdir(parents=True,exist_ok=True)
    table=json.loads((ROOT/'data/benchmarks/environment_v1/lco_lpscl_4v.json').read_text())
    thermo={r['candidate_id']:r for r in table['results']}
    def card(cid,formula):
        r=thermo[cid];pen=r['component_analysis']['penalties']
        return {'candidate_id':cid,'formula':formula,'sulfide_penalty_eV_per_non_Li_atom':max(pen.values()),
                'penalty_components':pen,'acceptable':r['acceptable'],'band_gap_eV':r['band_gap_eV'],
                'thermo_table':'data/benchmarks/environment_v1/lco_lpscl_4v.json','thermo_table_sha256':table['sha256']}
    def copy_build(name):
        src=args.inputs/name if (args.inputs/name).exists() else args.inputs/'sensitivity'/name
        out=dest/name;out.mkdir(exist_ok=True)
        for f in ('build.json','interface.json','selected.json','initial.extxyz','registries.json'):
            if (src/f).exists():shutil.copy2(src/f,out/f)
        return out
    manifest={'schema':'coating-pilot-manifest-v1','frozen_before_new_interface_energies':True,
        'protocol':{'checkpoint_sha256':CHECKPOINT,'model':'PET-MAD S 1.6.0 (r2SCAN), upet 0.3.1','force_target_eV_A':0.05,
                    'step_limit':400,'vacuum_A':15.0,'initial_gap_A':2.0,'optimizer':'FIRE; joined + film + substrate relaxations',
                    'separation':'rigid-fragment single points (W_sep), same device','device':'cuda (RTX 3090, sm3090el9_devel)',
                    'code':'immutable git-archive snapshot per batch, CODE=code_<commit>'},
        'construction':{'substrates':{'cathode':'LiCoO2(001) Li_P6/mmm_1, 2 layers (26.77 Å), PET-MAD unconstrained bulk',
                                      'electrolyte':'seed-0 Li6PS5Cl(111) mapped Cl cut Li6Cl_P1_7, 4 layers (21.28 Å)'},
                        'area_tiers_A2':[300,600],'max_atoms':1250,
                        'atom_cap_amendment':'1,200 -> 1,250 uniform, construction-driven, before selection and new energies '
                                             '(SYNC_CLAUDE_10.md); the original 1,200-atom screen is retained',
                        'zsl':{'max_length_tol':.05,'max_angle_tol':.03,'max_area_ratio_tol':.10},'max_strain':.06,
                        'coating_min_span_A':40.0,'facets':'symmetry-distinct, index <= 1, same coating facet on both contacts',
                        'gates':'neutral, stoichiometric, no overlaps, no cut PS4/PO4',
                        'ordering':'fewest broken cation-ligand bonds per area, lower total formal polarity, fewer atoms, lower strain, termination',
                        'enumeration':'per termination, 60 candidates per build (12 in the screen)'},
        'fixed_rule':{c:{'depth_A':d} for c,d in DEPTH.items()},
        'registry_rule':'(0,0); then farthest translation class modulo the coating/substrate surface lattices; '
                        'no exact symmetry equivalents (scripts/select_registries.py, 12x12 grid); up to 3 per contact',
        'selection_rule':'per contact, lowest relaxed joined energy among valid primary registries',
        'sensitivity_slots':{'thickness_increment':'+1 coating layer, same in-plane cell',
                             'fixed_depth_variation':{'cathode_depth_A':VARIED_DEPTH['cathode'],'electrolyte_depth_A':VARIED_DEPTH['electrolyte']},
                             'robustness_case':{'cathode':'3 LiCoO2 layers, same in-plane cell','electrolyte':'seed-4 Li6PS5Cl, mapped Cl cut'}},
        'budget':{'max_full_jobs':36,'per_new_coating':'6 primary + up to 6 sensitivity','reference_new_jobs':0},
        'failure_policy':'failed or unconverged jobs are terminal outcomes with null works; a failed contact consumes the material '
                         'slot; no automatic replacement material, retry or extension; sensitivity never enters decisions',
        'menu':[card(REFERENCE['candidate_id'],REFERENCE['formula'])|{'role':'reference','feasible':True,
                 'construction':'(001) F2_P-6_3, 4 layers (archived)'}]+
               [card(cid,f)|{'role':'option','feasible':True,'construction':desc} for cid,(f,desc) in COATINGS.items()]+
               [card(cid,f)|{'role':'excluded','feasible':False,'exclusion_reason':why} for cid,(f,why) in EXCLUDED.items()],
        'coatings':{}}
    unavailable={('mp-aaaaajby','electrolyte','thickness_increment'):'not_run_resource_limit (1,302 atoms > 1,250)',
                 ('mp-aaaaajby','electrolyte','robustness_case'):'not_run_no_admissible_construction (seed-4 bulk, 300 and 600 Å²)',
                 ('mp-aaaaabru','electrolyte','robustness_case'):'not_run_no_admissible_construction (seed-4 bulk, 300 and 600 Å²)'}
    sens_builds={'thickness_increment':{'mp-aaacjmqp':'_thickness_L5','mp-aaaaajby':'_thickness_L11','mp-aaaaabru':'_thickness_L16'},
                 'robustness_case':{'cathode':'_cathode_substrate3','electrolyte':'_electrolyte_seed4'}}
    for cid,(formula,_) in COATINGS.items():
        contacts={}
        for contact in ('cathode','electrolyte'):
            primary=copy_build(f'{formula}_{contact}');exp=expected(primary,contact)
            regs=json.loads((primary/'registries.json').read_text())['registries']
            sens={}
            for slot in ('thickness_increment','fixed_depth_variation','robustness_case'):
                if (cid,contact,slot) in unavailable:sens[slot]={'status':unavailable[(cid,contact,slot)].split(' ')[0],
                                                                 'reason':unavailable[(cid,contact,slot)]};continue
                if slot=='fixed_depth_variation':
                    sens[slot]={'status':'pending','build':str(primary.relative_to(ROOT)),'depth_A':VARIED_DEPTH[contact],
                                'registry':'selected primary registry'};continue
                name=(f'{formula}_{contact}{sens_builds[slot][cid]}' if slot=='thickness_increment'
                      else f'{formula}{sens_builds[slot][contact]}')
                b=copy_build(name)
                sens[slot]={'status':'pending','build':str(b.relative_to(ROOT)),'build_sha256':sha(b/'interface.json'),
                            'depth_A':DEPTH[contact],'registry':'selected primary registry' if slot!='robustness_case' or contact=='cathode'
                            else 'fractional (0,0) and the selected primary offset are not physically comparable across bases; use (0,0)'}
            cand=json.loads((primary/'selected.json').read_text())['candidate']
            contacts[contact]={'expected':exp|{'candidate':{k:cand[k] for k in ('pair','film_miller','substrate_miller','termination')}},
                               'build':str(primary.relative_to(ROOT)),
                               'registries':[{'id':r['id'],'offset':r['offset'],'gap_A':2.0} for r in regs],'sensitivity':sens}
        manifest['coatings'][cid]={'formula':formula,'contacts':contacts}
    manifest['reference']={'candidate_id':REFERENCE['candidate_id'],'formula':'LiNbF6','status':'reused archive',
        'primary_runs':{'cathode':{'R1':'data/petmad/niflheim_batch1/cathode_ref','R2':'data/petmad/niflheim_batch1/cathode_reg_sixth_0',
                                   'R3':'data/petmad/niflheim_batch1/cathode_reg_third_third'},
                        'electrolyte':{'R1':'data/petmad/niflheim_batch1/electrolyte_seed0_ref','R2':'data/petmad/final_checks_v1/electrolyte_reg_0_0.5'}},
        'registry_provenance':'chosen before the geometric registry rule (cathode from an unrelaxed 6x6 energy diagnostic; electrolyte '
                              'the two distinct classes of a 2x2 grid). The geometric rule would choose cathode (0,0),(1/4,1/4),(1/12,1/4) '
                              'and electrolyte (0,0),(1/4,1/2),(1/12,3/4).',
        'optional_consistency_jobs':'4 jobs (the geometric-rule registries not yet run); not run unless approved; never in decisions',
        'sensitivity_context':'archived thickness, constraint, vacuum and seed-4 results are material-specific context, not an error bar'}
    text=json.dumps(manifest,indent=1)+'\n';(args.out/'manifest.json').write_text(text)
    digest=hashlib.sha256(text.encode()).hexdigest();(args.out/'manifest.json.sha256').write_text(digest+'\n')
    # Initial index in the agreed contract: every planned job pending, written before any energy.
    runs=[]
    for cid,entry in manifest['coatings'].items():
        for contact,spec in entry['contacts'].items():
            e=spec['expected']
            for r in spec['registries']:
                runs.append({'run_id':f"{cid}:{contact}:primary:{r['id']}",'candidate_id':cid,'contact':contact,'role':'primary',
                    'sensitivity_kind':None,'registry_id':r['id'],'registry':r['offset'],'gap_A':r['gap_A'],
                    'fixed_rule':{'depth_A':DEPTH[contact]},'n_fixed':e['n_fixed'],'fixed_species':e['fixed_species'],
                    'n_atoms':e['n_atoms'],'area_A2':e['area_A2'],'build_sha256':e['build_sha256'],'contact_build_id':spec['build'],
                    'status':'pending','W_adh_J_m2':None,'W_sep_J_m2':None,'checkpoint_sha256':CHECKPOINT,
                    'planned_in_manifest_sha256':digest,'reused_from':None})
            for slot,s in spec['sensitivity'].items():
                runs.append({'run_id':f'{cid}:{contact}:sensitivity:{slot}','candidate_id':cid,'contact':contact,'role':'sensitivity',
                    'sensitivity_kind':slot,'status':s['status'],'failure_reason':s.get('reason'),'W_adh_J_m2':None,'W_sep_J_m2':None,
                    'checkpoint_sha256':CHECKPOINT,'planned_in_manifest_sha256':digest,'contact_build_id':s.get('build')})
    # The LiNbF6 reference enters as reused archive runs with their recorded values and source hashes.
    offsets={'cathode':{'R1':[0,0],'R2':[1/6,0],'R3':[1/3,1/3]},'electrolyte':{'R1':[0,0],'R2':[0,0.5]}}
    for contact,regs in manifest['reference']['primary_runs'].items():
        for rid,path in regs.items():
            r=json.loads((ROOT/path/'result.json').read_text());R=r['relaxations']
            sep=json.loads((ROOT/path/'fixed_geometry_separation.json').read_text())
            fixed=R['interface']['fixed_atom_indices']
            runs.append({'run_id':f"{REFERENCE['candidate_id']}:{contact}:primary:{rid}",'candidate_id':REFERENCE['candidate_id'],
                'contact':contact,'role':'primary','sensitivity_kind':None,'registry_id':rid,'registry':offsets[contact][rid],'gap_A':2.0,
                'fixed_rule':{'depth_A':DEPTH[contact]} if r.get('fixed_depth_A') else {'fraction':r.get('fixed_fraction')},
                'n_fixed':len(fixed),'n_atoms':r['n_atoms'],'area_A2':r['area_A2'],'status':'valid','failure_reason':None,
                'W_adh_J_m2':r['work_of_adhesion_J_m2'],'W_sep_J_m2':sep['W_sep_fixed_geometry_J_m2'],
                'joined_energy_eV':R['interface']['final_energy_eV'],'checkpoint_sha256':r['checkpoint_sha256'],
                'result_path':f'{path}/result.json','result_sha256':sha(ROOT/path/'result.json'),
                'separation_path':f'{path}/fixed_geometry_separation.json','separation_single_points':2,'device':r.get('device'),
                'calculator_calls':r['calculator_calls'],'wall_seconds':r['wall_seconds'],'reused_from':path,
                'warnings':['registry chosen before the geometric registry rule (see manifest reference.registry_provenance)']})
    index={'schema_version':'coating_comparison_v1','checkpoint_sha256':CHECKPOINT,'manifest_sha256':digest,
           'menu':[{k:m.get(k) for k in ('candidate_id','formula','feasible','role','construction','exclusion_reason')}|
                   {'limitations':['formally polar slabs','finite-range MLIP','no Li transport']} for m in manifest['menu']],
           'runs':runs,'cohort':[{'candidate_id':REFERENCE['candidate_id'],'slot_reason':'reference'}]}
    (args.out/'index.json').write_text(json.dumps(index,indent=1)+'\n')
    n_primary=sum(r['role']=='primary' for r in runs);n_sens=sum(r['role']=='sensitivity' and r['status']=='pending' for r in runs)
    print(f'manifest sha256 {digest[:16]}; planned primary {n_primary}, pending sensitivity {n_sens}, '
          f'unavailable {sum(r["role"]=="sensitivity" and r["status"]!="pending" for r in runs)}')

if __name__=='__main__':main()
