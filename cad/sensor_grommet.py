"""eSUN TPU-LW sleeve: original upper collar and lips, plus a hollow lower bulb."""
import cadquery as cq


def annulus_profile(points):
    return cq.Workplane('XZ').polyline(points).close().revolve(360,(0,0),(0,1))


def build_sensor_grommet(bore=15.2,center=(-27,60,110)):
    # Roof hole Ø20.4: loose sleeve Ø19.8, not a thick interference-fit cylinder.
    q=cq.Workplane('XY',origin=(0,0,1)).circle(9.9).circle(9.3).extrude(6)
    # Reinforce inward: the Ø20.4 roof hole and collar seat at Z8.5 stay fixed.
    # A 1.6 mm axial overlap and tapered inner web replace the thin neck joint.
    q=q.union(annulus_profile([(9.9,6),(9.9,7),(12,7),(12,8.5),
                              (8.6,8.5),(8.2,8.1),(8.2,7),
                              (8.7,6),(9.3,5.4)]))
    # Thin flared retainer below the roof; folds during insertion.
    q=q.union(annulus_profile([(9.3,.6),(9.9,1.2),(11,.1),(10.4,-.5)]))
    for z in (1.5,4):
        reach=9.35-bore/2
        q=q.union(annulus_profile([(9.35,z+reach),(9.35,z+.55+reach),
                                  (bore/2,z+.55),(bore/2,z)]))
    for z in (2,4.5):
        q=q.union(annulus_profile([(9.85,z+.45),(9.85,z+.95),(10.3,z+.5),(10.3,z)]))
    # Lower cylinder gets a supported hollow contact band in addition to the
    # original lips. The collar/neck above local Z5.32 remain unchanged.
    r=bore/2-.1
    bulb=annulus_profile([(9.65,5.2),(9.1,5.2),(r+.8,4.3),(r+.3,3.8),
                          (r,3.3),(r,2.6),(r+.3,2.3),(r+1,1.6),(9.1,.9),(9.65,.9)])
    cavity=annulus_profile([(9.05,4.6),(r+.85,3.8),(r+.55,3.3),
                            (r+.55,2.8),(r+.95,2.4),(9.05,1.7),(9.1,1.7),(9.1,4.6)])
    hollow_bulb=bulb.cut(cavity)
    assert hollow_bulb.val().isValid() and len(hollow_bulb.solids().vals())==1
    q=q.union(hollow_bulb)
    assert q.val().isValid() and len(q.solids().vals())==1
    return q.translate(center)


def sensor_grommet_print(obj):
    """Outer collar face on the bed; the flexible lips point upward during printing."""
    q=obj.rotate((0,0,0),(1,0,0),180)
    b=q.val().BoundingBox()
    return q.translate((-(b.xmin+b.xmax)/2,-(b.ymin+b.ymax)/2,-b.zmin))
