// Extend the reviewed non-expert deck without rebuilding its existing evidence.
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {pathToFileURL} from 'node:url';
import {execFileSync} from 'node:child_process';
process.on('uncaughtException',e=>{console.error(e.message);console.error(e.stack?.split('\n').slice(1,6).join('\n'));process.exit(1);});
const ROOT=process.env.INTERPHAISE_ROOT || process.cwd();
const RUNTIME='/Users/davidetisi/.cache/codex-runtimes/codex-primary-runtime/dependencies';
const SKILL='/Users/davidetisi/.codex/plugins/cache/openai-primary-runtime/presentations/26.1015.12040/skills/presentations';
process.env.RUNTIME_NODE_MODULES ||= path.join(RUNTIME,'node/node_modules');
const {PresentationFile,FileBlob}=await import(pathToFileURL(path.join(RUNTIME,'node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs')).href);
const {finalizePresentation}=await import(pathToFileURL(path.join(SKILL,'container_tools/artifact_tool_utils.mjs')).href);
const BUILD=path.join(ROOT,'presentations/.build/nonexpert_tools_shortlist');
const OUT=path.join(ROOT,'presentations/nonexpert_2026-10-22');
await fs.mkdir(BUILD,{recursive:true});
const SOURCE=path.join(OUT,'interphAIse_the_idea_and_LLM_results_2026-10-22_v3.pptx');
const sourceHash=crypto.createHash('sha256').update(await fs.readFile(SOURCE)).digest('hex');
const E=JSON.parse(await fs.readFile(path.join(ROOT,'presentations/source/results_synthesis_2026-10-22.json'),'utf8'));
const screenPath=path.join(ROOT,'data/benchmarks/environment_v1/lco_lpscl_4v.json');
const screen=JSON.parse(await fs.readFile(screenPath,'utf8'));
const passing=screen.results.filter(x=>x.acceptable);
if(passing.length!==4 || new Set(passing.map(x=>x.formula)).size!==3)throw Error('Shortlist source changed');
await fs.writeFile(path.join(BUILD,'shortlist-evidence.json'),JSON.stringify({screen_source:screenPath,screen_sha256:crypto.createHash('sha256').update(await fs.readFile(screenPath)).digest('hex'),rows:passing.map(({candidate_id,formula,penalty,penalty_bin,band_gap_eV})=>({candidate_id,formula,penalty,penalty_bin,band_gap_eV}))},null,2));
const P=await PresentationFile.importPptx(await FileBlob.load(SOURCE));
await fs.writeFile(path.join(BUILD,'source-inspection.ndjson'),(await P.inspect({select:'$.slides[*]',include:['id','index','title','elements.id','elements.kind','elements.text','elements.position','notes.text']})).ndjson);
await fs.writeFile(path.join(BUILD,'source-layouts.ndjson'),(await P.inspect({kind:'layout',maxChars:50000})).ndjson);
await fs.writeFile(path.join(BUILD,'source-masters.json'),JSON.stringify({masters:P.masters.items.map(x=>({id:x.id,name:x.name})),placeholders:P.slides.items.map(s=>({id:s.id,items:s.placeholders.items.map(x=>({name:x.name,id:x.id}))}))},null,2));
const FONT='Helvetica Neue';
const C={bg:'#FAFAF7',ink:'#172B3A',muted:'#526472',rule:'#D6DEDE',teal:'#007F7B',white:'#FFFFFF'};
function text(s,str,x,y,w,h,size=28,color=C.ink,bold=false){const q=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});q.text=str;q.text.style={typeface:FONT,fontSize:size,color,bold,autoFit:'none',wrap:'square',insets:0,verticalAlignment:'top'};return q;}
function slide(title,section,subtitle){const s=P.slides.add();s.background.fill=C.bg;text(s,section.toUpperCase(),56,27,1110,26,18,C.teal,true);text(s,title,56,74,1168,75,44,C.ink,true);text(s,subtitle,56,155,1168,60,27,C.muted);text(s,'interphAIse  /  Results through 22 October 2026',56,679,1090,24,17,C.muted);text(s,'00',1160,677,64,28,19,C.muted);return s;}
function table(s,values,widths,{top=225,height=325,font=27,header=24}={}){const t=s.tables.add({rows:values.length,columns:widths.length,left:56,top,width:1168,height,values,columnWidths:widths});t.styleOptions={headerRow:false,bandedRows:false};t.borders.assign({fill:C.rule,width:0.6,style:'solid'});values.forEach((row,i)=>{t.rows[i].height=height/values.length;row.forEach((_,j)=>{const c=t.getCell(i,j);c.fill=i===0?C.ink:C.bg;c.text.style={typeface:FONT,fontSize:i===0?header:font,color:i===0?C.white:C.ink,bold:i===0,autoFit:'none',insets:0};});});t.cells.block({row:0,column:0,rowCount:values.length,columnCount:widths.length}).assign({margins:{left:14,right:12,top:5,bottom:5},anchor:'center'});return t;}
// New main slide 5: tools are named together with their scientific jobs.
{
 const s=slide('The tools behind each decision','How it works','The LLM chooses the next test. Specialized tools return the numerical evidence.');
 table(s,[['Tool used','Its job in interphAIse'],['Claude Haiku 5.5','Chooses materials, explains choices and predicts outcomes'],['Materials Project','Supplies known crystal structures and reference energy data'],['pymatgen + SciPy','Calculate reaction scores for the chemical screen'],['ASE + PET-MAD','Relax atomic structures and calculate adhesion energies'],['Python workflow','Enforces the test budget and saves decisions and results']],[362,806],{top:221,height:366,font:27,header:25});
 text(s,'Niflheim GPUs + Slurm run the atomic calculations.\nThe 3D viewer lets researchers inspect the structures.',56,613,1168,59,24,C.muted);
 s.speakerNotes.text='The LLM used in the archived trials is Claude Haiku 5.5 through the direct Anthropic endpoint. It selects existing candidate IDs, supplies rationales and states prospective adhesion ranges. It does not calculate the reported energies. Materials Project supplies known structures, corrected GGA/GGA+U reference energies and band gaps. pymatgen handles materials, structures and phase-diagram machinery. The custom evaluator uses SciPy linear programming (linprog) for the frozen production reaction scores; pymatgen phase diagrams also provide cross-checks. In the benchmark, these scores are precomputed and the runner reveals only queried results. The LLM cannot access the whole answer table.\n\npymatgen builds matched contact structures. ASE handles atomic optimization and constraints. PET-MAD S 1.6.0 (r²SCAN), accessed through UPET, supplies energy and force predictions. PET-MAD is a separate machine-learning model, not the language model. Joined and separated structures give work-of-adhesion values. Niflheim GPU jobs use Slurm. Python scripts validate IDs, enforce charged evaluation budgets and save hash-linked manifests, choices and results. The generated 3D viewer supports human geometry inspection; it does not independently validate the physics. Materials Project and PET-MAD energies are kept separate.\n\nSources:\n'+['requirements.txt','pyproject.toml','interphaise/discovery_evaluator.py','interphaise/tools/matcher.py','interphaise/tools/relaxation.py','interphaise/tools/mlip.py','ENVIRONMENT_PROTOCOL.md','FINAL_PILOT_REVIEW.md','RESULTS_SYNTHESIS_2026-10-22.md'].map(p=>path.join(ROOT,p)).join('\n')+'\n'+path.join(path.dirname(ROOT),'interphAIse-integration/FINAL_INTEGRATION.md');
}
// New main slide 16: a qualified candidate conclusion after the physical results.
{
 const s=slide('A small shortlist for further testing','Candidate outcome','Four of 141 structures pass the sulfide screen, representing three chemical formulas.');
 table(s,[['Material and role','Adhesion at weaker\ncontact (J/m²)','What the evidence supports'],['LiNbF₆\nReference',E.physical.LiNbF6.contacts.electrolyte.W_adh_J_m2.toFixed(3),'Promising reference'],['LiTaF₆\nFirst LLM choice',E.physical.LiTaF6.contacts.electrolyte.W_adh_J_m2.toFixed(3),'Promising alternative'],['LiCaAlF₆\nSecond LLM choice',E.physical.LiCaAlF6.contacts.electrolyte.W_adh_J_m2.toFixed(3),'Passes chemistry,\nbut attaches less strongly']],[330,310,528],{top:226,height:302,font:28,header:24});
 text(s,'Suggested follow-up: LiNbF₆ and LiTaF₆.\nTheir small difference does not establish a proven optimum.',56,552,1168,79,30,C.teal,true);
 text(s,'Two Ta crystal forms pass screening. One was simulated. Real battery performance remains untested.',56,643,1168,34,22,C.muted);
 s.speakerNotes.text='This slide answers whether the method produced a small set of useful candidates. In the flagship LiCoO2 / Li6PS5Cl system at 4 V, the frozen chemical screen accepts four of 141 structure IDs: LiNbF6, LiCaAlF6 and two LiTaF6 polymorphs (the same chemical formula with different crystal arrangements). These are known Materials Project materials. The whole frozen table establishes the pool shortlist; it is not an output invented by the LLM or guaranteed to be recovered in each ten-query search. The physical pilot starts from LiNbF6 reference results, then the LLM selects one LiTaF6 structure and LiCaAlF6.\n\n'+passing.map(x=>`${x.candidate_id}: ${x.formula}, reaction penalty ${x.penalty} eV/non-Li atom, objective bin ${x.penalty_bin}, band gap ${x.band_gap_eV} eV.`).join('\n')+'\n\nThe frozen pass rule is penalty ≤0.050 eV/non-Li atom and band gap ≥2 eV. LiNbF6 and both LiTaF6 polymorphs occupy the best observed reaction-score bin (bin 1, width 0.020 eV/non-Li atom). LiCaAlF6 passes in bin 2. Best observed score bin is a property of the fixed pool and proxy, not a global material optimum.\n\nThe table shows the selected-primary work of adhesion at the weaker contact, the electrolyte side in all three cases. The proposed Nb/Ta follow-up pair is an interpretation of chemical acceptability plus stronger calculated attachment. Neither is a validated optimal coating. Their 0.056 J/m² primary gap is smaller than the roughly 0.121 and 0.114 J/m² reference/construction sensitivities. Ca–Al is a useful contrasting result but has lower adhesion in these calculations and unquantified electrolyte thickness/reference sensitivity. All model contacts are formally polar. Transport, processing, cycling and experimental performance remain untested. The shortlist is specific to this sulfide environment and cannot be generalized to the other electrolytes.\n\nSources:\n'+[screenPath,path.join(ROOT,'presentations/source/results_synthesis_2026-10-22.json'),path.join(ROOT,'FINAL_PILOT_REVIEW.md'),path.join(ROOT,'RESULTS_SYNTHESIS_2026-10-22.md')].join('\n')+'\nArchived outcome commits: agent '+E.sources.agent_commit+'; physics '+E.sources.physics_commit+'.';
}
// Source slides remain intact, with only page markers and note cross-references updated.
const beforeOrder=(await P.inspect({select:'$.slides[*]',include:['id','index']})).records;
const order=[0,1,2,3,22,...Array.from({length:10},(_,i)=>4+i),23,...Array.from({length:8},(_,i)=>14+i)];
P.slides.reorder(order.map(i=>beforeOrder[i].id));
P.slides.items[0].speakerNotes.text=P.slides.items[0].speakerNotes.text.replace('slides 1–16, approximately 15 minutes. Slides 17–22','slides 1–18, approximately 15–18 minutes. Slides 19–24');
for(const s of P.slides.items){s.speakerNotes.text=s.speakerNotes.text.replace('backup slide 17','backup slide 19').replace('backup slide 19.','backup slide 21.').replace('backup slide 20','backup slide 22');}
// Correct the first cross-reference separately to avoid chained number replacement.
P.slides.items[8].speakerNotes.text=P.slides.items[8].speakerNotes.text.replace('all five counts and planned statistics are in backup slide 21','all five counts and planned statistics are in backup slide 19');
const snapshot=await P.inspect({select:'$.slides[*]',include:['id','index','elements.id','elements.kind','elements.text','elements.position']});
for(const row of snapshot.records)for(const e of row.elements??[])if(e.kind==='textbox'&&/^\d{2}$/.test(e.text)&&e.position?.left>=1150&&e.position?.top>=670)P.resolve(e.id).text.replace(e.text,String(row.index+1).padStart(2,'0'));
const inspection=await P.inspect({select:'$.slides[*]',include:['id','index','title','elements.id','elements.kind','elements.text','elements.position','notes.text']});
await fs.writeFile(path.join(BUILD,'final-inspection.ndjson'),inspection.ndjson);
if(/HELLMM/i.test(inspection.ndjson))throw Error('Unrelated project reference in presentation');
const tableOwners=inspection.records.filter(x=>x.elements.some(e=>e.kind==='table')).map(x=>x.index+1);
const chartOwners=inspection.records.filter(x=>x.elements.some(e=>e.kind==='chart')).map(x=>x.index+1);
const candidate=path.join(BUILD,'candidate.pptx');await (await PresentationFile.exportPptx(P)).save(candidate);
// Import/export omits workbook relationships; retain the unchanged original chart packages.
const preserved=path.join(BUILD,'candidate-preserved.pptx');
execFileSync(path.join(RUNTIME,'python/bin/python3'),[path.join(ROOT,'presentations/source/preserve_nonexpert_chart_packages_2026-10-22.py'),SOURCE,candidate,preserved],{stdio:'inherit'});
const finalPath=path.join(OUT,process.env.DECK_FILENAME || 'interphAIse_the_idea_and_LLM_results_2026-10-22_v4.pptx');
const result=await finalizePresentation({workspaceDir:ROOT,candidatePath:preserved,finalPath,pythonExecutable:path.join(RUNTIME,'python/bin/python3'),integrityValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',...tableOwners.flatMap(n=>['--require-native-table-slide',String(n)])],requiredNativeTableOwnerSlides:tableOwners,requiredNativeChartOwnerSlides:chartOwners,requiredEmbeddedWorkbookChartOwnerSlides:chartOwners,materializeLiteralChartWorkbooks:false,fontPolicy:{basis:'reference',families:[FONT],referencePath:SOURCE,referenceSha256:sourceHash},verifyArtifactToolImport:true,receiptPath:path.join(BUILD,path.basename(finalPath)+'.validation.json')});
console.log(JSON.stringify({path:finalPath,slides:P.slides.items.length,tableOwners,chartOwners,sha256:result.finalSha256},null,2));
const final=await PresentationFile.importPptx(await FileBlob.load(finalPath));
await fs.mkdir(path.join(BUILD,'rendered'),{recursive:true});
for(let i=0;i<final.slides.items.length;i++){const b=await final.export({slide:final.slides.items[i],format:'png',scale:1.5});await fs.writeFile(path.join(BUILD,'rendered',`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await b.arrayBuffer()));console.log('Rendered',i+1);}
