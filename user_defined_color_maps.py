USER_DEFINED_COLOR_MAPS = {}

# Format:
#     USER_DEFINED_COLOR_MAPS['name'] = {'cmap':[[v, r, b, g, a], [v, r, b, g, a], ...], 'interp':'Ease'}
# where each of [v, r, b, g, a] is a float between 0 and 1, 
# mapping a value "v" to a color given by [r,g,b,a]
# and "interp" is a string from ['EASE', 'CARDINAL', 'LINEAR', 'B_SPLINE', 'CONSTANT']

# Examples
USER_DEFINED_COLOR_MAPS['my_hot'] = {'cmap':[[0.2, 0, 0, 0, 1], [0.4, 1, 0, 0, 1], [0.6, 1, 1, 0, 1], [0.8, 1, 1, 1, 1]], 'interp':'EASE'}
USER_DEFINED_COLOR_MAPS['my_cold'] = {'cmap':[[0.2, 0, 0, 0, 1], [0.4, 0, 0, 1, 1], [0.6, 0, 1, 1, 1], [0.8, 1, 1, 1, 1]], 'interp':'EASE'}
USER_DEFINED_COLOR_MAPS['my_step_cold'] = {'cmap':[[0.2, 0, 0, 0, 1], [0.4, 0, 0, 1, 1], [0.6, 0, 1, 1, 1], [0.8, 1, 1, 1, 1]], 'interp':'CONSTANT'}

# See matplotlib_color_maps.py for more examples


