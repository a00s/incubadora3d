"""Preliminary mechanical layout; millimetres. Not validated for operation."""
import json
import math
import sys
from pathlib import Path
import cadquery as cq
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.gp import gp_Pnt
from OCP.TopAbs import TopAbs_IN
OUT=Path(__file__).resolve().parents[1]/'output'/'v58'
OUT.mkdir(exist_ok=True)
CHECK_MOVEMENTS="--check-movements" in sys.argv
P=dict(width=120,depth=115,height=140,wall=4,mixer_radius=32,mixer_height=110,slide_length=76,slide_width=26,slide_height=1,tray_pitch=29,port_diameter=5.6,insulation_extension=10,air_cell_width=6,outer_skin=2)
P.update(sensor_diameter=15.62, sensor_insertion=80.75, sensor_mount_clearance_diameter=20.4, inlet_height=10.5, hose_od=5.8, inlet_socket_diameter=5.6, inlet_socket_depth=12, inlet_bore_diameter=3.5)
P.update(sensor_collar_diameter=18.31, sensor_head_width=20.55, sensor_seal_bore=15.3, rj_cutout_width=14.79, rj_cutout_height=19.31, rj_panel_thickness=1.6)
P.update(tray_depth=72,tray_rear_y=80,heater_front_y=106,tray_heater_gap=26)
parts=[]
clash_envelopes={}
integral_thread_cuts=[]
integral_thread_reliefs=[]
integral_threaded_names=set()
def box(w,d,h,x=0,y=0,z=0):
    return cq.Workplane('XY').box(w,d,h,centered=False).translate((x,y,z))
def add(name,obj,color,kind='part'):
    assert obj.val().isValid(),name
    assert obj.val().Volume()>0,name
    parts.append((name,obj,color,kind))
def independent(obj):
    # Keep diagnostic Boolean operations from modifying shared OCCT face tolerances.
    return cq.Workplane(obj=obj.val().copy())
def yhole(x,y,z,r,length):
    return cq.Workplane('XZ',origin=(x,y,z)).circle(r).extrude(length,both=True)
print('Building chamber and sealing frame',flush=True)
w,d,h,t=P['width'],P['depth'],P['height'],P['wall']
outer=box(w,d,h).edges('|Y').fillet(8)
# Constant rounded XZ section, with square joins to the planar rear wall.
cavity=box(w-2*t,d+6,h-2*t,t,-10,t).edges('|Y').fillet(6)
body=outer.cut(cavity)
# Front sealing land moves outboard instead of narrowing the chamber entrance.
# Its rear edge grows at 45 degrees when printed rear-down.
rim=box(w+8,8,h+8,-4,0,-4).edges('|Y').fillet(12)
rim=rim.faces('>Y').edges().chamfer(4).cut(cavity)
body=body.union(rim)
P.update(chamber_width=112,chamber_height=132,chamber_depth=111,
         chamber_corner_radius=6,chamber_rear_join_radius=0,
         front_opening_matches_chamber=True,integral_tray_supports=False,
         liner_material='inox 304',liner_thickness=.3,liner_side_clearance=.5,
         liner_outer_width=111,liner_outer_height=131,liner_outer_depth=110,
         liner_inner_width=110.4,liner_inner_height=130.4,liner_inner_depth=109.7,
         seal_centerline_inset=0,hinge_axis_x=130,hinge_axis_y=-6)
# Sections are (depth y, half-width), relative to centreline inset 0 mm.
# Entry chamfer -> narrow throat -> wider retained foot cavity.
GROOVE=[(-0.1,1.6),(0.5,1.2),(0.9,1.2),(1.6,2.0),(3.2,2.0)]
FOOT=[(0.0,0.95),(0.9,0.95),(1.65,1.75),(2.8,1.75),(3.0,1.5)]
LIP_CENTERS=[(0,.65),(-.7,1.1),(-2.5,2.4)]
BODY_INNER_LIP_CENTERS=[(0,.65),(-.7,-.4),(-2.5,-.8)]
LIP_WALL=.6
P.update(gasket_material_hardness='TPU 95A',gasket_lip_count=2,gasket_lip_wall=.6,
         gasket_free_lip_depth=2.5,gasket_closed_face_gap=1,
         gasket_nominal_lip_deflection=1.5,gasket_leak_test='pending physical test')
def rounded_wire(inset,y):
    return box(w-2*inset,1,h-2*inset,inset,y-1,inset).edges('|Y').fillet(8-inset).faces('>Y').val().outerWire()
def seal_ring(stations):
    outer_wires=[rounded_wire(P['seal_centerline_inset']-half,y) for y,half in stations]
    inner_wires=[rounded_wire(P['seal_centerline_inset']+half,y) for y,half in stations]
    return cq.Workplane(obj=cq.Solid.makeLoft(outer_wires,ruled=True)).cut(cq.Solid.makeLoft(inner_wires,ruled=True))
ring=seal_ring(GROOVE)
body=body.cut(ring)
# One gas wall follows the external rounded profile; no inner duplicate shell.
def lateral_envelope(radius,rear_y,z,height,right_x=-10):
    front=cq.Workplane('XY',origin=(-10,60,z)).circle(radius).extrude(height)
    front=front.intersect(box(radius+right_x+10,radius,height,-10-radius,60-radius,z))
    rear=box(radius+right_x+10,rear_y-60,height,-10-radius,60,z)
    return front.union(rear)
def printable_gas_cavity(radius,rear_y,z,height):
    # Rear-down printing: a straight 45-degree closing face replaces the inner arc.
    # The external arc stays unchanged; each new layer advances inward by its height.
    points=[(-10-radius,60),(-10,60-radius),(-10,rear_y),(-10-radius,rear_y)]
    ramp=cq.Workplane('XY',origin=(0,0,z)).polyline(points).close().extrude(height)
    return lateral_envelope(radius,rear_y,z,height).intersect(ramp)
P.update(mixer_radius=49,mixer_internal_radius=45,mixer_curved_wall_thickness=4,
         mixer_wall_count=1,mixer_internal_floor_z=-6,print_body_bed_face='rear Y125',
         print_body_build_direction='-Y',print_orientation_review='gas closure changed to 45-degree internal ramp; full slicing and PC coupon pending',
         print_material='PC',print_printer='Creality K1C',gas_internal_closure_angle_deg=45,
         gas_external_curve_preserved=True,gas_closure_cavity_reduced=True)
r=P['mixer_radius'];mh=P['mixer_height'];cy=60
mix=lateral_envelope(49,96.5,-10,112)
inner=printable_gas_cavity(45,94,-6,103.5)
# A short reinforced ring retains the cover seat without a second gas wall.
inner=inner.union(printable_gas_cavity(43.3,94,97.5,4.5))
gas_shell=mix.cut(inner)
body=body.union(gas_shell)
# Shared-wall passage accepts the silicone OD5.8 tube with nominal 0.2 mm interference.
P.update(port_hose_outer_diameter=5.8,port_nominal_diametral_interference=.2,port_wall_path_length=14)
# Continuous passage below slides and above the water pan.
passage=cq.Workplane('YZ',origin=(-18,cy,34)).circle(P['port_diameter']/2).extrude(30)
body=body.cut(passage)
# External rear socket for silicone OD5.8; straight, accessible gas passage.
# Local +Z becomes global +Y, outward through the rear lower enclosure.
P.update(inlet_internal_exit_height=10.5,inlet_axis='+Y',inlet_type='flush rear female socket',
         inlet_outer_diameter=10,inlet_total_length=33,inlet_external_projection=0,
         inlet_socket_mouth_diameter=6.2,inlet_socket_chamfer_depth=1,
         inlet_root_center=[-23,92,10.5],inlet_tip_center=[-23,125,10.5],
         inlet_internal_channel_end=[-23,84,10.5])
def inlet_socket():
    q=cq.Workplane('XY').circle(P['inlet_outer_diameter']/2).extrude(P['inlet_total_length'])
    q=q.cut(cq.Workplane('XY',origin=(0,0,-5)).circle(P['inlet_bore_diameter']/2).extrude(P['inlet_total_length']+6))
    q=q.cut(cq.Workplane('XY',origin=(0,0,P['inlet_total_length']-P['inlet_socket_depth'])).circle(P['inlet_socket_diameter']/2).extrude(P['inlet_socket_depth']+1))
    # Taper the internal shoulder for rear-down printing instead of a flat overhang.
    q=q.cut(cq.Solid.makeCone(P['inlet_bore_diameter']/2,P['inlet_socket_diameter']/2,2,cq.Vector(0,0,P['inlet_total_length']-P['inlet_socket_depth']-2)))
    q=q.cut(cq.Solid.makeCone(P['inlet_socket_diameter']/2,P['inlet_socket_mouth_diameter']/2,1,cq.Vector(0,0,P['inlet_total_length']-1)))
    return q
inlet=inlet_socket().rotate((0,0,0),(1,0,0),-90).translate(P['inlet_root_center'])
inlet_bore=cq.Workplane('XZ',origin=(-23,84,10.5)).circle(P['inlet_bore_diameter']/2).extrude(-43)
inlet_socket_clearance=cq.Workplane('XZ',origin=(-23,113,10.5)).circle(P['inlet_socket_diameter']/2).extrude(-13)
body=body.union(inlet).cut(inlet_bore)
assert independent(body).intersect(inlet_bore).val().Volume()<1e-6,'Straight CO2 inlet blocked'
assert not body.val().isInside((-23,84,10.5)), 'CO2 inlet does not reach mixer chamber'
assert len(inlet.solids().vals())==1, 'CO2 socket disconnected'
assert independent(inlet).intersect(mix).val().Volume()>0, 'CO2 socket misses mixer wall'

# Real mating helical threads; dimensions describe our own printed profiles.
def printed_thread(clearance=False,diameter=8,pitch=2,length=31):
    root=diameter*.375
    crest=diameter*(.54375 if clearance else .5)
    half=pitch*(.475 if clearance else .325)
    path=cq.Wire.makeHelix(pitch,length,root)
    tooth=cq.Workplane('XZ').polyline([(diameter*.25,-half),(crest,0),(diameter*.25,half)]).close().sweep(path,isFrenet=True)
    result=cq.Workplane('XY').circle(diameter*(.425 if clearance else .385)).extrude(length).union(tooth).intersect(cq.Workplane('XY').circle(crest+.1).extrude(length))
    assert result.val().isValid() and len(result.solids().vals())==1, 'Invalid thread solid'
    assert result.val().isInside((0,0,length/2)), 'Thread core missing'
    assert result.val().Volume()>=math.pi*(diameter*(.425 if clearance else .385))**2*length*.99, 'Thread core volume missing'
    return result

# Compact hinges use the user's M4x20 bolts and metal nuts in the door.
# A compression sleeve keeps tightening force off the stationary middle knuckle.
doorpart=box(w+8,5,h+8,-4,-6,-4).edges('|Y').fillet(12)
P.update(hinge_bore_diameter=6.4,hinge_bolt='M4x20',hinge_bolt_count=2,
         hinge_nut_across_flats=7,hinge_nut_thickness=3.2,
         hinge_nut_pocket_across_flats=7.3,hinge_nut_pocket_depth=3.4,
         hinge_stack_height=17.5,hinge_axial_clearance=.25,
         hinge_sleeve_od=6,hinge_sleeve_id=4.4,hinge_sleeve_length=8.5,
         hinge_nuts_in_door=True,hinge_head_style='countersunk, confirmed by user')
