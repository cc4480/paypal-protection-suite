"""Flask routes — the UI shell plus status/receipts APIs.

The landing page (templates/landing.html) is the front door at / —
hero, carousel, and a plain-words explanation of what the suite does;
it links into the shell at /app. The shell (templates/shell.html) is
the click-through frame for the three agents. It renders before any credential exists; /api/status
states plainly that live checks are NOT READY until credentials are
seated, and anything the shell previews with fixture data is stamped
SIMULATED.

The agent endpoints live in app/agent_routes.py (WITNESS, SEATBELT,
AUDITOR, receipt explainer) — including the live PayPal wiring, which
degrades honestly when credentials are absent: UNVERIFIED verdicts,
labeled sample figures, plain 503s. Nothing fabricated, ever.
"""

from __future__ import annotations

import json
import sqlite3

from flask import Flask, jsonify, render_template

from .agent_routes import bp as agent_bp
from .auditor_routes import bp as auditor_bp
from .config import AppConfig, load_dotenv
from .db import init_db


def create_app(config: AppConfig | None = None) -> Flask:
    load_dotenv()
    cfg = config or AppConfig()
    init_db(cfg.database_path)
    app = Flask(__name__)
    app.secret_key = cfg.secret_key
    app.config["SUITE"] = cfg
    app.register_blueprint(agent_bp)
    app.register_blueprint(auditor_bp)

    @app.get("/")
    def index():
        return render_template("landing.html")

    @app.get("/app")
    def shell():
        return render_template("shell.html")

    @app.get("/video")
    def video():
        # The demo-video composition: a self-contained Framer Motion
        # build (source in ~/workspace/paypal-video) that plays the
        # seven scripted scenes from VIDEO-SCRIPT.md, timed to the VO.
        return app.send_static_file("video.html")

    @app.get("/api/status")
    def status():
        pp = cfg.paypal
        ready = pp.has_credentials
        return jsonify(
            ready=ready,
            account_mode="live" if ready else "demo",
            message=(
                "sandbox credentials present"
                if ready
                else "missing .env keys: " + ", ".join(pp.missing_keys)
            ),
            api_base=pp.api_base,
            deepseek={
                "ready": cfg.deepseek.has_key,
                "model": cfg.deepseek.model,
            },
        )

    @app.get("/api/receipts")
    def receipts():
        conn = sqlite3.connect(str(cfg.database_path))
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(
                "SELECT id, created_at, module, operation, mode, method,"
                " endpoint, http_status, ok, detail FROM receipts"
                " ORDER BY id DESC LIMIT 50"
            ).fetchall()
        except sqlite3.OperationalError:  # table not created yet
            rows = []
        finally:
            conn.close()
        out = []
        for r in rows:
            item = dict(r)
            try:
                item["detail"] = json.loads(item["detail"])
            except (TypeError, ValueError):
                item["detail"] = {}
            out.append(item)
        return jsonify(receipts=out)

    return app
