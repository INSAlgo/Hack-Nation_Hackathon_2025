from __future__ import annotations
import sys
import time
from typing import List, Dict, Iterable, Optional

from .config import AppConfig
from .io_utils import print_message, format_prefix

Message = Dict[str, str]

try:
    from openai import OpenAI  # hypothetical main client
except ImportError:  # pragma: no cover - library missing
    OpenAI = None  # type: ignore

# from openai import OpenAI
# client = OpenAI()

# Extensibility: Could abstract a Provider interface if adding non-OpenAI later.

class ChatSession:
    def __init__(self, config: AppConfig, history: Optional[List[Message]] = None):
        self.config = config
        self.history: List[Message] = history or []
        if config.system_prompt and not any(m["role"] == "system" for m in self.history):
            self.history.insert(0, {"role": "system", "content": config.system_prompt})
        self._client = None

    def client(self):
        if self._client is None:
            if OpenAI is None:
                raise RuntimeError("openai-agents library not installed. Did you run pip install -r requirements.txt?")
            # openai-agents style - adapt if actual API differs
            self._client = OpenAI(api_key=self.config.api_key, base_url=self.config.base_url)
        return self._client

    def switch_model(self, new_model: str):
        self.config.switch_model(new_model)

    # Streaming chat completion
    def complete(self, user_content: str) -> Message:
        user_msg: Message = {"role": "user", "content": user_content}
        self.history.append(user_msg)
        assistant_msg: Message = {"role": "assistant", "content": ""}

        # Attempt streaming first
        try:
            client = self.client()
            # The specific API might differ. We'll assume openai-agents exposes a similar interface
            # to openai's python client with client.chat.completions.create(stream=True, ...)
            stream = None
            try:
                stream = client.chat.completions.create(
                    model=self.config.model,
                    messages=self.history,
                    stream=True,
                )
            except TypeError:
                # Fallback: maybe method signature differs; attempt without stream
                stream = None

            if stream is not None:
                prefix_printed = False
                for chunk in stream:
                    # Each chunk expected to have choices[0].delta.content similar to OpenAI
                    delta = getattr(chunk.choices[0], "delta", None) if chunk.choices else None
                    token = getattr(delta, "content", None) if delta else None
                    if token:
                        if not prefix_printed:
                            sys.stdout.write(format_prefix("assistant", self.config.color) + " ")
                            prefix_printed = True
                        sys.stdout.write(token)
                        sys.stdout.flush()
                        assistant_msg["content"] += token
                if prefix_printed:
                    sys.stdout.write("\n")
                self.history.append(assistant_msg)
                return assistant_msg
        except Exception as e:  # streaming failed, fallback
            print(f"[warn] Streaming failed ({e}); falling back to non-streaming.", file=sys.stderr)

        # Non-streaming fallback
        try:
            client = self.client()
            resp = client.chat.completions.create(
                model=self.config.model,
                messages=self.history,
                stream=False,
            )
            content = resp.choices[0].message.content  # aligns with OpenAI style
            assistant_msg["content"] = content
            self.history.append(assistant_msg)
            print_message(assistant_msg, self.config.color)
            return assistant_msg
        except Exception as e:
            print(f"[error] Request failed: {e}", file=sys.stderr)
            assistant_msg["content"] = f"<error: {e}>"
            self.history.append(assistant_msg)
            return assistant_msg