for z in [22,102]:
    middle=cq.Workplane('XY',origin=(130,-6,z+4.75)).circle(6).circle(3.2).extrude(8)
    fixed=box(6,12,8,124,-6,z+4.75).union(middle)
    # Rear-down build (-Y): grow the outboard barrel from the side wall at
    # 45 degrees, then support its rear half up to the widest circular section.
    hinge_ramp=cq.Workplane('XY',origin=(0,0,z+4.75)).polyline(
        [(128,-6),(136,-6),(136,6),(128,14)]).close().extrude(8)
    # The mounting web enters the insulation void at X124..128, Y2..6.
    # Its former flat rear face at Y6 needs support INSIDE the closed wall.
    # Grow it from the existing outer skin X128 at Y10 toward X124 at Y6.
    hinge_internal_ramp=cq.Workplane('XY',origin=(0,0,z+4.75)).polyline(
        [(124,-6),(130,-6),(130,12),(124,6)]).close().extrude(8)
    fixed=fixed.union(hinge_ramp).union(hinge_internal_ramp)
    internal_roof_faces=[f for f in hinge_internal_ramp.val().Faces() if f.normalAt().y>.1]
    assert len(internal_roof_faces)==1
    assert abs(internal_roof_faces[0].normalAt().y-1/math.sqrt(2))<1e-6
    P.update(hinge_internal_wall_support_ramp_angle_deg=45,
             hinge_internal_wall_support_ramp_count=2,
             hinge_internal_wall_support_ramp_profile_xy=[[124,-6],[130,-6],[130,12],[124,6]],
             hinge_internal_wall_supported_void_region_xy=[124,128,6,10])
    P.update(hinge_external_support_ramp_angle_deg=45,
             hinge_external_support_ramp_build_direction='-Y',
             hinge_external_support_ramp_count=2,
             hinge_external_support_ramp_axial_height_mm=8)
    assert hinge_ramp.val().isValid()
    # The only rear-facing outer roof plane advances X and Y equally.
    ramp_faces=[f for f in hinge_ramp.val().Faces() if f.normalAt().y>.1]
    assert len(ramp_faces)==1 and abs(ramp_faces[0].normalAt().y-1/math.sqrt(2))<1e-6
    fixed=fixed.cut(cq.Workplane('XY',origin=(130,-6,z+4.5)).circle(3.2).extrude(8.5))
    body=body.union(fixed)
    moving=None
    for zz in [z,z+13]:
        lug=cq.Workplane('XY',origin=(130,-6,zz)).circle(6).circle(2.2).extrude(4.5)
        lug=lug.union(box(7,5,4.5,123,-6,zz))
        moving=lug if moving is None else moving.union(lug)
    nut_pocket=cq.Workplane('XY',origin=(130,-6,z-.1)).polygon(6,7.3/math.cos(math.pi/6)).extrude(3.5)
    # Clip the moving barrel's front cap flush with the sealing face for flat printing.
    moving=moving.cut(box(24,10,20,118,-1,z-1)).cut(nut_pocket)
    # 90-degree countersink, Ø8.8 at the upper face, Ø4.4 at its root.
    head_seat=cq.Solid.makeCone(2.2,4.4,2.2,cq.Vector(130,-6,z+15.3))
    # Clear the shaft again after unioning the bridge webs into the barrels.
    moving=moving.cut(cq.Workplane('XY',origin=(130,-6,z-.1)).circle(2.2).extrude(17.7)).cut(head_seat)
    doorpart=doorpart.union(moving)
    sleeve=cq.Workplane('XY',origin=(130,-6,z+4.5)).circle(3).circle(2.2).extrude(8.5)
    add(f'bucha_dobradica_{z}',sleeve,'#b5a78c','hinge_sleeve')
    # Metal reference: countersunk M4x20 overall length, plain shaft envelope.
    bolt=cq.Workplane('XY',origin=(130,-6,z-2.5)).circle(2).extrude(18)
    bolt=bolt.union(cq.Solid.makeCone(2,4,2,cq.Vector(130,-6,z+15.5)))
    nut=cq.Workplane('XY',origin=(130,-6,z+.2)).polygon(6,7/math.cos(math.pi/6)).circle(2.1).extrude(3.2)
    add(f'parafuso_M4x20_dobradica_{z}',bolt,'#505965','hardware')
    add(f'porca_M4_dobradica_{z}',nut,'#505965','hardware')
    assert independent(fixed).intersect(sleeve).val().Volume()<1e-5,'Hinge sleeve binds fixed knuckle'
    assert independent(moving).intersect(nut).val().Volume()<1e-5,'Metal nut pocket too small'
    # Independent coupon preserves the actual knuckles, nut seat and screw seat.
    if z==22:
        hinge_fixed_coupon=fixed.union(box(14,23,18,116,-9,z)).cut(cq.Workplane('XY',origin=(130,-6,z)).circle(3.2).extrude(18))
        hinge_door_coupon=moving.union(box(10,5,17.5,113,-6,z))
# Fully printed adjustable latch: custom 8 mm thread, pitch 2 mm.
# Only the last 7 mm are threaded; the integral receiver starts at axial 26 mm.
# Start at 24 mm (12 full pitches) to retain the mating helix phase.
thread=printed_thread(length=7).translate((0,0,24))
thread=thread.union(cq.Workplane('XY').circle(4).extrude(24.2))
P.update(latch_shaft_smooth_length=24,latch_shaft_smooth_diameter=8,latch_shaft_radial_clearance=.35,latch_thread_length=7)
assert thread.val().isValid() and len(thread.solids().vals())==1
thread_clear=printed_thread(True,length=9).translate((0,0,24))
printed_nut=cq.Workplane('XY',origin=(0,0,26)).polygon(6,14).extrude(5).cut(thread_clear)
assert printed_nut.val().isValid() and len(printed_nut.solids().vals())==1
assert independent(thread).intersect(printed_nut).val().Volume()<1e-5,'Printed thread clearance failed'
latches=[]
P.update(latch_count=1,latch_height=70,latch_axis_x=-13)
for z in [P['latch_height']]:
    def at_latch(obj):return obj.rotate((0,0,0),(1,0,0),-90).translate((-13,-23,z))
    tab=box(19.75,26,20,-24,-16,z-10).edges('|Y').fillet(3)
    # Fill only the insulation behind the latch mounting web, not the gas cavity.
    # Start in the outer skin X-8 at Y13.75; reach X-4.25 at Y10 with a 45° roof.
    latch_internal_ramp=cq.Workplane('XY',origin=(0,0,z-10)).polyline(
        [(-10,9.8),(-4.25,9.8),(-4.25,10),(-10,15.75)]).close().extrude(20)
    tab=tab.union(latch_internal_ramp)
    latch_roof_faces=[f for f in latch_internal_ramp.val().Faces() if f.normalAt().y>.1]
    assert len(latch_roof_faces)==1
    assert abs(latch_roof_faces[0].normalAt().y-1/math.sqrt(2))<1e-6
    P.update(latch_internal_wall_support_ramp_angle_deg=45,
             latch_internal_wall_support_ramp_profile_xy=[[-10,9.8],[-4.25,9.8],[-4.25,10],[-10,15.75]],
             latch_internal_wall_supported_void_region_xy=[-8,-4.25,10,13.75])
    # Smooth guide up to the last 7 mm of the base, then an integral female thread.
    guide=cq.Workplane('XY').circle(4.351).extrude(26)
    receiver_cut=at_latch(thread_clear.union(guide))
    integral_thread_cuts.append(receiver_cut)
    integral_thread_reliefs.append(at_latch(cq.Workplane('XY',origin=(0,0,26)).circle(4.4).extrude(7.1)))
    body=body.union(tab).cut(at_latch(guide))
    # Broad pressure face with a chamfered lead-in; raised finger grip clears
    # both the central knob and the adjacent door handle in the assembled pose.
    dog=box(30,4,16,-20,-20,z-8).edges('|Y').fillet(2)
    dog=dog.faces('>Y').edges().chamfer(.8).cut(yhole(-13,-18,z,4.35,5))
    grip=box(8,10.5,16,2,-30,z-8).edges('|Y').fillet(2)
    for dz in [-5,0,5]:
        grip=grip.union(box(6,2,2,3,-31,z+dz-1).edges('|X').fillet(.6))
    dog=dog.union(grip)
    assert dog.val().isValid() and len(dog.solids().vals())==1,'Invalid finger-grip latch'
    P.update(latch_finger_grip_projection=11,latch_contact_height=16,latch_contact_chamfer=.8)
    knob=cq.Workplane('XZ',origin=(-13,-20,z)).polygon(8,20).extrude(6).union(at_latch(thread))
    add(f'lingueta_fecho_{z}',dog,'#e6a454','latch')
    add(f'manipulo_fecho_{z}',knob,'#c88b43','knob')
    latches.append((z,dog))
    clash_envelopes[f'manipulo_fecho_{z}']=cq.Workplane('XZ',origin=(-13,-20,z)).polygon(8,20).extrude(6).union(yhole(-13,-7.5,z,4,15.5))
    integral_threaded_names.add(f'manipulo_fecho_{z}')
# Pull handle, open underneath.
handle=box(8,13,42,7,-19,49).cut(box(10,10,26,6,-17,57))
doorpart=doorpart.union(handle.translate((10,-10,0)))

# Free TPU shape: foot retained in channel; lip compressed by nominal 1.5 mm.
def lip_ring(side,wall=LIP_WALL):
    centres=BODY_INNER_LIP_CENTERS if side==1 else LIP_CENTERS
    outer=[rounded_wire(P['seal_centerline_inset']+side*centre-wall/2,y) for y,centre in centres]
    inner=[rounded_wire(P['seal_centerline_inset']+side*centre+wall/2,y) for y,centre in centres]
    return cq.Workplane(obj=cq.Solid.makeLoft(outer,ruled=True)).cut(cq.Solid.makeLoft(inner,ruled=True))
seal=seal_ring(FOOT).union(lip_ring(-1)).union(lip_ring(1))
assert len(seal.solids().vals())==1,'Double-lip gasket disconnected'
add('junta_porta',seal,'#45ae89','seal')

print('Building removable rack',flush=True)
# Windowed side frames with broad, open L rails.
# No upper rail: trays rest freely and enter without threading a narrow slot.
RACK_LEVELS=[40,69,98]
TRAY_THICKNESS=3
TRAY_LATERAL_CLEARANCE=.8
TRAY_WIDTH=109.8-6-2*TRAY_LATERAL_CLEARANCE
TRAY_X=(120-TRAY_WIDTH)/2
rack=None
for xx in [5.1,111.9]:
    side=box(3,75.5,107.2,xx,8,4.8)
    for lo,hi in [(12,38),(51.6,67),(80.6,96)]:
        side_window=box(5,62.5,hi-lo,xx-1,14,lo).edges('|X and <Y').chamfer((hi-lo-.4)/2)
        side=side.cut(side_window)
    rack=side if rack is None else rack.union(side)
for zz in RACK_LEVELS:
    for xx in [8.1,105.9]:
        # Entry grows from a thin nose to full thickness at 45 degrees.
        rail=box(6,75.5,3,xx,8,zz).edges('|X and <Y and >Z').chamfer(2)
        rack=rack.union(rail)
        rack=rack.union(box(6,3,3,xx,80.5,zz+3))
for zz in [4.8,109]:
    rack=rack.union(box(109.8,3,2.5 if zz<10 else 3,5.1,80.5,zz))
# Trim the feet to the lining's rounded floor/side corners.
rack=rack.intersect(box(110.4,109.7,130.4,4.8,0,4.8).edges('|Y').fillet(5.2))
assert len(rack.solids().vals())==1,'Removable rack disconnected'
P.update(tray_base_thickness_mm=TRAY_THICKNESS,tray_captive_guide_type='open L rails',
         tray_lateral_clearance_per_side_mm=.8,tray_vertical_guide_clearance_mm=None,
         tray_guide_support_width_mm=6,tray_minimum_lateral_overlap_mm=4.4,
         tray_upper_guide_removed=True,tray_entry_chamfer_mm=2,
         rack_side_frame_thickness_mm=3,rack_side_frame_front_post_depth_mm=6,rack_side_frame_rear_post_depth_mm=7,
         rack_side_frame_windowed=True)
