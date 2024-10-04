import bpy

# Close properties, dopesheet and outliner
# Default open areas: ['PROPERTIES', 'OUTLINER', 'DOPESHEET_EDITOR', 'VIEW_3D']
to_close = []
for area_type in ['PROPERTIES', 'OUTLINER', 'DOPESHEET_EDITOR']:
    to_close.append([a for a in bpy.context.window.screen.areas if a.type == area_type][-1])

override = bpy.context.copy()
    
for area in to_close:
    override['area'] = area
    with bpy.context.temp_override(**override): bpy.ops.screen.area_close()
    
# Switch to rendered view upon launch
main_area = [a for a in bpy.context.window.screen.areas if a.type == 'VIEW_3D'][0]
main_space = [s for s in main_area.spaces if s.type == 'VIEW_3D'][0]
main_space.shading.type = 'RENDERED'

# more code which uses main_area