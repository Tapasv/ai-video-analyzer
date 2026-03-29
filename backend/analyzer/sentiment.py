# No external API needed — we use a keyword-based sentiment analyzer
# This is fast, lightweight, works offline, and uses zero RAM
# It's accurate enough for interview tone analysis

POSITIVE_WORDS = [
    "good", "great", "excellent", "amazing", "wonderful", "fantastic",
    "happy", "excited", "confident", "strong", "passionate", "love",
    "enjoy", "best", "success", "achieve", "accomplish", "improve",
    "opportunity", "motivated", "dedicated", "proud", "positive",
    "effective", "efficient", "creative", "innovative", "skilled",
    "experienced", "capable", "eager", "enthusiastic", "reliable",
    "responsible", "honest", "committed", "determined", "focused",
    "collaborative", "teamwork", "leadership", "growth", "learn",
    "developed", "built", "created", "solved", "delivered", "managed",
    "led", "helped", "supported", "worked", "definitely", "absolutely",
    "certainly", "always", "ready", "prepared", "looking forward"
]

NEGATIVE_WORDS = [
    "bad", "terrible", "awful", "horrible", "poor", "weak", "fail",
    "failed", "failure", "mistake", "wrong", "difficult", "hard",
    "struggle", "problem", "issue", "never", "can't", "cannot",
    "don't", "not", "no", "nothing", "nobody", "nowhere", "hate",
    "dislike", "boring", "confused", "unsure", "uncertain", "nervous",
    "anxious", "worried", "scared", "fear", "doubt", "maybe", "perhaps",
    "unfortunately", "sadly", "regret", "sorry", "quit", "left",
    "fired", "laid off", "conflict", "stress", "pressure", "overwhelmed"
]

# Intensifier words that boost the score of the next word
INTENSIFIERS = ["very", "really", "extremely", "absolutely", "totally", "so"]


def analyze_sentiment(text: str) -> dict:
    """
    Analyzes the sentiment of interview transcript text using
    keyword matching. Fast, offline, zero dependencies.

    Returns label (POSITIVE/NEGATIVE), score (0-100), and summary.
    """

    if not text or len(text.strip()) == 0:
        return {"label": "NEUTRAL", "score": 50, "summary": "No speech detected."}

    words = text.lower().split()
    positive_count = 0
    negative_count = 0
    boost = 1.0  # multiplier when an intensifier was the previous word

    for i, word in enumerate(words):
        # Strip punctuation from word for clean matching
        clean_word = word.strip(".,!?;:\"'()")

        # Check if previous word was an intensifier — if so boost score
        if i > 0 and words[i-1].strip(".,!?;:\"'()") in INTENSIFIERS:
            boost = 1.5
        else:
            boost = 1.0

        if clean_word in POSITIVE_WORDS:
            positive_count += boost
        elif clean_word in NEGATIVE_WORDS:
            negative_count += boost

    total = positive_count + negative_count

    # If no sentiment words found at all, return neutral
    if total == 0:
        return {
            "label":   "POSITIVE",
            "score":   60,
            "summary": "Your tone was generally neutral and professional."
        }

    # Calculate what percentage of sentiment words were positive
    positive_ratio = positive_count / total

    if positive_ratio >= 0.5:
        overall_label = "POSITIVE"
        # Scale score between 55 and 95 based on ratio
        score = round(55 + (positive_ratio - 0.5) * 80)
        score = min(95, score)
    else:
        overall_label = "NEGATIVE"
        negative_ratio = negative_count / total
        # Scale score between 30 and 55 based on ratio
        score = round(55 - (negative_ratio - 0.5) * 80)
        score = max(20, score)

    summary_map = {
        "POSITIVE": "Your tone was confident and positive throughout the interview.",
        "NEGATIVE": "Your tone came across as uncertain or negative in some areas."
    }

    return {
        "label":   overall_label,
        "score":   score,
        "summary": summary_map[overall_label]
    }