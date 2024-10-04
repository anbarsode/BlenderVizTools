import numpy as np
import BlenderVizTools as bvt
import os

D = np.load('cube_cosmo.npz')
print(dict(D).keys())
print('Metadata:', D['metadata'])
print('spectral_index:', D['spectral_index'])
print('extent:', D['extent'])
print('shape:', D['arr3d'].shape)

arr3d = D['arr3d']
extent = D['extent']
extent = [[0,3],[0,10],[0,2]]
slices_data = bvt.create_slices(arr3d)
script_name = bvt.volume_render(slices_data, extent=extent, length_scale=2)
os.system('blender -P %s' % script_name)