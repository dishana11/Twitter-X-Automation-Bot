import os
import requests

def test_claude_api():
    claude_api_key = os.environ.get("CLAUDE_API_KEY")
    if not claude_api_key or not claude_api_key.strip():
        raise ValueError("CLAUDE_API_KEY environment variable not set or invalid.")

    url = "https://api.anthropic.com/v1/claude-3.7/sonnet/completions"
    headers = {
        "Authorization": f"Bearer {claude_api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "claude-3.7-sonnet",
        "prompt": "Say hello in a friendly way.",
        "max_tokens": 50
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print("API Response:")
        print(data)
    else:
        print(f"Request failed with status code {response.status_code}: {response.text}")

if __name__ == "__main__":
    test_claude_api()
