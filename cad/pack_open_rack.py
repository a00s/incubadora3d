"""Replace the saved rack mesh and remove its superseded separate front ring."""
import json
import shutil
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET
from pack_forming_tools import CORE, PROD, NS, values, meta, load_mesh
ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'output/v59'
NAME='suporte_gavetas_removivel'
OBSOLETE='moldura_frontal_inox_removivel'


def pack():
    path=ROOT/'output/incubadora_CrealityPrint_7.2.1.3mf'
    with zipfile.ZipFile(path) as z:entries={i.filename:(i,z.read(i)) for i in z.infolist()}
    model=ET.fromstring(entries['3D/3dmodel.model'][1]);config=ET.fromstring(entries['Metadata/model_settings.config'][1])
    resources=model.find('m:resources',NS);build=model.find('m:build',NS)
    old_config=ET.fromstring(entries['Metadata/model_settings.config'][1])
    saved=next(o for o in config.findall('object') if values(o).get('name')==NAME)
    oid=saved.get('id');wrapper=next(o for o in resources if o.get('id')==oid)
    component=wrapper.find('m:components/m:component',NS);target=component.get(f'{{{PROD}}}path').lstrip('/')
    owner=ET.fromstring(entries[target][1]);obj=next(o for o in owner.find('m:resources',NS) if o.get('id')==component.get('objectid'))
    obj.remove(obj.find('m:mesh',NS));mesh=ET.SubElement(obj,f'{{{CORE}}}mesh')
    vertices,faces,dims=load_mesh(FOLDER/f'{NAME}.stl',lambda p:(p[0],-p[2],p[1]))
    item=next(i for i in build if i.get('objectid')==oid)
    transform=[float(v) for v in item.get('transform').split()]
    assert transform[:9]==[1,0,0,0,1,0,0,0,1]
    vv=ET.SubElement(mesh,f'{{{CORE}}}vertices');tt=ET.SubElement(mesh,f'{{{CORE}}}triangles')
    for p in vertices:
        p=(p[0],p[1],p[2]-transform[11])
        ET.SubElement(vv,f'{{{CORE}}}vertex',**{a:format(p[i],'.9g') for i,a in enumerate('xyz')})
    for face in faces:ET.SubElement(tt,f'{{{CORE}}}triangle',**{f'v{i+1}':str(v) for i,v in enumerate(face)})
    removed_files=set();removed_plates=set();modified_plate=None
    for p in config.findall('plate'):
        for instance in p.findall('model_instance'):
            if values(instance).get('object_id')==oid:
                modified_plate=values(p)['plater_id']
                for m in list(p.findall('metadata')):
                    if m.get('key') in ('thumbnail_file','thumbnail_no_light_file','top_file','pick_file'):
                        removed_files.add(m.get('value'));p.remove(m)
                removed_files.add(f'Metadata/plate_{modified_plate}_small.png')
    # Keep saved object settings; the thin beams are mostly perimeters.
    for obsolete in list(config.findall('object')):
        if values(obsolete).get('name')!=OBSOLETE:continue
        old_id=obsolete.get('id');old_wrapper=next(o for o in resources if o.get('id')==old_id)
        old_mid=old_wrapper.find('m:components/m:component',NS).get('objectid')
        for node in list(resources):
            if node.get('id') in (old_id,old_mid):resources.remove(node)
        for node in list(build):
            if node.get('objectid')==old_id:build.remove(node)
        for p in list(config.findall('plate')):
            for inst in list(p.findall('model_instance')):
                if values(inst).get('object_id')==old_id:p.remove(inst)
            if not p.findall('model_instance'):
                removed_plates.add(values(p)['plater_id']);config.remove(p)
        config.remove(obsolete)
    # Existing settings, other objects, and plate membership must be unchanged.
    current_objects={o.get('id'):o for o in config.findall('object')}
    for o in old_config.findall('object'):
        if values(o).get('name')!=OBSOLETE:assert ET.tostring(o)==ET.tostring(current_objects[o.get('id')])
    updates={target:ET.tostring(owner,encoding='utf-8',xml_declaration=True),
             '3D/3dmodel.model':ET.tostring(model,encoding='utf-8',xml_declaration=True),
             'Metadata/model_settings.config':ET.tostring(config,encoding='utf-8',xml_declaration=True)}
    tmp=path.with_suffix('.tmp')
    with zipfile.ZipFile(tmp,'w') as z:
        for n,(info,data) in entries.items():
            if n not in removed_files:z.writestr(info,updates.get(n,data))
    with zipfile.ZipFile(tmp) as z:
        assert z.testzip() is None
        for n,(_,data) in entries.items():
            if n not in updates and n not in removed_files:assert z.read(n)==data,n
    tmp.replace(path);shutil.copy2(path,FOLDER/'incubadora_v59_CrealityPrint_7.2.1.3mf')
    report=dict(peca=NAME,bandeja=int(modified_plate),dimensoes_impressao_mm=dims,configuracoes_anteriores_preservadas=True,moldura_separada_substituida_por_H_integrado=True,bandejas=len(config.findall('plate')),pecas=len(config.findall('object')),face_de_impressao='H frontal na mesa')
    (FOLDER/'open_rack_project_report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(report,indent=2,ensure_ascii=False))

if __name__=='__main__':pack()