add('suporte_gavetas_removivel',rack,'#b5a78c','rack')

# Nominal slide reference; adjust these three dimensions to the measured item.
SLIDE_LENGTH=76
SLIDE_WIDTH=26
SLIDE_THICKNESS=1
SLIDE_X=(120-SLIDE_LENGTH)/2
SLIDE_Y=38
SLIDE_FIT_CLEARANCE=.4
SLIDE_POCKET_DEPTH=.6
P.update(slide_length=SLIDE_LENGTH,slide_width=SLIDE_WIDTH,slide_reference_thickness_mm=SLIDE_THICKNESS,
         slide_dimensions_status='standard 76x26; also checked for 75x25, thickness 0.9 to 1.2 mm',
         slide_height=SLIDE_THICKNESS,slide_pocket_depth_mm=SLIDE_POCKET_DEPTH,
         slide_retention='open shallow lower pocket; no upper clips',
         slide_fit_clearance_mm=SLIDE_FIT_CLEARANCE,slide_clip_top_overlap_mm=0,
         slide_can_be_lifted_straight_up=True,slide_retention_physical_test='pending')
tray_slides=[]
for i,z in enumerate([43,72,101],1):
    tray=box(TRAY_WIDTH,P['tray_depth'],TRAY_THICKNESS,TRAY_X,8,z).edges('|Z').fillet(3)
    tray=tray.cut(box(62,38,5,29,24,z-1).edges('|Z').fillet(5))
    # The pull bar stays inside the C rails rather than crossing their upper lip.
    tray=tray.union(box(90,3,6,15,8,z+TRAY_THICKNESS))
    tray_top=z+TRAY_THICKNESS
    # A shallow recess supports only the underside and bounds the edges.
    # The entire slide footprint remains open upward: no clip, ledge or flexure.
    pocket=box(SLIDE_LENGTH+.8,SLIDE_WIDTH+.8,2,
               SLIDE_X-.4,SLIDE_Y-.4,tray_top-SLIDE_POCKET_DEPTH).edges('|Z').fillet(.5)
    tray=tray.cut(pocket)
    slide=box(SLIDE_LENGTH,SLIDE_WIDTH,SLIDE_THICKNESS,
              SLIDE_X,SLIDE_Y,tray_top-SLIDE_POCKET_DEPTH)
    assert tray.val().isValid() and len(tray.solids().vals())==1,'Tray disconnected'
    assert independent(tray).intersect(slide).val().Volume()<1e-5,'Slide clashes with lower pocket'
    tray_slides.append((i,tray,slide))
    assert abs(tray.val().BoundingBox().ymax-P['tray_rear_y'])<1e-6
    assert P['heater_front_y']-tray.val().BoundingBox().ymax>=26
    assert independent(body).intersect(tray).val().Volume()<1e-5, 'Tray interferes with body'
    assert independent(rack).intersect(tray).val().Volume()<1e-5, 'Tray interferes with removable rails/stops'
    add(f'bandeja_{i}',tray,'#e6a454','tray')
    add(f'uslide_referencia_{i}',slide,'#81c6bf','reference')
pan=box(90,70,18,15,22,8).edges('|Z').fillet(7).cut(box(84,64,22,18,25,11).edges().fillet(4))
add('reservatorio_agua',pan,'#6eadd8')
# Integral CO2 roof, with only the existing sensor aperture.
def dshape(radius,flat,z,height,corner=4):
    shape=cq.Workplane('XY',origin=(0,cy,z)).circle(radius).extrude(height)
    shape=shape.intersect(box(radius+flat+1,2*radius+2,height+2,-radius-1,cy-radius-1,z-1))
    return shape.edges('|Z').fillet(corner).translate((-10,0,0))
collar=lateral_envelope(46,96.5,102,9).cut(printable_gas_cavity(42,94,101,11))
sensor_hole=cq.Workplane('XY',origin=(-27,cy,mh-1)).circle(P['sensor_mount_clearance_diameter']/2).extrude(10)
mixer_roof=lateral_envelope(46,96.5,mh+1,6).cut(sensor_hole)
body=body.union(collar).union(mixer_roof)
P.update(latch_integral_thread=True,mixer_integral_threads=0,mixer_roof_integrated=True,
         mixer_roof_bottom_z=111,mixer_roof_top_z=117,mixer_sensor_aperture_diameter=20.4)
assert independent(body).intersect(sensor_hole).val().Volume()<1e-5, 'Integral sensor aperture blocked'
# Legacy door insulation: orientation review remains deferred for the door.
# Body insulation below uses a separate rear-down layout.
air_cells=[]
def cell(x,y,z,sx,sy,sz):
    c=box(sx,sy,sz,x,y,z)
    bevel=min(sx/2-0.2,sz/2-0.2,2.8)
    return c.edges('|Y and >Z').chamfer(bevel)
def cellular_block(x,y,z,sx,sy,sz,orientation='wall'):
    outer=box(sx,sy,sz,x,y,z)
    holes=[]
    # Cells have at least 2 mm skins and 2 mm separating ribs.
    for ax in range(2,int(sx)-3,8):
        for ay in range(2,int(sy)-3,20):
            for az in range(2,int(sz)-3,22):
                dx=min(6,sx-ax-2);dy=min(18,sy-ay-2);dz=min(20,sz-az-2)
                if min(dx,dy,dz)<2:continue
                holes.append(cell(x+ax,y+ay,z+az,dx,dy,dz).val())
    void=cq.Workplane(obj=cq.Compound.makeCompound(holes))
    air_cells.extend(holes)
    return outer.cut(void)
# Rear-down insulation: long cavities, 2 mm skins/ribs and 45-degree roofs.
# Build direction is -Y. Each void closes across its 6 mm THIN dimension,
# never across its long dimension. The final nominal bridge is only 0.4 mm.
body_air_cells=[]
body_insulation_layout=[]
def rear_down_insulation(name,x,y,z,sx,sy,sz,thin_axis):
    envelope=box(sx,sy,sz,x,y,z)
    holes=[]
    if thin_axis=='X':
        spans=[(2,sz/2-1),(sz/2+1,sz-2)]
        dimensions=[(x+2,y+2,z+lo,sx-4,sy-4,hi-lo) for lo,hi in spans]
    elif thin_axis=='Z':
        spans=[(2,sx/2-1),(sx/2+1,sx-2)]
        dimensions=[(x+lo,y+2,z+2,hi-lo,sy-4,sz-4) for lo,hi in spans]
    else:
        # The rear gap has only 6 mm in the build direction: broad cavities
        # cannot close at 45 degrees here. Use long narrow X channels instead.
        dimensions=[(x+offset,y+2,z+2,min(6,sx-offset-2),sy-4,sz-4)
                    for offset in range(2,int(sx)-3,8)]
    for cx,cy,cz,dx,dy,dz in dimensions:
        closing_axis='Z' if thin_axis=='Z' else 'X'
        width=dz if closing_axis=='Z' else dx
        bevel=(width-.4)/2
        assert bevel>0 and bevel<dy, 'Insulation roof cannot close within cavity'
        edges='|X and <Y' if closing_axis=='Z' else '|Z and <Y'
        void=box(dx,dy,dz,cx,cy,cz).edges(edges).chamfer(bevel)
        assert void.val().isValid() and len(void.solids().vals())==1
        holes.append(void.val())
        body_air_cells.append(void.val())
        body_insulation_layout.append(dict(wall=name,bounds=[cx,cy,cz,dx,dy,dz],
            closing_axis=closing_axis,roof_start_y=cy+bevel,roof_end_y=cy,
            roof_angle_deg=45,closure_bridge_mm=.4,skin_mm=2))
    return envelope.cut(cq.Compound.makeCompound(holes))
body=body.union(rear_down_insulation('right',120,0,-10,10,125,160,'X'))
body=body.union(rear_down_insulation('rear',0,115,-10,120,10,160,'Y'))
body=body.union(rear_down_insulation('top',0,0,140,120,115,10,'Z'))
body=body.union(rear_down_insulation('bottom',0,0,-10,120,115,10,'Z'))
left=rear_down_insulation('left',-10,0,-10,10,125,160,'X')
body=body.union(left)
P.update(body_insulation_layout='long cavities with 45-degree closure toward -Y',
         body_insulation_cavity_count=len(body_air_cells),body_insulation_skin_mm=2,
         body_insulation_partition_mm=2,body_insulation_closure_bridge_mm=.4,
         body_insulation_roof_angle_deg=45,body_insulation_rear_channel_max_width_mm=6,
         body_insulation_transverse_partitions_per_side=1,
         body_insulation_transverse_partitions_per_top_bottom=1,
         body_insulation_rear_transverse_partitions=0,
         print_orientation_review='rear-down insulation and gas roofs adapted; full slicing and physical PC test pending')
(OUT/'body_insulation_layout.json').write_text(json.dumps(body_insulation_layout,indent=2))
# Flat front caps close the four corners while retaining the void behind them.
P['front_corner_cap_depth']=3
for xx,zz in [(0,0),(w-10,0),(0,h-10),(w-10,h-10)]:
    cap=box(10,P['front_corner_cap_depth'],10,xx,0,zz).cut(cavity)
    body=body.union(cap)
body=body.cut(ring)
for xx,zz in [(0.5,0.5),(w-.5,.5),(.5,h-.5),(w-.5,h-.5)]:
    for yy in [.2,1.5,2.8]:
        assert body.val().isInside((xx,yy,zz)), 'Front corner cap missing'
    assert not body.val().isInside((xx,12,zz)), 'Corner air void filled'
P['closed_corner_channels']=4
# Solid sleeve through the insulation prevents gas entering the air cells.
sleeve=cq.Workplane('YZ',origin=(-10,cy,34)).circle(6).extrude(14)
body=body.union(sleeve).cut(passage)
# Sample the air layer at bottom, middle and top opposite the mixer.
for zprobe in [20,60,135]:
    assert not body.val().isInside((-5,30,zprobe)), 'Left air layer obstructed'
# Split TPU seals: heater wires measured 1.68 mm; sensor wires measured 1.36 mm.
# Heater channels 1.60 mm are an initial interference fit, requiring TPU testing.
P.update(sensor_wire_diameter=1.36,sensor_seal_channel_diameter=1.30,heater_wire_diameter=1.68,heater_seal_channel_diameter=1.6)
def cable_port(name,origin,rear,wire_diameter,positions):
    global body
    def place(obj):
        if rear=='side':return obj.rotate((0,0,0),(0,1,0),-90).translate(origin)
        if rear:obj=obj.rotate((0,0,0),(1,0,0),-90)
        return obj.translate(origin)
    sleeve=cq.Workplane('XY').circle(8).extrude(14)
    aperture=cq.Workplane('XY',origin=(0,0,-2)).circle(6).extrude(24)
    body=body.union(place(sleeve)).cut(place(aperture))
    rubber=cq.Workplane('XY').circle(6.1).extrude(14)
    rubber=rubber.union(cq.Workplane('XY',origin=(0,0,14)).circle(8 if name=='sensor' else 10).extrude(2))
    rubber=rubber.union(cq.Solid.makeCone(6.1,7,1.5,cq.Vector(0,0,-1.5)))
    for yy in positions:
        rubber=rubber.cut(cq.Workplane('XY',origin=(0,yy,-2)).circle(wire_diameter/2).extrude(20))
    if rear:
        add(f'TPU_passagem_{name}',place(rubber),'#45ae89')
        return
    keeper=box(34,26,3,-17,-13,15.6).cut(box(4,10,5,-2,-5,15))
    for xx in [-13,13]:
        for yy in [-8,8]:
            post=cq.Workplane('XY',origin=(xx,yy,6)).circle(3.5).extrude(9.6)
            bore=cq.Workplane('XY',origin=(xx,yy,8)).circle(1.7).extrude(P['inlet_socket_depth']+1)
            nut=cq.Workplane('XY',origin=(xx,yy,12.6)).polygon(6,6.4).extrude(3.1)
            body=body.union(place(post)).cut(place(bore)).cut(place(nut))
            keeper=keeper.cut(bore)
    # Each split face passes through wire axes; wires can be removed laterally.
    for side,xx in [('A',-30),('B',0)]:
        half=box(30,60,30,xx,-30,-3)
        add(f'TPU_passagem_{name}_{side}',place(rubber.intersect(half)),'#45ae89')
        add(f'prensa_passagem_{name}_{side}',place(keeper.intersect(half)),'#729daf')
    assert independent(body).intersect(place(aperture)).val().Volume()<1e-5,'Cable route blocked'
    assert len(body.solids().vals())==1,'Cable-port bosses disconnected'
