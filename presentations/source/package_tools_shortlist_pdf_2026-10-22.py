"""Create the static PDF companion from checked v4 slide renders."""
from pathlib import Path
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.utils import ImageReader
from pypdf import PdfReader
from PIL import Image

root = Path.cwd()
images = sorted((root / 'presentations/.build/nonexpert_tools_shortlist/rendered').glob('slide-*.png'))
assert len(images) == 24
out = root / 'presentations/nonexpert_2026-10-22/interphAIse_the_idea_and_LLM_results_2026-10-22_v4.pdf'
assert not out.exists(), 'Preserve prior outputs; choose a new filename for revisions.'
c = Canvas(str(out), pagesize=(960, 540), pageCompression=1)
c.setTitle('interphAIse: the idea, tools and LLM results')
c.setAuthor('Davide Tisi and Adem R. N. Aouichaoui')
c.setSubject('18 main slides and 6 technical backups; static companion to the editable PowerPoint')
for image in images:
    c.drawImage(ImageReader(str(image)), 0, 0, width=960, height=540)
    c.showPage()
c.save()
reader = PdfReader(out)
assert len(reader.pages) == 24
for page, source in zip(reader.pages, images):
    embedded = list(page.images)
    assert len(embedded) == 1
    expected = Image.open(source).convert('RGB')
    actual = embedded[0].image.convert('RGB')
    assert expected.size == actual.size and expected.tobytes() == actual.tobytes()
print(f'{out}: 24 pages, all embedded images match final PPTX renders exactly.')
