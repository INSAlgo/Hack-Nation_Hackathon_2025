import random
import datetime
import time
from pathlib import Path
from typing import List

try:
    from google import genai
    from google.genai import types
except ImportError:  # pragma: no cover
    genai = None  # type: ignore
    types = None  # type: ignore

def generate_random_hash_of_length(length: int) -> str:
    """Generate a random hash of specified length."""
    if length <= 0:
        raise ValueError("Length must be a positive integer.")
    return ''.join(random.choices('0123456789abcdef', k=length))

def generate_timestamped_random_filename(prefix: str = "video", extension: str = "mp4") -> str:
    """Generate a timestamped random filename."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
    random_hash = generate_random_hash_of_length(8)
    return f"{prefix}_{random_hash}_{timestamp}.{extension}"

# New helper for Veo3 video generation ---------------------------------------

def generate_veo3_video(client, description: str, negative_keywords: List[str], out_dir: str = "data/video_tests") -> str:
    """Generate a video with Google's Veo3 (preview) model.

    Args:
        client: An instantiated genai.Client
        description: The textual prompt / description.
        negative_keywords: List of keywords to discourage (joined into negative_prompt).
        out_dir: Directory to save the resulting mp4.
    Returns:
        Path to saved video file (string). On error returns a string starting with '<error'.
    """
    if genai is None:
        return "<error: google-genai not installed>"
    
    return "https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4" # TODO - Template video to avoid using all of our credits
    
    negative_prompt = ", ".join(negative_keywords) if negative_keywords else ""
    cfg = None
    if types is not None:
        try:
            # Some SDK versions may not have negative_prompt; ignore if invalid
            cfg = types.GenerateVideosConfig()  # type: ignore[call-arg]
        except Exception:
            cfg = None
    try:
        operation = client.models.generate_videos(
            model="veo-3.0-generate-preview",
            prompt=description,
            config=cfg,
        )
    except Exception as e:  # pragma: no cover
        return f"<error: failed to start video generation: {e}>"

    # Poll (bounded attempts)
    attempts = 0
    while not getattr(operation, 'done', True) and attempts < 60:  # up to ~10 min at 10s interval
        time.sleep(10)
        attempts += 1
        try:
            operation = client.operations.get(operation)
        except Exception as e:  # pragma: no cover
            return f"<error: polling failed: {e}>"

    if not getattr(operation, 'done', False):
        return "<error: timeout waiting for video>"
    try:
        generated_video = operation.response.generated_videos[0]
    except Exception as e:
        return f"<error: no video in response: {e}>"

    Path(out_dir).mkdir(parents=True, exist_ok=True)
    filename = generate_timestamped_random_filename(prefix="veo3", extension="mp4")
    out_path = Path(out_dir) / filename
    try:
        client.files.download(file=generated_video.video)
        generated_video.video.save(str(out_path))
    except Exception as e:  # pragma: no cover
        return f"<error: failed to save video: {e}>"
    return str(out_path)

