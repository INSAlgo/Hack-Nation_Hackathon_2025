from buzzbot.chat import ChatSession
from buzzbot.config import AppConfig
from agents import set_default_openai_key
from buzzbot.veo3 import generate_veo3_video

class PlotGenerator:
    def __init__(self, session: ChatSession = None):
        if not session:
            try:
                config = AppConfig.load()
                set_default_openai_key(config.openai_api_key)
            except RuntimeError as e:
                print(f"[error] {e}\nSet OPENAI_API_KEY and other params in environment or .env.")
                return 1
            
            self.session = ChatSession(config=config)
            self.prompt = "Give me an unique idea for a viral AI-generated video of about 8s formatted as a prompt for an AI video generation model, in two lines without any formatting, first line containing the title and second line containing the prompt, without any extra text"
        else:
            self.session = session

    def generate_plot(self) -> str:
        response = self.session.openai_client().chat.completions.create(
            model=self.session.config.model,
            messages=[{"role": "user", "content": self.prompt}],
            max_tokens=150
        )
        resp = response.choices[0].message.content
        return resp

class ClipGenerator:
    def __init__(self, session: ChatSession = None):
        if not session:
            try:
                config = AppConfig.load()
                set_default_openai_key(config.openai_api_key)
            except RuntimeError as e:
                print(f"[error] {e}\nSet OPENAI_API_KEY and other params in environment or .env.")
                return 1
            
            self.session = ChatSession(config=config)
        else:
            self.session = session
        self.plot_gen = PlotGenerator(self.session)

    def generate_clip(self) -> str:
        plot = self.plot_gen.generate_plot()

        title = plot.split('\n')[0].strip()
        prompt = plot.split('\n')[1].strip()

        out_path = generate_veo3_video(self.session, description=prompt, negative_keywords=["low quality", "bad lighting", "unrelated content"], out_dir = "data/video_tests")

        return out_path