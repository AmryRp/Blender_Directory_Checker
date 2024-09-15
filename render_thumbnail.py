import bpy
import sys
import os

def render_thumbnail(blend_file, output_dir):
    # Open the .blend file
    thumbnail_path = os.path.join(output_dir, f"{os.path.basename(blend_file)}_thumbnail.png")
    if os.path.exists(thumbnail_path):
        return thumbnail_path
    bpy.ops.wm.open_mainfile(filepath=blend_file)
    os.path.basename(blend_file)
    # Set up the render settings for the thumbnail
    scene = bpy.context.scene
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 75
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = thumbnail_path
    bpy.data.scenes[scene.name].cycles.samples = 128
    bpy.data.scenes[scene.name].render.use_stamp = True

    # Render the thumbnail
    bpy.ops.render.render(write_still=True)
    return thumbnail_path

if __name__ == "__main__":
    blend_file = sys.argv[1]
    output_dir = sys.argv[2]
    render_thumbnail(blend_file, output_dir)
