"""Check the geometry, plate references and printer bounds of our 3MF project.
This does not substitute for opening the project in the user's Creality Print.
"""
import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--version',default='v59');args=parser.parse_args()
folder=ROOT/'output'/args.version
manifest=json.loads((folder/'bandejas_creality.json').read_text())
path=folder/manifest['arquivo'];ns={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
with zipfile.ZipFile(path) as archive:
    assert archive.testzip() is None
    model=ET.fromstring(archive.read('3D/3dmodel.model'))
    config=ET.fromstring(archive.read('Metadata/model_settings.config'))
    settings=json.loads(archive.read('Metadata/project_settings.config'))
    assert not any(n.endswith('.gcode') for n in archive.namelist())
assert model.attrib['unit']=='millimeter'
assert settings['printer_model']=='Creality K1C'
assert settings['filament_type']==['PC','TPU']
assert settings['filament_settings_id']==[
    'Generic PC @Creality K1C 0.4 nozzle', 'Generic TPU @Creality K1C 0.4 nozzle']
assert not manifest['configuracoes_filamento_personalizadas']
assert not any('temperature' in key or key.endswith('_temp') or key.endswith('_temp_initial_layer')
               or 'speed' in key or 'fan' in key or 'flow' in key for key in settings)
assert next(r for r in manifest['bandejas'] if r['arquivo']=='junta_porta.stl')['material']=='TPU'
objects={int(o.attrib['id']):o for o in model.find('m:resources',ns)}
build=list(model.find('m:build',ns));plates=config.findall('plate')
records=manifest['bandejas']+manifest.get('pecas_adicionais',[])
assert len(build)==len(records)
assert len(plates)==len(manifest['bandejas'])
assert len(plates)<=36
seen=set()
plate_bounds={}
for record in records:
    plate=next(p for p in plates if any(m.get('key')=='plater_id' and int(m.get('value'))==record['bandeja'] for m in p.findall('metadata')))
    item=next(i for i in build if int(i.get('objectid'))==record['objeto_id'])
    def values(node):return {n.attrib['key']:n.attrib['value'] for n in node.findall('metadata')}
    pm=values(plate);im=next(values(i) for i in plate.findall('model_instance') if int(values(i)['object_id'])==record['objeto_id'])
    objid=int(im['object_id']);assert objid not in seen;seen.add(objid)
    assert objid==record['objeto_id']==int(item.attrib['objectid'])
    assert int(pm['plater_id'])==record['bandeja']
    if 'nome' in record:assert pm['plater_name']==record['nome']
    assert im['instance_id']=='0'
    component=objects[objid].find('m:components/m:component',ns)
    meshid=int(component.attrib['objectid']);assert meshid==record['malha_id']
    mesh=objects[meshid].find('m:mesh',ns)
    vertices=[tuple(float(v.attrib[a]) for a in 'xyz') for v in mesh.find('m:vertices',ns)]
    faces=[tuple(int(t.attrib[f'v{a}']) for a in [1,2,3]) for t in mesh.find('m:triangles',ns)]
    assert len(vertices)==record['vertices'] and len(faces)==record['triangulos']
    assert all(len(set(f))==3 and min(f)>=0 and max(f)<len(vertices) for f in faces)
    low=[min(p[a] for p in vertices) for a in range(3)]
    high=[max(p[a] for p in vertices) for a in range(3)]
    assert abs(low[2])<1e-6
    assert all(abs(high[a]-low[a]-record['dimensoes_mm'][a])<.001 for a in range(3))
    transform=[float(n) for n in item.attrib['transform'].split()]
    assert transform[:9]==[1,0,0,0,1,0,0,0,1], 'Scaling/rotation in instance unexpectedly added'
    ox,oy,_=record['origem_mm'];dx,dy,dz=transform[9:]
    cx,cy,cz=record.get('centro_local_mm',[110,110,0])
    assert dx==ox+cx and dy==oy+cy and dz==cz
    assert 5<=low[0]+dx-ox and high[0]+dx-ox<=215
    assert 5<=low[1]+dy-oy and high[1]+dy-oy<=215 and high[2]<=250
    plate_bounds.setdefault(record['bandeja'],[]).append(([low[a]+transform[9+a] for a in range(3)],[high[a]+transform[9+a] for a in range(3)]))
    om=values(config.find(f"object[@id='{objid}']"))
    assert set(om)=={'name','extruder'}, 'Unexpected per-object process override'
    assert int(om['extruder'])==(2 if record['material']=='TPU' else 1)
for bounds in plate_bounds.values():
    for i,(lo,hi) in enumerate(bounds):
        for other_lo,other_hi in bounds[i+1:]:
            assert any(hi[a]+5<=other_lo[a] or other_hi[a]+5<=lo[a] for a in (0,1)), 'Pieces on a shared plate need at least 5 mm separation'
report=dict(espaco_entre_pecas_minimo_mm=5,arquivo=path.name,zip_valid=True,xml_valid=True,bandejas=len(plates),
            pecas=len(records),uma_peca_por_bandeja=len(records)==len(plates),escala_1para1=True,malhas_e_indices_validos=True,
            cabe_k1c_com_margem_5mm=True,gcode_incluido=False,configuracoes_filamento_personalizadas=False,
            verificacao='Estrutura e geometria; leitura e renderizacao no Creality Print dependem do teste nativo separado')
(folder/'projeto_creality_verificacao.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
print(json.dumps(report,indent=2,ensure_ascii=False))
