import bpy
import sys
import os
import logging

# Set up logging
script_dir = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(script_dir, "blender_logfile.log")
if not os.path.exists(script_dir):
    os.makedirs(script_dir)
logging.basicConfig(filename=log_file_path, level=logging.DEBUG, format='%(asctime)s - %(message)s')

def log_message(message):
    logging.debug(message)

def remove_video_sequences(scene, settings):
    if "have_seq" in settings and settings["have_seq"]:
        sequence_editor = scene.sequence_editor
        if sequence_editor:
            for seq in sequence_editor.sequences_all:
                if seq.type in ['MOVIE', 'IMAGE', 'SOUND']:
                    sequence_editor.sequences.remove(seq)
            log_message("All video sequences removed.")
        else:
            log_message("No sequence editor found.")

def str_to_bool(s):
    log_message(f"str to bool{s}")
    try:
        return s.lower() in ['true', '1', 'yes']
    except:
        return s

def apply_render_settings(scene, D, settings):
    log_message(f"APPLY {settings}")
    scene.render.engine = settings.get("Render_Engine", scene.render.engine)
    # scene.render.fps = int(settings.get("FPS", scene.render.fps))
    # scene.frame_start = 1
    # scene.frame_end = int(settings.get("Total_Frames", scene.frame_end + scene.frame_start))+1
    scene.render.resolution_x = int(settings.get("Resolution_X", scene.render.resolution_x))
    scene.render.resolution_y = int(settings.get("Resolution_Y", scene.render.resolution_y))
    scene.render.filepath = settings.get("File_Path", scene.render.filepath)
    scene.render.resolution_percentage = int(settings.get("Resolution_Percentage", scene.render.resolution_percentage))
    scene.render.use_simplify = str_to_bool(settings.get("Simplify", scene.render.use_simplify))
    D.scenes[bpy.context.scene.name].render.image_settings.file_format = settings.get("File_Format")

    if scene.world:
        scene.world.name = settings.get("World_Name", scene.world.name)

    if scene.render.engine in ['BLENDER_EEVEE', 'EEVEE']:
        scene.eevee.use_gtao = str_to_bool(settings.get("Ambient_Occlusion", scene.eevee.use_gtao))
        scene.eevee.use_ssr = str_to_bool(settings.get("Subsurface_Reflection", scene.eevee.use_ssr))
        scene.eevee.use_bloom = str_to_bool(settings.get("Bloom", scene.eevee.use_bloom))
        scene.eevee.use_motion_blur = str_to_bool(settings.get("Motion_Blur", scene.eevee.use_motion_blur))
        scene.eevee.taa_render_samples = int(settings.get("Render_Samples", scene.eevee.taa_render_samples))
    elif scene.render.engine == 'CYCLES':
        scene.cycles.samples = int(settings.get("Render_Samples", scene.cycles.samples))
        scene.cycles.adaptive_threshold = float(settings.get("noise_t", scene.cycles.adaptive_threshold))

    scene.use_nodes = str_to_bool(settings.get("w_comp", scene.use_nodes))

    remove_video_sequences(scene, settings)

    log_message(f"Settings applied to scene '{scene.name}'")

def save_blend_file(output_path, settings):
    main_file_path = eval(settings).get("FilePath")
    bpy.ops.wm.open_mainfile(filepath=main_file_path)
    apply_render_settings(bpy.context.scene, bpy.data, eval(settings))
    bpy.ops.wm.save_as_mainfile(filepath=output_path)

if __name__ == "__main__":
    settings = sys.argv[2]  # Get the output file path from command line arguments
    file_path = sys.argv[1]
    output_path = file_path
    save_blend_file(output_path, settings)
