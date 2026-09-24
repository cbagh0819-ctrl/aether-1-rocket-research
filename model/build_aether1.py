import bpy
import math
from pathlib import Path
from mathutils import Vector

OUTPUT_DIR = Path(__file__).resolve().parent


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.materials, bpy.data.curves, bpy.data.meshes, bpy.data.cameras, bpy.data.lights):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)


def material(name, color, metallic=0.0, roughness=0.35, emission=None, emission_strength=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    if emission:
        bsdf.inputs['Emission Color'].default_value = (*emission, 1.0)
        bsdf.inputs['Emission Strength'].default_value = emission_strength
    return mat


def emission_material(name, color, strength=1.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    mat.node_tree.nodes.clear()
    output = mat.node_tree.nodes.new('ShaderNodeOutputMaterial')
    emission = mat.node_tree.nodes.new('ShaderNodeEmission')
    emission.inputs['Color'].default_value = (*color, 1.0)
    emission.inputs['Strength'].default_value = strength
    mat.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])
    return mat


def translucent_emission_material(name, color, strength, opacity):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, opacity)
    mat.use_nodes = True
    mat.node_tree.nodes.clear()
    output = mat.node_tree.nodes.new('ShaderNodeOutputMaterial')
    transparent = mat.node_tree.nodes.new('ShaderNodeBsdfTransparent')
    emission = mat.node_tree.nodes.new('ShaderNodeEmission')
    emission.inputs['Color'].default_value = (*color, 1.0)
    emission.inputs['Strength'].default_value = strength
    mix = mat.node_tree.nodes.new('ShaderNodeMixShader')
    mix.inputs[0].default_value = opacity
    mat.node_tree.links.new(transparent.outputs['BSDF'], mix.inputs[1])
    mat.node_tree.links.new(emission.outputs['Emission'], mix.inputs[2])
    mat.node_tree.links.new(mix.outputs['Shader'], output.inputs['Surface'])
    mat.surface_render_method = 'BLENDED'
    return mat


def assign(obj, mat):
    obj.data.materials.append(mat)
    return obj


def cyl(name, radius, depth, loc, mat, vertices=96, bevel=0.04, radius2=None):
    if radius2 is None:
        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    else:
        bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=radius, radius2=radius2, depth=depth, location=loc)
    obj = bpy.context.object
    obj.name = name
    assign(obj, mat)
    if bevel:
        mod = obj.modifiers.new('Soft machined edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        obj.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
    return obj


def torus(name, major_radius, minor_radius, loc, mat, rotation=None):
    bpy.ops.mesh.primitive_torus_add(major_segments=96, minor_segments=16, major_radius=major_radius, minor_radius=minor_radius, location=loc)
    obj = bpy.context.object
    obj.name = name
    if rotation:
        obj.rotation_euler = rotation
    assign(obj, mat)
    return obj


def rod_between(name, start, end, radius, mat, vertices=24):
    start, end = Vector(start), Vector(end)
    direction = end - start
    mid = (start + end) * 0.5
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=direction.length, location=mid)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()
    assign(obj, mat)
    bevel = obj.modifiers.new('Edge glint', 'BEVEL')
    bevel.width = min(radius * 0.22, 0.04)
    bevel.segments = 2
    obj.modifiers.new('Normals', 'WEIGHTED_NORMAL')
    return obj


def tube(name, points, radius, mat, resolution=12):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = 16
    curve.bevel_depth = radius
    curve.bevel_resolution = resolution
    spline = curve.splines.new('BEZIER')
    spline.bezier_points.add(len(points) - 1)
    for bp, pt in zip(spline.bezier_points, points):
        bp.co = pt
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    assign(obj, mat)
    return obj


