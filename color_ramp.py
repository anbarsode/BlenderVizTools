import numpy as np
# import matplotlib.pyplot as plt
from user_defined_color_maps import USER_DEFINED_COLOR_MAPS
from matplotlib_color_maps import MATPLOTLIB_COLOR_MAPS

'''
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
    elif cmap_name in USER_DEFINED_COLOR_MAPS.keys():
        cmap = USER_DEFINED_COLOR_MAPS[cmap_name]['cmap']
        interp = USER_DEFINED_COLOR_MAPS[cmap_name]['interp']
    elif cmap_name in MATPLOTLIB_COLOR_MAPS.keys():
        cmap = MATPLOTLIB_COLOR_MAPS[cmap_name]['cmap']
        interp = MATPLOTLIB_COLOR_MAPS[cmap_name]['interp']
    else:
        print('Colormap "%s" found neither in user_defined_color_maps nor in matplotlib_color_maps\n Defaulting to "my_cold"' % cmap_name)
        cmap = MATPLOTLIB_COLOR_MAPS['my_cold']['cmap']
        interp = MATPLOTLIB_COLOR_MAPS['my_cold']['interp']
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
    
    # create node, assign basic properties
    node = mat.node_tree.nodes.new('ShaderNodeValToRGB')
    node.name = name
    node.location = loc
    node.color_ramp.interpolation = interp
    
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
