"""CapCut project generator.

Creates a native CapCut Desktop project (draft_content.json + meta)
from MP3, SRT, and sorted images, so the user can open it in CapCut
for further editing and export.

Time unit in CapCut: **microseconds** (1 second = 1_000_000).
"""

import json
import os
import shutil
import time
import uuid
from typing import Optional

from PIL import Image

from .srt_parser import SrtSegment
from .image_sorter import get_sorted_images

# CapCut project root on this machine
CAPCUT_PROJECTS_ROOT = os.path.join(
    os.path.expanduser('~'),
    'AppData', 'Local', 'CapCut', 'User Data', 'Projects',
    'com.lveditor.draft',
)

SEC_TO_US = 1_000_000  # seconds → microseconds


def _uuid() -> str:
    """Generate a CapCut-style UUID (uppercase, hyphenated)."""
    return str(uuid.uuid4()).upper()


def _sec_us(seconds: float) -> int:
    """Convert seconds to microseconds (CapCut time unit)."""
    return int(round(seconds * SEC_TO_US))


def _make_photo_material(
    mat_id: str, path: str, width: int, height: int, filename: str,
) -> dict:
    """Create a CapCut video material entry for a photo."""
    return {
        "id": mat_id,
        "unique_id": "",
        "type": "photo",
        "duration": 10800000000,  # CapCut default for photos
        "path": path.replace('\\', '/'),
        "media_path": "",
        "local_id": "",
        "has_audio": False,
        "reverse_path": "",
        "intensifies_path": "",
        "reverse_intensifies_path": "",
        "intensifies_audio_path": "",
        "cartoon_path": "",
        "width": width,
        "height": height,
        "category_id": "",
        "category_name": "",
        "material_id": "",
        "material_name": filename,
        "material_url": "",
        "crop": {
            "upper_left_x": 0.0, "upper_left_y": 0.0,
            "upper_right_x": 1.0, "upper_right_y": 0.0,
            "lower_left_x": 0.0, "lower_left_y": 1.0,
            "lower_right_x": 1.0, "lower_right_y": 1.0,
        },
        "crop_ratio": "free",
        "audio_fade": None,
        "crop_scale": 1.0,
        "extra_type_option": 0,
        "stable": {"stable_level": 0, "matrix_path": "", "time_range": {"start": 0, "duration": 0}},
        "matting": {
            "flag": 0, "path": "", "interactiveTime": [],
            "has_use_quick_brush": False, "strokes": [],
            "has_use_quick_eraser": False, "expansion": 0,
            "feather": 0, "reverse": False,
            "custom_matting_id": "", "enable_matting_stroke": False,
            "is_clould": False, "mask_video_path": "",
            "cloud_product_fps": 0.0,
        },
        "source": 0,
        "source_platform": 0,
        "formula_id": "",
        "check_flag": 62978047,
        "video_algorithm": {
            "algorithms": [], "time_range": None, "path": "",
            "gameplay_configs": [], "ai_in_painting_config": [],
            "complement_frame_config": None, "motion_blur_config": None,
            "deflicker": None, "noise_reduction": None,
            "quality_enhance": None, "super_resolution": None,
            "ai_background_configs": [], "smart_complement_frame": None,
            "aigc_generate": None, "aigc_generate_list": [],
            "mouth_shape_driver": None, "ai_expression_driven": None,
            "ai_motion_driven": None, "image_interpretation": None,
            "story_video_modify_video_config": {
                "task_id": "", "is_overwrite_last_video": False,
                "tracker_task_id": "",
            },
            "skip_algorithm_index": [],
        },
        "is_unified_beauty_mode": False,
        "is_set_beauty_mode": False,
        "object_locked": None,
        "smart_motion": None,
        "multi_camera_info": None,
        "freeze": None,
        "picture_from": "none",
        "picture_set_category_id": "",
        "picture_set_category_name": "",
        "team_id": "",
        "local_material_id": "",
        "origin_material_id": "",
        "request_id": "",
        "has_sound_separated": False,
        "is_text_edit_overdub": False,
        "is_ai_generate_content": False,
        "aigc_type": "none",
        "is_copyright": False,
        "aigc_history_id": "",
        "aigc_item_id": "",
        "local_material_from": "",
        "smart_match_info": None,
        "beauty_face_preset_infos": [],
        "beauty_body_preset_id": "",
        "beauty_face_auto_preset": {"preset_id": "", "name": "", "rate_map": "", "scene": ""},
        "beauty_face_auto_preset_infos": [],
        "beauty_body_auto_preset": None,
        "live_photo_timestamp": -1,
        "live_photo_cover_path": "",
        "content_feature_info": None,
        "corner_pin": None,
        "surface_trackings": [],
        "video_mask_stroke": {
            "resource_id": "", "path": "", "type": "", "color": "",
            "size": 0.0, "alpha": 0.0, "distance": 0.0, "texture": 0.0,
            "horizontal_shift": 0.0, "vertical_shift": 0.0,
        },
        "video_mask_shadow": {
            "resource_id": "", "path": "", "color": "",
            "alpha": 0.0, "blur": 0.0, "distance": 0.0, "angle": 0.0,
        },
    }