def bell_shell(name, outer, inner, outer_mat, inner_mat, segments=128):
    # Ring surfaces give a clean open nozzle with a visible insulating inner wall.
    verts_outer, faces_outer = [], []
    for radius, z in outer:
        for i in range(segments):
            a = 2 * math.pi * i / segments
            verts_outer.append((radius * math.cos(a), radius * math.sin(a), z))
    for ring in range(len(outer) - 1):
        for i in range(segments):
            a = ring * segments + i
            b = ring * segments + (i + 1) % segments
            faces_outer.append((a, b, b + segments, a + segments))
    mesh = bpy.data.meshes.new(name + ' outer mesh')
    mesh.from_pydata(verts_outer, [], faces_outer)
    mesh.materials.append(outer_mat)
    obj = bpy.data.objects.new(name + ' / alloy bell', mesh)
    bpy.context.collection.objects.link(obj)
    for poly in mesh.polygons:
        poly.use_smooth = True

    verts_inner, faces_inner = [], []
    for radius, z in inner:
        for i in range(segments):
            a = 2 * math.pi * i / segments
            verts_inner.append((radius * math.cos(a), radius * math.sin(a), z))
    for ring in range(len(inner) - 1):
        for i in range(segments):
            a = ring * segments + i
            b = ring * segments + (i + 1) % segments
            faces_inner.append((a, a + segments, b + segments, b))
    mesh = bpy.data.meshes.new(name + ' inner mesh')
    mesh.from_pydata(verts_inner, [], faces_inner)
    mesh.materials.append(inner_mat)
    obj = bpy.data.objects.new(name + ' / ceramic liner', mesh)
    bpy.context.collection.objects.link(obj)
    for poly in mesh.polygons:
        poly.use_smooth = True

    # Rolled exit lip and throat band.
    torus(name + ' exit rim', 1.57, 0.115, (0, 0, -3.08), outer_mat)
    torus(name + ' throat band', 0.46, 0.08, (0, 0, -0.18), gold)


def label(name, body, cam, x, y, size, mat, align='LEFT'):
    curve = bpy.data.curves.new(name, 'FONT')
    curve.body = body
    curve.size = size
    curve.align_x = align
    curve.extrude = 0.0
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    local = Vector((x, y, -12.0))
    obj.location = cam.matrix_world @ local
    obj.rotation_euler = cam.rotation_euler
    assign(obj, mat)
    return obj


def screen_line(name, cam, x1, y1, x2, y2, mat, thickness=0.012):
    p1 = cam.matrix_world @ Vector((x1, y1, -12.0))
    p2 = cam.matrix_world @ Vector((x2, y2, -12.0))
    return tube(name, [p1, p2], thickness, mat, resolution=3)


clear_scene()
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE_NEXT'
scene.render.resolution_x = 1600
scene.render.resolution_y = 1400
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = False
scene.render.image_settings.color_mode = 'RGBA'
scene.render.filepath = str(OUTPUT_DIR / 'AETHER-1_concept.png')
scene.render.resolution_percentage = 100
scene.render.engine = 'BLENDER_EEVEE_NEXT'
scene.render.image_settings.color_depth = '8'
scene.render.resolution_percentage = 100
scene.render.fps = 24
scene.frame_start = 1
scene.frame_end = 120
scene.view_settings.view_transform = 'AgX'
scene.render.image_settings.color_mode = 'RGBA'

# Restrained graphite, titanium, ceramic, and hydrogen-blue palette.
graphite = material('01 | Graphite ceramic', (0.028, 0.052, 0.075), 0.72, 0.27)
titanium = material('02 | Brushed titanium', (0.34, 0.47, 0.55), 0.78, 0.24)
dark_titanium = material('03 | Shadowed alloy', (0.09, 0.15, 0.20), 0.82, 0.29)
ceramic = material('04 | Hot-side ceramic', (0.11, 0.065, 0.045), 0.22, 0.34)
gold = material('05 | Heat barrier / amber', (0.95, 0.43, 0.10), 0.62, 0.24, (0.22, 0.045, 0.005), 0.35)
hydrogen = material('06 | LH2 flow marker', (0.045, 0.58, 0.72), 0.48, 0.24, (0.01, 0.25, 0.38), 0.7)
white = material('07 | Type / ivory', (0.77, 0.87, 0.90), 0.15, 0.4, (0.26, 0.38, 0.42), 0.5)
muted = material('08 | Muted type', (0.25, 0.42, 0.49), 0.1, 0.5, (0.06, 0.14, 0.18), 0.35)
ui_white = emission_material('UI | ivory', (0.72, 0.86, 0.89), 1.25)
ui_cyan = emission_material('UI | cyan', (0.06, 0.68, 0.82), 1.35)
ui_muted = emission_material('UI | muted blue', (0.20, 0.38, 0.45), 0.9)
flame_outer = translucent_emission_material('Flame | outer amber', (1.0, 0.075, 0.008), 1.8, 0.32)
flame_mid = translucent_emission_material('Flame | gold', (1.0, 0.34, 0.035), 2.6, 0.66)
flame_core = emission_material('Flame | hot core', (1.0, 0.82, 0.48), 4.2)
bg = material('09 | Background', (0.009, 0.018, 0.030), 0.1, 0.8)

