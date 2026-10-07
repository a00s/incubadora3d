"""True circular double helix, entirely outside the sealed door."""
import math
from io import BytesIO
import cadquery as cq


def dna_grip():
    cx, cy, z0, height, radius, rod = -15, -8.4, 94, 36, 6, 1.6
    def normalize(shape):
        stream=BytesIO()
        shape.exportBrep(stream)
        stream.seek(0)
        return cq.Shape.importBrep(stream)
    def point(side, offset):
        a=2*math.pi*offset/height
        return cq.Vector(cx+side*radius*math.cos(a),cy+side*radius*math.sin(a),z0+offset)
    elements=[]
    for side in [1,-1]:
        path=cq.Wire.makeHelix(height,height,radius)
        if side==-1:
            path=path.rotate((0,0,0),(0,0,1),180)
        path=path.translate((cx,cy,z0))
        plane=cq.Plane(origin=path.startPoint(),normal=path.tangentAt(0))
        rail=cq.Workplane(plane).circle(rod).sweep(cq.Workplane(obj=path),isFrenet=True)
        elements.append(normalize(rail.val()))
    for offset in [2,10,18,26,34]:
        a,b=point(-1,offset),point(1,offset)
        v=(b-a).normalized()
        elements.append(cq.Solid.makeCylinder(1.1,(b-a).Length+1,a-v*.5,v))
    # Organic roots curve away from the helix and flare into the intact shell.
    for z, direction in [(94,-1),(130,1)]:
        stations=[(-10,0,1.8),(-8,.15,1.9),(-4,1.8,2.3),(0,3.7,3.3),(3,5,4)]
        wires=[cq.Workplane('YZ',origin=(x,cy,z+direction*rise)).circle(r).val()
               for x,rise,r in stations]
        elements.append(normalize(cq.Solid.makeLoft(wires,ruled=False)))
    grip=cq.Workplane(obj=elements[0].fuse(*elements[1:],tol=1e-5))
    assert grip.val().isValid() and len(grip.solids().vals())==1
    for side in [-1,1]:
        for offset in range(1,36):
            assert grip.val().isInside(point(side,offset).toTuple()),(side,offset)
    return grip