def _make_audio_material(
    mat_id: str, path: str, duration_us: int, filename: str,
) -> dict:
    """Create a CapCut audio material entry."""
    return {
        "id": mat_id,
        "unique_id": "",
        "type": "extract_music",
        "name": filename,
        "duration": duration_us,
        "path": path.replace('\\', '/'),
        "category_name": "local",
        "wave_points": [],
        "music_id": "",
        "app_id": 0,
        "text_id": "",
        "tone_type": "",
        "source_platform": 0,
        "video_id": "",
        "effect_id": "",
        "resource_id": "",
        "third_resource_id": "",
        "category_id": "",
        "intensifies_path": "",
        "formula_id": "",
        "check_flag": 1,
        "team_id": "",
        "local_material_id": "",
        "tone_speaker": "",
        "mock_tone_speaker": "",
        "tone_effect_id": "",
        "tone_effect_name": "",
        "tone_platform": "",
        "cloned_model_type": "",
        "tone_category_id": "",
        "tone_category_name": "",
        "tone_second_category_id": "",
        "tone_second_category_name": "",
        "tone_emotion_name_key": "",
        "tone_emotion_style": "",
        "tone_emotion_role": "",
        "tone_emotion_selection": "",
        "tone_emotion_scale": 0.0,
        "moyin_emotion": "",
        "request_id": "",
        "query": "",
        "search_id": "",
        "sound_separate_type": "",
        "is_text_edit_overdub": False,
        "is_ugc": False,
        "is_ai_clone_tone": False,
        "is_ai_clone_tone_post": False,
        "source_from": "",
        "copyright_limit_type": "none",
        "aigc_history_id": "",
        "aigc_item_id": "",
        "music_source": "",
        "pgc_id": "",
        "pgc_name": "",
        "similiar_music_info": {"original_song_id": "", "original_song_name": ""},
        "ai_music_type": 0,
        "ai_music_enter_from": "",
        "lyric_type": 0,
        "tts_task_id": "",
        "tts_generate_scene": "",
        "ai_music_generate_scene": 0,
        "tts_benefit_info": {
            "benefit_type": "none", "benefit_log_id": "",
            "benefit_log_extra": "", "benefit_amount": -1,
        },
    }


def _make_video_segment(
    seg_id: str,
    material_id: str,
    target_start_us: int,
    duration_us: int,
    extra_refs: list[str],
) -> dict:
    """Create a segment on the video track."""
    return {
        "id": seg_id,
        "source_timerange": {"start": 0, "duration": duration_us},
        "target_timerange": {"start": target_start_us, "duration": duration_us},
        "render_timerange": {"start": 0, "duration": 0},
        "desc": "",
        "state": 0,
        "speed": 1.0,
        "is_loop": False,
        "is_tone_modify": False,
        "reverse": False,
        "intensifies_audio": False,
        "cartoon": False,
        "volume": 1.0,
        "last_nonzero_volume": 1.0,
        "clip": {
            "scale": {"x": 1.0, "y": 1.0},
            "rotation": 0.0,
            "transform": {"x": 0.0, "y": 0.0},
            "flip": {"vertical": False, "horizontal": False},
            "alpha": 1.0,
        },
        "uniform_scale": {"on": True, "value": 1.0},
        "material_id": material_id,
        "extra_material_refs": extra_refs,
        "render_index": 0,
        "keyframe_refs": [],
        "enable_lut": True,
        "enable_adjust": True,
        "enable_hsl": False,
        "visible": True,
        "group_id": "",
        "enable_color_curves": True,
        "enable_hsl_curves": True,
        "track_render_index": 0,
        "hdr_settings": {"mode": 1, "intensity": 1.0, "nits": 1000},
        "enable_color_wheels": True,
        "track_attribute": 0,
        "is_placeholder": False,
        "template_id": "",
        "enable_smart_color_adjust": False,
        "template_scene": "default",
        "common_keyframes": [],
        "caption_info": None,
        "responsive_layout": {
            "enable": False, "target_follow": "",
            "size_layout": 0, "horizontal_pos_layout": 0,
            "vertical_pos_layout": 0,
        },
        "enable_color_match_adjust": False,
        "enable_color_correct_adjust": False,
        "enable_adjust_mask": False,
        "raw_segment_id": "",
        "lyric_keyframes": None,
        "enable_video_mask": True,
        "digital_human_template_group_id": "",
        "color_correct_alg_result": "",
        "source": "segmentsourcenormal",
        "enable_mask_stroke": False,
        "enable_mask_shadow": False,
        "enable_color_adjust_pro": False,
    }


