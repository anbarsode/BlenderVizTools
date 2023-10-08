import bpy
import numpy as np
import os, sys
cwd = os.getcwd()
sys.path.append(cwd + '/BlenderVizTools')
from color_ramp import create_color_ramp

##### Load images and their z locations
px = 64
py = px
pz = 8
z_locs = np.linspace(0, 1, pz)
image_filenames = ['cube_data/t_10_px_%d_py_%d_pz_64/cube_z_%d.png' % (px, py, i) for i in range(pz)]
images = [bpy.data.images.load(cwd + '/' + image_filename) for image_filename in image_filenames]
loc_tol = np.min(np.diff(z_locs)) * 1e-3

##### Opening UI
# disable the opening "splash" screen
bpy.context.preferences.view.show_splash = False

# Delete the default cube and light
bpy.data.objects.remove(bpy.data.objects['Cube'], do_unlink=True)
bpy.data.objects.remove(bpy.data.objects['Light'], do_unlink=True)

# removing unnecessary workspaces
for ws in bpy.data.workspaces:
    if ws.name != 'Layout':
        override = {'workspace': ws}
        with bpy.context.temp_override(**override): bpy.ops.workspace.delete()
bpy.data.workspaces['Layout'].name = 'Rendered'
bpy.context.window.workspace = bpy.data.workspaces['Rendered']

##### For opening rendered view, with no properties or outliner, camera locked to view
# close properties, dopesheet and outliner
# Default open areas: ['PROPERTIES', 'OUTLINER', 'DOPESHEET_EDITOR', 'VIEW_3D']
for area_type in ['PROPERTIES', 'OUTLINER', 'DOPESHEET_EDITOR']:
    area = [a for a in bpy.context.window.screen.areas if a.type == area_type][0]
    override = {'space_data':area.spaces.active, 'region':area.regions[-1], 'area':area}
    with bpy.context.temp_override(**override): bpy.ops.screen.area_close()
    
# switch to rendered view upon launch
main_area = [a for a in bpy.context.window.screen.areas if a.type == 'VIEW_3D'][0]
main_space = [s for s in main_area.spaces if s.type == 'VIEW_3D'][0]
main_space.shading.type = 'RENDERED'

# remove unwanted toolbars
main_space.show_region_header = False
main_space.show_region_toolbar = False
main_space.show_region_ui = True

# Output render settings
bpy.data.objects['Camera'].location = [1.34, -1.37, 3.88]
bpy.data.objects['Camera'].rotation_euler = [0.558, 0, 0.436]
bpy.data.scenes['Scene'].render.resolution_percentage = 50
bpy.data.scenes['Scene'].render.use_border = True
bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = [0, 0, 0, 1]

bpy.data.scenes['Scene'].cycles.preview_adaptive_threshold = 1.0
bpy.data.scenes['Scene'].cycles.preview_samples = 6
bpy.data.scenes['Scene'].cycles.adaptive_threshold = 1.0
bpy.data.scenes['Scene'].cycles.samples = 6
bpy.data.scenes['Scene'].cycles.use_denoising = False
bpy.data.scenes['Scene'].cycles.caustics_reflective = False
bpy.data.scenes['Scene'].cycles.caustics_refractive = False
bpy.data.scenes['Scene'].cycles.max_bounces = 0
bpy.data.scenes['Scene'].cycles.volume_max_steps = 2

bpy.data.scenes['Scene'].eevee.taa_render_samples = 128
bpy.data.scenes['Scene'].eevee.taa_samples = 16
bpy.data.scenes['Scene'].eevee.volumetric_tile_size = '4'

# viewport display
viewport_cycles = True
if viewport_cycles: bpy.data.scenes['Scene'].render.engine = 'CYCLES'
else: bpy.data.scenes['Scene'].render.engine = 'BLENDER_EEVEE'

# lock camera to view
main_space.lock_camera = True

# copy camera params for future use or set something by hand
CAMERA_HOME_LOCATION = bpy.data.objects['Camera'].location.copy() # or set something by hand
CAMERA_HOME_ROTATION = bpy.data.objects['Camera'].rotation_euler.copy() # or set something by hand

