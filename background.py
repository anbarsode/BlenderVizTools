import bpy

bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = [0, 0, 0, 1]