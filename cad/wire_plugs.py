"""Split labial cable plugs for the existing Ø12 × 14 mm wall passages.

Local Z points outward. Z=0 is the inner wall, Z=14 the outer wall.
The split plane X=0 passes through every cable axis.
"""
import cadquery as cq
from sensor_grommet import annulus_profile

SPECS = {
    'sensor': (1.40, (-2.8, 0, 2.8)),
    'aquecedor': (1.42, (-2.5, 2.5)),
}


def build_wire_plug(name):
    diameter, positions = SPECS[name]
    q = cq.Workplane('XY', origin=(0, 0, .3)).circle(5.8).extrude(13.7)
    q = q.union(cq.Workplane('XY', origin=(0, 0, 14)).circle(8).extrude(1.5))
    for y in positions:
        q = q.cut(cq.Workplane('XY', origin=(0, y, 0)).circle(1.3).extrude(16))
        # Only the thin inclined lips grip the cable; the bulk channel is Ø2.6.
        free_radius = diameter / 2 - .05
        reach = 1.35 - free_radius
        for z in (3, 9):
            lip = annulus_profile([(1.35, z+reach), (1.35, z+.4+reach),
                                   (free_radius, z+.4), (free_radius, z)])
            q = q.union(lip.translate((0, y, 0)))
    for z in (4, 10):
        q = q.union(annulus_profile([(5.75, z+.4), (5.75, z+.85),
                                    (6.15, z+.45), (6.15, z)]))
    halves = tuple(q.intersect(cq.Workplane('XY', origin=(x, -10, -1))
                   .box(10, 20, 18, centered=False)) for x in (-10, 0))
    assert all(h.val().isValid() and len(h.solids().vals()) == 1 for h in halves)
    return halves


def compound(halves):
    return cq.Workplane('XY').newObject([cq.Compound.makeCompound([h.val() for h in halves])])


def print_pair(halves):
    # Flat outer flanges on the bed; 4 mm between the split faces.
    return compound(tuple(h.rotate((0, 0, 0), (1, 0, 0), 180)
                    .translate((dx, 0, 15.5)) for h, dx in zip(halves, (-2, 2))))


def check_wire_plug(name, halves):
    diameter, positions = SPECS[name]
    q = compound(halves)
    bb = q.val().BoundingBox()
    assert abs(bb.zmin-.3) < 1e-5 and abs(bb.zmax-15.5) < 1e-5
    assert halves[0].intersect(halves[1]).val().Volume() < 1e-5
    outside_hole = cq.Workplane('XY').circle(9).circle(6).extrude(14)
    for z in (4, 10):
        outside_hole = outside_hole.cut(cq.Workplane('XY', origin=(0, 0, z))
                                       .circle(9).extrude(.9))
    assert q.intersect(outside_hole).val().Volume() < 1e-5
    for y in positions:
        wire = cq.Workplane('XY', origin=(0, y, 0)).circle(diameter/2).extrude(16)
        bulk = q
        for z in (3, 9):
            bulk = bulk.cut(cq.Workplane('XY', origin=(0, y, z))
                            .circle(1.36).extrude(1.2))
        assert bulk.intersect(wire).val().Volume() < 1e-5
        # Both halves expose each wire groove on their mating face.
        for h in halves:
            assert h.intersect(wire).val().Volume() > 0
    pair = print_pair(halves)
    assert len(pair.solids().vals()) == 2 and pair.val().isValid()
    assert abs(pair.val().BoundingBox().zmin) < 1e-5
    return dict(fios=len(positions), diametro_fios_mm=diameter,
                furo_existente_mm=12, parede_existente_mm=14,
                recuo_interno_mm=.3, profundidade_inserida_mm=13.7,
                flange_externa_mm=1.5, diametro_flange_mm=16,
                diametro_corpo_mm=11.6, diametro_labios_externos_mm=12.3,
                diametro_livre_labios_fios_mm=round(diameter-.1, 2),
                espessura_labios_fios_mm=.4, labios_por_fio=2,
                metades=2, distancia_metades_impressao_mm=4,
                interferencia_fios_apenas_labios=True,
                encaixe_e_vedacao_fisicos_pendentes=True)
