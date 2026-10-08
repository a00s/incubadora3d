"""Add the split dies to the last two PC sample plates, preserving saved settings."""
from pathlib import Path
import json
import struct
import xml.etree.ElementTree as ET
import zipfile

CORE = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
PROD = 'http://schemas.microsoft.com/3dmanufacturing/production/2015/06'
NS = {'m': CORE}
IDENTITY = '1 0 0 0 1 0 0 0 1'
ET.register_namespace('', CORE)
ET.register_namespace('p', PROD)
ET.register_namespace('BambuStudio', 'http://schemas.bambulab.com/package/2021')


def values(node):
    return {n.get('key'): n.get('value') for n in node.findall('metadata')}


def meta(parent, key, value):
    ET.SubElement(parent, 'metadata', key=key, value=str(value))


def load_mesh(path):
    data = path.read_bytes()
    assert len(data) == 84 + struct.unpack_from('<I', data, 80)[0] * 50
    points, faces, ids = [], [], {}
    for record in struct.iter_unpack('<12fH', data[84:]):
        face = []
        for start in (3, 6, 9):
            point = tuple(record[start:start+3])
            if point not in ids:
                ids[point] = len(points)
                points.append(point)
            face.append(ids[point])
        if len(set(face)) == 3:
            faces.append(face)
    lo = [min(p[a] for p in points) for a in range(3)]
    hi = [max(p[a] for p in points) for a in range(3)]
    shift = [(lo[0]+hi[0])/2, (lo[1]+hi[1])/2, lo[2]]
    points = [tuple(p[a]-shift[a] for a in range(3)) for p in points]
    return points, faces, [hi[a]-lo[a] for a in range(3)]


