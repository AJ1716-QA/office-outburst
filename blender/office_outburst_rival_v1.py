import bpy
import math
from mathutils import Vector

# OFFICE OUTBURST — RIVAL CHARACTER BLOCKOUT V1
# Blender 5.x. Creates a separate stylized rival character scene.
# Save as Office_Outburst_Rival_v1.blend. Does not alter the live game.

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, roughness=0.5, metallic=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*color, 1)
    bs.inputs["Roughness"].default_value = roughness
    bs.inputs["Metallic"].default_value = metallic
    return m

skin = material("Rival warm light skin", (0.72, 0.48, 0.34))
hair = material("Slick dark brown hair", (0.035, 0.022, 0.018), 0.34)
shirt = material("Midnight navy office shirt", (0.025, 0.075, 0.14), 0.62)
tie = material("Silver grey tie", (0.38, 0.42, 0.46), 0.3, 0.25)
pants = material("Graphite trousers", (0.045, 0.052, 0.065), 0.65)
shoes = material("Black leather shoes", (0.012, 0.016, 0.022), 0.22)
white = material("Eye whites", (0.96, 0.96, 0.92), 0.25)
iris = material("Dark eyes", (0.09, 0.045, 0.025), 0.25)
black = material("Pupils", (0.006, 0.005, 0.004), 0.2)
brows = material("Sharp eyebrows", (0.055, 0.028, 0.018), 0.7)
metal = material("Watch and glasses metal", (0.35, 0.40, 0.46), 0.22, 0.7)
lens = material("Smoky glasses lenses", (0.12, 0.18, 0.22), 0.18, 0.25)
mouth = material("Smug mouth", (0.19, 0.045, 0.035), 0.5)
badge_mat = material("Employee badge navy", (0.02, 0.12, 0.20), 0.35)

def smooth(o):
    if o.type == "MESH":
        for p in o.data.polygons:
            p.use_smooth = True
    return o

def sphere(name, loc, scale, mat, seg=32, rings=20):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=rings, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    o.data.materials.append(mat)
    smooth(o)
    return o

def rounded_box(name, loc, dims, mat, bevel=0.1):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    b = o.modifiers.new("Soft bevels", "BEVEL")
    b.width = bevel
    b.segments = 4
    o.modifiers.new("Weighted normals", "WEIGHTED_NORMAL")
    return o

def limb(name, a, b, radius, mat, radius_top=None):
    a, b = Vector(a), Vector(b)
    d = b-a
    bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=radius,
        radius2=radius if radius_top is None else radius_top,
        depth=d.length, location=(a+b)/2)
    o = bpy.context.object
    o.name = name
    o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    o.data.materials.append(mat)
    smooth(o)
    bevel = o.modifiers.new("Rounded ends", "BEVEL")
    bevel.width = radius * 0.35
    bevel.segments = 3
    o.modifiers.new("Weighted normals", "WEIGHTED_NORMAL")
    sphere(name+" joint A", a, (radius,)*3, mat, 20, 12)
    sphere(name+" joint B", b, (radius,)*3, mat, 20, 12)

# Facing toward -Y. Slightly leaner, more angular silhouette than the hero.
for side, x in (("L", -0.19), ("R", 0.19)):
    rounded_box(side+" leather shoe", (x, -0.12, 0.16), (0.31, 0.55, 0.21), shoes, 0.08)
    limb(side+" lower leg", (x, 0, 0.28), (x, 0, 0.91), 0.105, pants, 0.13)
    limb(side+" upper leg", (x, 0, 0.88), (x*0.9, 0, 1.46), 0.14, pants, 0.17)
rounded_box("Trouser waist", (0, 0, 1.46), (0.51, 0.32, 0.22), pants, 0.07)
rounded_box("Silver belt buckle", (0, -0.17, 1.46), (0.10, 0.025, 0.07), metal, 0.015)

rounded_box("Navy shirt torso", (0, 0, 2.02), (0.86, 0.42, 1.08), shirt, 0.17)
sphere("Neck", (0, 0, 2.65), (0.15, 0.15, 0.22), skin)
for s in (-1, 1):
    collar = rounded_box("Pointed shirt collar", (s*0.13, -0.23, 2.55), (0.18, 0.07, 0.20), shirt, 0.035)
    collar.rotation_euler[1] = s*math.radians(-15)
sphere("Tie knot", (0, -0.255, 2.46), (0.075, 0.045, 0.085), tie)
rounded_box("Loose silver tie", (0, -0.25, 2.13), (0.12, 0.055, 0.55), tie, 0.025)
bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0, radius2=0.065, depth=0.14, location=(0, -0.25, 1.78))
tie_tip = bpy.context.object
tie_tip.name = "Tie pointed tip"
tie_tip.rotation_euler[2] = math.radians(45)
tie_tip.data.materials.append(tie)

# Arms posed in a smug, arms-akimbo stance.
for side, x in (("L", -0.53), ("R", 0.53)):
    sphere(side+" shoulder", (x*0.82, 0, 2.40), (0.20, 0.20, 0.21), shirt)
    limb(side+" upper sleeve", (x*0.82, 0, 2.39), (x*1.08, -0.02, 2.04), 0.13, shirt, 0.12)
    limb(side+" forearm", (x*1.08, -0.02, 2.04), (x*0.78, -0.13, 1.79), 0.095, shirt, 0.085)
    sphere(side+" hand", (x*0.72, -0.15, 1.76), (0.11, 0.08, 0.12), skin)
    # Wristwatch on left arm
    if side == "L":
        sphere("Luxury watch face", (x*0.96, -0.06, 1.94), (0.075, 0.035, 0.075), metal)

