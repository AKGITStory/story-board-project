"""Sound & Image Notes — local app.

Upload a sound file and an image; the sound is transcribed with Whisper,
the image is read with Tesseract OCR, and you give the combined text a heading.

Run:  python app.py   then open http://127.0.0.1:5000
"""
import os
import re
import tempfile

from flask import Flask, jsonify, render_template, request, Response

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024  # 200 MB uploads

WHISPER_MODEL = os.environ.get("WHISPER_MODEL", "small")
_whisper = None


def get_whisper():
    # Loaded on first use so the app starts quickly
    global _whisper
    if _whisper is None:
        from faster_whisper import WhisperModel
        _whisper = WhisperModel(WHISPER_MODEL, device="auto", compute_type="int8")
    return _whisper


def transcribe_audio(path, language=None):
    segments, info = get_whisper().transcribe(path, language=language or None, vad_filter=True)
    return " ".join(s.text.strip() for s in segments).strip(), info.language


def read_image(path, lang="eng"):
    import pytesseract
    from PIL import Image, ImageOps

    img = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    return pytesseract.image_to_string(img, lang=lang).strip()


def save_upload(storage):
    suffix = os.path.splitext(storage.filename or "")[1]
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, "wb") as f:
        storage.save(f)
    return path


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/audio")
def api_audio():
    f = request.files.get("file")
    if not f:
        return jsonify(error="No sound file was uploaded."), 400
    path = save_upload(f)
    try:
        text, lang = transcribe_audio(path, request.form.get("language"))
        return jsonify(text=text, language=lang)
    except Exception as e:
        return jsonify(error=f"Couldn't transcribe this file: {e}"), 500
    finally:
        os.remove(path)


@app.post("/api/image")
def api_image():
    f = request.files.get("file")
    if not f:
        return jsonify(error="No image was uploaded."), 400
    path = save_upload(f)
    try:
        return jsonify(text=read_image(path, request.form.get("lang", "eng")))
    except Exception as e:
        return jsonify(error=f"Couldn't read this image: {e}"), 500
    finally:
        os.remove(path)


@app.post("/api/save")
def api_save():
    data = request.get_json(force=True)
    header = (data.get("header") or "").strip()
    parts = [header, ""]
    if (data.get("audio") or "").strip():
        parts += ["From the sound", data["audio"].strip(), ""]
    if (data.get("image") or "").strip():
        parts += ["From the image", data["image"].strip(), ""]
    name = re.sub(r"[^\w\- ]+", "", header).strip().replace(" ", "-")[:60] or "notes"
    return Response(
        "\n".join(parts).strip() + "\n",
        content_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{name}.txt"'},
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)), debug=False)
