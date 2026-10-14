"""Split compression cable plugs in eSUN TPU-LW for the existing Ø12 × 14 mm wall passages.

Local Z points outward. Z=0 is the inner wall, Z=14 the outer wall.
The split plane X=0 passes through every cable axis.
"""
import cadquery as cq

SPECS = {
    'sensor': (1.40, (-2.8, 0, 2.8)),
    'aquecedor': (1.42, (-2.5, 2.5)),
}


def build_wire_plug(name):
    diameter, positions = SPECS[name]
    # Foam compresses over the entire bore and along each cable. The oversized
    # body also presses the two mating faces together inside the rigid Ø12 bore.
    q = cq.Workplane('XY', origin=(0, 0, .3)).circle(6.12).extrude(13.7)
    q = q.union(cq.Workplane('XY', origin=(0, 0, 14)).circle(8).extrude(1.5))
    for y in positions:
        radius = diameter/2 - .08
        q = q.cut(cq.Workplane('XY', origin=(0, y, 0)).circle(radius).extrude(16))
        # Lead-ins on both ends; all layers begin on the outer flange.
        q = q.cut(cq.Solid.makeCone(radius+.3, radius, .5,
                                   cq.Vector(0,y,.3)))
        q = q.cut(cq.Solid.makeCone(radius, radius+.3, .5,
                                   cq.Vector(0,y,15)))
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
    # Interference is deliberate for this foam: 0.12 radial at the body,
    # 0.08 radial at each wire, and continuous compression along the split.
    for y in positions:
        wire = cq.Workplane('XY', origin=(0, y, 1)).circle(diameter/2).extrude(12)
        for h in halves:
            assert h.intersect(wire).val().Volume() > 0
    assert q.intersect(cq.Workplane('XY').circle(6.12).circle(6).extrude(14)).val().Volume()>0
    pair = print_pair(halves)
    assert len(pair.solids().vals()) == 2 and pair.val().isValid()
    assert abs(pair.val().BoundingBox().zmin) < 1e-5
    return dict(fios=len(positions), diametro_fios_mm=diameter,
                furo_existente_mm=12, parede_existente_mm=14,
                recuo_interno_mm=.3, profundidade_inserida_mm=13.7,
                flange_externa_mm=1.5, diametro_flange_mm=16,
                diametro_corpo_mm=12.24, material="eSUN TPU-LW",
                diametro_livre_canais_fios_mm=round(diameter-.16, 2),
                contato_fios_continuo_mm=13.7,
                metades=2, distancia_metades_impressao_mm=4,
                interferencia_fios_radial_mm=.08, interferencia_corpo_radial_mm=.12,
                encaixe_e_vedacao_fisicos_pendentes=True)
