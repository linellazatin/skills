"""One explicit non-streaming chat-completions adapter, without retries."""
import json
import os
from pathlib import Path
import time
from urllib.parse import urlsplit
from urllib.request import Request
from urllib.error import HTTPError

from buffer_core import attempt_store, classify, load_workspace, parse_json, read_json, write_json


def redact(value, secret):
    if isinstance(value, str):
        return value.replace(secret, '[REDACTED]') if secret else value
    if isinstance(value, list):
        return [redact(x, secret) for x in value]
    if isinstance(value, dict):
        return {redact(k, secret): redact(v, secret) for k, v in value.items()}
    return value


def evaluate(workspace, endpoint, model, api_key_env=None, resume=False, token_field='max_tokens'):
    manifest = load_workspace(workspace)
    workspace = Path(workspace)
    parsed = urlsplit(endpoint)
    if parsed.scheme not in ('http', 'https') or not parsed.netloc or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError('endpoint must be an explicit HTTP(S) URL without credentials/query/fragment')
    if not model or token_field not in ('max_tokens', 'max_completion_tokens'):
        raise ValueError('model and supported token field required')
    secret = os.environ.get(api_key_env) if api_key_env else None
    if api_key_env and not secret:
        raise ValueError('specified API-key environment variable is empty')
    config = {'version': 1, 'endpoint': endpoint, 'model': model, 'api_key_env': api_key_env, 'token_field': token_field, 'fingerprint': manifest['fingerprint']}
    if secret and secret in json.dumps(config):
        raise ValueError('credential appears in configuration')
    config_path = workspace / 'evaluation.json'
    data = attempt_store(workspace, manifest)
    if config_path.exists():
        if not resume or read_json(config_path) != config:
            raise ValueError('explicit resume with identical configuration required')
    else:
        if resume:
            raise ValueError('no evaluation to resume')
        if data['attempts']:
            raise ValueError('workspace already contains imported attempts')
        write_json(config_path, config)
    completed = {row['job_id'] for row in data['attempts']}
    settings = manifest['settings']
    for job in manifest['jobs']:
        if job['id'] in completed:
            continue
        request = dict(settings['provider_parameters'], model=model, messages=[{'role': 'user', 'content': job['prompt']}], stream=False, temperature=settings['temperature'], seed=settings['seed'])
        request[token_field] = settings['max_tokens']
        headers = {'Content-Type': 'application/json'}
        if secret:
            headers['Authorization'] = 'Bearer ' + secret
        started = time.monotonic()
        response, raw, error, telemetry = '', None, None, None
        status = 'complete'
        try:
            # Never follow redirects, which could forward authorization to a different endpoint.
            from urllib.request import HTTPRedirectHandler, build_opener
            class NoRedirect(HTTPRedirectHandler):
                def redirect_request(self, req, fp, code, msg, headers, newurl):
                    return None
            with build_opener(NoRedirect).open(Request(endpoint, data=json.dumps(request).encode(), headers=headers), timeout=settings['timeout']) as handle:
                raw = handle.read().decode('utf-8')
        except (OSError, ValueError) as exc:
            status, error = 'transport-error', str(exc)
            if isinstance(exc, HTTPError):
                exc.close()
        if status != 'transport-error':
            try:
                decoded = parse_json(raw)
                choice = decoded['choices'][0]
                response = choice['message']['content']
                if not isinstance(response, str) or choice.get('finish_reason') not in ('stop', 'length'):
                    raise ValueError('unsupported response shape or completion reason')
                status = 'truncated' if choice['finish_reason'] == 'length' else 'complete'
                telemetry = decoded.get('usage') if isinstance(decoded.get('usage'), dict) else None
            except (ValueError, TypeError, KeyError, IndexError):
                response = ''
                error = 'malformed provider response'
                status = 'malformed-output'
        row = {'job_id': job['id'], 'response': response, 'completion_status': status, 'classification': classify(manifest, job, response, status), 'fingerprint': manifest['fingerprint'], 'provenance': {'label': 'http-chat-completions'}, 'request': request, 'raw_response': raw, 'error': error, 'telemetry': telemetry, 'elapsed_seconds': time.monotonic() - started}
        row = redact(row, secret)
        # Classify the stored, sanitized content so later verification is consistent.
        row['classification'] = classify(manifest, job, row['response'], status)
        if status == 'transport-error':
            failures = read_json(workspace / 'failures.json') if (workspace / 'failures.json').exists() else {'version': 1, 'failures': []}
            failures['failures'].append(row)
            write_json(workspace / 'failures.json', failures)
            return {'version': 1, 'stopped': True, 'job_id': job['id'], 'error': row['error']}
        data['attempts'].append(row)
        write_json(workspace / 'attempts.json', data)
    return {'version': 1, 'stopped': False, 'completed': len(data['attempts'])}
