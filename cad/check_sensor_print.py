"""Audit axisymmetric bushing sections for 45-degree support-free growth."""
import cadquery as cq
from sensor_grommet import build_sensor_grommet,sensor_grommet_print
q=sensor_grommet_print(build_sensor_grommet(center=(0,0,0)))
q=cq.Workplane('XY').newObject([q.val()])
step=.2;previous=[];checks=0
for layer in range(45):
 z=(layer+.5)*step
 radii=sorted(set(round(e.radius(),6) for e in q.section(z).edges().vals() if e.geomType()=='CIRCLE'))
 occupied=[(a,b) for a,b in zip(radii,radii[1:]) if q.val().isInside(((a+b)/2,0,z))]
 if layer:
  support=[]
  for a,b in previous:
   a-=step+1e-5;b+=step+1e-5
   if support and a<=support[-1][1]:support[-1]=(support[-1][0],max(support[-1][1],b))
   else:support.append((a,b))
  for a,b in occupied:assert any(a>=lo and b<=hi for lo,hi in support),(layer,z,occupied,previous)
 previous=occupied;checks+=1
print('Passed:',checks,'CAD sections at 0.2 mm; radial growth <=45 degrees; no lip starts suspended')

if __name__=='__main__':
    import json
    from pathlib import Path
    path=Path(__file__).resolve().parents[1]/'output/v59/sensor_grommet_report.json'
    report=json.loads(path.read_text())
    report['verificacao_crescimento_camadas']=dict(cortes=checks,altura_camada_mm=step,angulo_maximo_graus=45,labios_sem_inicio_suspenso=True)
    path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