# Top interface and pressure vessel.
cyl('Vehicle interface / load ring', 1.26, 0.30, (0, 0, 3.20), titanium, bevel=0.055)
cyl('Upper attachment collar', 1.08, 0.34, (0, 0, 2.94), graphite, bevel=0.04)
for z, r in [(3.35, 1.17), (3.03, 1.24), (2.80, 1.02)]:
    torus('Machined flange bead', r, 0.035, (0, 0, z), gold if z == 3.03 else dark_titanium)

cyl('Thermal reactor pressure shell', 0.88, 1.65, (0, 0, 1.86), graphite, bevel=0.13)
cyl('Core shield band', 0.95, 0.44, (0, 0, 1.85), dark_titanium, bevel=0.055)
cyl('Lower reflector housing', 0.82, 0.66, (0, 0, 0.72), titanium, bevel=0.09)
cyl('Throat transition housing', 0.63, 0.44, (0, 0, 0.21), graphite, bevel=0.05)
for z, radius in [(2.63, 0.89), (2.39, 0.90),  (1.30, 0.93), (0.99, 0.88), (0.48, 0.73)]:
    torus('Vessel perimeter bead', radius, 0.028, (0, 0, z), titanium)

# Abstract sealed core indicator under the shield window, with broad thermal ribs.
cyl('Core window / opaque amber insert', 0.63, 0.18, (0, 0, 1.86), gold, bevel=0.03)
cyl('Core window bezel', 0.70, 0.12, (0, 0, 1.98), dark_titanium, bevel=0.02)
for i in range(12):
    a = 2 * math.pi * i / 12
    x, y = 0.92 * math.cos(a), 0.92 * math.sin(a)
    cyl('Radial shield fin %02d' % i, 0.09, 0.66, (x, y, 1.78), titanium, vertices=24, bevel=0.018)

# LH2 supply line pair: clearly marked external runs, kept at concept scale.
for side in (-1, 1):
    x = side * 0.95
    tube('LH2 supply manifold', [(side*1.12, -0.10, 3.75), (side*1.32, -0.10, 3.48), (side*1.32, -0.10, 3.05), (side*1.10, -0.10, 2.75), (side*0.95, -0.10, 2.54)], 0.085, hydrogen)
    cyl('Feed coupling', 0.14, 0.18, (side*1.12, -0.10, 3.73), titanium, bevel=0.025)
    torus('Feed coupling band', 0.15, 0.025, (side*1.12, -0.10, 3.73), gold)

# Nozzle shell and warm-side liner.
outer_profile = [
    (0.70, 0.50), (0.61, 0.25), (0.50, -0.05), (0.46, -0.30),
    (0.54, -0.64), (0.70, -1.00), (0.92, -1.40), (1.17, -1.82),
    (1.40, -2.22), (1.56, -2.62), (1.66, -3.06)
]
inner_profile = [
    (0.64, 0.50), (0.55, 0.25), (0.43, -0.05), (0.39, -0.30),
    (0.47, -0.64), (0.63, -1.00), (0.85, -1.40), (1.10, -1.82),
    (1.33, -2.22), (1.49, -2.62), (1.59, -3.06)
]
bell_shell('Adaptive expansion nozzle', outer_profile, inner_profile, titanium, ceramic)

