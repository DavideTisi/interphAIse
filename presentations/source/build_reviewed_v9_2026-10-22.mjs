/** Targeted review of v8, using Artifact Tool. Run from the repository root.
 * CODEX_RUNTIME and PRESENTATION_SKILL override local bundled-runtime paths.
 * Use --finalize only after inspecting draft renders. Outputs never overwrite.
 */
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {pathToFileURL} from 'node:url';
const ROOT=process.cwd();
const RT=process.env.CODEX_RUNTIME||'/Users/davidetisi/.cache/codex-runtimes/codex-primary-runtime/dependencies';
const SK=process.env.PRESENTATION_SKILL||'/Users/davidetisi/.codex/plugins/cache/openai-primary-runtime/presentations/26.1015.12040/skills/presentations';
process.env.RUNTIME_NODE_MODULES ||= path.join(RT,'node/node_modules');
const {PresentationFile,FileBlob}=await import(pathToFileURL(path.join(RT,'node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs')).href);
const {finalizePresentation}=await import(pathToFileURL(path.join(SK,'container_tools/artifact_tool_utils.mjs')).href);
const BASE=path.join(ROOT,'runs/presentations_v9');
const OUT=path.join(ROOT,'presentations/two_formats_2026-10-22');
const PUBLIC='https://github.com/DavideTisi/interphAIse/blob/main/';
const REPO='https://github.com/DavideTisi/interphAIse';
const VIEWER='https://davidetisi.github.io/interphAIse/';
const C={ink:'#172B3A',muted:'#526472',teal:'#007F7B'};
const localSource=/\/Users\/davidetisi\/Documents\/Work\/DTU\/OSI_Hackathon\/interphAIse(?:-integration)?\/([^\n]+)/g;
const noteAdditions={
 pool:'Candidates are known crystal structures from Materials Project. The 141 IDs represent 100 compositions because several compositions have multiple crystal structures. Repeated searches can find the same candidate. Success is a property of a ten-query search, not a count of distinct new materials.',
 models:'Cross-model comparisons are descriptive. The query budget and screening task are shared, but reasoning compute is not matched. Each model has its own preregistered six-comparison McNemar/Holm family. The DeepSeek family has no significant result after correction.',
 llzo:'The frozen LLZO proxy admits chemically questionable oxyhalogens. The post-hoc audit leaves the original criterion and counts unchanged: random has 18 successes with unflagged candidates plus six flagged-only successes, Haiku iterative has 12 unflagged successes, and DeepSeek upfront has 20 unflagged successes. DeepSeek iterative has nine unflagged and one flagged-only success. Upfront also changes the selection policy, so its contrast with iterative does not isolate the effect of feedback.',
 physics:'All reported adhesion values are provisional model results for formally polar interfaces. Li-ion transport is untested. Nb and Ta differ by only 0.056 J/m² at the weaker contact, below the roughly 0.12 J/m² bulk-reference/construction sensitivity. Ca–Al electrolyte thickness and bulk-structure sensitivity are unquantified. Sensitivity evidence was released after the live decisions. LiF was not calculated.'
};
async function publicNotes(text){
 const matches=[...text.matchAll(localSource)];
 for(const m of matches){
  let rel=m[1].trim();
  if(!rel.includes('/')&&rel.endsWith('.md'))rel='docs/'+rel;
  if(rel==='presentations/source/branding/interphaise-logo-battery-v2.png')rel='assets/branding/interphaise-logo-battery-v2.png';
  await fs.access(path.join(ROOT,rel));
  text=text.replace(m[0],PUBLIC+rel);
 }
 return text;
}
for(const stem of ['4_minute_pitch','15_minute_talk']){
 const long=stem.startsWith('15'),kind=long?'15min':'4min';
 const source=path.join(ROOT,'presentations/source/reference_v8',`interphAIse_${stem}_2026-10-22_v8.pptx`);
 const expected=long?'dc50513addfc3421bde4baa81980c6349f5d54e44a3aa79b91b1e998d533315c':'17a0ad836d84af269b1b358ea9ff578baecd0d35719064f78858090b667dcd85';
 const hash=crypto.createHash('sha256').update(await fs.readFile(source)).digest('hex');if(hash!==expected)throw Error('Source changed');
 const build=path.join(BASE,kind);await fs.mkdir(build,{recursive:true});
 const P=await PresentationFile.importPptx(await FileBlob.load(source));
 const before=await P.inspect({select:'$.slides[*]',include:['id','index','elements.id','elements.kind','elements.text','elements.position','notes.text']});
 const changes={source_sha256:hash,slide_count:long?24:8,slides:{}};
 function edit(n,old,text,{y,h,size,color,bold,link}={}){
  const matches=before.records[n-1].elements.filter(e=>e.text===old);if(matches.length!==1)throw Error(`Cannot locate ${n}: ${old}`);
  const e=matches[0],q=P.resolve(e.id);q.text.replace(old,text);
  if(y!==undefined||h!==undefined)q.position={...e.position,top:y??e.position.top,height:h??e.position.height};
  if(size!==undefined||color!==undefined||bold!==undefined)q.text.style={typeface:'Helvetica Neue',fontSize:size??26,color:color??C.ink,bold:bold??false,autoFit:'none',wrap:'square',insets:0,verticalAlignment:'top'};
  if(link)q.text.get(text).link={uri:link,isExternal:true};
  (changes.slides[n]||=[]).push({before:old,after:text});
 }
 function note(n,script,addition){
  const s=P.slides.items[n-1],old=s.speakerNotes.text;
  const first=old.indexOf('\n'),detail=old.indexOf('\n\nSCIENTIFIC DETAIL');
  if(script&&detail!==-1)s.speakerNotes.text=old.slice(0,first+1)+script+old.slice(detail);
  s.speakerNotes.text+='\n\nV9 REVIEW\n'+addition;
 }
 const setup=long?5:2;
 edit(setup,long?'141 structures. Three electrolytes. Ten choices per search.':'141 candidates selected by fixed chemistry and structure filters.','141 known crystal structures representing 100 compositions.',{size:29,color:C.teal,bold:true});
 edit(setup,long?'810 completed searches. Same task and budget, different model configurations.':'Same cathode. Sulfide, chloride and oxide test different chemistries.','Three electrolytes. Ten choices per search. 810 completed searches.',{size:25,color:C.muted});
 note(setup,null,noteAdditions.pool+'\n'+noteAdditions.models);
 const success=long?7:3;
 if(long)edit(success,'A candidate passes only if it meets both criteria.','A candidate must pass both gates. Different runs may find the same material.',{size:26,color:C.muted});
 else edit(success,'Same menu, ten choices and 30 searches per strategy.','Thirty searches per strategy. Different runs may find the same material.',{size:26,color:C.muted});
 note(success,null,noteAdditions.pool);
 const sulfide=long?10:4;
 edit(sulfide,'Haiku beats both feedback controls in planned tests. DeepSeek remains inconclusive.','Haiku beats both controls after correction. DeepSeek remains inconclusive.\nCross-model contrasts are descriptive. Reasoning compute differs.',{y:625,h:48,size:20,color:C.muted});
 edit(sulfide,'Correct feedback: Haiku 20 and DeepSeek 12, compared with random 8.','Correct feedback: Haiku 20 and DeepSeek 12, compared with random 8.',{y:584,h:39,size:28,color:C.teal,bold:true});
 note(sulfide,null,noteAdditions.models);
 const llzo=long?17:7;
 edit(llzo,'DeepSeek: 20 upfront, 10 with correct feedback. No clear benefit in the planned feedback tests.','DeepSeek: 20 upfront, 10 with feedback. This also changes the selection policy.\nThe acceptance proxy admits questionable oxyhalogens. The frozen counts stay unchanged.',{y:625,h:48,size:19,color:C.muted});
 edit(llzo,'Every LLM strategy trails random choice on the observed success count.','Every LLM strategy trails random choice on the observed success count.',{y:584,h:39,size:28,color:C.teal,bold:true});
 note(llzo,null,noteAdditions.llzo);
 if(long){
  edit(15,'LiNbF₆ and LiTaF₆ are promising candidates for further testing.','LiNbF₆ and LiTaF₆ remain a follow-up pair, without a reliable winner.',{y:552,h:53,size:29,color:C.teal,bold:true});
  edit(15,'Their small difference does not establish a reliable winner. Transport remains untested.','Provisional values for formally polar interfaces. Lithium transport is untested.\nNb–Ta gap: 0.056 J/m², below the ~0.12 J/m² bulk-reference sensitivity.',{y:615,h:59,size:22,color:C.muted});
  note(15,null,noteAdditions.physics);
  edit(24,'Wadh: separated slabs are allowed to relax.\nWsep: fragments retain their joined-interface geometry.','All values in J/m². Wadh allows separated slabs to relax.\nWsep keeps their joined geometry. Both contacts are formally polar.\nLiF remains uncomputed.',{y:528,h:82,size:22,color:C.ink});
  edit(24,'J/m². Primary snapshots unchanged. Later robustness checks are a separate record.','Ca–Al electrolyte thickness and bulk-structure sensitivity remain unquantified.\nPrimary snapshots unchanged. Later robustness checks are separate.',{y:622,h:49,size:20,color:C.muted});
  note(24,null,noteAdditions.physics);
 }else{
  edit(5,'CHOICE AND PHYSICAL RESULT','HAIKU / PROSPECTIVE PHYSICAL TEST');
  edit(5,'All three pass the chemical screen. Higher adhesion means stronger attachment.','Haiku selects and forecasts. PET-MAD tests both contacts.',{size:27,color:C.muted});
  edit(5,'Ta forecasts held. Ca–Al forecasts failed. Nb/Ta remain a follow-up pair.','Ta forecasts held. Ca–Al electrolyte forecast: 1.4–1.9 J/m².\nPET-MAD returned 0.744 J/m². The forecast failed.',{y:549,h:78,size:28,color:C.teal,bold:true});
  edit(5,'Only thermodynamics. Lithium transport remains untested.','Provisional adhesion from formally polar interfaces. Lithium transport is untested.',{y:639,h:36,size:22,color:C.muted});
  note(5,'Haiku chose tantalum fluoride as a close analogue of the niobium reference, then calcium aluminium fluoride, the only acceptable option left. The tantalum forecasts held. For the calcium aluminium electrolyte contact, Haiku predicted 1.4 to 1.9 joules per square metre, but PET-MAD returned 0.744. These are provisional polar model interfaces. Nb and Ta remain a follow-up pair, with lithium transport still untested.',noteAdditions.physics);
 }
 const close=long?20:8;
 edit(close,'WHAT COMES NEXT','FINDING AND NEXT STEPS');
 edit(close,'Next: can lithium cross the protective layer?','What the LLM contributes');
 edit(close,'Test ionic mobility across the interphases','Useful chemical knowledge and useful adaptation\nto feedback are distinct capabilities.',{y:202,h:102,size:34,color:C.teal,bold:true});
 edit(close,'Use longer simulations to track lithium through the coating\nand through the layers formed at its contacts.','Next: test lithium transport through the shortlisted coatings.',{y:338,h:50,size:29,color:C.ink});
 edit(close,'Combine mobility with chemical compatibility and adhesion.','Then validate with higher-accuracy calculations and experiments.\nNo human-expert comparison or validated coating yet.',{y:397,h:78,size:25,color:C.muted});
 edit(close,'Then validate the leading candidates with stronger models and experiments.','Code and evidence: github.com/DavideTisi/interphAIse',{y:519,h:38,size:25,color:C.teal,link:REPO});
 edit(close,'Transport calculations were beyond the two-day computation window.','Structure viewer: davidetisi.github.io/interphAIse',{y:572,h:38,size:25,color:C.teal,link:VIEWER});
 note(close,'The LLM takes on a specific scientific judgment: what to calculate next and what result to expect. Our controls show that useful prior knowledge and useful adaptation to feedback are distinct capabilities. Their value depends on the environment and model configuration. We have no matched human-expert comparison and no validated coating yet. The next physical test is lithium transport, followed by higher-accuracy calculations and experiments. The complete code, evidence and interactive structures are public at these links.','No equivalence to human scientific intuition or measured expensive-compute savings is established. Transport calculations remain future work.\n'+REPO+'\n'+VIEWER);
 for(const slide of P.slides.items)slide.speakerNotes.text=await publicNotes(slide.speakerNotes.text);
 const draft=path.join(build,'authored.pptx'),candidate=path.join(build,'candidate.pptx'),manifest=path.join(build,'edits.json');
 await fs.writeFile(manifest,JSON.stringify(changes,null,2)+'\n');
 await (await PresentationFile.exportPptx(P)).save(draft);
 const patch=execFileSync(path.join(RT,'python/bin/python3'),[path.join(ROOT,'presentations/source/preserve_reviewed_deck_parts_v9.py'),source,draft,manifest,candidate],{encoding:'utf8'});
 await fs.writeFile(path.join(build,'preservation.json'),patch);
 const finalPath=path.join(OUT,`interphAIse_${stem}_2026-10-22_v9.pptx`);
 if(process.argv.includes('--finalize')){
  const tableOwners=before.records.filter(r=>r.elements.some(e=>e.kind==='table')).map(r=>r.index+1),chartOwners=long?[10,16,17]:[4,6,7];
  await finalizePresentation({workspaceDir:ROOT,candidatePath:candidate,finalPath,pythonExecutable:path.join(RT,'python/bin/python3'),integrityValidatorPath:path.join(SK,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(SK,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',...tableOwners.flatMap(n=>['--require-native-table-slide',String(n)])],explicitTotalSlideCount:long?24:8,requiredNativeTableOwnerSlides:tableOwners,requiredNativeChartOwnerSlides:chartOwners,requiredEmbeddedWorkbookChartOwnerSlides:chartOwners,fontPolicy:{basis:'reference',families:['Helvetica Neue'],referencePath:source,referenceSha256:hash},verifyArtifactToolImport:true,receiptPath:path.join(build,'validation.json')});
 }
 const checked=await PresentationFile.importPptx(await FileBlob.load(process.argv.includes('--finalize')?finalPath:candidate));
 await fs.mkdir(path.join(build,'rendered'),{recursive:true});
 for(let i=0;i<checked.slides.items.length;i++){
  const png=await checked.export({slide:checked.slides.items[i],format:'png',scale:1.5});
  await fs.writeFile(path.join(build,'rendered',`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await png.arrayBuffer()));
 }
 console.log(JSON.stringify({kind,slides:checked.slides.items.length,finalized:process.argv.includes('--finalize')}));
}
