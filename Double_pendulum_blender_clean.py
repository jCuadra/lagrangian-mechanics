# Double_pendulum_blender_clean.py
# 
# By Filip Strand and Jakob Arnoldsson
# (used with Blender 2.76) 
# 
# This script is most easily run by
# starting up blender with the
# --python flag via the command line.
# The script assumes that there is a file
# called 'maple_data.txt' containing the
# information about the generalized
# coordinates in the following format
# (columns are separated by space):
# 
# | t   | q_1 | ... | q_n | u_1 | ... | u_n |
# |-----+-----+-----+-----+-----+-----+-----|
# | t_0 |     |     |     |     |     |     |
# | t_1 |     |     |     |     |     |     |
# | .   |     |     |     |     |     |     |
# | .   |     |     |     |     |     |     |
# | t_k |     |     |     |     |     |     |
# 
# To start the animation, press alt-A or manually
# move through the timeline. 

import bpy
import math
import mathutils

# IMPORTANT: Set the rendering engine to CYCLES
scn = bpy.context.scene
scn.render.engine = 'CYCLES'

# Geometric Constants
l0 = 3
l1 = 7
l2 = 3
m1 = 1
m2 = 0.5
k1 = 50
k2 = 50
g = 9.82

# Read the 'maple_data.txt' file
dat=open("/Users/filipstrand/Desktop/maple_data.txt","r")
t=[]
q1=[]
q2=[]
q3=[]
q4=[]
for line in dat.readlines():
        row=list(map(float,line.split()))
        t.append(row[0])
        q1.append(row[1])
        q2.append(row[2])
        q3.append(row[3])
        q4.append(row[4])
dat.close()

# Set the number of frame to be the same
# as the amount of rows in the data file 
scn = bpy.context.scene 
scn.frame_end = len(t) 

# ----------Build Geometric Primitives-----------------
# IMPORANT!: Do not change the order in which these
# objects are made, this will cause mixups in referring
# to the correct objects later.

# Remove the default cube at the start
bpy.ops.object.delete()

# add Plane
bpy.ops.mesh.primitive_plane_add(radius = 300)
plane = bpy.data.objects.get("Plane")

# add Plane.001
bpy.ops.mesh.primitive_plane_add(radius = 300)
plane_001 = bpy.data.objects.get("Plane.001")

# add Cube
bpy.ops.mesh.primitive_cube_add()
cube = bpy.data.objects.get("Cube")

# add Cube.001
bpy.ops.mesh.primitive_cube_add()
cube_001 = bpy.data.objects.get("Cube.001")

# add Sphere
bpy.ops.mesh.primitive_uv_sphere_add(
        segments = 50,
        ring_count = 50,
        size = 0.5)
sphere = bpy.data.objects.get("Sphere")

# add Cylinder
bpy.ops.mesh.primitive_cylinder_add(
        radius = 0.1, 
        depth = 3.5)
cylinder = bpy.data.objects.get("Cylinder")

# add Cylinder.001
bpy.ops.mesh.primitive_cylinder_add(
        radius = 1, 
        depth = 3.5)
cylinder_001 = bpy.data.objects.get("Cylinder.001")

# add Cylinder.002
bpy.ops.mesh.primitive_cylinder_add(
        radius = 1, 
        depth = 3.5)
cylinder_002 = bpy.data.objects.get("Cylinder.002")

# add Cylinder.003
bpy.ops.mesh.primitive_cylinder_add(
        radius = 0.8, 
        depth = 7)
cylinder_003 = bpy.data.objects.get("Cylinder.003")

# add Cylinder.004
bpy.ops.mesh.primitive_cylinder_add(
        radius = 1, 
        depth = 3.5)
cylinder_004 = bpy.data.objects.get("Cylinder.004")

# add Cylinder.005
bpy.ops.mesh.primitive_cylinder_add(
        radius = 1, 
        depth = 3.5)
cylinder_005 = bpy.data.objects.get("Cylinder.005")
# ----------Build Geometric Primitives-----------------


# :::::::: MAKING MATERIALS::::::::::::::::::::::::::::
# Here we merely construct and assign empty materials
# to every object that we will later change in the Blender GUI.
# The only important property at this stage is the
# unique name for the different materials.

material3 = bpy.data.materials.new(name="Material3")

plane.data.materials.append(bpy.data.materials.new(name="Material1"))
plane_001.data.materials.append(bpy.data.materials.new(name="Material2"))
cube.data.materials.append(material3)
cube_001.data.materials.append(bpy.data.materials.new(name="Material4"))
sphere.data.materials.append(bpy.data.materials.new(name="Material5"))
cylinder.data.materials.append(bpy.data.materials.new(name="Material3"))
cylinder_001.data.materials.append(material3)
cylinder_002.data.materials.append(material3)
cylinder_003.data.materials.append(material3)
cylinder_004.data.materials.append(material3)
cylinder_005.data.materials.append(material3)

