"""Configuration loading.

Reads settings from the process environment, first loading a local `.env`
file if one exists (a tiny built-in parser — no dependency, and `.env` is
gitignored; see SCOPE §6 risk 7 / §7 item 1).

Fails loud: constructing the PayPal client config without the sandbox
credentials raises ConfigError naming the missing keys. The Flask app
itself boots without credentials (Slice 0 acceptance: the shell renders),
but it reports itself NOT READY, and any live PayPal call refuses to run.
"""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_API_BASE = "https://api-m3.sandbox.paypal.com"

# Keys the PayPal client cannot run without.
REQUIRED_PAYPAL_KEYS = ("PAYPAL_CLIENT_ID", "PAYPAL_CLIENT_SECRET")


class ConfigError(RuntimeError):
    """Raised when required configuration is missing or malformed."""


def load_dotenv(path: Path | None = None) -> None:
    """Load KEY=VALUE lines from `.env` into os.environ (no override)."""
    env_path = path or (PROJECT_ROOT / ".env")
    if not env_path.exists():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


class PayPalConfig:
    """Sandbox API settings. `require_credentials()` is the loud gate."""

    def __init__(self, environ: dict | None = None) -> None:
        env = environ if environ is not None else os.environ
        self.client_id = env.get("PAYPAL_CLIENT_ID", "").strip()
        self.client_secret = env.get("PAYPAL_CLIENT_SECRET", "").strip()
        self.api_base = (
            env.get("PAYPAL_API_BASE", "").strip() or DEFAULT_API_BASE
        ).rstrip("/")
        self.business_email = env.get("PAYPAL_BUSINESS_EMAIL", "").strip()
        self.personal_email = env.get("PAYPAL_PERSONAL_EMAIL", "").strip()

    @property
    def missing_keys(self) -> list[str]:
        values = {
            "PAYPAL_CLIENT_ID": self.client_id,
            "PAYPAL_CLIENT_SECRET": self.client_secret,
        }
        return [k for k in REQUIRED_PAYPAL_KEYS if not values.get(k)]

    @property
    def has_credentials(self) -> bool:
        return not self.missing_keys

    def require_credentials(self) -> None:
        missing = self.missing_keys
        if missing:
            raise ConfigError(
                "Missing required .env keys: "
                + ", ".join(missing)
                + ". Seat the sandbox app Client ID + Secret in "
                + str(PROJECT_ROOT / ".env")
                + " (see .env.example). Refusing to make any PayPal call."
            )


DEFAULT_DEEPSEEK_BASE = "https://api.deepseek.com"
# SCOPE: DeepSeek Flash is the default AI model, swappable by config.
DEFAULT_DEEPSEEK_MODEL = "deepseek-chat"


class DeepSeekConfig:
    """DeepSeek AI settings (SCOPE: provider-swappable by config).

    Same loud-gate shape as PayPalConfig: the app boots without a key,
    reports itself not ready for AI work, and any agent call refuses to
    run until Carlos seats DEEPSEEK_API_KEY in `.env` himself.
    """

    def __init__(self, environ: dict | None = None) -> None:
        env = environ if environ is not None else os.environ
        self.api_key = env.get("DEEPSEEK_API_KEY", "").strip()
        self.api_base = (
            env.get("DEEPSEEK_API_BASE", "").strip() or DEFAULT_DEEPSEEK_BASE
        ).rstrip("/")
        self.model = (
            env.get("DEEPSEEK_MODEL", "").strip() or DEFAULT_DEEPSEEK_MODEL
        )

    @property
    def has_key(self) -> bool:
        return bool(self.api_key)

    def require_key(self) -> None:
        if not self.api_key:
            raise ConfigError(
                "Missing required .env key: DEEPSEEK_API_KEY. Seat the "
                "DeepSeek API key in "
                + str(PROJECT_ROOT / ".env")
                + " yourself (never paste it into chat). Refusing to "
                "make any AI call."
            )


class AppConfig:
    """Flask app settings."""

    def __init__(self, environ: dict | None = None) -> None:
        env = environ if environ is not None else os.environ
        self.secret_key = env.get("FLASK_SECRET_KEY", "dev-only-not-secret")
        self.database_path = Path(
            env.get("SUITE_DB_PATH", str(PROJECT_ROOT / "suite.db"))
        )
        self.paypal = PayPalConfig(environ)
        self.deepseek = DeepSeekConfig(environ)
