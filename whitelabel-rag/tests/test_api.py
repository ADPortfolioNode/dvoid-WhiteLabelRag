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
    assert b"Answers come from your documents first" in resp.data  # footer names the doc-first chain
    assert b"Google Gemini" in resp.data  # Help names Gemini as the first provider
    assert b"Azure AI" not in resp.data


def test_ingest_endpoint_exists(app):
    client = app.test_client()
    resp = client.post("/api/documents/upload_and_ingest_document", data={})
    assert resp.status_code == 400  # no file provided — but the route exists
    assert "error" in resp.get_json()


def test_home_is_responsive_bootstrap(app):
    """Modern sleek layout: slim app bar + offcanvas-lg sidebar below lg,
    64px icon rail md–lg, workflow bar md+, stepped centered column
    (540/720/768/800/860px) and a persistent right rail at xl+, with the
    Bootstrap bundle actually served (it 404'd before vendoring)."""
    client = app.test_client()
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.data
    # Drawer / sidebar shell (Bootstrap offcanvas-lg pattern).
    assert b"offcanvas" in html
    assert b"offcanvas-lg" in html
    assert b"data-bs-toggle=\"offcanvas\"" in html
    assert b"icon-rail" in html
    assert b"wlr-sidebar" in html
    # Workflow bar + switcher, composer tools row, context rail.
    assert b"workflow-bar" in html
    assert b"ragDropdown" in html
    assert b"composer-tools" in html
    assert b"btnAttach" in html
    assert b"context-rail" in html
    assert b"viewport-fit=cover" in html
    # Every element ID the redesign must preserve.
    for el_id in (
        b"mobileNav", b"mobileNavLabel", b"navbarNav", b"navDocuments",
        b"navStats", b"navHelp", b"welcomeMessage", b"chatMessages",
        b"chatForm", b"chatInput", b"btnClearChat", b"btnListFiles",
        b"chatSection", b"documentsSection", b"documentsList",
        b"uploadForm", b"fileInput", b"uploadStatus", b"statsSection",
        b"statsOutput", b"helpSection", b"ragWorkflowSection",
        b"ragWorkflowTitle", b"ragWorkflowContent",
    ):
        assert el_id in html, el_id
    # No dead script / wrong brand.
    assert b'src="/static/js/app.js"' not in html
    assert b"Azure AI" not in html


def test_home_breakpoint_measures_in_css(app):
    """The five breakpoint pops are real CSS, not classes: the stepped
    column measures and the rail/sidebar widths at each breakpoint."""
    client = app.test_client()
    css = client.get("/static/css/style.css")
    assert css.status_code == 200
    text = css.data.decode()
    assert "max-width: 540px" in text  # sm column
    assert "max-width: 720px" in text  # md column
    assert "max-width: 768px" in text  # lg column
    assert "minmax(0, 800px) 288px" in text  # xl column + rail
    assert "minmax(0, 860px) 320px" in text  # xxl column + rail
    assert "--bs-offcanvas-width: 85vw" in text  # xs drawer
    assert "--bs-offcanvas-width: 320px" in text  # sm drawer
    assert "flex: 0 0 264px" in text  # lg sidebar
    assert "flex-basis: 288px" in text  # xxl sidebar
    assert "#016a71" in text  # one accent: deep teal
    assert "#faf8f5" in text  # warm paper canvas


def test_bootstrap_assets_serve(app):
    client = app.test_client()
    css = client.get("/static/css/bootstrap.min.css")
    assert css.status_code == 200
    assert b"Bootstrap" in css.data
    js = client.get("/static/js/bootstrap.bundle.min.js")
    assert js.status_code == 200
    assert b"Bootstrap" in js.data


def test_home_workflow_views_complete(app):
    """Complete-workflows pass: no 'coming soon' placeholder; the workflow,
    documents, stats and help views all have their real markup."""
    client = app.test_client()
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.data.decode()
    assert "coming soon" not in html
    for element_id in ("ragWorkflowTitle", "ragWorkflowTagline", "ragWorkflowContent",
                       "btnUseWorkflow", "workflowActiveNote", "dropZone",
                       "statsOutput", "btnRefreshStats", "btnListFiles",
                       "documentsList", "uploadForm", "fileInput", "uploadStatus"):
        assert f'id="{element_id}"' in html, element_id
    assert "workflow_type" in html  # chat sends the selected workflow
    assert "Use this workflow" in html
    assert "Drop a file here to upload" in html
    assert "RAG workflows" in html  # Help explains the four workflows
