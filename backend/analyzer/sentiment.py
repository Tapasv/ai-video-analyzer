from transformers import pipeline
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)

# Maximum characters the model can handle in one chunk
MAX_CHUNK_LENGTH = 512


def chunk_text(text: str, max_length: int = MAX_CHUNK_LENGTH) -> list:
    
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        if current_length + len(word) + 1 > max_length:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_length = len(word)
        else:
            current_chunk.append(word)
            current_length += len(word) + 1

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def analyze_sentiment(text: str) -> dict:
    
    if not text or len(text.strip()) == 0:
        return {"label": "NEUTRAL", "score": 50, "summary": "No speech detected."}

    # Split transcript into chunks the model can handle
    chunks = chunk_text(text)

    # Run each chunk through the model
    results = sentiment_pipeline(chunks)

    # Count how many chunks were positive vs negative
    positive_scores = []
    negative_scores = []

    for r in results:
        if r["label"] == "POSITIVE":
            positive_scores.append(r["score"])
        else:
            negative_scores.append(r["score"])

    # Decide overall sentiment based on which side had more chunks
    if len(positive_scores) >= len(negative_scores):
        overall_label = "POSITIVE"
        avg_score = round(sum(positive_scores) / len(positive_scores) * 100, 1) if positive_scores else 50
    else:
        overall_label = "NEGATIVE"
        avg_score = round(sum(negative_scores) / len(negative_scores) * 100, 1) if negative_scores else 50

    summary_map = {
        "POSITIVE": "Your tone was confident and positive throughout the interview.",
        "NEGATIVE": "Your tone came across as uncertain or negative in some areas."
    }

    return {
        "label": overall_label,
        "score": avg_score,
        "summary": summary_map[overall_label]
    }