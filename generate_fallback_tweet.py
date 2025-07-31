import os
import requests
import json
import sys

def get_openai_tweet(api_key, prompt):
    try:
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": f"Write a concise, engaging tweet about: {prompt}.Format like (break line)content ______ ____ ____ ________ (break line) one line space in between hashtags### or if the humourous post it is then  A:      B:     A: then a line gap hashtags### Include trending not more than 2 hashtags."}]
        }
        resp = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data, timeout=15)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"OpenAI failed: {e}")
        return None

def get_claude_tweet(api_key, prompt):
    try:
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        data = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 150,
            "messages": [{"role": "user", "content": f"Write a concise, engaging tweet about: {prompt}. Include trending hashtags."}]
        }
        resp = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=data, timeout=15)
        resp.raise_for_status()
        # Adjust below if Claude's response structure is different
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Claude failed: {e}")
        return None

def get_openrouter_tweet(api_key, prompt):
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/dishana11/yourrepo",
            "X-Title": "GitHub Actions Claude Tweet Generator"
        }
        data = {
            "model": "anthropic/claude-3-sonnet:beta",
            "messages": [{"role": "user", "content": f"Write a concise, engaging tweet about: {prompt}. Include trending hashtags."}]
        }
        resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=15)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"OpenRouter failed: {e}")
        return None

def get_gemini_tweet(api_key, prompt):
    if not api_key:
        print("No Google Gemini API key provided.")
        return None
    endpoint_template = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    models = [
        "gemini-1.5-flash-latest",
        "gemini-1.5-pro-latest"
    ]
    headers = {"Content-Type": "application/json"}
    body = {
        "contents": [{"role": "user", "parts": [{"text": f"Write a concise, engaging tweet about: {prompt}. don't write the prompt in the tweet and leave a line space after tweet for hashtags Include 2 trending hashtags."}]}]
    }
    for model in models:
        try:
            url = endpoint_template.format(model=model, api_key=api_key)
            resp = requests.post(url, headers=headers, json=body, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                # Google's Gemini response structure
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
            else:
                print(f"Gemini {model} failed: {resp.status_code} {resp.text}")
        except Exception as e:
            print(f"Gemini {model} exception: {e}")
    print("All Gemini models failed.")
    return None

prompt = os.environ["PROMPT"]

tweet = None

# Try OpenAI (primary)
tweet = get_openai_tweet(os.environ.get("OPENAI_API_KEY"), prompt) if os.environ.get("OPENAI_API_KEY") else None

# Try OpenAI (secondary)
if not tweet:
    tweet = get_openai_tweet(os.environ.get("OPENAI_SAMAPI_KEY"), prompt) if os.environ.get("OPENAI_SAMAPI_KEY") else None

# Try Claude
if not tweet:
    tweet = get_claude_tweet(os.environ.get("CLAUDE_API_KEY"), prompt) if os.environ.get("CLAUDE_API_KEY") else None

# Try OpenRouter
if not tweet:
    tweet = get_openrouter_tweet(os.environ.get("OPENROUTER_API_KEY"), prompt) if os.environ.get("OPENROUTER_API_KEY") else None

# Try Gemini
if not tweet:
    tweet = get_gemini_tweet(os.environ.get("GOOGLE_GEMINI"), prompt) if os.environ.get("GOOGLE_GEMINI") else None

if tweet:
    print(f"Generated Tweet: {tweet}")
    with open("generated_tweet.txt", "w") as f:
        f.write(tweet)
else:
    print("All AI providers failed.")
    sys.exit(1)
