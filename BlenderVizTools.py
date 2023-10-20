import numpy as np
import matplotlib.pyplot as plt
from matplotlib.image import imsave
from tqdm import tqdm
from pathlib import Path
import os

def create_slices(arr, extent=[[0,1],[0,1],[0,1]], sepscale='linear', clim=None, cscale='linear', label='array'):
    # create a directory to save slice images
    cwd = os.getcwd()
    path_to_slices = cwd + '/__BVTcache__/%s' % label
    Path(path_to_slices).mkdir(parents=True, exist_ok=True)
    
    # check input parameters
    if clim is None:
        clim = [arr.min(), arr.max()]
    elif clim[0] >= clim[1]:
        raise ValueError('clim[0] must be < clim[1]')
    
    if cscale == 'log' and clim[0] <= 0:
        print('Warning: For log color scale, clim[0] must be > 0. Setting non-positive values transparant')
    
    # create slice images
    slice_paths = []
    for k in range(arr.shape[2]):
        R = np.clip(arr[:,:,k], clim[0], clim[1])
        B = np.zeros(R.shape)
        G = np.zeros(R.shape)
        A = np.ones(R.shape)
        
        if cscale == 'linear':
            R = (R - clim[0]) / (clim[1] - clim[0])
        elif cscale == 'log':
            R = np.log(R / clim[0]) / np.log(clim[1] / clim[0])
            A = 1.0 - np.isnan(R)
        else: raise ValueError('cscale must be "linear" or "log"')
        
        slice_paths.append(path_to_slices + '/%d.png' % k)
        plt.imsave(slice_paths[-1], np.stack([R,G,B,A], axis=-1))
    
    # find slice locations
    if sepscale == 'linear': z_locs = np.linspace(extent[2][0], extent[2][1], arr.shape[2])
    elif sepscale == 'log': z_locs = np.logspace(np.log10(extent[2][0]), np.log10(extent[2][1]), arr.shape[2])
    elif sepscale == 'geom': z_locs = np.geomspace(extent[2][0], extent[2][1], arr.shape[2])
    
    return label, path_to_slices, slice_paths, z_locs, extent

def volume_render(slices_data, kind='cuboid', cmap='my_cold', out='script.py', N_layers=8):
    __LABEL__, path_to_slices, __IMAGE_FILENAMES__, __Z_LOCS__, extent = slices_data
    __IMAGE_FILENAMES__ = repr(__IMAGE_FILENAMES__)
    __Z_LOCS__ = 'np.' + repr(__Z_LOCS__)
    __COLOR_MAP__ = cmap
    
    if kind == 'cuboid' or kind == 'cube':
        __MATERIAL_FUNC__ = 'create_scalar_Cuboid_layer'
        obj_scale = [e[1]-e[0] for e in extent]
        obj_size = 1
        obj_loc = [e[0] for e in extent]
        __OBJ_PROPERTIES__ = 'obj_scale = %s, obj_size = %f, obj_loc = %s' % (repr(obj_scale), obj_size, repr(obj_loc))
        __CAMERA_LOC_SCALE__ = repr([obj_size]*3)
    elif kind == 'ellipsoid' or kind == 'sphere':
        __MATERIAL_FUNC__ = 'create_scalar_Ellipsoid_layer'
        obj_scale = [1,1,1]
        obj_radius = 1
        obj_loc = [0,0,0]
        __OBJ_PROPERTIES__ = 'obj_scale = %s, obj_radius = %f, obj_loc = %s' % (repr(obj_scale), obj_radius, repr(obj_loc))
        __CAMERA_LOC_SCALE__ = repr([obj_radius]*3)
    elif kind == 'cylinder':
        __MATERIAL_FUNC__ = 'create_scalar_Cylinder_layer'
        obj_scale = [1,1,1]
        obj_radius = 1
        obj_height = 1
        obj_loc = [0,0,0]
        __OBJ_PROPERTIES__ = 'obj_scale = %s, obj_radius = %f, obj_height = %f, obj_loc = %s' % (repr(obj_scale), obj_radius, obj_height, repr(obj_loc))
        __CAMERA_LOC_SCALE__ = repr(obj_scale.copy())
    
    param_dir = {}
    param_dir['__Z_LOCS__'] = __Z_LOCS__
    param_dir['__IMAGE_FILENAMES__'] = __IMAGE_FILENAMES__
    param_dir['__LABEL__'] = __LABEL__
    param_dir['__COLOR_MAP__'] = __COLOR_MAP__
    param_dir['__MATERIAL_FUNC__'] = __MATERIAL_FUNC__
    param_dir['__OBJ_PROPERTIES__'] = __OBJ_PROPERTIES__
    param_dir['__CAMERA_LOC_SCALE__'] = __CAMERA_LOC_SCALE__
    param_dir['__N_LAYERS__'] = '%d' % N_layers
    
    outpath = path_to_slices + '/' + out
    with open('template_blender_script.txt', 'r') as fin:
        with open(outpath, 'w') as fout:
            for line in fin.readlines():
                for p in param_dir.keys():
                    if p in line:
                        line = param_dir[p].join(line.split(p))
                fout.write(line)
    
    return outpath