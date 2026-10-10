"""LLM call utility shared by improve_description.py and run_loop.py.

Provider detection order (no config needed — runtime env vars only):
  1. ANTHROPIC_API_KEY set → Anthropic Messages API (stdlib urllib)
  2. OPENAI_API_KEY set    → OpenAI-compatible API (stdlib urllib);
                             base URL from OPENAI_API_BASE env var
  3. Neither set           → claude -p subprocess (Claude Code CLI fallback)

Public interface: call(prompt, model=None, timeout=300) -> str
"""
import json
import os
import subprocess
import urllib.error
import urllib.request
from typing import Optional


def call(prompt: str, model: Optional[str] = None, timeout: int = 300) -> str:
    """Call the configured LLM provider with prompt; return text response."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        return _anthropic(prompt, model, api_key, timeout)

    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        base = os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1")
        return _openai(prompt, model or "gpt-4o", openai_key, base, timeout)

    return _claude_p(prompt, model, timeout)


def _anthropic(prompt: str, model: Optional[str], api_key: str, timeout: int) -> str:
    payload = {
        "model": model or "claude-sonnet-5",
        "max_tokens": 2048,
        "messages": [{"role": "user", "content": prompt}],
    }
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(payload).encode(),
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Anthropic API error {e.code}: {e.read().decode()}") from e
    return data["content"][0]["text"]


def _openai(prompt: str, model: str, api_key: str, base: str, timeout: int) -> str:
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
    }
    req = urllib.request.Request(
        f"{base.rstrip('/')}/chat/completions",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {api_key}",
            "content-type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"OpenAI API error {e.code}: {e.read().decode()}") from e
    return data["choices"][0]["message"]["content"]


def _claude_p(prompt: str, model: Optional[str], timeout: int) -> str:
    cmd = ["claude", "-p", "--output-format", "text"]
    if model:
        cmd.extend(["--model", model])
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    result = subprocess.run(
        cmd, input=prompt, capture_output=True, text=True, env=env, timeout=timeout
    )
    if result.returncode != 0:
        raise RuntimeError(f"claude -p exited {result.returncode}\n{result.stderr}")
    return result.stdout
