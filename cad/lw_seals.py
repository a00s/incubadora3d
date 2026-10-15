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
BULB=[(-4.05,.2,1.05),(-3,.15,1.35),(-1,.6,2.0),(0,.8,2.65),
      (.8,.05,2.65),(1.6,-.7,2.65),(2.2,-1.15,3.05),
      (2.7,-1.4,3.3),(3.1,-1.4,3.3),(3.5,-1.25,3.15),
      (4,-.85,2.75),(4.6,-.25,2.15),(5.2,.35,1.55),(5.7,.85,1.05)]
VOID=[(-3.3,.65,.72),(-2.5,.75,1.0),(-1,1.15,1.45),(0,1.35,2.1),
      (.8,.6,2.1),(1.6,-.15,2.1),(2.2,-.6,2.5),(2.7,-.85,2.75),
      (3,-.85,2.75),(3.4,-.65,2.55),(4,-.08,1.98),
      (4.6,.49,1.41),(4.95,.8225,1.0775),(5.1,.94,.96)]
LATCH_PROJECTION=5.7
HINGE_PROJECTION=2.0
HINGE_REDUCTION=LATCH_PROJECTION-HINGE_PROJECTION
BASE_REDUCTION=1.2
HINGE_EXTRA_REDUCTION=LATCH_PROJECTION-BASE_REDUCTION-HINGE_PROJECTION
HINGE_SCALE=(HINGE_PROJECTION+BASE_REDUCTION*4.05/(LATCH_PROJECTION+4.05))/LATCH_PROJECTION
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
    def ring(stations,is_void=False):
        def wire(inset,y,side):
            # Keep the proven section through X90. Only the last 30 mm of the
            # top/bottom runs transition into the smaller hinge-side bulb.
            blend=min(1,max(0,y+1))
            scale=1-(1-HINGE_SCALE)*blend
            target=1.7+(inset-1.7)*scale
            if not is_void:target+=side*.55*(1-scale)
            extra=HINGE_EXTRA_REDUCTION*max(0,y)/LATCH_PROJECTION
            r=10-inset;rh=10-target;root2=math.sqrt(2)
            def v(x,z,right=False):return cq.Vector(x,y-extra if right else y,z)
            pts=[v(10,inset),v(90,inset),v(110,target,True),
                 v(120-target,10,True),v(120-target,130,True),v(110,140-target,True),
                 v(90,140-inset),v(10,140-inset),v(inset,130),v(inset,10)]
            mids={2:v(110+rh/root2,10-rh/root2,True),
                  4:v(110+rh/root2,130+rh/root2,True),
                  7:v(10-r/root2,130+r/root2),9:v(10-r/root2,10-r/root2)}
            edges=[cq.Edge.makeThreePointArc(p,mids[i],pts[(i+1)%10]) if i in mids
                   else cq.Edge.makeLine(p,pts[(i+1)%10]) for i,p in enumerate(pts)]
            wire=cq.Wire.assembleEdges(edges)
            caps=[]
            groups=[edges[:1]+[cq.Edge.makeLine(pts[1],pts[6])]+edges[6:],
                    [edges[1],cq.Edge.makeLine(pts[2],pts[5]),edges[5],cq.Edge.makeLine(pts[6],pts[1])],
                    edges[2:5]+[cq.Edge.makeLine(pts[5],pts[2])]]
            reduction=BASE_REDUCTION*max(0,y+4.05)/(LATCH_PROJECTION+4.05)
            angle=-math.degrees(math.atan(reduction/120))
            for group in groups:
                caps.append(cq.Face.makeFromWires(cq.Wire.assembleEdges(group)).rotate((0,y,0),(0,y,1),angle))
            return wire.rotate((0,y,0),(0,y,1),angle),caps
        def loft(side):
            # The local height transition folds each end wire into three planes.
            # Sew explicit planar caps; automatic solid loft caps assume one plane.
            from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
            rows=[wire(a if side==-1 else b,y,side) for y,a,b in stations]
            builder=BRepOffsetAPI_ThruSections(False,True)
            for w,c in rows:builder.AddWire(w.wrapped)
            builder.Build()
            shell=cq.Shape.cast(builder.Shape())
            solid=cq.Solid.makeSolid(cq.Shell.makeShell(shell.Faces()+rows[0][1]+rows[-1][1])).fix()
            assert solid.isValid(),'Invalid hinge loft'
            return cq.Workplane(obj=solid)
        return loft(-1).cut(loft(1),clean=False)
    bulb=ring(BULB).cut(ring(VOID,True),clean=False)
    assert bulb.val().isValid() and len(bulb.solids().vals())==1
    seal=base.union(stem,clean=False).union(web,clean=False).union(bulb,clean=False)
    # Vent only the outward bulb skin into its cavity; inner sealing skin stays intact.
    vent=cq.Workplane('YZ',origin=(-2.1,3.0,70)).circle(.4).extrude(1.55)
    seal=seal.cut(vent,clean=False)
    assert seal.val().isValid() and len(seal.solids().vals())==1
    return seal
