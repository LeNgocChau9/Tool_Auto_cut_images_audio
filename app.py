"""CutCut – Auto Video Builder.

Flask backend that handles file uploads, SRT/image preview,
video building with progress tracking, and download.
"""

import os
import uuid
import shutil
import threading
import time

from flask import (
    Flask, render_template, request, jsonify, send_file, send_from_directory,
)

from engine.srt_parser import parse_srt
from engine.image_sorter import get_sorted_images, SUPPORTED_EXTENSIONS
from engine.capcut_builder import build_capcut_project

# ── App setup ─────────────────────────────────────────────────────
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500 MB

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')

os.makedirs(UPLOAD_DIR, exist_ok=True)

# In-memory build status (session_id → dict)
build_status: dict[str, dict] = {}


# ── Pages ─────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')


# ── API: Upload files ─────────────────────────────────────────────
@app.route('/api/upload', methods=['POST'])
def api_upload():
    """Accept MP3, SRT, and image files.  Return a session ID."""
    try:
        session_id = uuid.uuid4().hex[:8]
        session_dir = os.path.join(UPLOAD_DIR, session_id)
        os.makedirs(session_dir, exist_ok=True)

        result = {'session_id': session_id, 'mp3': None, 'srt': None, 'images': []}

        # ── Audio ─────────────────────────────────────────────────────
        mp3 = request.files.get('mp3')
        if mp3 and mp3.filename:
            ext = os.path.splitext(mp3.filename)[1].lower() or '.mp3'
            audio_name = f'audio{ext}'
            mp3.save(os.path.join(session_dir, audio_name))
            result['mp3'] = mp3.filename

        # ── SRT ───────────────────────────────────────────────────────
        srt = request.files.get('srt')
        if srt and srt.filename:
            srt.save(os.path.join(session_dir, 'subtitles.srt'))
            result['srt'] = srt.filename

        # ── Images ────────────────────────────────────────────────────
        images = request.files.getlist('images')
        img_dir = os.path.join(session_dir, 'images')
        os.makedirs(img_dir, exist_ok=True)

        for img in images:
            if img and img.filename:
                filename = os.path.basename(img.filename)
                ext = os.path.splitext(filename)[1].lower()
                if ext in SUPPORTED_EXTENSIONS:
                    img.save(os.path.join(img_dir, filename))
                    result['images'].append(filename)

        result['image_count'] = len(result['images'])
        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ── API: Preview mapping ─────────────────────────────────────────
@app.route('/api/preview/<session_id>')
def api_preview(session_id):
    """Return the image ↔ SRT segment mapping for review."""
    session_dir = os.path.join(UPLOAD_DIR, session_id)
    if not os.path.isdir(session_dir):
        return jsonify({'error': 'Session not found'}), 404

    try:
        segments = parse_srt(os.path.join(session_dir, 'subtitles.srt'))
        images = get_sorted_images(os.path.join(session_dir, 'images'))

        mapping = []
        for i, seg in enumerate(segments):
            img_name = (
                os.path.basename(images[i])
                if i < len(images)
                else os.path.basename(images[-1])
            )
            mapping.append({
                'index': seg.index,
                'image': img_name,
                'start_display': seg.start_display(),
                'end_display': seg.end_display(),
                'duration': round(seg.duration, 2),
                'text': seg.text,
                'reused': i >= len(images),
            })

        warning = None
        if len(images) == 0:
            warning = "Không có ảnh nào được tải lên!"
        elif len(images) < len(segments):
            warning = (
                f"Chỉ có {len(images)} ảnh cho {len(segments)} đoạn. "
                f"Ảnh cuối sẽ được dùng lại cho các đoạn còn thừa."
            )
        elif len(images) > len(segments):
            warning = (
                f"Có {len(images)} ảnh nhưng chỉ {len(segments)} đoạn SRT. "
                f"{len(images) - len(segments)} ảnh thừa sẽ bị bỏ qua."
            )

        return jsonify({
            'total_segments': len(segments),
            'total_images': len(images),
            'total_duration': round(segments[-1].end_time, 2) if segments else 0,
            'mapping': mapping,
            'warning': warning,
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f"Lỗi đọc file SRT hoặc Ảnh: {str(e)}"}), 500


