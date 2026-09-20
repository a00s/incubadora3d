"""Check exported binary STL envelopes and center each separately on K1C bed.
This is a dimensional check, not slicer validation or automatic orientation.
"""
import json,struct
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'output/v26'
limit=(220,220,250); brim=5
result=[]; destination=p/'k1c_posicionados';destination.mkdir(exist_ok=True)
for path in sorted(p.glob('*.stl')):
    raw=path.read_bytes(); count=struct.unpack_from('<I',raw,80)[0]
    assert len(raw)==84+count*50, f'Unexpected STL format: {path}'
    triangles=list(struct.iter_unpack('<12fH',raw[84:]))
    vertices=[t[i:i+3] for t in triangles for i in (3,6,9)]
    lo=[min(v[a] for v in vertices) for a in range(3)]
    hi=[max(v[a] for v in vertices) for a in range(3)]
    size=[hi[a]-lo[a] for a in range(3)]
    fits=all(size[a]+(2*brim if a<2 else 0)<=limit[a]+1e-4 for a in range(3))
    assert fits, f'{path.name} exceeds build envelope including brim allowance'
    shift=[110-(lo[0]+hi[0])/2,110-(lo[1]+hi[1])/2,-lo[2]]
    out=bytearray(raw[:84])
    for tri in triangles:
        row=list(tri)
        for i in (3,6,9):
            for a in range(3):row[i+a]+=shift[a]
        out.extend(struct.pack('<12fH',*row))
    (destination/path.name).write_bytes(out)
    result.append(dict(peca=path.name,dimensoes_mm=[round(n,2) for n in size],cabe_com_margem_5mm=fits))
report=dict(impressora='Creality K1C',volume_mm=limit,fonte='https://www.creality.com/products/k1c-carbon-3d-printer',margem_por_lado_mm=brim,orientacao='Mantida a orientação do CAD; peças centralizadas individualmente com Z mínimo zero. Suportes e orientação final pendentes.',pecas=result)
(p/'compatibilidade_k1c.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
for row in result:print(row['peca'],row['dimensoes_mm'])
