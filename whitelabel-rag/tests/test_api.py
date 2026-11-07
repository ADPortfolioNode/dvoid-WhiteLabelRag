"""Smoke tests for the HTTP API and page routes.

These exist because the repo's own verification (scripts/final-verification.py)
expects test_api.py / test_services.py, and because a blueprint-registration
regression once left every route returning 404. They use the `app` fixture
from conftest.py and never call the LLM or Chroma.
"""

import pytest


def test_health_returns_ok(app):
    client = app.test_client()
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_home_renders(app):
    client = app.test_client()
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"html" in resp.data.lower()


def test_api_files_lists(app):
    client = app.test_client()
    resp = client.get("/api/files")
    assert resp.status_code == 200
    assert "files" in resp.get_json()


def test_api_files_upload_requires_file(app):
    client = app.test_client()
    resp = client.post("/api/files", data={})
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_routes_are_registered(app):
    rules = {str(rule) for rule in app.url_map.iter_rules()}
    assert "/health" in rules
    assert "/" in rules
    assert "/api/files" in rules
    assert "/api/query" in rules


def test_home_has_working_chat_wiring(app):
    """Home page wires chat to the REST query API (not the dead Socket.IO
    app.js, which needs a socket.io client this template never loads)."""
    client = app.test_client()
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"welcomeMessage" in resp.data
    assert b"chatForm" in resp.data
    assert b"/api/query" in resp.data
    assert b'src="/static/js/app.js"' not in resp.data  # no script tag loads it
    assert b"Google Gemini" in resp.data
    assert b"Azure AI" not in resp.data


def test_ingest_endpoint_exists(app):
    client = app.test_client()
    resp = client.post("/api/documents/upload_and_ingest_document", data={})
    assert resp.status_code == 400  # no file provided — but the route exists
    assert "error" in resp.get_json()


def test_home_is_responsive_bootstrap(app):
    """Mobile-first responsive shell: offcanvas drawer below lg, content
    column narrowing across the five named breakpoints (sm/md/lg/xl/xxl),
    and the Bootstrap bundle actually served (it 404'd before vendoring)."""
    client = app.test_client()
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"offcanvas" in resp.data
    assert b"data-bs-toggle=\"offcanvas\"" in resp.data
    assert b"col-md-10" in resp.data
    assert b"col-lg-8" in resp.data
    assert b"col-xl-7" in resp.data
    assert b"col-xxl-6" in resp.data
    assert b"viewport-fit=cover" in resp.data


def test_bootstrap_assets_serve(app):
    client = app.test_client()
    css = client.get("/static/css/bootstrap.min.css")
    assert css.status_code == 200
    assert b"Bootstrap" in css.data
    js = client.get("/static/js/bootstrap.bundle.min.js")
    assert js.status_code == 200
    assert b"Bootstrap" in js.data
