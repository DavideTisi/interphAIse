#!/usr/bin/env python3
"""Construction screen of one coating against both reviewed substrate cuts (no energies).

For every symmetry-distinct low-index coating facet, both contacts are enumerated with the
reviewed substrate termination fixed (LiCoO2(001) Li cut; seed-0 Li6PS5Cl(111) mapped Cl cut),
area tier 300 Å² then 600 Å², unchanged ZSL/strain tolerances. The coating layer count is the
smallest giving a coating span >= --min-span. Every enumerated candidate is recorded with its
gate outcome: atom cap, strain, neutrality, stoichiometry, overlaps, cut protected groups
(PS4, PO4) and broken coating cation-ligand bonds per area, plus formal polarity.
"""
import argparse,collections,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import numpy as np
from ase.io import read
from pymatgen.analysis.interfaces.coherent_interfaces import CoherentInterfaceBuilder
from pymatgen.analysis.interfaces.zsl import ZSLGenerator
from pymatgen.io.ase import AseAtomsAdaptor
from interphaise.tools.matcher import enumerate_interfaces,MatchSettings,low_index_millers
from interphaise.tools.validation import validate,oxidation_map,slab_charge_and_dipole,_min_distance_violations

B=ROOT/'data/petmad/bulk_relaxation_v1'
SUBSTRATES={'cathode':dict(formula='LiCoO2',bulk=B/'LiCoO2/stability_check/final.extxyz',miller=(0,0,1),
                           termination='Li_P6/mmm_1',layers=2,protected=[('Co','O',2.2)]),
            'electrolyte':dict(formula='Li6PS5Cl',bulk=B/'Li6PS5Cl/stability_check/final.extxyz',miller=(1,1,1),
                               termination='Li6Cl_P1_7',layers=4,protected=[('P','S',2.4)])}
# Protected coating groups must stay whole; other cation-ligand deficits are reported per area.
PROTECTED={'LiZr2(PO4)3':[('P','O',1.8)]}
LIGAND_CUTOFF={'F':2.4,'O':2.5}


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def coordination(structure,centre,ligand,cutoff):
    return [sum(1 for n in structure.get_neighbors(site,cutoff) if n.specie.symbol==ligand)
            for site in structure if site.specie.symbol==centre]


def bulk_coordination(bulk,ligand):
    cations=sorted({s.specie.symbol for s in bulk if s.specie.symbol not in ('Li',ligand)}) or ['Li']
    return {c:max(coordination(bulk,c,ligand,LIGAND_CUTOFF[ligand])) for c in cations}


def broken_bonds(slab,bulk_cn,ligand):
    out={}
    for c,cn in bulk_cn.items():
        counts=coordination(slab,c,ligand,LIGAND_CUTOFF[ligand])
        out[c]=int(sum(cn-k for k in counts if k<cn))
    return out


