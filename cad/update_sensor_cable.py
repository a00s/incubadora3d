"""Replace the user's separated sensor halves by a single TPU 85A cable plug."""
import json
import shutil
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import Counter
from pack_forming_tools import CORE, PROD, NS, values, load_mesh
ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'output/incubadora_CrealityPrint_7.2.1.3mf'
OUT=ROOT/'output/v59'

def update():
    with zipfile.ZipFile(PATH) as z: entries={i.filename:(i,z.read(i)) for i in z.infolist()}
    config=ET.fromstring(entries['Metadata/model_settings.config'][1])
    model=ET.fromstring(entries['3D/3dmodel.model'][1])
    resources=model.find('m:resources',NS); build=model.find('m:build',NS)
    candidates=[o for o in config.findall('object') if values(o).get('name','').startswith('TPU_passagem_sensor')]
    assert candidates
    saved=candidates[0];oid=saved.get('id');ids={o.get('id') for o in candidates[1:]}
    for m in saved.findall('metadata'):
        if m.get('key')=='name':m.set('value','TPU_passagem_sensor')
    for part in saved.findall('part'):
        for m in part.findall('metadata'):
            if m.get('key')=='name':m.set('value','TPU_passagem_sensor')
            if m.get('key')=='source_file':m.set('value','TPU_passagem_sensor.stl')
    wrapper=next(o for o in resources if o.get('id')==oid)
    component=wrapper.find('m:components/m:component',NS)
    target=component.get(f'{{{PROD}}}path').lstrip('/')
    owner=ET.fromstring(entries[target][1]);obj=next(o for o in owner.find('m:resources',NS) if o.get('id')==component.get('objectid'))
    points,faces,size=load_mesh(OUT/'TPU_passagem_sensor.stl')
    item=next(i for i in build if i.get('objectid')==oid)
    transform=[float(x) for x in item.get('transform').split()]
    assert transform[:9]==[1,0,0,0,1,0,0,0,1]
    assert size==[16.0,16.0,15.199999809265137] or all(abs(a-b)<.01 for a,b in zip(size,[16,16,15.2]))
    obj.remove(obj.find('m:mesh',NS));mesh=ET.SubElement(obj,f'{{{CORE}}}mesh')
    vv=ET.SubElement(mesh,f'{{{CORE}}}vertices');tt=ET.SubElement(mesh,f'{{{CORE}}}triangles')
    for p in points:ET.SubElement(vv,f'{{{CORE}}}vertex',**{a:format(p[j]-(transform[11] if j==2 else 0),'.9g') for j,a in enumerate('xyz')})
    for f in faces:ET.SubElement(tt,f'{{{CORE}}}triangle',**{f'v{j+1}':str(v) for j,v in enumerate(f)})
    edges=Counter(tuple(sorted((a,b))) for f in faces for a,b in zip(f,f[1:]+f[:1]))
    assert all(n==2 for n in edges.values())
    for o in candidates[1:]:config.remove(o)
    for o in list(resources):
        if o.get('id') in ids:resources.remove(o)
    for o in list(build):
        if o.get('objectid') in ids:build.remove(o)
    affected=[];removed=set()
    for plate in config.findall('plate'):
        instances=plate.findall('model_instance')
        if any(values(i).get('object_id') in ids|{oid} for i in instances):
            pid=int(values(plate)['plater_id']);affected.append(pid)
            for i in instances:
                if values(i).get('object_id') in ids:plate.remove(i)
            for m in list(plate.findall('metadata')):
                if m.get('key') in ('thumbnail_file','thumbnail_no_light_file','top_file','pick_file'):removed.add(m.get('value'));plate.remove(m)
            removed.add(f'Metadata/plate_{pid}_small.png')
            # Existing saved placement: retain XY, verify against its own bed.
            ox,oy=264*((pid-1)%6),-264*((pid-1)//6)
            assert 5<=transform[9]-8-ox and transform[9]+8-ox<=215
            assert 5<=transform[10]-8-oy and transform[10]+8-oy<=215
    for assembly in config.findall('assemble'):
        for i in list(assembly):
            if i.get('object_id') in ids:assembly.remove(i)
    updates={target:ET.tostring(owner,encoding='utf-8',xml_declaration=True),'3D/3dmodel.model':ET.tostring(model,encoding='utf-8',xml_declaration=True),'Metadata/model_settings.config':ET.tostring(config,encoding='utf-8',xml_declaration=True)}
    tmp=PATH.with_suffix('.tmp')
    with zipfile.ZipFile(tmp,'w') as z:
        for n,(info,data) in entries.items():
            if n not in removed:z.writestr(info,updates.get(n,data))
    with zipfile.ZipFile(tmp) as z:
        assert z.testzip() is None
        for n,(_,data) in entries.items():
            if n not in updates and n not in removed:assert z.read(n)==data,n
    # Every other object's saved settings remain exact.
    old=ET.fromstring(entries['Metadata/model_settings.config'][1])
    current={o.get('id'):o for o in config.findall('object')}
    for o in old.findall('object'):
        if o.get('id') not in ids|{oid}:assert ET.tostring(o)==ET.tostring(current[o.get('id')])
    tmp.replace(PATH);shutil.copy2(PATH,OUT/'incubadora_v59_CrealityPrint_7.2.1.3mf')
    report=dict(peca='TPU_passagem_sensor',bandejas_afetadas=affected,pecas_sensor=1,malha_fechada=True,limites_k1c_com_margem_5mm=True,dimensoes_mm=size,configuracoes_demais_objetos_preservadas=True,perfis_salvos_preservados=True)
    (OUT/'sensor_cable_project_report.json').write_text(json.dumps(report,indent=2)+'\n');print(report)

if __name__=='__main__':update()
