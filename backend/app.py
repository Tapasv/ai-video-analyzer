from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
import traceback
from dotenv import load_dotenv

# Load .env file so API keys are available as environment variables
# This must happen before importing the analyzers because they read
# the keys at import time via os.environ.get()
load_dotenv()

from analyzer.extractor import extract_audio_from_video
from analyzer.transcriber import transcribe_audio
from analyzer.sentiment import analyze_sentiment
from analyzer.emotion import analyze_emotion
from analyzer.clarity import analyze_clarity
from analyzer.scorer import compute_score

app = Flask(__name__)

# Allow requests from the React frontend
# In production, replace * with your actual Vercel URL
CORS(app, origins=[
    os.environ.get("FRONTEND_URL", "*")
])

ALLOWED_EXTENSIONS = {"mp4", "mov", "avi", "webm", "mkv"}
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024  # 100MB limit


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/analyze", methods=["POST"])
def analyze():
    if "video" not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    file = request.files["video"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed. Use mp4, mov, avi, webm, or mkv"}), 400

    try:
        # Save uploaded video to a temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_video:
            file.save(tmp_video.name)
            video_path = tmp_video.name

        # Step 1: Extract audio from video
        audio_path = extract_audio_from_video(video_path)

        # Step 2: Transcribe audio via AssemblyAI API
        transcript = transcribe_audio(audio_path)

        # Step 3: Analyze sentiment via HuggingFace API
        sentiment_result = analyze_sentiment(transcript["text"])

        # Step 4: Detect facial emotions using OpenCV (no external API)
        emotion_result = analyze_emotion(video_path)

        # Step 5: Analyze speaking clarity (local, no API needed)
        clarity_result = analyze_clarity(transcript)

        # Step 6: Compute final score
        score_result = compute_score(sentiment_result, emotion_result, clarity_result)

        # Clean up temp files
        os.unlink(video_path)
        os.unlink(audio_path)

        return jsonify({
            "transcript": transcript["text"],
            "sentiment": sentiment_result,
            "emotion": emotion_result,
            "clarity": clarity_result,
            "score": score_result
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)