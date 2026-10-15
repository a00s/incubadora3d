"""Assembly guide drawn from transverse sections of the exported cradle/cap STEP files."""
from pathlib import Path
import math
import sys
from wire_plugs import SPECS, RADIAL_INTERFERENCE
NAME=sys.argv[1] if len(sys.argv)>1 else "sensor"
DIAMETER,POSITIONS=SPECS[NAME]
PITCH=POSITIONS[1]-POSITIONS[0]
CHANNEL=DIAMETER-2*RADIAL_INTERFERENCE[NAME]
import cadquery as cq
from OCP.BRepTools import BRepTools_WireExplorer
OUT=Path(__file__).resolve().parents[1]/'output/v59'

def section_paths(label,cx):
    q=cq.importers.importStep(str(OUT/f'TPU_passagem_{NAME}_metade_{label}.step'))
    q=q.rotate((0,0,0),(1,0,0),180).translate((0,0,15.5))
    cut=cq.Workplane('XY').newObject([q.val()]).section(7)
    paths=[]
    for wire in cut.wires().vals():
        walk=BRepTools_WireExplorer(wire.wrapped);points=[]
        while walk.More():
            edge=cq.Edge(walk.Current());vertex=cq.Vertex(walk.CurrentVertex())
            start=edge.positionAt(0);end=edge.positionAt(1)
            reverse=math.dist(vertex.toTuple(),end.toTuple())<math.dist(vertex.toTuple(),start.toTuple())
            samples=16 if edge.geomType()=='CIRCLE' else 1
            for i in range(samples):
                t=i/samples;t=1-t if reverse else t;p=edge.positionAt(t)
                points.append((cx+p.x*18,220-p.y*18))
            walk.Next()
        paths.append('M'+' L'.join(f'{x:.2f},{y:.2f}' for x,y in points)+' Z')
    return ' '.join(paths)

a=section_paths('A',140);closed_a=section_paths('A',540);b=section_paths('B',540)
wire_marks=''.join(f'<circle cx="{cx}" cy="{220-y*18:.1f}" r="{DIAMETER*9:.2f}" fill="#aeb7bf" fill-opacity=".8" stroke="#4b5964"/>' for cx in (140,540) for y in POSITIONS)
arrows=''.join(f'<path d="M245,{220-y*18:.1f} H164" stroke="#425c6b" stroke-width="2" marker-end="url(#wire-arrow)"/>' for y in POSITIONS)
svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 740 450" width="740" height="450" style="width:100%;max-width:800px;height:auto" role="img" aria-label="Berço A com {len(POSITIONS)} labios de retencao e tampa B que comprime cada fio">
<title>Rolha {NAME} · {len(POSITIONS)} fios · berço A + tampa B</title>
<rect width="740" height="450" fill="white"/>
<defs><marker id="wire-arrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="#425c6b"/></marker></defs>
<g font-family="sans-serif" font-size="17" fill="#17313f" text-anchor="middle">
<text x="160" y="35">A · berço de encaixe</text><text x="540" y="35">A + B · tampa fechada</text>
<text x="160" y="65" font-size="15">Um fio por alojamento</text><text x="540" y="65" font-size="15">Apoios individuais de compressão</text>
<circle cx="140" cy="220" r="110.16" fill="none" stroke="#c8d3db" stroke-dasharray="4 4"/>
<path d="{a}" fill="#45ae89" fill-rule="evenodd" stroke="#173c32"/>
<path d="{closed_a}" fill="#45ae89" fill-rule="evenodd" stroke="#173c32"/>
<path d="{b}" fill="#82afd0" fill-rule="evenodd" stroke="#385b75"/>
{wire_marks}{arrows}
<text x="370" y="365">Verde: berço A · azul: tampa B · cinza: fios Ø{DIAMETER:.2f} mm</text>
<text x="370" y="395">Centros a {PITCH:.2f} mm · canais livres Ø{CHANNEL:.2f} mm · preenchimento 30%</text>
<text x="370" y="425" font-size="15">Seção real dos STEP, sem deformação · montagem e vedação por testar</text>
</g></svg>'''
(OUT/f'corte_rolha_{NAME}_berco_tampa.svg').write_text(svg)
print('Cradle/cap section generated from STEP')
