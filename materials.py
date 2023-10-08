import bpy
from color_ramp import *

def create_scalar_CubeMap_layer(ID, z0, z1, image0, image1, cmap_name = 'my_cold', \
                                obj_scale = [1,1,1], obj_size = 1, \
                                obj_loc = [0,0,0], randomize_loc = True, loc_tol = 1e-3):
    # The locations have to be slightly offset in order for cycles to work properly
    if randomize_loc:
        # loc_tol should be much smaller than grid resolution in x-y direction
        loc = np.array(obj_loc) + np.random.uniform(0.5 - loc_tol, 0.5 + loc_tol, (3))
    else:
        loc = np.array(obj_loc) + np.array([0.5, 0.5, 0.5])
    
    # Create the object and assign a new material to it
    bpy.ops.mesh.primitive_cube_add(size = obj_size, enter_editmode = False, align='WORLD', \
                                    location = loc, scale = obj_scale)
    bpy.context.active_object.name = 'Layer %d' % ID
    bpy.data.materials.new(name='Material Layer %d' % ID)
    mat = bpy.data.materials.get('Material Layer %d' % ID)
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
    node_im.image = image0
    mat.node_tree.links.new(node_im.inputs[0], node_tex_coord.outputs[0])
    node_red = mat.node_tree.nodes.new('ShaderNodeSeparateColor')
    node_red.name = 'Red 0'
    node_red.location = [-1100, 0]
    mat.node_tree.links.new(node_red.inputs[0], node_im.outputs[0])
    node_col = create_color_ramp(mat, name='Color Ramp 0', loc=[-900, 0], cmap_name=cmap_name)
    mat.node_tree.links.new(node_col.inputs[0], node_red.outputs[0])
    
    node_im = mat.node_tree.nodes.new('ShaderNodeTexImage')
    node_im.name = 'Image 1'
    node_im.location = [-1400, 300]
    node_im.image = image1
    mat.node_tree.links.new(node_im.inputs[0], node_tex_coord.outputs[0])
    node_red = mat.node_tree.nodes.new('ShaderNodeSeparateColor')
    node_red.name = 'Red 1'
    node_red.location = [-1100, 300]
    mat.node_tree.links.new(node_red.inputs[0], node_im.outputs[0])
    node_col = create_color_ramp(mat, name='Color Ramp 1', loc=[-900, 300], cmap_name=cmap_name)
    mat.node_tree.links.new(node_col.inputs[0], node_red.outputs[0])
    
    # Create pairwise interpolated colors
    node_maprange = mat.node_tree.nodes.new('ShaderNodeMapRange')
    node_maprange.name = 'Map Range'
    node_maprange.location = [-900, 600]
    node_maprange.inputs[1].default_value = z0
    node_maprange.inputs[2].default_value = z1
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
    node_compare.inputs[1].default_value = 0.5 * (z1 + z0)
    node_compare.inputs[2].default_value = 0.5 * (z1 - z0)
    
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