# Head, deliberately narrower and more angular.
sphere("Rival head", (0, -0.01, 3.02), (0.36, 0.32, 0.46), skin, 48, 32)
sphere("Angular jaw", (0, -0.06, 2.83), (0.29, 0.28, 0.20), skin, 40, 24)
for s in (-1, 1):
    sphere("Ear", (s*0.36, -0.01, 3.02), (0.075, 0.09, 0.13), skin)
    sphere("Eye white", (s*0.13, -0.305, 3.10), (0.092, 0.05, 0.075), white)
    sphere("Iris", (s*0.13, -0.35, 3.095), (0.041, 0.022, 0.043), iris)
    sphere("Pupil", (s*0.13, -0.369, 3.095), (0.021, 0.012, 0.025), black)
    brow = sphere("Raised sharp eyebrow", (s*0.14, -0.315, 3.22), (0.12, 0.035, 0.025), brows)
    brow.rotation_euler[1] = s*math.radians(12)

# Narrow glasses frames and bridge, built from rounded bars.
for s in (-1, 1):
    frame = rounded_box("Glasses frame", (s*0.13, -0.36, 3.10), (0.22, 0.035, 0.15), metal, 0.045)
    inner = rounded_box("Smoky lens", (s*0.13, -0.382, 3.10), (0.17, 0.012, 0.105), lens, 0.035)
rounded_box("Glasses bridge", (0, -0.38, 3.10), (0.075, 0.025, 0.025), metal, 0.01)
sphere("Nose", (0, -0.36, 2.98), (0.065, 0.075, 0.09), skin)
# One-sided smirk
smirk = sphere("Smug smirk", (0.045, -0.325, 2.86), (0.10, 0.022, 0.022), mouth)
smirk.rotation_euler[1] = math.radians(-10)

# Neat slick side-part hairstyle and swept comb-over.
sphere("Slick hair cap", (0, 0.015, 3.34), (0.37, 0.33, 0.19), hair, 40, 24)
sphere("Hair side left", (-0.31, 0.005, 3.18), (0.08, 0.25, 0.20), hair)
sphere("Hair side right", (0.31, 0.005, 3.18), (0.08, 0.25, 0.20), hair)
for loc, scale, angle in [
    ((-0.14, -0.18, 3.43), (0.25, 0.15, 0.075), -0.12),
    ((0.08, -0.17, 3.45), (0.27, 0.15, 0.075), 0.10),
    ((0.24, -0.08, 3.40), (0.18, 0.14, 0.065), 0.28),
]:
    lock = sphere("Comb-over hair sweep", loc, scale, hair)
    lock.rotation_euler[1] = angle

# ID badge and cuff details
rounded_box("Rival ID badge", (0.27, -0.225, 2.17), (0.15, 0.03, 0.20), badge_mat, 0.02)
rounded_box("Badge stripe", (0.27, -0.244, 2.20), (0.07, 0.012, 0.045), metal, 0.008)
for z in (2.31, 2.12, 1.98):
    sphere("Shirt button", (0, -0.216, z), (0.014, 0.01, 0.014), metal, 16, 10)

# Studio floor, camera and soft three-point lighting.
floor_mat = material("Studio floor", (0.065, 0.078, 0.095), 0.82)
rounded_box("Floor", (0, 0, 0.015), (200, 200, 0.03), floor_mat, 0.01)

bpy.ops.object.camera_add(location=(4.4, -8.8, 3.35))
camera = bpy.context.object
camera.name = "Rival presentation camera"
target = Vector((0, -0.02, 1.78))
camera.rotation_euler = (target-camera.location).to_track_quat("-Z", "Y").to_euler()
camera.data.type = "ORTHO"
camera.data.ortho_scale = 4.25
bpy.context.scene.camera = camera

def area_light(name, location, power, size, color, target):
    bpy.ops.object.light_add(type="AREA", location=location)
    light = bpy.context.object
    light.name = name
    light.data.energy = power
    light.data.shape = "DISK"
    light.data.size = size
    light.data.color = color
    light.rotation_euler = (Vector(target)-light.location).to_track_quat("-Z", "Y").to_euler()

area_light("Warm key", (4, -5, 7), 650, 5, (1.0, 0.82, 0.70), (0, 0, 2))
area_light("Cool fill", (-4, -3, 4), 420, 4, (0.68, 0.80, 1.0), (0, 0, 2))
area_light("Hair rim", (1, 3, 5), 750, 3, (1.0, 0.72, 0.48), (0, 0, 2.5))

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE_NEXT"
scene.render.resolution_x = 1000
scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = "AgX"
scene.world.color = (0.12, 0.12, 0.12)

bpy.ops.object.select_all(action="DESELECT")
head = bpy.data.objects.get("Rival head")
if head:
    head.select_set(True)
    bpy.context.view_layer.objects.active = head

print("OFFICE OUTBURST RIVAL V1 created. Save as Office_Outburst_Rival_v1.blend")
