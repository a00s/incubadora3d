"""Door-only hollow TPU-LW bellows; do not remove the fragile body's gasket.

The foot fits the existing groove with gradual growth for printing. A rear
web passes behind the broken receiver;
the bulb stays outside its nominal envelope and contacts the intact Y=0 land.
"""
import math
import cadquery as cq

# (Y, outer inset, inner inset); inset grows toward the chamber centre.
# Widen outward only above the rigid door land, preserving hinge sweep clearance.
# Skin remains >= extrusion width so support analysis retains both walls.
BULB=[(-4.05,.2,1.05),(-3.0,.15,1.35),(-1.0,.6,2.0),
      (0,.8,2.65),(1.3,-.45,2.65),(1.5,-.45,2.65),(3.2,1.05,1.15)]
VOID=[(-3.3,.65,.72),(-2.5,.75,1.0),(-1.0,1.15,1.45),
      (0,1.35,2.1),(1.3,.1,2.1),(2.6,1.15,1.25)]
LATCH_PROJECTION=3.2
HINGE_PROJECTION=2.0
HINGE_REDUCTION=LATCH_PROJECTION-HINGE_PROJECTION
STEM_TOP=-3.0
FOOT_OUTER_OFFSET=.6



def build_door_seal(inset_ring,inset_loft,boss_inset,foot):
    base=inset_ring([(y,boss_inset(y)-FOOT_OUTER_OFFSET) for y,d in foot],
                    [(y,boss_inset(y)+d) for y,d in foot])
    # These parts stay below the nominal receiver's Y=-3.7 starting plane.
    web=inset_ring([(-4.25,.15),(-3.8,.15)],
                   [(y,boss_inset(y)-.05) for y in (-4.25,-3.8)])
    stem=inset_ring([(y,boss_inset(y)-.6) for y in (-4.25,STEM_TOP)],
                    [(y,boss_inset(y)-.05) for y in (-4.25,STEM_TOP)])
    def ring(stations):
        def wire(inset,y):
            wire=inset_loft([(y,inset),(y+.01,inset)]).faces('<Y').val().outerWire()
            reduction=HINGE_REDUCTION*max(0,y+4.05)/(LATCH_PROJECTION+4.05)
            return wire.rotate((0,y,0),(0,y,1),-math.degrees(math.atan(reduction/120)))
        outer=cq.Solid.makeLoft([wire(a,y) for y,a,b in stations],ruled=True)
        inner=cq.Solid.makeLoft([wire(b,y) for y,a,b in stations],ruled=True)
        return cq.Workplane(obj=outer).cut(inner)
    bulb=ring(BULB).cut(ring(VOID))
    seal=base.union(stem,clean=False).union(web,clean=False).union(bulb,clean=False)
    assert seal.val().isValid() and len(seal.solids().vals())==1
    return seal
