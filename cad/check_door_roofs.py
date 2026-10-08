"""Audit actual STL cavity ceilings for the door's upright (+Z) build direction."""
import json
import math
from pathlib import Path
import struct

ROOT=Path(__file__).resolve().parents[1]
raw=(ROOT/'output/v59/porta_articulada.stl').read_bytes()
slopes=[]
bridges=[]
for record in struct.iter_unpack('<12fH',raw[84:]):
    p=[record[i:i+3] for i in (3,6,9)]
    center=[sum(v[a] for v in p)/3 for a in range(3)]
    if not (10<=center[0]<=110 and -14.0001<=center[1]<=-7.9999 and 1.9<center[2]<138.1):continue
    # Rounded perimeter corners have curved surfaces; audit the regular cell field.
    if (center[0]<10 or center[0]>110) and (center[2]<10 or center[2]>130):continue
    if not all(-14.0001<=v[1]<=-7.9999 for v in p):continue
    u=[p[1][a]-p[0][a] for a in range(3)];v=[p[2][a]-p[0][a] for a in range(3)]
    n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
    length=math.sqrt(sum(a*a for a in n))
    if length<.001:continue
    n=[a/length for a in n]
    if n[2]>=-.01:continue
    if n[2]<-.999:
        width=max(v[0] for v in p)-min(v[0] for v in p)
        assert width<=2.401, width
        bridges.append(width)
    else:
        assert abs(n[2])<=1/math.sqrt(2)+1e-4,(n,p,length/2)
        slopes.append(math.degrees(math.asin(abs(n[2]))))
assert len(slopes)>100 and bridges
report=dict(orientacao='Porta em pe, borda inferior Z=-4 na mesa',crescimento='+Z',
            triangulos_de_rampa_conferidos=len(slopes),angulo_maximo_rampas_graus=max(slopes),
            triangulos_de_ponte_conferidos=len(bridges),maior_largura_de_ponte_mm=max(bridges),
            nota='Campo central das celulas (X=10 a 110); perimetro curvo e raizes da pega excluidos. Ultima fileira curta conserva pontes de ate 2,4 mm. Sem ensaio de impressao.')
(ROOT/'output/v59/door_roof_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
