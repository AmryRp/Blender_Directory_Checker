import sys
import bpy
import os

def render_Settings(C,D, scene):
    render_settings = scene.render
    file_path = D.filepath
    
    settings = {
        "FilePath": file_path,
        "FileName": os.path.basename(file_path),
        "Render_Engine": scene.render.engine,
        "FPS": scene.render.fps,
        "Total_Frames": scene.frame_end - scene.frame_start,
        "Render_Samples": D.scenes[C.scene.name].cycles.samples,
        "Resolution_X": render_settings.resolution_x,
        "Resolution_Y": render_settings.resolution_y,
        "File_Path": render_settings.filepath,"World_Name": "-" if scene.world is None else scene.world.name,
        "File_Format": render_settings.image_settings.file_format,
        "Resolution_Percentage": render_settings.resolution_percentage,
        "Scene": C.scene.name,
        "have_seq": has_video_sequence(C, D),
        "Ambient_Occlusion": "-",
        "Subsurface_Reflection": "-",
        "Simplify": "-",
        "Bloom": "-",
        "Motion_Blur": "-",
        
    }

    # Update values for EEVEE engine
    if scene.render.engine in ['BLENDER_EEVEE', "EEVEE"]:
        settings.update({
            "Ambient_Occlusion": D.scenes[C.scene.name].eevee.use_gtao,
            "Subsurface_Reflection": D.scenes[C.scene.name].eevee.use_ssr,
            "Simplify": scene.render.use_simplify,
            "Bloom": D.scenes[C.scene.name].eevee.use_bloom,
            "Motion_Blur": D.scenes[C.scene.name].eevee.use_motion_blur,
            "Render_Samples": D.scenes[C.scene.name].eevee.taa_render_samples,
        })
    return settings

def has_video_sequence(C, D):
    # Get the Video Sequence Editor (VSE)
    if not D.scenes:
        return False

    # Assuming the active scene has the VSE
    scene = C.scene
    if scene.sequence_editor is None:
        return False

    # Check if there are any video strips
    for strip in scene.sequence_editor.sequences_all:
        if strip.type == 'MOVIE':
            return True

    return False


def load_blend_file(file_path):
    bpy.context.preferences.view.use_save_prompt = False
    bpy.ops.wm.open_mainfile(filepath=file_path)
    
    # Format the important information
    settings_info = (
        f"_Result"
        f"{render_Settings(bpy.context, bpy.data, bpy.context.scene)}"
        f"_Result"
    )
    return settings_info

if __name__ == "__main__":
    file_path = sys.argv[1]
    try:
        info = load_blend_file(file_path)
        print(info)
    except Exception as e:
        print(f"Failed to load Blender file:\n{str(e)}", file=sys.stderr)
        sys.exit(1)
