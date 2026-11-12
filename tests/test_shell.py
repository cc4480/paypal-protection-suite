"""The UI shell: renders all three agents, states its readiness honestly,
shows the Buyer Protection honesty text, and serves stored receipts."""

import pytest

from app import db
from app.config import AppConfig
from app.receipts import LIVE, Receipt, ReceiptLog
from app.routes import create_app


@pytest.fixture()
def client(tmp_path):
    cfg = AppConfig(environ={
        "SUITE_DB_PATH": str(tmp_path / "shell.db"),
        "FLASK_SECRET_KEY": "test",
    })
    app = create_app(cfg)
    app.config.update(TESTING=True)
    return app.test_client(), cfg


def test_shell_renders_three_agents_and_honesty_text(client):
    http, _ = client
    html = http.get("/app").get_data(as_text=True)
    for name in ("WITNESS", "SEATBELT", "AUDITOR"):
        assert name in html
    # SCOPE hard honesty rules, present in the shell itself:
    assert "Friends &amp; Family has NO Buyer Protection" in html
    assert "180 days" in html  # dispute window from the exclusions list
    assert "protected with conditions" in html  # never a universal guarantee
    assert "LIVE SANDBOX" in html and "SIMULATED" in html  # stamp legend
    assert "paypal-mark.svg" in html  # PayPal monogram in the header


def test_status_reports_not_ready_without_credentials(client):
    http, _ = client
    body = http.get("/api/status").get_json()
    assert body["ready"] is False
    assert "PAYPAL_CLIENT_ID" in body["message"]


def test_receipts_endpoint_serves_stored_stamped_receipts(client):
    http, cfg = client
    conn = db.connect(cfg.database_path)
    ReceiptLog(conn).record(Receipt(
        module="spike", operation="invoices_list", mode=LIVE, method="GET",
        endpoint="/v2/invoicing/invoices", http_status=200, ok=True,
        detail={"summary": {"total_items": 3}}))
    body = http.get("/api/receipts").get_json()
    assert len(body["receipts"]) == 1
    r = body["receipts"][0]
    assert r["mode"] == "LIVE SANDBOX" and r["operation"] == "invoices_list"


def test_landing_is_the_front_door_and_explains_the_suite(client):
    http, _ = client
    resp = http.get("/")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    # It says what the app is, in plain words, before anything else:
    assert "PayPal Protection Suite" in html
    assert "These three work for you" in html
    assert 'href="/app"' in html  # the way into the suite
    # Hero carousel: one slide per agent, with its picture:
    assert 'id="slides"' in html
    for img in ("slide-witness.jpg", "slide-seatbelt.jpg",
                "slide-auditor.jpg"):
        assert img in html
    assert "paypal-logo.svg" in html  # PayPal wordmark in the hero lockup
    css = http.get("/static/landing.css").get_data(as_text=True)
    assert "hero-backdrop.jpg" in css  # hero backdrop image wired in
    assert "@keyframes kenburns" in css  # images carry a slight motion
    assert "reveal" in html and "inview" in css  # sections rise in on scroll
    js = http.get("/static/landing.js").get_data(as_text=True)
    assert "IntersectionObserver" in js  # the reveal is actually driven
    assert "AI Hackathon" not in html  # product framing — no event talk
    for name in ("WITNESS", "SEATBELT", "AUDITOR"):
        assert name in html
    # The honesty rules live on the landing page too, not just inside:
    assert "Friends &amp; Family has NO Buyer Protection" in html
    assert "180 days" in html
    assert "protected with conditions" in html
    assert "LIVE SANDBOX" in html and "SIMULATED" in html


def test_video_page_serves_the_framer_composition(client):
    http, _ = client
    page = http.get("/video")
    assert page.status_code == 200
    html = page.get_data(as_text=True)
    assert "Framer Motion" in html  # the composition's own title
    assert len(html) > 1_000_000  # self-contained: art inlined


def test_landing_assets_are_served(client):
    http, _ = client
    for path in ("/static/landing.css", "/static/landing.js",
                 "/static/img/slide-witness.jpg",
                 "/static/img/slide-seatbelt.jpg",
                 "/static/img/slide-auditor.jpg",
                 "/static/img/paypal-logo.svg",
                 "/static/img/paypal-mark.svg",
                 "/static/img/hero-backdrop.jpg"):
        assert http.get(path).status_code == 200, path
