"""Audit new cavity roofs and the actual door STL for outer-face-down printing."""
import json
import math
from pathlib import Path
import struct
import cadquery as cq
from door_insulation import build_door_insulation

ROOT=Path(__file__).resolve().parents[1]
_,cells,layout=build_door_insulation()
assert len(cells)==30
# build_door_insulation checks all cavity ceiling faces, including curved corners.
raw=(ROOT/'output/v59/porta_articulada.stl').read_bytes()
slopes=[];bridges=[]
for record in struct.iter_unpack('<12fH',raw[84:]):
    p=[record[i:i+3] for i in (3,6,9)]
    center=[sum(v[a] for v in p)/3 for a in range(3)]
    # Check the actual central STL too; perimeter/grip surfaces are not cavity roofs.
    if not (10<=center[0]<=110 and 2<center[2]<138):continue
    if not all(-14.0001<=v[1]<=-7.9999 for v in p):continue
    u=[p[1][a]-p[0][a] for a in range(3)];v=[p[2][a]-p[0][a] for a in range(3)]
    n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
    length=math.sqrt(sum(a*a for a in n))
    if length<.001:continue
    n=[a/length for a in n]
    if n[1]>=-.01:continue
    if n[1]<-.999:
        width=max(v[0] for v in p)-min(v[0] for v in p)
        assert width<=.401,width
        bridges.append(width)
    else:
        assert abs(n[1])<=1/math.sqrt(2)+1e-4,(n,p)
        slopes.append(math.degrees(math.asin(abs(n[1]))))
assert len(slopes)>=100 and bridges
# Confirm taper across the narrow X dimension, not the long Z dimension.
for cell,record in zip(cells,layout):
    x,y,z,dx,dy,dz=record['bounds_mm']
    for offset in (0,.5,1,1.5):
        level=record['roof_start_y']+offset
        plane=cq.Workplane('XZ',origin=(0,level,0)).rect(1000,1000).extrude(.001,both=True).val()
        section=cell.intersect(plane)
        assert section.BoundingBox().xlen<=dx-2*offset+.003
report=dict(orientacao='Frente plana Y=-16 na mesa; ressalto V para cima',crescimento='+Y',
            canais=len(cells),paredes_mm=2,nervura_central_mm=2,
            todas_cavidades_cad_auditadas=True,triangulos_de_rampa_stl_conferidos=len(slopes),
            angulo_maximo_rampas_graus=max(slopes),triangulos_de_ponte_stl_conferidos=len(bridges),
            maior_largura_de_ponte_mm=max(bridges),fechamento_transversal_conferido=True,
            nota='Geometria CAD de todas as cavidades e STL central conferidos; sem ensaio fisico.')
(ROOT/'output/v59/door_roof_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
