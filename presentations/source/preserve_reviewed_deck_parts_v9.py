"""Transplant Artifact Tool text/geometry edits, preserving original native evidence.

Only explicitly edited shapes, speaker-note bodies and required hyperlink
relationships change. Charts, workbooks, logos and unchanged layouts stay exact.
"""
import copy
import json
import sys
import zipfile
from lxml import etree as ET

source, draft, manifest, output = sys.argv[1:]
ns = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
rel_ns = 'http://schemas.openxmlformats.org/package/2006/relationships'
normalize = lambda text: ''.join(text.split())
def find_shape(root, text):
    shapes = [e for e in root.findall('.//p:spTree/p:sp', ns)
              if normalize(''.join(e.xpath('.//a:t/text()', namespaces=ns))) == normalize(text)]
    assert len(shapes) == 1, (text, len(shapes))
    return shapes[0]
def dump(root):
    return ET.tostring(root, encoding='utf-8', xml_declaration=True, standalone=True)

changes = json.load(open(manifest))
with zipfile.ZipFile(source) as src, zipfile.ZipFile(draft) as author:
    patches = {}
    for slide, edits in changes['slides'].items():
        name = f'ppt/slides/slide{slide}.xml'
        root, changed = ET.fromstring(src.read(name)), ET.fromstring(author.read(name))
        relname = f'ppt/slides/_rels/slide{slide}.xml.rels'
        rels = ET.fromstring(src.read(relname))
        authored_rels = ET.fromstring(author.read(relname))
        added = 0
        for edit in edits:
            before, after = find_shape(root, edit['before']), find_shape(changed, edit['after'])
            body = copy.deepcopy(after.find('p:txBody', ns))
            for link in body.xpath('.//a:hlinkClick', namespaces=ns):
                rid = link.get('{'+ns['r']+'}id')
                entries = [e for e in authored_rels if e.get('Id') == rid]
                assert len(entries) == 1
                added += 1
                fresh = f'rIdV9Link{added}'
                assert not any(e.get('Id') == fresh for e in rels)
                relation = copy.deepcopy(entries[0]); relation.set('Id', fresh)
                rels.append(relation); link.set('{'+ns['r']+'}id', fresh)
            before.replace(before.find('p:txBody', ns), body)
            old_xfrm = before.find('p:spPr/a:xfrm', ns)
            new_xfrm = after.find('p:spPr/a:xfrm', ns)
            assert old_xfrm is not None and new_xfrm is not None
            old_xfrm.getparent().replace(old_xfrm, copy.deepcopy(new_xfrm))
        patches[name] = dump(root)
        if added: patches[relname] = dump(rels)
    for slide in range(1, changes['slide_count'] + 1):
        name = f'ppt/notesSlides/notesSlide{slide}.xml'
        root, changed = ET.fromstring(src.read(name)), ET.fromstring(author.read(name))
        def note_body(r):
            found = r.xpath('.//p:sp[p:nvSpPr/p:nvPr/p:ph[@type="body"]]/p:txBody', namespaces=ns)
            assert len(found) == 1
            return found[0]
        original = note_body(root)
        original.getparent().replace(original, copy.deepcopy(note_body(changed)))
        patches[name] = dump(root)
        assert b'/Users/' not in patches[name]
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as out:
        for info in src.infolist():
            out.writestr(info, patches.get(info.filename, src.read(info.filename)))
with zipfile.ZipFile(source) as src, zipfile.ZipFile(output) as out:
    assert set(src.namelist()) == set(out.namelist())
    actual = [n for n in src.namelist() if src.read(n) != out.read(n)]
    assert set(actual) <= set(patches)
    evidence = [n for n in src.namelist() if '/charts/' in n or n.endswith('.xlsx') or n.startswith('ppt/media/')]
    assert all(src.read(n) == out.read(n) for n in evidence)
print(json.dumps({'changed_parts': actual, 'preserved_chart_workbook_media_parts': len(evidence)}))
