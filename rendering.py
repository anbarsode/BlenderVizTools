import bpy

bpy.data.scenes['Scene'].render.use_border = True
bpy.data.scenes['Scene'].cycles.device = 'GPU'

VIEW_SETTINGS = {'engine':'fast', 'quality':'medium', 'denoise':False}
RENDER_SETTINGS = {'engine':'fast', 'quality':'good', 'denoise':False, 'resolution':[960,540]}

def reset_viewport_settings(engine='fast', quality='medium', denoise=False):
    if engine == 'fast':
        bpy.data.scenes['Scene'].render.engine = 'BLENDER_EEVEE'
        if quality == 'low':
            bpy.data.scenes['Scene'].eevee.taa_samples = 16
            bpy.data.scenes['Scene'].eevee.volumetric_tile_size = '8'
        if quality == 'medium':
            bpy.data.scenes['Scene'].eevee.taa_samples = 32
            bpy.data.scenes['Scene'].eevee.volumetric_tile_size = '4'
        if quality == 'good':
            bpy.data.scenes['Scene'].eevee.taa_samples = 128
            bpy.data.scenes['Scene'].eevee.volumetric_tile_size = '2'
        if quality == 'high':
            bpy.data.scenes['Scene'].eevee.taa_samples = 0
            bpy.data.scenes['Scene'].eevee.volumetric_tile_size = '2'
    
    if engine == 'accurate':
        bpy.data.scenes['Scene'].render.engine = 'CYCLES'
        bpy.data.scenes['Scene'].cycles.preview_adaptive_threshold = 1.0
        bpy.data.scenes['Scene'].cycles.use_preview_denoising = denoise
        if quality == 'low':
            bpy.data.scenes['Scene'].cycles.preview_samples = 4
            bpy.data.scenes['Scene'].cycles.volume_max_steps = 2
        if quality == 'medium':
            bpy.data.scenes['Scene'].cycles.preview_samples = 6
            bpy.data.scenes['Scene'].cycles.volume_max_steps = 8
        if quality == 'good':
            bpy.data.scenes['Scene'].cycles.preview_samples = 8
            bpy.data.scenes['Scene'].cycles.volume_max_steps = 16
        if quality == 'high':
            bpy.data.scenes['Scene'].cycles.preview_samples = 64
            bpy.data.scenes['Scene'].cycles.volume_max_steps = 128

def reset_render_settings(engine='fast', quality='good', denoise=False, resolution=[960,540]):
    bpy.data.scenes['Scene'].render.resolution_x = resolution[0]
    bpy.data.scenes['Scene'].render.resolution_y = resolution[1]
    if engine == 'fast':
        bpy.data.scenes['Scene'].render.engine = 'BLENDER_EEVEE'
        if quality == 'low':
            bpy.data.scenes['Scene'].eevee.taa_render_samples = 16
            bpy.data.scenes['Scene'].eevee.volumetric_tile_size = '8'
        if quality == 'medium':
            bpy.data.scenes['Scene'].eevee.taa_render_samples = 32
            bpy.data.scenes['Scene'].eevee.volumetric_tile_size = '4'
        if quality == 'good':
            bpy.data.scenes['Scene'].eevee.taa_render_samples = 128
            bpy.data.scenes['Scene'].eevee.volumetric_tile_size = '2'
        if quality == 'high':
            bpy.data.scenes['Scene'].eevee.taa_render_samples = 0
            bpy.data.scenes['Scene'].eevee.volumetric_tile_size = '2'
    
    if engine == 'accurate':
        bpy.data.scenes['Scene'].render.engine = 'CYCLES'
        bpy.data.scenes['Scene'].cycles.adaptive_threshold = 1.0
        bpy.data.scenes['Scene'].cycles.use_denoising = denoise
        if quality == 'low':
            bpy.data.scenes['Scene'].cycles.samples = 4
            bpy.data.scenes['Scene'].cycles.volume_max_steps = 2
        if quality == 'medium':
            bpy.data.scenes['Scene'].cycles.samples = 6
            bpy.data.scenes['Scene'].cycles.volume_max_steps = 8
        if quality == 'good':
            bpy.data.scenes['Scene'].cycles.samples = 8
            bpy.data.scenes['Scene'].cycles.volume_max_steps = 16
        if quality == 'high':
            bpy.data.scenes['Scene'].cycles.samples = 64
            bpy.data.scenes['Scene'].cycles.volume_max_steps = 128