import bpy
from color_ramp import *
from appearance import *
from rendering import *
from background import *

##### Viewing
# set
class BVT_OT_set_home_view(bpy.types.Operator):
    """
    Set the current view as the HOME view
    """
    
    bl_idname = 'bvt.set_home_view'
    bl_label = ''

    def execute(self, context):
        global CAMERA_HOME_LOCATION, CAMERA_HOME_ROTATION
        
        CAMERA_HOME_LOCATION = bpy.data.objects['Camera'].location.copy()
        CAMERA_HOME_ROTATION = bpy.data.objects['Camera'].rotation_euler.copy()
        
        return {'FINISHED'}

# go to
class BVT_OT_goto_home_view(bpy.types.Operator):
    """
    Go to the HOME view
    """
    
    bl_idname = 'bvt.goto_home_view'
    bl_label = ''

    def execute(self, context):        
        bpy.data.objects['Camera'].location = CAMERA_HOME_LOCATION.copy()
        bpy.data.objects['Camera'].rotation_euler = CAMERA_HOME_ROTATION.copy()
        
        override = {'area':context.area, 'region':context.region}
        with bpy.context.temp_override(**override):
            if context.area.spaces[0].region_3d.view_perspective != 'CAMERA':
                bpy.ops.view3d.view_camera()
            bpy.ops.view3d.view_center_camera()
        return {'FINISHED'}

# refresh
class BVT_OT_refresh_view(bpy.types.Operator):
    """
    Refresh the view
    """
    
    bl_idname = 'bvt.refresh_view'
    bl_label = 'Refresh'

    def execute(self, context):
        global VIEW_SETTINGS
        if bpy.context.scene.user_inputs.viewport_raytracing: VIEW_SETTINGS['engine'] = 'accurate'
        else: VIEW_SETTINGS['engine'] = 'fast'
        VIEW_SETTINGS['denoise'] = bpy.context.scene.user_inputs.viewport_denoise
        VIEW_SETTINGS['quality'] = bpy.context.scene.user_inputs.viewport_quality
        reset_viewport_settings(**VIEW_SETTINGS)
        
        # Reset requested layers if out of bounds
        Ntot = bpy.context.scene.user_inputs.view_layers_tot
        if bpy.context.scene.user_inputs.view_layers_N > Ntot:
            bpy.context.scene.user_inputs.view_layers_N = Ntot
        if bpy.context.scene.user_inputs.view_layers_0 > Ntot - 1:
            bpy.context.scene.user_inputs.view_layers_0 = Ntot - 1
            bpy.context.scene.user_inputs.view_layers_N = 1
        if bpy.context.scene.user_inputs.view_layers_0 + \
           bpy.context.scene.user_inputs.view_layers_N > Ntot:
            bpy.context.scene.user_inputs.view_layers_N = Ntot - \
                     bpy.context.scene.user_inputs.view_layers_0
        
        # Refresh colormap
        refresh_colormaps(bpy.context.scene.user_inputs.view_layers_0, \
                          bpy.context.scene.user_inputs.view_layers_N)
        
        return {'FINISHED'}

def auto_refresh(op, ctx): BVT_OT_refresh_view.execute(op, ctx)

# print current camera coordinates
class BVT_OT_print_camera_coords(bpy.types.Operator):
    """
    Print camera coordinates and orientation to console.
    """
    
    bl_idname = 'bvt.print_camera_coords'
    bl_label = ''

    def execute(self, context):
        loc = [x for x in bpy.data.objects['Camera'].location]
        rot = [x for x in bpy.data.objects['Camera'].rotation_euler]
        print('\nCurrent location (Meters):\n\t', repr(loc))
        print('Current orientation (Euler XYZ, radians):\n\t', repr(rot), '\n')
        return {'FINISHED'}
    
    
# Layers
def show_hide_layers(op, ctx):
    ID0 = bpy.context.scene.user_inputs.view_layers_0
    N = bpy.context.scene.user_inputs.view_layers_N
    
    for obj in bpy.data.objects:
        if obj.name[:5] == 'Layer':
            ID = int(obj.name.split()[1])
            if ID >= ID0 and ID < (ID0 + N):
                obj.hide_viewport = False
                obj.hide_render = False
            else:
                obj.hide_viewport = True
                obj.hide_render = True


