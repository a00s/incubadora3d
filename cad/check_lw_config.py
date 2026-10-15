"""Guard the GUI failure caused by a scalar per-object small_perimeter_speed.

Keep the user's full-project process unchanged. The dedicated print project
uses an absolute numeric speed vector and inherits it in every object.
"""
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

ROOT=Path(__file__).resolve().parents[1]
from pack_lw_seals import TPU_NAMES
NAMES=set(TPU_NAMES)
for path in (ROOT/'output/incubadora_CrealityPrint_7.2.1.3mf',
             ROOT/'output/v59/incubadora_v59_CrealityPrint_7.2.1.3mf',
             ROOT/'output/v59/vedacoes_eSUN_TPU_LW.3mf'):
    dedicated=path.name=='vedacoes_eSUN_TPU_LW.3mf'
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        config=ET.fromstring(z.read('Metadata/model_settings.config'))
        count=0
        for obj in config.findall('object'):
            name=next(m.get('value') for m in obj.findall('metadata') if m.get('key')=='name')
            if dedicated or name in NAMES:
                assert not any(m.get('key')=='small_perimeter_speed' for m in obj.iter('metadata')),name
                if name.startswith(('TPU_passagem_sensor','TPU_passagem_aquecedor')):
                    settings={m.get('key'):m.get('value') for m in obj.findall('metadata')}
                    assert settings['sparse_infill_density']=='30%'
                    assert settings['sparse_infill_pattern']=='gyroid'
                    assert settings['wall_loops']=='3'
                    assert settings['top_shell_layers']==settings['bottom_shell_layers']=='4'
                count+=1
        if not dedicated:
            assert not any(m.get('key')=='extruder' and m.get('value')=='2' for o in config.findall('object') for m in o.iter('metadata')),'Legacy TPU still assigned'
        assert count==(12 if dedicated else 10),(path.name,count)
        assert all(next((m.get('value') for m in o.findall('metadata') if m.get('key')=='extruder'),None)==('1' if dedicated else '4') for o in config.findall('object') if dedicated or next((m.get('value') for m in o.findall('metadata') if m.get('key')=='name'),None) in NAMES)
        process=json.loads(z.read('Metadata/project_settings.config'))
        assert isinstance(process['small_perimeter_speed'],list)
        if dedicated:
            assert process['small_perimeter_speed']==['25']
            assert float(process['small_perimeter_speed'][0])==25
    print(path.name,': configuracao verificada;',count,'objetos sem sobrescrita escalar')
