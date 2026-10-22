// Editable scientific presentation. See presentations/README.md for reproduction.
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const ROOT=process.env.INTERPHAISE_ROOT || process.cwd();
const RUNTIME=process.env.CODEX_RUNTIME || '/Users/davidetisi/.cache/codex-runtimes/codex-primary-runtime/dependencies';
process.env.RUNTIME_NODE_MODULES ||= path.join(RUNTIME,'node/node_modules');
const SKILL=process.env.PRESENTATION_SKILL || '/Users/davidetisi/.codex/plugins/cache/openai-primary-runtime/presentations/26.1015.12040/skills/presentations';
const {Presentation,PresentationFile,FileBlob}=await import(pathToFileURL(path.join(RUNTIME,'node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs')).href).catch(async()=>import('@oai/artifact-tool'));
const {resolvePresentationFont,applyPresentationChartFont,finalizePresentation}=await import(pathToFileURL(path.join(SKILL,'container_tools/artifact_tool_utils.mjs')).href);
const BUILD=path.join(ROOT,'presentations/.build/results_synthesis');
const OUT=path.join(ROOT,'presentations/results_2026-10-22');
const E=JSON.parse(await fs.readFile(path.join(ROOT,'presentations/source/results_synthesis_2026-10-22.json'),'utf8'));
const FONT=resolvePresentationFont();
const C={bg:'#FAFAF7',ink:'#172B3A',muted:'#526472',rule:'#D6DEDE',teal:'#007F7B',blue:'#366AA8',orange:'#CA713A',purple:'#9076A9',gray:'#8A949C',red:'#A44838',white:'#FFFFFF'};
const ARM={iterative:{name:'Iterative',color:C.teal},sequential:{name:'Sequential',color:C.blue},shuffled:{name:'Shuffled',color:C.orange},upfront:{name:'Upfront',color:C.purple},random:{name:'Random',color:C.gray}};
const P=Presentation.create({slideSize:{width:1280,height:720}});
const TABLES=[],CHARTS=[],MANIFEST=[];
const common='Sources pinned for this synthesis: davide '+E.sources.davide_commit+'; agent '+E.sources.agent_commit+'; physics '+E.sources.physics_commit+'. No new live LLM or MLIP calls. Figures use the archived outcomes, not a new experiment.';
function text(s,str,x,y,w,h,size=26,color=C.ink,bold=false){const q=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});q.text=str;q.text.style={typeface:FONT,fontSize:size,color,bold,autoFit:'none',wrap:'square',insets:0,verticalAlignment:'top'};return q;}
function slide(title,section,notes='',subtitle=''){const s=P.slides.add();s.background.fill=C.bg;const n=P.slides.items.length;text(s,section.toUpperCase(),56,27,1110,26,18,C.teal,true);text(s,title,56,74,1168,110,44,C.ink,true);if(subtitle)text(s,subtitle,56,154,1168,59,25,C.muted);text(s,'interphAIse  /  Results through 22 October 2026',56,679,1090,24,17,C.muted);text(s,String(n).padStart(2,'0'),1160,677,64,28,19,C.muted);s.speakerNotes.text=notes+'\n\n'+common;MANIFEST.push({slide:n,title,section,notes});return s;}
function note(s,str,y=615,color=C.muted){text(s,str,56,y,1168,55,23,color);}
function table(s,values,widths,{top=212,height=330,font=25,header=23}={}){const t=s.tables.add({rows:values.length,columns:widths.length,left:56,top,width:1168,height,values,columnWidths:widths});TABLES.push(P.slides.items.indexOf(s)+1);t.styleOptions={headerRow:false,bandedRows:false};t.borders.assign({fill:C.rule,width:0.6,style:'solid'});const rowH=height/values.length;values.forEach((row,i)=>{t.rows[i].height=rowH;row.forEach((_,j)=>{const cell=t.getCell(i,j);cell.fill=i===0?C.ink:C.bg;cell.text.style={typeface:FONT,fontSize:i===0?header:font,color:i===0?C.white:C.ink,bold:i===0,autoFit:'none',insets:0};});});t.cells.block({row:0,column:0,rowCount:values.length,columnCount:widths.length}).assign({margins:{left:14,right:12,top:4,bottom:4},anchor:'center'});return t;}
function chart(s,type,config){config.series=config.series.map(v=>({...v,smooth:false,values:v.values.map(n=>n===null?null:Number(n.toPrecision(10)))}));const q=s.charts.add(type,{lineOptions:{smooth:false},chartFill:C.bg,plotAreaFill:C.bg,chartLine:{fill:'none',width:0},plotAreaLine:{fill:'none',width:0},...config});applyPresentationChartFont(q,{fontFamily:FONT});CHARTS.push(P.slides.items.indexOf(s)+1);return q;}
const axis={textStyle:{fontSize:22,fill:C.ink},line:{fill:C.rule,width:1},majorGridlines:{fill:C.rule,width:1}};
function lineSeries(arm,values){return {name:ARM[arm].name,values,line:{fill:ARM[arm].color,width:3.4,style:'solid'},marker:{symbol:arm==='iterative'?'circle':'none',size:6,fill:ARM[arm].color}};}
function fmt(v,n=3){return v.toFixed(n);}

