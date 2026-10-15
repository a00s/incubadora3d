"""Check actual Creality-generated paths, not just the saved profile values.

Usage: python cad/check_lw_print.py /tmp
Expects tpulw-slice-N/plate_N.gcode for the six print-only plates.
"""
import json
import re
import sys
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
from pack_forming_tools import NS, values

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/v59'
folder=Path(sys.argv[1])
records=[]
with zipfile.ZipFile(OUT/'vedacoes_eSUN_TPU_LW.3mf') as z:
    assert z.testzip() is None
    model=ET.fromstring(z.read('3D/3dmodel.model'))
    config=ET.fromstring(z.read('Metadata/model_settings.config'))
    assert len(config.findall('plate'))==6
    objects={o.get('id'):o for o in model.find('m:resources',NS)}
    items={i.get('objectid'):i for i in model.find('m:build',NS)}
    for plate in config.findall('plate'):
        pid=int(values(plate)['plater_id'])
        instances=plate.findall('model_instance');assert len(instances)==1
        oid=values(instances[0])['object_id'];wrapper=objects[oid]
        component=wrapper.find('m:components/m:component',NS);mesh=objects[component.get('objectid')].find('m:mesh',NS)
        vertices=[tuple(float(v.get(a)) for a in 'xyz') for v in mesh.find('m:vertices',NS)]
        t=[float(v) for v in items[oid].get('transform').split()];assert t[:9]==[1,0,0,0,1,0,0,0,1]
        ox,oy=264*((pid-1)%3),-264*((pid-1)//3)
        lo=[min(v[a]+t[9+a] for v in vertices) for a in range(3)]
        hi=[max(v[a]+t[9+a] for v in vertices) for a in range(3)]
        assert lo[0]>=ox+5 and hi[0]<=ox+215 and lo[1]>=oy+5 and hi[1]<=oy+215 and abs(lo[2])<1e-5 and hi[2]<=250
        path=folder/f'tpulw-slice-{pid}'/f'plate_{pid}.gcode'
        data=path.read_text();active=False;feed=None;role='';speeds=set();negative=[];layers=0
        for line in data.splitlines():
            if line.startswith(';LAYER_CHANGE'):active=True;layers+=1
            if line.startswith(';TYPE:'):role=line
            if not active:continue
            assert 'support' not in role.lower(),(pid,role)
            cmd=line.split(';')[0].strip()
            if re.match(r'^G(?:10|11)\b',cmd):raise AssertionError((pid,'firmware retraction'))
            if not re.match(r'^G[123]\b',cmd):continue
            params={a:float(b) for a,b in re.findall(r'([XYZEF])(-?\d*\.?\d+)',cmd)}
            if 'F' in params:feed=params['F']
            if params.get('E',0)<-1e-6:negative.append(cmd)
            if params.get('E',0)>1e-6 and any(a in params for a in 'XY'):speeds.add(round(feed/60,3))
        assert not negative,(pid,negative[:3])
        assert speeds=={25.0},(pid,speeds)
        assert 'START_PRINT EXTRUDER_TEMP=256 BED_TEMP=50' in data
        assert not re.search(r'^T[1-9]\d*\s*$',data,re.M)
        assert 'M106 S255' in data
        result=json.loads((path.parent/'result.json').read_text());assert result['return_code']==0
        warning=result['sliced_plates'][0]['warning_message']
        assert not warning,(pid,warning)
        log=(folder/f'tpulw-native-{pid}.log').read_text()
        assert 'set no_check to 0' in log,(pid,'support detection bypassed')
        assert 'is_support_necessary takes' in log,(pid,'support detection not run')
        records.append(dict(bandeja=pid,camadas=layers,velocidades_extrusao_mm_s=sorted(speeds),retracoes=0,suportes=False,detector_suportes_ativo=True,aviso_fatiador=warning or None,limites_k1c_com_margem_5mm=True))
report=dict(creality_version='7.2.1.5476',arquivo='vedacoes_eSUN_TPU_LW.3mf',bandejas=records,gcode_apenas_temporario=True,ensaio_fisico_pendente=True)
(OUT/'tpulw_slice_report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(report,indent=2,ensure_ascii=False))