cable_port('sensor',(4,90,127.5),'side',P['sensor_seal_channel_diameter'],[-2.8,0,2.8])
cable_port('aquecedor',(60,111,116),True,P['heater_seal_channel_diameter'],[-2.5,2.5])
# Position references only: exact module mount and heater support pending dimensions.
add('sensor_temperatura_umidade_referencia',box(7,20,15,8,80,119.7),'#d8d8ce','reference')
add('chapa_aquecedor_referencia',box(33,1,90,43.5,106,18),'#9ca6b0','reference')
add('pelicula_aquecedora_90x33_referencia',box(33,.3,90,43.5,107,18),'#d1a047','reference')

# Compact dry compartment in the same lateral strip as the mixer, below its flange.
# Rear face stays at Y125; side face stays at X-56.
P.update(pcb_length=43.12,pcb_width=25.16,electronics_internal_width=41,
         electronics_internal_depth=22.5,electronics_internal_height=90)
case=box(49,34,95,-59,94,5)
case=case.cut(box(41,34,90,-53.5,96.5,7.5))
case=case.cut(box(49,6,95,-59,122,5))
case=case.cut(box(41,9,3,-53.5,119,97.5))
# PCB raised above the lower RJ45 zone; component depth remains provisional.
P.update(pcb_bottom_z=52,pcb_top_z=95.12,rj_center_z=32,rj_clearance_bottom_z=18.5,rj_clearance_top_z=45.5)
case=case.union(box(29.16,3,47.12,-49,96.5,50))
for xx in [-49,-21.84]:case=case.union(box(2,7,47.12,xx,96.5,50))
# Side rails retain PCB edges; the centre below the board stays open for connectors.
for zz in [59,85]:
    case=case.cut(box(2,10,4,-47,95,zz)).cut(box(2,10,4,-23.84,95,zz))
pcb=box(25.16,1.6,43.12,-47,99.5,P['pcb_bottom_z'])
# Rear panel is part of a single upward-removable service cover.
cover=box(47.6,2.4,95,-58.3,122.6,5)
cover=cover.union(box(3,3.6,84,-36,119.2,12))
# Keep the fixed rear inlet clear when the service cover is assembled or lifted.
cover=cover.cut(box(10.8,9,11.1,-28.4,118,4.8))
service_guides=[]
for xx in [-54,-14]:
    guide=box(1.6,1.9,80,xx+.2,120.9,10)
    cover=cover.union(guide)
    service_guides.append(box(2.4,1.9,91,xx-.2,120.5,9.8))
# Keystone directly in side wall; local panel thickness 1.6 mm.
rjopening=box(10,P['rj_cutout_width'],P['rj_cutout_height'],-62,108.5-P['rj_cutout_width']/2,P['rj_center_z']-P['rj_cutout_height']/2)
rjrelief=box(6,23,27,-57.4,97,P['rj_clearance_bottom_z'])
# Small independent fit sample replicates aperture and wall thickness.
rjplate=box(1.6,27,31,-56,95,P['rj_center_z']-15.5).cut(rjopening)
# Extend the electronics into the existing upper dry hood, below Z150.
# Preserve the blind cover-tab roof sockets farther back at Y112.35.
electronics_roof_opening=box(31.5,14,6,-50,96.5,97.5)
case=case.cut(electronics_roof_opening)
P.update(pcb_connector_clearance_above=10,pcb_connector_clearance_below=10,
         pcb_connector_space_bottom_z=42,pcb_connector_space_top_z=105.12,
         electronics_roof_opening_top_z=103.5,
         electronics_connector_aperture_width=15,electronics_connector_aperture_depth=10,
         electronics_connector_aperture_center=[-34.5,104.5],electronics_closed_roof_bottom_z=108)
# Close the previous wide opening above the connector clearance, under the hood.
# Rear and side walls connect the raised dry roof to the existing enclosure.
for wall in [box(2,14,10.5,-50,96.5,97.5),box(2,14,10.5,-20.5,96.5,97.5),
             box(31.5,2,10.5,-50,96.5,97.5),box(31.5,1,10.5,-50,109.5,97.5)]:
    case=case.union(wall)
connector_aperture=box(15,10,12,-42,99.5,107)
electronics_roof=box(31.5,14,2.5,-50,96.5,108).cut(connector_aperture)
case=case.union(electronics_roof)
# Provisional connector envelopes cover the board width and 10 mm component depth.
connector_spaces=[box(25.16,10,10,-47,99.5,z) for z in [42,95.12]]
# The external rounded skin is already the gas shell; no separate fairing.
P.update(lateral_front_radius=49,lateral_front_center=[-10,60],lateral_base_z=-10,
         lateral_feet_count=0,lateral_support_type='continuous hollow enclosure',
         service_cover_inlet_slot_width=10.8,service_cover_inlet_slot_top_z=15.9,
         lateral_curved_wall_thickness=4,lateral_cover_seat_reinforced_band_z=[97.5,102])
# Continuous hollow rear plinth meets the existing electronics floor.
lower_case=box(49,31,17.5,-59,94,-10)
lower_case=lower_case.cut(box(41,26,16,-53.5,96.5,-7.5))
lower_case=lower_case.cut(box(50,3.1,4,-59.5,121.9,4.8))
case=case.union(lower_case)
body=body.union(case).cut(inlet_bore).cut(inlet_socket_clearance).cut(connector_aperture)
# Clear only the dry outer flange lip; the CO2 cavity and gasket land are untouched.
upper_connector_space=connector_spaces[1]
assert independent(upper_connector_space).intersect(inner).val().Volume()<1e-5, 'Connector recess reaches gas cavity'
body=body.cut(upper_connector_space)
for guide in service_guides:body=body.cut(guide)
sensor_side_aperture=cq.Workplane('YZ',origin=(-18,90,127.5)).circle(6).extrude(24)
body=body.cut(sensor_side_aperture)
assert independent(body).intersect(sensor_side_aperture).val().Volume()<1e-5,'Sensor wire route blocked'
for name,obj,_,_ in parts:
    if name=='sensor_temperatura_umidade_referencia':
        assert independent(body).intersect(obj).val().Volume()<1e-5,'Temperature sensor intersects enclosure'
assert 90+10 < d-t,'Sensor grommet reaches rear wall'
assert body.val().isValid(),'Invalid side-skin union'
body=body.cut(rjopening).cut(rjrelief)
assert body.val().isValid(),'Invalid integrated keystone opening'
assert independent(body).intersect(rjopening).val().Volume()<1e-5,'Keystone aperture blocked'
assert independent(body).intersect(inlet_bore).val().Volume()<1e-6, 'Side inlet obstructed by fairing'
assert independent(body).intersect(inlet_socket_clearance).val().Volume()<1e-6, 'Hose socket obstructed by fairing'
assert independent(gas_shell).intersect(inner).val().Volume()<1e-5, 'Unified gas wall obstructs chamber'
assert body.val().isInside((-57,60,50)), 'Single gas wall missing'
assert not body.val().isInside((-50,60,50)), 'Duplicate inner gas wall remains'
assert len(body.solids().vals())==1,'Electronics must be integral to the main body'
for name,obj,color,kind in [('placa_eletronica_referencia',pcb,'#458bb0','reference')]:
    assert len(obj.solids().vals())==1,name
    add(name,obj,color,kind)
assert independent(body).intersect(pcb).val().Volume()<1e-5,'Integrated housing interferes with PCB'
for connector_space in connector_spaces:
    connector_clash=independent(body).intersect(connector_space).val()
    assert connector_clash.Volume()<1e-5, f'Connector space obstructed by body: z={connector_space.val().BoundingBox().zmin}, volume={connector_clash.Volume()}, bounds={connector_clash.BoundingBox().__dict__}'
assert independent(body).intersect(cover).val().Volume()<1e-5,'Electronics lid interferes'

# Enlarged dry wiring pod: depth unchanged, pins replaced by two blind M4 mounts.
POD_WIDTH,POD_HEIGHT,POD_DEPTH=70,60,21
POD_SCREW_LENGTH=12
pod_x=60-POD_WIDTH/2;pod_z=116-POD_HEIGHT/2
# Short 4 mm engagement: the tall pod floor limits screw penetration.
pod_web=POD_SCREW_LENGTH-4
assert 3<=pod_web<=POD_DEPTH-5,'Invalid pod screw length / web'
pod_seat_y=125+pod_web
# Contact-side top/bottom edges stay square; round only the exposed rear edges.
power_box=box(POD_WIDTH,POD_DEPTH,POD_HEIGHT,pod_x,125,pod_z).edges('|X and >Y').fillet(4)
pod_cavity=box(POD_WIDTH-5,21,POD_HEIGHT-5,pod_x+2.5,122.5,pod_z+2.5).edges('|X').fillet(1.5)
power_box=power_box.cut(pod_cavity)
# Preserve the connector height, depth and side facing right from behind.
power_hole=cq.Workplane('YZ',origin=(pod_x-1,135.5,116)).circle(4).extrude(6)
power_box=power_box.cut(power_hole)
pod_mounts=[(pod_x+7,pod_z+7),(pod_x+POD_WIDTH-7,pod_z+POD_HEIGHT-7)]
pod_pilots=[];pod_pads=[];pod_screws=[]
warm_wall_before_pod=body.intersect(box(112,4,132,4,111,4))
for i,(cx,cz) in enumerate(pod_mounts,1):
    # Fill the insulation locally; bore stops in this solid pad, behind warm wall.
    pad=cq.Workplane('XZ',origin=(cx,125,cz)).circle(8).extrude(10)
    pilot=cq.Workplane('XZ',origin=(cx,125.1,cz)).circle(1.75).extrude(4.5)
    body=body.union(pad).cut(pilot)
    pod_pilots.append(pilot);pod_pads.append(pad)
    tower=cq.Workplane('XZ',origin=(cx,146,cz)).circle(7).extrude(21)
    shaft_hole=cq.Workplane('XZ',origin=(cx,pod_seat_y+.1,cz)).circle(2.2).extrude(pod_web+.2)
    head_access=cq.Workplane('XZ',origin=(cx,146.1,cz)).circle(4.5).extrude(146.1-pod_seat_y)
    power_box=power_box.union(tower).cut(shaft_hole).cut(head_access)
    # Plain hardware reference. Real M4 thread crests engage plastic deliberately.
    screw=cq.Workplane('XZ',origin=(cx,pod_seat_y,cz)).circle(2).extrude(POD_SCREW_LENGTH)
    head=cq.Workplane('XZ',origin=(cx,pod_seat_y,cz)).circle(3.5).extrude(-4)
    screw=screw.union(head)
    name=f'parafuso_M4x{POD_SCREW_LENGTH}_caixinha_aquecedor_{i}'
    add(name,screw,'#505965','hardware')
    clash_envelopes[name]=cq.Workplane('XZ',origin=(cx,pod_seat_y,cz)).circle(1.7).extrude(POD_SCREW_LENGTH).union(head)
    pod_screws.append(screw)
    assert independent(power_box).intersect(screw).val().Volume()<1e-5,'Pod screw cannot enter access bore'
    assert pilot.val().BoundingBox().ymin>115,'Pod pilot reaches warm chamber wall'
    assert abs(screw.val().BoundingBox().ymin-121)<1e-5,'Pod screw length reaches warm wall'