// 1. Cover: restrained, type-led, no synthetic scientific imagery.
{
const s=slide('interphAIse','Materials discovery with computational feedback','Authors: Davide Tisi and Adem R. N. Aouichaoui. This new deck supersedes the results narrative in the 21 October v4 deck. Main story: slides 1–18. Technical backup: 19–24.');
text(s,'Can an LLM choose\nthe next useful\nmaterials calculation?',56,210,1150,265,62,C.ink,true);
text(s,'From a controlled search benchmark to a prospective\nthree-coating PET-MAD comparison',59,510,1120,85,31,C.teal);
text(s,'Davide Tisi and Adem R. N. Aouichaoui',59,624,1120,36,24,C.muted);
}
// 2. Headline, supported and bounded.
{
const s=slide('Feedback helps. The advantage is conditional.','The result', 'Do not pool the original and expanded sulfide datasets: they share candidates and winners. Environment comparisons use 30 runs per arm. The physical pilot is a separate prospective test with only two new coating choices. Sources: environment_summary.json, FINAL_PILOT_REVIEW.md, pilot INTERPRETATION.md.');
text(s,'20/30',56,220,280,80,60,C.teal,true);text(s,'Sulfide successes with feedback',370,224,825,46,30,C.ink,true);text(s,'Sequential 2/30, shuffled 6/30, random 8/30.',370,278,825,60,27,C.muted);
text(s,'12 vs 24',56,357,300,80,56,C.orange,true);text(s,'On LLZO, random beats iterative',370,360,825,46,30,C.ink,true);text(s,'Feedback helps a narrow prior, but too late in ten queries.',370,413,825,68,27,C.muted);
text(s,'2 held\n2 missed',56,494,290,127,44,C.blue,true);text(s,'Four prospective adhesion forecasts',370,506,825,48,30,C.ink,true);text(s,'LiTaF₆ matched both ranges. LiCaAlF₆ fell below both.',370,561,825,68,27,C.muted);
}
// 3. Exactly what human judgment is substituted.
{
const s=slide('The LLM replaces part of the selection judgment','Why the LLM is central','The decision policy is the object of study. The LLM interprets chemistry/results, chooses the next material and makes predictions. Deterministic software performs orchestration, validation, budget accounting and numeric evaluation. A rationale is a recorded hypothesis, not proof of an internal reasoning mechanism. Source: DISCOVERY_REPORT.md, DISCOVERY_IMPLEMENTATION_PLAN.md, pilot state/report.','The question is what to calculate next, and what result to expect.');
table(s,[['Human task being delegated','LLM contribution','Grounding / control'],['Propose a promising direction','Select a coating and explain why','Frozen candidate IDs and budget'],['Learn from a failed test','Relate outcomes to chemistry','Only observed feedback is exposed'],['Decide the next calculation','Revise priorities after feedback','No-feedback and shuffled controls'],['Anticipate the result','Forecast adhesion and weak contact','PET-MAD tests the prediction']], [400,395,373],{height:355,font:25});
note(s,'The LLM supplies the scientific decision policy. The tools supply the numerical evidence.',604,C.teal);
}
// 4. User's HELLMM comparison.
{
const s=slide('From mechanism proposals to material choices','Original inspiration','Source: supplied HELLMM___NeurIPS-7.pdf, sections 1–2, 5–6. HELLMM selects transformation rules, enumerates intermediates and prunes plausibility, with deterministic constraints and atomistic/CHE scoring. Its stated pipeline is sequential without feedback loops. Avoid claiming this project is categorically better. interphAIse does not invent novel compositions or mechanisms.','Both delegate a scientific choice, then test it with calculations.');
table(s,[['','HELLMM','interphAIse'],['What the LLM imagines','Possible intermediates and mechanisms','Promising materials and expected responses'],['What the tools test','Structures, pathways and energetics','Compatibility and contact adhesion'],['Where intuition is replaced','Which mechanisms should exist in the study?','Which material deserves the next test?'],['Distinct contribution here','Richer chemical hypothesis generation','Controlled evidence on feedback use']], [260,454,454],{height:355,font:25});
note(s,'Narrower creativity than HELLMM. A clearer experiment on sequential decision-making.',604,C.teal);
}
// 5. Chronology and scale.
{
const s=slide('Two days produced two complementary experiments','What was completed','Timeline refers to project records through 22 October, not all jobs being started on the displayed day. Original benchmark: 120 integrated runs plus 30 shuffled. Environment: 450 runs, 4500 charged queries, 2800 API calls including repairs. Physical pilot: one reference plus two selected coatings. Sources: archive summaries and final index.','The cheap study measures selection. The physical pilot tests forecasts.');
table(s,[['Stage','Scope','What it can establish'],['21 Oct: frozen benchmark','50 structures, 43 formulas\n150 runs across five arms','Whether feedback helps on one fixed task'],['21 Oct: environment study','141 structures, 100 formulas\n3 environments, 450 runs','Where the decision policy transfers or fails'],['22 Oct: physical pilot','3 coatings, 2 contacts each\n26 new jobs, 2 LLM choices','Prospective predictions and model sensitivity']], [330,410,428],{height:345,font:26});
note(s,'These are separate evidence layers. The larger pool includes the original 50 structures.',601);
}
// 6. Frozen objective.
{
const s=slide('“Acceptable” means passing a frozen proxy','Thermodynamic evaluator','Source: interphaise/discovery_evaluator.py evaluate_candidate; frozen objective a194076f…6c0d and ENVIRONMENT_PROTOCOL.md. The scalar penalty is max(coating self-decomposition, additional reaction with cathode, additional reaction with electrolyte), using nonnegative penalties normalized per non-Li atom. The equilibrated reference removes standalone endpoint decomposition from the contact term. This does not imply an intact electrolyte at 4 V. MP band gap is a proxy for insulation.','LiCoO₂ at 4.0 V, paired with each electrolyte. Lower penalty is better.');
text(s,'P = max(self-decomposition, cathode contact, electrolyte contact)',56,237,1168,91,34,C.teal,true);
table(s,[['Acceptance','Ranking resolution','Meaning'],['P ≤ 0.050 eV / non-Li atom\nBand gap ≥ 2 eV','0.020 eV / non-Li atom bins','Additional reaction on contact,\nrelative to equilibrated endpoints']], [435,345,388],{top:345,height:184,font:26});
note(s,'Lithium transport, finite-temperature behavior, synthesis and cycling were not validated.',574,C.red);
text(s,'The exhaustive table is cheap. Search on it is a controlled benchmark, not a compute-saving result.',56,631,1168,38,22,C.muted);
}
// 7. Experimental arms.
{
const s=slide('Five arms separate prior knowledge from feedback','Controlled search','Sources: ENVIRONMENT_PROTOCOL.md and archived experiments. Sequential sees its own earlier choices/rationales, so it can anchor on its history. Shuffled feedback retains occasional correct assignments and can contradict earlier rationales. No control establishes human-like internal reasoning. Haiku 5.5, temperature 1.0, max_tokens 4096, budget 10, 30 seeds/arm.','Same pool and ten charged evaluations. Thirty runs per arm.');
table(s,[['Arm','Information available','Question answered'],['Iterative','Own choices and true evaluated outcomes','Can useful feedback improve selection?'],['Sequential','Own choices, without evaluated outcomes','What changes without result feedback?'],['Shuffled','Outcome values assigned to wrong candidates','Does correct attribution matter?'],['Upfront','One shortlist before observing outcomes','How far does prior knowledge get?'],['Random','Uniform sampling without replacement','Does the LLM beat broad exploration?']], [225,475,468],{height:384,font:24,header:23});
note(s,'Haiku 5.5, temperature 1.0. Repeated or invalid queries consume budget.',620);
}
// 8. Original benchmark.
{
const s=slide('The original benchmark supports feedback use','21 Oct / 50 structures','Source: integrated_v3_20261021_s100/summary.json and shuffled_v3_20261021_s100/summary.json. 19/30 iterative, 4 sequential, 6 shuffled, 4 upfront, 10 sampled random. Paired iterative vs shuffled: 16 vs 3 discordant seeds, exact McNemar p≈0.00443, unadjusted. Exact random P=0.3632653. Fixed fluoride-first post-hoc baseline reaches acceptable at query 2. Original pool is not independent from expanded study.','Acceptable coating found within ten queries, out of 30 runs.');
const arms=E.arm_order;chart(s,'bar',{position:{left:52,top:220,width:800,height:355},categories:arms.map(a=>ARM[a].name),series:[{name:'Successful runs',values:arms.map(a=>E.original[a].count),points:arms.map((a,idx)=>({idx,fill:ARM[a].color}))}],hasLegend:false,barOptions:{direction:'column',grouping:'clustered',gapWidth:70,varyColors:true},yAxis:{...axis,min:0,max:30,majorUnit:10,title:{text:'Successful runs / 30',textStyle:{fontSize:22}}},xAxis:{...axis,majorGridlines:null},dataLabels:{showValue:true,position:'outEnd',textStyle:{fontSize:26,bold:true,fill:C.ink}}});
text(s,'19 vs 6',886,239,330,60,46,C.teal,true);text(s,'True versus shuffled feedback\nPaired p = 0.0044',886,310,330,98,26,C.ink);text(s,'Random expectation\n36.3% at query 10',886,440,330,98,26,C.muted);
note(s,'But a post-hoc fluoride-first rule succeeds by query 2. This is not superiority over every heuristic.',607,C.red);
}
// 9. Environment endpoint chart.
{
const s=slide('Performance depends strongly on the environment','21 Oct / 141 structures','Source: environment_v1/environment_summary.json at agent 800ba03. Counts plotted are observed, not exact baseline expectations. Important correction to collaborator prose: chloride random is 29/30, while all four LLM arms are 30/30. Each environment has 30 runs/arm. Primary endpoint unchanged.','Successful runs out of 30 after ten queries. Same LiCoO₂ cathode.');
chart(s,'bar',{position:{left:56,top:214,width:1168,height:380},categories:['Li₆PS₅Cl / sulfide','Li₃InCl₆ / chloride','LLZO / oxide'],series:E.arm_order.map(a=>({name:ARM[a].name,values:E.environment_order.map(env=>E.environments[env].counts[a]),fill:ARM[a].color})),hasLegend:true,legend:{position:'bottom',textStyle:{fontSize:23,fill:C.ink}},barOptions:{direction:'column',grouping:'clustered',gapWidth:75},xAxis:{...axis,majorGridlines:null},yAxis:{...axis,min:0,max:30,majorUnit:10},dataLabels:{showValue:true,position:'outEnd',textStyle:{fontSize:23,bold:true,fill:C.ink}}});
note(s,'Sulfide: feedback helps. Chloride: predicted ceiling. LLZO: random wins.',615,C.teal);
}
// 10. Curves as native editable charts.
{
const s=slide('On LLZO, adaptation arrives late','Budget trajectories','Cumulative success reconstructed exactly from first_acceptable_counts in frozen production analysis. Lines show empirical rates across 30 runs; exact random is a combinatorial expectation, not an additional sampled arm. This figure intentionally omits interval bands for readability; Wilson intervals and raw counts remain in the archived analysis. This is a budgeted query benchmark, not timing of costly evaluations.');
const configs=[['Li6PS5Cl','Sulfide',56],['Li7La3Zr2O12','LLZO',658]];
for(const [env,label,x] of configs){text(s,label,x,195,550,44,30,C.ink,true);const d=E.environments[env];chart(s,'line',{position:{left:x,top:246,width:560,height:332},categories:Array.from({length:10},(_,i)=>String(i+1)),series:['iterative','sequential','shuffled','upfront'].map(a=>lineSeries(a,d.curves[a])).concat([{name:'Exact random',values:d.random_exact_curve,line:{fill:C.gray,width:3,style:'dashed'},marker:{symbol:'none'}}]),hasLegend:false,xAxis:{...axis,title:{text:'Charged query',textStyle:{fontSize:22}},majorGridlines:null},yAxis:{...axis,min:0,max:1,majorUnit:0.25,numberFormatCode:'0%',title:{text:'Acceptable found',textStyle:{fontSize:21}}}});}
[['Iterative',C.teal],['Sequential',C.blue],['Shuffled',C.orange],['Upfront',C.purple],['Exact random',C.gray]].forEach(([l,c],i)=>text(s,l,58+i*237,592,230,35,23,c,true));
text(s,'LLZO: 10 of 12 iterative successes first appear at queries 8–10.',56,636,1168,32,24,C.muted);
}
// 11. Actual chemical decisions.
{
const s=slide('Where the LLM substitutes chemical intuition','One recorded sulfide trajectory','Source: environment_v1/lpscl/iterative_r202.json and SYNC_DAVIDE_7.md. Trace selection rule was lowest seed at typical first-hit index before reading rationales. This is an illustrative trace, not independently proven chemistry. Reported values are rounded actual evaluator penalties. Earlier failures include Li2O, Li3PO4, LiF, LiAlO2.','After familiar oxides and LiF fail, Haiku refines mixed-cation fluoride chemistry.');
table(s,[['Query','Chosen material','Observed penalty','Decision pattern'],['6','Li₃AlF₆','0.160','Test Al-containing fluoride'],['7','LiMgAlF₆','0.057','Change cation chemistry'],['8','LiCaAlF₆','0.048: acceptable','Refine a near-threshold candidate']], [125,250,280,513],{height:302,font:28});
text(s,'The delegated act is connecting a failed result to a new chemical proposal.',56,559,1168,60,32,C.teal,true);
note(s,'Penalties: eV / non-Li atom. The proposed mechanism is a hypothesis, not a verified explanation.',635);
}
// 12. LLZO caveat and concentration.
{
const s=slide('A narrow prior can lose to broad exploration','LLZO failure analysis','Source: data/reviews/llzo_chemistry_audit_20261021.json. Formula counts are across all 300 picks of an arm, not per run. Iterative has 29 acceptable picks, 28 at queries 6–10 and 26 from LiAlSiO4 polymorphs. Random has 33 acceptable picks. The pattern supports delayed/narrow adaptation, but rationales do not prove a mechanistic explanation.','Three hundred picks per arm. Random spreads its budget across more chemistry.');
table(s,[['Arm','Distinct formulas','Acceptable picks','Successful runs'],['Random','95','33 / 300','24 / 30'],['Iterative','33','29 / 300','12 / 30'],['Upfront','22','1 / 300','1 / 30'],['Sequential','19','0 / 300','0 / 30']], [290,282,298,298],{height:340,font:26});
note(s,'Iterative finds acceptable materials late and repeatedly visits LiAlSiO₄ polymorphs.',587,C.teal);
text(s,'A post-hoc chemical audit flags 5 of 17 acceptable structures. The frozen result stays unchanged.',56,636,1168,33,22,C.muted);
}
// 13. Prospective physical pilot.
{
const s=slide('The expensive pilot makes intuition falsifiable','22 Oct / prospective PET-MAD pilot','Sources: live state, execution records, frozen manifest 99ef2dc1…, final index. Initial shortlist LiTaF6, LiCaAlF6, LiF. Known reference LiNbF6. Sensitivity values were withheld until summary. LiF was thermodynamically ineligible under this frozen condition and not selected. Feasibility/menu and atom-cap amendment were fixed before new interface energies. No claim of a repeated expensive-search comparison.','One known reference, three feasible alternatives, two new coating evaluations.');
table(s,[['Stage','LLM responsibility','Physical evidence'],['Before a new coating','Choose the material and forecast both contacts','Reference LiNbF₆ only'],['After LiTaF₆','Assess its earlier forecasts and choose again','Six primary jobs, three registries per contact'],['After LiCaAlF₆','Explain what held and what failed','Six further primary jobs']], [270,485,413],{height:300,font:26});
note(s,'The order stayed LiTaF₆ then LiCaAlF₆. This pilot tests predictions, not search superiority.',559,C.red);
text(s,'PET-MAD S 1.6.0 (r²SCAN). Robustness results were released after the final LLM response.',56,634,1168,35,23,C.muted);
}
// 14. Main physical chart.
{
const s=slide('All three coatings have a weaker electrolyte contact','Common-protocol physical comparison','Source: index_final.json with SHA-256 '+E.sources.final_index_sha256+'. Selected registry minimizes relaxed joined-interface energy per contact. These are three material-specific constructions under shared selection and relaxation rules, not identical cells/facets. LiNb primary reused, five saved registry cases; six new primary jobs per other coating. Primary numeric selections unchanged after robustness release.');
const fs=['LiNbF6','LiTaF6','LiCaAlF6'];chart(s,'bar',{position:{left:56,top:214,width:1168,height:380},categories:['LiNbF₆ (reference)','LiTaF₆ (choice 2)','LiCaAlF₆ (choice 3)'],series:[{name:'Cathode contact',values:fs.map(f=>E.physical[f].contacts.cathode.W_adh_J_m2),fill:C.blue},{name:'Electrolyte contact',values:fs.map(f=>E.physical[f].contacts.electrolyte.W_adh_J_m2),fill:C.teal}],hasLegend:true,legend:{position:'bottom',textStyle:{fontSize:24,fill:C.ink}},barOptions:{direction:'column',grouping:'clustered',gapWidth:80},yAxis:{...axis,min:0,max:4,majorUnit:1,title:{text:'Wadh (J/m²)',textStyle:{fontSize:24}}},xAxis:{...axis,majorGridlines:null},dataLabels:{showValue:true,position:'outEnd',numberFormatCode:'0.00',textStyle:{fontSize:26,bold:true,fill:C.ink}}});
note(s,'Provisional adhesion for formally polar model contacts. LiF was not physically evaluated.',613,C.red);
}
// 15. Forecasts, literal ranges.
{
const s=slide('The analogy worked for Ta, failed for Ca–Al','Prospective forecast checks','Source: report_live/report.md and state.json at agent 800ba03; all ranges recorded before corresponding interface energies. The ranges are model forecasts, not calibrated confidence intervals. Weak contact predicted electrolyte for both and confirmed. Cathode Ca lower miss 1.573 J/m², electrolyte lower miss 0.656. The second selection matched the original shortlist, so feedback did not demonstrably change order.','All forecasts were recorded before the new coating’s calculations.');
table(s,[['Coating / contact','Forecast Wadh','Observed','Check'],['LiTaF₆ / cathode','3.2–3.9','3.339','In range'],['LiTaF₆ / electrolyte','1.4–1.9','1.577','In range'],['LiCaAlF₆ / cathode','3.0–3.8','1.427','Below range'],['LiCaAlF₆ / electrolyte','1.4–1.9','0.744','Below range']], [440,280,220,228],{height:355,font:27});
note(s,'The weak contact was predicted correctly twice. Haiku acknowledged the Ca–Al forecast failure.',601,C.teal);
text(s,'Units: J/m². Two material choices do not establish forecast calibration or search advantage.',56,642,1168,28,21,C.muted);
}
// 16. Robustness.
{
const s=slide('A small ranking gap is not a robust materials winner','Uncertainty and model limits','Source: FINAL_PILOT_REVIEW.md, FINAL_COMPARISON.md, final index. Nb−Ta weaker-contact gap = '+fmt(E.physical.LiNbF6.contacts.electrolyte.W_adh_J_m2-E.physical.LiTaF6.contacts.electrolyte.W_adh_J_m2)+'. Seed changes combine bulk ordering, strain, cell, area and fixed-set effects, not isolated disorder uncertainty. They are finite sensitivity tests, not confidence intervals. Ca available checks ≤0.014 do not quantify missing thickness and bulk slots.');
table(s,[['Observation','Magnitude','What we can conclude'],['LiNbF₆ versus LiTaF₆\nweaker-contact gap','0.056 J/m²','Too small to establish a robust winner'],['Alternative electrolyte structure\nNb and Ta','−0.121 / −0.114 J/m²','Construction sensitivity exceeds that gap'],['LiCaAlF₆ electrolyte\nregistry range','0.523–0.744 J/m²','Substantially lower primary adhesion'],['LiCaAlF₆ electrolyte\nthickness and bulk structure','Unquantified','Four passing checks do not close these gaps']], [455,285,428],{top:199,height:380,font:24});
note(s,'All contact models are formally polar. Numerical convergence is not physical validation.',611,C.red);
}
// 17. Original design mapping.
{
const s=slide('What survived the original design, and what changed','Review against the initial idea','Sources: DISCOVERY_REPORT.md, DISCOVERY_IMPLEMENTATION_PLAN.md, EXPERIMENT_AMENDMENT.md, physical pilot protocol, final review. Initial tiny pool and exact float lexicographic objective were repaired before definitive runs. The user explicitly chose design A: cheap exhaustive benchmark, then limited MLIP follow-up. This deck distinguishes that agreed design from the earlier full-mode search ambition.');
table(s,[['Original intent','What we achieved','Assessment'],['Delegate scientific intuition','Choices, feedback interpretation, forecasts','Implemented and tested'],['Distinguish reasoning from recall','Five arms, 30 runs, shuffled feedback','Feedback benefit is conditional'],['Find better coatings efficiently','Exhaustive benchmark, environment transfer','No general win over random'],['Compare 3–5 coatings with MLIP','Three coatings, two contacts, robustness','Lower end reached; LiF unrun'],['Accelerate real materials discovery','Candidate prioritization under proxies','Not physically validated']], [340,555,273],{top:204,height:386,font:24});
note(s,'Stronger evaluation than the initial plan. A narrower discovery claim than the initial ambition.',620,C.teal);
}
// 18. Final main slide.
{
const s=slide('An auditable test of scientific judgment','What we should claim','This is a synthesis and interpretation, not an additional statistical test. Supported: true feedback changes performance under specified tasks, prospective predictions can be tested, limits of narrow priors and proxy objectives are exposed. Not supported: new composition discovery, general reasoning superiority, validated battery coating, or proven compute savings. Next priorities must preserve frozen primary results and use new predeclared experiments.');
text(s,'An LLM can take over a bounded part of the scientist’s job:\nchoose a hypothesis, test it, and reassess it.',56,217,1168,130,38,C.teal,true);
text(s,'Our evidence shows where that helps: the sulfide benchmark.\nIt also shows where it fails: narrow exploration on LLZO\nand failed transfer to LiCaAlF₆.',56,374,1168,149,31,C.ink);
text(s,'Next: improve exploration, add practical coating constraints,\nand test expensive selection across more independent decisions.',56,563,1168,90,28,C.muted);
}
// 19. Exact preregistered statistics.
{
const s=slide('Three of six planned contrasts survive correction','Backup / statistical evidence','Source: environment_summary.json contrasts. Two-sided exact paired McNemar, seeds 200–229, Holm across all six comparisons. The chloride contrasts have no discordant pairs, p=1. Random comparisons are descriptive relative to the preregistered six-test family; no new p-value added.');
const vals=[['Environment / contrast','Discordant I : control','Raw p','Holm p']];for(const [env,label] of [['Li6PS5Cl','Sulfide'],['Li3InCl6','Chloride'],['Li7La3Zr2O12','LLZO']])for(const a of ['sequential','shuffled']){const d=E.environments[env].contrasts['iterative-'+a];vals.push([label+' / '+a,d.left_only+' : '+d.right_only,d.p<.001?d.p.toExponential(2):d.p.toFixed(4),d.p_holm<.001?d.p_holm.toExponential(2):d.p_holm.toFixed(4)]);}
table(s,vals,[470,308,195,195],{top:199,height:405,font:24,header:23});note(s,'Primary endpoint: at least one acceptable coating within ten charged queries.',628);
}
// 20. Metric caveats.
{
const s=slide('Acceptability, optimum-finding and practicality differ','Backup / objective interpretation','Sources: frozen objective and environment analysis. Two acceptable structures in 50; 4/141 sulfide,55/141 chloride,17/141 LLZO. P cutoff0.050 crosses bin2 underwidth0.020. Best-bin success is a separate endpoint. Expanded sulfide iterative6 random5; LLZO allLLM0 random2. Missing/invalid/ineligible candidates cannot pass. Threshold not changed after outcomes.');
table(s,[['Question','Measure','Observed limitation'],['Can the policy find a passing candidate?','Acceptance at P ≤ 0.050','This is the primary reported result'],['Does it find the pool’s optimum?','Best-bin discovery / regret','Sulfide: iterative 6, random 5\nLLZO: all LLMs 0, random 2 (of 30)'],['Is the actual coating useful?','Transport, processing, electrochemistry','Not established by this evaluator'],['Is the search saving compute?','Cost of avoided expensive evaluations','Cheap tables alone cannot show this']], [365,365,438],{height:355,font:25});
note(s,'Acceptance cuts through a ranking bin. Near-threshold conclusions depend on the frozen definition.',609);
}
// 21. LLZO posthoc.
{
const s=slide('The LLZO audit qualifies the criterion, not the score','Backup / post-hoc chemistry review','Source: data/reviews/llzo_chemistry_audit_20261021.json and SYNC_ADEM_10.md. LiIO3 and LiClO4 have supplier oxidizer classifications; Li5IO6 is a family-level review flag, not verified compound-specific GHS. Supplier links and original reference are preserved in the audit JSON. Evaluator does include O2 products, so do not claim it cannot form gas. No evidence that Haiku deliberately avoided these candidates. Frozen criterion unchanged.');
text(s,'5 of 17 acceptable structures were flagged for practical review:\nLiIO₃, LiClO₄ and Li₅IO₆.',56,215,1168,107,34,C.ink,true);
table(s,[['Random’s 24 successful runs','Count'],['Also found an unflagged acceptable candidate','18'],['Succeeded only through a flagged candidate','6']], [935,233],{top:355,height:198,font:27});
note(s,'This is a descriptive partition, not a rerun with a new endpoint. Primary result: 24 versus 12.',588,C.red);
text(s,'The model is not proven to be making a safety judgment. Finite-temperature and processing limits remain.',56,637,1168,32,22,C.muted);
}
// 22. Wadh/Wsep fulltable.
{
const s=slide('Relaxed adhesion and rigid separation are different','Backup / final physical values','Source: final index; Wadh = (relaxed constrained separated slab energies − relaxed joined interface energy)/area, same model and reference conventions. Wsep uses separated fragments frozen at the joined geometry. It is not an experimental fracture toughness. Large Wsep−Wadh indicates relaxation of freed surfaces within this protocol. Chosen registry minimizes joined energy, not max Wadh.');
table(s,[['Coating','Cathode\nWadh / Wsep','Electrolyte\nWadh / Wsep','Atoms\nC / E'],...['LiNbF6','LiTaF6','LiCaAlF6'].map(f=>[f.replaceAll('6','₆'),fmt(E.physical[f].contacts.cathode.W_adh_J_m2)+' / '+fmt(E.physical[f].contacts.cathode.W_sep_J_m2),fmt(E.physical[f].contacts.electrolyte.W_adh_J_m2)+' / '+fmt(E.physical[f].contacts.electrolyte.W_sep_J_m2),E.physical[f].contacts.cathode.n_atoms+' / '+E.physical[f].contacts.electrolyte.n_atoms])], [260,355,355,198],{height:300,font:28});
text(s,'Wadh: separated slabs are allowed to relax.\nWsep: fragments retain their joined-interface geometry.',56,547,1168,83,28,C.teal);
text(s,'J/m². Primary snapshots unchanged. Later robustness checks are a separate record.',56,641,1168,27,22,C.muted);
}
// 23. Actual structure figure, not an illustrative reconstruction.
{
const s=slide('The structures and convergence evidence are archived','Backup / physical realization','Source image: data/petmad/niflheim_batch1/cathode_reg_third_third/inspection.png at davide750b382. Actual LiCoO2(001)|LiNbF6(001), 696 atoms, selected (1/3,1/3) registry. Force trace is maximum free-atom force; fixed atoms are excluded. Their residual force remains a limitation. Vacuum isolation reflects finite-range8Å model, not long-range polar convergence.');
const b=await fs.readFile(path.join(ROOT,'data/petmad/niflheim_batch1/cathode_reg_third_third/inspection.png'));s.images.add({blob:b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength),contentType:'image/png',alt:'Archived 696-atom LiCoO2 and LiNbF6 structure before and after relaxation, and free-atom force convergence',fit:'contain',position:{left:130,top:193,width:1020,height:475}});
}
// 24. Evidence and remaining work.
{
const s=slide('The result is reproducible; integration remains separate','Backup / accounting and handoff','Sources: FINAL_PILOT_REVIEW.md, environment production archive, job accounting and git heads. Finalreader integration patch prepared but not applied to agent800ba03. Physics165tests and agent32 targeted tests verified in prior review; patch39tests in isolated archive. This synthesis does not rerun those code tests or merge branches. Primary packets and later robustness indices remain distinct. Prices are logged list-rate arithmetic, not current advertised prices or billing verification.');
table(s,[['Evidence / cost','Verified record'],['Environment study','450 runs, 2,800 API calls, about $3.63 at recorded list rates'],['Physical pilot LLM','5 / 10 HTTP attempts, about $0.006 at recorded list rates'],['New PET-MAD jobs','26 / 36, all converged, 6,632 runner calls + 52 single points'],['Compute time','25.4 min runner time; 47.5 min summed Slurm elapsed\nReused work, bulk preparation and queue time are separate'],['Remaining delivery work','Apply final-index reader patch, review combined diff, merge,\nand synchronize the structure viewer']], [340,828],{top:207,height:389,font:24});
note(s,'Frozen decisions, later robustness, source hashes and limitations remain independently inspectable.',627);
}

