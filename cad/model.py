"""Preliminary mechanical layout; millimetres. Not validated for operation."""
import json
from pathlib import Path
import cadquery as cq
OUT=Path(__file__).resolve().parents[1]/'output'/'v26'
OUT.mkdir(exist_ok=True)
P=dict(width=120,depth=115,height=140,wall=4,mixer_radius=32,mixer_height=110,slide_length=80,slide_width=30,slide_height=16,tray_pitch=29,port_diameter=8,insulation_extension=10,air_cell_width=6,outer_skin=2)
P.update(sensor_diameter=15.62, sensor_insertion=80.75, sensor_mount_clearance_diameter=20.4, inlet_height=18, hose_id=4.5, inlet_stem_diameter=4.6, inlet_barb_diameter=5.0, inlet_bore_diameter=2.6)
P.update(sensor_collar_diameter=18.31, sensor_head_width=20.55, sensor_seal_bore=15.3, rj_cutout_width=14.79, rj_cutout_height=19.31, rj_panel_thickness=1.6)
P.update(tray_depth=72,tray_rear_y=80,heater_front_y=106,tray_heater_gap=26)
parts=[]
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
w,d,h,t=P['width'],P['depth'],P['height'],P['wall']
outer=box(w,d,h).edges('|Y').fillet(8)
cavity=box(w-2*t,d+6,h-2*t,t,-10,t).edges().fillet(6)
body=outer.cut(cavity)
# Unused generic rear ports removed.
for z in [40,69,98]:
    for x in [4,108]:
        body=body.union(box(8,74.5,3,x,8,z))
        body=body.union(box(8,2,6,x,80.5,z+3))
# Reinforced front rim, 8 mm sealing land. Rounded inner opening.
rim=box(w,8,h).edges('|Y').fillet(8).cut(box(w-16,12,h-16,8,-2,8).edges('|Y').fillet(6))
body=body.union(rim)
# Sections are (depth y, half-width), relative to centreline inset 4 mm.
# Entry chamfer -> narrow throat -> wider retained foot cavity.
GROOVE=[(-0.1,1.6),(0.5,1.2),(0.9,1.2),(1.6,2.0),(3.2,2.0)]
FOOT=[(0.0,0.95),(0.9,0.95),(1.65,1.75),(2.8,1.75),(3.0,1.5)]
LIP=[(-1.5,0.7),(-1.1,1.35),(-0.5,1.5),(0.15,1.1)]
def rounded_wire(inset,y):
    return box(w-2*inset,1,h-2*inset,inset,y-1,inset).edges('|Y').fillet(8-inset).faces('>Y').val().outerWire()
def seal_ring(stations):
    outer_wires=[rounded_wire(4-half,y) for y,half in stations]
    inner_wires=[rounded_wire(4+half,y) for y,half in stations]
    return cq.Workplane(obj=cq.Solid.makeLoft(outer_wires,ruled=True)).cut(cq.Solid.makeLoft(inner_wires,ruled=True))
ring=seal_ring(GROOVE)
body=body.cut(ring)
# Rounded half-cylinder shares the incubator's x=0..4 wall.
r=P['mixer_radius']; mh=P['mixer_height']; cy=60
clip=box(r+1,2*r+2,mh+2,-r-1,cy-r-1,0)
mix=cq.Workplane('XY').center(0,cy).circle(r).extrude(mh).intersect(clip)
inner=cq.Workplane('XY',origin=(0,0,t)).center(0,cy).circle(r-t).extrude(mh).intersect(clip)
inner=inner.edges('|Z').fillet(4).edges('<Z').fillet(3)
body=body.union(mix.cut(inner).translate((-10,0,0)))
# Continuous passage through shared wall, below slides and above water pan.
passage=cq.Workplane('YZ',origin=(-18,cy,34)).circle(4).extrude(30)
body=body.cut(passage)
# Integral rear-facing hose barb; dimensions are preliminary for silicone ID 4.5.
# Local Z becomes global +Y. Wide root overlaps the curved mixer wall.
def inlet_spigot():
    q=cq.Workplane('XY').circle(5).extrude(5)
    q=q.union(cq.Workplane('XY',origin=(0,0,5)).circle(P['inlet_stem_diameter']/2).extrude(11))
    for z in [7,11]:
        q=q.union(cq.Solid.makeCone(P['inlet_barb_diameter']/2,2.3,2,cq.Vector(0,0,z)))
    q=q.union(cq.Solid.makeCone(2.3,1.95,2,cq.Vector(0,0,16)))
    return q.cut(cq.Workplane('XY',origin=(0,0,-1)).circle(P['inlet_bore_diameter']/2).extrude(20))
