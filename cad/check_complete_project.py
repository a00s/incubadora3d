"""Validate shared plates and external/inline meshes in the user's full 3MF."""
from collections import Counter
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile
from pack_forming_tools import CORE, PROD, NS, values, load_mesh

ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'output/incubadora_CrealityPrint_7.2.1.3mf'
with zipfile.ZipFile(path) as z:
    assert z.testzip() is None
    model=ET.fromstring(z.read('3D/3dmodel.model'))
    config=ET.fromstring(z.read('Metadata/model_settings.config'))
    objects={o.get('id'):o for o in model.find('m:resources',NS)}
    items={o.get('objectid'):o for o in model.find('m:build',NS)}
    labels={o.get('id'):values(o)['name'] for o in config.findall('object')}
    assert len(items)==len(labels)==38
    assert all(n in labels.values() for n in ('porta_articulada','molde_caixa_inox_referencia','contraforma_inox_inferior','contraforma_inox_superior'))
    seen=set()
    for plate in config.findall('plate'):
        pid=int(values(plate)['plater_id']);ox,oy=264*((pid-1)%6),-264*((pid-1)//6)
        boxes=[]
        for instance in plate.findall('model_instance'):
            oid=values(instance)['object_id'];assert oid not in seen;seen.add(oid)
            component=objects[oid].find('m:components/m:component',NS)
            assert component.get('transform')=='1 0 0 0 1 0 0 0 1 0 0 0'
            target=component.get(f'{{{PROD}}}path')
            owner=ET.fromstring(z.read(target.lstrip('/'))) if target else model
            obj=next(o for o in owner.find('m:resources',NS) if o.get('id')==component.get('objectid'))
            mesh=obj.find('m:mesh',NS)
            vertices=[tuple(float(v.get(a)) for a in 'xyz') for v in mesh.find('m:vertices',NS)]
            faces=[tuple(int(t.get(f'v{i}')) for i in (1,2,3)) for t in mesh.find('m:triangles',NS)]
            assert all(len(set(f))==3 and min(f)>=0 and max(f)<len(vertices) for f in faces)
            edge=Counter(tuple(sorted((a,b))) for f in faces for a,b in zip(f,f[1:]+f[:1]))
            if labels[oid] in ('molde_caixa_inox_referencia','contraforma_inox_inferior','contraforma_inox_superior'):
                assert all(n==2 for n in edge.values()),labels[oid]
            transform=[float(v) for v in items[oid].get('transform').split()]
            assert transform[:9]==[1,0,0,0,1,0,0,0,1]
            if labels[oid]=='porta_articulada':
                expected,_,_=load_mesh(ROOT/'output/v59/porta_articulada.stl',lambda p:(p[0],-p[2],p[1]))
                assert len(expected)==len(vertices)
                assert all(abs(p[a]-(v[a]+(transform[11] if a==2 else 0)))<1e-5 for p,v in zip(expected,vertices) for a in range(3))
                # CAD outer Y=-16 maps to print Z=0; inner Y=3 maps to Z=19.
                assert abs(min(v[2]+transform[11] for v in vertices))<1e-5
                assert abs(max(v[2]+transform[11] for v in vertices)-19)<1e-5
            low=[min(v[a] for v in vertices)+transform[9+a] for a in range(3)]
            high=[max(v[a] for v in vertices)+transform[9+a] for a in range(3)]
            assert 5<=low[0]-ox and high[0]-ox<=215,labels[oid]
            assert 5<=low[1]-oy and high[1]-oy<=215,labels[oid]
            assert abs(low[2])<.001 and high[2]<=250,labels[oid]
            boxes.append((low,high))
        for i,(lo,hi) in enumerate(boxes):
            for other_lo,other_hi in boxes[i+1:]:
                assert any(hi[a]+5<=other_lo[a] or other_hi[a]+5<=lo[a] for a in (0,1))
    assert seen==set(items)
    assert len(config.findall('plate'))==36
report=dict(arquivo=path.name,bandejas=36,pecas=38,zip_xml_validos=True,malhas_ferramental_fechadas=True,
            limites_k1c_com_margem_5mm=True,espaco_minimo_entre_pecas_mm=5,
            contraformas_nas_bandejas=[35,36],molde_na_bandeja=10,porta_face_externa_para_baixo=True,porta_ressalto_v_para_cima=True)
(ROOT/'output/v59/ferramental_inox/projeto_completo_verificacao.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(report,indent=2,ensure_ascii=False))