await fs.mkdir(BUILD,{recursive:true});await fs.mkdir(OUT,{recursive:true});
await fs.writeFile(path.join(BUILD,'slides.json'),JSON.stringify(MANIFEST,null,2));
await fs.writeFile(path.join(BUILD,'font.json'),JSON.stringify({basis:'design',families:[FONT]}));
const candidate=path.join(BUILD,'candidate_v2.pptx');
await (await PresentationFile.exportPptx(P)).save(candidate);
console.log('Exported draft',candidate,'slides',P.slides.items.length,'font',FONT);
const finalPath=path.join(OUT,'interphAIse_results_synthesis_2026-10-22_v2.pptx');
await finalizePresentation({workspaceDir:ROOT,candidatePath:candidate,finalPath,pythonExecutable:path.join(RUNTIME,'python/bin/python3'),integrityValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',...[...new Set(TABLES)].flatMap(n=>['--require-native-table-slide',String(n)])],requiredNativeTableOwnerSlides:[...new Set(TABLES)],requiredNativeChartOwnerSlides:[...new Set(CHARTS)],materializeLiteralChartWorkbooks:true,fontPolicy:{basis:'design',families:[FONT]},verifyArtifactToolImport:true,receiptPath:path.join(BUILD,'validation_v2.json')});
console.log('Finalized',finalPath);
// Render the actual finalized artifact, including workbook repair and roundtrip.
const final=await PresentationFile.importPptx(await FileBlob.load(finalPath));
await fs.mkdir(path.join(BUILD,'rendered'),{recursive:true});
for(let i=0;i<final.slides.items.length;i++){const blob=await final.export({slide:final.slides.items[i],format:'png',scale:1});await fs.writeFile(path.join(BUILD,'rendered',`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await blob.arrayBuffer()));console.log('Rendered',i+1);}
console.log('DONE');