# Bottom recess, rear-facing inlet entirely inside the body envelope.
P.update(inlet_height=-1,inlet_internal_exit_height=12)
inlet=inlet_spigot().rotate((0,0,0),(1,0,0),-90).translate((-26,78,-1))
inlet_sleeve=cq.Workplane('XY',origin=(-26,80,-6)).circle(5).extrude(11)
inlet_horizontal=cq.Workplane('XZ',origin=(-26,80,-1)).circle(P['inlet_bore_diameter']/2).extrude(-18)
inlet_vertical=cq.Workplane('XY',origin=(-26,80,-1)).circle(P['inlet_bore_diameter']/2).extrude(13)
inlet_bore=inlet_horizontal.union(inlet_vertical)
root_plug=cq.Workplane('XZ',origin=(-26,78,-1)).circle(5).extrude(-1)
body=body.union(inlet_sleeve).union(inlet).union(root_plug).cut(inlet_bore)
assert independent(body).intersect(inlet_bore).val().Volume()<1e-6,'Bottom inlet blocked'
assert not body.val().isInside((-26,80,12)), 'Bottom inlet does not reach chamber'

# Hinges on RIGHT: fixed knuckles surround each moving central knuckle.
def barrel(z,height):
    return cq.Workplane('XY',origin=(126,-5,z)).circle(5).circle(1.7).extrude(height)
doorpart=box(w,5,h,0,-6,0).edges('|Y').fillet(8)
for z in [22,102]:
    for dz in [0,18]:
        body=body.union(box(6,10,8,120,-5,z+dz)).union(barrel(z+dz,8))
    doorpart=doorpart.union(box(7,5,9,119,-6,z+8.5)).union(barrel(z+8.5,9))
    bore=cq.Workplane('XY',origin=(126,-5,z-1)).circle(1.7).extrude(28)
    body=body.cut(bore); doorpart=doorpart.cut(bore)
    add(f'pino_dobradica_{z}',cq.Workplane('XY',origin=(126,-5,z-1)).circle(1.5).extrude(28),'#505965','printed_pin')
# Fully printed adjustable latches: custom coarse 8 mm thread, pitch 2 mm.
def printed_thread(clearance=False):
    root,crest,half=(3,4.35,.95) if clearance else (3,4,.65)
    path=cq.Wire.makeHelix(2,31,root)
    tooth=cq.Workplane('XZ').polyline([(root,-half),(crest,0),(root,half)]).close().sweep(path,isFrenet=True)
    return cq.Workplane('XY').circle(3.4 if clearance else 3.08).extrude(31).union(tooth).intersect(cq.Workplane('XY').circle(crest+.1).extrude(31))
thread=printed_thread()
thread_clear=printed_thread(True)
printed_nut=cq.Workplane('XY',origin=(0,0,26)).polygon(6,14).extrude(5).cut(thread_clear)
assert printed_nut.val().isValid() and len(printed_nut.solids().vals())==1
assert independent(thread).intersect(printed_nut).val().Volume()<1e-5,'Printed thread clearance failed'
latches=[]
clash_envelopes={}
for z in [30,116]:
    def at_latch(obj):return obj.rotate((0,0,0),(1,0,0),-90).translate((-9,-23,z))
    tab=box(20,26,20,-20,-16,z-10).edges('|Y').fillet(3).cut(yhole(-9,-2,z,4.35,22))
    nutseat=cq.Workplane('XZ',origin=(-9,8.3,z)).polygon(6,14.6).extrude(5.6)
    loading=box(16,5.6,12.7,-25,2.7,z-6.35)
    body=body.union(tab.cut(nutseat).cut(loading))
    dog=box(27,4,14,-16,-20,z-7).edges('|Y').fillet(2).cut(yhole(-9,-18,z,4.35,5))
    knob=cq.Workplane('XZ',origin=(-9,-20,z)).polygon(8,20).extrude(6).union(at_latch(thread))
    nut=at_latch(printed_nut)
    add(f'porca_impressa_fecho_{z}',nut,'#729daf','printed_nut')
    add(f'lingueta_fecho_{z}',dog,'#e6a454','latch')
    add(f'manipulo_fecho_{z}',knob,'#c88b43','knob')
    latches.append((z,dog))
    clash_envelopes[f'manipulo_fecho_{z}']=cq.Workplane('XZ',origin=(-9,-20,z)).polygon(8,20).extrude(6).union(yhole(-9,-7.5,z,4,15.5))
    clash_envelopes[f'porca_impressa_fecho_{z}']=cq.Workplane('XZ',origin=(-9,8,z)).polygon(6,14).extrude(5)