for (cx,cz),pilot in zip(pod_mounts,pod_pilots):
    floor=cq.Workplane('XZ',origin=(cx,120.6,cz)).circle(8).extrude(5.6)
    surround=cq.Workplane('XZ',origin=(cx,125,cz)).circle(8).circle(1.75).extrude(4.4)
    assert independent(floor).cut(body).val().Volume()<1e-5,'Pod pilot floor is not solid'
    assert independent(surround).cut(body).val().Volume()<1e-5,'Pod pilot side stock missing'
assert len(power_box.solids().vals())==1,'Power pod disconnected'
assert independent(body).intersect(power_box).val().Volume()<1e-5,'Power pod interferes'
assert independent(power_box).intersect(power_hole).val().Volume()<1e-5,'Jack aperture blocked'
# Validate a continuous removal corridor and the uninterrupted wall under mounts.
for dy in [0,.5,1,3,8,15,25]:
    assert independent(body).intersect(power_box.translate((0,dy,0))).val().Volume()<1e-5,'Pod removal blocked'
assert independent(warm_wall_before_pod).cut(body).val().Volume()<1e-5,'Blind pod mounts remove warm-wall material'
for name,obj,_,_ in parts:
    if name=='TPU_passagem_aquecedor':
        assert independent(power_box).intersect(obj).val().Volume()<1e-5,'Pod touches heater TPU seal'
P.update(power_connector_hole_diameter=8,power_connector_axis='-X, right when viewed from rear',
         power_pod_outer_size=[POD_WIDTH,POD_HEIGHT,POD_DEPTH],
         power_pod_inner_envelope=[POD_WIDTH-5,POD_HEIGHT-5,18.5],
         power_pod_contact_edge_radius=0,power_pod_exposed_rear_edge_radius=4,
         power_pod_pin_count=0,power_pod_screw=f'M4x{POD_SCREW_LENGTH}',power_pod_screw_count=2,
         power_pod_mount_centres=pod_mounts,power_pod_screw_web=pod_web,
         power_pod_screw_access_diameter=9,power_pod_clearance_diameter=4.4,
         power_pod_pilot_diameter=3.5,power_pod_pilot_depth=4.4,
         power_pod_pilot_min_y=120.6,power_pod_screw_tip_y=121,
         power_pod_pilot_solid_pad_diameter=16,power_pod_pilot_solid_pad_depth=10,
         power_pod_pilot_solid_floor=5.6,power_pod_pilot_side_stock=6.25,
         power_pod_pilot_to_chamber_inner_plane=9.6,power_pod_screw_engagement=4,
         power_pod_continuous_chamber_wall=4,power_pod_mount_wall_barrier_checked=True,
         power_pod_removal_lifts_mm=[0,.5,1,3,8,15,25])
add('caixinha_encaixe_aquecedor',power_box,'#c5d4df')
# No new hole through the warm wall: sealed heater-wire feedthrough already exists.
hose_approach=cq.Workplane('XZ',origin=(-23,125.1,10.5)).circle(5).extrude(-30)
assert independent(body).intersect(hose_approach).val().Volume()<1e-5,'External hose approach obstructed'
assert abs(inlet.val().BoundingBox().ymax-125)<1e-5
assert inlet.val().BoundingBox().zmin>=-10
# One lift-off service cover: upper dry cap and rear electronics access panel.
# The integral CO2 roof remains fixed while the dry service hood lifts off.
hood=lateral_envelope(49,125,102.3,47.7)
hood=hood.cut(lateral_envelope(46.25,122.25,100,47,0))
hood=hood.union(box(41,13.5,2.3,-56.5,111.5,100)).union(cover)
# Overlapping skirt hides the horizontal seam; clearance stays inside the joint.
skirt=lateral_envelope(49,125,98,5)
skirt=skirt.cut(lateral_envelope(47.8,123.8,97,7,0))
seat=lateral_envelope(49.4,125.4,97.7,4.7)
seat=seat.cut(lateral_envelope(47.3,123.3,97,6,0))
body=body.cut(seat)
hood=hood.union(skirt)

# One lower rear M4 screw, directly into plastic; no nut or upper bracket.
# The local cover pad projects inward only; the screw head is recessed.
service_z=10.5
P.update(service_cover_pin_count=0,service_cover_screw_count=1,
         service_cover_screw='M4x12',service_cover_screw_axis='-Y, lower rear access',
         service_cover_screw_center=[-34.5,120.8,service_z],
         service_cover_clearance_diameter=4.4,service_cover_pilot_diameter=3.5,
         service_cover_pilot_depth=9.9,service_cover_skirt_clearance=.4,
         service_cover_rear_side_clearance=.7,
         service_cover_head_recess_diameter=8.5,service_cover_head_recess_depth=4.2,
         service_cover_lower_mount_center_z=service_z)
body=body.union(box(49,4,3,-59,121,2))
# Small blind support grows from the electronics floor, below the PCB.
service_boss=box(13,10.4,service_z+1,-41,108,5)
service_bore=cq.Workplane('XZ',origin=(-34.5,118.5,service_z)).circle(1.75).extrude(10)
service_boss=service_boss.cut(service_bore)
body=body.union(service_boss)
# Keep the pad behind Y119.4 so it clears the roof during upward removal.
service_cover_pad=cq.Workplane('XZ',origin=(-34.5,122.8,service_z)).circle(6).extrude(3.4)
# Flat underside retains the original lower edge of the cover.
service_cover_pad=service_cover_pad.intersect(box(13,8,20,-41,118,5.4))
# A small local pocket in the rear floor lets the pad sit close to the base.
service_floor_seat=cq.Workplane('XZ',origin=(-34.5,125.1,service_z)).circle(6.4).extrude(6.1)
service_floor_seat=service_floor_seat.intersect(box(14,8,20,-41.5,118,5))
body=body.cut(service_floor_seat)
hood=hood.union(service_cover_pad)
service_cover_hole=cq.Workplane('XZ',origin=(-34.5,125.1,service_z)).circle(2.2).extrude(6.4)
service_head_recess=cq.Workplane('XZ',origin=(-34.5,125.1,service_z)).circle(4.25).extrude(4.3)
hood=hood.cut(service_cover_hole).cut(service_head_recess)
# Hardware reference only: actual M4 thread crests engage the plastic pilot.
service_screw=cq.Workplane('XZ',origin=(-34.5,120.8,service_z)).circle(2).extrude(12)
service_screw=service_screw.union(cq.Workplane('XZ',origin=(-34.5,120.8,service_z)).circle(3.5).extrude(-2.5))
add('parafuso_M4x12_tampa_manutencao_eletronica',service_screw,'#505965','hardware')
service_screw_root=cq.Workplane('XZ',origin=(-34.5,120.8,service_z)).circle(1.65).extrude(12)
service_screw_root=service_screw_root.union(cq.Workplane('XZ',origin=(-34.5,120.8,service_z)).circle(3.5).extrude(-2.5))
clash_envelopes['parafuso_M4x12_tampa_manutencao_eletronica']=service_screw_root
assert service_screw.val().BoundingBox().ymax<125, 'Service screw head protrudes'
assert independent(service_boss).intersect(pcb).val().Volume()<1e-5,'Service boss touches PCB'
assert rjrelief.val().BoundingBox().zmin > service_boss.val().BoundingBox().zmax, 'RJ45 below screw support'
assert rjrelief.val().BoundingBox().zmax < pcb.val().BoundingBox().zmin, 'RJ45 reaches PCB'
assert independent(body).intersect(rjrelief).val().Volume()<1e-5, 'RJ45 insertion relief blocked'
assert independent(body).intersect(hood).val().Volume()<1e-5,'Service cover interferes'
assert independent(service_boss).intersect(inner).val().Volume()<1e-5,'Service fastener reaches gas cavity'
assert body.val().isInside((-34.5,108.25,service_z)), 'Blind screw bore bottom missing'
# Two broad locating tongues seat vertically in blind sockets in the dry roof.
# They carry alignment loads; the existing lower screw retains the cover.
P.update(service_cover_tab_count=2,service_cover_tab_width=8,
         service_cover_tab_depth=3.5,service_cover_tab_height=1.5,
         service_cover_tab_side_clearance=.4,service_cover_tab_bottom_clearance=.2,
         service_cover_tab_centers=[[-45,114.5],[-23,114.5]])
for tab_x in [-45,-23]:
    tab_socket=box(8.8,4.3,1.9,tab_x-4.4,112.35,98.3)
    tab=box(8,3.5,1.5,tab_x-4,112.75,98.5).edges('<Z').chamfer(.4)
    body=body.cut(tab_socket)
    hood=hood.union(tab)
    assert independent(tab_socket).intersect(inner).val().Volume()<1e-5,'Cover tab reaches gas cavity'
    assert independent(tab_socket).intersect(rjrelief).val().Volume()<1e-5,'Cover tab alters RJ45 clearance'
    assert body.val().isInside((tab_x,114.5,98.1)), 'Cover socket bottom missing'
assert independent(body).intersect(hood).val().Volume()<1e-5,'Locating tabs interfere'
# Integral mixer threads eliminate lateral nut-loading channels.
# An open-bottom rear notch lets the cover lift past the fixed inlet.
inlet_cover_slot=box(10.8,9,11.1,-28.4,118,4.8)
hood=hood.cut(inlet_cover_slot)
add('tampa_manutencao_CO2_eletronica',hood,'#c5d4df','hood')
assert len(hood.solids().vals())==1,'Service cover must be one printed part'
for connector_space in connector_spaces:
    assert independent(hood).intersect(connector_space).val().Volume()<1e-5, 'Connector space obstructed by hood'
assert independent(body).intersect(connector_aperture).val().Volume()<1e-5, 'Rectangular connector aperture blocked'
assert P['pcb_connector_space_top_z'] < h+10, 'Electronics exceeds incubator top'
assert hood.val().BoundingBox().zmax <= h+10, 'Hood exceeds incubator top'
assert independent(connector_aperture).intersect(inner).val().Volume()<1e-5, 'Connector aperture reaches gas chamber'
# Check only the changed cover: remove the screw before lifting vertically.
for lift in [0,.5,2,5,12,25,50,90,110]:
    assert independent(body).intersect(hood.translate((0,0,lift))).val().Volume()<1e-5, f'Service cover removal blocked at {lift} mm'
# Other assembly movement tests remain deferred.
# Continuous rounded support reaches the incubator base; separate feet removed.
body=body.cut(inlet_bore).cut(inlet_socket_clearance)
assert independent(body).intersect(inlet_bore).val().Volume()<1e-6, 'Rear inlet route blocked'
assert independent(body).intersect(inlet_socket_clearance).val().Volume()<1e-6, 'Rear hose socket blocked'
assert len(body.solids().vals())==1,'Lateral base must join main body'
P['lateral_feet_count']=0
P['lateral_feet_base_z']=-10
for probe in [(-58,70,-9.9),(-50,100,-9.9),(-20,118,-9.9)]:
    assert body.val().isInside(probe), 'Continuous lateral support missing'
