# Sound & Image Notes (local app)

A small app that runs on your computer. Upload a sound file and an image:
the sound is transcribed (Whisper) and the image's text is read (Tesseract OCR).
Then it asks **"What is this text about?"** and uses your answer as the heading.
Everything happens offline on your machine once the models are downloaded.

## 1. Install once

1. **Python 3.9+**: https://www.python.org/downloads/
2. **Tesseract OCR** (reads text in images)
   - Windows: install from https://github.com/UB-Mannheim/tesseract/wiki
     and tick the extra languages you need (e.g. Marathi, Hindi).
   - Mac: `brew install tesseract tesseract-lang`
   - Linux: `sudo apt install tesseract-ocr tesseract-ocr-mar tesseract-ocr-hin`
3. **Python packages** — in this folder run:
   ```
   pip install -r requirements.txt
   ```

## 2. Run

```
python app.py
```

Open http://127.0.0.1:5000 in your browser.

The first sound file takes longer because the speech model (~460 MB for `small`)
downloads once. For faster but less accurate transcription:
`WHISPER_MODEL=base python app.py` (Windows: `set WHISPER_MODEL=base` then `python app.py`).
For better accuracy, especially for Marathi, use `medium`.