##### Rendering
class BVT_OT_render(bpy.types.Operator):
    """
    Render the current view to create a PNG image.
    """
    
    bl_idname = "bvt.render"
    bl_label = "Render image"

    def execute(self, context):
        # Change to wireframe view to save computing
        global main_space, RENDER_SETTINGS
        main_space.shading.type = 'WIREFRAME'
        
        # Update RENDER_SETTINGS
        if bpy.context.scene.user_inputs.render_raytracing: RENDER_SETTINGS['engine'] = 'accurate'
        else: RENDER_SETTINGS['engine'] = 'fast'
        RENDER_SETTINGS['denoise'] = bpy.context.scene.user_inputs.render_denoise
        RENDER_SETTINGS['quality'] = bpy.context.scene.user_inputs.render_quality
        RENDER_SETTINGS['resolution'][0] = bpy.context.scene.user_inputs.output_resolution_x
        RENDER_SETTINGS['resolution'][1] = bpy.context.scene.user_inputs.output_resolution_y
        
        # Switch to rendering settings
        reset_render_settings(**RENDER_SETTINGS)
        
        # Set output path
        bpy.data.scenes['Scene'].render.filepath = bpy.context.scene.user_inputs.output_image_name
        
        # Render
        bpy.ops.render.render(write_still = True)
        
        # Restore viewport settings
        reset_viewport_settings(**VIEW_SETTINGS)
        
        # Switch back to rendered view
        main_space.shading.type = 'RENDERED'
        return {'FINISHED'}


##### All user inputs i.e. "properties"
class MyProperties(bpy.types.PropertyGroup):
    output_image_name : \
    bpy.props.StringProperty(name = 'Output', \
                             description = 'Name of the output image file. Default: ./image.png', \
                             default = 'image')
    
    viewport_raytracing : \
    bpy.props.BoolProperty(name = 'Use ray tracing', \
                           description = 'Whether to use physically accurate ray tracing based rendering using "Cycles" or to use a faster but approximate rendering engine ("Eevee")', \
                           default = False, \
                           update = auto_refresh)
    
    render_raytracing : \
    bpy.props.BoolProperty(name = 'Use ray tracing', \
                           description = 'Whether to use physically accurate ray tracing based rendering using "Cycles" or to use a faster but approximate rendering engine ("Eevee")', \
                           default = False)
    
    viewport_denoise : \
    bpy.props.BoolProperty(name = 'Denoise', \
                           description = 'Denoise the image', \
                           default = False, \
                           update = auto_refresh)
    
    render_denoise : \
    bpy.props.BoolProperty(name = 'Denoise', \
                           description = 'Denoise the image', \
                           default = False)
    
    viewport_quality : \
    bpy.props.EnumProperty(items = [('low', 'low', '', 0), \
                                    ('medium', 'medium', '', 1), \
                                    ('good', 'good', '', 2), \
                                    ('high', 'high', '', 3)], \
                           name = 'Quality', \
                           description = 'Set the quality of the view', \
                           default = 1, \
                           update = auto_refresh)
    
    render_quality : \
    bpy.props.EnumProperty(items = [('low', 'low', '', 0), \
                                    ('medium', 'medium', '', 1), \
                                    ('good', 'good', '', 2), \
                                    ('high', 'high', '', 3)], \
                           name = 'Quality', \
                           description = 'Set the quality of the image', \
                           default = 2)
    
    output_resolution_x : \
    bpy.props.IntProperty(name = 'px', \
                          description = 'Horizontal resolution of the output image', \
                          default = 960, \
                          min = 0, \
                          max = 10000, \
                          update = auto_refresh)
    
    output_resolution_y : \
    bpy.props.IntProperty(name = 'py', \
                          description = 'Vertical resolution of the output image', \
                          default = 540, \
                          min = 0, \
                          max = 10000, \
                          update = auto_refresh)
    
    view_layers_N : \
    bpy.props.IntProperty(name = 'N', \
                          description = 'View these many layers only', \
                          default = 1, \
                          min = 1, \
                          max = 2048, \
                          update = show_hide_layers)
    
    view_layers_0 : \
    bpy.props.IntProperty(name = 'Start', \
                          description = 'View layers starting from this one', \
                          default = 0, \
                          min = 0, \
                          max = 2048, \
                          update = show_hide_layers)
    
    view_layers_tot : \
    bpy.props.IntProperty(name = '_total_number_of_layers_', \
                          description = '_not_exposed_to_user_', \
                          default = 0, \
                          min = 0, \
                          max = 2048, \
                          update = show_hide_layers)

