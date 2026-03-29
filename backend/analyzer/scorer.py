def compute_score(sentiment: dict, emotion: dict, clarity: dict) -> dict:
    """
    Takes results from sentiment, emotion, and clarity analyzers.
    Computes a final interview score out of 100.
    Each category has a weight:
      - Sentiment (tone):  30%
      - Emotion (face):    30%
      - Clarity (speech):  40%
    Returns a score breakdown and overall grade.
    """

    # ── SENTIMENT SCORE (0–100) ──────────────────────────────────────
    # If positive sentiment, use the confidence score directly
    # If negative, flip it (100 - score) so negativity reduces the score
    if sentiment["label"] == "POSITIVE":
        sentiment_score = sentiment["score"]
    else:
        sentiment_score = 100 - sentiment["score"]

    # ── EMOTION SCORE (0–100) ────────────────────────────────────────
    # Map each dominant emotion to a score representing how well it
    # comes across in an interview context
    emotion_score_map = {
        "happy":    90,
        "neutral":  75,
        "surprise": 60,
        "sad":      40,
        "fear":     35,
        "angry":    25,
        "disgust":  20
    }
    dominant = emotion.get("dominant_emotion", "neutral")
    emotion_score = emotion_score_map.get(dominant, 70)

    # ── CLARITY SCORE (0–100) ────────────────────────────────────────
    clarity_score = 100

    # Deduct points for filler words
    total_fillers = clarity.get("total_fillers", 0)
    if total_fillers <= 2:
        filler_deduction = 0
    elif total_fillers <= 5:
        filler_deduction = 10
    elif total_fillers <= 10:
        filler_deduction = 20
    else:
        filler_deduction = 30

    # Deduct points for long pauses
    long_pauses = clarity.get("long_pauses", 0)
    if long_pauses <= 1:
        pause_deduction = 0
    elif long_pauses <= 3:
        pause_deduction = 10
    else:
        pause_deduction = 20

    # Deduct points for bad speaking pace
    wpm = clarity.get("words_per_minute", 130)
    if 110 <= wpm <= 170:
        pace_deduction = 0       # Ideal range
    elif 90 <= wpm < 110 or 170 < wpm <= 190:
        pace_deduction = 10      # Slightly off
    else:
        pace_deduction = 20      # Too fast or too slow

    clarity_score = max(0, clarity_score - filler_deduction - pause_deduction - pace_deduction)

    # ── FINAL WEIGHTED SCORE ─────────────────────────────────────────
    final_score = round(
        (sentiment_score * 0.30) +
        (emotion_score   * 0.30) +
        (clarity_score   * 0.40)
    )

    # ── GRADE ────────────────────────────────────────────────────────
    if final_score >= 85:
        grade = "A"
        grade_label = "Excellent"
        overall_feedback = "Outstanding performance! You're interview-ready."
    elif final_score >= 70:
        grade = "B"
        grade_label = "Good"
        overall_feedback = "Good job! A little more practice and you'll be great."
    elif final_score >= 55:
        grade = "C"
        grade_label = "Average"
        overall_feedback = "Decent effort. Focus on clarity and reducing filler words."
    elif final_score >= 40:
        grade = "D"
        grade_label = "Needs Work"
        overall_feedback = "Needs improvement. Practice speaking confidently and clearly."
    else:
        grade = "F"
        grade_label = "Poor"
        overall_feedback = "Significant practice needed. Focus on tone, expression, and speech."

    return {
        "final_score": final_score,
        "grade": grade,
        "grade_label": grade_label,
        "overall_feedback": overall_feedback,
        "breakdown": {
            "sentiment_score": round(sentiment_score),
            "emotion_score": round(emotion_score),
            "clarity_score": round(clarity_score)
        }
    }