from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.utils import ImageReader
from pathlib import Path
from pypdf import PdfReader
root=Path.cwd(); images=sorted((root/'presentations/.build/results_synthesis/pdf_images').glob('slide-*.png'))
assert len(images)==24
out=root/'presentations/results_2026-10-22/interphAIse_results_synthesis_2026-10-22_v2.pdf'
c=Canvas(str(out),pagesize=(960,540),pageCompression=1)
c.setTitle('interphAIse: results synthesis, 22 October 2026')
c.setAuthor('Davide Tisi and Adem R. N. Aouichaoui')
c.setSubject('Static visual companion to the editable PowerPoint; 18 main slides and 6 backups')
for image in images:
 c.drawImage(ImageReader(str(image)),0,0,width=960,height=540)
 c.showPage()
c.save()
assert len(PdfReader(out).pages)==24
print('PDF created:',out.stat().st_size,'bytes; 24 pages')
