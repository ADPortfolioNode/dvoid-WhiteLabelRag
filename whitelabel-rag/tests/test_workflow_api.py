"""Workflow selection + Stats endpoint (complete-workflows pass).

The four RAG workflows are real backend modes, but the UI used to never
send its choice (every query ran basic) and the Stats view was an empty
box. These tests pin the route contract with a stubbed RAG manager —
they never call the LLM or Chroma.
"""

from unittest.mock import patch


class _StubManager:
    """Stand-in for RAGManager: records the workflow it was asked for."""

    def __init__(self, stats=None, stats_error=None):
        self.seen_workflow = None
        self.stats = stats or {'documents_count': 7, 'steps_count': 2, 'total_items': 9}
        self.stats_error = stats_error

    def query_documents(self, query, n_results=3, workflow_type='basic',
                        force_internet_search=False):
        self.seen_workflow = workflow_type
        return {
            'rag_response': {
                'text': 'stub answer',
                'sources': ['doc.txt'],
                'workflow': workflow_type,
                'results': [],
                'context_used': True,
            },
            'internet_search_response': None,
        }

    def get_collection_stats(self):
        if self.stats_error is not None:
            raise self.stats_error
        return dict(self.stats)


def _post_query(client, payload):
    return client.post('/api/query', json=payload)


def test_query_passes_workflow_type(app):
    stub = _StubManager()
    with patch('app.api.routes.get_rag_manager', return_value=stub):
        resp = _post_query(app.test_client(), {'query': 'hello', 'workflow_type': 'advanced'})
    assert resp.status_code == 200
    assert stub.seen_workflow == 'advanced'
    assert resp.get_json()['rag_response']['workflow'] == 'advanced'


def test_query_defaults_to_basic(app):
    stub = _StubManager()
    with patch('app.api.routes.get_rag_manager', return_value=stub):
        resp = _post_query(app.test_client(), {'query': 'hello'})
    assert resp.status_code == 200
    assert stub.seen_workflow == 'basic'


def test_query_unknown_workflow_falls_back_to_basic(app):
    stub = _StubManager()
    with patch('app.api.routes.get_rag_manager', return_value=stub):
        resp = _post_query(app.test_client(), {'query': 'hello', 'workflow_type': 'nonsense'})
    assert resp.status_code == 200
    assert stub.seen_workflow == 'basic'


def test_stats_returns_counts(app):
    stub = _StubManager()
    with patch('app.api.routes.get_rag_manager', return_value=stub):
        resp = app.test_client().get('/api/stats')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['documents_count'] == 7
    assert data['steps_count'] == 2
    assert data['total_items'] == 9
    assert data['chroma_available'] is True
    assert isinstance(data['files'], int)


def test_stats_degrades_when_chroma_down(app):
    stub = _StubManager(stats_error=RuntimeError('ChromaDB service not available'))
    with patch('app.api.routes.get_rag_manager', return_value=stub):
        resp = app.test_client().get('/api/stats')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['chroma_available'] is False
    assert data['documents_count'] == 0
    assert data['total_items'] == 0


def test_stats_route_registered(app):
    rules = {str(rule) for rule in app.url_map.iter_rules()}
    assert '/api/stats' in rules