# Layered, stylized exhaust shells. Their looping transform keys create a
# visible flame flicker in the Blender timeline; this is a visual effect only.
def flame_layer(name, profile, mat, phase_offset, segments=72):
    verts, faces = [], []
    max_depth = abs(min(z for radius, z in profile))
    for radius, z in profile:
        depth = abs(z) / max_depth
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            wave = 0.045 * depth * math.sin(4 * angle + 9 * depth + phase_offset)
            wave += 0.022 * depth * math.sin(7 * angle - 13 * depth + phase_offset * 1.7)
            r = radius * (1.0 + wave)
            axial = z + 0.035 * depth * math.sin(3 * angle + 7 * depth + phase_offset)
            verts.append((r * math.cos(angle), r * math.sin(angle), axial))
    for ring in range(len(profile) - 1):
        for i in range(segments):
            a = ring * segments + i
            b = ring * segments + (i + 1) % segments
            faces.append((a, b, b + segments, a + segments))
    mesh = bpy.data.meshes.new(name + ' mesh')
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    for poly in mesh.polygons:
        poly.use_smooth = True
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = (0, 0, -3.055)
    obj['visual_effect'] = 'Stylized exhaust animation; not a thrust or combustion simulation.'

    # Ten breathing pulses over five seconds at 24 fps, with slightly different
    # phases so the nested flame tongues do not move as one rigid cone.
    for frame in range(1, 121):
        t = (frame - 1) / 119.0
        phase = 2 * math.pi * 10 * t + phase_offset
        fast = 2 * math.pi * 23 * t + phase_offset * 2.0
        radial = 1.0 + 0.045 * math.sin(phase * 0.68) + 0.018 * math.sin(fast)
        length = 1.0 + 0.11 * math.sin(phase) + 0.045 * math.sin(fast)
        obj.scale = (radial, radial, length)
        obj.rotation_euler[2] = 0.045 * math.sin(phase * 0.61) + 0.018 * math.sin(fast)
        obj.keyframe_insert(data_path='scale', frame=frame, group='Flame flicker')
        obj.keyframe_insert(data_path='rotation_euler', frame=frame, group='Flame flicker')
    return obj


flame_layer('Exhaust plume / outer tongue', [
    (1.52, 0.00), (1.70, -0.28), (1.52, -0.76), (1.18, -1.32),
    (0.78, -1.98), (0.38, -2.76), (0.025, -3.65)
], flame_outer, 0.15)
flame_layer('Exhaust plume / gold layer', [
    (1.20, 0.00), (1.31, -0.22), (1.11, -0.64), (0.82, -1.15),
    (0.50, -1.73), (0.20, -2.36), (0.012, -2.96)
], flame_mid, 1.1)
flame_layer('Exhaust plume / hot core', [
    (0.84, 0.00), (0.87, -0.16), (0.70, -0.47), (0.46, -0.90),
    (0.24, -1.38), (0.075, -1.88), (0.008, -2.24)
], flame_core, 2.25)

# Gimbal and nozzle support struts.
torus('Gimbal outer ring', 0.89, 0.075, (0, 0, -0.45), dark_titanium)
torus('Gimbal inner ring', 0.69, 0.055, (0, 0, -0.45), gold)
for i in range(4):
    a = math.radians(45 + 90 * i)
    rod_between('Gimbal strut', (1.05*math.cos(a), 1.05*math.sin(a), 0.18), (0.70*math.cos(a), 0.70*math.sin(a), -0.86), 0.075, titanium)

# Distinct small details on the mount ring, not functional hardware dimensions.
for i in range(16):
    a = 2 * math.pi * i / 16
    x, y = 1.18 * math.cos(a), 1.18 * math.sin(a)
    cyl('Mount ring fastener', 0.045, 0.045, (x, y, 3.37), gold if i % 4 == 0 else dark_titanium, vertices=24, bevel=0.008)

# Small brand plate on front side of the shield canister.
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -0.888, 2.08))
badge = bpy.context.object
badge.name = 'AETHER identification plaque'
badge.dimensions = (0.92, 0.06, 0.25)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
badge.data.materials.append(dark_titanium)
bev = badge.modifiers.new('Plaque bevel', 'BEVEL'); bev.width = 0.045; bev.segments = 3
badge.modifiers.new('Plaque normals', 'WEIGHTED_NORMAL')

# Ground plane and subtle halo platform for a product-render read.
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -8.0))
floor = bpy.context.object
floor.name = 'Studio floor'
assign(floor, bg)

# Camera and studio lighting.
bpy.ops.object.camera_add(location=(10.5, -17.5, 9.2))
cam = bpy.context.object
cam.name = 'Presentation camera'
target = Vector((0, 0, 0.25))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 16.0
scene.camera = cam