def _make_audio_segment(
    seg_id: str,
    material_id: str,
    duration_us: int,
    extra_refs: list[str],
) -> dict:
    """Create a segment on the audio track."""
    return {
        "id": seg_id,
        "source_timerange": {"start": 0, "duration": duration_us},
        "target_timerange": {"start": 0, "duration": duration_us},
        "render_timerange": {"start": 0, "duration": 0},
        "desc": "",
        "state": 0,
        "speed": 1.0,
        "is_loop": False,
        "is_tone_modify": False,
        "reverse": False,
        "intensifies_audio": False,
        "cartoon": False,
        "volume": 1.0,
        "last_nonzero_volume": 1.0,
        "clip": None,
        "uniform_scale": None,
        "material_id": material_id,
        "extra_material_refs": extra_refs,
        "render_index": 0,
        "keyframe_refs": [],
        "enable_lut": False,
        "enable_adjust": False,
        "enable_hsl": False,
        "visible": True,
        "group_id": "",
        "enable_color_curves": True,
        "enable_hsl_curves": True,
        "track_render_index": 1,
        "hdr_settings": None,
        "enable_color_wheels": True,
        "track_attribute": 0,
        "is_placeholder": False,
        "template_id": "",
        "enable_smart_color_adjust": False,
        "template_scene": "default",
        "common_keyframes": [],
        "caption_info": None,
        "responsive_layout": {
            "enable": False, "target_follow": "",
            "size_layout": 0, "horizontal_pos_layout": 0,
            "vertical_pos_layout": 0,
        },
        "enable_color_match_adjust": False,
        "enable_color_correct_adjust": False,
        "enable_adjust_mask": False,
        "raw_segment_id": "",
        "lyric_keyframes": None,
        "enable_video_mask": True,
        "digital_human_template_group_id": "",
        "color_correct_alg_result": "",
        "source": "segmentsourcenormal",
        "enable_mask_stroke": False,
        "enable_mask_shadow": False,
        "enable_color_adjust_pro": False,
    }


def _get_image_dimensions(path: str) -> tuple[int, int]:
    """Get image width and height using Pillow."""
    with Image.open(path) as img:
        return img.size  # (width, height)


def _get_audio_duration_us(audio_path: str) -> int:
    """Get accurate audio duration using imageio_ffmpeg."""
    try:
        import subprocess
        import imageio_ffmpeg
        import re
        
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

        cmd = [ffmpeg, '-i', audio_path]
        creation_flags = 0
        if os.name == 'nt':
            creation_flags = subprocess.CREATE_NO_WINDOW
        
        # ffmpeg outputs to stderr for '-i'
        result = subprocess.run(
            cmd, capture_output=True, text=True,
            creationflags=creation_flags,
        )
        
        output = result.stderr
        match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", output)
        if match:
            h, m, s = match.groups()
            duration_sec = int(h) * 3600 + int(m) * 60 + float(s)
            return int(duration_sec * SEC_TO_US)
    except Exception as e:
        print("Failed to get audio duration via ffmpeg:", e)

    # Fallback: estimate from file size (128kbps MP3)
    file_size = os.path.getsize(audio_path)
    return int((file_size * 8 / 128000) * SEC_TO_US)