assert abs(body.val().BoundingBox().zmin+10)<1e-5, 'Support plane changed'
P['heater_voltage']=12
# Original cellular insulation retained behind the enlarged sealing panel.
# The outer bulge leaves the handle and compression areas exposed.
door_outer=box(w,10,h,0,-16,0).edges('|Y').fillet(8)
door_border=door_outer.cut(box(w-4,12,h-4,2,-17,2).edges('|Y').fillet(6))
door_insulation=cellular_block(0,-16,0,w,10,h).intersect(door_outer).union(door_border)
doorpart=doorpart.union(door_insulation)
assert len(doorpart.solids().vals())==1, 'Door must be one solid'
for xprobe in [5,21,101,117]:
    assert not doorpart.val().isInside((xprobe,-11,70)), 'Door air layer missing near side'
for zprobe in [4,135]:
    assert not doorpart.val().isInside((53,-11,zprobe)), 'Door air layer missing near top/bottom'
# Entire monolithic inner boss is tapered: flat tip, inclined perimeter on all sides.
# Existing sealing land survives outside inset 0; a recessed annulus clears
# the body's forward conical receiver without seams in the rigid door.
def boss_inset(y): return 4.95+.5*y
def receiver_inset(y): return 4+.4125*y
def inset_loft(stations):
    # Cone corner centres match chamber/inox at X/Z10, avoiding corner collisions.
    wires=[box(w-2*inset,1,h-2*inset,inset,y-1,inset).edges('|Y').fillet(10-inset).faces('>Y').val().outerWire() for y,inset in stations]
    return cq.Workplane(obj=cq.Solid.makeLoft(wires,ruled=True))
def inset_ring(outer,inner):
    return inset_loft(outer).cut(inset_loft(inner),clean=False)
relief=inset_ring([(-4.6,0),(-.9,0)],[(-4.6,6.9),(-.9,6.9)])
doorpart=doorpart.cut(relief)
BOSS_PROFILE=[(-4.6,boss_inset(-4.6)),(3,boss_inset(3))]
centering=inset_loft(BOSS_PROFILE)
doorpart=doorpart.union(centering)
# Receiver mouth remains wider than the unchanged 112 x 132 chamber opening.
RECEIVER_PROFILE=[(-3.7,receiver_inset(-3.7)),(0,receiver_inset(0)),(.2,4)]
receiver=inset_ring([(y,inset-1) for y,inset in RECEIVER_PROFILE],RECEIVER_PROFILE)
body=body.union(receiver)
# Dovetail retention follows the conical surface; two axial annular lips
# contact the inclined receiver. Free TPU shape intentionally overlaps receiver.
V_GROOVE=[(-3.7,.25),(-3.5,.85),(-3.0,.85),(-2.8,.25)]
V_FOOT=[(-3.6,.20),(-3.45,.7),(-3.05,.7),(-2.9,.2)]
v_channel=inset_ring([(y,boss_inset(y)-.8) for y,depth in V_GROOVE],
                     [(y,boss_inset(y)+depth) for y,depth in V_GROOVE])
doorpart=doorpart.cut(v_channel,clean=False)
v_seal=inset_ring([(y,boss_inset(y)-.25) for y,depth in V_FOOT],
                  [(y,boss_inset(y)+depth) for y,depth in V_FOOT])
V_LIPS=[ [(-3.4,.35),(-3.5,.75),(-3.65,.95)],
         [(-3.2,.35),(-2.6,.75),(-1.6,1.15)] ]
for stations in V_LIPS:
    lip=inset_ring([(y,boss_inset(y)-extension-.3) for y,extension in stations],
                   [(y,boss_inset(y)-extension+.3) for y,extension in stations])
    v_seal=v_seal.union(lip,clean=False)
assert len(doorpart.solids().vals())==1 and doorpart.val().isValid(),'Tapered monolithic door invalid'
assert len(v_seal.solids().vals())==1 and v_seal.val().isValid(),'V gasket disconnected'
assert independent(v_seal).intersect(doorpart).val().Volume()<1e-5,'V gasket foot collides with door'
P.update(door_rigid_piece_count=1,door_hatch_insert_snap_fit=False,
         door_hatch_inner_projection=3,door_boss_profile=BOSS_PROFILE,
         door_boss_side_angle_to_axis_deg=math.degrees(math.atan(.5)),
         door_receiver_profile=RECEIVER_PROFILE,door_receiver_wall=1,
         door_v_lip_wall=.6,door_v_tpu_retention='dovetail around tapered boss',
         door_body_gasket_preserved=True,door_print_orientation='deferred by user',
         door_hatch_extra_screws=0,door_v_seal_test='pending physical fit and leak test',
         rack_outer_width=109.8,rack_liner_side_clearance=.3)
add('junta_V_porta_TPU',v_seal,'#45ae89','door_seal')
add('porta_articulada',doorpart,'#729daf','door')
# Display-only cuts show actual cavities without exporting a second physical body.
assert body.val().isValid(),'Body invalid before section'
body_section=independent(body).cut(box(240,200,90,-80,-30,70))
door_section=doorpart.cut(box(220,180,90,-60,-30,70))
add('corte_corpo_referencia',body_section,'#c5d4df','section_body')
add('corte_porta_referencia',door_section,'#729daf','section_door')
add('corpo_integrado',body,'#c5d4df','shell')
# Free-shape TPU dimensions: 0.2 mm diametral interference against rigid hole.
# Lower tapered flange snaps below the 6 mm lid; upper flange supports collar.
def sensor_grommet(bore):
    q=cq.Workplane('XY',origin=(-27,cy,mh+1)).circle(10.3).extrude(6)
    q=q.union(cq.Workplane('XY',origin=(-27,cy,mh+7)).circle(12).extrude(1.5))
    q=q.union(cq.Solid.makeCone(10.3,11,1.5,cq.Vector(-27,cy,mh-0.5)))
    q=q.cut(cq.Workplane('XY',origin=(-27,cy,mh-1)).circle(bore/2).extrude(11))
    for zz,r1,r2 in [(mh-0.5,bore/2+0.5,bore/2),(mh+7.5,bore/2,bore/2+0.5)]:
        q=q.cut(cq.Solid.makeCone(r1,r2,1,cq.Vector(-27,cy,zz)))
    return q
sensor_seal=sensor_grommet(P['sensor_seal_bore'])
add('bucha_sensor_TPU',sensor_seal,'#45ae89','sensor_seal')
assert len(sensor_seal.solids().vals())==1
# The TPU neck intentionally compresses by 0.1 mm radially in the sensor bore.
sensor_neck_compression=cq.Workplane('XY',origin=(-27,cy,mh+1)).circle(10.31).extrude(6)
assert independent(body).intersect(independent(sensor_seal).cut(sensor_neck_compression)).val().Volume()<1e-5,'Sensor flange collides with integral roof'
sensor_shoulder=mh+8.5
sensor_tip=sensor_shoulder-P['sensor_insertion']
sensor_ref=cq.Workplane('XY',origin=(-27,cy,sensor_tip)).circle(P['sensor_diameter']/2).extrude(P['sensor_insertion'])
sensor_ref=sensor_ref.union(cq.Workplane('XY',origin=(-27,cy,sensor_shoulder)).circle(P['sensor_collar_diameter']/2).extrude(2.5))
# Collar height and head depth/height remain provisional visual references.
sensor_ref=sensor_ref.union(box(P['sensor_head_width'],25,25,-27-P['sensor_head_width']/2,cy-12.5,sensor_shoulder+2.5))
assert P['inlet_internal_exit_height'] < sensor_tip, 'Inlet must remain below sensor tip'
assert independent(body).intersect(sensor_ref).val().Volume()<1e-5, 'Sensor intersects mixer body'
assert independent(hood).intersect(sensor_ref).val().Volume()<1e-5,'Hood interferes with sensor'
add('sensor_referencia',sensor_ref,'#505965','sensor')
# Display-only indication of the real through-wall channel.
# The highlight is confined to the wall thickness, not a protruding tube.
passage_display=cq.Workplane('YZ',origin=(-10,cy,34)).circle(P['port_diameter']/2).extrude(14)
add('passagem_gas_referencia',passage_display,'#d47cac','channel')
assert len(body.solids().vals())==1, 'Integrated body must be one solid'
assert independent(body).intersect(passage).val().Volume()<1e-6, 'Gas passage obstructed'
print('Checking lining insertion and changed door',flush=True)
# Metal lining: thin shell, front open; penetrations align with existing ports.
liner_outer=box(111,110,131,4.5,0,4.5).edges('|Y').fillet(5.5)
liner_inner=box(110.4,110.7,130.4,4.8,-1,4.8).edges('|Y').fillet(5.2)
liner=liner_outer.cut(liner_inner)
liner=liner.cut(cq.Workplane('YZ',origin=(3,60,34)).circle(2.9).extrude(4))
liner=liner.cut(cq.Workplane('YZ',origin=(3,90,127.5)).circle(7).extrude(4))
liner=liner.cut(yhole(60,110,116,7,2))
add('revestimento_inox_referencia',liner,'#a6b2b6','reference')
assert independent(rack).intersect(liner).val().Volume()<1e-5,'Rack hits metal lining'
# Envelope covers all positions of the lining as it slides from the front.
insertion=box(111,260,131,4.5,-150,4.5).edges('|Y').fillet(5.5)
assert independent(body).intersect(insertion).val().Volume()<1e-5,'Front insertion envelope obstructed'
for angle in [0,.25,.5,1,2,3,5,7,10,12,15,18,20,25,30,45,60,75,90,110]:
    opened=doorpart.rotate((130,-6,0),(130,-6,1),angle)
    assert independent(body).intersect(opened).val().Volume()<1e-5,f'Changed door collision at {angle}'
    moved_ring=centering.rotate((130,-6,0),(130,-6,1),angle)
    assert independent(body).intersect(moved_ring).val().Volume()<1e-5,f'Hatch insert hits body at {angle}'
    assert independent(liner).intersect(opened).val().Volume()<1e-5,f'Monolithic door hits inox at {angle}'
# Parked 90-degree latch must clear the door from the first fraction of a degree.
LATCH_DOOR_ANGLES=[0,.1,.25,.5,1,2,3,5,7,10,12,15,18,20,25,30,45,60,75,90,110]
for z,dog in latches:
    parked=dog.rotate((-13,0,z),(-13,1,z),90).translate((0,-.8,0))
    assert parked.val().BoundingBox().xmax<=-5+1e-5,'Free latch still overhangs door edge'
    for angle in LATCH_DOOR_ANGLES:
        moved=doorpart.rotate((130,-6,0),(130,-6,1),angle)
        assert independent(moved).intersect(parked).val().Volume()<1e-5,f'Free latch blocks door at {angle}'
    for angle in range(0,91,5):
        released=dog.rotate((-13,0,z),(-13,1,z),angle).translate((0,-.8,0))
        for obstacle in [body,doorpart]:
            assert independent(obstacle).intersect(released).val().Volume()<1e-5,f'Latch release collision at {angle}'
P.update(latch_parked_angle=90,latch_parked_rightmost_x=-5,
         latch_closed_door_leftmost_x=-4,latch_parked_nominal_edge_clearance=1,
         latch_loosen_translation=.8,latch_free_door_angles_checked=LATCH_DOOR_ANGLES,
         latch_release_angles_checked=list(range(0,91,5)))
assert independent(opened).intersect(insertion).val().Volume()<1e-5,'Door obstructs lining insertion at 110 degrees'
P.update(liner_insertion_test='continuous swept envelope; door at 110 degrees; cable seals installed afterwards',
         changed_door_angles_checked=[0,.25,.5,1,2,3,5,7,10,12,15,18,20,25,30,45,60,75,90,110],
         liner_sensor_opening_diameter=14,liner_heater_opening_diameter=14,
         liner_co2_opening_diameter=5.8)