# switch to camera view and maximize it to fit the window
override = {'area':main_area, 'region':main_area.regions[-1]}
with bpy.context.temp_override(**override):
    bpy.ops.view3d.view_camera()
    bpy.ops.view3d.view_center_camera()

'''
##### For opening shader editor by default
# find the default 3D view area
main_area = [a for a in bpy.context.window.screen.areas if a.type == 'VIEW_3D'][0]
# change its type
main_area.type = 'NODE_EDITOR'
# change the specific type
main_area.ui_type = 'ShaderNodeTree'
'''

for i in range(len(images)-1):
    # Create a cube "layer", and assign a new material to it
    # the locations have to be slightly offset in order for cycles to work properly
    loc = np.random.uniform(0.5 - loc_tol, 0.5 + loc_tol, (3))
    bpy.ops.mesh.primitive_cube_add(size=1, enter_editmode=False, align='WORLD', location = loc, scale=(1, 1, 1))
    bpy.context.active_object.name = 'Layer %d' % i
    bpy.data.materials.new(name='Material Layer %d' % i)
    mat = bpy.data.materials.get('Material Layer %d' % i)
    if bpy.context.active_object.data.materials:
        # assign to 1st material slot
        bpy.context.active_object.data.materials[0] = mat
    else:
        # no slots
        bpy.context.active_object.data.materials.append(mat)
    
    ##### create the material
    mat.use_nodes = True
    mat.node_tree.nodes.clear()
    
    # Generate a texture coordinate node and get z component
    node_tex_coord = mat.node_tree.nodes.new('ShaderNodeTexCoord')
    node_tex_coord.name = 'Texture Coordinate'
    node_tex_coord.location = [-1600, 600]

    node_z = mat.node_tree.nodes.new('ShaderNodeSeparateXYZ')
    node_z.name = 'Texture Coordinate z'
    node_z.location = [-1100, 600]
    mat.node_tree.links.new(node_z.inputs[0], node_tex_coord.outputs[0])
    
    # Generate image textures and the derived colors
    node_im = mat.node_tree.nodes.new('ShaderNodeTexImage')
    node_im.name = 'Image 0'
    node_im.location = [-1400, 0]
    node_im.image = images[i]
    mat.node_tree.links.new(node_im.inputs[0], node_tex_coord.outputs[0])
    node_red = mat.node_tree.nodes.new('ShaderNodeSeparateColor')
    node_red.name = 'Red 0'
    node_red.location = [-1100, 0]
    mat.node_tree.links.new(node_red.inputs[0], node_im.outputs[0])
    node_col = create_color_ramp(mat, name='Color Ramp 0', loc=[-900, 0], cmap_name='my_cold')
    mat.node_tree.links.new(node_col.inputs[0], node_red.outputs[0])
    
    node_im = mat.node_tree.nodes.new('ShaderNodeTexImage')
    node_im.name = 'Image 1'
    node_im.location = [-1400, 300]
    node_im.image = images[i+1]
    mat.node_tree.links.new(node_im.inputs[0], node_tex_coord.outputs[0])
    node_red = mat.node_tree.nodes.new('ShaderNodeSeparateColor')
    node_red.name = 'Red 1'
    node_red.location = [-1100, 300]
    mat.node_tree.links.new(node_red.inputs[0], node_im.outputs[0])
    node_col = create_color_ramp(mat, name='Color Ramp 1', loc=[-900, 300], cmap_name='my_cold')
    mat.node_tree.links.new(node_col.inputs[0], node_red.outputs[0])
    
    # Create pairwise interpolated colors
    node_maprange = mat.node_tree.nodes.new('ShaderNodeMapRange')
    node_maprange.name = 'Map Range'
    node_maprange.location = [-900, 600]
    node_maprange.inputs[1].default_value = z_locs[i]
    node_maprange.inputs[2].default_value = z_locs[i+1]
    mat.node_tree.links.new(node_maprange.inputs[0], node_z.outputs[2])
    
    node_interp_color = mat.node_tree.nodes.new('ShaderNodeMix')
    node_interp_color.name = 'Color interpolation'
    node_interp_color.location = [-600, 300]
    node_interp_color.data_type = 'RGBA'
    mat.node_tree.links.new(node_interp_color.inputs[0], node_maprange.outputs[0])
    node_col = mat.node_tree.nodes.get('Color Ramp 0')
    mat.node_tree.links.new(node_interp_color.inputs[6], node_col.outputs[0])
    node_col = mat.node_tree.nodes.get('Color Ramp 1')
    mat.node_tree.links.new(node_interp_color.inputs[7], node_col.outputs[0])
    
    node_compare = mat.node_tree.nodes.new('ShaderNodeMath')
    node_compare.operation = 'COMPARE'
    node_compare.name = 'Compare'
    node_compare.location = [-900, 800]
    mat.node_tree.links.new(node_compare.inputs[0], node_z.outputs[2])
    node_compare.inputs[1].default_value = 0.5 * (z_locs[i+1] + z_locs[i])
    node_compare.inputs[2].default_value = 0.5 * (z_locs[i+1] - z_locs[i])
    
    node_volume_color = mat.node_tree.nodes.new('ShaderNodeMix')
    node_volume_color.name = 'Region color'
    node_volume_color.location = [-400, 300]
    node_volume_color.data_type = 'RGBA'
    mat.node_tree.links.new(node_volume_color.inputs[0], node_compare.outputs[0])
    node_volume_color.inputs[6].default_value = [0, 0, 0, 1]
    mat.node_tree.links.new(node_volume_color.inputs[7], node_interp_color.outputs[2])
    
    # Generate final emisson
    node_emit = mat.node_tree.nodes.new('ShaderNodeEmission')
    node_emit.name = 'Final Emission'
    node_emit.location = [-200, 300]
    mat.node_tree.links.new(node_emit.inputs[0], node_volume_color.outputs[2])
    
    node_out = mat.node_tree.nodes.new('ShaderNodeOutputMaterial')
    node_out.location = [0, 300]
    mat.node_tree.links.new(node_out.inputs[1], node_emit.outputs[0])

