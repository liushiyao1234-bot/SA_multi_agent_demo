"""GLM HTTP client and response parsing helpers."""

import json

import requests

from config import API_KEY, API_URL, MODEL_NAME, REQUEST_TIMEOUT


def call_glm(system_prompt, user_prompt):
    if not API_KEY:
        raise RuntimeError("GLM_API_KEY is not configured. Add it to the project .env file.")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }
    data = {
        "model": MODEL_NAME,
        "stream": False,
        "thinking": {"type": "disabled"},
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    response = requests.post(
        API_URL,
        headers=headers,
        json=data,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    result = response.json()
    return result["choices"][0]["message"]["content"]


def parse_json_response(text):
    if isinstance(text, (dict, list)):
        return text
    if not text or not text.strip():
        raise ValueError("Empty response from agent.")

    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return json.loads(text.strip())