# Pull handle, open underneath.
handle=box(8,13,42,7,-19,49).cut(box(10,10,26,6,-17,57))
doorpart=doorpart.union(handle.translate((0,-10,0)))

# Free TPU shape: foot retained in channel; lip compressed by nominal 0.5 mm.
seal=seal_ring(FOOT).union(seal_ring(LIP))
add('junta_porta',seal,'#45ae89','seal')

for i,z in enumerate([43,72,101],1):
    tray=box(103,P['tray_depth'],2,8.5,8,z).edges('|Z').fillet(3)
    # Open central area, leaving support at the ends of the slide.
    tray=tray.cut(box(62,46,4,29,24,z-1).edges('|Z').fillet(5))
    tray=tray.union(box(103,3,6,8.5,8,z+2))
    assert abs(tray.val().BoundingBox().ymax-P['tray_rear_y'])<1e-6
    assert P['heater_front_y']-tray.val().BoundingBox().ymax>=26
    assert independent(body).intersect(tray).val().Volume()<1e-5, 'Tray interferes with rails/stops'
    add(f'bandeja_{i}',tray,'#e6a454','tray')
    add(f'uslide_referencia_{i}',box(80,30,3,20,38,z+2),'#81c6bf','reference')
pan=box(90,70,18,15,22,8).edges('|Z').fillet(7).cut(box(84,64,22,18,25,11).edges().fillet(4))
add('reservatorio_agua',pan,'#6eadd8')
# Removable D-shaped lid: three external M4 fasteners, no printed threads.
# Reinforced top collar retains a push-in TPU gasket; underside nut pockets.
def dshape(radius,flat,z,height,corner=4):
    shape=cq.Workplane('XY',origin=(0,cy,z)).circle(radius).extrude(height)
    shape=shape.intersect(box(radius+flat+1,2*radius+2,height+2,-radius-1,cy-radius-1,z-1))
    return shape.edges('|Z').fillet(corner).translate((-10,0,0))
def dwire(radius,flat,z,corner):
    return dshape(radius,flat,z-1,1,corner).faces('>Z').val().outerWire()
def mixer_ring(stations):
    ow=[dwire(32+half,-2+half,mh-depth,4+half) for depth,half in stations]
    iw=[dwire(32-half,-2-half,mh-depth,4-half) for depth,half in stations]
    return cq.Workplane(obj=cq.Solid.makeLoft(ow,ruled=True)).cut(cq.Solid.makeLoft(iw,ruled=True))
collar=dshape(46,0,mh-8,8).cut(dshape(28,-4,mh-9,10,2))
body=body.union(collar)
mix_groove=mixer_ring(GROOVE)
body=body.cut(mix_groove)
mix_seal=mixer_ring(FOOT).union(mixer_ring(LIP))
lid=dshape(46,-0.3,mh+1,6)
# Sensor interface: replaceable TPU grommet; physical sealing untested.
sensor_hole=cq.Workplane('XY',origin=(-27,cy,mh)).circle(P['sensor_mount_clearance_diameter']/2).extrude(10)
lid=lid.cut(sensor_hole)
for i,(bx,by) in enumerate([(-20,cy-38),(-49,cy),(-20,cy+38)],1):
    bore=cq.Workplane('XY',origin=(bx,by,mh-10)).circle(2.2).extrude(25)
    pocket=cq.Workplane('XY',origin=(bx,by,mh-8)).polygon(6,8.5).extrude(4)
    body=body.cut(bore).cut(pocket)
    # Hard stop sets 1 mm gap and nominal 0.5 mm lip compression.
    stop=cq.Workplane('XY',origin=(bx,by,mh)).circle(5).circle(2.2).extrude(1)
    body=body.union(stop)
    lid=lid.cut(bore)
    nut=cq.Workplane('XY',origin=(bx,by,mh-7.8)).polygon(6,8).circle(2.2).extrude(3.5)
    screw=cq.Workplane('XY',origin=(bx,by,mh-8)).circle(2).extrude(15.8)
    screw=screw.union(cq.Workplane('XY',origin=(bx,by,mh+7.8)).polygon(6,8).extrude(3))
    washer=cq.Workplane('XY',origin=(bx,by,mh+7)).circle(4.5).circle(2.2).extrude(0.8)
    add(f'porca_tampa_{i}',nut,'#505965','hardware')
    add(f'parafuso_tampa_{i}',screw,'#505965','lid_hardware')
    add(f'arruela_tampa_{i}',washer,'#505965','lid_hardware')