# Material for the springs (it is set later in update_springs(scene,n))
material6 = bpy.data.materials.new(name="Material6")
# :::::::: MAKING MATERIALS::::::::::::::::::::::::::::


# This function draws the first spring for each frame.
# The mesh is unfortunately redrawn completely for every
# frame making it very expensive to animate. As shown later
# we recommend to disable this function for performance 
# reasons when working and re-enabling it when rendering.
# (NOTE: The springs are math-surfaces generated by the
# plug-in 'bpy.ops.mesh.primitive_xyz_function_surface'
# which is included in Blender but have to be activated
# in settings.)
def set_spring_1_position(n):
        
        # Spring properties
        spiral_radius = 0.25
        wire_radius = 0.05
        coils_number = 10
        spring_height = (l0+q4[n]-0.6)*2*math.pi/coils_number

        # Koordinatbyte för springen
        alpha_1 = "(("  + str(spiral_radius) + "+" + str(wire_radius) + "*cos(2*pi*v))*cos(2*pi*u))"
        alpha_2 = "((" + str(spring_height) + "/(2*pi))*u +" + str(wire_radius) + "*sin(2*pi*v))"
        alpha_3 = "(("  + str(spiral_radius) + "+" + str(wire_radius) + "*cos(2*pi*v))*sin(2*pi*u))"
        
        bpy.ops.mesh.primitive_xyz_function_surface(x_eq = alpha_1,
                                                    y_eq= alpha_2,
                                                    z_eq= alpha_3,
                                                    range_u_min = 0,
                                                    range_u_max = coils_number,
                                                    range_v_min = 0,
                                                    range_v_max = 1,
                                                    wrap_u = False,
                                                    wrap_v = False,
                                                    range_u_step = 200,
                                                    range_v_step = 200)


        for item in bpy.data.objects:  
                 if item.type == "MESH" and item.name.startswith("XYZ"):
                         item.name = "spring_1"



# Identical function as before but for the second spring
# The difference is in the X,Y,Z coordinate description 
def set_spring_2_position(n):

        # Spring properties
        spiral_radius = 0.15
        wire_radius = 0.05
        coils_number = 20
        spring_height = (l2+q3[n])*2*math.pi/coils_number

        # Change to polar coordinates
        alpha_1 = "(("  + str(spiral_radius) + "+" + str(wire_radius) + "*cos(2*pi*v))*cos(2*pi*u))"
        alpha_11 = "((" + str(spring_height) + "/(2*pi))*u +" + str(wire_radius) + "*sin(2*pi*v))"
        alpha_3 = "(("  + str(spiral_radius) + "+" + str(wire_radius) + "*cos(2*pi*v))*sin(2*pi*u))"

        beta_1 = alpha_1
        beta_2 = "(" +  "cos(" + str(q1[n]+q2[n]+math.pi/2) + ")*" + alpha_11 + "+ sin(" + str(q1[n]+q2[n]+math.pi/2) +")*" + alpha_3 + "+" + str(l0+q4[n]-l1*math.sin(q1[n])) + ")"
        beta_3 = "(" +  "-sin(" + str(q1[n]+q2[n]+math.pi/2) + ")*" + alpha_11 + "+ cos(" + str(q1[n]+q2[n]+math.pi/2) +")*" + alpha_3 + "-" + str(l1*math.cos(q1[n])) + ")"
        
        
        bpy.ops.mesh.primitive_xyz_function_surface(x_eq = beta_1,
                                                    y_eq= beta_2,
                                                    z_eq= beta_3,
                                                    range_u_min = 0,
                                                    range_u_max = coils_number,
                                                    range_v_min = 0,
                                                    range_v_max = 1,
                                                    wrap_u = False,
                                                    wrap_v = False,
                                                    range_u_step = 200,
                                                    range_v_step = 200)


        for item in bpy.data.objects:  
         if item.type == "MESH" and item.name.startswith("XYZ"):
                 item.name = "spring_2"



# This function updates the two spring positions for every
# frame. The function can be commented out for performance
# reasons as the redrawing of the springs are slow
def update_springs(scene,n):

        # Remove the previous two springs from the last frame
        bpy.ops.object.select_all(action='DESELECT')
        loopindex = 0 
        for item in bpy.data.objects:  
                 if item.type == "MESH" and item.name.startswith("spring"):  
                        bpy.data.objects[item.name].select = True;
                        try:
                                scene.objects.unlink(bpy.data.objects[item.name])                                
                                bpy.data.objects.remove(item)
                        except:
                                pass
                        loopindex = loopindex + 1
                                
        set_spring_1_position(n)
        set_spring_2_position(n)

        spring_1 = bpy.data.objects.get("spring_1")
        spring_2 = bpy.data.objects.get("spring_2")

        depth_offset = 1.7
        spring_2.location = (depth_offset,0,0)
        
        spring_1.data.materials.append(material6)
        spring_2.data.materials.append(material6)
                
        bpy.ops.object.select_all(action='DESELECT')

        


