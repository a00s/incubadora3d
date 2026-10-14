"""Door-only hollow TPU-LW bellows; do not remove the fragile body's gasket.

The foot fits the existing groove with gradual growth for printing. A rear
web passes behind the broken receiver;
the bulb stays outside its nominal envelope and contacts the intact Y=0 land.
"""
import math
import cadquery as cq

# (Y, outer inset, inner inset); inset grows toward the chamber centre.
BULB=[(-3.85,.15,1.0),(-3.0,.15,1.35),(-1.0,.7,2.0),(0,1.2,2.5),(.65,1.85,2.2)]
VOID=[(-3.3,.65,.85),(-2.5,.75,1.25),(-.8,1.2,1.6),(-.15,1.6,1.8)]


def build_door_seal(inset_ring,inset_loft,boss_inset,foot):
    base=inset_ring([(y,boss_inset(y)-.25) for y,d in foot],
                    [(y,boss_inset(y)+d) for y,d in foot])
    # These parts stay below the nominal receiver's Y=-3.7 starting plane.
    web=inset_ring([(-4.25,.15),(-3.8,.15)],
                   [(y,boss_inset(y)-.05) for y in (-4.25,-3.8)])
    stem=inset_ring([(y,boss_inset(y)-.6) for y in (-4.25,-3.45)],
                    [(y,boss_inset(y)-.05) for y in (-4.25,-3.45)])
    def ring(stations):
        def wire(inset,y):
            wire=inset_loft([(y,inset),(y+.01,inset)]).faces('<Y').val().outerWire()
            reduction=.4*max(0,y+3.85)/4.5
            return wire.rotate((0,y,0),(0,y,1),-math.degrees(math.atan(reduction/120)))
        outer=cq.Solid.makeLoft([wire(a,y) for y,a,b in stations],ruled=True)
        inner=cq.Solid.makeLoft([wire(b,y) for y,a,b in stations],ruled=True)
        return cq.Workplane(obj=outer).cut(inner)
    bulb=ring(BULB).cut(ring(VOID))
    seal=base.union(stem,clean=False).union(web,clean=False).union(bulb,clean=False)
    assert seal.val().isValid() and len(seal.solids().vals())==1
    return seal