def stoichiometric(slab,bulk):
    return slab.composition.reduced_composition==bulk.composition.reduced_composition


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('formula');ap.add_argument('bulk',type=Path)
    ap.add_argument('--tiers',type=float,nargs='+',default=[300,600]);ap.add_argument('--max-atoms',type=int,default=1200)
    ap.add_argument('--min-span',type=float,default=40.0,help='Minimum coating slab span, Å')
    ap.add_argument('--max-layers',type=int,default=40);ap.add_argument('--per-termination',type=int,default=12)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    film_bulk=AseAtomsAdaptor.get_structure(read(args.bulk))
    ligand='O' if 'O' in {s.specie.symbol for s in film_bulk} else 'F'
    bulk_cn=bulk_coordination(film_bulk,ligand)
    report={'formula':args.formula,'bulk':str(args.bulk),'bulk_sha256':sha(args.bulk),'ligand':ligand,
            'bulk_cation_coordination':bulk_cn,'min_span_A':args.min_span,'tiers_A2':args.tiers,'max_atoms':args.max_atoms,
            'zsl':{'max_length_tol':.05,'max_angle_tol':.03,'max_area_ratio_tol':.10},'max_strain':.06,'facets':{}}
    for fm in low_index_millers(film_bulk):
        key=''.join(map(str,fm));report['facets'][key]={}
        for contact,sub in SUBSTRATES.items():
            s=AseAtomsAdaptor.get_structure(read(sub['bulk']));rows=[];found_tier=None
            for tier in args.tiers:
                zsl=ZSLGenerator(max_area=tier,max_length_tol=.05,max_angle_tol=.03,max_area_ratio_tol=.10)
                builder=CoherentInterfaceBuilder(substrate_structure=s,film_structure=film_bulk,film_miller=fm,
                                                 substrate_miller=sub['miller'],zslgen=zsl)
                terms=[t for t in builder.terminations if t[1]==sub['termination']]
                entry={'tier_A2':tier,'zsl_matches':len(builder.zsl_matches),'film_terminations':[t[0] for t in terms],
                       'all_substrate_terminations':sorted({t[1] for t in builder.terminations}),'candidates':[]}
                if builder.zsl_matches and terms:
                    def build(layers):
                        # Each termination is enumerated separately with its own cap, so one termination
                        # can never exhaust the cap and hide another.
                        st=MatchSettings(max_area=tier,max_length_tol=.05,max_angle_tol=.03,film_thickness=layers,
                                         substrate_thickness=sub['layers'],max_candidates=args.per_termination)
                        pairs=[];rep={'truncated_terminations':[]}
                        for term in terms:
                            r={};pairs+=enumerate_interfaces(s,film_bulk,sub['miller'],fm,(sub['formula'],args.formula),st,
                                                             terminations=[term],report=r)
                            if r.get('truncated'):rep['truncated_terminations'].append(list(term))
                        rep['truncated']=bool(rep['truncated_terminations'])
                        return pairs,[float(np.ptp(i.film.cart_coords[:,2])) for _,i in pairs],rep
                    # Estimate the layer count from the 1- and 2-layer spans, then step up until the smallest
                    # span reaches the target or even the smallest cell exceeds the atom cap.
                    p1,s1,_=build(1);p2,s2,_=build(2)
                    per_layer=max(min(s2)-min(s1),1e-3) if p1 and p2 else None
                    layers=max(1,int(np.ceil((args.min_span-min(s1))/per_layer))+1) if per_layer else 1
                    layers=min(layers,args.max_layers)
                    while True:
                        pairs,spans,rep=build(layers)
                        too_big=pairs and min(c.n_atoms for c,_ in pairs)>args.max_atoms
                        if not pairs or min(spans)>=args.min_span or too_big or layers>=args.max_layers:break
                        layers+=1
                    entry.update(film_layers=layers,truncated=rep.get('truncated'),truncated_terminations=rep.get('truncated_terminations'),
                                 stopped_because='span reached' if pairs and min(spans)>=args.min_span else
                                 'atom cap exceeded' if too_big else 'layer limit' if layers>=args.max_layers else 'no candidates')
                    for (c,i),span in zip(pairs,spans):
                        ok,reject,warn=validate(c,i,max_atoms=args.max_atoms,max_strain=.06,film_oxi=oxidation_map(film_bulk),
                                                substrate_oxi=oxidation_map(s),film_formula=args.formula,substrate_formula=sub['formula'])
                        gates={'validate':ok,'reject':reject,'span_ok':span>=args.min_span,
                               'film_stoichiometric':stoichiometric(i.film,film_bulk),'substrate_stoichiometric':stoichiometric(i.substrate,s),
                               'overlaps':len(_min_distance_violations(i))}
                        protected={f'{a}{b}':sum(k<4 for k in coordination(i.film,a,b,r)) for a,b,r in PROTECTED.get(args.formula,[])}
                        protected.update({f'sub_{a}{b}':sum(k<4 for k in coordination(i.substrate,a,b,r)) for a,b,r in sub['protected'] if a=='P'})
                        bb=broken_bonds(i.film,bulk_cn,ligand)
                        pol=[abs(slab_charge_and_dipole(sl,oxidation_map(fo))[1])/c.area for sl,fo in ((i.film,film_bulk),(i.substrate,s))]
                        q=[slab_charge_and_dipole(sl,oxidation_map(fo))[0] for sl,fo in ((i.film,film_bulk),(i.substrate,s))]
                        admissible=(ok and gates['span_ok'] and gates['film_stoichiometric'] and gates['substrate_stoichiometric']
                                    and not gates['overlaps'] and not any(protected.values()) and all(abs(x)<1e-6 for x in q))
                        entry['candidates'].append({'termination':list(c.termination),'n_atoms':c.n_atoms,'area_A2':c.area,
                            'strain':c.von_mises_strain,'film_span_A':span,'film_atoms':len(i.film),'gates':gates,
                            'formal_charge':q,'formal_polarity_e_per_A':pol,'protected_cut':protected,
                            'broken_cation_ligand_bonds':bb,'broken_bonds_per_area':sum(bb.values())/c.area,
                            'admissible':admissible,'warnings':warn})
                rows.append(entry)
                if any(x['admissible'] for x in entry['candidates']):found_tier=tier;break
            report['facets'][key][contact]={'tiers':rows,'admissible_tier_A2':found_tier,
                                            'n_admissible':sum(x['admissible'] for e in rows for x in e['candidates'])}
            print(f"{args.formula} {fm} {contact}: "+'; '.join(f"tier {e['tier_A2']:g}: zsl {e['zsl_matches']}, terms {len(e['film_terminations'])}, "
                  f"layers {e.get('film_layers','-')}, cands {len(e['candidates'])}, admissible {sum(x['admissible'] for x in e['candidates'])}" for e in rows),flush=True)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=1,default=lambda o:o.tolist() if hasattr(o,'tolist') else str(o))+'\n')

if __name__=='__main__':main()