def build_capcut_project(
    project_name: str,
    images: list[str],
    segments: list[SrtSegment],
    audio_path: str,
    canvas_width: int = 1920,
    canvas_height: int = 1080,
    progress_callback=None,
) -> str:
    """Generate a CapCut project from images + SRT + audio.

    Creates a project folder inside CapCut's local draft directory
    with all required JSON files. The user can then open CapCut
    and see the project in their drafts list.

    Args:
        project_name: Name shown in CapCut's project list.
        images: Sorted list of absolute image paths.
        segments: Parsed SRT segments.
        audio_path: Absolute path to the audio file.
        canvas_width: Canvas width (default 1920).
        canvas_height: Canvas height (default 1080).
        progress_callback: Optional fn(percent, message).

    Returns:
        Path to the created project folder.
    """
    if progress_callback:
        progress_callback(5, "Creating project structure...")

    # ── Create project folder ─────────────────────────────────────
    project_dir = os.path.join(CAPCUT_PROJECTS_ROOT, project_name)
    os.makedirs(project_dir, exist_ok=True)

    # Create subdirectories
    for sub in ['Resources', 'Timelines', 'adjust_mask', 'common_attachment',
                'matting', 'qr_upload', 'smart_crop', 'subdraft']:
        os.makedirs(os.path.join(project_dir, sub), exist_ok=True)

    draft_id = _uuid()
    video_track_id = _uuid()
    audio_track_id = _uuid()

    # ── Audio ─────────────────────────────────────────────────────
    audio_abs = os.path.abspath(audio_path)
    audio_duration_us = _get_audio_duration_us(audio_abs)
    audio_filename = os.path.basename(audio_abs)
    audio_mat_id = _uuid()

    # Audio extra materials
    audio_speed_id = _uuid()
    audio_beat_id = _uuid()
    audio_placeholder_id = _uuid()
    audio_balance_id = _uuid()
    audio_vocal_sep_id = _uuid()

    audio_material = _make_audio_material(
        audio_mat_id, audio_abs, audio_duration_us, audio_filename,
    )

    audio_segment = _make_audio_segment(
        seg_id=_uuid(),
        material_id=audio_mat_id,
        duration_us=audio_duration_us,
        extra_refs=[audio_speed_id, audio_placeholder_id, audio_beat_id,
                    audio_balance_id, audio_vocal_sep_id],
    )

    if progress_callback:
        progress_callback(15, "Processing images...")

    # ── Images / Video segments ───────────────────────────────────
    video_materials = []
    video_segments = []
    canvases = []
    speeds = [{"id": audio_speed_id, "type": "speed", "mode": 0, "speed": 1.0, "curve_speed": None}]
    material_animations = []
    placeholder_infos = [
        {"id": audio_placeholder_id, "type": "placeholder_info",
         "meta_type": "none", "res_path": "", "res_text": "",
         "error_path": "", "error_text": ""},
    ]
    sound_channel_mappings = []
    material_colors = []
    vocal_separations = [
        {"id": audio_vocal_sep_id, "type": "vocal_separation",
         "choice": 0, "removed_sounds": [], "time_range": None,
         "production_path": "", "final_algorithm": "", "enter_from": ""},
    ]

    current_time_us = 0
    total_segments = len(segments)

    for i, seg in enumerate(segments):
        if progress_callback:
            pct = 15 + int((i / max(total_segments, 1)) * 60)
            progress_callback(pct, f"Processing segment {i + 1}/{total_segments}...")

        # Pick image (reuse last if fewer images than segments)
        img_path = images[i] if i < len(images) else images[-1]
        img_abs = os.path.abspath(img_path)
        img_filename = os.path.basename(img_path)

        # Get dimensions
        try:
            w, h = _get_image_dimensions(img_abs)
        except Exception:
            w, h = canvas_width, canvas_height

        # Create material
        mat_id = _uuid()
        video_materials.append(
            _make_photo_material(mat_id, img_abs, w, h, img_filename)
        )

        # Extra material refs for this segment
        canvas_id = _uuid()
        speed_id = _uuid()
        anim_id = _uuid()
        ph_id = _uuid()
        sc_id = _uuid()
        mc_id = _uuid()
        vs_id = _uuid()

        canvases.append({
            "id": canvas_id, "type": "canvas_color", "color": "",
            "blur": 0.0, "image": "", "album_image": "",
            "image_id": "", "image_name": "",
            "source_platform": 0, "team_id": "",
        })
        speeds.append({"id": speed_id, "type": "speed", "mode": 0, "speed": 1.0, "curve_speed": None})
        material_animations.append({
            "id": anim_id, "type": "sticker_animation",
            "animations": [], "multi_language_current": "none",
        })
        placeholder_infos.append({
            "id": ph_id, "type": "placeholder_info",
            "meta_type": "none", "res_path": "", "res_text": "",
            "error_path": "", "error_text": "",
        })
        sound_channel_mappings.append({
            "id": sc_id, "type": "", "audio_channel_mapping": 0,
            "is_config_open": False,
        })
        material_colors.append({
            "id": mc_id, "is_color_clip": False, "is_gradient": False,
            "solid_color": "", "gradient_colors": [],
            "gradient_percents": [], "gradient_angle": 90.0,
            "width": 0.0, "height": 0.0,
        })
        vocal_separations.append({
            "id": vs_id, "type": "vocal_separation",
            "choice": 0, "removed_sounds": [], "time_range": None,
            "production_path": "", "final_algorithm": "", "enter_from": "",
        })

        extra_refs = [speed_id, ph_id, canvas_id, anim_id, sc_id, mc_id, vs_id]

        # Calculate exact timeline coverage to avoid gaps
        start_sec = 0 if i == 0 else seg.start_time
        if i < total_segments - 1:
            end_sec = segments[i + 1].start_time
        else:
            end_sec = seg.end_time

        target_start_us = _sec_us(start_sec)
        duration_us = _sec_us(end_sec - start_sec)

        video_segments.append(
            _make_video_segment(
                seg_id=_uuid(),
                material_id=mat_id,
                target_start_us=target_start_us,
                duration_us=duration_us,
                extra_refs=extra_refs,
            )
        )

        current_time_us = target_start_us + duration_us

    # Also add audio channel mapping for audio segment
    audio_sc_id = _uuid()
    sound_channel_mappings.append({
        "id": audio_sc_id, "type": "", "audio_channel_mapping": 0,
        "is_config_open": False,
    })

    total_duration_us = current_time_us

    if progress_callback:
        progress_callback(80, "Writing project files...")

    # ── Build draft_content.json ──────────────────────────────────
    draft_content = {
        "id": draft_id,
        "version": 360000,
        "new_version": "171.0.0",
        "name": "",
        "duration": total_duration_us,
        "create_time": 0,
        "update_time": 0,
        "fps": 30.0,
        "is_drop_frame_timecode": False,
        "color_space": 0,
        "config": {
            "video_mute": False,
            "record_audio_last_index": 1,
            "extract_audio_last_index": 1,
            "original_sound_last_index": 1,
            "subtitle_recognition_id": "",
            "subtitle_taskinfo": [],
            "lyrics_recognition_id": "",
            "lyrics_taskinfo": [],
            "subtitle_sync": True,
            "lyrics_sync": True,
            "voice_change_sync": False,
            "sticker_max_index": 1,
            "adjust_max_index": 1,
            "material_save_mode": 0,
            "export_range": None,
            "maintrack_adsorb": False,
            "combination_max_index": 1,
            "attachment_info": [],
            "zoom_info_params": None,
            "system_font_list": [],
            "multi_language_mode": "none",
            "multi_language_main": "none",
            "multi_language_current": "none",
            "multi_language_list": [],
            "subtitle_keywords_config": None,
            "use_float_render": False,
        },
        "canvas_config": {
            "ratio": "original",
            "width": canvas_width,
            "height": canvas_height,
            "background": None,
        },
        "tracks": [
            {
                "id": video_track_id,
                "type": "video",
                "segments": video_segments,
                "flag": 0,
                "attribute": 0,
                "name": "",
                "is_default_name": True,
            },
            {
                "id": audio_track_id,
                "type": "audio",
                "segments": [audio_segment],
                "flag": 0,
                "attribute": 0,
                "name": "",
                "is_default_name": True,
            },
        ],
        "group_container": None,
        "materials": {
            "flowers": [],
            "videos": video_materials,
            "tail_leaders": [],
            "audios": [audio_material],
            "images": [],
            "texts": [],
            "effects": [],
            "stickers": [],
            "canvases": canvases,
            "transitions": [],
            "audio_effects": [],
            "audio_fades": [],
            "beats": [{"id": audio_beat_id, "type": "beats", "enable_ai_beats": False,
                       "gear": 404, "gear_count": 0, "mode": 404,
                       "user_beats": [], "user_delete_ai_beats": None,
                       "ai_beats": {"melody_url": "", "melody_path": "",
                                    "beats_url": "", "beats_path": "",
                                    "melody_percents": [0.0],
                                    "beat_speed_infos": []}}],
            "material_animations": material_animations,
            "placeholders": [],
            "placeholder_infos": placeholder_infos,
            "speeds": speeds,
            "common_mask": [],
            "chromas": [],
            "text_templates": [],
            "realtime_denoises": [],
            "audio_pannings": [],
            "audio_pitch_shifts": [],
            "video_trackings": [],
            "hsl": [],
            "drafts": [],
            "color_curves": [],
            "hsl_curves": [],
            "primary_color_wheels": [],
            "log_color_wheels": [],
            "video_effects": [],
            "audio_balances": [{"id": audio_balance_id}] if audio_balance_id else [],
            "handwrites": [],
            "manual_deformations": [],
            "manual_beautys": [],
            "plugin_effects": [],
            "sound_channel_mappings": sound_channel_mappings,
            "green_screens": [],
            "shapes": [],
            "material_colors": material_colors,
            "digital_humans": [],
            "digital_human_model_dressing": [],
            "smart_crops": [],
            "ai_translates": [],
            "audio_track_indexes": [],
            "loudnesses": [],
            "vocal_beautifys": [],
            "vocal_separations": vocal_separations,
            "smart_relights": [],
            "time_marks": [],
            "multi_language_refs": [],
            "video_shadows": [],
            "video_strokes": [],
            "video_radius": [],
        },
        "keyframes": {
            "videos": [], "audios": [], "texts": [],
            "stickers": [], "filters": [], "adjusts": [],
            "handwrites": [], "effects": [],
        },
        "keyframe_graph_list": [],
        "platform": {
            "os": "windows",
            "os_version": "10.0.26200",
            "app_id": 359289,
            "app_version": "8.7.0",
            "app_source": "cc",
            "device_id": "",
            "hard_disk_id": "",
            "mac_address": "",
        },
        "last_modified_platform": {
            "os": "windows",
            "os_version": "10.0.26200",
            "app_id": 359289,
            "app_version": "8.7.0",
            "app_source": "cc",
            "device_id": "",
            "hard_disk_id": "",
            "mac_address": "",
        },
        "mutable_config": None,
        "cover": None,
        "retouch_cover": None,
        "extra_info": None,
        "relationships": [],
        "render_index_track_mode_on": True,
        "free_render_index_mode_on": False,
        "static_cover_image_path": "",
        "source": "default",
        "time_marks": None,
        "path": "",
        "lyrics_effects": [],
        "uneven_animation_template_info": {
            "composition": "", "content": "", "order": "",
            "sub_template_info_list": [],
        },
        "draft_type": "video",
        "smart_ads_info": {"page_from": "", "routine": "", "draft_url": ""},
        "function_assistant_info": {
            "smart_rec_applied": False, "fixed_rec_applied": False,
            "auto_adjust": False, "auto_adjust_segid_list": [],
            "color_correction": False, "color_correction_segid_list": [],
            "enhance_quality": False, "smooth_slow_motion": False,
            "deflicker_segid_list": [], "video_noise_segid_list": [],
            "enhance_quality_segid_list": [], "smart_segid_list": [],
            "retouch": False, "retouch_segid_list": [],
            "enhande_voice": False, "enhance_voice_segid_list": [],
            "audio_noise_segid_list": [], "auto_caption": False,
            "auto_caption_segid_list": [], "auto_caption_template_id": "",
            "caption_opt": False, "caption_opt_segid_list": [],
            "eye_correction": False, "eye_correction_segid_list": [],
            "normalize_loudness": False,
            "normalize_loudness_segid_list": [],
            "normalize_loudness_audio_denoise_segid_list": [],
            "auto_adjust_fixed": False, "auto_adjust_fixed_value": 50.0,
            "color_correction_fixed": False, "color_correction_fixed_value": 50.0,
            "normalize_loudness_fixed": False,
            "enhande_voice_fixed": False, "retouch_fixed": False,
            "enhance_quality_fixed": False, "smooth_slow_motion_fixed": False,
            "fps": {"num": 0, "den": 1},
        },
    }

    # Write draft_content.json
    content_path = os.path.join(project_dir, 'draft_content.json')
    with open(content_path, 'w', encoding='utf-8') as f:
        json.dump(draft_content, f, ensure_ascii=False, separators=(',', ':'))

    # Write backup
    shutil.copy2(content_path, content_path + '.bak')

    if progress_callback:
        progress_callback(90, "Writing metadata...")

    # ── Build draft_meta_info.json ────────────────────────────────
    now_ts = int(time.time())
    now_ts_us = now_ts * SEC_TO_US

    draft_materials = []
    # Audio material entry
    draft_materials.append({
        "ai_group_type": "", "create_time": now_ts,
        "duration": audio_duration_us // (SEC_TO_US // 1000),  # milliseconds? No, same unit
        "enter_from": 0, "extra_info": audio_filename,
        "file_Path": audio_abs.replace('\\', '/'),
        "height": 0,
        "id": str(uuid.uuid4()),
        "import_time": now_ts,
        "import_time_ms": now_ts_us,
        "item_source": 1, "md5": "",
        "metetype": "music",
        "roughcut_time_range": {"duration": audio_duration_us, "start": 0},
        "sub_time_range": {"duration": -1, "start": -1},
        "type": 0, "width": 0,
    })

    # Image material entries
    for img_path in images:
        img_abs_path = os.path.abspath(img_path)
        img_fn = os.path.basename(img_path)
        try:
            w, h = _get_image_dimensions(img_abs_path)
        except Exception:
            w, h = 0, 0
        draft_materials.append({
            "ai_group_type": "", "create_time": now_ts,
            "duration": 5000000,
            "enter_from": 0, "extra_info": img_fn,
            "file_Path": img_abs_path.replace('\\', '/'),
            "height": h,
            "id": str(uuid.uuid4()),
            "import_time": now_ts,
            "import_time_ms": now_ts_us,
            "item_source": 1, "md5": "",
            "metetype": "photo",
            "roughcut_time_range": {"duration": -1, "start": -1},
            "sub_time_range": {"duration": -1, "start": -1},
            "type": 0, "width": w,
        })

    draft_meta = {
        "cloud_draft_cover": False,
        "cloud_draft_sync": False,
        "cloud_package_completed_time": "",
        "draft_cloud_capcut_purchase_info": "",
        "draft_cloud_last_action_download": False,
        "draft_cloud_package_type": "",
        "draft_cloud_purchase_info": "",
        "draft_cloud_template_id": "",
        "draft_cloud_tutorial_info": "",
        "draft_cloud_videocut_purchase_info": "",
        "draft_cover": "",
        "draft_deeplink_url": "",
        "draft_enterprise_info": {
            "draft_enterprise_extra": "",
            "draft_enterprise_id": "",
            "draft_enterprise_name": "",
            "enterprise_material": [],
        },
        "draft_fold_path": project_dir.replace('\\', '/'),
        "draft_id": draft_id,
        "draft_is_ae_produce": False,
        "draft_is_ai_packaging_used": False,
        "draft_is_ai_shorts": False,
        "draft_is_ai_translate": False,
        "draft_is_article_video_draft": False,
        "draft_is_cloud_temp_draft": False,
        "draft_is_from_deeplink": "false",
        "draft_is_invisible": False,
        "draft_is_pippit_draft": False,
        "draft_is_web_article_video": False,
        "draft_materials": [
            {"type": 0, "value": draft_materials},
            {"type": 1, "value": []},
            {"type": 2, "value": []},
            {"type": 3, "value": []},
            {"type": 6, "value": []},
            {"type": 7, "value": []},
            {"type": 8, "value": []},
        ],
        "draft_materials_copied_info": [],
        "draft_name": project_name,
        "draft_need_rename_folder": False,
        "draft_new_version": "",
        "draft_removable_storage_device": "",
        "draft_root_path": CAPCUT_PROJECTS_ROOT.replace('\\', '/'),
        "draft_segment_extra_info": [],
        "draft_timeline_materials_size_": 0,
        "draft_type": "",
        "draft_web_article_video_enter_from": "",
        "tm_draft_cloud_completed": "",
        "tm_draft_cloud_entry_id": -1,
        "tm_draft_cloud_modified": 0,
        "tm_draft_cloud_parent_entry_id": -1,
        "tm_draft_cloud_space_id": -1,
        "tm_draft_cloud_user_id": -1,
        "tm_draft_create": now_ts_us,
        "tm_draft_modified": now_ts_us,
        "tm_draft_removed": 0,
        "tm_duration": total_duration_us,
    }

    with open(os.path.join(project_dir, 'draft_meta_info.json'), 'w', encoding='utf-8') as f:
        json.dump(draft_meta, f, ensure_ascii=False, separators=(',', ':'))

    # ── Other config files ────────────────────────────────────────
    with open(os.path.join(project_dir, 'draft_agency_config.json'), 'w') as f:
        json.dump({
            "is_auto_agency_enabled": False,
            "is_auto_agency_popup": False,
            "is_single_agency_mode": False,
            "marterials": None,
            "use_converter": False,
            "video_resolution": 720,
        }, f)

    with open(os.path.join(project_dir, 'draft_biz_config.json'), 'w') as f:
        json.dump({
            "timeline_settings": {
                draft_id: {"adsorb_enabled": False, "linkage_enabled": False}
            },
            "track_settings": {
                video_track_id: {"height": 113}
            },
        }, f, indent=4)

    with open(os.path.join(project_dir, 'draft_settings'), 'w') as f:
        f.write(f"[General]\n")
        f.write(f"draft_create_time={now_ts}\n")
        f.write(f"draft_last_edit_time={now_ts}\n")
        f.write(f"real_edit_seconds=0\n")
        f.write(f"real_edit_keys=0\n")

    with open(os.path.join(project_dir, 'draft_virtual_store.json'), 'w') as f:
        json.dump({"version": 1, "virtual_store": []}, f)

    with open(os.path.join(project_dir, 'performance_opt_info.json'), 'w') as f:
        json.dump({"performance_opt_info": {"split_screen": False}}, f)

    with open(os.path.join(project_dir, 'timeline_layout.json'), 'w') as f:
        json.dump({"timeline_layout": {"expand_track_ids": [video_track_id]}}, f)

    with open(os.path.join(project_dir, 'attachment_pc_common.json'), 'w') as f:
        json.dump({
            "attachment_common_info": [],
            "enable_ai_music": False,
            "enable_ai_music_v2": False,
            "enable_text_to_video": False,
        }, f)

    # ── Update root_meta_info.json ────────────────────────────────
    _register_project(project_name, draft_id, project_dir, now_ts_us, total_duration_us)

    if progress_callback:
        progress_callback(100, "CapCut project created!")

    return project_dir


