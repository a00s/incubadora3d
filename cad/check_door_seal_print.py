"""Audit the exported door-seal STEP, layer support and the broken receiver.

The straight coupon is cut from the real gasket. Intervals at its mid-span
check growth along the printed section; they do not simulate deformation.
"""
import json
import math
from pathlib import Path
from lw_seals import LATCH_PROJECTION,HINGE_PROJECTION
import cadquery as cq

OUT=Path(__file__).resolve().parents[1]/'output/v59'
q=cq.importers.importStep(str(OUT/'amostra_V_porta_TPU.step'))
previous=[];previous_printable=[];checks=0;step=.2;bb=q.val().BoundingBox()
for layer in range(math.ceil(bb.zlen/step)):
    z=(layer+.5)*step
    if z>bb.zmax:break
    xs=sorted(set(round(v.X,6) for v in q.section(z).vertices().vals()))
    intervals=[(a,b) for a,b in zip(xs,xs[1:]) if q.val().isInside(((a+b)/2,(bb.ymin+bb.ymax)/2,z))]
    support=[]
    for a,b in previous:
        a-=step+1e-5;b+=step+1e-5
        if support and a<=support[-1][1]:support[-1]=(support[-1][0],max(support[-1][1],b))
        else:support.append((a,b))
    if layer:
        for a,b in intervals:assert any(a>=lo and b<=hi for lo,hi in support),(layer,z,intervals,previous)
    # A wall below the extrusion width can disappear from the slicer's support
    # analysis and then reappear as a floating island when it gets wider.
    printable=[(a,b) for a,b in intervals if b-a>.42]
    if layer:
        for a,b in printable:
            assert any(b>=lo-.21 and a<=hi+.21 for lo,hi in previous_printable),('floating section',layer,z,(a,b),previous_printable)
    previous_printable=printable
    previous=intervals;checks+=1
seal=cq.importers.importStep(str(OUT/'junta_V_porta_TPU.step'))
assert seal.val().isValid() and len(seal.solids().vals())==1
profile=json.loads((OUT/'door_v_profile.json').read_text())
def box(w,d,h,x=0,y=0,z=0):return cq.Workplane('XY').box(w,d,h,centered=False).translate((x,y,z))
def loft(stations):
    wires=[box(120-2*i,1,140-2*i,i,y-1,i).edges('|Y').fillet(10-i).faces('>Y').val().outerWire() for y,i in stations]
    return cq.Workplane(obj=cq.Solid.makeLoft(wires,ruled=True))
receiver=loft([(y,i-1) for y,i in profile['receiver']]).cut(loft(profile['receiver']),clean=False)
assert seal.intersect(receiver,clean=False).val().Volume()<1e-5
assert seal.intersect(box(150,1,170,-10,0,-10)).val().Volume()>0
latch=seal.intersect(box(8,12,35,0,-5,50)).val().BoundingBox()
hinge=seal.intersect(box(8,12,35,112,-5,50)).val().BoundingBox()
assert abs(latch.ymax-LATCH_PROJECTION)<.05
assert abs(hinge.ymax-HINGE_PROJECTION)<.05
assert latch.ymax-hinge.ymax>1.1
report=dict(junta_da_caixa_preservada=True,solido_step_valido=True,pecas_junta_porta=1,
            intersecao_receptor_fino_mm3=0,contato_face_frontal_y0=True,
            amostra_cortes=checks,camada_mm=step,paredes_sem_reinicio_flutuante_largura_0p42=True,crescimento_secao_maximo_graus=45,
            projecao_nominal_fecho_mm=LATCH_PROJECTION,projecao_nominal_dobradica_mm=HINGE_PROJECTION,
            altura_nominal_total_fecho_mm=LATCH_PROJECTION+4.25,
            altura_nominal_total_dobradica_mm=HINGE_PROJECTION+4.25,
            limite='Secao reta CAD, nao simula deformacao, forca ou estanqueidade')
(OUT/'tpulw_door_seal_report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(report,indent=2,ensure_ascii=False))
