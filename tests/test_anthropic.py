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


@pytest.mark.parametrize('model', ['anthropic/claude-sonnet-4-6', 'claude-sonnet', 'claude-haiku-4-5-20251001'])
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
