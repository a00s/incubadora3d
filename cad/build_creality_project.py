"""Package existing STL meshes as a Creality Print 7.2.1 multi-plate project.
Generic filament presets only; no custom filament or process overrides.
The model/plate schema and 1.2-bed-width plate grid follow the official
CrealityPrint v7.2.1 bbs_3mf.cpp and PartPlate.cpp implementation.
"""
import argparse
import json
import math
from pathlib import Path
import struct
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--version', default='v59')
args = parser.parse_args()
FOLDER = ROOT / 'output' / args.version
DEST = FOLDER / f'incubadora_{args.version}_CrealityPrint_7.2.1.3mf'
CORE = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
ET.register_namespace('', CORE)
IDENTITY = '1 0 0 0 1 0 0 0 1 0 0 0'
MATRIX = '1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1'


def metadata(parent, key, value):
    return ET.SubElement(parent, 'metadata', key=key, value=str(value))


def xml_bytes(node):
    return ET.tostring(node, encoding='utf-8', xml_declaration=True)


def orient(name, point):
    x, y, z = point
    # The body uses its dedicated rear-down STL, and the mould is already flat.
    if name in ('porta_articulada', 'painel_interno_escotilha_encaixe', 'tampa_manutencao_CO2_eletronica',
                'suporte_gavetas_removivel', 'caixinha_encaixe_aquecedor', 'junta_porta', 'junta_V_porta_TPU',
                'TPU_passagem_aquecedor') or name.startswith('lingueta_fecho'):
        return x, z, -y
    if name == 'TPU_passagem_sensor':
        return -z, y, x
    if name.startswith('pino_dobradica'):
        return x, -y, -z
    if name.startswith('manipulo_fecho'):
        return x, -z, y
    return point


def read_stl(path):
    raw = path.read_bytes()
    count = struct.unpack_from('<I', raw, 80)[0]
    assert len(raw) == 84 + count * 50, path
    vertices, triangles, index = [], [], {}
    for record in struct.iter_unpack('<12fH', raw[84:]):
        face = []
        for start in (3, 6, 9):
            point = tuple(orient(path.stem, record[start:start + 3]))
            if point not in index:
                index[point] = len(vertices)
                vertices.append(point)
            face.append(index[point])
        # Binary STL quantization may collapse duplicate corners: these faces have zero area.
        if len(set(face))==3:triangles.append(face)
    low = [min(v[a] for v in vertices) for a in range(3)]
    high = [max(v[a] for v in vertices) for a in range(3)]
    size = [high[a] - low[a] for a in range(3)]
    shift = [-(low[0] + high[0]) / 2, -(low[1] + high[1]) / 2, -low[2]]
    vertices = [tuple(v[a] + shift[a] for a in range(3)) for v in vertices]
    # All transformations are rotations and translations, never scaling.
    assert size[0] + 10 <= 220.01 and size[1] + 10 <= 220.01 and size[2] <= 250.01
    return vertices, triangles, size


paths = list(FOLDER.glob('*.stl'))
priority = ['corpo_integrado', 'porta_articulada', 'tampa_manutencao_CO2_eletronica',
            'suporte_gavetas_removivel', 'bandeja_1', 'bandeja_2', 'bandeja_3',
            'reservatorio_agua', 'caixinha_encaixe_aquecedor', 'molde_caixa_inox_referencia']
paths.sort(key=lambda p: (0, priority.index(p.stem)) if p.stem in priority else
           (2 if p.stem.startswith('amostra_') else 1, p.stem))
assert len(paths) <= 36, 'Creality Print 7.2.1 supports at most 36 plates'
columns = math.ceil(math.sqrt(len(paths)))
model = ET.Element(f'{{{CORE}}}model', unit='millimeter', **{'{http://www.w3.org/XML/1998/namespace}lang': 'pt-BR'})
for key, value in [('Application', 'Creality_Print V7.2.1.5476'),
                   ('BambuStudio:3mfVersion', '1'),
                   ('Title', f'Incubadora {args.version} - pecas e amostras por bandeja'),
                   ('Description', 'Projeto organizado, nao fatiado. Perfis genericos PC/TPU; selecionar perfil padrao e ajustar temperatura no fatiador.')]:
    ET.SubElement(model, f'{{{CORE}}}metadata', name=key).text = value
