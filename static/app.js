/**
 * CutCut – Frontend Application
 *
 * State machine: UPLOAD → PREVIEW → BUILD → DONE/ERROR
 */

// ── Helpers ──────────────────────────────────────────────────────
const $ = (s) => document.querySelector(s);
const $$ = (s) => document.querySelectorAll(s);

const IMAGE_EXTS = new Set([
    '.jpg','.jpeg','.png','.webp','.bmp','.tiff','.tif','.gif',
]);

function isImageFile(name) {
    const ext = '.' + name.split('.').pop().toLowerCase();
    return IMAGE_EXTS.has(ext);
}

function formatBytes(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1048576).toFixed(1) + ' MB';
}

function showToast(msg) {
    const t = $('#toast');
    $('#toast-msg').textContent = msg;
    t.style.display = 'flex';
    clearTimeout(t._tid);
    t._tid = setTimeout(() => t.style.display = 'none', 6000);
}

// ── State ────────────────────────────────────────────────────────
const state = {
    mp3File: null,
    srtFile: null,
    imageFiles: [],     // File objects
    sessionId: null,
    pollTimer: null,
};

// ── Init ─────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    setupZone('mp3');
    setupZone('srt');
    setupZone('images');
    setupButtons();
    $('#toast-close').onclick = () => $('#toast').style.display = 'none';
});

// ── File Zones ───────────────────────────────────────────────────
function setupZone(type) {
    const zone = $(`#zone-${type}`);
    const input = $(`#input-${type}`);

    // Click → open file picker
    zone.addEventListener('click', (e) => {
        if (e.target.closest('.badge-remove')) return;
        input.click();
    });

    // File picker change
    input.addEventListener('change', () => {
        if (type === 'images') {
            const files = Array.from(input.files).filter(f => isImageFile(f.name));
            if (files.length) setFiles(type, files);
        } else if (input.files[0]) {
            setFiles(type, input.files[0]);
        }
    });

    // Drag & Drop
    zone.addEventListener('dragenter', (e) => { e.preventDefault(); zone.classList.add('dragover'); });
    zone.addEventListener('dragover',  (e) => { e.preventDefault(); zone.classList.add('dragover'); });
    zone.addEventListener('dragleave', ()  => { zone.classList.remove('dragover'); });
    zone.addEventListener('drop', (e) => {
        e.preventDefault();
        zone.classList.remove('dragover');
        handleDrop(type, e.dataTransfer);
    });

    // Remove button
    const rmBtn = zone.querySelector('.badge-remove');
    if (rmBtn) {
        rmBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            clearFiles(type);
        });
    }
}

async function handleDrop(type, dt) {
    if (type === 'images') {
        // Try folder via webkitGetAsEntry
        const items = Array.from(dt.items || []);
        const files = [];

        for (const item of items) {
            const entry = item.webkitGetAsEntry?.();
            if (entry) {
                const entryFiles = await readEntry(entry);
                files.push(...entryFiles);
            }
        }

        // Fallback to flat file list
        if (files.length === 0) {
            for (const f of dt.files) {
                if (isImageFile(f.name)) files.push(f);
            }
        }

        if (files.length) setFiles('images', files);
        else showToast('Không tìm thấy ảnh trong thư mục.');
    } else {
        const f = dt.files[0];
        if (f) setFiles(type, f);
    }
}

function readEntry(entry) {
    return new Promise((resolve) => {
        if (entry.isFile) {
            entry.file((f) => resolve(isImageFile(f.name) ? [f] : []));
        } else if (entry.isDirectory) {
            const reader = entry.createReader();
            const all = [];
            const readBatch = () => {
                reader.readEntries(async (entries) => {
                    if (entries.length === 0) { resolve(all); return; }
                    for (const e of entries) {
                        const sub = await readEntry(e);
                        all.push(...sub);
                    }
                    readBatch();
                });
            };
            readBatch();
        } else {
            resolve([]);
        }
    });
}

