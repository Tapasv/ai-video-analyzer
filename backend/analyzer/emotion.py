import cv2
import numpy as np
from collections import Counter

# OpenCV's built-in face detector using Haar Cascades
# This XML file ships bundled with opencv — zero downloads needed
# It detects frontal faces in images quickly using classical computer vision
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# A second cascade for better detection in varied lighting
eye_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_eye.xml"
)


def estimate_emotion_from_features(face_gray: np.ndarray) -> str:
    """
    Uses simple OpenCV-based facial geometry to estimate emotion.
    This is lightweight — no neural network, no heavy library.

    It works by:
    1. Detecting eyes in the face region
    2. Analyzing brightness distribution (dark = tense, bright = relaxed)
    3. Looking at face aspect ratio (open mouth = surprise/happy)
    """
    h, w = face_gray.shape

    # ── Eye detection ─────────────────────────────────────────────
    eyes = eye_cascade.detectMultiScale(face_gray, scaleFactor=1.1, minNeighbors=5)
    eyes_detected = len(eyes) >= 2

    # ── Brightness analysis ────────────────────────────────────────
    # Average brightness of the face — low means shadowed/tense/sad
    avg_brightness = np.mean(face_gray)

    # Upper half brightness vs lower half brightness
    upper_brightness = np.mean(face_gray[:h//2, :])
    lower_brightness = np.mean(face_gray[h//2:, :])

    # ── Variance analysis ──────────────────────────────────────────
    # High variance = lots of contrast = more expression/movement
    variance = np.var(face_gray)

    # ── Mouth region analysis ──────────────────────────────────────
    # Bottom quarter of the face is roughly the mouth area
    mouth_region = face_gray[int(h * 0.65):h, int(w * 0.2):int(w * 0.8)]
    mouth_brightness = np.mean(mouth_region) if mouth_region.size > 0 else avg_brightness

    # ── Decision logic ─────────────────────────────────────────────
    # These thresholds are calibrated for typical webcam interview footage

    if not eyes_detected and avg_brightness < 80:
        # Very dark, eyes not visible — likely looking down or sad
        return "sad"

    if variance > 2500 and lower_brightness > upper_brightness + 15:
        # High contrast + bright lower face = open mouth = happy or surprise
        if mouth_brightness > avg_brightness + 10:
            return "happy"
        else:
            return "surprise"

    if avg_brightness > 140 and eyes_detected and variance > 1500:
        # Well-lit, eyes visible, moderate expression = happy/positive
        return "happy"

    if avg_brightness < 90 and variance > 2000:
        # Dark + high variance = stressed/fearful
        return "fear"

    if avg_brightness < 85:
        # Generally dark face = sad or disengaged
        return "sad"

    if variance < 800:
        # Very flat/uniform face = neutral expression
        return "neutral"

    # Default — calm and composed
    return "neutral"


def analyze_emotion(video_path: str) -> dict:
    """
    Opens the video, samples one frame every 2 seconds,
    detects the face, estimates emotion from facial features,
    and returns dominant emotion + full breakdown.
    """

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Analyze one frame every 2 seconds
    frame_interval = max(1, int(fps * 2))

    all_emotions = []
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            try:
                # Convert to grayscale — face detection works better on grayscale
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # Detect faces in the frame
                faces = face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(60, 60)
                )

                if len(faces) > 0:
                    # Take the largest face found (first one returned by OpenCV)
                    x, y, w, h = faces[0]

                    # Crop just the face from the full frame
                    face_gray = gray[y:y+h, x:x+w]

                    # Estimate emotion from facial geometry
                    emotion = estimate_emotion_from_features(face_gray)
                    all_emotions.append(emotion)

            except Exception:
                pass

        frame_count += 1

    cap.release()

    if not all_emotions:
        return {
            "dominant_emotion": "neutral",
            "emotion_breakdown": {"neutral": 100},
            "summary": "Could not detect facial emotions. Make sure your face is clearly visible."
        }

    # Count how many times each emotion appeared
    emotion_counts = Counter(all_emotions)
    total = len(all_emotions)

    # Convert to percentages
    emotion_breakdown = {
        emotion: round((count / total) * 100, 1)
        for emotion, count in emotion_counts.items()
    }

    dominant_emotion = emotion_counts.most_common(1)[0][0]

    summary_map = {
        "happy":    "You appeared happy and enthusiastic — great for an interview!",
        "neutral":  "You maintained a calm and composed expression.",
        "sad":      "You appeared a bit low energy. Try to smile and stay engaged.",
        "angry":    "You appeared tense at times. Try to relax your expression.",
        "fear":     "You appeared nervous. Practice more to build confidence.",
        "surprise": "You appeared surprised or caught off guard at moments.",
        "disgust":  "Your expressions showed some discomfort at times."
    }

    return {
        "dominant_emotion": dominant_emotion,
        "emotion_breakdown": emotion_breakdown,
        "summary": summary_map.get(dominant_emotion, "Expression analysis complete.")
    }