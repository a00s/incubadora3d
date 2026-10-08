"""Split finishing dies for the 0.3 mm stainless liner; dimensions in mm."""
import json
from pathlib import Path
import cadquery as cq

ROOT = Path(__file__).resolve().parents[1]


def box(w, d, h, x, y, z):
    return cq.Workplane('XY').box(w, d, h, centered=False).translate((x, y, z))


# Positions come from the three actual penetrations in cad/model.py's liner.
HOLES = [dict(nome='entrada_CO2', eixo='X', centro_mm=[4.5, 60, 34], diametro_final_mm=6.2),
         dict(nome='acesso_lateral', eixo='X', centro_mm=[4.5, 90, 127.5], diametro_final_mm=14),
         dict(nome='acesso_traseiro', eixo='Y', centro_mm=[60, 110, 116], diametro_final_mm=14)]
PILOT_DIAMETER = 2.5


def build_tools():
    male = box(110.4, 109.7, 130.4, 4.8, 0, 4.8).edges('|Y').fillet(5.2)
    # Offset the male cross-section by sheet thickness + 0.15 mm fitting clearance.
    # The cavity ends behind the rear sheet, leaving 0.15 mm rear clearance too.
    cavity = box(111.3, 111.15, 131.3, 4.35, -1, 4.35).edges('|Y').fillet(5.65)
    sleeve = box(159.3, 122.15, 179.3, -19.65, 0, -19.65).cut(cavity)
    # External ribs join both side posts to the top/bottom pressing faces.
    # The 12 mm rear diaphragm also braces each half and carries the rear pilot.
    for x in (-31.65, 135.65):
        for y in (8, 47, 86):
            rib = box(16, 18, 179.3, x, y, -19.65).edges('|Z').fillet(3)
            sleeve = sleeve.union(rib)
    for x in (-7.65, 127.65):
        for y in (20, 90):
            sleeve = sleeve.cut(cq.Workplane('XY', origin=(x, y, -20)).circle(3.3).extrude(181))
    for hole in HOLES:
        x, y, z = hole['centro_mm']
        if hole['eixo'] == 'X':
            sleeve = sleeve.cut(cq.Workplane('YZ', origin=(-40, y, z)).circle(PILOT_DIAMETER/2).extrude(45))
            male = male.cut(cq.Workplane('YZ', origin=(4.79, y, z)).circle(PILOT_DIAMETER/2).extrude(3.01))
        else:
            # XZ workplanes extrude toward -Y.
            sleeve = sleeve.cut(cq.Workplane('XZ', origin=(x, 123, z)).circle(PILOT_DIAMETER/2).extrude(13))
            male = male.cut(cq.Workplane('XZ', origin=(x, 109.71, z)).circle(PILOT_DIAMETER/2).extrude(3.01))
    lower = sleeve.intersect(box(190, 125, 89.65, -35, -1, -19.65))
    upper = sleeve.intersect(box(190, 125, 89.65, -35, -1, 70))
    return [('molde_caixa_inox_referencia', male, '#e0ad54', 'forming_male'),
            ('contraforma_inox_inferior', lower, '#668ec7', 'forming_lower'),
            ('contraforma_inox_superior', upper, '#b890cc', 'forming_upper')]


