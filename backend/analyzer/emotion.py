import cv2
import numpy as np
from hsemotion_onnx.facial_emotions import HSEmotionRecognizer
from collections import Counter

# Load the emotion recognizer once at startup
# model_name="enet_b0_8_best_afew" is a lightweight model — fast and accurate enough
recognizer = HSEmotionRecognizer(model_name="enet_b0_8_best_afew")

# OpenCV's built-in face detector — no extra downloads needed
# This XML file comes bundled with opencv-python-headless
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)


def analyze_emotion(video_path: str) -> dict:
    """
    Opens the video file, samples one frame every 2 seconds,
    detects the face in each frame, runs emotion recognition,
    and returns the dominant emotion plus a full breakdown.
    """

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Analyze one frame every 2 seconds to keep things fast
    frame_interval = max(1, int(fps * 2))

    all_emotions = []
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            try:
                # Convert to grayscale for face detection
                # Face detection works better on grayscale images
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # Detect faces in the frame
                # scaleFactor=1.1 means scan at multiple scales
                # minNeighbors=5 means a face must be confirmed 5 times to count
                faces = face_cascade.detectMultiScale(
                    gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
                )

                if len(faces) > 0:
                    # Take the first (largest) face found
                    x, y, w, h = faces[0]

                    # Crop just the face region from the frame
                    face_img = frame[y:y+h, x:x+w]

                    # Convert BGR (OpenCV format) to RGB (what hsemotion expects)
                    face_rgb = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)

                    # Run emotion recognition on the cropped face
                    # Returns the emotion label e.g. "Happy", "Neutral", "Fear"
                    emotion, _ = recognizer.predict_emotions(face_rgb, logits=False)

                    # Normalize to lowercase for consistency
                    all_emotions.append(emotion.lower())

            except Exception:
                pass

        frame_count += 1

    cap.release()

    if not all_emotions:
        return {
            "dominant_emotion": "neutral",
            "emotion_breakdown": {"neutral": 100},
            "summary": "Could not detect facial emotions clearly. Make sure your face is visible."
        }

    # Count occurrences of each emotion across all sampled frames
    emotion_counts = Counter(all_emotions)
    total = len(all_emotions)

    # Convert counts to percentages
    emotion_breakdown = {
        emotion: round((count / total) * 100, 1)
        for emotion, count in emotion_counts.items()
    }

    dominant_emotion = emotion_counts.most_common(1)[0][0]

    summary_map = {
        "happy":    "You appeared happy and enthusiastic — great for an interview!",
        "neutral":  "You maintained a calm and composed expression.",
        "sad":      "You appeared a bit sad or low energy. Try to smile more.",
        "angry":    "You appeared tense or frustrated at times. Try to relax.",
        "fear":     "You appeared nervous. Practice more to build confidence.",
        "surprise": "You appeared surprised or caught off guard at moments.",
        "disgust":  "Your expressions showed discomfort at times."
    }

    return {
        "dominant_emotion": dominant_emotion,
        "emotion_breakdown": emotion_breakdown,
        "summary": summary_map.get(dominant_emotion, "Expression analysis complete.")
    }