"""Retain the v3 chart XML, relationships and workbooks unchanged in the v4 edit."""
import sys
import zipfile
import xml.etree.ElementTree as ET

source, candidate, output = sys.argv[1:]
ct_path = '[Content_Types].xml'
ns = 'http://schemas.openxmlformats.org/package/2006/content-types'
ET.register_namespace('', ns)
with zipfile.ZipFile(source) as src, zipfile.ZipFile(candidate) as dst:
    parts = [n for n in src.namelist() if n.startswith('ppt/slides/charts/') or n.startswith('ppt/embeddings/chart-data-snapshot-')]
    assert len(parts) == 9, parts
    for slide, chart in [(8, 1), (9, 2), (15, 3)]:
        assert f'/ppt/slides/charts/chart{chart}.xml' in dst.read(f'ppt/slides/_rels/slide{slide}.xml.rels').decode()
    content_types = ET.fromstring(dst.read(ct_path))
    existing = {(e.tag, e.get('Extension'), e.get('PartName')) for e in content_types}
    for entry in ET.fromstring(src.read(ct_path)):
        if (entry.get('PartName') or '').lstrip('/') in parts or entry.get('Extension') == 'xlsx':
            key = (entry.tag, entry.get('Extension'), entry.get('PartName'))
            if key not in existing:
                content_types.append(entry)
                existing.add(key)
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as out:
        for item in dst.infolist():
            if item.filename not in parts and item.filename != ct_path:
                out.writestr(item, dst.read(item.filename))
        for name in parts:
            out.writestr(name, src.read(name))
        out.writestr(ct_path, ET.tostring(content_types, encoding='utf-8', xml_declaration=True))
with zipfile.ZipFile(source) as src, zipfile.ZipFile(output) as out:
    assert all(src.read(name) == out.read(name) for name in parts)
print(f'Preserved {len(parts)} chart/workbook parts byte for byte.')