# -------------Set the geometry for the objects-----------
def set_plane():
        minimum_height = (l1 + l2 + max(q3)) + 0.3*(l1 + l2 + max(q3))
        plane.location = (0,0,-minimum_height)

def set_plane_001():
        plane_001.location = (-18,0,0)
        plane_001.rotation_euler = (0.0, math.pi/2, 0.0)

def set_cube():
        cube.location  = (0,-0.2,0)
        cube.scale = (0.33,0.2,0.32)
         
def set_cube_001(n):
        cube_001.location  = (0,l0+q4[n],0)
        cube_001.scale = (0.33,0.86,0.32)
        
def set_sphere(n):
        depth_offset = 1.7
        padding = 0.3
        sphere.location = (depth_offset,
                            l0+q4[n]-(l1-0.1)*math.sin(q1[n])-(l2+q3[n]+padding)*math.sin(q1[n]+q2[n]),
                            -(l1-0.1)*math.cos(q1[n])-(l2+q3[n]+padding)*math.cos(q1[n]+q2[n]))
        sphere.scale  = (0.78,0.78,0.78)
        sphere.rotation_mode = 'ZYX'
        sphere.rotation_euler  = (-(q1[n]+q2[n]),0,0)

def set_cylinder():
        cylinder.rotation_euler = (math.pi/2, 0,0)
        cylinder.scale = (1,1,20)
        cylinder.location = (0, 0, 0)

def set_cylinder_001(n):
        cylinder_001.location  = (0.39489,l0+q4[n],0)
        cylinder_001.scale  = (0.1,0.1,0.2)
        cylinder_001.rotation_euler = (0, math.pi/2,0)

def set_cylinder_002(n):
        cylinder_002.rotation_mode = 'XZY'
        cylinder_002.rotation_euler = (0, math.pi/2,-q1[n])
        cylinder_002.location  = (1.01279,l0+q4[n],0)
        cylinder_002.scale  = (0.3,0.3,0.15)

def set_cylinder_003(n):
        depth_offset = 1
        cylinder_003.location = (depth_offset, l0+q4[n]-(l1/2)*math.sin(q1[n]),-(l1/2)*math.cos(q1[n]))
        cylinder_003.rotation_euler = (-q1[n],0,0)
        cylinder_003.scale = (0.3,0.3,l1/7)

def set_cylinder_004(n):
        depth_offset = 1.5
        cylinder_004.location  = (depth_offset,l0+q4[n]-(l1-0.1)*math.sin(q1[n]),-(l1-0.1)*math.cos(q1[n]))
        cylinder_004.scale  = (0.05,0.05,0.2)
        cylinder_004.rotation_euler = (0, math.pi/2,0)

def set_cylinder_005(n):
        depth_offset = 1.7
        cylinder_005.rotation_mode = 'XZY'
        cylinder_005.rotation_euler = (0, math.pi/2,-(q1[n] + q2[n]))
        cylinder_005.location  = (depth_offset,l0+q4[n]-(l1-0.1)*math.sin(q1[n]),-(l1-0.1)*math.cos(q1[n]))
        cylinder_005.scale  = (0.3,0.3,0.15)
# -------------Set the geometry for the objects-----------
    
# Setting the static geometry
def setStaticGeometry():
        set_plane()
        set_plane_001()
        set_cube()
        set_cylinder()

# This function gets called every time the frame updates
def my_handler(scene):
    n = int(scene.frame_current)
    updateMovingGeometry(scene,n)

# Setting the moving geometry
def updateMovingGeometry(scene,n):
        set_cube_001(n)
        set_sphere(n)
        set_cylinder_001(n)
        set_cylinder_002(n)
        set_cylinder_003(n)
        set_cylinder_004(n)
        set_cylinder_005(n)
        update_springs(scene,n)
        # Comment out 'update_springs(scene,n)' to remove the drawing of the springs
        # These are made using custom MATH-SURFACE method and are slow to render
        # A tip can be to disable these during modeling and reanableing the springs
        # when a final render is to be made

# Set the static geometry at startup
setStaticGeometry()
# Set the geometry update to the first frame
updateMovingGeometry(my_handler,1)
# Run every time the frame is chnaged
bpy.app.handlers.frame_change_pre.append(my_handler) 