def area(name, loc, power, color, size, target=(0, 0, 0)):
    bpy.ops.object.light_add(type='AREA', location=loc)
    light = bpy.context.object
    light.name = name
    light.data.energy = power
    light.data.color = color
    light.data.shape = 'DISK'
    light.data.size = size
    light.rotation_euler = (Vector(target) - light.location).to_track_quat('-Z', 'Y').to_euler()

area('Key / cool softbox', (6, -8, 10), 1900, (0.60, 0.82, 1.0), 7.0, (0, 0, 0.5))
area('Rim / cyan', (-6, 1, 6), 2200, (0.08, 0.58, 0.82), 5.0, (0, 0, 0.3))
area('Rim / warm', (2, 5, 2), 1500, (1.0, 0.35, 0.12), 4.5, (0, 0, -0.4))
area('Nozzle fill', (-3, -4, -2.5), 850, (0.72, 0.38, 0.18), 3.5, (0, 0, -1.7))

world = bpy.data.worlds.new('Deep space studio') if not bpy.data.worlds else bpy.data.worlds[0]
scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.004, 0.012, 0.022, 1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.35

# Camera-space title and engineering callouts.
label('Title', 'AETHER-1', cam, -5.0, 4.65, 0.54, ui_white)
label('Subtitle', 'THERMAL PROPULSION CONCEPT  /  LH2', cam, -4.98, 4.20, 0.18, ui_cyan)
screen_line('Title rule', cam, -5.0, 4.05, -2.45, 4.05, ui_cyan, 0.012)
label('Class', 'HIGH-Isp  /  VACUUM OPTIMIZED', cam, 5.0, 4.55, 0.16, ui_white, 'RIGHT')
label('Propellant marker', 'H2  ->  CORE  ->  EXPANSION', cam, 5.0, 4.25, 0.14, ui_cyan, 'RIGHT')
label('Playback note', 'PLAY TIMELINE  /  120-FRAME FLAME LOOP', cam, 5.0, 3.92, 0.11, ui_cyan, 'RIGHT')

label('Target heading', 'DESIGN TARGET', cam, -5.0, -3.98, 0.16, ui_cyan)
label('Target figure', '~50%', cam, -5.0, -4.45, 0.48, ui_white)
label('Target caption', 'LESS PROPELLANT MASS*', cam, -3.46, -4.37, 0.17, ui_white)
label('Target footnote', '*Mission-specific target; not validated by this model.', cam, -5.0, -4.68, 0.12, ui_muted)
label('Right note 1', 'CLOSED-CORE HEAT EXCHANGER', cam, 5.0, -3.98, 0.14, ui_white, 'RIGHT')
label('Right note 2', 'NON-COMBUSTING THERMAL CYCLE', cam, 5.0, -4.28, 0.13, ui_muted, 'RIGHT')
label('Right note 3', 'CONCEPT GEOMETRY  /  NOT FLIGHT HARDWARE', cam, 5.0, -4.68, 0.105, ui_muted, 'RIGHT')

# Add restrained screen-frame accents.
screen_line('Left frame', cam, -5.0, 4.00, -5.0, -5.00, ui_muted, 0.006)
screen_line('Right frame', cam, 5.0, 4.00, 5.0, -5.00, ui_muted, 0.006)

# Render settings and useful opening view.
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = str(OUTPUT_DIR / 'AETHER-1_concept.png')
scene.render.resolution_x = 1600
scene.render.resolution_y = 1400
scene.render.resolution_percentage = 100
scene.render.engine = 'BLENDER_EEVEE_NEXT'
scene.camera.data.lens = 50
scene.render.image_settings.color_mode = 'RGBA'
scene.render.film_transparent = False
scene.view_settings.view_transform = 'AgX'
scene.render.resolution_percentage = 100
scene.render.use_file_extension = True
scene.world.color = (0.01, 0.02, 0.03)
scene.camera.data.dof.use_dof = False
scene.render.filepath = str(OUTPUT_DIR / 'AETHER-1_concept.png')
scene.timeline_markers.new('FLAME ON', frame=1)
scene.timeline_markers.new('LOOP POINT', frame=120)
scene.frame_set(1)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.region_3d.view_perspective = 'CAMERA'
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_DIR / 'AETHER-1.blend'))
bpy.ops.render.render(write_still=True)
