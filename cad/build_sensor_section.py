"""Draw a radial section of the exported CO2 bushing, including its real voids."""
from pathlib import Path
import cadquery as cq
from OCP.BRepTools import BRepTools_WireExplorer
OUT=Path(__file__).resolve().parents[1]/'output/v59'
q=cq.importers.importStep(str(OUT/'bucha_sensor_TPU.step')).rotate((0,0,0),(1,0,0),180).translate((0,0,8.5))
cut=cq.Workplane('XZ').newObject([q.val()]).section(0)
def xy(r,z):return (80+(r-7)*45,60+(8.5-z)*45)
paths=[]
for wire in cut.wires().vals():
    if wire.BoundingBox().xmin<0:continue
    walk=BRepTools_WireExplorer(wire.wrapped);points=[]
    while walk.More():
        v=cq.Vertex(walk.CurrentVertex());points.append(xy(v.X,v.Z));walk.Next()
    paths.append('M'+' L'.join(f'{x:.2f},{y:.2f}' for x,y in points)+' Z')
assert len(paths)>=2,'Section must expose a closed hollow chamber'
def polygon(points):return ' '.join(f'{x:.2f},{y:.2f}' for x,y in (xy(r,z) for r,z in points))
sensor=polygon([(7,-.5),(7.785,-.5),(7.785,5.32),(8.3,5.32),(8.3,8.5),(7,8.5)])
svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 565" width="600" height="565" style="width:100%;max-width:650px;height:auto" role="img" aria-label="Corte da bucha CO2 com bulbo inferior oco e labios preservados">
<title>Bucha CO₂ · seção radial real do STEP</title>
<rect width="600" height="565" fill="white"/>
<g font-family="sans-serif" font-size="16" fill="#172b35">
<text x="300" y="25" text-anchor="middle">Sensor CO₂ · bulbo inferior oco + lábios</text>
<polygon points="{sensor}" fill="#aab4bd" opacity=".6"/>
<path d="{' '.join(paths)}" fill="#45ae89" fill-rule="evenodd" stroke="#173c32"/>
<text x="335" y="90">Apoio superior preservado</text>
<text x="335" y="120">Anel Ø16,60 × 3,18 mm</text>
<text x="335" y="245">Tubo Ø15,57 mm</text>
<text x="335" y="275">Bulbo livre Ø15,00 mm</text>
<text x="335" y="305">Pele nominal 0,55 mm</text>
<text x="300" y="505" text-anchor="middle">Verde: TPU-LW livre · cinza: sensor medido</text>
<text x="300" y="535" text-anchor="middle">Sobreposição indica compressão; deformação por testar</text>
</g></svg>'''
(OUT/'corte_bucha_CO2_TPU_LW.svg').write_text(svg)
print('Sensor section SVG:',len(paths),'contours')
