import random
import datetime
import time
from pathlib import Path
from typing import List
import os

try:
    from google import genai
    from google.genai import types
except ImportError:  # pragma: no cover
    genai = None  # type: ignore
    types = None  # type: ignore

# Determine project root (../.. from this file: buzzbot/ -> src/ -> repo root)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
VIDEO_DIR = Path(os.getenv("BUZZBOT_VIDEO_DIR", PROJECT_ROOT / "data" / "video_tests")).resolve()
VIDEO_DIR.mkdir(parents=True, exist_ok=True)

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

MAX_VEO3_QUERIES = 10
NB_VEO3_QUERIES = 0

PUBLIC_VIDEO_ROUTE_PREFIX = "/videos"  # where Flask will serve from
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL")


def generate_veo3_video(client, description: str, negative_keywords: List[str], out_dir: str = str(VIDEO_DIR)) -> str:
    """Generate a video with Google's Veo3 model and return a public route.
    Saves files under VIDEO_DIR so webserver can serve them.
    """
    if genai is None:
        return "<error: google-genai not installed>"
    global NB_VEO3_QUERIES
    NB_VEO3_QUERIES += 1
    if NB_VEO3_QUERIES > MAX_VEO3_QUERIES:
        return "<error: too many Veo3 queries, please try again later (increase limit)>"

    negative_prompt = ", ".join(negative_keywords) if negative_keywords else ""
    cfg = None
    if types is not None:
        try:
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

    attempts = 0
    while not getattr(operation, 'done', True) and attempts < 60:
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

    filename = generate_timestamped_random_filename(prefix="veo3", extension="mp4")
    out_path = VIDEO_DIR / filename
    try:
        client.files.download(file=generated_video.video)
        generated_video.video.save(str(out_path))
    except Exception as e:  # pragma: no cover
        return f"<error: failed to save video: {e}>"

    # Debug note for logs
    print(f"[info] Saved Veo3 video to {out_path} (public {PUBLIC_VIDEO_ROUTE_PREFIX}/{filename})")
    # Build absolute URL if PUBLIC_BASE_URL provided
    if PUBLIC_BASE_URL:
        return f"{PUBLIC_BASE_URL.rstrip('/')}{PUBLIC_VIDEO_ROUTE_PREFIX}/{filename}"
    return f"{PUBLIC_VIDEO_ROUTE_PREFIX}/{filename}"

