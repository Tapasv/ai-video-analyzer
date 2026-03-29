import re


# List of filler words commonly used when someone is nervous or unprepared
FILLER_WORDS = [
    "um", "uh", "like", "you know", "basically", "literally",
    "actually", "so", "right", "i mean", "kind of", "sort of",
    "you see", "well", "okay", "hmm"
]


def analyze_clarity(transcript: dict) -> dict:
    """
    Takes the transcript dictionary (with text and segments).
    Analyzes:
      1. Words per minute (speaking pace)
      2. Filler word count and which ones were used
      3. Number of long pauses
    Returns a dictionary with all these metrics and a summary.
    """

    text = transcript.get("text", "")
    segments = transcript.get("segments", [])

    # ── 1. WORDS PER MINUTE ──────────────────────────────────────────
    words = text.split()
    word_count = len(words)

    # Calculate total speaking duration from the segments
    # segments are like: [{start: 0.0, end: 3.5, text: "Hello my name is..."}]
    if segments:
        total_duration_seconds = segments[-1]["end"] - segments[0]["start"]
    else:
        total_duration_seconds = 0

    if total_duration_seconds > 0:
        words_per_minute = round((word_count / total_duration_seconds) * 60)
    else:
        words_per_minute = 0

    # Ideal speaking pace for an interview is 120–160 WPM
    if words_per_minute < 100:
        pace_feedback = "You spoke too slowly. Try to speak a bit faster and more energetically."
    elif words_per_minute > 180:
        pace_feedback = "You spoke too fast. Slow down so interviewers can follow along."
    else:
        pace_feedback = "Your speaking pace was ideal for an interview."

    # ── 2. FILLER WORDS ──────────────────────────────────────────────
    text_lower = text.lower()
    filler_found = {}

    for filler in FILLER_WORDS:
        # Use regex to find exact word matches (not parts of other words)
        # e.g. "so" should not match "society"
        pattern = r'\b' + re.escape(filler) + r'\b'
        matches = re.findall(pattern, text_lower)
        if matches:
            filler_found[filler] = len(matches)

    total_fillers = sum(filler_found.values())

    if total_fillers == 0:
        filler_feedback = "Excellent! No filler words detected."
    elif total_fillers <= 5:
        filler_feedback = f"You used {total_fillers} filler word(s). Minor — but try to reduce them."
    else:
        filler_feedback = f"You used {total_fillers} filler words. Practice speaking without them."

    # ── 3. PAUSES ────────────────────────────────────────────────────
    long_pauses = 0

    # Look at the gap between consecutive segments
    # If the gap is more than 2 seconds, it's a long pause
    for i in range(1, len(segments)):
        gap = segments[i]["start"] - segments[i - 1]["end"]
        if gap > 2.0:
            long_pauses += 1

    if long_pauses == 0:
        pause_feedback = "Great flow! No long pauses detected."
    elif long_pauses <= 3:
        pause_feedback = f"{long_pauses} pause(s) detected. Acceptable, but try to maintain flow."
    else:
        pause_feedback = f"{long_pauses} long pauses detected. Work on keeping momentum."

    return {
        "words_per_minute": words_per_minute,
        "word_count": word_count,
        "pace_feedback": pace_feedback,
        "filler_words": filler_found,
        "total_fillers": total_fillers,
        "filler_feedback": filler_feedback,
        "long_pauses": long_pauses,
        "pause_feedback": pause_feedback
    }