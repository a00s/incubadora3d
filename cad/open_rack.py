"""Open drawer rack with a low front H brace, independent of the damaged lip."""
import cadquery as cq
from forming_tools import box


def build_rack():
    # Full-height front posts leave 0.15 mm per edge in the nominal liner.
    posts=[box(3.15,12,130.1,x,3.6,4.95) for x in (4.95,111.9)]
    rack=posts[0].union(posts[1])
    # The crossbar is in the gap above the water pan and below the lowest drawer.
    brace=box(110.1,12,6,4.95,3.6,29).edges('|X').fillet(.8)
    rack=rack.union(brace)
    for x in (4.95,111.9):
        rack=rack.union(box(3.15,7,107.05,x,76.5,4.95))
    # Six open guide beams, with no side panels or rear transverse braces.
    for z in (40,69,98):
        for x in (4.95,101.9):
            rail=box(13.15,75.5,3,x,8,z).edges('|X and <Y and >Z').chamfer(2)
            rack=rack.union(rail)
        for x in (8.1,101.9):
            rack=rack.union(box(10,3,3,x,80.5,z+3))
    # Local feet transfer vertical load into the liner floor, without a bottom panel.
    for x in (4.95,105.9):
        for y,depth in ((3.6,12),(76.5,7)):
            foot=box(9.15,depth,3.05,x,y,4.95)
            rack=rack.union(foot)
    # Small planar gussets under the front crossbar distribute load to the posts.
    for points in ([(8.1,23),(8.1,29),(14.1,29)],
                   [(111.9,23),(111.9,29),(105.9,29)]):
        rib=cq.Workplane('XZ',origin=(0,15.6,0)).polyline(points).close().extrude(12)
        rack=rack.union(rib)
    # Rounded contact section follows the original liner, with fitting clearance.
    envelope=box(110.1,110,130.1,4.95,0,4.95).edges('|Y').fillet(5.05)
    rack=rack.intersect(envelope)
    assert rack.val().isValid() and len(rack.solids().vals())==1
    return rack


def check_drawer_support(rack):
    """Measure actual contact under each drawer at both lateral clearance limits."""
    overlaps=[]
    for z in (43,72,101):
        for dx in (-.8,0,.8):
            for lo,hi in ((8.9+dx,60),(60,111.1+dx)):
                probe=box(hi-lo,50,.05,lo,20,z-.05)
                contact=rack.intersect(probe).val().Volume()
                width=contact/(50*.05)
                assert width>=8.4-1e-4,(z,dx,width)
                overlaps.append(width)
    return min(overlaps)