# Integral insulation skin, with sealed small air cells. Internal cavity unchanged.
# Narrow pitched roofs reduce internal bridging when the body is printed upright.
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
# Back, right, roof, floor and exposed left side. Front sealing rim untouched.
body=body.union(cellular_block(120,0,-10,10,125,160))
body=body.union(cellular_block(0,115,-10,120,10,160))
body=body.union(cellular_block(0,0,140,120,115,10))
body=body.union(cellular_block(0,0,-10,120,115,10))
# Continuous left insulating wall; mixer shifted outboard by 10 mm.
left=cellular_block(-10,0,-10,10,125,160)
body=body.union(left)
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
            bore=cq.Workplane('XY',origin=(xx,yy,8)).circle(1.7).extrude(13)
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
add('sensor_temperatura_umidade_referencia',box(7,20,15,8,80,120),'#d8d8ce','reference')
add('chapa_aquecedor_referencia',box(33,1,90,43.5,106,18),'#9ca6b0','reference')
add('pelicula_aquecedora_90x33_referencia',box(33,.3,90,43.5,107,18),'#d1a047','reference')

# Compact dry compartment in the same lateral strip as the mixer, below its flange.
# Rear face stays at Y125; side face stays at X-56.
P.update(pcb_length=43.12,pcb_width=25.16,electronics_internal_width=41,
         electronics_internal_depth=25.5,electronics_internal_height=90)
case=box(49,34,95,-59,94,5)
case=case.cut(box(41,34,90,-53.5,96.5,7.5))
case=case.cut(box(49,3,95,-59,125,5))
case=case.cut(box(41,6,3,-53.5,122,97.5))
# PCB upright on the front inner wall; height of components still provisional.
case=case.union(box(29.16,3,47.12,-49,96.5,20))
for xx in [-49,-21.84]:case=case.union(box(2,7,47.12,xx,96.5,20))
case=case.union(box(29.16,7,2,-49,96.5,20))
for zz in [29,55]:
    case=case.cut(box(2,10,4,-47,95,zz)).cut(box(2,10,4,-23.84,95,zz))
pcb=box(25.16,1.6,43.12,-47,99.5,22)
# Rear panel is part of a single upward-removable service cover.
cover=box(48.4,2.8,95,-58.7,125.2,5)
cover=cover.union(box(3,3,84,-36,122.2,12))
service_guides=[]
for xx in [-54,-14]:
    guide=box(2,1.5,80,xx,123.7,10)
    cover=cover.union(guide)
    service_guides.append(box(2.4,1.9,91,xx-.2,123.5,9.8))
# Keystone directly in side wall; local panel thickness 1.6 mm.
rjopening=box(10,P['rj_cutout_width'],P['rj_cutout_height'],-62,108.5-P['rj_cutout_width']/2,82-P['rj_cutout_height']/2)
rjrelief=box(6,23,27,-57.4,97,68.5)
# Small independent fit sample replicates aperture and wall thickness.
rjplate=box(1.6,27,31,-56,95,66.5).cut(rjopening)
# Provisional sensor cable entry into dry compartment from above.
case=case.cut(cq.Workplane('XY',origin=(-34,108,96)).circle(3.5).extrude(6))
# Continuous side skin bridges mixer and electronics; original gas wall preserved.
fairing=box(49,85.5,97,-59,11,5).edges('|Z').fillet(3)
fairing=fairing.cut(box(41,80.5,92,-53.5,13.5,7.5).edges('|Z').fillet(1))
# Keep a 0.2 mm clearance to the existing curved mixer wall to avoid sliver unions.
mixer_envelope=cq.Workplane('XY',origin=(-10,cy,0)).circle(r+0.2).extrude(mh+2)
fairing=fairing.cut(mixer_envelope)
body=body.union(case).union(fairing).cut(inlet_bore)
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
assert independent(fairing).intersect(inner.translate((-10,0,0))).val().Volume()<1e-5, 'Fairing obstructs mixer cavity' 
assert len(body.solids().vals())==1,'Electronics must be integral to the main body'
for name,obj,color,kind in [('placa_eletronica_referencia',pcb,'#458bb0','reference')]:
    assert len(obj.solids().vals())==1,name
    add(name,obj,color,kind)
