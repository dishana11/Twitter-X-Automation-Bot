# 🐦 Twitter Automation Bot — Quick Setup Guide

## 🔧 Environment Variables to Set

Go to your GitHub repository:

```
Settings → Secrets and variables → Actions
```

Then **add the following variables**:

```
API_TOKEN_GITHUB  
CLAUDE_API_KEY  
GOOGLE_GEMINI  
OPENAI_API_KEY  
OPENAI_SAMAPI_KEY  
OPENROUTER_API_KEY  
TWITTER_ACCESS_TOKEN  
TWITTER_ACCESS_TOKEN_SECRET  
TWITTER_BEARER_TOKEN  
TWITTER_CONSUMER_KEY  
TWITTER_CONSUMER_SECRET  
```

---

## 🔑 Get Your API Keys

- [Twitter Developer Keys](https://developer.twitter.com/en/portal/dashboard)  
- [Google Gemini API Key](https://aistudio.google.com/app/apikey)  
- [Claude API Key (Anthropic)](https://console.anthropic.com/settings/keys)  
- [OpenAI API Key](https://platform.openai.com/account/api-keys)  
- [OpenRouter API Key](https://openrouter.ai/keys)

---

## 🚀 How to Use

### ▶️ Option 1: Streamlit Dashboard (Manual Posting)

```bash
streamlit run streamlit_twitter_bot.py --server.port 5000 --server.address 0.0.0.0
```

### ▶️ Option 2: Production Bot (Command Line)

```bash
python production_bot_v2.py
```

### ▶️ Option 3: GitHub Actions Workflows

1. Go to the **Actions** tab of your repository  
2. Select a workflow:
   - `manual-post.yml` (Manual post)
   - `scheduled-posts.yml` (Daily at 10 AM IST)

---

## 📦 Features

- ✅ Sentiment-aware smart tweeting  
- ✅ Auto-post hourly/daily with GitHub Actions  
- ✅ Manual + AI-generated tweet creation  
- ✅ Trending tweet detection  
- ✅ Works on Streamlit, CLI, Docker, and GitHub Actions

---

## 🗃️ Directory Structure

```text
.
├── streamlit_twitter_bot.py          # Streamlit UI
├── production_bot_v2.py              # CLI bot
├── .github/
│   └── workflows/
│       ├── manual-post.yml
│       └── scheduled-posts.yml
├── README.md                         # This file
└── requirements.txt
```

---

## 🛠️ Requirements

Install all dependencies using pip:

```bash
pip install -r requirements.txt
```

---

## 💡 Tip

Keep your API keys secret. Never commit `.env` files or secrets directly into the repository.

---

## ✅ Done!

You're ready to tweet like a pro, automatically!  
Happy hacking 💻🐤
