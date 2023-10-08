import bpy

# Disable the opening "splash" screen
bpy.context.preferences.view.show_splash = False

# Delete the default cube and light
bpy.data.objects.remove(bpy.data.objects['Cube'], do_unlink=True)
bpy.data.objects.remove(bpy.data.objects['Light'], do_unlink=True)

# Remove unnecessary workspaces
for ws in bpy.data.workspaces:
    if ws.name != 'Layout':
        override = {'workspace': ws}
        with bpy.context.temp_override(**override): bpy.ops.workspace.delete()
bpy.data.workspaces['Layout'].name = 'Rendered'
bpy.context.window.workspace = bpy.data.workspaces['Rendered']

# Close properties, dopesheet and outliner
# Default open areas: ['PROPERTIES', 'OUTLINER', 'DOPESHEET_EDITOR', 'VIEW_3D']
for area_type in ['PROPERTIES', 'OUTLINER', 'DOPESHEET_EDITOR']:
    area = [a for a in bpy.context.window.screen.areas if a.type == area_type][0]
    override = {'space_data':area.spaces.active, 'region':area.regions[-1], 'area':area}
    with bpy.context.temp_override(**override): bpy.ops.screen.area_close()
    
# Switch to rendered view upon launch
main_area = [a for a in bpy.context.window.screen.areas if a.type == 'VIEW_3D'][0]
main_space = [s for s in main_area.spaces if s.type == 'VIEW_3D'][0]
main_space.shading.type = 'RENDERED'

# Remove unwanted toolbars
main_space.show_region_header = False
main_space.show_region_toolbar = False
main_space.show_region_ui = True

# Lock camera to view
main_space.lock_camera = True

# Default camera location and rotation upon launch
CAMERA_HOME_LOCATION = [7, -2.5, 4]
CAMERA_HOME_ROTATION = [1.1, 0, 1.15]
bpy.data.objects['Camera'].location = CAMERA_HOME_LOCATION.copy()
bpy.data.objects['Camera'].rotation_euler = CAMERA_HOME_ROTATION.copy()

# switch to camera view and maximize it to fit the window
override = {'area':main_area, 'region':main_area.regions[-1]}
with bpy.context.temp_override(**override):
    bpy.ops.view3d.view_camera()
    bpy.ops.view3d.view_center_camera()

