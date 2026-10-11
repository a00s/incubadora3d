"""Removable, smooth front spreader for an already printed stainless liner."""
import json
from pathlib import Path
import cadquery as cq
from forming_tools import box
from rear_insert import pack
ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'output/v59'
NAME='moldura_frontal_inox_removivel'


def export():
    # Ends ahead of the rack (Y8), behind the closed door tip (Y3).
    outer=box(110.1,4,130.1,4.95,3.6,4.95).edges('|Y').fillet(5.05)
    aperture=box(104.5,6,124.5,7.75,2.6,7.75).edges('|Y').fillet(2.25)
    frame=outer.cut(aperture)
    # Rounded front/rear edges, no blind recesses or retention grooves.
    frame=frame.edges('not |Y').fillet(.6)
    assert frame.val().isValid() and len(frame.solids().vals())==1
    liner=cq.importers.importStep(str(FOLDER/'revestimento_inox_referencia.step'))
    assert frame.intersect(liner).val().Volume()<1e-5
    meshes=json.loads((FOLDER/'mesh.json').read_text())
    checked=[]
    for mesh in meshes:
        if mesh['kind'] in ('rack','tray') or mesh['name']=='reservatorio_agua':
            v=mesh['vertices'];lo=[min(p[a] for p in v) for a in range(3)];hi=[max(p[a] for p in v) for a in range(3)]
            obstacle=box(*(hi[a]-lo[a] for a in range(3)),*lo)
            if mesh['kind']=='tray':
                # Continuous extraction envelope, including pull bar and rounded tray.
                obstacle=box(hi[0]-lo[0],hi[1]+150,hi[2]-lo[2],lo[0],-150,lo[2])
            assert frame.intersect(obstacle).val().Volume()<1e-5,mesh['name']
            checked.append(mesh['name'])
    # A conservative enclosing slab of the complete door, rotated about its hinge.
    door=next(m for m in meshes if m['name']=='porta_articulada')
    v=door['vertices'];lo=[min(p[a] for p in v) for a in range(3)];hi=[max(p[a] for p in v) for a in range(3)]
    slab=box(*(hi[a]-lo[a] for a in range(3)),*lo)
    angles=[0,.1,.25,.5,1,2,3,5,7,10,12,15,18,20,25,30,45,60,75,90,110]
    for angle in angles:
        assert frame.intersect(slab.rotate((130,-6,0),(130,-6,1),angle)).val().Volume()<1e-5,angle
    # Insertion at open door angle: swept full outer cross section.
    sweep=box(110.1,157.6,130.1,4.95,-150,4.95).edges('|Y').fillet(5.05)
    assert sweep.intersect(slab.rotate((130,-6,0),(130,-6,1),110)).val().Volume()<1e-5
    cq.exporters.export(frame,str(FOLDER/f'{NAME}.step'))
    flat=frame.rotate((0,0,0),(1,0,0),90)
    bb=flat.val().BoundingBox();flat=flat.translate((-bb.xmin,-bb.ymin,-bb.zmin))
    bb=flat.val().BoundingBox();dims=[bb.xlen,bb.ylen,bb.zlen]
    assert dims[0]+10<220 and dims[1]+10<220 and abs(dims[2]-4)<.001
    cq.exporters.export(flat,str(FOLDER/f'{NAME}.stl'))
    vv,ff=frame.val().tessellate(.15,.2)
    (FOLDER/'front_frame_mesh.json').write_text(json.dumps([dict(name=NAME,kind='front_frame',color='#b8cf7d',vertices=[[p.x,p.y,p.z] for p in vv],faces=ff)],separators=(',',':')))
    return dict(dimensoes_mm=[110.1,130.1,4],abertura_mm=[104.5,124.5],largura_aro_mm=2.8,arredondamento_bordas_mm=.6,folga_inox_por_borda_mm=.15,posicao_y_mm=[3.6,7.6],folga_porta_fechada_mm=.6,folga_suporte_gavetas_mm=.4,pecas_conferidas=checked,extracao_gavetas_continua_conferida=True,angulos_porta_conferidos=angles,insercao_retirada_com_porta_110=True,sem_interferencia_inox=True,solido_valido=True,limites_k1c=True,limpeza='Remover a mao; sem cola, parafusos, canais ou furos cegos; bordas arredondadas',encaixe_e_retirada_fisicos_pendentes=True)

if __name__=='__main__':
    report=export();report.update(pack(NAME,'Moldura frontal inox removivel'))
    (FOLDER/'front_frame_report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(report,indent=2,ensure_ascii=False))