def export_tools(folder):
    folder = Path(folder)
    dest = folder / 'ferramental_inox'
    dest.mkdir(exist_ok=True)
    tools = build_tools()
    for name, obj, _, _ in tools:
        assert obj.val().isValid() and len(obj.solids().vals()) == 1, name
    male, lower, upper = [obj for _, obj, _, _ in tools]
    for a, b in ((male, lower), (male, upper), (lower, upper)):
        assert a.intersect(b).val().Volume() < 1e-5
    liner = cq.importers.importStep(str(folder / 'revestimento_inox_referencia.step'))
    for _, obj, _, _ in tools:
        assert obj.intersect(liner).val().Volume() < 1e-5
    # Opening along Z must clear the tool without an undercut.
    for distance in (0, .1, 1, 10, 40, 80):
        for obj, direction in ((lower, -1), (upper, 1)):
            moved = obj.translate((0, 0, direction * distance))
            assert moved.intersect(male).val().Volume() < 1e-5
            assert moved.intersect(liner).val().Volume() < 1e-5
    # A pilot axis must be clear in both dies; material must remain alongside it.
    for hole in HOLES:
        x, y, z = hole['centro_mm']
        if hole['eixo'] == 'X':
            axis = cq.Workplane('YZ', origin=(-40, y, z)).circle(1).extrude(47.79)
        else:
            axis = cq.Workplane('XZ', origin=(x, 123, z)).circle(1).extrude(16.29)
        for obj in (male, lower if z < 70 else upper):
            assert obj.intersect(axis).val().Volume() < 1e-5, hole['nome']
            assert obj.intersect(axis.translate((0, 0, 2.5))).val().Volume() > .1, hole['nome']
    for distance in (1, 10, 40, 110):
        moved = male.translate((0, -distance, 0))
        assert moved.intersect(lower).val().Volume() < 1e-5
        assert moved.intersect(upper).val().Volume() < 1e-5
    meshes, records = [], []
    for name, obj, color, kind in tools:
        cq.exporters.export(obj, str(dest / f'{name}.step'))
        flat = obj.rotate((0, 0, 0), (1, 0, 0), -90)
        bb = flat.val().BoundingBox()
        flat = flat.translate((-bb.xmin, -bb.ymin, -bb.zmin))
        cq.exporters.export(flat, str(dest / f'{name}.stl'))
        bounds = flat.val().BoundingBox()
        dims = [bounds.xlen, bounds.ylen, bounds.zlen]
        assert dims[0] + 10 <= 220 and dims[1] + 10 <= 220 and dims[2] <= 250
        v, f = obj.val().tessellate(.3, .3)
        meshes.append(dict(name=name, kind=kind, color=color,
                           vertices=[[p.x, p.y, p.z] for p in v], faces=f))
        records.append(dict(nome=name, dimensoes_impressao_mm=dims, solido_valido=True))
    # Keep the historical male exports current, with the same print placement.
    cq.exporters.export(male, str(folder / 'molde_caixa_inox_referencia.step'))
    flat = male.rotate((0, 0, 0), (1, 0, 0), -90).translate((-4.8, -4.8, 109.7))
    cq.exporters.export(flat, str(folder / 'molde_caixa_inox_referencia.stl'))
    (dest / 'mesh.json').write_text(json.dumps(meshes, separators=(',', ':')))
    report = dict(chapa_inox_mm=.3, folga_adicional_por_face_mm=.15,
                  distancia_macho_cavidade_mm=.45, raio_interno_mm=5.2,
                  raio_cavidade_mm=5.65, comprimento_util_mm=109.7,
                  contraforma_dividida_em='Z=70 mm', furos_alinhamento_mm=6.6,
                  parede_contraforma_mm=24, nervuras_externas_mm=12, parede_traseira_mm=12,
                  diametro_guias_marcacao_mm=PILOT_DIAMETER,
                  profundidade_pilotos_cegos_no_macho_mm=3, posicoes_furos_inox=HOLES,
                  centros_furos_xy_mm=[[x, y] for x in (-7.65, 127.65) for y in (20, 90)],
                  guias_alinhadas_e_desobstruidas=True,
                  extracao_macho_pela_frente_conferida_mm=[1,10,40,110],
                  sem_interferencia_com_macho_e_inox=True,
                  abertura_z_conferida_mm=[0, .1, 1, 10, 40, 80],
                  pecas=records, limites=['Acabamento de quatro dobras longitudinais preformadas',
                  'Nao forma o fundo nem define recortes ou emendas da chapa',
                  'Retorno elastico e forca de conformacao nao simulados; ensaio fisico pendente'])
    (dest / 'verificacao.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    return report


if __name__ == '__main__':
    print(json.dumps(export_tools(ROOT / 'output/v59'), indent=2, ensure_ascii=False))