# Put the object layers in a collection
bpy.ops.object.select_all(action = 'DESELECT')
bpy.ops.object.select_pattern(pattern = "Layer *")
bpy.ops.object.move_to_collection(collection_index = 0, is_new = True, new_collection_name = 'Cube 1' )
bpy.ops.object.select_all(action = 'DESELECT')

##### Setting a HOME view, with a "button" to return to it
# set
class BVT_OT_set_home_view(bpy.types.Operator):
    """
    Sets the HOME view
    """
    
    bl_idname = "bvt.set_home_view"
    bl_label = "Set as HOME view"

    def execute(self, context):
        global CAMERA_HOME_LOCATION, CAMERA_HOME_ROTATION
        CAMERA_HOME_LOCATION = bpy.data.objects['Camera'].location.copy()
        CAMERA_HOME_ROTATION = bpy.data.objects['Camera'].rotation_euler.copy()
        return {'FINISHED'}

# go to
class BVT_OT_goto_home_view(bpy.types.Operator):
    """
    Takes you to the HOME view
    """
    
    bl_idname = "bvt.goto_home_view"
    bl_label = "Go to HOME view"

    def execute(self, context):
        global main_space
        main_space.shading.type = 'RENDERED'
        if viewport_cycles: bpy.data.scenes['Scene'].render.engine = 'CYCLES'
        else: bpy.data.scenes['Scene'].render.engine = 'BLENDER_EEVEE'
        
        bpy.data.objects['Camera'].location = CAMERA_HOME_LOCATION.copy()
        bpy.data.objects['Camera'].rotation_euler = CAMERA_HOME_ROTATION.copy()
        
        override = {'area':context.area, 'region':context.region}
        with bpy.context.temp_override(**override):
            if context.area.spaces[0].region_3d.view_perspective != 'CAMERA':
                bpy.ops.view3d.view_camera()
            bpy.ops.view3d.view_center_camera()
        return {'FINISHED'}

