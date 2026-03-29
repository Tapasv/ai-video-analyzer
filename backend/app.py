from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
import traceback
from dotenv import load_dotenv

load_dotenv()

from analyzer.extractor import extract_audio_from_video
from analyzer.transcriber import transcribe_audio
from analyzer.sentiment import analyze_sentiment
from analyzer.emotion import analyze_emotion
from analyzer.clarity import analyze_clarity
from analyzer.scorer import compute_score

app = Flask(__name__)

# Allow ALL origins — fixes CORS for any frontend domain
CORS(app, resources={r"/*": {"origins": "*"}})

ALLOWED_EXTENSIONS = {"mp4", "mov", "avi", "webm", "mkv"}
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.after_request
def add_cors_headers(response):
    """
    This function runs after every request and manually adds
    CORS headers to every response — even error responses.
    This is a safety net in case flask-cors misses anything.
    """
    response.headers["Access-Control-Allow-Origin"]  = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/analyze", methods=["POST", "OPTIONS"])
def analyze():
    # Handle preflight OPTIONS request from browser
    # Browser sends OPTIONS first to check if CORS is allowed
    # before sending the actual POST request
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    if "video" not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    file = request.files["video"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed. Use mp4, mov, avi, webm, or mkv"}), 400

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_video:
            file.save(tmp_video.name)
            video_path = tmp_video.name

        audio_path    = extract_audio_from_video(video_path)
        transcript    = transcribe_audio(audio_path)
        sentiment_result = analyze_sentiment(transcript["text"])
        emotion_result   = analyze_emotion(video_path)
        clarity_result   = analyze_clarity(transcript)
        score_result     = compute_score(sentiment_result, emotion_result, clarity_result)

        os.unlink(video_path)
        os.unlink(audio_path)

        return jsonify({
            "transcript": transcript["text"],
            "sentiment":  sentiment_result,
            "emotion":    emotion_result,
            "clarity":    clarity_result,
            "score":      score_result
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)