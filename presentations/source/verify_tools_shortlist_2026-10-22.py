"""Verify the additions, retained evidence, chart packages and visual preservation."""
import hashlib
import json
import re
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
from PIL import Image, ImageChops

root = Path.cwd()
build = root / 'presentations/.build/nonexpert_tools_shortlist'
out = root / 'presentations/nonexpert_2026-10-22'
source = out / 'interphAIse_the_idea_and_LLM_results_2026-10-22_v3.pptx'
deck = out / 'interphAIse_the_idea_and_LLM_results_2026-10-22_v4.pptx'
e = json.loads((root / 'presentations/source/results_synthesis_2026-10-22.json').read_text())
screen = json.loads((root / 'data/benchmarks/environment_v1/lco_lpscl_4v.json').read_text())
passing = [r for r in screen['results'] if r.get('acceptable', False)]
assert len(passing) == 4
assert sorted(r['formula'] for r in passing) == ['LiCaAlF6','LiNbF6','LiTaF6','LiTaF6']
assert {r['candidate_id'] for r in passing} == set(screen['diagnostics']['acceptable_ids'])
ns = {'c':'http://schemas.openxmlformats.org/drawingml/2006/chart','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
expected = [
    [[e['original'][a]['count'] for a in e['arm_order']]],
    [[e['environments'][env]['counts'][a] for env in e['environment_order']] for a in ['iterative','sequential','random']],
    [[e['physical'][f]['contacts'][side]['W_adh_J_m2'] for f in ['LiNbF6','LiTaF6','LiCaAlF6']] for side in ['cathode','electrolyte']],
]
with zipfile.ZipFile(deck) as z, zipfile.ZipFile(source) as original:
    slides = sorted([n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+.xml',n)],key=lambda n:int(re.search(r'(\d+)\.xml',n)[1]))
    notes = [n for n in z.namelist() if re.fullmatch(r'ppt/notesSlides/notesSlide\d+.xml',n)]
    charts = sorted(n for n in z.namelist() if re.search(r'/chart\d+\.xml$',n))
    workbooks = [n for n in z.namelist() if n.endswith('.xlsx')]
    assert len(slides) == len(notes) == 24
    assert len(charts) == len(workbooks) == 3
    assert sum(z.read(n).count(b'<a:tbl>') for n in slides) == 11
    assert not any(b'hellmm' in z.read(n).lower() for n in slides+notes)
    preserved = [n for n in original.namelist() if n.startswith('ppt/slides/charts/') or n.startswith('ppt/embeddings/chart-data-snapshot-')]
    assert len(preserved) == 9 and all(original.read(n)==z.read(n) for n in preserved)
    for part,wanted in zip(charts,expected):
        xml = ET.fromstring(z.read(part))
        actual = [[float(v.text) for v in ser.findall('.//c:val//c:pt/c:v',ns)] for ser in xml.findall('.//c:ser',ns)]
        assert len(actual)==len(wanted)
        for found,target in zip(actual,wanted):
            assert len(found)==len(target) and all(abs(a-b)<1e-8 for a,b in zip(found,target))
    def text(n,notes=False):
        part = f'ppt/notesSlides/notesSlide{n}.xml' if notes else f'ppt/slides/slide{n}.xml'
        return '\n'.join(t.text or '' for t in ET.fromstring(z.read(part)).findall('.//a:t',ns))
    for n,values in [(13,['3.2–3.9','1.4–1.9','3.339','1.577']),(14,['3.0–3.8','1.4–1.9','1.427','0.744'])]:
        assert all(v in text(n) for v in values)
    assert all(x in text(5) for x in ['Haiku 5.5','Materials Project','pymatgen','SciPy','ASE','PET-MAD','Python','Niflheim','Slurm','3D viewer'])
    assert all(x in text(16) for x in ['Four of 141','LiNbF₆','LiTaF₆','LiCaAlF₆','1.633','1.577','0.744','proven optimum','performance remains untested'])
    for row in passing:
        assert row['candidate_id'] in text(16,True)
        assert str(row['penalty']) in text(16,True)
    assert 'backup slide 19' in text(9,True)
    assert 'backup slide 21' in text(11,True)
    assert 'backup slide 22' in text(15,True)
    assert 'slides 1–18' in text(1,True) and 'Slides 19–24' in text(1,True)
    assert '0.160' in text(10) and '0.057' in text(10) and '0.048' in text(10)
    assert '33' in text(11) and '95' in text(11)
    # Existing slide text is unchanged except its page marker.
    for old in range(1,23):
        new = old if old<5 else old+1 if old<=14 else old+2
        prior = [t.text or '' for t in ET.fromstring(original.read(f'ppt/slides/slide{old}.xml')).findall('.//a:t',ns)]
        current = [t.text or '' for t in ET.fromstring(z.read(f'ppt/slides/slide{new}.xml')).findall('.//a:t',ns)]
        assert [t for t in prior if t!=f'{old:02d}'] == [t for t in current if t!=f'{new:02d}']

changes = []
for old in range(1,23):
    new = old if old<5 else old+1 if old<=14 else old+2
    a = Image.open(root / 'presentations/.build/nonexpert_story/rendered' / f'slide-{old:02d}.png').convert('RGB')
    b = Image.open(build / 'rendered' / f'slide-{new:02d}.png').convert('RGB')
    bbox = ImageChops.difference(a,b).getbbox()
    assert not bbox or (bbox[0]>=1740 and bbox[1]>=1023 and bbox[2]<=1771 and bbox[3]<=1045), (old,new,bbox)
    if bbox: changes.append({'source':old,'final':new,'bbox':bbox})
report = {'pptx_sha256':hashlib.sha256(deck.read_bytes()).hexdigest(),'slides':24,'notes':24,'native_tables':11,'native_charts':3,'embedded_workbooks':3,'preserved_chart_parts':9,'shortlist_rows_verified':4,'original_visual_content':'pixel-identical outside changed page numbers','plotted_evidence':'matches pinned JSON within 1e-8','forecast_ranges':'unchanged','source_notes_cross_references':'updated','page_number_changes':changes}
(build/'content-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='page_number_changes'},indent=2))