function setFiles(type, data) {
    const zone = $(`#zone-${type}`);
    const badge = $(`#badge-${type}`);
    const nameEl = badge.querySelector('.badge-name');

    if (type === 'mp3') {
        state.mp3File = data;
        nameEl.textContent = data.name;
    } else if (type === 'srt') {
        state.srtFile = data;
        nameEl.textContent = data.name;
    } else {
        state.imageFiles = Array.isArray(data) ? data : Array.from(data);
        nameEl.textContent = `${state.imageFiles.length} ảnh đã chọn`;
    }

    zone.classList.add('has-file');
    badge.style.display = 'inline-flex';
    checkReady();
}

function clearFiles(type) {
    const zone = $(`#zone-${type}`);
    const badge = $(`#badge-${type}`);
    const input = $(`#input-${type}`);

    if (type === 'mp3') state.mp3File = null;
    else if (type === 'srt') state.srtFile = null;
    else state.imageFiles = [];

    zone.classList.remove('has-file');
    badge.style.display = 'none';
    input.value = '';
    checkReady();
}

function checkReady() {
    const ready = state.mp3File && state.srtFile && state.imageFiles.length > 0;
    $('#action-upload').style.display = ready ? 'flex' : 'none';
}

// ── Buttons ──────────────────────────────────────────────────────
function setupButtons() {
    $('#btn-upload').addEventListener('click', doUpload);
    $('#btn-back').addEventListener('click', () => goStep(1));
    $('#btn-build').addEventListener('click', doBuild);
    $('#btn-new').addEventListener('click', doReset);
    $('#btn-retry').addEventListener('click', () => goStep(1));
}

// ── Step Navigation ──────────────────────────────────────────────
function goStep(n) {
    // Sections
    $('#section-upload').classList.toggle('hidden', n !== 1);
    $('#section-preview').classList.toggle('hidden', n !== 2);
    $('#section-build').classList.toggle('hidden', n !== 3);

    // Re-animate visible section
    const visible = $(`.section:not(.hidden)`);
    if (visible) {
        visible.style.animation = 'none';
        visible.offsetHeight; // reflow
        visible.style.animation = '';
    }

    // Steps indicator
    $$('.step').forEach((el) => {
        const s = +el.dataset.step;
        el.classList.toggle('active', s === n);
        el.classList.toggle('done', s < n);
    });
    $$('.step-line').forEach((el, i) => {
        el.classList.toggle('done', i + 1 < n);
        el.classList.toggle('active', i + 1 === n);
    });
}

// ── Upload ───────────────────────────────────────────────────────
async function doUpload() {
    const btn = $('#btn-upload');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner" style="width:20px;height:20px;border-width:2px"></span> Uploading...';

    try {
        const fd = new FormData();
        fd.append('mp3', state.mp3File);
        fd.append('srt', state.srtFile);
        for (const img of state.imageFiles) {
            fd.append('images', img, img.name);
        }

        const res = await fetch('/api/upload', { method: 'POST', body: fd });
        if (!res.ok) throw new Error('Upload failed: ' + res.statusText);

        const data = await res.json();
        state.sessionId = data.session_id;

        // Load preview
        await loadPreview();
        goStep(2);

    } catch (err) {
        showToast('Lỗi upload: ' + err.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = 'Upload &amp; Xem Preview <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>';
    }
}

// ── Preview ──────────────────────────────────────────────────────
async function loadPreview() {
    const res = await fetch(`/api/preview/${state.sessionId}`);
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.error || 'Preview failed');
    }
    const data = await res.json();
    renderPreview(data);
}

function renderPreview(data) {
    // Stats
    const statsBar = $('#stats-bar');
    statsBar.innerHTML = `
        <div class="stat"><span>Đoạn SRT:</span> <span class="stat-val">${data.total_segments}</span></div>
        <div class="stat"><span>Ảnh:</span> <span class="stat-val">${data.total_images}</span></div>
        <div class="stat"><span>Tổng thời lượng:</span> <span class="stat-val">${formatDuration(data.total_duration)}</span></div>
    `;

    // Warning
    const warn = $('#preview-warning');
    if (data.warning) {
        warn.textContent = '⚠️ ' + data.warning;
        warn.style.display = 'block';
    } else {
        warn.style.display = 'none';
    }

    // Table
    const tbody = $('#preview-body');
    tbody.innerHTML = '';

    for (const m of data.mapping) {
        const tr = document.createElement('tr');
        if (m.reused) tr.classList.add('reused');

        tr.innerHTML = `
            <td>${m.index}</td>
            <td><img class="thumb" src="/api/image/${state.sessionId}/${encodeURIComponent(m.image)}" alt="${m.image}" loading="lazy"></td>
            <td><span class="time-range">${m.start_display} → ${m.end_display}</span></td>
            <td><span class="duration-badge">${m.duration}s</span></td>
            <td><span class="sub-text" title="${escapeHtml(m.text)}">${escapeHtml(m.text)}</span></td>
        `;
        tbody.appendChild(tr);
    }
}

