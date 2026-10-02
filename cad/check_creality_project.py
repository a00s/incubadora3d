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
assert next(r for r in manifest['bandejas'] if r['arquivo']=='junta_porta.stl')['material']=='TPU'
objects={int(o.attrib['id']):o for o in model.find('m:resources',ns)}
build=list(model.find('m:build',ns));plates=config.findall('plate')
assert len(build)==len(plates)==len(manifest['bandejas'])
assert len(plates)<=36
seen=set()
for record,plate,item in zip(manifest['bandejas'],plates,build):
    def values(node):return {n.attrib['key']:n.attrib['value'] for n in node.findall('metadata')}
    pm=values(plate);im=values(plate.find('model_instance'))
    objid=int(im['object_id']);assert objid not in seen;seen.add(objid)
    assert objid==record['objeto_id']==int(item.attrib['objectid'])
    assert int(pm['plater_id'])==record['bandeja']
    assert pm['plater_name']==record['nome'] and im['instance_id']=='0'
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
    assert dx==ox+110 and dy==oy+110 and dz==0
    assert 5<=low[0]+dx-ox and high[0]+dx-ox<=215
    assert 5<=low[1]+dy-oy and high[1]+dy-oy<=215 and high[2]<=250
    om=values(config.find(f"object[@id='{objid}']"))
    assert int(om['extruder'])==(2 if record['material']=='TPU' else 1)
report=dict(arquivo=path.name,zip_valid=True,xml_valid=True,bandejas=len(plates),
            uma_peca_por_bandeja=True,escala_1para1=True,malhas_e_indices_validos=True,
            cabe_k1c_com_margem_5mm=True,gcode_incluido=False,
            verificacao='Estrutura e geometria; leitura e renderizacao no Creality Print dependem do teste nativo separado')
(folder/'projeto_creality_verificacao.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
print(json.dumps(report,indent=2,ensure_ascii=False))