# Validate open guides and unobstructed placement from above.
print('Checking open drawer guides and lower-only slide pockets',flush=True)
tray_pull_positions=[0,5,15,30,50,72,80]
for i,tray,slide in tray_slides:
    for dx in [-.79,0,.79]:
        for lift in [0,.5,1]:
            assert independent(rack).intersect(tray.translate((dx,0,lift))).val().Volume()<1e-5, 'Open drawer guide binds'
    for dx in [-1.2,1.2]:
        assert independent(rack).intersect(tray.translate((dx,0,0))).val().Volume()>1, 'Drawer lateral stop missing'
    for pull in tray_pull_positions:
        moved=tray.translate((0,-pull,0))
        for obstacle in [rack,body,liner,opened]:
            assert independent(obstacle).intersect(moved).val().Volume()<1e-5, f'Drawer {i} extraction clash at {pull}'
    top=slide.val().BoundingBox().zmin
    for length,width in [(76,26),(75,25)]:
        for thickness in [.9,1,1.2]:
            sample_slide=box(length,width,thickness,(120-length)/2,SLIDE_Y,top)
            assert independent(tray).intersect(sample_slide).val().Volume()<1e-5, 'Standard slide does not fit pocket'
            # A continuous vertical envelope proves there is nothing above it.
            vertical_envelope=box(length,width,thickness+40,(120-length)/2,SLIDE_Y,top)
            assert independent(tray).intersect(vertical_envelope).val().Volume()<1e-5, 'Part overlaps slide from above'
            assert independent(tray).intersect(sample_slide.translate((0,0,-.1))).val().Volume()>1e-4, 'Slide lacks underside support'
            for vector in [(0,-2,0),(0,2,0),(-2,0,0),(2,0,0)]:
                assert independent(tray).intersect(sample_slide.translate(vector)).val().Volume()>1e-4, 'Pocket lacks edge stop'
P.update(tray_extraction_positions_checked_mm=tray_pull_positions,
         slide_supported_nominal_sizes_mm=[[76,26],[75,25]],
         slide_supported_thicknesses_checked_mm=[.9,1,1.2],
         slide_upper_clearance_continuous_sweep_mm=40,
         slide_retention_geometry_checked=True,tray_open_clearance_geometry_checked=True)
(OUT/'tray_retention_report.json').write_text(json.dumps(dict(
    version='v58',tray_count=3,drawer_extraction_positions_mm=tray_pull_positions,
    drawer_lateral_clearance_per_side_mm=.8,drawer_upper_guides=False,
    drawer_lateral_stops_checked=True,nominal_slide_sizes_mm=[[76,26],[75,25]],
    slide_thicknesses_checked_mm=[.9,1,1.2],slide_vertical_placement_envelope_mm=40,
    slide_no_upper_overlap=True,slide_bottom_support_and_edge_stops_checked=True,
    limitations=['Rigid geometric checks', 'Printed fit and strength require physical test',
                 'Open pockets do not retain slides against lifting or inversion']),indent=2))
# Inner forming mould is exported separately, never as a component of the assembly.
mould=box(110.4,109.7,130.4,4.8,0,4.8).edges('|Y').fillet(5.2)
assert mould.val().isValid()
cq.exporters.export(mould,str(OUT/'molde_caixa_inox_referencia.step'))
cq.exporters.export(liner,str(OUT/'revestimento_inox_referencia.step'))
# Reference STL for the mould, flat rear on bed.
mould_print=mould.rotate((0,0,0),(1,0,0),-90).translate((-4.8,-4.8,109.7))
cq.exporters.export(mould_print,str(OUT/'molde_caixa_inox_referencia.stl'))
if CHECK_MOVEMENTS:
    # Door sweep with dogs parked 90 degrees and loosened by 0.8 mm.
    print('Checking door sweep',flush=True)
    for angle in range(0,111,5):
        print(f'Checking door angle {angle}',flush=True)
        opened=doorpart.rotate((130,-6,0),(130,-6,1),angle)
        assert independent(body).intersect(opened).val().Volume()<1e-5, f'Door collision at {angle}'
        for z,dog in latches:
            parked=dog.rotate((-13,0,z),(-13,1,z),90).translate((0,-0.8,0))
            assert opened.intersect(parked).val().Volume()<1e-5, f'Latch collision at {angle}'
    # Check the full unlocking rotation, including the central handle clearance.
    for z,dog in latches:
        for angle in range(0,91,5):
            print(f'Checking latch angle {angle}',flush=True)
            moving=dog.rotate((-13,0,z),(-13,1,z),angle).translate((0,-0.8,0))
            for obstacle in (body,doorpart):
                assert independent(obstacle).intersect(moving).val().Volume()<1e-5, f'Latch unlocking collision at {angle}'
# Reapply threaded passages after all unions so insulation cannot obstruct them.
for index,cutter in enumerate(integral_thread_cuts,1):
    print(f'Creating integral thread {index}/{len(integral_thread_cuts)}',flush=True)
    body=body.cut(cutter,clean=False)
assert body.val().isValid(), 'Final body invalid after integral threads'
assert len(body.solids().vals())==1, 'Body must remain one connected solid'
# Audit the ACTUAL final ceiling faces inside the wall, after all mounting unions.
# Front face is -Y; ceilings inside a closed void face +Y (toward the bed).
internal_roof_regions=[('hinge_lower',box(5.998,18,7.998,122.001,2,26.751)),
                       ('hinge_upper',box(5.998,18,7.998,122.001,2,106.751)),
                       ('latch',box(5.998,18,19.998,-7.999,2,60.001))]
internal_roof_audit=[]
for name,region in internal_roof_regions:
    roof_count=0;flat_roof_area=0
    for face in body.val().Faces():
        if face.geomType()!='PLANE':continue
        normal=face.normalAt()
        if normal.y<.01:continue
        clipped_face=face.intersect(region.val())
        overlap=clipped_face.Area()
        if overlap<1e-5:continue
        roof_count+=1
        if normal.y>.99:
            # The existing insulation roof ends in a nominal 0.4 mm bridge.
            # Keep that tiny closure, reject the former broad mounting ledges.
            span=clipped_face.BoundingBox().xlen
            assert span<=.40001, f'Unsupported internal flat mounting roof: {name}, span {span}'
            flat_roof_area+=overlap
        else:
            assert normal.y<=1/math.sqrt(2)+1e-6, f'Unsupported internal mounting ramp: {name}'
    assert roof_count>0, f'Missing internal mounting ramp: {name}'
    internal_roof_audit.append(dict(region=name,ceiling_faces_checked=roof_count,flat_ceiling_area_mm2=flat_roof_area))
(OUT/'internal_mount_roof_report.json').write_text(json.dumps(dict(
    version='v58',build_direction='-Y',maximum_ceiling_angle_deg=45,
    actual_final_body_faces_checked=True,maximum_retained_bridge_mm=.4,regions=internal_roof_audit,
    limitation='CAD roof-face check; support generation must be checked in slicer preview'),indent=2))

P['body_solid_volume_mm3']=body.val().Volume()
P['service_cover_removal_lifts_mm']=[0,.5,2,5,12,25,50,90,110]
P['rear_plane_y']=125
assert abs(hood.val().BoundingBox().ymax-P['rear_plane_y'])<1e-5, 'Cover rear face must be flush at Y125'
assert abs(body.val().BoundingBox().ymax-125)<1e-5, 'Rear inlet must be flush at Y125'
# Envelopes check surrounding material; the matching helical receivers above
# are checked separately. Reliefs affect diagnostics only, never the exported CAD.
body_for_thread_envelopes=independent(body)
for index,relief in enumerate(integral_thread_reliefs,1):
    print(f'Preparing thread clearance {index}/{len(integral_thread_cuts)}',flush=True)
    body_for_thread_envelopes=body_for_thread_envelopes.cut(relief,clean=False)
thread_motion_checks=0
if CHECK_MOVEMENTS:
    # Screw-in motion: angle and axial travel obey each thread's pitch.
    # Reuse classifiers; rebuilding them for every probe is expensive for helices.
    def point_classifier(shape):
        classifier=BRepClass3d_SolidClassifier(shape.wrapped)
        def contains(point):
            classifier.Perform(gp_Pnt(*point),1e-6)
            return classifier.State()==TopAbs_IN
        return contains
    thread_motion_checks=0
    for male,female,pitch,travel in [(thread,printed_nut,2,6)]:
        inside_male=point_classifier(male.val())
        inside_female=point_classifier(female.val())
        diameter=male.val().BoundingBox().xlen
        female_bounds=female.val().BoundingBox()
        # OCCT can return a false empty common for translated periodic helices.
        # An interior witness in both solids confirms resistance to axial sliding.
        radius=diameter*.475
        zmid=female.val().Center().z
        phase=2*math.pi*(zmid+pitch/2)/pitch
        witness=(radius*math.cos(phase),radius*math.sin(phase),zmid)
        assert inside_male((witness[0],witness[1],zmid+pitch/2)), 'Engagement witness outside screw'
        assert inside_female(witness), 'Thread does not engage axially'
        for step in range(int(travel*4)+1):
            advance=-step/4
            print(f'Checking thread pitch {pitch}, axial position {advance}',flush=True)
            moving=male.rotate((0,0,0),(0,0,1),advance/pitch*360).translate((0,0,advance))
            assert independent(moving).intersect(independent(female)).val().Volume()<1e-4, 'Screw-in thread collision'
            # Crest and both flanks: transform probes back to the original screw.
            for fraction in [1/3,2/3]:
                zz=female_bounds.zmin+female_bounds.zlen*fraction
                if not 0.1<zz-advance<male.val().BoundingBox().zmax-.1:continue
                for offset,ratio in [(0,.475),(-math.pi/9,.43),(math.pi/9,.43)]:
                    theta=2*math.pi*zz/pitch+offset
                    rr=diameter*ratio
                    point=(rr*math.cos(theta),rr*math.sin(theta),zz)
                    source_theta=theta-advance/pitch*2*math.pi
                    source=(rr*math.cos(source_theta),rr*math.sin(source_theta),zz-advance)
                    assert inside_male(source), 'Thread crest/flank missing'
                    assert not inside_female(point), 'Thread flank interference'
            thread_motion_checks+=1
    # Pins enter from above; nuts are installed from below after insertion.
    for name,pin,_,kind in parts:
        if kind!='printed_pin':continue
        for lift in [0,.5,2,8,18,32]:
            print(f'Checking pin insertion {name}, lift {lift}',flush=True)
            shifted=clash_envelopes[name].translate((0,0,lift))
            for obstacle in (body,doorpart):
                assert independent(obstacle).intersect(shifted).val().Volume()<1e-5, 'Hinge pin insertion blocked'
# Replace the earlier display/export body with final latch passages.
parts=[(n,body if n=='corpo_integrado' else (independent(body).cut(box(240,200,90,-80,-30,70),clean=False) if n=='corte_corpo_referencia' else o),c,k) for n,o,c,k in parts]
for n,o,c,k in parts:
    if k in ('knob','printed_nut','printed_pin','hinge_nut','latch','tray'):
        print('Checking body clearance:',n,flush=True)
        obstacle=body_for_thread_envelopes if n in integral_threaded_names else body
        assert independent(obstacle).intersect(clash_envelopes.get(n,o)).val().Volume()<1e-5,'Body clash: '+n
sensor_tpu=next(o for n,o,c,k in parts if n=='TPU_passagem_sensor')
for n,o,c,k in parts:
    if n in ('tampa_misturador','tampa_manutencao_CO2_eletronica','sensor_referencia','sensor_temperatura_umidade_referencia'):
        assert independent(sensor_tpu).intersect(o).val().Volume()<1e-5,'Sensor bushing clash: '+n