def pack_tools(path, folder):
    path, folder = Path(path), Path(folder)
    with zipfile.ZipFile(path) as z:
        entries = {i.filename: (i, z.read(i)) for i in z.infolist()}
    model = ET.fromstring(entries['3D/3dmodel.model'][1])
    config = ET.fromstring(entries['Metadata/model_settings.config'][1])
    resources = model.find('m:resources', NS)
    build = model.find('m:build', NS)
    # Replace previous die revisions while retaining every other saved object.
    for obj in list(config.findall('object')):
        if values(obj).get('name') not in ('contraforma_inox_inferior','contraforma_inox_superior'):
            continue
        oid = obj.get('id')
        wrapper = next(o for o in resources if o.get('id') == oid)
        mid = wrapper.find('m:components/m:component',NS).get('objectid')
        for node in list(resources):
            if node.get('id') in (oid,mid):resources.remove(node)
        for node in list(build):
            if node.get('objectid') == oid:build.remove(node)
        for plate in config.findall('plate'):
            for inst in list(plate.findall('model_instance')):
                if values(inst).get('object_id') == oid:plate.remove(inst)
        config.remove(obj)
    next_id = max(int(o.get('id')) for o in resources) + 1
    updates, removed = {}, set()
    # Update the existing male too: its three blind pilot marks are new geometry.
    male_config = next(o for o in config.findall('object') if values(o).get('name')=='molde_caixa_inox_referencia')
    male_id = male_config.get('id')
    wrapper = next(o for o in resources if o.get('id')==male_id)
    component = wrapper.find('m:components/m:component',NS)
    mesh_path = component.get(f'{{{PROD}}}path')
    owner = ET.fromstring(entries[mesh_path.lstrip('/')][1]) if mesh_path else model
    mesh_owner = next(o for o in owner.find('m:resources',NS) if o.get('id')==component.get('objectid'))
    old_mesh = mesh_owner.find('m:mesh',NS)
    mesh_owner.remove(old_mesh)
    new_mesh = ET.SubElement(mesh_owner,f'{{{CORE}}}mesh')
    vv = ET.SubElement(new_mesh,f'{{{CORE}}}vertices')
    points,triangles,_ = load_mesh(folder/'molde_caixa_inox_referencia.stl')
    item = next(i for i in build if i.get('objectid')==male_id)
    dz=float(item.get('transform').split()[11])
    for point in points:
        point=(point[0],point[1],point[2]-dz)
        ET.SubElement(vv,f'{{{CORE}}}vertex',**{a:format(point[j],'.9g') for j,a in enumerate('xyz')})
    tt=ET.SubElement(new_mesh,f'{{{CORE}}}triangles')
    for face in triangles:
        ET.SubElement(tt,f'{{{CORE}}}triangle',**{f'v{j+1}':str(v) for j,v in enumerate(face)})
    if mesh_path:updates[mesh_path.lstrip('/')]=ET.tostring(owner,encoding='utf-8',xml_declaration=True)
    male_plate = next(p for p in config.findall('plate') if any(values(i).get('object_id')==male_id for i in p.findall('model_instance')))
    for m in list(male_plate.findall('metadata')):
        if m.get('key') in ('thumbnail_file','thumbnail_no_light_file','top_file','pick_file'):
            removed.add(m.get('value'));male_plate.remove(m)
    removed.add('Metadata/plate_10_small.png')
    records = []
    for plate_index, name in ((35, 'contraforma_inox_inferior'), (36, 'contraforma_inox_superior')):
        plate = next(p for p in config.findall('plate') if values(p).get('plater_id') == str(plate_index))
        instance = plate.find('model_instance')
        sample_id = values(instance)['object_id']
        sample = next(i for i in build if i.get('objectid') == sample_id)
        transform = sample.get('transform').split()
        ox, oy = 264*((plate_index-1)%6), -264*((plate_index-1)//6)
        # Park the small existing sample behind the die, on the same plate.
        assert [float(v) for v in transform[:9]] == [1,0,0,0,1,0,0,0,1]
        transform[9:11] = [str(ox+110), str(oy+175)]
        sample.set('transform', ' '.join(transform))
        vertices, faces, size = load_mesh(folder/'ferramental_inox'/f'{name}.stl')
        mesh_id, object_id = next_id, next_id+1
        next_id += 2
        obj = ET.SubElement(resources, f'{{{CORE}}}object', id=str(mesh_id), type='model', name=name)
        mesh = ET.SubElement(obj, f'{{{CORE}}}mesh')
        vv = ET.SubElement(mesh, f'{{{CORE}}}vertices')
        for point in vertices:
            ET.SubElement(vv, f'{{{CORE}}}vertex', **{a:format(point[j], '.9g') for j,a in enumerate('xyz')})
        tt = ET.SubElement(mesh, f'{{{CORE}}}triangles')
        for face in faces:
            ET.SubElement(tt, f'{{{CORE}}}triangle', **{f'v{j+1}':str(v) for j,v in enumerate(face)})
        wrapper = ET.SubElement(resources, f'{{{CORE}}}object', id=str(object_id), type='model', name=name)
        comp = ET.SubElement(wrapper, f'{{{CORE}}}components')
        ET.SubElement(comp, f'{{{CORE}}}component', objectid=str(mesh_id), transform=IDENTITY+' 0 0 0')
        ET.SubElement(build, f'{{{CORE}}}item', objectid=str(object_id), transform=IDENTITY+f' {ox+110} {oy+75} 0', printable='1')
        obj_config = ET.SubElement(config, 'object', id=str(object_id))
        meta(obj_config, 'name', name);meta(obj_config, 'extruder', 1)
        part = ET.SubElement(obj_config, 'part', id=str(mesh_id), subtype='normal_part')
        for key,value in [('name',name),('matrix','1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1'),('source_file',f'{name}.stl'),('source_object_id',0),('source_volume_id',0)]:
            meta(part,key,value)
        new_instance = ET.SubElement(plate,'model_instance')
        for key,value in [('object_id',object_id),('instance_id',0),('identify_id',object_id)]:
            meta(new_instance,key,value)
        for m in list(plate.findall('metadata')):
            if m.get('key')=='plater_name':m.set('value',f'{plate_index:02d} - PC - {name} + amostra')
            if m.get('key') in ('thumbnail_file','thumbnail_no_light_file','top_file','pick_file'):
                removed.add(m.get('value'));plate.remove(m)
        removed.add(f'Metadata/plate_{plate_index}_small.png')
        records.append(dict(bandeja=plate_index, arquivo=f'ferramental_inox/{name}.stl', material='PC',objeto_id=object_id,malha_id=mesh_id,origem_mm=[ox,oy,0],centro_local_mm=[110,75,0],dimensoes_mm=[round(v,4) for v in size],vertices=len(vertices),triangulos=len(faces)))
    updates['3D/3dmodel.model'] = ET.tostring(model, encoding='utf-8', xml_declaration=True)
    updates['Metadata/model_settings.config'] = ET.tostring(config, encoding='utf-8', xml_declaration=True)
    tmp = path.with_suffix('.tmp')
    with zipfile.ZipFile(tmp,'w') as z:
        for name,(info,data) in entries.items():
            if name not in removed:z.writestr(info,updates.get(name,data))
    with zipfile.ZipFile(tmp) as z:
        assert z.testzip() is None
        for name,(_,data) in entries.items():
            if name not in removed|updates.keys():assert z.read(name)==data,name
    tmp.replace(path)
    return records


if __name__ == '__main__':
    root=Path(__file__).resolve().parents[1]
    folder=root/'output/v59'
    print(json.dumps(pack_tools(root/'output/incubadora_CrealityPrint_7.2.1.3mf',folder),indent=2))
