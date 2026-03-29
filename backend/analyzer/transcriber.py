import whisper

model = whisper.load_model("base")

def transcribe_audio(audio_path: str) -> dict:
    
    result = model.transcribe(audio_path, fp16 = False)

    return {
        "text": result["text"].strip(),
        "segments": result["segments"]        
    }