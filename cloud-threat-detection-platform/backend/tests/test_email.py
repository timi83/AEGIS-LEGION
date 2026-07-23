from unittest.mock import MagicMock

import src.services.notification_service as ns


def test_send_email_alert_routes_to_sendgrid(monkeypatch):
    """With SENDGRID_API_KEY set (and no Resend key), send_email_alert posts to
    the SendGrid API with the verified sender and returns True on 202."""
    monkeypatch.setenv("SENDGRID_API_KEY", "SG.test-key")
    monkeypatch.setenv("ALERT_EMAIL_FROM", "sender@example.com")
    monkeypatch.delenv("RESEND_API_KEY", raising=False)

    captured = {}

    def fake_post(url, json=None, headers=None, timeout=None):
        captured["url"] = url
        captured["json"] = json
        captured["headers"] = headers
        resp = MagicMock()
        resp.status_code = 202  # SendGrid success
        resp.text = ""
        return resp

    monkeypatch.setattr(ns.requests, "post", fake_post)

    ok = ns.send_email_alert("Welcome", "<p>Hello</p>", "newuser@example.com")

    assert ok is True
    assert captured["url"] == "https://api.sendgrid.com/v3/mail/send"
    assert captured["json"]["from"]["email"] == "sender@example.com"
    assert captured["json"]["personalizations"][0]["to"][0]["email"] == "newuser@example.com"
    assert captured["json"]["content"][0]["type"] == "text/html"
    assert "Bearer SG.test-key" in captured["headers"]["Authorization"]


def test_sendgrid_failure_returns_false(monkeypatch):
    """A non-2xx SendGrid response (e.g. unverified sender -> 403) returns False."""
    monkeypatch.setenv("SENDGRID_API_KEY", "SG.test-key")
    monkeypatch.setenv("ALERT_EMAIL_FROM", "sender@example.com")
    monkeypatch.delenv("RESEND_API_KEY", raising=False)

    def fake_post(*args, **kwargs):
        resp = MagicMock()
        resp.status_code = 403
        resp.text = "The from address does not match a verified Sender Identity."
        return resp

    monkeypatch.setattr(ns.requests, "post", fake_post)

    assert ns.send_email_alert("Subject", "<p>x</p>", "u@example.com") is False


def test_resend_takes_priority_over_sendgrid(monkeypatch):
    """If both keys are set, Resend wins (SendGrid is the fallback)."""
    monkeypatch.setenv("RESEND_API_KEY", "re_test")
    monkeypatch.setenv("SENDGRID_API_KEY", "SG.test-key")
    monkeypatch.setenv("ALERT_EMAIL_FROM", "sender@example.com")

    def fake_post(url, json=None, headers=None, timeout=None):
        resp = MagicMock()
        resp.status_code = 200
        resp.json = lambda: {"id": "abc"}
        resp.text = ""
        # Record which provider was hit via the URL.
        fake_post.url = url
        return resp

    monkeypatch.setattr(ns.requests, "post", fake_post)

    assert ns.send_email_alert("S", "<p>x</p>", "u@example.com") is True
    assert "resend.com" in fake_post.url
