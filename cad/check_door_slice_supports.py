import json,re,struct
from pathlib import Path
import argparse
from door_insulation import build_door_insulation
root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description='Check support extrusion midpoints against door cavities in a test G-code.')
parser.add_argument('gcode',type=Path)
args=parser.parse_args()
raw=(root/'output/v59/porta_articulada.stl').read_bytes()
points=[r[i:i+3] for r in struct.iter_unpack('<12fH',raw[84:]) for i in (3,6,9)]
xmid=(min(p[0] for p in points)+max(p[0] for p in points))/2
zmid=(min(p[2] for p in points)+max(p[2] for p in points))/2
ymin=min(p[1] for p in points)
_,cells,layout=build_door_insulation()
position={'X':0.,'Y':0.,'Z':0.};role='';support_segments=0;inside=[]
gcode=args.gcode
for line in gcode.read_text().splitlines():
 if line.startswith(';TYPE:'):role=line[6:]
 if not line.startswith(('G0 ','G1 ')):continue
 codes={k:float(v) for k,v in re.findall(r'([XYZE])\s*([-+]?\d*\.?\d+)',line)}
 nxt={a:codes.get(a,position[a]) for a in position}
 if role.startswith('Support') and codes.get('E',0)>0 and any(abs(nxt[a]-position[a])>.001 for a in 'XY'):
  support_segments+=1
  mid={a:(nxt[a]+position[a])/2 for a in position}
  point=(mid['X']-110+xmid,mid['Z']+ymin,110+zmid-mid['Y'])
  for cell,record in zip(cells,layout):
   x,y,z,dx,dy,dz=record['bounds_mm']
   if x+.05<point[0]<x+dx-.05 and y+.05<point[1]<y+dy-.05 and z+.05<point[2]<z+dz-.05:
    if cell.isInside(point,tolerance=1e-5):inside.append(point)
 position=nxt
assert support_segments>0 and not inside,inside[:5]
r=json.loads((root/'output/v59/door_slice_report.json').read_text())
r.update(altura_fatiada_mm=19,camadas=99,avisos_do_fatiador=[],segmentos_suporte_conferidos=support_segments,segmentos_suporte_nas_cavidades=0,metodo_suportes='Pontos medios de segmentos de extrusao de suporte comparados com as cavidades CAD')
(root/'output/v59/door_slice_report.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
print('Support segments:',support_segments,'inside cavities:',len(inside))