##### UI Panel in the sidebar (The "N" panel.)
# Main panel
class VIEW3D_PT_BVTFloatingPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BlenderVizTools'
    bl_label = 'Blender Viz Tools'
    
    def draw(self, context):
        layout = self.layout
        split = layout.split()
        # col = split.column()
        # col.operator(BVT_OT_refresh_view.bl_idname, icon='FILE_REFRESH')
        col = split.column()
        col.operator(BVT_OT_goto_home_view.bl_idname, icon='HOME')
        col = split.column()
        col.operator(BVT_OT_print_camera_coords.bl_idname, icon='TRACKER')
        col = split.column()
        col.operator(BVT_OT_set_home_view.bl_idname, icon='PINNED')
        
        split = layout.split()
        col = split.column()
        col.prop(bpy.context.scene.user_inputs, 'view_layers_0')
        col = split.column()
        col.prop(bpy.context.scene.user_inputs, 'view_layers_N')

# Colormap
class VIEW3D_PT_BVTFloatingPanel_ColorMap(bpy.types.Panel):
    # Copied from blender's source code
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BlenderVizTools'
    bl_label = 'Color Map'
    bl_parent_id = 'VIEW3D_PT_BVTFloatingPanel'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        mat = bpy.data.materials.get(TEMPLATE_CMAP_MAT_NAME)
        node = mat.node_tree.nodes.get(TEMPLATE_CMAP_NODE_NAME)
        # set "node" context pointer for the panel layout
        layout.context_pointer_set("node", node)

        if hasattr(node, "draw_buttons_ext"):
            node.draw_buttons_ext(context, layout)
        elif hasattr(node, "draw_buttons"):
            node.draw_buttons(context, layout)
        
        layout.operator(BVT_OT_refresh_view.bl_idname, icon='FILE_REFRESH')

# View
class VIEW3D_PT_BVTFloatingPanel_View(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BlenderVizTools'
    bl_label = 'View settings'
    bl_parent_id = 'VIEW3D_PT_BVTFloatingPanel'
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        layout.prop(bpy.context.scene.user_inputs, 'viewport_raytracing')
        layout.prop(bpy.context.scene.user_inputs, 'viewport_denoise')
        layout.prop(bpy.context.scene.user_inputs, 'viewport_quality')

# Render
class VIEW3D_PT_BVTFloatingPanel_Render(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BlenderVizTools'
    bl_label = 'Render settings'
    bl_parent_id = 'VIEW3D_PT_BVTFloatingPanel'
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        layout.prop(bpy.context.scene.user_inputs, 'render_raytracing')
        layout.prop(bpy.context.scene.user_inputs, 'render_denoise')
        layout.prop(bpy.context.scene.user_inputs, 'render_quality')
        row = layout.row(align=True)
        row.prop(bpy.context.scene.user_inputs, 'output_resolution_x')
        row.prop(bpy.context.scene.user_inputs, 'output_resolution_y')
        layout.prop(bpy.context.scene.user_inputs, 'output_image_name')
        layout.operator(BVT_OT_render.bl_idname, icon='RESTRICT_RENDER_OFF')

blender_classes = [VIEW3D_PT_BVTFloatingPanel, \
                   VIEW3D_PT_BVTFloatingPanel_ColorMap, VIEW3D_PT_BVTFloatingPanel_View, VIEW3D_PT_BVTFloatingPanel_Render, \
                   MyProperties, \
                   BVT_OT_goto_home_view, BVT_OT_set_home_view, BVT_OT_print_camera_coords, BVT_OT_refresh_view, \
                   BVT_OT_render]