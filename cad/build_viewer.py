import base64
import gzip
import json
from pathlib import Path
p=Path(__file__).resolve().parents[1]
folder=p/'output/v26'
# Compact display mesh only; CAD/STL export precision is unchanged.
preview=json.loads((folder/'mesh.json').read_text())
for part in preview:
    unique={}; vertices=[]; mapping=[]
    for vertex in part['vertices']:
        key=tuple(round(v*10) for v in vertex)
        if key not in unique:
            unique[key]=len(vertices);vertices.append(key)
        mapping.append(unique[key])
    previous=(0,0,0)
    deltas=[]
    for vertex in vertices:
        deltas.append([vertex[a]-previous[a] for a in range(3)])
        previous=vertex
    part['vertices']=deltas
    part['faces']=[f for face in part['faces'] if len(set(f:=[mapping[i] for i in face]))==3]
mesh=base64.b64encode(gzip.compress(json.dumps(preview,separators=(',',':')).encode())).decode()
profile=json.loads((folder/'seal_profile.json').read_text())
def polygon(stations):
    pts=[(240+half*30,140+y*30) for y,half in stations]+[(240-half*30,140+y*30) for y,half in reversed(stations)]
    return ' '.join(f'{x:.1f},{y:.1f}' for x,y in pts)
# This explanatory section uses the exact channel and gasket station coordinates.
svg=f'''<svg viewBox="0 0 480 300" style="width:100%;max-width:600px" role="img" aria-label="Corte da junta: lábio de vedação para fora, pé alargado preso sob a garganta chanfrada do canal.">
<title>Junta TPU pressionada no canal, sem cola</title>
<defs><mask id="seal-cut"><rect width="480" height="300" fill="white"/><polygon points="{polygon(profile['groove'])}" fill="black"/></mask></defs>
<rect x="135" y="140" width="210" height="118" fill="var(--muted)" stroke="currentColor" mask="url(#seal-cut)"/>
<polygon points="{polygon(profile['foot'])}" fill="var(--green)" stroke="currentColor"/>
<polygon points="{polygon(profile['lip'])}" fill="var(--green)" stroke="currentColor"/>
<g fill="currentColor" font-size="18" font-family="sans-serif">
<text x="240" y="30" text-anchor="middle">Corte ampliado · medidas provisórias</text>
<text x="240" y="75" text-anchor="middle">Lábio de vedação</text>
<text x="8" y="127">Chanfro</text><text x="8" y="149">de entrada</text>
<text x="365" y="199">Pé</text><text x="365" y="221">retido</text>
<text x="240" y="286" text-anchor="middle">Garganta 2,4 mm · pé TPU 3,5 mm</text>
</g><g stroke="currentColor" fill="none"><path d="M240 79V94M100 136L194 146M357 203L295 204"/></g>
</svg>'''
s=(p/'cad/viewer-template.html').read_text().replace('__MESH_GZIP__',mesh).replace('__SEAL_SECTION__',svg)
out=p/'output/incubadora-3d.html';out.write_text(s)
assert out.stat().st_size<1_000_000
print(out,out.stat().st_size)
