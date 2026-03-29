import requests
import time
import os
from dotenv import load_dotenv

# Load .env directly in this file too — safety net in case
# app.py's load_dotenv() hasn't run yet when this module is imported
load_dotenv()

ASSEMBLYAI_API_KEY = os.environ.get("ASSEMBLYAI_API_KEY", "")

UPLOAD_URL     = "https://api.assemblyai.com/v2/upload"
TRANSCRIPT_URL = "https://api.assemblyai.com/v2/transcript"


def transcribe_audio(audio_path: str) -> dict:
    """
    Uploads the audio file to AssemblyAI and waits for
    the transcript to be ready. Returns a dict with:
      - "text": full transcript string
      - "segments": list of {start, end, text} chunks
    """

    if not ASSEMBLYAI_API_KEY:
        raise Exception("ASSEMBLYAI_API_KEY is missing. Check your .env file.")

    # Headers for every request — authorization proves who we are
    headers_auth_only = {"authorization": ASSEMBLYAI_API_KEY}
    headers_json      = {
        "authorization": ASSEMBLYAI_API_KEY,
        "content-type":  "application/json"
    }

    # ── STEP 1: Upload audio file to AssemblyAI ────────────────────
    # We read the audio as raw bytes and POST it directly
    # AssemblyAI stores it and gives back a temporary URL
    with open(audio_path, "rb") as f:
        upload_response = requests.post(
            UPLOAD_URL,
            headers=headers_auth_only,
            data=f
        )

    if upload_response.status_code != 200:
        raise Exception(
            f"AssemblyAI upload failed: {upload_response.status_code} — {upload_response.text}"
        )

    audio_url = upload_response.json()["upload_url"]

    # ── STEP 2: Request transcription ─────────────────────────────
    transcript_response = requests.post(
        TRANSCRIPT_URL,
        headers=headers_json,
        json={
            "audio_url":    audio_url,
            "punctuate":    True,
            "format_text":  True,
            "speech_models": ["universal-2"]
        }
    )

    if transcript_response.status_code != 200:
        raise Exception(
            f"AssemblyAI transcript request failed: {transcript_response.status_code} — {transcript_response.text}"
        )

    transcript_id = transcript_response.json()["id"]

    # ── STEP 3: Poll until transcription is complete ───────────────
    # AssemblyAI processes asynchronously — we check every 3 seconds
    polling_url = f"{TRANSCRIPT_URL}/{transcript_id}"

    while True:
        poll_response = requests.get(polling_url, headers=headers_json)
        poll_response.raise_for_status()
        result = poll_response.json()

        if result["status"] == "completed":
            break
        elif result["status"] == "error":
            raise Exception(f"AssemblyAI transcription error: {result.get('error')}")

        time.sleep(3)

    # ── STEP 4: Format result into our app's expected structure ────
    full_text = result.get("text", "")
    words     = result.get("words", [])
    segments  = []

    if words:
        # Group every 10 words into one segment chunk
        chunk_size = 10
        for i in range(0, len(words), chunk_size):
            chunk = words[i:i + chunk_size]
            segments.append({
                "start": chunk[0]["start"] / 1000.0,  # ms → seconds
                "end":   chunk[-1]["end"]  / 1000.0,
                "text":  " ".join(w["text"] for w in chunk)
            })

    return {
        "text":     full_text,
        "segments": segments
    }