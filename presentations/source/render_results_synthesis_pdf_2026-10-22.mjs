import fs from 'node:fs/promises';
import {PresentationFile,FileBlob} from '@oai/artifact-tool';
const p=await PresentationFile.importPptx(await FileBlob.load('presentations/results_2026-10-22/interphAIse_results_synthesis_2026-10-22_v2.pptx'));
await fs.mkdir('presentations/.build/results_synthesis/pdf_images',{recursive:true});
for(let i=0;i<p.slides.items.length;i++){
 const b=await p.export({slide:p.slides.items[i],format:'png',scale:2});
 await fs.writeFile(`presentations/.build/results_synthesis/pdf_images/slide-${String(i+1).padStart(2,'0')}.png`,new Uint8Array(await b.arrayBuffer()));
}
console.log('Rendered 24 high-resolution PDF pages');
