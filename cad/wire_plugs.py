"""Split compression cable plugs in eSUN TPU-LW for the existing Ø12 × 14 mm wall passages.

Local Z points outward. Z=0 is the inner wall, Z=14 the outer wall.
Both plugs use a contoured cradle/cap around the wire axes.
"""
import cadquery as cq

SPECS = {
    'sensor': (1.40, (-3.3, 0, 3.3)),
    'aquecedor': (1.42, (-2.5, 2.5)),
}


RADIAL_INTERFERENCE={'sensor':.15,'aquecedor':.08}
LEAD_IN_RADIAL={'sensor':.15,'aquecedor':.3}

def build_wire_plug(name):
    diameter, positions = SPECS[name]
    # Foam compresses over the entire bore and along each cable. The oversized
    # body also presses the two mating faces together inside the rigid Ø12 bore.
    q = cq.Workplane('XY', origin=(0, 0, .3)).circle(6.12).extrude(13.7)
    q = q.union(cq.Workplane('XY', origin=(0, 0, 14)).circle(8).extrude(1.5))
    for y in positions:
        radius = diameter/2 - RADIAL_INTERFERENCE[name]
        q = q.cut(cq.Workplane('XY', origin=(0, y, 0)).circle(radius).extrude(16))
        # Lead-ins on both ends; all layers begin on the outer flange.
        q = q.cut(cq.Solid.makeCone(radius+LEAD_IN_RADIAL[name], radius, .5,
                                   cq.Vector(0,y,.3)))
        q = q.cut(cq.Solid.makeCone(radius, radius+LEAD_IN_RADIAL[name], .5,
                                   cq.Vector(0,y,15)))
    halves = tuple(q.intersect(cq.Workplane('XY', origin=(x, -10, -1))
                   .box(10, 20, 18, centered=False)) for x in (-10, 0))
    # A carries all wires: individual flexible lips wrap past the wire axes.
    # B is the complementary cap, with a tongue for every funnel mouth.
    cradle=halves[0]
    for y in positions:
        boss=cq.Workplane('XY',origin=(0,y,.3)).circle(1.15).extrude(15.2)
        mouth=cq.Workplane('XY',origin=(0,y,0)).polyline(
            [(.15,-.4),(.55,-.4),(.85,-.8),(1.4,-.8),
             (1.4,.8),(.85,.8),(.55,.4),(.15,.4)]).close().extrude(16)
        cradle=cradle.union(q.intersect(boss).cut(mouth))
    cap=q.cut(cradle)
    halves=(cradle,cap)
    assert all(h.val().isValid() and len(h.solids().vals()) == 1 for h in halves)
    return halves


def compound(halves):
    return cq.Workplane('XY').newObject([cq.Compound.makeCompound([h.val() for h in halves])])


def print_pair(halves):
    # Flat outer flanges on the bed; 4 mm between actual part envelopes.
    flats=tuple(h.rotate((0,0,0),(1,0,0),180).translate((0,0,15.5)) for h in halves)
    extra=flats[0].val().BoundingBox().xmax
    left_shift=-2-extra if extra>1e-4 else -2
    return compound((flats[0].translate((left_shift,0,0)),flats[1].translate((2,0,0))))


def check_wire_plug(name, halves):
    diameter, positions = SPECS[name]
    q = compound(halves)
    bb = q.val().BoundingBox()
    assert abs(bb.zmin-.3) < 1e-5 and abs(bb.zmax-15.5) < 1e-5
    assert halves[0].intersect(halves[1]).val().Volume() < 1e-5
    # Interference is deliberate for this foam: 0.12 radial at the body,
    # the specified radial interference at each wire, and continuous compression along the split.
    for y in positions:
        channel_radius=diameter/2-RADIAL_INTERFERENCE[name]
        for z in (1,7,14.5):
            assert not halves[1].val().isInside((channel_radius-.01,y,z))
            assert halves[1].val().isInside((channel_radius+.01,y,z))
        wire = cq.Workplane('XY', origin=(0, y, 1)).circle(diameter/2).extrude(12)
        for h in halves:
            assert h.intersect(wire).val().Volume() > 0
    assert q.intersect(cq.Workplane('XY').circle(6.12).circle(6).extrude(14)).val().Volume()>0
    for y in positions:
        a,b=[h.val() for h in halves]
        assert a.isInside((.65,y+.6,7)) and a.isInside((.65,y-.6,7))
        assert not a.isInside((.8,y,7)) and b.isInside((.8,y,7))
    pair = print_pair(halves)
    assert len(pair.solids().vals()) == 2 and pair.val().isValid()
    assert abs(pair.val().BoundingBox().zmin) < 1e-5
    report=dict(fios=len(positions), diametro_fios_mm=diameter,
                furo_existente_mm=12, parede_existente_mm=14,
                recuo_interno_mm=.3, profundidade_inserida_mm=13.7,
                flange_externa_mm=1.5, diametro_flange_mm=16,
                diametro_corpo_mm=12.24, material="eSUN TPU-LW",
                diametro_livre_canais_fios_mm=round(diameter-2*RADIAL_INTERFERENCE[name], 2),
                contato_fios_continuo_mm=13.7,
                metades=2, distancia_metades_impressao_mm=4,
                diametro_entrada_canais_mm=round(diameter-2*RADIAL_INTERFERENCE[name]+2*LEAD_IN_RADIAL[name],2),
                interferencia_fios_radial_mm=RADIAL_INTERFERENCE[name], interferencia_corpo_radial_mm=.12,
                encaixe_e_vedacao_fisicos_pendentes=True)
    report.update(metade_A='berco com labios individuais de retencao',metade_B='tampa com '+('tres' if len(positions)==3 else 'dois')+' apoios de compressao',
                  centros_canais_mm=list(positions),passo_canais_mm=round(positions[1]-positions[0],2),espaco_nominal_entre_fios_mm=round(positions[1]-positions[0]-diameter,2),
                  boca_lateral_minima_mm=.8,entrada_lateral_funil_mm=1.6,espessura_nominal_labios_mm=round(1.15-(diameter/2-RADIAL_INTERFERENCE[name]),2))
    return report
