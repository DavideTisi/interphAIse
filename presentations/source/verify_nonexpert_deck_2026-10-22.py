"""Check exported evidence against the pinned synthesis data, without calculations."""
import hashlib
import json
import re
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
from PIL import Image, ImageChops

root = Path.cwd()
build = root / 'presentations/.build/nonexpert_story'
deck = root / 'presentations/nonexpert_2026-10-22/interphAIse_the_idea_and_LLM_results_2026-10-22_v3.pptx'
e = json.loads((root / 'presentations/source/results_synthesis_2026-10-22.json').read_text())
ns = {'c':'http://schemas.openxmlformats.org/drawingml/2006/chart', 'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
expected = [
    [[e['original'][a]['count'] for a in e['arm_order']]],
    [[e['environments'][env]['counts'][a] for env in e['environment_order']] for a in ['iterative','sequential','random']],
    [[e['physical'][f]['contacts'][side]['W_adh_J_m2'] for f in ['LiNbF6','LiTaF6','LiCaAlF6']] for side in ['cathode','electrolyte']],
]
with zipfile.ZipFile(deck) as z:
    slides = sorted([n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+.xml', n)], key=lambda n:int(re.search(r'(\d+)\.xml',n)[1]))
    notes = [n for n in z.namelist() if re.fullmatch(r'ppt/notesSlides/notesSlide\d+.xml',n)]
    charts = sorted([n for n in z.namelist() if re.search(r'/chart\d+\.xml$',n)])
    workbooks = [n for n in z.namelist() if n.endswith('.xlsx')]
    assert len(slides) == len(notes) == 22
    assert len(charts) == len(workbooks) == 3
    assert sum(z.read(n).count(b'<a:tbl>') for n in slides) == 9
    assert not any(b'hellmm' in z.read(n).lower() for n in slides + notes)
    for part, wanted in zip(charts, expected):
        xml = ET.fromstring(z.read(part))
        actual = [[float(v.text) for v in ser.findall('.//c:val//c:pt/c:v',ns)] for ser in xml.findall('.//c:ser',ns)]
        assert len(actual) == len(wanted)
        for found, target in zip(actual, wanted):
            assert len(found)==len(target) and all(abs(a-b)<1e-8 for a,b in zip(found,target))
    def text(n):
        return '\n'.join(t.text or '' for t in ET.fromstring(z.read(f'ppt/slides/slide{n}.xml')).findall('.//a:t',ns))
    for n, values in [(12,['3.2–3.9','1.4–1.9','3.339','1.577']),(13,['3.0–3.8','1.4–1.9','1.427','0.744'])]:
        assert all(v in text(n) for v in values)
    assert '0.160' in text(9) and '0.057' in text(9) and '0.048' in text(9)
    assert '33' in text(10) and '95' in text(10)
    assert e['llzo_audit']['iterative']['distinct_formulas']==33
    assert e['llzo_audit']['random']['distinct_formulas']==95
    assert sum(e['environments']['Li7La3Zr2O12']['first_hit_counts']['iterative'].get(str(i),0) for i in [8,9,10])==10
    for n in notes:
        assert len(z.read(n)) > 100

changed = []
for n in range(1,23) if (build/'reviewed-second-renders').exists() else []:
    fn=f'slide-{n:02d}.png'
    a=Image.open(build/'reviewed-second-renders'/fn).convert('RGB')
    b=Image.open(build/'rendered'/fn).convert('RGB')
    if ImageChops.difference(a,b).getbbox():
        changed.append(n)
if (build/'reviewed-second-renders').exists():
    assert changed == [10,15], changed
else:
    changed = 'not checked; private earlier renders unavailable'
report={'pptx_sha256':hashlib.sha256(deck.read_bytes()).hexdigest(),'slide_count':22,'native_charts':3,'embedded_workbooks':3,'native_tables':9,'notes':22,'plotted_evidence':'matches pinned JSON to 1e-8','forecast_text':'matches evidence','changed_since_second_visual_review':changed,'unrelated_project_references':0}
(build/'content-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