assert independent(body).intersect(pcb).val().Volume()<1e-5,'Integrated housing interferes with PCB'
assert independent(body).intersect(cover).val().Volume()<1e-5,'Electronics lid interferes'

# Simple separate pod: one TPU feedthrough, two direct push-in locating pins.
power_box=box(36,21,30,42,125,101).edges('|X').fillet(4)
power_box=power_box.cut(box(31,21,25,44.5,122.5,103.5).edges('|X').fillet(1.5))
# Right when viewed from behind corresponds to -X in model coordinates.
power_hole=cq.Workplane('YZ',origin=(41,135.5,116)).circle(4).extrude(6)
power_box=power_box.cut(power_hole)
P['power_connector_hole_diameter']=8
P['power_connector_axis']='-X, right when viewed from rear'
# Blind 2 mm sockets; small local pads keep sockets out of air cells.
for zz in [102.5,129.5]:
    pad=cq.Workplane('XZ',origin=(60,125,zz)).circle(2.5).extrude(4)
    socket=cq.Workplane('XZ',origin=(60,125.1,zz)).circle(1.2).extrude(2.1)
    body=body.union(pad).cut(socket)
    pin=cq.Solid.makeCone(1.0,1.2,2,cq.Vector(60,123,zz),cq.Vector(0,1,0))
    power_box=power_box.union(box(5,3,3,57.5,125,zz-1.5)).union(pin)
add('caixinha_encaixe_aquecedor',power_box,'#c5d4df')
assert len(power_box.solids().vals())==1,'Power pod disconnected'
assert independent(body).intersect(power_box).val().Volume()<1e-5,'Power pod interferes'
for dy in [0,1,3,15]:
    assert independent(body).intersect(power_box.translate((0,dy,0))).val().Volume()<1e-5,'Pod removal blocked'
for name,obj,_,_ in parts:
    if name=='TPU_passagem_aquecedor':
        assert independent(power_box).intersect(obj).val().Volume()<1e-5,'Pod touches TPU'
assert independent(power_box).intersect(power_hole).val().Volume()<1e-5,'Jack aperture blocked'
# No new hole through the warm wall: sealed heater-wire feedthrough already exists.
hose_approach=cq.Workplane('XZ',origin=(-26,97,-1)).circle(4).extrude(-30)
assert independent(body).intersect(hose_approach).val().Volume()<1e-5,'Rear hose approach obstructed'
assert inlet.val().BoundingBox().ymax<=128 and inlet.val().BoundingBox().zmin>=-10
# One lift-off service cover: upper dry cap and rear electronics access panel.
# Gas-tight mixer lid and its TPU gasket remain a separate functional seal.
hood=box(49,117,47.7,-59,11,102.3).edges('|Z').fillet(2)
hood=hood.cut(box(50,111.5,47,-56.25,13.75,100))
hood=hood.union(box(41,14,2.3,-56.5,111.5,100)).union(cover)
# Overlapping skirt hides the horizontal seam; clearance stays inside the joint.
skirt=box(49,117,5,-59,11,98).edges('|Z').fillet(2)
skirt=skirt.cut(box(50,114.6,7,-57.8,12.2,97))
seat=box(49.4,117.4,4.7,-59.2,10.8,97.7).edges('|Z').fillet(2.2)
seat=seat.cut(box(50,114,6,-57.5,12.5,97))
body=body.cut(seat)
hood=hood.union(skirt)

# Four pins: two at upper support and two at the lower rear sill.
P['service_cover_pin_count']=4
body=body.union(box(49,6.4,3,-59,122,2))
for xx,yy,root_z in [(-48,114.5,100),(-22,114.5,100),(-48,126.6,5),(-22,126.6,5)]:
    hole=cq.Workplane('XY',origin=(xx,yy,root_z-2.5)).circle(1.6).extrude(3)
    body=body.cut(hole)
    pin=cq.Solid.makeCone(1.35,1.6,2,cq.Vector(xx,yy,root_z-2))
    hood=hood.union(pin)