function formatDuration(sec) {
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    return `${m}:${String(s).padStart(2, '0')}`;
}

function escapeHtml(str) {
    const d = document.createElement('div');
    d.textContent = str;
    return d.innerHTML;
}

// ── Build ────────────────────────────────────────────────────────
async function doBuild() {
    const btn = $('#btn-build');
    btn.disabled = true;

    // Stop audio to release file lock on Windows
    const audioPlayer = $('#audio-player');
    if (audioPlayer) {
        audioPlayer.pause();
        audioPlayer.src = '';
        audioPlayer.load();
    }

    // Show build section
    $('#card-building').classList.remove('hidden');
    $('#card-done').classList.add('hidden');
    $('#card-error').classList.add('hidden');
    $('#progress-fill').style.width = '0%';
    $('#progress-pct').textContent = '0%';
    $('#progress-msg').textContent = 'Đang chuẩn bị...';
    goStep(3);

    try {
        let projectName = $('#input-project-name').value.trim();
        if (!projectName) {
            projectName = 'CutCut_Project_' + state.sessionId.substring(0, 6);
        }

        const res = await fetch('/api/build', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: state.sessionId,
                project_name: projectName,
            }),
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.error || 'Build request failed');
        }

        // Start polling
        pollStatus();

    } catch (err) {
        showError(err.message);
    }
}

function pollStatus() {
    clearInterval(state.pollTimer);
    state.pollTimer = setInterval(async () => {
        try {
            const res = await fetch(`/api/status/${state.sessionId}`);
            const data = await res.json();

            if (data.status === 'building') {
                $('#progress-fill').style.width = data.percent + '%';
                $('#progress-pct').textContent = data.percent + '%';
                $('#progress-msg').textContent = data.message || '';
            } else if (data.status === 'done') {
                clearInterval(state.pollTimer);
                showDone(data);
            } else if (data.status === 'error') {
                clearInterval(state.pollTimer);
                showError(data.message);
            }
        } catch (err) {
            // Network error, keep polling
        }
    }, 800);
}

function showDone(data) {
    $('#card-building').classList.add('hidden');
    $('#card-done').classList.remove('hidden');

    if (data.project_dir) {
        $('#file-size').textContent = `Lưu tại: ${data.project_dir}`;
    }
}

function showError(msg) {
    $('#card-building').classList.add('hidden');
    $('#card-error').classList.remove('hidden');
    $('#error-detail').textContent = msg;
}

// ── Reset ────────────────────────────────────────────────────────
function doReset() {
    // Cleanup server session
    if (state.sessionId) {
        fetch(`/api/cleanup/${state.sessionId}`, { method: 'POST' }).catch(() => {});
    }

    clearInterval(state.pollTimer);
    state.mp3File = null;
    state.srtFile = null;
    state.imageFiles = [];
    state.sessionId = null;

    // Reset UI
    ['mp3', 'srt', 'images'].forEach(clearFiles);
    $('#action-upload').style.display = 'none';
    $('#btn-build').disabled = false;
    $('#input-project-name').value = '';
    
    goStep(1);
}

// ── Shutdown ─────────────────────────────────────────────────────
async function shutdownServer() {
    if (!confirm('Bạn có chắc chắn muốn tắt Tool? (Server sẽ tự động tắt và bạn có thể đóng tab này)')) return;
    try {
        await fetch('/api/shutdown', { method: 'POST' });
    } catch (e) {}
    document.body.innerHTML = '<div style="display:flex; height:100vh; width:100vw; align-items:center; justify-content:center; flex-direction:column; background:#0f172a; color:#f8fafc; font-family:sans-serif;"><h2>Tool đã được tắt an toàn!</h2><p>Bạn có thể đóng tab này.</p></div>';
    setTimeout(() => window.close(), 1000);
}
