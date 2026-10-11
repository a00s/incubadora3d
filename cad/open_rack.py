"""Open drawer rack with central-height H braces at front and mid-depth, independent of the damaged lip."""
import cadquery as cq
from forming_tools import box


def build_rack():
    # Two H frames at the front and halfway along the depth.
    # A central-height brace ends 3 mm below the second drawer's base.
    rack=None
    for y in (3.6,40.55):
        for x in (4.95,111.9):
            bottom,top=(40,101) if y==40.55 else (4.95,101)
            post=box(3.15,6,top-bottom,x,y,bottom).edges('|Z').fillet(.6)
            rack=post if rack is None else rack.union(post)
        brace=box(110.1,6,4,4.95,y,65).edges('|X').fillet(.8)
        rack=rack.union(brace)
    for x in (4.95,111.9):
        rack=rack.union(box(3.15,4,96.05,x,79.5,4.95).edges('|Z').fillet(.6))
    # Six open guide beams, with no side panels or rear transverse braces.
    for z in (40,69,98):
        for x in (4.95,101.9):
            rail=box(13.15,75.5,3,x,8,z).edges('|X and <Y and >Z').chamfer(2)
            rack=rack.union(rail)
        for x in (8.1,101.9):
            rack=rack.union(box(10,3,3,x,80.5,z+3))
    # A low continuous outer edge retains the top drawer without isolated post tips.
    for x in (4.95,111.9):
        rack=rack.union(box(3.15,72.0,1.5,x,8,101).edges('|Y and >Z').fillet(.5))
    # Local feet transfer vertical load into the liner floor, without a bottom panel.
    for x in (4.95,105.9):
        for y,depth in ((3.6,6),(79.5,4)):
            foot=box(9.15,depth,3.05,x,y,4.95).edges('|Z').fillet(.6)
            rack=rack.union(foot)
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


def check_entry_clearance(rack):
    """Conservative drawer envelopes, slightly tilted and lifted for insertion."""
    checks=0
    for z in (43,72,101):
        drawer=box(102.2,72,9,8.9,8,z)
        for angle in (-3,3):
            tilted=drawer.rotate((60,44,z),(61,44,z),angle).translate((0,0,3))
            for pull in (0,5,15,30,50,72,80):
                placed=tilted.translate((0,-pull,0))
                assert rack.intersect(placed).val().Volume()<1e-5,(z,angle,pull)
                checks+=1
    return checks