# M4 nuts slide in horizontally from the exposed collar perimeter.
# 7.4 mm channel retains the two parallel flats of the 8 mm reference hex.
# Cut after all body unions so the fairing cannot close the entrances.
for bx,by in [(-20,cy-38),(-49,cy),(-20,cy+38)]:
    access=box(bx+60,7.4,4,-60,by-3.7,mh-8)
    body=body.cut(access)
    assert independent(body).intersect(access).val().Volume()<1e-5,'Nut entry blocked'
add('tampa_manutencao_CO2_eletronica',hood,'#c5d4df','hood')
assert len(hood.solids().vals())==1,'Service cover must be one printed part'
for lift in [0,3,10,30,80,160]:
    assert independent(body).intersect(hood.translate((0,0,lift))).val().Volume()<1e-5,'Service cover removal blocked'
# Integrated lateral feet, coplanar with the main enclosure base at Z-10.
for yy in [13,109]:
    foot=box(16,16,17,-58,yy,-10).edges('|Z').fillet(2)
    body=body.union(foot)
assert len(body.solids().vals())==1,'Support feet must join main body'
P['lateral_feet_count']=2
P['heater_voltage']=12
# Door inner sealing face and hinge coordinates unchanged. Solid perimeter for dogs.
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
add('porta_articulada',doorpart,'#729daf','door')
# Display-only cuts show actual cavities without exporting a second physical body.
assert body.val().isValid(),'Body invalid before section'
body_section=independent(body).cut(box(240,200,90,-80,-30,70))
door_section=doorpart.cut(box(220,180,90,-60,-30,70))
add('corte_corpo_referencia',body_section,'#c5d4df','section_body')
add('corte_porta_referencia',door_section,'#729daf','section_door')
add('corpo_integrado',body,'#c5d4df','shell')
add('junta_tampa_TPU',mix_seal,'#45ae89','mixer_seal')
add('tampa_misturador',lid,'#98bbad','lid')
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
assert independent(body).intersect(sensor_seal).val().Volume()<1e-5,'Sensor grommet collides with body'
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
assert independent(body).intersect(mix_seal).val().Volume()<1e-5,'Mixer seal collides with collar'
assert len(mix_seal.solids().vals())==1,'Mixer gasket must be continuous'
for lift in [0,5,20,40]:
    assert independent(body).intersect(lid.translate((0,0,lift))).val().Volume()<1e-5,'Lid removal blocked'
# Display-only indication of the real through-wall channel.
add('passagem_gas_referencia',passage,'#d47cac','channel')
assert len(body.solids().vals())==1, 'Integrated body must be one solid'
assert independent(body).intersect(passage).val().Volume()<1e-6, 'Gas passage obstructed'
# Door sweep with dogs parked 90 degrees and loosened by 0.8 mm.
print('Checking door sweep',flush=True)
for angle in range(0,111,5):
    opened=doorpart.rotate((126,-5,0),(126,-5,1),angle)
    assert independent(body).intersect(opened).val().Volume()<1e-5, f'Door collision at {angle}'
    for z,dog in latches:
        parked=dog.rotate((-9,0,z),(-9,1,z),90).translate((0,-0.8,0))
        assert opened.intersect(parked).val().Volume()<1e-5, f'Latch collision at {angle}'
# Verify functional clearances after every body union, including insulation.
for z,_ in latches:
    body=body.cut(yhole(-9,-2,z,4.35,22),clean=False)
    body=body.cut(cq.Workplane('XZ',origin=(-9,8.3,z)).polygon(6,14.6).extrude(5.6),clean=False)
    body=body.cut(box(16,5.6,12.7,-25,2.7,z-6.35),clean=False)
# Replace the earlier display/export body with final latch passages.
parts=[(n,body if n=='corpo_integrado' else (independent(body).cut(box(240,200,90,-80,-30,70)) if n=='corte_corpo_referencia' else o),c,k) for n,o,c,k in parts]
for n,o,c,k in parts:
    if k in ('knob','printed_nut','printed_pin','latch','tray'):
        print('Checking body clearance:',n,flush=True)
        assert independent(body).intersect(clash_envelopes.get(n,o)).val().Volume()<1e-5,'Body clash: '+n
