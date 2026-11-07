"""Regression tests for the gunicorn worker fix.

gunicorn 26 removed the eventlet worker, so --worker-class eventlet
fails at boot with "class uri 'eventlet' invalid or not found".
The app's SocketIO runs in threading mode, so the matching worker
is gthread. eventlet.monkey_patch() also deadlocks real threads, so
run.py must not apply it. These tests pin that configuration in
the files that define it. No LLM calls, no Chroma calls, no network.
"""

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read(name):
    with open(os.path.join(ROOT, name)) as fh:
        return fh.read()


def _code(text):
    """File content with comment lines and trailing comments removed,
    so explanatory comments cannot trip the assertions."""
    lines = []
    for line in text.splitlines():
        code = line.split("#", 1)[0]
        lines.append(code)
    return "\n".join(lines)


def test_run_py_does_not_monkey_patch_eventlet():
    text = _code(_read("run.py"))
    assert "import eventlet" not in text
    assert "monkey_patch" not in text


def test_entrypoint_uses_gthread_worker():
    text = _code(_read("docker-entrypoint.sh"))
    assert "--worker-class gthread" in text
    assert "--threads" in text
    assert "THREADS=${THREADS:-4}" in text
    assert "--worker-class eventlet" not in text


def test_requirements_and_dockerfile_have_no_eventlet():
    req = _read("requirements.txt")
    assert not any(
        line.split("#")[0].strip().startswith("eventlet")
        for line in req.splitlines()
    ), "eventlet must not be a requirement"
    dockerfile = _read("Dockerfile")
    assert "gunicorn eventlet" not in dockerfile
    assert "pip install --no-cache-dir gunicorn" in dockerfile
    assert "ENV THREADS=4" in dockerfile


def test_compose_passes_threads():
    assert "THREADS=${THREADS:-4}" in _read("docker-compose.yml")
