"""Create static PDF companions from the reviewed v9 slide renders.

The editable PowerPoints remain the source; closing links are clickable in PDF.
"""
from pathlib import Path
import hashlib
import json
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.utils import ImageReader
from pypdf import PdfReader
from PIL import Image
root=Path.cwd()
records=[]
for kind,stem,count,closing in [('4min','4_minute_pitch',8,8),('15min','15_minute_talk',24,20)]:
    images=sorted((root/f'runs/presentations_v9/{kind}/rendered').glob('slide-*.png'))
    assert len(images)==count
    out=root/f'presentations/two_formats_2026-10-22/interphAIse_{stem}_2026-10-22_v9.pdf'
    assert not out.exists(), 'Use a fresh output filename for a new revision.'
    c=Canvas(str(out),pagesize=(960,540),pageCompression=1)
    c.setTitle('interphAIse: '+('4-minute pitch' if kind=='4min' else '15-minute scientific talk'))
    c.setAuthor('Davide Tisi and Adem R. N. Aouichaoui')
    c.setSubject('Reviewed Haiku and DeepSeek evidence, prospective PET-MAD pilot, and public sources')
    for number,im in enumerate(images,1):
        c.drawImage(ImageReader(str(im)),0,0,width=960,height=540)
        if number==closing:
            for top,url in [(519,'https://github.com/DavideTisi/interphAIse'),(572,'https://davidetisi.github.io/interphAIse/')]:
                c.linkURL(url,(42,540-(top+38)*.75,900,540-top*.75),relative=0,thickness=0)
        c.showPage()
    c.save()
    reader=PdfReader(out)
    assert len(reader.pages)==count
    for page,im in zip(reader.pages,images):
        embedded=list(page.images);assert len(embedded)==1
        a=Image.open(im).convert('RGB'); b=embedded[0].image.convert('RGB')
        assert a.size==b.size and a.tobytes()==b.tobytes()
    assert len(reader.pages[closing-1].get('/Annots'))==2
    records.append({'path':str(out.relative_to(root)),'pages':count,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'pixels':'Every PDF page equals the reviewed slide render','closing_links':2})
(root/'runs/presentations_v9/pdf-validation.json').write_text(json.dumps(records,indent=2)+'\n')
print(json.dumps(records,indent=2))