##### Printing current camera coordinates
class BVT_OT_print_camera_coords(bpy.types.Operator):
    """
    Print camera coordinates and orientation to console.
    """
    
    bl_idname = "bvt.print_camera_coords"
    bl_label = "Print view"

    def execute(self, context):
        loc = [x for x in bpy.data.objects['Camera'].location]
        rot = [x for x in bpy.data.objects['Camera'].rotation_euler]
        print('\nCurrent location (Meters):\n\t', repr(loc))
        print('Current orientation (Euler XYZ, radians):\n\t', repr(rot), '\n')
        return {'FINISHED'}

##### Rendering an image
class BVT_OT_render_cycles(bpy.types.Operator):
    """
    Render the current view using ray tracing to create a PNG image. Slow, but gives realistic results.
    """
    
    bl_idname = "bvt.render_cycles"
    bl_label = "Render image (cycles)"

    def execute(self, context):
        global main_space
        main_space.shading.type = 'WIREFRAME'
        bpy.data.scenes['Scene'].render.engine = 'CYCLES'
        bpy.data.scenes['Scene'].render.filepath = bpy.context.scene.output_image_name
        bpy.data.scenes['Scene'].cycles.volume_max_steps = 16
        bpy.ops.render.render(write_still = True)
        
        # restore viewport settings
        main_space.shading.type = 'RENDERED'
        bpy.data.scenes['Scene'].cycles.volume_max_steps = 2
        if not viewport_cycles: bpy.data.scenes['Scene'].render.engine = 'BLENDER_EEVEE'
        return {'FINISHED'}

class BVT_OT_render_eevee(bpy.types.Operator):
    """
    Render the current view using eevee to create a PNG image. Fast, but may give noisy artifacts.
    """
    
    bl_idname = "bvt.render_eevee"
    bl_label = "Render image (eevee)"

    def execute(self, context):
        global main_space
        main_space.shading.type = 'WIREFRAME'
        bpy.data.scenes['Scene'].render.engine = 'BLENDER_EEVEE'
        bpy.data.scenes['Scene'].render.filepath = bpy.context.scene.output_image_name
        bpy.data.scenes['Scene'].eevee.volumetric_tile_size = '2'
        bpy.ops.render.render(write_still = True)
        
        # restore viewport settings
        main_space.shading.type = 'RENDERED'
        bpy.data.scenes['Scene'].eevee.volumetric_tile_size = '4'
        if viewport_cycles: bpy.data.scenes['Scene'].render.engine = 'CYCLES'
        return {'FINISHED'}

##### UI Panel in the sidebar (The "N" panel.)
class VIEW3D_PT_BVTFloatingPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BlenderVizTools'
    bl_label = 'Blender Viz Tools'
    
    def draw(self, context):
        layout = self.layout
        layout.operator(BVT_OT_goto_home_view.bl_idname, icon='HOME')
        layout.operator(BVT_OT_print_camera_coords.bl_idname, icon='TRACKER')
        layout.operator(BVT_OT_set_home_view.bl_idname, icon='PINNED')
        layout.prop(bpy.context.scene, 'output_image_name')
        layout.operator(BVT_OT_render_cycles.bl_idname, icon='RESTRICT_RENDER_OFF')
        layout.operator(BVT_OT_render_eevee.bl_idname, icon='RESTRICT_RENDER_OFF')

classes = [VIEW3D_PT_BVTFloatingPanel, BVT_OT_goto_home_view, BVT_OT_print_camera_coords, BVT_OT_set_home_view, BVT_OT_render_cycles, BVT_OT_render_eevee]

def register():
    for cls in classes: bpy.utils.register_class(cls)
    
    bpy.types.Scene.output_image_name = bpy.props.StringProperty \
      (
        name = "Output",
        description = "Name of the output image file. Default: ./image.png",
        default = "image"
      )

def unregister():
    del bpy.types.Scene.output_image_name
    for cls in classes: bpy.utils.unregister_class(cls)

if __name__ == '__main__':
    register()
