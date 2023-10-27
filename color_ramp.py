import bpy
import numpy as np
from user_defined_color_maps import USER_DEFINED_COLOR_MAPS
from matplotlib_color_maps import MATPLOTLIB_COLOR_MAPS

'''
import matplotlib.pyplot as plt
def matplotlib_cmap_to_colorramp(cmap_name = 'my_cold', npts = 10):
    try:
        cmap = plt.get_cmap(cmap_name)
    except ValueError:
        return None
    
    pts = np.linspace(0, 1, npts)
    return {'cmap':[[v]+list(cmap(v)) for v in pts], 'interp':'EASE'}
'''

def create_color_ramp(mat, name, loc, cmap_name = 'my_cold', cmap_data = None):
    # get colormap elements
    if cmap_data is not None:
        cmap = cmap_data['cmap']
        interp = cmap_data['interp']
        mode = cmap_data['mode']
    elif cmap_name in USER_DEFINED_COLOR_MAPS.keys():
        cmap = USER_DEFINED_COLOR_MAPS[cmap_name]['cmap']
        interp = USER_DEFINED_COLOR_MAPS[cmap_name]['interp']
        mode = 'RGB'
    elif cmap_name in MATPLOTLIB_COLOR_MAPS.keys():
        cmap = MATPLOTLIB_COLOR_MAPS[cmap_name]['cmap']
        interp = MATPLOTLIB_COLOR_MAPS[cmap_name]['interp']
        mode = 'RGB'
    else:
        print('Colormap "%s" found neither in user_defined_color_maps nor in matplotlib_color_maps\n Defaulting to "my_cold"' % cmap_name)
        cmap = MATPLOTLIB_COLOR_MAPS['my_cold']['cmap']
        interp = MATPLOTLIB_COLOR_MAPS['my_cold']['interp']
        mode = 'RGB'
    '''
    else:
        cmap = matplotlib_cmap_to_colorramp(cmap_name, 10)
        if cmap is None:
            raise ValueError('Colormap "%s" found neither in USER_DEFINED_COLOR_MAPS nor in matplotlib' % cmap_name)
    '''
    
    if len(cmap) < 2:
        print('Warning: Number of elements in colormap cannot be < 2. Defaulting to "my_cold"')
        # cmap = matplotlib_cmap_to_colorramp('my_cold', 10)
        cmap = MATPLOTLIB_COLOR_MAPS['my_cold']['cmap']
        interp = MATPLOTLIB_COLOR_MAPS['my_cold']['interp']
        mode = 'RGB'
    
    # create node, assign basic properties
    node = mat.node_tree.nodes.new('ShaderNodeValToRGB')
    node.name = name
    node.location = loc
    node.color_ramp.interpolation = interp
    node.color_ramp.color_mode = mode
    
    # assign first two elements which are present by default
    node.color_ramp.elements[0].position = cmap[0][0]
    node.color_ramp.elements[0].color = cmap[0][1:]
    node.color_ramp.elements[1].position = cmap[1][0]
    node.color_ramp.elements[1].color = cmap[1][1:]
    
    # create new elements
    for i,element in enumerate(cmap[2:]):
        node.color_ramp.elements.new(element[0])
        node.color_ramp.elements[i+2].color = element[1:]
    
    return node

TEMPLATE_CMAP_MAT_NAME = 'Template Color Map'
TEMPLATE_CMAP_NODE_NAME = 'Template Color Map'

def create_template_colormap(cmap_name, cmap_data=None):
    bpy.data.materials.new(name = TEMPLATE_CMAP_MAT_NAME)
    mat = bpy.data.materials.get(TEMPLATE_CMAP_MAT_NAME)
    mat.use_nodes = True
    mat.node_tree.nodes.clear()
    create_color_ramp(mat, TEMPLATE_CMAP_NODE_NAME, [0,0], cmap_name, cmap_data)

def refresh_colormaps(layer_id0, N_layers):
    mat = bpy.data.materials.get(TEMPLATE_CMAP_MAT_NAME)
    node = mat.node_tree.nodes.get(TEMPLATE_CMAP_NODE_NAME)
    interp = node.color_ramp.interpolation
    mode = node.color_ramp.color_mode
    cmap = []
    for e in node.color_ramp.elements:
        cmap.append([e.position] + list(e.color))

    for ID in range(layer_id0, layer_id0 + N_layers):
        mat = bpy.data.materials.get('Material Layer %d' % ID)
        if mat is None: continue
        for nodename in ['Color Ramp 0', 'Color Ramp 1']:
            node = mat.node_tree.nodes.get(nodename)
            node.color_ramp.interpolation = interp
            node.color_ramp.color_mode = mode
            if len(node.color_ramp.elements) > len(cmap):
                for i in range(len(cmap)):
                    node.color_ramp.elements[i].position = cmap[i][0]
                    node.color_ramp.elements[i].color = cmap[i][1:]
                for i in range(len(cmap), len(node.color_ramp.elements)):
                    node.color_ramp.elements.remove(node.color_ramp.elements[i])
            elif len(node.color_ramp.elements) < len(cmap):
                for i in range(len(node.color_ramp.elements)):
                    node.color_ramp.elements[i].position = cmap[i][0]
                    node.color_ramp.elements[i].color = cmap[i][1:]
                for i in range(len(node.color_ramp.elements), len(cmap)):
                    node.color_ramp.elements.new(cmap[i][0])
                    node.color_ramp.elements[i].color = cmap[i][1:]
            else:
                for i in range(len(node.color_ramp.elements)):
                    node.color_ramp.elements[i].position = cmap[i][0]
                    node.color_ramp.elements[i].color = cmap[i][1:]