sensor_tpu=next(o for n,o,c,k in parts if n=='TPU_passagem_sensor')
for n,o,c,k in parts:
    if n in ('tampa_misturador','tampa_manutencao_CO2_eletronica','sensor_referencia','sensor_temperatura_umidade_referencia'):
        assert independent(sensor_tpu).intersect(o).val().Volume()<1e-5,'Sensor bushing clash: '+n
# Static rigid-parts audit; intentional TPU compression is excluded.
rigid=[(n,o,k) for n,o,c,k in parts if k not in ('section_body','section_door','channel') and n!='corpo_integrado' and not any(t in n for t in ('TPU','junta','bucha'))]
checked=0
for i,(an,ao,ak) in enumerate(rigid):
    ab=ao.val().BoundingBox()
    for bn,bo,bk in rigid[i+1:]:
        bb=bo.val().BoundingBox()
        if min(ab.xmax,bb.xmax)-max(ab.xmin,bb.xmin)<=.001 or min(ab.ymax,bb.ymax)-max(ab.ymin,bb.ymin)<=.001 or min(ab.zmax,bb.zmax)-max(ab.zmin,bb.zmin)<=.001:continue
        if {ak,bk}=={'knob','printed_nut'}:continue # Actual mating threads checked separately above.
        checked+=1
        print('Checking rigid pair:',an,bn,flush=True)
        vol=independent(clash_envelopes.get(an,ao)).intersect(independent(clash_envelopes.get(bn,bo))).val().Volume()
        assert vol<1e-4,f'Rigid clash: {an} / {bn}: {vol}'
print(f'Rigid-parts clash audit passed: {checked} overlapping bounding-box pairs')
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
(OUT/'pecas.json').write_text(json.dumps([dict(nome=n,tipo=k,stl=f'{n}.stl' if k not in ('reference','channel','hardware','fastener','lid_hardware','sensor','section_body','section_door') else None) for n,o,c,k in parts],indent=2))
(OUT/'mesh.json').write_text(json.dumps(mesh,separators=(',',':')))
(OUT/'parameters.json').write_text(json.dumps(P,indent=2))
print(f'{len(parts)} valid parts exported')

# Printable short fit coupons use exactly the same seal/channel profiles.
def section(stations,length):
    points=[(10+half,y) for y,half in stations]+[(10-half,y) for y,half in reversed(stations)]
    return cq.Workplane('XY').polyline(points).close().extrude(length)
rigid=box(20,8,35).cut(section(GROOVE,35))
flex=section(FOOT,35).union(section(LIP,35))
for name,obj in [('amostra_canal_rigido',rigid),('amostra_junta_TPU',flex)]:
    assert obj.val().isValid() and obj.val().Volume()>0
    flat=obj.rotate((0,0,0),(1,0,0),-90)
    flat=flat.translate((0,0,-flat.val().BoundingBox().zmin))
    cq.exporters.export(flat,str(OUT/f'{name}.stl'))
(OUT/'seal_profile.json').write_text(json.dumps(dict(groove=GROOVE,foot=FOOT,lip=LIP,nominal_compression=0.5),indent=2))
assert independent(body).intersect(seal).val().Volume()<1e-5,'Seal retention foot collides with body'
print('Door and lid removal checked; both gasket feet fit; coupons valid')

# Horizontal coupon reproduces the integrated barb printing orientation.
coupon=inlet_spigot().rotate((0,0,0),(1,0,0),-90).translate((0,0,5))
coupon=coupon.union(box(18,4,10,-9,0,0)).cut(yhole(0,9,5,P['inlet_bore_diameter']/2,12))
assert coupon.val().isValid() and len(coupon.solids().vals())==1
cq.exporters.export(coupon,str(OUT/'amostra_entrada_CO2_4p5mm.stl'))

# Fit coupons, printed flat before committing to the full lid.
sensor_test=box(32,32,6,-43,44,mh+1).cut(sensor_hole)
cq.exporters.export(sensor_test.translate((43,-44,-mh-1)),str(OUT/'amostra_tampa_sensor.stl'))
for bore in [15.3,15.5]:
    obj=sensor_grommet(bore).translate((27,-cy,-mh+0.5))
    cq.exporters.export(obj,str(OUT/f'amostra_bucha_sensor_TPU_{bore:.1f}.stl'))
cq.exporters.export(rjplate.rotate((0,0,0),(0,1,0),-90).translate((97.5,-95,56)),str(OUT/'amostra_encaixe_RJ45.stl'))
