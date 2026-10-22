"""Offline evidence, package-preservation and public-link checks for v9."""
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as E
import hashlib
import json
import re
root=Path.cwd()
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}
models={'Haiku 5.5':json.loads((root/'data/experiments/environment_v1/environment_summary.json').read_text()),'DeepSeek V3.2':json.loads((root/'data/experiments/deepseek_v1/environment_summary.json').read_text())}
envs=['Li6PS5Cl','Li3InCl6','Li7La3Zr2O12']
arms={'Upfront shortlist':'upfront','Mixed-up results':'shuffled','No results':'sequential','Correct feedback':'iterative'}
assertions=0
records=[]
for stem,count,closing in [('4_minute_pitch',8,8),('15_minute_talk',24,20)]:
    file=root/f'presentations/two_formats_2026-10-22/interphAIse_{stem}_2026-10-22_v9.pptx'
    source=root/f'presentations/source/reference_v8/interphAIse_{stem}_2026-10-22_v8.pptx'
    with ZipFile(file) as z, ZipFile(source) as old:
        assert set(z.namelist())==set(old.namelist())
        notes=[]
        for i in range(1,count+1):
            slide=f'ppt/slides/slide{i}.xml'
            before=E.fromstring(old.read(slide));after=E.fromstring(z.read(slide))
            assert [E.tostring(t) for t in before.findall('.//a:tbl',ns)]==[E.tostring(t) for t in after.findall('.//a:tbl',ns)]
            text='\n'.join(E.fromstring(z.read(f'ppt/notesSlides/notesSlide{i}.xml')).itertext())
            assert '/Users/' not in text
            notes.append(text)
        for n,env in enumerate(envs,1):
            name=f'ppt/slides/charts/chart{n}.xml'
            assert z.read(name)==old.read(name)
            chart=E.fromstring(z.read(name))
            axis=chart.find('.//c:valAx',ns)
            assert axis.find('c:tickLblPos',ns).get('val')=='low'
            assert float(axis.find('c:crossesAt',ns).get('val'))==0
            for series in chart.findall('.//c:ser',ns):
                model=series.find('c:tx/c:v',ns).text
                labels=[v.text for v in series.findall('c:cat//c:pt/c:v',ns)]
                values=[float(v.text) for v in series.findall('c:val//c:pt/c:v',ns)]
                for label,value in zip(labels,values):
                    assert value==models[model]['environments'][env]['arms'][arms[label]]['acceptable']
                    assertions+=1
        for name in z.namelist():
            if '/charts/' in name or name.endswith('.xlsx') or name.startswith('ppt/media/'):
                assert z.read(name)==old.read(name)
        public=set(re.findall(r'https://github.com/DavideTisi/interphAIse/blob/main/([^\s]+)','\n'.join(notes)))
        for relative in public:
            assert (root/relative).is_file(),relative
        rels=E.fromstring(z.read(f'ppt/slides/_rels/slide{closing}.xml.rels'))
        urls={r.get('Target') for r in rels if r.get('TargetMode')=='External'}
        assert {'https://github.com/DavideTisi/interphAIse','https://davidetisi.github.io/interphAIse/'} <= urls
    records.append({'path':str(file.relative_to(root)),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'slides':count,'verified_public_note_sources':len(public),'native_tables_charts_workbooks_media':'unchanged from v8'})
assert assertions==48
result={'chart_values_verified_against_final_archives':assertions,'decks':records}
(root/'runs/presentations_v9').mkdir(parents=True,exist_ok=True)
(root/'runs/presentations_v9/evidence-checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
