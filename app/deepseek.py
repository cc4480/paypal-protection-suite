"""DeepSeek client — the suite's one AI call path.

Every agent (WITNESS, SEATBELT, AUDITOR, RECEIPTS) talks to DeepSeek
through here, with its system prompt loaded from `app/prompts/<seat>.md`
— the grounded job descriptions from the 2026-11-08 role research, in
`~/workspace/paypal-suite/role-research/`.

Rules kept from SCOPE:
  - The AI never computes money. Agents pass figures computed by code
    (app/money.py) and the model only extracts, flags, and narrates.
  - No key, no call: `DeepSeekConfig.require_key()` is the loud gate.
    Without DEEPSEEK_API_KEY the client refuses and the routes answer
    with an honest "not configured" — never a fabricated AI result.
  - Provider-swappable by config (base URL + model in .env).
"""

from __future__ import annotations

import json
from pathlib import Path

import requests

from .config import DeepSeekConfig

PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"

# Generous for narration, short enough that a hung call fails visibly.
REQUEST_TIMEOUT_SECONDS = 60


class DeepSeekError(RuntimeError):
    """Raised when a DeepSeek call fails or returns unusable output."""


def load_prompt(seat: str) -> str:
    """Load one seat's system prompt (app/prompts/<seat>.md)."""
    path = PROMPTS_DIR / f"{seat}.md"
    if not path.exists():
        raise DeepSeekError(f"system prompt missing: {path}")
    return path.read_text(encoding="utf-8")


class DeepSeekClient:
    """Minimal chat-completions client returning parsed JSON objects."""

    def __init__(self, config: DeepSeekConfig) -> None:
        self.config = config

    def chat_json(self, seat: str, user_payload: dict) -> dict:
        """Run one agent turn: the seat's prompt + a JSON payload.

        The prompts contract a single JSON object back; anything else
        (HTTP error, non-JSON, non-object) is a loud DeepSeekError.
        """
        self.config.require_key()
        body = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": load_prompt(seat)},
                {"role": "user", "content": json.dumps(user_payload)},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
        }
        try:
            resp = requests.post(
                f"{self.config.api_base}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json",
                },
                json=body,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
        except requests.RequestException as exc:
            raise DeepSeekError(f"DeepSeek request failed: {exc}") from exc
        if resp.status_code != 200:
            raise DeepSeekError(
                f"DeepSeek HTTP {resp.status_code}: {resp.text[:200]}"
            )
        try:
            content = resp.json()["choices"][0]["message"]["content"]
            parsed = json.loads(content)
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise DeepSeekError(
                f"DeepSeek returned unusable output: {exc}"
            ) from exc
        if not isinstance(parsed, dict):
            raise DeepSeekError("DeepSeek returned a non-object JSON value")
        return parsed
