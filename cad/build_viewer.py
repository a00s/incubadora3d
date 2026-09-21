import base64
import gzip
import json
from pathlib import Path
p=Path(__file__).resolve().parents[1]
folder=p/'output/v32'
# Compact display mesh only; CAD/STL export precision is unchanged.
preview=json.loads((folder/'mesh.json').read_text())
# Adjustable sections are computed in the viewer; omit obsolete fixed-cut meshes.
preview=[part for part in preview if not part['kind'].startswith('section_')]
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
# Integral helical receivers add mesh detail; keep a bounded standalone payload.
assert out.stat().st_size<1_500_000
print(out,out.stat().st_size)
# Generate the standalone page from the same fragment, so CAD and HTML stay in sync.
standalone='''<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Incubadora 3D — v0.32</title>
<style>
:root{color-scheme:light dark;font-family:system-ui,sans-serif}body{margin:0;padding:20px;background:light-dark(#f6f8fa,#182027);color:light-dark(#243542,#e3edf3)}
#incubator-view{max-width:1500px;margin:auto}.viz-controls{display:flex;flex-wrap:wrap;gap:14px;align-items:center;padding:14px;border:1px solid #8294a655;border-radius:10px}
.form-label,.form-check{display:inline-flex;align-items:center;gap:7px}.form-range{max-width:150px}.form-select,button{font:inherit;padding:5px 9px;border:1px solid #8294a677;border-radius:5px;background:light-dark(#fff,#283742);color:inherit;cursor:pointer}
input{accent-color:#328eab}details{margin:14px 0}summary{cursor:pointer;font-weight:600;margin:8px 0}.viz-row{display:flex;justify-content:space-between;align-items:center;gap:8px;margin:6px 0}.text-small{font-size:13px;line-height:1.6;margin-top:10px}#inc-status{font-weight:600}
</style></head><body>'''+s+'</body></html>'
(p/'output/visualizador.html').write_text(standalone)
print(p/'output/visualizador.html',len(standalone.encode()))