# Static rigid-parts audit; intentional TPU compression is excluded.
rigid=[(n,o,k) for n,o,c,k in parts if k not in ('section_body','section_door','channel') and not any(t in n for t in ('TPU','junta','bucha'))]
checked=0
for i,(an,ao,ak) in enumerate(rigid):
    ab=ao.val().BoundingBox()
    for bn,bo,bk in rigid[i+1:]:
        bb=bo.val().BoundingBox()
        if min(ab.xmax,bb.xmax)-max(ab.xmin,bb.xmin)<=.001 or min(ab.ymax,bb.ymax)-max(ab.ymin,bb.ymin)<=.001 or min(ab.zmax,bb.zmax)-max(ab.zmin,bb.zmin)<=.001:continue
        if {ak,bk}=={'printed_pin','hinge_nut'} and an.split('_')[-1]==bn.split('_')[-1]:continue
        checked+=1
        print('Checking rigid pair:',an,bn,flush=True)
        a_shape=body_for_thread_envelopes if an=='corpo_integrado' and bn in integral_threaded_names else clash_envelopes.get(an,ao)
        b_shape=body_for_thread_envelopes if bn=='corpo_integrado' and an in integral_threaded_names else clash_envelopes.get(bn,bo)
        vol=independent(a_shape).intersect(independent(b_shape)).val().Volume()
        assert vol<1e-4,f'Rigid clash: {an} / {bn}: {vol}'
print(f'Rigid-parts clash audit passed: {checked} overlapping bounding-box pairs')
(OUT/'clash_report.json').write_text(json.dumps(dict(version='v58',changed_door_angles_deg=P['changed_door_angles_checked'],liner_insertion=P['liner_insertion_test'],removable_rack_clearance_checked=True,latch_free_door_angles_deg=P['latch_free_door_angles_checked'],latch_release_angles_deg=P['latch_release_angles_checked'],rigid_pairs_checked=checked,rigid_clashes=0,door_angles_deg=list(range(0,111,5)) if CHECK_MOVEMENTS else [],movement_tests="executed" if CHECK_MOVEMENTS else "deferred",service_cover_removal_lifts_mm=P['service_cover_removal_lifts_mm'],latch_count=1,lateral_feet_count=0,support_plane_z_mm=-10,closed_corner_channels=4,gas_passage_diameter_mm=P['port_diameter'],thread_motion_checks=thread_motion_checks,limitations=['Discrete movement samples', 'Intentional TPU compression excluded', 'Conservative envelopes for threaded parts against surrounding components', 'Integral threaded receivers checked separately; cylindrical reliefs used only for diagnostic envelopes', 'Movement checks deferred unless explicitly enabled', 'Service M4 shaft is checked at thread-root diameter; actual thread crests intentionally engage plastic.']),indent=2))
print('Exporting validated parts',flush=True)
assembly=cq.Assembly()
mesh=[]
for name,obj,color,kind in parts:
    if kind not in ('channel','section_body','section_door'): assembly.add(obj,name=name)
    if kind not in ('reference','channel','hardware','fastener','lid_hardware','sensor','section_body','section_door'):cq.exporters.export(obj,str(OUT/f'{name}.stl'))
    v,f=obj.val().tessellate(0.9,0.8)
    unique={}; vertices=[]; remap=[]
    for point in v:
        key=tuple(round(a,2) for a in point.toTuple())
        if key not in unique:
            unique[key]=len(vertices); vertices.append(key)
        remap.append(unique[key])
    mesh.append(dict(name=name,color=color,kind=kind,vertices=vertices,faces=[[remap[i] for i in tri] for tri in f]))
cq.exporters.export(assembly.toCompound(),str(OUT/'conjunto.step'))
# Body orientation requested by the user: rear Y125 flat on the bed, build toward -Y.
print_folder=OUT/'impressao_traseira_na_mesa';print_folder.mkdir(exist_ok=True)
rear_down=body.rotate((0,0,0),(1,0,0),-90).translate((59,10,125))
assert abs(rear_down.val().BoundingBox().zmin)<1e-5, 'Rear-down body does not sit on bed'
cq.exporters.export(rear_down,str(print_folder/'corpo_integrado.stl'))
(OUT/'pecas.json').write_text(json.dumps([dict(nome=n,tipo=k,stl=f'{n}.stl' if k not in ('reference','channel','hardware','fastener','lid_hardware','sensor','section_body','section_door') else None) for n,o,c,k in parts],indent=2))
(OUT/'mesh.json').write_text(json.dumps(mesh,separators=(',',':')))
(OUT/'parameters.json').write_text(json.dumps(P,indent=2))
print(f'{len(parts)} valid parts exported')

# Actual hollow wall coupon includes both the external and internal hinge ramps.
hinge_fixed_coupon=body.intersect(box(18,31,18,120,-13,22))
assert hinge_fixed_coupon.val().isValid() and len(hinge_fixed_coupon.solids().vals())==1
# Printable short fit coupons use exactly the same seal/channel profiles.
def section(stations,length):
    points=[(10+half,y) for y,half in stations]+[(10-half,y) for y,half in reversed(stations)]
    return cq.Workplane('XY').polyline(points).close().extrude(length)
rigid=box(20,8,35).cut(section(GROOVE,35))
def lip_section(side,wall,length):
    centres=BODY_INNER_LIP_CENTERS if side==1 else LIP_CENTERS
    points=[(10+side*centre+wall/2,y) for y,centre in centres]
    points += [(10+side*centre-wall/2,y) for y,centre in reversed(centres)]
    return cq.Workplane('XY').polyline(points).close().extrude(length)
def flexible_coupon(wall):
    return section(FOOT,35).union(lip_section(-1,wall,35)).union(lip_section(1,wall,35))
flex=flexible_coupon(.6)
for name,obj in [('amostra_canal_rigido',rigid),('amostra_junta_TPU',flex),('amostra_junta_TPU_labios_0p8',flexible_coupon(.8))]:
    assert obj.val().isValid() and obj.val().Volume()>0
    flat=obj.rotate((0,0,0),(1,0,0),-90)
    flat=flat.translate((0,0,-flat.val().BoundingBox().zmin))
    cq.exporters.export(flat,str(OUT/f'{name}.stl'))
(OUT/'door_v_profile.json').write_text(json.dumps(dict(boss=BOSS_PROFILE,receiver=RECEIVER_PROFILE,groove=V_GROOVE,foot=V_FOOT,lips=V_LIPS,lip_wall=.6),indent=2))
(OUT/'seal_profile.json').write_text(json.dumps(dict(groove=GROOVE,foot=FOOT,lip_centers=LIP_CENTERS,inner_lip_centers=BODY_INNER_LIP_CENTERS,lip_wall=LIP_WALL,nominal_compression=1.5),indent=2))
assert independent(body).intersect(seal).val().Volume()<1e-5,'Seal retention foot collides with body'
pressure_coupon=box(20,3,35,0,-4,0)
for xx in [0,18]:pressure_coupon=pressure_coupon.union(box(2,1,35,xx,-1,0))
for name,obj in [('amostra_pressao_junta',pressure_coupon),('amostra_dobradica_base_M4x20',hinge_fixed_coupon),('amostra_dobradica_porta_M4x20',hinge_door_coupon)]:
    assert obj.val().isValid() and len(obj.solids().vals())==1,name
    flat=obj.rotate((0,0,0),(1,0,0),90 if name=='amostra_pressao_junta' else -90)
    bb=flat.val().BoundingBox()
    flat=flat.translate((-bb.xmin,-bb.ymin,-bb.zmin))
    cq.exporters.export(flat,str(OUT/f'{name}.stl'))
# Straight V coupons match the actual inclined surfaces and retention profile.
v_clip=box(18,10,35,-4,-6,50)
for name,obj in [('amostra_V_porta_rigida',doorpart.intersect(v_clip)),
                 ('amostra_V_porta_TPU',v_seal.intersect(v_clip)),
                 ('amostra_V_assento_corpo',receiver.intersect(v_clip).union(box(18,3,35,-4,.1,50)))]:
    assert obj.val().isValid() and len(obj.solids().vals())==1,name
    flat=obj.rotate((0,0,0),(1,0,0),-90)
    bb=flat.val().BoundingBox()
    flat=flat.translate((-bb.xmin,-bb.ymin,-bb.zmin))
    cq.exporters.export(flat,str(OUT/f'{name}.stl'))
# A single sample STL holds the actual pod corner and its blind base side by side.
cx,cz=pod_mounts[0]
pod_clip=box(20,30,20,cx-10,120,cz-10)
pod_corner=power_box.intersect(pod_clip)
pod_base=box(20,4,20,cx-10,111,cz-10).union(pod_pads[0]).union(box(20,2,20,cx-10,123,cz-10)).cut(pod_pilots[0])
pod_samples=[];sample_x=0
for obj in [pod_corner,pod_base]:
    assert obj.val().isValid() and len(obj.solids().vals())==1,'Invalid pod mount sample'
    flat=obj.rotate((0,0,0),(1,0,0),-90)
    bb=flat.val().BoundingBox();flat=flat.translate((sample_x-bb.xmin,-bb.ymin,-bb.zmin))
    pod_samples.append(flat.val());sample_x+=bb.xlen+8
pod_sample=cq.Compound.makeCompound(pod_samples)
assert pod_sample.isValid() and len(cq.Workplane(obj=pod_sample).solids().vals())==2
cq.exporters.export(pod_sample,str(OUT/'amostra_caixinha_fixacao_M4.stl'))
print('Static clearances checked; gasket feet fit; coupons valid')

# Mouth-down coupon matches the planned rear-down body printing direction.
coupon=inlet_socket()
coupon=coupon.rotate((0,0,0),(1,0,0),180).translate((5,5,P['inlet_total_length']))
assert coupon.val().isValid() and len(coupon.solids().vals())==1
assert abs(coupon.val().BoundingBox().zmin)<1e-5
cq.exporters.export(coupon,str(OUT/'amostra_entrada_CO2_mangueira_OD5p8.stl'))

# Closure coupon reproduces the actual curved exterior and 45-degree inside face.
closure_coupon=gas_shell.intersect(box(60,100,8,-65,0,20))
# Represent the flat shared chamber wall so the coupon is a closed cavity slice.
closure_coupon=closure_coupon.union(box(4,85.5,8,-10,11,20))
closure_coupon=closure_coupon.rotate((0,0,0),(1,0,0),-90).translate((59,-20,96.5))
assert closure_coupon.val().isValid() and len(closure_coupon.solids().vals())==1
assert abs(closure_coupon.val().BoundingBox().zmin)<1e-5
cq.exporters.export(closure_coupon,str(OUT/'amostra_fechamento_CO2_45graus_PC.stl'))

# Shared-wall fit coupon, with the hole horizontal as in rear-down printing.
port_coupon=box(14,18,18,0,0,0)
port_coupon_hole=cq.Workplane('YZ',origin=(-1,9,9)).circle(P['port_diameter']/2).extrude(16)
port_coupon=port_coupon.cut(port_coupon_hole)
assert port_coupon.val().isValid() and len(port_coupon.solids().vals())==1
assert independent(port_coupon).intersect(port_coupon_hole).val().Volume()<1e-6
cq.exporters.export(port_coupon,str(OUT/'amostra_passagem_interna_CO2_OD5p8.stl'))

# Fit coupons, printed flat before committing to the full lid.
sensor_test=box(32,32,6,-43,44,mh+1).cut(sensor_hole)
cq.exporters.export(sensor_test.translate((43,-44,-mh-1)),str(OUT/'amostra_furo_sensor_integrado.stl'))
for bore in [15.3,15.5]:
    obj=sensor_grommet(bore).translate((27,-cy,-mh+0.5))
    cq.exporters.export(obj,str(OUT/f'amostra_bucha_sensor_TPU_{bore:.1f}.stl'))
cq.exporters.export(rjplate.rotate((0,0,0),(0,1,0),-90).translate((P['rj_center_z']+15.5,-95,56)),str(OUT/'amostra_encaixe_RJ45.stl'))
