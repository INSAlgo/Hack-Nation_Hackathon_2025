"""Simple smoke tests for BuzzBot CLI components.
Run with: python tests_smoke.py
"""
from pathlib import Path
import json

from buzzbot_cli.io_utils import save_history, load_history
from buzzbot_cli.config import AppConfig
from buzzbot_cli.chat import ChatSession

class DummyClient:
    class _Choices(list):
        pass
    class _Delta:
        def __init__(self, content):
            self.content = content
    class _Chunk:
        def __init__(self, token):
            self.choices = [type('X', (), {'delta': type('Y', (), {'content': token})})()]
    class _Resp:
        def __init__(self, full):
            self.choices = [type('M', (), {'message': type('MM', (), {'content': full})()})()]

    def __init__(self, tokens):
        self.tokens = tokens
    class chat:
        class completions:
            @staticmethod
            def create(model, messages, stream=False):
                # very small emulator
                if stream:
                    for t in ["Hello", " world"]:
                        yield DummyClient._Chunk(t)
                else:
                    return DummyClient._Resp("Hello world")


def test_jsonl_roundtrip():
    history = [
        {"role": "user", "content": "Hi"},
        {"role": "assistant", "content": "Hello"},
    ]
    path = save_history(history)
    loaded = load_history(path)
    assert history == loaded, "Roundtrip mismatch"
    print("JSONL roundtrip OK")


def test_chat_mock_stream():
    cfg = AppConfig(api_key="DUMMY", base_url="http://example", model="test")
    session = ChatSession(config=cfg)
    # inject dummy client
    session._client = DummyClient(tokens=["Hello", " world"])
    msg = session.complete("Say hi")
    assert "Hello" in msg["content"], "Expected assistant reply"
    print("Chat streaming mock OK")


if __name__ == "__main__":
    test_jsonl_roundtrip()
    test_chat_mock_stream()
    print("All smoke tests passed.")
