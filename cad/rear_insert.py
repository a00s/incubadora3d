"""Rear spreader inside the already formed liner; regenerate without changing saved settings."""
from pathlib import Path
import json
import shutil
import zipfile
import xml.etree.ElementTree as ET
import cadquery as cq
from forming_tools import box
from pack_forming_tools import CORE, NS, IDENTITY, values, meta, load_mesh
ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'output/v59'
NAME='fundo_interno_inox_5mm'


def export():
    # 0.6 mm inset on each edge of the historical male; same corner centres.
    part=box(109.2,5,129.2,5.4,104.7,5.4).edges('|Y').fillet(4.6)
    part=part.cut(cq.Workplane('XZ',origin=(60,110,116)).circle(7).extrude(6))
    assert part.val().isValid() and len(part.solids().vals())==1
    liner=cq.importers.importStep(str(FOLDER/'revestimento_inox_referencia.step'))
    assert part.intersect(liner).val().Volume()<1e-5
    # Existing rack, drawers and mixer must remain clear at the installed position.
    checked=[]
    for mesh in json.loads((FOLDER/'mesh.json').read_text()):
        if mesh['kind'] in ('rack','tray'):
            assert max(v[1] for v in mesh['vertices']) < 104.7, mesh['name']
            checked.append(mesh['name'])
    cq.exporters.export(part,str(FOLDER/f'{NAME}.step'))
    flat=part.rotate((0,0,0),(1,0,0),90)
    bb=flat.val().BoundingBox()
    flat=flat.translate((-bb.xmin,-bb.ymin,-bb.zmin))
    bb=flat.val().BoundingBox()
    assert bb.xlen+10<220 and bb.ylen+10<220 and abs(bb.zlen-5)<.001
    cq.exporters.export(flat,str(FOLDER/f'{NAME}.stl'))
    vertices,faces=part.val().tessellate(.15,.2)
    (FOLDER/'rear_insert_mesh.json').write_text(json.dumps([dict(name=NAME,kind='rear_insert',color='#da9560',vertices=[[v.x,v.y,v.z] for v in vertices],faces=faces)],separators=(',',':')))
    return dict(dimensoes_mm=[109.2,129.2,5],reducao_por_borda_mm=.6,raio_mm=4.6,furo_diametro_mm=14,furo_centro_cad_mm=[60,110,116],posicao_y_mm=[104.7,109.7],sem_interferencia_inox=True,pecas_conferidas=checked,solido_valido=True,limites_k1c=True,encaixe_fisico_pendente=True)


def pack(name=NAME, label="Fundo interno inox 5 mm"):
    part_name=name
    path=ROOT/'output/incubadora_CrealityPrint_7.2.1.3mf'
    with zipfile.ZipFile(path) as z: entries={i.filename:(i,z.read(i)) for i in z.infolist()}
    model=ET.fromstring(entries['3D/3dmodel.model'][1]);config=ET.fromstring(entries['Metadata/model_settings.config'][1])
    resources=model.find('m:resources',NS);build=model.find('m:build',NS)
    assert not any(values(o).get('name')==part_name for o in config.findall('object')), 'Already packed'
    mid=max(int(o.get('id')) for o in resources)+1;oid=mid+1
    points,faces,size=load_mesh(FOLDER/f'{part_name}.stl')
    obj=ET.SubElement(resources,f'{{{CORE}}}object',id=str(mid),type='model',name=part_name)
    mesh=ET.SubElement(obj,f'{{{CORE}}}mesh');vv=ET.SubElement(mesh,f'{{{CORE}}}vertices');tt=ET.SubElement(mesh,f'{{{CORE}}}triangles')
    for p in points: ET.SubElement(vv,f'{{{CORE}}}vertex',**{a:format(p[i],'.9g') for i,a in enumerate('xyz')})
    for face in faces: ET.SubElement(tt,f'{{{CORE}}}triangle',**{f'v{i+1}':str(v) for i,v in enumerate(face)})
    wrapper=ET.SubElement(resources,f'{{{CORE}}}object',id=str(oid),type='model',name=part_name)
    components=ET.SubElement(wrapper,f'{{{CORE}}}components')
    ET.SubElement(components,f'{{{CORE}}}component',objectid=str(mid),transform=IDENTITY+' 0 0 0')
    pid=max(int(values(p)['plater_id']) for p in config.findall('plate'))+1
    ox,oy=264*((pid-1)%6),-264*((pid-1)//6)
    ET.SubElement(build,f'{{{CORE}}}item',objectid=str(oid),transform=IDENTITY+f' {ox+110} {oy+110} 0',printable='1')
    cfg=ET.SubElement(config,'object',id=str(oid));meta(cfg,'name',part_name);meta(cfg,'extruder',1)
    # Explicit solid infill for this thin spreader, keeping all prior settings intact.
    meta(cfg,'sparse_infill_density','100%')
    sub=ET.SubElement(cfg,'part',id=str(mid),subtype='normal_part')
    for k,v in [('name',part_name),('matrix','1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1'),('source_file',part_name+'.stl'),('source_object_id',0),('source_volume_id',0)]:meta(sub,k,v)
    plate=ET.SubElement(config,'plate')
    for k,v in [('plater_id',pid),('plater_name',f'{pid:02d} - PC - {label}'),('locked','false')]:meta(plate,k,v)
    inst=ET.SubElement(plate,'model_instance')
    for k,v in [('object_id',oid),('instance_id',0),('identify_id',oid)]:meta(inst,k,v)
    changed={'3D/3dmodel.model':ET.tostring(model,encoding='utf-8',xml_declaration=True),'Metadata/model_settings.config':ET.tostring(config,encoding='utf-8',xml_declaration=True)}
    tmp=path.with_suffix('.tmp')
    with zipfile.ZipFile(tmp,'w') as z:
        for n,(info,data) in entries.items():z.writestr(info,changed.get(n,data))
    with zipfile.ZipFile(tmp) as z:
        assert z.testzip() is None
        for n,(_,data) in entries.items():
            if n not in changed:assert z.read(n)==data,n
        current=ET.fromstring(z.read('Metadata/model_settings.config'))
        for tag in ('object','plate'):
            old=ET.fromstring(entries['Metadata/model_settings.config'][1]).findall(tag)
            assert all(ET.tostring(a)==ET.tostring(b) for a,b in zip(old,current.findall(tag)))
    tmp.replace(path)
    shutil.copy2(path,FOLDER/'incubadora_v59_CrealityPrint_7.2.1.3mf')
    return dict(bandeja=pid,preenchimento='100%',configuracoes_anteriores_preservadas=True)

if __name__=='__main__':
    report=export();report.update(pack())
    (FOLDER/'rear_insert_report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(report,indent=2))