def _register_project(
    name: str, draft_id: str, folder: str,
    timestamp_us: int, duration_us: int,
):
    """Register the new project in CapCut's root_meta_info.json."""
    root_meta_path = os.path.join(CAPCUT_PROJECTS_ROOT, 'root_meta_info.json')

    if os.path.isfile(root_meta_path):
        with open(root_meta_path, 'r', encoding='utf-8') as f:
            root_meta = json.load(f)
    else:
        root_meta = {
            "all_draft_store": [],
            "draft_ids": 0,
            "root_path": CAPCUT_PROJECTS_ROOT.replace('\\', '/'),
        }

    # Check if already registered
    for entry in root_meta.get('all_draft_store', []):
        if entry.get('draft_fold_path', '').rstrip('/').endswith(name):
            return  # Already registered

    # Add new entry
    new_entry = {
        "draft_fold_path": folder.replace('\\', '/'),
        "draft_id": draft_id,
        "draft_name": name,
        "draft_new_version": "",
        "draft_removable_storage_device": "",
        "draft_root_path": CAPCUT_PROJECTS_ROOT.replace('\\', '/'),
        "tm_draft_cloud_completed": "",
        "tm_draft_cloud_entry_id": -1,
        "tm_draft_cloud_modified": 0,
        "tm_draft_cloud_parent_entry_id": -1,
        "tm_draft_cloud_space_id": -1,
        "tm_draft_cloud_user_id": -1,
        "tm_draft_create": timestamp_us,
        "tm_draft_modified": timestamp_us,
        "tm_draft_removed": 0,
        "tm_duration": duration_us,
    }

    root_meta['all_draft_store'].insert(0, new_entry)
    root_meta['draft_ids'] = root_meta.get('draft_ids', 0) + 1

    with open(root_meta_path, 'w', encoding='utf-8') as f:
        json.dump(root_meta, f, ensure_ascii=False, separators=(',', ':'))
