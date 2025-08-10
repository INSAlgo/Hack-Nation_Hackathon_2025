from __future__ import annotations
from multiprocessing.util import DEBUG
import sys
import os
import random
from typing import List, Dict, Optional, Callable, Any, cast

from .config import AppConfig
from .io_utils import print_message, format_prefix

Message = Dict[str, Any]

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None  # type: ignore

# ---------------------------------------------------------------------------
# Tool (function) implementations
# ---------------------------------------------------------------------------

def get_random_D6_dice_value() -> int:
    """
    Just a simple function to simulate rolling a D6 die.
    Used to demonstrate tool calls in the chat session.
    """
    debug: str | bool = os.environ.get("DEBUG", False)
    if debug and debug != "0":
        print("[debug] Rolling a D6...")
    return random.randint(1, 6)


class ChatSession:
    def __init__(self, config: AppConfig, history: Optional[List[Message]] = None):
        self.config = config
        self.history: List[Message] = history or []
        if config.system_prompt and not any(m.get("role") == "system" for m in self.history):
            self.history.insert(0, {"role": "system", "content": config.system_prompt})
        self._client = None

    def client(self):
        if self._client is None:
            if OpenAI is None:
                raise RuntimeError("openai library not installed. Run: pip install openai")
            self._client = OpenAI(api_key=self.config.openai_api_key, base_url=self.config.base_url)
        return self._client

    def switch_model(self, new_model: str):
        self.config.switch_model(new_model)

    # Tool specs for OpenAI (JSON schema w/out params) -----------------------
    def _tool_specs(self):
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_random_D6_dice_value",
                    "description": "Return a random integer between 1 and 6 inclusive (simulate rolling a D6)",
                    "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
                },
            }
        ]

    def _tool_dispatch(self, name: str, arguments: str) -> str:
        funcs: Dict[str, Callable[[], Any]] = {
            "get_random_D6_dice_value": get_random_D6_dice_value,
        }
        fn = funcs.get(name)
        if not fn:
            return f"<error: unknown function {name}>"
        try:
            return str(fn())
        except Exception as e:  # pragma: no cover
            return f"<error executing {name}: {e}>"

    def _convert_history(self) -> List[Dict[str, Any]]:
        converted: List[Dict[str, Any]] = []
        for m in self.history:
            role = m.get("role")
            if role == "tool":
                converted.append({
                    "role": "tool",
                    "content": m.get("content", ""),
                    "tool_call_id": m.get("tool_call_id"),
                })
            elif role == "assistant" and m.get("tool_calls"):
                # Preserve tool_calls structure
                converted.append({
                    "role": "assistant",
                    "content": m.get("content", ""),
                    "tool_calls": m.get("tool_calls"),
                })
            else:
                converted.append({"role": role, "content": m.get("content", "")})
        return converted

    # Core completion with tool loop; final response prints (streamless for tool phase)
    def complete(self, user_content: str) -> Message:
        user_msg: Message = {"role": "user", "content": user_content}
        self.history.append(user_msg)
        client = self.client()
        tools = self._tool_specs()

        # Tool-call loop (non-streaming to inspect tool_calls)
        while True:
            try:
                msgs = self._convert_history()
                resp = client.chat.completions.create(  # type: ignore[arg-type]
                    model=self.config.model,
                    messages=msgs,  # type: ignore[arg-type]
                    tools=tools,  # type: ignore[arg-type]
                    tool_choice="auto",
                )
            except Exception as e:
                print(f"[warn] Tool-call phase failed ({e}); falling back to simple completion.", file=sys.stderr)
                return self._fallback_completion(client)

            choice = resp.choices[0]
            msg = choice.message
            if msg.tool_calls:
                # Append the assistant tool-call message FIRST per API requirements
                assistant_call_msg: Message = {
                    "role": "assistant",
                    "content": msg.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": getattr(tc.function, "name", ""),
                                "arguments": getattr(tc.function, "arguments", ""),
                            },
                        }
                        for tc in msg.tool_calls
                        if getattr(tc, "type", None) == "function"
                    ],
                }
                self.history.append(assistant_call_msg)

                # Now execute each function tool call and append tool messages
                for tc in msg.tool_calls:
                    fn_obj = getattr(tc, "function", None)
                    if fn_obj and getattr(tc, "type", None) == "function":
                        fn_name = getattr(fn_obj, "name", "<unknown>")
                        fn_args = getattr(fn_obj, "arguments", "{}")
                        result = self._tool_dispatch(fn_name, fn_args)  # type: ignore[arg-type]
                        self.history.append({
                            "role": "tool",
                            "tool_call_id": getattr(tc, "id", None),
                            "name": fn_name,
                            "content": result,
                        })
                # Loop again so model can use tool outputs
                continue
            assistant_msg: Message = {"role": "assistant", "content": msg.content or ""}
            self.history.append(assistant_msg)
            print_message(assistant_msg, self.config.color)
            return assistant_msg

    # Fallback simple non-streaming
    def _fallback_completion(self, client) -> Message:
        assistant_msg: Message = {"role": "assistant", "content": ""}
        try:
            resp = client.chat.completions.create(  # type: ignore[arg-type]
                model=self.config.model,
                messages=self._convert_history(),  # type: ignore[arg-type]
            )
            assistant_msg["content"] = resp.choices[0].message.content
            self.history.append(assistant_msg)
            print_message(assistant_msg, self.config.color)
            return assistant_msg
        except Exception as e:
            print(f"[error] Request failed: {e}", file=sys.stderr)
            assistant_msg["content"] = f"<error: {e}>"
            self.history.append(assistant_msg)
            return assistant_msg

