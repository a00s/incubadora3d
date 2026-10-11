"""Thin TPU sleeve with two flexible lips against the sensor and the roof hole."""
import cadquery as cq


def annulus_profile(points):
    return cq.Workplane('XZ').polyline(points).close().revolve(360,(0,0),(0,1))


def build_sensor_grommet(bore=15.4,center=(-27,60,110)):
    # Roof hole Ø20.4: loose sleeve Ø19.8, not a thick interference-fit cylinder.
    q=cq.Workplane('XY',origin=(0,0,1)).circle(9.9).circle(9.3).extrude(6)
    # Collar seat stays at Z8.5; entry chamfer clears the Ø15.62 sensor body.
    q=q.union(annulus_profile([(9.3,7),(12,7),(12,8.5),(8.6,8.5),(8.2,8.1)]))
    # Thin flared retainer below the roof; folds during insertion.
    q=q.union(annulus_profile([(9.3,.6),(9.9,1.2),(11,.1),(10.4,-.5)]))
    for z in (1.5,4):
        reach=9.35-bore/2
        q=q.union(annulus_profile([(9.35,z),(9.35,z+.55),
                                  (bore/2,z+.55+reach),(bore/2,z+reach)]))
    for z in (2,4.5):
        q=q.union(annulus_profile([(9.85,z),(9.85,z+.5),(10.3,z+.95),(10.3,z+.45)]))
    assert q.val().isValid() and len(q.solids().vals())==1
    return q.translate(center)
