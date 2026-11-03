import bpy
from mathutils import Vector

# OFFICE OUTBURST — RIVAL BASIC RIG V1
# Run this AFTER office_outburst_rival_v1.py in the same Blender scene.
# Adds a usable starter armature and rigidly attaches the existing character
# parts to appropriate bones. This is a blockout rig, not production skinning.

scene = bpy.context.scene
# Do not depend on one exact object name: Blender may append .001 or the
# user may rename the head. Confirm the character is present by its mesh count.
character_meshes = [
    obj for obj in scene.objects
    if obj.type == "MESH" and obj.name != "Floor"
]
if len(character_meshes) < 10:
    raise RuntimeError(
        "Rival model not found in this scene. Open the saved rival character "
        "project first, then run this rig script in that same scene."
    )

# Remove an earlier generated rig if this script is rerun.
old = bpy.data.objects.get("Rival_Rig")
if old:
    bpy.data.objects.remove(old, do_unlink=True)

arm_data = bpy.data.armatures.new("Rival_Rig_Armature")
rig = bpy.data.objects.new("Rival_Rig", arm_data)
scene.collection.objects.link(rig)
bpy.context.view_layer.objects.active = rig
rig.select_set(True)
bpy.ops.object.mode_set(mode="EDIT")

bones = {}
def bone(name, head, tail, parent=None, connected=False):
    b = arm_data.edit_bones.new(name)
    b.head = head
    b.tail = tail
    if parent:
        b.parent = bones[parent]
        b.use_connect = connected
    bones[name] = b

bone("root", (0,0,0.12), (0,0,0.48))
bone("hips", (0,0,1.35), (0,0,1.58), "root")
bone("spine", (0,0,1.58), (0,0,2.20), "hips")
bone("chest", (0,0,2.20), (0,0,2.52), "spine")
bone("neck", (0,0,2.52), (0,0,2.78), "chest")
bone("head", (0,0,2.78), (0,0,3.35), "neck")
for side, sign in (("L",-1),("R",1)):
    bone(side+"_thigh", (sign*0.16,0,1.48), (sign*0.19,0,0.91), "hips")
    bone(side+"_shin", (sign*0.19,0,0.91), (sign*0.19,0,0.28), side+"_thigh")
    bone(side+"_foot", (sign*0.19,0,0.28), (sign*0.19,-0.32,0.14), side+"_shin")
    bone(side+"_upper_arm", (sign*0.38,0,2.40), (sign*0.58,-0.02,2.04), "chest")
    bone(side+"_forearm", (sign*0.58,-0.02,2.04), (sign*0.42,-0.13,1.79), side+"_upper_arm")
    bone(side+"_hand", (sign*0.42,-0.13,1.79), (sign*0.42,-0.14,1.62), side+"_forearm")

bpy.ops.object.mode_set(mode="OBJECT")

# Rigid bone parenting keeps each existing piece attached to the closest
# semantic body part. It allows basic posing; smooth deformation is a later step.
def choose_bone(obj):
    n = obj.name.lower()
    loc = obj.matrix_world.translation
    side = "L" if n.startswith("l ") or n.startswith("l_") else ("R" if n.startswith("r ") or n.startswith("r_") else None)

    if any(k in n for k in ("shoe", "lower leg", "upper leg", "trouser")):
        if side:
            if "shoe" in n: return side+"_foot"
            if "lower leg" in n: return side+"_shin"
            return side+"_thigh"
        # neutral waist/other trouser parts
        return "hips"
    if any(k in n for k in ("upper sleeve", "shoulder")) and side:
        return side+"_upper_arm"
    if "forearm" in n and side:
        return side+"_forearm"
    if any(k in n for k in ("hand", "watch")) and side:
        return side+"_hand"
    if any(k in n for k in ("head", "jaw", "ear", "eye", "iris", "pupil", "eyebrow",
                            "glasses", "lens", "nose", "smirk", "hair")):
        return "head"
    if "neck" in n:
        return "neck"
    if any(k in n for k in ("shirt", "tie", "badge", "button", "collar", "buckle")):
        return "chest" if "badge" in n or "button" in n or "collar" in n else "spine"
    if side and "joint" in n:
        if "upper leg" in n: return side+"_thigh"
        if "lower leg" in n: return side+"_shin"
    return "spine"

for obj in list(scene.objects):
    if obj == rig or obj.type not in {"MESH", "EMPTY"}:
        continue
    # Keep floor/stage independent.
    if obj.name in {"Floor"}:
        continue
    bone_name = choose_bone(obj)
    if bone_name not in arm_data.bones:
        bone_name = "spine"
    obj.parent = rig
    obj.parent_type = "BONE"
    obj.parent_bone = bone_name

# Make armature visible in front of the character for posing.
rig.show_in_front = True
rig.data.display_type = "OCTAHEDRAL"
rig.hide_render = True

# Select rig and switch to pose mode.
bpy.ops.object.select_all(action="DESELECT")
rig.select_set(True)
bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode="POSE")

print("RIVAL BASIC RIG V1 created. Select bones and rotate to test. Save a new copy before posing.")
