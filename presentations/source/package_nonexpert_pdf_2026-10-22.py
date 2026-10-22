"""Package the checked final slides as a lossless static PDF companion."""
from pathlib import Path
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.utils import ImageReader
from pypdf import PdfReader
from PIL import Image

root = Path.cwd()
images = sorted((root / 'presentations/.build/nonexpert_story/rendered').glob('slide-*.png'))
assert len(images) == 22
out = root / 'presentations/nonexpert_2026-10-22/interphAIse_the_idea_and_LLM_results_2026-10-22_v3.pdf'
assert not out.exists(), 'Keep previous outputs; use a new file name for revisions.'
c = Canvas(str(out), pagesize=(960, 540), pageCompression=1)
c.setTitle('interphAIse: the idea and LLM results, step by step')
c.setAuthor('Davide Tisi and Adem R. N. Aouichaoui')
c.setSubject('16 main slides and 6 technical backups; static companion to the editable PowerPoint')
for image in images:
    c.drawImage(ImageReader(str(image)), 0, 0, width=960, height=540)
    c.showPage()
c.save()
reader = PdfReader(out)
assert len(reader.pages) == 22
for page, source in zip(reader.pages, images):
    embedded = list(page.images)
    assert len(embedded) == 1
    expected = Image.open(source).convert('RGB')
    actual = embedded[0].image.convert('RGB')
    assert expected.size == actual.size and expected.tobytes() == actual.tobytes()
print(f'{out}: 22 pages; embedded pixels match all finalized slide renders exactly.')
