// Reframe the reviewed presentation for a mixed scientific/non-expert audience.
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {pathToFileURL} from 'node:url';
process.on('uncaughtException',e=>{console.error(e.message);console.error(e.stack?.split('\n').slice(1,6).join('\n'));process.exit(1);});
const ROOT=process.env.INTERPHAISE_ROOT || process.cwd();
const RUNTIME='/Users/davidetisi/.cache/codex-runtimes/codex-primary-runtime/dependencies';
const SKILL='/Users/davidetisi/.codex/plugins/cache/openai-primary-runtime/presentations/26.1015.12040/skills/presentations';
process.env.RUNTIME_NODE_MODULES ||= path.join(RUNTIME,'node/node_modules');
const {PresentationFile,FileBlob}=await import(pathToFileURL(path.join(RUNTIME,'node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs')).href);
const {applyPresentationChartFont,finalizePresentation}=await import(pathToFileURL(path.join(SKILL,'container_tools/artifact_tool_utils.mjs')).href);
const BUILD=path.join(ROOT,'presentations/.build/nonexpert_story');
const OUT=path.join(ROOT,'presentations/nonexpert_2026-10-22');
await fs.mkdir(BUILD,{recursive:true});await fs.mkdir(OUT,{recursive:true});
const SOURCE=path.join(ROOT,'presentations/results_2026-10-22/interphAIse_results_synthesis_2026-10-22_v2.pptx');
const sourceHash=crypto.createHash('sha256').update(await fs.readFile(SOURCE)).digest('hex');
const E=JSON.parse(await fs.readFile(path.join(ROOT,'presentations/source/results_synthesis_2026-10-22.json'),'utf8'));
const P=await PresentationFile.importPptx(await FileBlob.load(SOURCE));
await fs.writeFile(path.join(BUILD,'source-inspection.ndjson'),(await P.inspect({select:'$.slides[*]',include:['id','index','title','layout','elements.id','elements.kind','elements.text','elements.position','notes.text']})).ndjson);
await fs.writeFile(path.join(BUILD,'source-layouts.ndjson'),(await P.inspect({kind:'layout',maxChars:50000})).ndjson);
await fs.writeFile(path.join(BUILD,'source-masters.json'),JSON.stringify({masters:P.masters.items.map(x=>({id:x.id,name:x.name})),placeholders:P.slides.items.map(s=>({id:s.id,items:s.placeholders.items.map(x=>({name:x.name,id:x.id}))}))},null,2));
// Retain the source cover and all six technical backups. Rebuild the main narrative.
P.slides.keep([0,18,19,20,21,22,23]);
const FONT='Helvetica Neue';
const C={bg:'#FAFAF7',ink:'#172B3A',muted:'#526472',rule:'#D6DEDE',teal:'#007F7B',blue:'#366AA8',orange:'#CA713A',purple:'#9076A9',gray:'#8A949C',red:'#A44838',white:'#FFFFFF'};
const ARM={iterative:{label:'Uses results',color:C.teal},sequential:{label:'No results',color:C.blue},shuffled:{label:'Mixed-up results',color:C.orange},upfront:{label:'One list',color:C.purple},random:{label:'Random',color:C.gray}};
const created=[],tables=[],charts=[],manifest=[];
const SRC={synthesis:'RESULTS_SYNTHESIS_2026-10-22.md',protocol:'ENVIRONMENT_PROTOCOL.md',original:'INTEGRATED_DISCOVERY_RESULTS.md',pilot:'FINAL_PILOT_REVIEW.md',evidence:'presentations/source/results_synthesis_2026-10-22.json',audit:'data/reviews/llzo_chemistry_audit_20261021.json'};
function notes(s,explanation,refs){s.speakerNotes.text=explanation+'\n\nSources:\n'+refs.map(r=>path.join(ROOT,SRC[r]||r)).join('\n')+'\n\nArchived outcome commits: agent '+E.sources.agent_commit+'; physics '+E.sources.physics_commit+'. Original benchmark source: '+E.sources.davide_commit+'.';}
function text(s,str,x,y,w,h,size=28,color=C.ink,bold=false){const q=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});q.text=str;q.text.style={typeface:FONT,fontSize:size,color,bold,autoFit:'none',wrap:'square',insets:0,verticalAlignment:'top'};return q;}
function slide(title,section,subtitle=''){const s=P.slides.add();s.background.fill=C.bg;created.push(s);text(s,section.toUpperCase(),56,27,1110,26,18,C.teal,true);text(s,title,56,74,1168,108,44,C.ink,true);if(subtitle)text(s,subtitle,56,155,1168,60,27,C.muted);text(s,'interphAIse  /  Results through 22 October 2026',56,679,1090,24,17,C.muted);text(s,'00',1160,677,64,28,19,C.muted);manifest.push({title,section});return s;}
function note(s,str,y=615,color=C.muted){text(s,str,56,y,1168,53,24,color);}
function table(s,values,widths,{top=225,height=325,font=27,header=24}={}){const t=s.tables.add({rows:values.length,columns:widths.length,left:56,top,width:1168,height,values,columnWidths:widths});tables.push(s);t.styleOptions={headerRow:false,bandedRows:false};t.borders.assign({fill:C.rule,width:0.6,style:'solid'});values.forEach((row,i)=>{t.rows[i].height=height/values.length;row.forEach((_,j)=>{const c=t.getCell(i,j);c.fill=i===0?C.ink:C.bg;c.text.style={typeface:FONT,fontSize:i===0?header:font,color:i===0?C.white:C.ink,bold:i===0,autoFit:'none',insets:0};});});t.cells.block({row:0,column:0,rowCount:values.length,columnCount:widths.length}).assign({margins:{left:14,right:12,top:5,bottom:5},anchor:'center'});return t;}
function chart(s,type,config){const q=s.charts.add(type,{chartFill:C.bg,plotAreaFill:C.bg,chartLine:{fill:'none',width:0},plotAreaLine:{fill:'none',width:0},...config,series:config.series.map(v=>({...v,smooth:false,values:v.values.map(x=>Number(x.toPrecision(10)))}))});applyPresentationChartFont(q,{fontFamily:FONT});charts.push(s);return q;}
const axis={textStyle:{fontSize:23,fill:C.ink},line:{fill:C.rule,width:1},majorGridlines:{fill:C.rule,width:1}};
function line(s,n,heading,body,y){text(s,n,56,y,90,62,43,C.teal,true);text(s,heading,174,y,1035,46,31,C.ink,true);text(s,body,174,y+49,1035,70,28,C.muted);}
// 1: edit the original cover in place.
{
 const cover=P.slides.items[0];
 const changes=new Map([
 ['MATERIALS DISCOVERY WITH COMPUTATIONAL FEEDBACK','AI-GUIDED BATTERY COATINGS'],
 ['Can an LLM choose\nthe next useful\nmaterials calculation?','Can an LLM choose\nthe next battery\ncoating to test?'],
 ['From a controlled search benchmark to a prospective\nthree-coating PET-MAD comparison','Why the LLM matters\nWhat it achieved, step by step']
 ]);
 for(const e of (await P.inspect({select:'$.slides[0]',include:['elements.id','elements.text']})).records[0].elements??[]){if(changes.has(e.text))P.resolve(e.id).text.replace(e.text,changes.get(e.text));}
 notes(cover,'Opening: interphAIse asks whether an AI language model can take on one part of scientific work: deciding which material deserves the next calculation. We will explain the battery problem, the decision loop, and three stages of evidence. Main talk: slides 1–16, approximately 15 minutes. Slides 17–22 are technical backup. Authors: Davide Tisi and Adem R. N. Aouichaoui. The LLM is Haiku 5.5. All outcomes are from the completed archived studies through 22 October 2026.',['synthesis','evidence']);
}
// 2: concrete problem before chemical formulas.
{
 const s=slide('The problem: a protective layer inside a battery','The idea','The cathode stores lithium. The electrolyte lets lithium ions move.');
 const b=await fs.readFile(path.join(ROOT,'presentations/source/nonexpert_assets/coating-concept.png'));
 s.images.add({blob:b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength),contentType:'image/png',fit:'contain',alt:'Conceptual cathode, thin protective coating and solid electrolyte touching at two interfaces. Not to scale.',position:{left:56,top:205,width:705,height:455}});
 text(s,'A useful coating must',795,223,424,48,30,C.ink,true);
 text(s,'Limit unwanted reactions\nat both contacts.',795,302,424,95,29,C.teal,true);
 text(s,'Stay attached to the\nneighboring materials.',795,420,424,96,29,C.blue,true);
 text(s,'Lithium ions must also pass\nthrough. That was not tested.',795,552,424,92,26,C.muted);
 notes(s,'A cathode is an electrode that stores lithium. The solid electrolyte carries lithium ions between electrodes. Where these materials touch, unwanted reactions and poor contact can be problems. The coating is a very thin protective layer between them, so it has two contacts to satisfy. The project tests chemical compatibility and simulated adhesion separately. The broad battery objective also requires lithium transport, synthesis and cycling, which were outside these tests. Image is an AI-generated conceptual illustration, not a simulation or an experimental image.',['synthesis','README.md','presentations/source/nonexpert_assets/provenance.json']);
}
// 3: central role, with a clear division of scientific labor.
{
 const s=slide('Why the LLM is central','The decision being tested','LLM = large language model. Here, it chooses what to calculate next.');
 line(s,'01','Connect chemistry to a candidate','Choose a known material and explain why it might work.',233);
 line(s,'02','Use the last result','Read what failed or nearly passed, then choose the next test.',357);
 line(s,'03','Make a prediction that can fail','State an expected result before the physical calculation.',481);
 note(s,'Researchers define the task. The LLM makes choices. The physics tools calculate the results.',629,C.teal);
 notes(s,'The motivation is that a calculator can score a specified material but does not itself decide which chemical idea is worth pursuing. The LLM supplies that selection judgment and can express a hypothesis in words. This is why it is central to the experiment. Humans still define the candidate menu, scoring rule, budget and scientific interpretation. Deterministic code validates the choices and reveals numerical results. We measure the quality of the decisions, not whether the model internally reasons like a human. The LLM selects existing structure IDs, rather than inventing new compositions.',['synthesis','DISCOVERY_REPORT.md']);
}
// 4: the repeatable loop in ordinary language.
{
 const s=slide('One decision loop, repeated after each result','How it works');
 line(s,'1','LLM: choose a material','Record the proposed coating and its chemical rationale.',190);
 line(s,'2','Tool: test the material','Return a numerical result from the defined calculation.',302);
 line(s,'3','LLM: interpret the feedback','Compare the result with the earlier expectation.',414);
 line(s,'4','LLM: choose the next test','Continue until the evaluation budget is used.',526);
 notes(s,'Read these steps as a loop: the fourth step becomes the next first step. In the controlled search benchmark the numerical feedback is read from a precomputed thermodynamic table. The LLM cannot see the full answer table. In the later physical pilot, new interface calculations follow choices and numerical forecasts that have already been recorded. Keeping these two forms of testing distinct prevents a false claim that the cheap benchmark saved expensive compute.',['synthesis','protocol','pilot']);
}
// 5: success is understandable before any chart.
{
 const s=slide('First test: can it find a coating that passes?','Step 1 / controlled selection');
 text(s,'Choose from a fixed menu of known materials.',56,213,1168,58,34,C.ink,true);
 text(s,'A calculation scores unwanted chemical reactions.\nA material passes only if it meets the preset limits.',56,303,1168,105,32,C.muted);
 text(s,'10 tries',56,463,360,80,58,C.teal,true);
 text(s,'per search',56,551,360,50,30,C.ink);
 text(s,'30 searches',510,463,650,80,58,C.teal,true);
 text(s,'per strategy, with varied candidate order',510,551,680,50,30,C.ink);
 note(s,'“Success” means finding at least one passing material. It does not mean a working battery.',626,C.red);
 notes(s,'The original menu contains 50 structure IDs representing 43 formulas. Two structures pass. Each strategy receives ten charged evaluations, repeated 30 times. Unknown, duplicate and failed queries still consume budget. The pass rule combines a thermodynamic reaction penalty no greater than 0.050 eV per non-Li atom with a band-gap proxy for electronic insulation of at least 2 eV. Lower reaction penalty is better. The rule was frozen before decisive runs. It is a screening criterion, not a demonstration of useful battery performance.',['original','protocol','evidence']);
}
// 6: plain labels for the controls, reused on all main charts.
{
 const s=slide('Five strategies make the comparison fair','Step 1 / comparison','The same menu, the same ten tries, and the same definition of success.');
 table(s,[['Strategy used in the charts','How the next choice is made'],['Uses results','LLM sees the outcomes of its earlier choices'],['No results','LLM sees its choices, but not their outcomes'],['Mixed-up results','LLM sees outcomes reassigned between materials'],['One list','LLM chooses all ten materials before any result'],['Random','Software picks materials at random, without repeats']],[380,788],{height:371,font:27,header:25});
 note(s,'The first four use the same LLM. Random search provides a simple comparison.',624);
 notes(s,'The archived names are iterative, sequential, shuffled, upfront and random. The shorter labels used in the main talk explain what differs. No-results retains earlier choices and rationales. Mixed-up results tests whether correct attribution matters, although occasional correct assignments and contradictions with earlier rationales remain limitations. All LLM arms use Haiku 5.5, temperature 1.0. No single comparison proves an internal reasoning mechanism.',['protocol','synthesis']);
}
// 7: original complete five-arm result.
{
 const s=slide('Using results improved the first search test','Step 1 / result','Successful searches out of 30, using the original 50-structure menu.');
 const arms=E.arm_order;
 chart(s,'bar',{position:{left:56,top:220,width:1168,height:365},categories:arms.map(a=>ARM[a].label),series:[{name:'Successful searches',values:arms.map(a=>E.original[a].count),points:arms.map((a,idx)=>({idx,fill:ARM[a].color}))}],hasLegend:false,barOptions:{direction:'column',grouping:'clustered',gapWidth:90,varyColors:true},xAxis:{...axis,majorGridlines:null},yAxis:{...axis,min:0,max:30,majorUnit:10,title:{text:'Successful searches / 30',textStyle:{fontSize:23}}},dataLabels:{showValue:true,position:'outEnd',textStyle:{fontSize:29,bold:true,fill:C.ink}}});
 note(s,'Correct feedback helped: 19 successes, versus 4 without results and 6 with mixed-up results.',604,C.teal);
 notes(s,'This combines 120 original runs with the matched 30-run shuffled follow-up. Counts are 19, 4, 6, 4 and 10. Do not add the earlier ten-run preview. Exact random expectation is 36.33%, compared with the observed random 10/30. Iterative versus shuffled paired exact McNemar p is about 0.0044, unadjusted. The evidence supports useful feedback in this task. A fluoride-first rule designed after seeing the table succeeds by query two, so this result does not establish superiority over every simpler policy. The original candidate pool overlaps the expanded pool.',['original','synthesis','evidence']);
}
// 8: expansion and its negative result on one readable chart.
{
 const s=slide('The benefit changed with the battery materials','Step 2 / a larger test','141 structures, three electrolytes, 450 searches across all five strategies.');
 const shown=['iterative','sequential','random'];
 chart(s,'bar',{position:{left:56,top:220,width:1168,height:365},categories:['Sulfide','Chloride','Oxide (LLZO)'],series:shown.map(a=>({name:ARM[a].label,values:E.environment_order.map(env=>E.environments[env].counts[a]),fill:ARM[a].color})),hasLegend:true,legend:{position:'bottom',textStyle:{fontSize:24,fill:C.ink}},barOptions:{direction:'column',grouping:'clustered',gapWidth:95},xAxis:{...axis,majorGridlines:null},yAxis:{...axis,min:0,max:30,majorUnit:10,title:{text:'Successful searches / 30',textStyle:{fontSize:23}}},dataLabels:{showValue:true,position:'outEnd',textStyle:{fontSize:27,bold:true,fill:C.ink}}});
 text(s,'Feedback helped',106,603,344,45,29,C.teal,true);
 text(s,'Almost all succeeded',451,603,390,45,29,C.ink,true);
 text(s,'Random did better',879,603,345,45,29,C.orange,true);
 notes(s,'The electrolyte is the material carrying lithium ions. Changing it changes which coatings pass, even though the cathode remains LiCoO2 at 4 V. There are 4/141 passing structures in sulfide, 55/141 in chloride and 17/141 in LLZO. The chart shows three of the five strategies for clarity; all five counts and planned statistics are in backup slide 17. Sulfide counts are 20,2,6,0,8; chloride 30,30,30,30,29; LLZO 12,0,4,1,24, in iterative,sequential,shuffled,upfront,random order. Every run begins fresh: this is not learning transferred between environments. The expanded pool includes the original 50 structures. Do not pool those studies as independent replications.',['protocol','synthesis','evidence']);
}
// 9: a concrete observed decision sequence.
{
 const s=slide('A real example: refining a near miss','Step 2 / what the LLM did','Three consecutive choices in one sulfide search. Lower reaction score is better.');
 table(s,[['Try','Material chosen','Reaction score','What the test said'],['6','Li₃AlF₆','0.160','Does not pass'],['7','LiMgAlF₆','0.057','Close, but still above the limit'],['8','LiCaAlF₆','0.048','Passes the 0.050 limit']],[120,280,265,503],{height:288,font:29,header:25});
 text(s,'The LLM kept testing related chemistry after a promising near miss.',56,550,1168,76,33,C.teal,true);
 note(s,'One illustrative search. Reaction scores are in eV per non-lithium atom.',637);
 notes(s,'This is sulfide seed 202. The trace was chosen in the earlier analysis using the lowest seed with a typical first-hit position, before reading the rationales. The model tried familiar oxides and LiF unsuccessfully, then explored mixed-cation fluorides. It interpreted the 0.057 result as a near miss and chose the Ca analogue. The values are recorded scores in eV per non-Li atom, rounded to three decimals. Its proposed chemical explanation is a hypothesis, not a verified reaction mechanism. The observed sequence makes the delegated judgment concrete without treating one attractive example as proof. Source archive: agent commit, data/experiments/environment_v1/lpscl/iterative_r202.json.',['synthesis','evidence']);
}
// 10: why the loss matters, using simple quantities.
{
 const s=slide('On the oxide, the LLM tried fewer chemical options','Step 2 / where it struggled','LLZO is the oxide electrolyte in the previous chart.');
 text(s,'33',56,241,420,90,72,C.teal,true);text(s,'different chemical formulas\ntried by the LLM using results',56,342,500,96,31,C.ink);
 text(s,'95',689,241,450,90,72,C.gray,true);text(s,'different chemical formulas\ntried by random search',689,342,530,96,31,C.ink);
 text(s,'10 of its 12 successful searches first passed on tries 8–10.',56,493,1168,72,34,C.orange,true);
 note(s,'Across 300 choices per strategy. Broad exploration was more effective in this test.',615);
 notes(s,'Formula coverage is pooled across all 30 runs, ten picks per run, not a single search. Random has 24 successful runs and iterative 12. Iterative makes 29 acceptable picks, 28 in queries 6–10, with 26 picks from LiAlSiO4 polymorphs. Random makes 33 acceptable picks. These patterns describe late and concentrated selection, not the model’s private cognitive process. A later practical-chemistry audit flagged five of 17 acceptable structures; 18 of the 24 successful random runs also found an unflagged candidate. The main endpoint remains unchanged, and there is no evidence the LLM intentionally avoided flagged materials. Details are in backup slide 19.',['audit','synthesis','evidence']);
}
// 11: introduce adhesion before the forecasts.
{
 const s=slide('Next test: predict how strongly the coating attaches','Step 3 / physical calculations');
 text(s,'One known reference',56,226,475,50,33,C.ink,true);
 text(s,'The LLM sees calculated results\nfor LiNbF₆, then chooses two\nmore coatings from a small menu.',56,300,500,146,31,C.muted);
 text(s,'A prediction before the test',689,226,535,50,33,C.ink,true);
 text(s,'For each choice, it predicts\nadhesion at both contacts\nbefore the new results exist.',689,300,535,146,31,C.muted);
 text(s,'Adhesion = energy needed to separate a contact in this model.\nHigher values mean stronger attachment under the tested conditions.',56,496,1168,110,30,C.teal,true);
 note(s,'PET-MAD simulates the atoms. These results have not been measured in a real battery.',632);
 notes(s,'PET-MAD is a machine-learned interatomic potential used to relax explicit atomic structures and compute energies. It is a separate model from the LLM. The physical pilot uses the sulfide stack. Reference LiNbF6 is evaluated first. Feasible alternatives are LiTaF6, LiCaAlF6 and LiF; LiF does not pass the frozen thermodynamic rule and was not physically evaluated. The known-material menu and construction rules constrain the choice. The adhesion quantity W_adh compares relaxed joined and separated surfaces under fixed protocol constraints, per interface area in J/m². It is not measured fracture toughness. Three registry positions per contact were tested for each new coating.',['pilot','synthesis','evidence']);
}
// 12: one prospective choice at a time.
{
 const s=slide('First choice: the forecast worked for LiTaF₆','Step 3 / prediction checked','Its idea: replace niobium (Nb) with chemically related tantalum (Ta).');
 table(s,[['Contact with the coating','LLM forecast','Calculated adhesion'],['Cathode side','3.2–3.9','3.339 (within range)'],['Electrolyte side','1.4–1.9','1.577 (within range)']],[430,300,438],{top:237,height:246,font:30,header:25});
 text(s,'Both forecasts held. It also predicted the weaker contact correctly.',56,535,1168,77,34,C.teal,true);
 note(s,'Units: J/m². Forecasts were recorded before the new calculations.',631);
 notes(s,'The LLM chose LiTaF6 using an Nb/Ta chemical analogy. Exact selected-primary values are 3.338748412819128 and 1.5773585444472311 J/m². Both fall inside the archived prospective ranges. The electrolyte contact is weaker, as forecast. This is one successful material-level analogy, not a calibrated error model. Ranges were stated by the model and are not statistical confidence intervals. Registry selection minimizes relaxed joined-interface energy, rather than choosing the largest adhesion value.',['pilot','synthesis','evidence']);
}
// 13: failed forecast receives equal visual weight.
{
 const s=slide('Second choice: the forecast failed for LiCaAlF₆','Step 3 / prediction checked','The LLM expected stronger attachment than the calculations found.');
 table(s,[['Contact with the coating','LLM forecast','Calculated adhesion'],['Cathode side','3.0–3.8','1.427 (below range)'],['Electrolyte side','1.4–1.9','0.744 (below range)']],[430,300,438],{top:237,height:246,font:30,header:25});
 text(s,'Both forecasts missed. The LLM acknowledged the failure afterward.',56,535,1168,77,34,C.orange,true);
 note(s,'Units: J/m². It still identified the electrolyte side as the weaker contact.',631);
 notes(s,'Exact selected-primary values are 1.426710445485596 and 0.7435735865694895 J/m². Both are below the previously recorded ranges. The model’s final assessment acknowledged the Ca–Al miss. Its choice order remained LiTaF6 then LiCaAlF6, the same as its initial shortlist; the second was the only remaining acceptable candidate in the feasible menu. The pilot therefore tests forecasts but cannot demonstrate adaptive-selection gain. The final summary also misread a weaker-contact field as a minimum over registries. The archived response is retained, with an explanatory correction in the review.',['pilot','synthesis','evidence']);
}
// 14: physically meaningful comparison plus the ranking caveat.
{
 const s=slide('What the physical calculations found','Step 3 / result','Adhesion in the tested structures. Higher values mean stronger attachment.');
 const formulas=['LiNbF6','LiTaF6','LiCaAlF6'];
 chart(s,'bar',{position:{left:56,top:221,width:1168,height:355},categories:['LiNbF₆ (reference)','LiTaF₆ (first choice)','LiCaAlF₆ (second choice)'],series:[{name:'Cathode side',values:formulas.map(f=>E.physical[f].contacts.cathode.W_adh_J_m2),fill:C.blue},{name:'Electrolyte side',values:formulas.map(f=>E.physical[f].contacts.electrolyte.W_adh_J_m2),fill:C.teal}],hasLegend:true,legend:{position:'bottom',textStyle:{fontSize:24,fill:C.ink}},barOptions:{direction:'column',grouping:'clustered',gapWidth:110},xAxis:{...axis,majorGridlines:null},yAxis:{...axis,min:0,max:4,majorUnit:1,title:{text:'Adhesion (J/m²)',textStyle:{fontSize:23}}},dataLabels:{showValue:true,numberFormatCode:'0.00',position:'outEnd',textStyle:{fontSize:27,bold:true,fill:C.ink}}});
 note(s,'Ca–Al attached less strongly. The small Nb–Ta gap does not establish a reliable winner.',599,C.teal);
 text(s,'Numerical sensitivity and charged model surfaces still limit the physical interpretation.',56,641,1168,31,22,C.muted);
 notes(s,'The electrolyte is the weaker contact for all three coatings. The Nb–Ta gap on that side is about 0.056 J/m². Changing the electrolyte bulk reference shifts their values by about 0.121 and 0.114 J/m², larger than the gap. These are construction sensitivities, not statistical error bars. Ca–Al shows much lower primary adhesion, but its electrolyte thickness and bulk-reference sensitivities remain unquantified. All contact models are formally polar, so numerical convergence does not remove the electrostatic limitation. The final values supersede earlier pilot values obtained with different constructions. Full W_adh/W_sep values appear in backup slide 20.',['pilot','synthesis','evidence']);
}
// 15: answer the user's question directly, with evidence boundaries.
{
 const s=slide('What the LLM achieved','The answer');
 line(s,'01','Useful feedback improved some choices','Strong gains in the sulfide tests. The oxide result showed a limit.',217);
 line(s,'02','It made chemical hypotheses testable','Two adhesion forecasts held and two failed, all recorded in advance.',349);
 line(s,'03','It assessed results, but still needed review','Its order stayed the same. A human corrected one interpretation.',481);
 note(s,'We tested a scientific decision process. A better battery coating has not yet been validated.',631,C.teal);
 notes(s,'This is the central conclusion for a mixed audience. Feedback utility is conditional on the environment and the benchmark. Forecast checking is valuable because the calculation can contradict the model’s words. The physical pilot had two choices and no repeated expensive-search control, so it cannot prove general predictive reliability, compute savings or adaptive selection superiority. The model correctly identified the weaker contact twice but misunderstood the meaning of min_W_adh_J_m2 in the summary. Human interpretation and independent validation remain necessary.',['synthesis','pilot']);
}
// 16: a concrete, accessible ending.
{
 const s=slide('What comes next','Toward useful battery coatings');
 line(s,'1','Improve how the LLM explores','Test ways to avoid repeating a narrow set of chemical ideas.',211);
 line(s,'2','Test choices over more physical calculations','Compare LLM-guided selection with simple rules and random choices.',343);
 line(s,'3','Check the missing battery requirements','Test ion transport, practical preparation and experimental performance.',475);
 note(s,'The contribution: a measured test of AI-guided scientific choices, including where they fail.',631,C.teal);
 notes(s,'These are future research directions, not completed experiments. A new study should preregister an exploration mechanism and compare policies on independent expensive decisions. Physical models need additional validation, particularly polar-interface treatment and missing sensitivity checks. A functional coating also needs suitable transport, processability and cycling behavior. The current bounded pilot is complete and does not require new calculations to reproduce its existing outcomes. The integrated code and viewer have since been completed in the separate final-integration worktree; this deck does not merge branches.',['synthesis','pilot']);
}
// Put the sixteen main slides first, then the six retained backups.
const orderInspection=await P.inspect({select:'$.slides[*]',include:['id','index']});
P.slides.reorder([0,...Array.from({length:15},(_,i)=>7+i),1,2,3,4,5,6].map(i=>orderInspection.records[i].id));
// Backup 17: replace the dense statistics table with complete counts and compact tests.
{
 const s=P.slides.items[16];
 const record=(await P.inspect({select:'$.slides[16]',include:['elements.id','elements.kind','elements.text','elements.position']})).records[0];
 for(const e of record.elements??[]){if(e.position?.top>180&&e.position?.top<670)P.delete(e.id);if(e.text==='Three of six planned contrasts survive correction')P.resolve(e.id).text.replace(e.text,'All five strategies and the planned statistical tests');}
 table(s,[['Electrolyte','Uses results','No results','Mixed up','One list','Random'],['Sulfide','20','2','6','0','8'],['Chloride','30','30','30','30','29'],['Oxide (LLZO)','12','0','4','1','24']],[278,178,178,178,178,178],{top:218,height:278,font:27,header:24});
 text(s,'Successful searches out of 30, after ten tries. Holm-adjusted paired tests:',56,524,1168,42,26,C.ink,true);
 text(s,'Sulfide: versus no results p = 0.0000458, versus mixed-up p = 0.00244.\nLLZO: versus no results p = 0.00244, versus mixed-up p = 0.172.\nChloride: p = 1 for both comparisons. Six planned tests in total.',56,574,1168,96,24,C.muted);
 notes(s,'Counts are the primary frozen endpoint from the 450-run environment study. Exact paired McNemar tests use display-order seeds 200–229 and Holm correction across all six planned comparisons. Three survive the 0.05 threshold. Random comparisons are descriptive relative to this preregistered family. Acceptable pool sizes are 4/141 sulfide, 55/141 chloride and 17/141 LLZO. The frozen objective uses P≤0.050 eV per non-Li atom, band gap≥2 eV and equilibrated contact endpoints. It does not predict finite-temperature behavior, ion transport, synthesis or battery cycling.',['protocol','evidence','synthesis']);
}
// Backup 22: current delivery status replaces an obsolete integration-pending row.
{
 const s=P.slides.items[21];
 const record=(await P.inspect({select:'$.slides[21]',include:['elements.id','elements.kind','elements.text']})).records[0];
 for(const e of record.elements??[]){
  if(e.text==='The result is reproducible; integration remains separate')P.resolve(e.id).text.replace(e.text,'Archived evidence and completed integration');
  if(e.kind==='table'){const t=P.resolve(e.id);t.cells.set(5,0,'Integrated delivery');t.cells.set(5,1,'Reader fix, code integration and structure viewer completed\non the separate final-integration branch');}
 }
 s.speakerNotes.text='Scientific accounting: environment study 450 runs and 2,800 API calls; physical pilot five HTTP attempts, 26 new jobs, 6,632 runner calls plus 52 rigid-fragment single points. Cost figures are recorded list-rate arithmetic, not current pricing or bills. Runner times and summed allocation times differ and exclude queue delay.\n\nCurrent engineering checkpoint: work/final-integration-20261022 at 91afca5 includes both collaborators, the final-index reader correction and the generated viewer launch fix. The integrated tree previously passed 227 tests; the viewer fix passed 13 viewer tests. These are recorded prior checks, not tests rerun to produce this deck. Main/davide remain separate.\n\nSources:\n'+path.join(ROOT,'FINAL_PILOT_REVIEW.md')+'\n'+path.join(path.dirname(ROOT),'interphAIse-integration/FINAL_INTEGRATION.md')+'\n'+path.join(path.dirname(ROOT),'interphAIse-integration/REPORT.md');
}
// Renumber and preserve the standard footer throughout.
const snapshot=await P.inspect({select:'$.slides[*]',include:['id','index','title','elements.id','elements.kind','elements.text','elements.position','notes.text']});
for(const row of snapshot.records){for(const e of row.elements??[]){if(e.kind==='textbox'&&/^\d{2}$/.test(e.text)&&e.position?.left>=1150&&e.position?.top>=670)P.resolve(e.id).text.replace(e.text,String(row.index+1).padStart(2,'0'));}}
const finalInspection=await P.inspect({select:'$.slides[*]',include:['id','index','title','elements.id','elements.kind','elements.text','notes.text']});
if(/HELLMM/i.test(finalInspection.ndjson))throw new Error('Unrelated project remains in deck');
await fs.writeFile(path.join(BUILD,'final-inspection.ndjson'),finalInspection.ndjson);
await fs.writeFile(path.join(BUILD,'narrative.json'),JSON.stringify(manifest,null,2));
const tableOwners=[],chartOwners=[];
for(const row of finalInspection.records){if(row.elements.some(e=>e.kind==='table'))tableOwners.push(row.index+1);if(row.elements.some(e=>e.kind==='chart'))chartOwners.push(row.index+1);}
const candidate=path.join(BUILD,'candidate.pptx');await (await PresentationFile.exportPptx(P)).save(candidate);
const finalPath=path.join(OUT,process.env.DECK_FILENAME || 'interphAIse_the_idea_and_LLM_results_2026-10-22_v3.pptx');
const result=await finalizePresentation({workspaceDir:ROOT,candidatePath:candidate,finalPath,pythonExecutable:path.join(RUNTIME,'python/bin/python3'),integrityValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',...tableOwners.flatMap(n=>['--require-native-table-slide',String(n)])],requiredNativeTableOwnerSlides:tableOwners,requiredNativeChartOwnerSlides:chartOwners,materializeLiteralChartWorkbooks:true,fontPolicy:{basis:'reference',families:[FONT],referencePath:SOURCE,referenceSha256:sourceHash},verifyArtifactToolImport:true,receiptPath:path.join(BUILD,path.basename(finalPath)+'.validation.json')});
console.log(JSON.stringify({path:finalPath,slides:P.slides.items.length,tableOwners,chartOwners,sha256:result.finalSha256,layout:result.presentationLayout},null,2));
const final=await PresentationFile.importPptx(await FileBlob.load(finalPath));
await fs.mkdir(path.join(BUILD,'rendered'),{recursive:true});
for(let i=0;i<final.slides.items.length;i++){const b=await final.export({slide:final.slides.items[i],format:'png',scale:1.5});await fs.writeFile(path.join(BUILD,'rendered',`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await b.arrayBuffer()));console.log('Rendered',i+1);}