resources = ET.SubElement(model, f'{{{CORE}}}resources')
build = ET.SubElement(model, f'{{{CORE}}}build')
config = ET.Element('config')
plates = []
for i, original in enumerate(paths):
    name = original.stem
    path = FOLDER / 'impressao_traseira_na_mesa' / original.name if name == 'corpo_integrado' else original
    vertices, triangles, size = read_stl(path)
    mesh_id, object_id = 2 * i + 1, 2 * i + 2
    obj = ET.SubElement(resources, f'{{{CORE}}}object', id=str(mesh_id), type='model', name=name)
    mesh = ET.SubElement(obj, f'{{{CORE}}}mesh')
    vv = ET.SubElement(mesh, f'{{{CORE}}}vertices')
    for point in vertices:
        ET.SubElement(vv, f'{{{CORE}}}vertex', **{a: format(point[j], '.9g') for j, a in enumerate('xyz')})
    tt = ET.SubElement(mesh, f'{{{CORE}}}triangles')
    for face in triangles:
        ET.SubElement(tt, f'{{{CORE}}}triangle', **{f'v{j + 1}': str(value) for j, value in enumerate(face)})
    wrapper = ET.SubElement(resources, f'{{{CORE}}}object', id=str(object_id), type='model', name=name)
    components = ET.SubElement(wrapper, f'{{{CORE}}}components')
    ET.SubElement(components, f'{{{CORE}}}component', objectid=str(mesh_id), transform=IDENTITY)
    ox, oy = 264 * (i % columns), -264 * (i // columns)
    transform = f'1 0 0 0 1 0 0 0 1 {110 + ox} {110 + oy} 0'
    ET.SubElement(build, f'{{{CORE}}}item', objectid=str(object_id), transform=transform, printable='1')
    material = 'TPU' if 'TPU' in name or name == 'junta_porta' else 'PC'
    label = f'{i + 1:02d} - {material} - {name}'
    record = ET.SubElement(config, 'object', id=str(object_id))
    metadata(record, 'name', name)
    metadata(record, 'extruder', 2 if material == 'TPU' else 1)
    part = ET.SubElement(record, 'part', id=str(mesh_id), subtype='normal_part')
    metadata(part, 'name', name)
    metadata(part, 'matrix', MATRIX)
    metadata(part, 'source_file', original.name)
    metadata(part, 'source_object_id', 0)
    metadata(part, 'source_volume_id', 0)
    plate = ET.SubElement(config, 'plate')
    for key, value in [('plater_id', i + 1), ('plater_name', label), ('locked', 'false')]:
        metadata(plate, key, value)
    instance = ET.SubElement(plate, 'model_instance')
    for key, value in [('object_id', object_id), ('instance_id', 0), ('identify_id', object_id)]:
        metadata(instance, key, value)
    plates.append(dict(bandeja=i + 1, nome=label, arquivo=original.name,
                       material=material, objeto_id=object_id, malha_id=mesh_id,
                       origem_mm=[ox, oy, 0], dimensoes_mm=[round(v, 4) for v in size],
                       vertices=len(vertices), triangulos=len(triangles),
                       faces_de_area_zero_removidas=struct.unpack_from('<I',path.read_bytes(),80)[0]-len(triangles),
                       orientacao='traseira na mesa' if name == 'corpo_integrado' else
                       'orientacao inicial; revisar no fatiador'))

# Reference standard presets without embedding custom filament settings.
settings = dict(printer_settings_id='Creality K1C 0.4 nozzle', printer_model='Creality K1C',
                print_settings_id='0.20mm Standard @Creality K1C 0.4 nozzle',
                printer_variant='0.4', nozzle_diameter=['0.4'], printer_technology='FFF',
                printable_area=['0x0', '220x0', '220x220', '0x220'], printable_height='250',
                filament_settings_id=['Generic PC @Creality K1C 0.4 nozzle', 'Generic TPU @Creality K1C 0.4 nozzle'],
                filament_type=['PC', 'TPU'], filament_colour=['#F08A24', '#45AE89'])
settings.update(filament_diameter=['1.75', '1.75'], filament_is_support=['0', '0'])
creality = ET.Element('config')
for key, value in [('Company', 'Creality'), ('Application', 'Creality_Print'),
                   ('AppVersion', '7.2.1.5476'), ('AppStage', 'Release'),
                   ('FileVersion', '1.0'), ('FileType', 'Undefined')]:
    metadata(creality, key, value)
content_types = ET.Element('Types', xmlns='http://schemas.openxmlformats.org/package/2006/content-types')
for extension, mime in [('rels', 'application/vnd.openxmlformats-package.relationships+xml'),
                        ('model', 'application/vnd.ms-package.3dmanufacturing-3dmodel+xml'),
                        ('config', 'application/xml')]:
    ET.SubElement(content_types, 'Default', Extension=extension, ContentType=mime)
rels = ET.Element('Relationships', xmlns='http://schemas.openxmlformats.org/package/2006/relationships')
ET.SubElement(rels, 'Relationship', Id='rel0', Target='/3D/3dmodel.model',
              Type='http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel')
with zipfile.ZipFile(DEST, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
    for member, value in [('[Content_Types].xml', xml_bytes(content_types)), ('_rels/.rels', xml_bytes(rels)),
                          ('3D/3dmodel.model', xml_bytes(model)), ('Metadata/model_settings.config', xml_bytes(config)),
                          ('Metadata/project_settings.config', json.dumps(settings, ensure_ascii=False).encode()),
                          ('Metadata/creality.config', xml_bytes(creality))]:
        archive.writestr(member, value)
manifest = dict(arquivo=DEST.name, versao_creality='7.2.1', impressora='K1C',
                bico_inicial_mm=.4, bico_observacao='Confirmar o bico instalado no Creality Print',
                bandejas=plates, fatiado=False, gcode_incluido=False,
                perfis_filamento='Genericos PC/TPU; selecionar perfil padrao no fatiador',
                configuracoes_filamento_personalizadas=False,
                perfis_termicos_validados=False, colunas=columns, passo_bandejas_mm=264)
(FOLDER / 'bandejas_creality.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
print(f'{DEST}: {len(plates)} bandejas, {DEST.stat().st_size} bytes')
