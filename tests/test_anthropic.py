import io
import json
import urllib.error

import pytest

from interphaise.llm import make_llm


def test_direct_haiku_payload(monkeypatch):
    monkeypatch.setenv('MY_ANTHROPIC_KEY', 'dummy-test-key')
    captured = []
    def respond(request, timeout):
        captured.append(json.loads(request.data))
        assert request.full_url == 'https://api.anthropic.com/v1/messages'
        return io.BytesIO(json.dumps({'model': 'claude-haiku-5-5', 'stop_reason': 'end_turn',
                                     'usage': {'output_tokens': 5},
                                     'content': [{'type': 'text', 'text': '{"ok": true}'}]}).encode())
    monkeypatch.setattr('urllib.request.urlopen', respond)
    llm = make_llm('anthropic/claude-haiku-5-5', temperature=0.3, max_tokens=32)
    assert llm('JSON only', 'test') == {'ok': True}
    assert captured[0]['model'] == 'claude-haiku-5-5'
    assert captured[0]['temperature'] == 0.3
    assert captured[0]['max_tokens'] == 32
    assert llm.last_metadata['usage']['output_tokens'] == 5


@pytest.mark.parametrize('model', ['anthropic/claude-sonnet-4-6', 'claude-sonnet', 'claude-haiku-4-5-20251001',
                                 'openrouter/anthropic/claude-haiku-5-5',
                                 'openrouter/deepseek/deepseek-v3.2', 'gpt-4o', 'deepseek-v3.2'])
def test_other_anthropic_models_blocked(model):
    with pytest.raises(ValueError, match='restricted'):
        make_llm(model)


def test_authentication_failure_has_no_fallback_or_raw_error(monkeypatch):
    monkeypatch.setenv('MY_ANTHROPIC_KEY', 'dummy-test-key')
    calls = []
    def fail(*args, **kwargs):
        calls.append(1)
        raise urllib.error.HTTPError('https://api.anthropic.com/v1/messages', 403,
                                     'sensitive error', {}, io.BytesIO(b'sensitive response'))
    monkeypatch.setattr('urllib.request.urlopen', fail)
    with pytest.raises(RuntimeError, match=r'HTTP 403') as error:
        make_llm('anthropic/claude-haiku-5-5')('test', 'test')
    assert 'sensitive' not in str(error.value)
    assert len(calls) == 1


class _Response(io.BytesIO):
    def __init__(self, body, request_id):
        super().__init__(json.dumps(body).encode())
        self.headers = {"request-id": request_id}


def _ok(text='{"ok": true}'):
    return {"id": "msg_test", "model": "claude-haiku-5-5", "stop_reason": "end_turn",
            "usage": {"input_tokens": 3, "output_tokens": 5}, "content": [{"type": "text", "text": text}]}


def test_429_then_success_counts_transport_retry(monkeypatch):
    monkeypatch.setenv('MY_ANTHROPIC_KEY', 'dummy-test-key')
    monkeypatch.setattr('time.sleep', lambda s: None)
    replies = iter(['429', 'ok'])
    def respond(request, timeout):
        if next(replies) == '429':
            raise urllib.error.HTTPError(request.full_url, 429, 'rate limited', {'request-id': 'req_1'},
                                         io.BytesIO(b'body'))
        return _Response(_ok(), 'req_2')
    monkeypatch.setattr('urllib.request.urlopen', respond)
    llm = make_llm('anthropic/claude-haiku-5-5', max_tokens=32)
    assert llm('JSON only', 'test') == {'ok': True}
    meta = llm.last_metadata
    assert (meta['http_attempts'], meta['transport_retries'], meta['final_error']) == (2, 1, None)
    assert [a['status'] for a in meta['attempts']] == [429, 200]
    assert [a['request_id'] for a in meta['attempts']] == ['req_1', 'req_2'] and meta['response_id'] == 'msg_test'
    assert 'dummy-test-key' not in json.dumps(meta)


def test_exhausted_retries_leave_failure_metadata(monkeypatch):
    monkeypatch.setenv('MY_ANTHROPIC_KEY', 'dummy-test-key')
    monkeypatch.setattr('time.sleep', lambda s: None)
    def fail(request, timeout):
        raise urllib.error.HTTPError(request.full_url, 529, 'overloaded', {}, io.BytesIO(b'body'))
    monkeypatch.setattr('urllib.request.urlopen', fail)
    llm = make_llm('anthropic/claude-haiku-5-5', retries=3)
    with pytest.raises(RuntimeError, match='HTTP 529'):
        llm('test', 'test')
    assert (llm.last_metadata['http_attempts'], llm.last_metadata['final_error']) == (3, 'HTTP 529')
    assert llm.last_metadata['usage'] is None


def test_malformed_output_is_kept_bounded(monkeypatch):
    from interphaise.llm import MALFORMED_TEXT_LIMIT
    monkeypatch.setenv('MY_ANTHROPIC_KEY', 'dummy-test-key')
    monkeypatch.setattr('urllib.request.urlopen', lambda r, timeout: _Response(_ok('no json ' * 2000), 'req_x'))
    llm = make_llm('anthropic/claude-haiku-5-5')
    with pytest.raises(RuntimeError, match='not valid JSON'):
        llm('test', 'test')
    meta = llm.last_metadata
    assert len(meta['malformed_text']) == MALFORMED_TEXT_LIMIT and meta['usage']['output_tokens'] == 5


def test_deepseek_route_pins_provider_and_rejects_unpinned_server(monkeypatch):
    monkeypatch.setenv('MY_OPENROUTER_API_KEY', 'dummy-test-key')
    served, captured = ['SiliconFlow'], []
    def respond(request, timeout):
        captured.append(json.loads(request.data))
        assert request.full_url == 'https://openrouter.ai/api/v1/chat/completions'
        return io.BytesIO(json.dumps({'model': 'deepseek/deepseek-v3.2', 'provider': served[0],
                                     'usage': {'prompt_tokens': 3, 'completion_tokens': 5, 'cost': 1e-6,
                                               'completion_tokens_details': {'reasoning_tokens': 4}},
                                     'choices': [{'finish_reason': 'stop', 'message': {'content': '{"ok": true}'}}]}).encode())
    monkeypatch.setattr('urllib.request.urlopen', respond)
    with pytest.raises(ValueError, match='pin one'):
        make_llm('deepseek/deepseek-v3.2')
    llm = make_llm('deepseek/deepseek-v3.2', temperature=1.0, max_tokens=4096, provider='siliconflow/fp8',
                   reasoning_max_tokens=3072)
    assert llm('JSON only', 'test') == {'ok': True}
    p = captured[0]
    assert p['provider'] == {'order': ['siliconflow/fp8'], 'allow_fallbacks': False, 'require_parameters': True}
    assert p['reasoning'] == {'max_tokens': 3072} and p['max_tokens'] == 4096
    assert llm.last_metadata['usage']['output_tokens_details']['thinking_tokens'] == 4
    served[0] = 'GMICloud'
    with pytest.raises(RuntimeError, match='unpinned'):
        llm('JSON only', 'test')
