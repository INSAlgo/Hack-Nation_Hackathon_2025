from buzzbot.buzzcli import parse_args, repl, run_hello_test, repl_multiline
from buzzbot.config import AppConfig

import time
from google import genai
from google.genai import types


# Parse command line arguments
args = parse_args()

# Load configuration from environment or .env file
try:
    config = AppConfig.load()
except RuntimeError as e:
    print(f"[error] {e}\nSet OPENAI_API_KEY and other params in environment or .env.")
    exit(1)
if args.no_color:
    config.color = False
if args.system:
    config.system_prompt = args.system

client = genai.Client(api_key=config.google_api_key)

def first_gemini_test_message():
    """Send a test message to Gemini and print the response."""
    print("Running Gemini test...")
    response = client.models.generate_content(
    model="gemini-2.5-flash", contents="Explain how AI works in a few words"
    )
    print(response.text)

def first_gemini_video_test():
    prompt = """A bird's eye view of flying islands and mountains on a sea of clouds. 
    A winged spaceship-like boat is flying over the clouds with its foils extending into
    the clouds and making a trail of broken clouds. Other small flying creatures pass by gracefully as small
    silhouettes. The scene is serene and peaceful."""

    operation = client.models.generate_videos(
        model="veo-3.0-generate-preview",
        prompt=prompt,
        config=types.GenerateVideosConfig(negative_prompt="painting, anime, colorful, keyframe, 3D"),
    )

    # Poll the operation status until the video is ready.
    while not operation.done:
        print("Waiting for video generation to complete...")
        time.sleep(10)
        operation = client.operations.get(operation)

    # Download the generated video.
    generated_video = operation.response.generated_videos[0]
    client.files.download(file=generated_video.video)
    generated_video.video.save("data/video_tests/flying_mountains.mp4")
    print("Generated video saved to data/video_tests/flying_mountains.mp4")

first_gemini_video_test()
