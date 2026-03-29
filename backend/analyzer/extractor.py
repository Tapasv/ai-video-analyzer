import tempfile
from moviepy.editor import VideoFileClip

def extract_audio_from_video(video_path: str) -> str:
    
    temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    audio_path = temp_audio.name
    temp_audio.close
    
    video = VideoFileClip(video_path)

    audio = video.audio
    
    audio.write_audiofile(
        audio_path,
        fps=16000,
        nbytes=2,
        ffmpeg_params=["-ac", "1"],
        logger=None
    )

    video.close()

    return audio_path