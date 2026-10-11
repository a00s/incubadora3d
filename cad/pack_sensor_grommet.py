"""Update only the three TPU sensor meshes in the user's saved project."""
import json
import shutil
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET
from pack_forming_tools import CORE, PROD, NS, values, load_mesh
ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'output/v59'
NAMES=('bucha_sensor_TPU','amostra_bucha_sensor_TPU_15.3','amostra_bucha_sensor_TPU_15.5')


def pack():
    path=ROOT/'output/incubadora_CrealityPrint_7.2.1.3mf'
    with zipfile.ZipFile(path) as z:entries={i.filename:(i,z.read(i)) for i in z.infolist()}
    model=ET.fromstring(entries['3D/3dmodel.model'][1]);config=ET.fromstring(entries['Metadata/model_settings.config'][1])
    resources=model.find('m:resources',NS);build=model.find('m:build',NS)
    updates={};removed=set();records=[]
    for name in NAMES:
        saved=next(o for o in config.findall('object') if values(o).get('name')==name)
        oid=saved.get('id');wrapper=next(o for o in resources if o.get('id')==oid)
        component=wrapper.find('m:components/m:component',NS)
        target=component.get(f'{{{PROD}}}path').lstrip('/')
        owner=ET.fromstring(updates.get(target,entries[target][1]))
        obj=next(o for o in owner.find('m:resources',NS) if o.get('id')==component.get('objectid'))
        obj.remove(obj.find('m:mesh',NS));mesh=ET.SubElement(obj,f'{{{CORE}}}mesh')
        points,faces,size=load_mesh(FOLDER/f'{name}.stl')
        item=next(i for i in build if i.get('objectid')==oid);transform=[float(v) for v in item.get('transform').split()]
        assert transform[:9]==[1,0,0,0,1,0,0,0,1]
        vv=ET.SubElement(mesh,f'{{{CORE}}}vertices');tt=ET.SubElement(mesh,f'{{{CORE}}}triangles')
        for p in points:
            p=(p[0],p[1],p[2]-transform[11])
            ET.SubElement(vv,f'{{{CORE}}}vertex',**{a:format(p[i],'.9g') for i,a in enumerate('xyz')})
        for face in faces:ET.SubElement(tt,f'{{{CORE}}}triangle',**{f'v{i+1}':str(v) for i,v in enumerate(face)})
        updates[target]=ET.tostring(owner,encoding='utf-8',xml_declaration=True)
        plate=next(p for p in config.findall('plate') if any(values(i).get('object_id')==oid for i in p.findall('model_instance')))
        pid=int(values(plate)['plater_id'])
        for m in list(plate.findall('metadata')):
            if m.get('key') in ('thumbnail_file','thumbnail_no_light_file','top_file','pick_file'):
                removed.add(m.get('value'));plate.remove(m)
        removed.add(f'Metadata/plate_{pid}_small.png')
        records.append(dict(peca=name,bandeja=pid,dimensoes_impressao_mm=size))
    updates['Metadata/model_settings.config']=ET.tostring(config,encoding='utf-8',xml_declaration=True)
    tmp=path.with_suffix('.tmp')
    with zipfile.ZipFile(tmp,'w') as z:
        for n,(info,data) in entries.items():
            if n not in removed:z.writestr(info,updates.get(n,data))
    with zipfile.ZipFile(tmp) as z:
        assert z.testzip() is None
        for n,(_,data) in entries.items():
            if n not in updates and n not in removed:assert z.read(n)==data,n
    old=ET.fromstring(entries['Metadata/model_settings.config'][1])
    assert all(ET.tostring(a)==ET.tostring(b) for a,b in zip(old.findall('object'),config.findall('object')))
    tmp.replace(path);shutil.copy2(path,FOLDER/'incubadora_v59_CrealityPrint_7.2.1.3mf')
    report=dict(configuracoes_salvas_preservadas=True,pecas=records)
    (FOLDER/'sensor_grommet_project_report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(report,indent=2,ensure_ascii=False))

if __name__=='__main__':pack()
