"""Insulation channels closing toward +Y, for the door's outer face on the bed."""
import math
import cadquery as cq


def box(w,d,h,x,y,z):
    return cq.Workplane('XY').box(w,d,h,centered=False).translate((x,y,z))


def build_door_insulation(width=120,height=140):
    outer=box(width,10,height,0,-16,0).edges('|Y').fillet(8)
    # Constant rounded inset preserves 2 mm perimeter skin even at the corners.
    inner=box(width-4,8,height-4,2,-15,2).edges('|Y').fillet(6)
    cells=[]
    records=[]
    for x in range(2,int(width)-3,8):
        dx=min(6,width-x-2)
        for z,dz in ((2,height/2-3),(height/2+1,height/2-3)):
            # 2 mm outside skin, 6 mm void depth, 2 mm inside skin.
            # Each long channel closes across X, never across its long Z axis.
            bevel=(dx-.4)/2
            cell=box(dx,6,dz,x,-14,z).edges('|Z and >Y').chamfer(bevel)
            cell=cell.intersect(inner)
            if cell.val().Volume()<1e-6:continue
            assert cell.val().isValid() and len(cell.solids().vals())==1
            for face in cell.val().Faces():
                if face.geomType()!='PLANE':continue
                n=face.normalAt()
                if n.y<.01:continue
                if n.y>.999:
                    assert face.BoundingBox().xlen<=.40001
                else:
                    assert n.y<=1/math.sqrt(2)+1e-6
            cells.append(cell.val())
            records.append(dict(bounds_mm=[x,-14,z,dx,6,dz],roof_start_y=-8-bevel,
                                roof_end_y=-8,roof_angle_deg=45,closure_width_mm=.4))
    shape=outer.cut(cq.Compound.makeCompound(cells))
    assert shape.val().isValid() and len(shape.solids().vals())==1
    return shape,cells,records
