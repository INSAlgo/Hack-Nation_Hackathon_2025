from tiktok_uploader.upload import upload_video
from tiktok_uploader.auth import AuthBackend

from pathlib import Path

class TikTokPublisher:
    def __init__(self, cookies_path: str = 'env/cookies.txt'):
        self.cookies_path = cookies_path

        # Load the content of the cookies file
        if not Path(cookies_path).exists():
            raise FileNotFoundError(f"Cookies file not found: {cookies_path}")
        with open(cookies_path, 'r') as f:
            self.cookies_content = f.read()

        self.auth_backend = AuthBackend(cookies = cookies_path)

    def publish_video(self, video_path: str, desc: str):
        failed_videos = upload_video(
            video_path,
            description=desc,
            cookies=self.cookies_path,
            headless=True
        )
        if failed_videos:
            print(f"Failed to upload videos: {failed_videos}")
        else:
            print("Video uploaded successfully.")