# ── API: Serve uploaded images (for preview thumbnails) ───────────
@app.route('/api/image/<session_id>/<filename>')
def api_image(session_id, filename):
    img_dir = os.path.join(UPLOAD_DIR, session_id, 'images')
    return send_from_directory(img_dir, filename)


# ── API: Build project ───────────────────────────────────────────
@app.route('/api/build', methods=['POST'])
def api_build():
    """Start CapCut project build in a background thread."""
    data = request.json or {}
    session_id = data.get('session_id')
    project_name = data.get('project_name', f'CutCut_Project_{session_id[:6]}')

    if not session_id:
        return jsonify({'error': 'Missing session_id'}), 400

    session_dir = os.path.join(UPLOAD_DIR, session_id)
    if not os.path.isdir(session_dir):
        return jsonify({'error': 'Session not found'}), 404

    build_status[session_id] = {
        'status': 'building',
        'percent': 0,
        'message': 'Đang chuẩn bị...',
    }

    thread = threading.Thread(
        target=_build_worker,
        args=(session_id, session_dir, project_name),
        daemon=True,
    )
    thread.start()

    return jsonify({'status': 'building'})


def _build_worker(session_id, session_dir, project_name):
    """Background worker that builds the CapCut project."""
    try:
        srt_path = os.path.join(session_dir, 'subtitles.srt')
        img_dir = os.path.join(session_dir, 'images')

        # Find audio file (saved as audio.mp3, audio.wav, etc.)
        audio_path = None
        for f in os.listdir(session_dir):
            if f.startswith('audio'):
                audio_path = os.path.join(session_dir, f)
                break
        if not audio_path:
            raise FileNotFoundError("Audio file not found in session.")

        segments = parse_srt(srt_path)
        images = get_sorted_images(img_dir)

        def on_progress(percent, message):
            build_status[session_id] = {
                'status': 'building',
                'percent': percent,
                'message': message,
            }

        project_dir = build_capcut_project(
            project_name=project_name,
            images=images,
            segments=segments,
            audio_path=audio_path,
            progress_callback=on_progress,
        )

        build_status[session_id] = {
            'status': 'done',
            'percent': 100,
            'message': 'Project hoàn thành!',
            'project_dir': project_dir,
        }

    except Exception as exc:
        shutil.rmtree(session_dir, ignore_errors=True)
        build_status[session_id] = {
            'status': 'error',
            'percent': 0,
            'message': str(exc),
        }


# ── API: Check build status ──────────────────────────────────────
@app.route('/api/status/<session_id>')
def api_status(session_id):
    return jsonify(build_status.get(session_id, {'status': 'unknown'}))


# ── API: Cleanup session ─────────────────────────────────────────
@app.route('/api/cleanup/<session_id>', methods=['POST'])
def api_cleanup(session_id):
    session_dir = os.path.join(UPLOAD_DIR, session_id)
    output_path = os.path.join(OUTPUT_DIR, f'{session_id}.mp4')

    if os.path.isdir(session_dir):
        shutil.rmtree(session_dir, ignore_errors=True)
    if os.path.isfile(output_path):
        os.remove(output_path)
    build_status.pop(session_id, None)

    return jsonify({'status': 'cleaned'})


# ── API: Shutdown server ─────────────────────────────────────────
@app.route('/api/shutdown', methods=['POST'])
def api_shutdown():
    """Shutdown the Flask server from the Web UI."""
    import signal
    os.kill(os.getpid(), signal.SIGINT)
    return jsonify({'status': 'shutting down'})


# ── Main ──────────────────────────────────────────────────────────
if __name__ == '__main__':
    print()
    print('=' * 50)
    print('  CutCut – Auto Video Builder')
    print('  http://localhost:5000')
    print('=' * 50)
    print()
    app.run(debug=False, host='0.0.0.0', port=5000)
