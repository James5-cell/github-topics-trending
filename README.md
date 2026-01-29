# GitHub Topics Trending

> AI-Curated. Daily Updates. Delivered to Telegram.

[![License: MIT](https://img.shields.io/badge/License-MIT-black.svg)](https://opensource.org/licenses/MIT)

**GitHub Topics Trending** is an intelligent trend tracker that cuts through the noise. Every day, it scans specific GitHub topics, uses Nvidia NIM (Llama 3) to analyze and summarize the most promising projects, and pushes a concise report directly to your Telegram.

It also generates a [Minimalist Static Website](https://geekjourneyx.github.io/github-topics-trending/) for browsing history.

---

## Why this exists?

Finding high-quality tools in a sea of repositories is hard.
- **Top Lists aren't enough**: You need context, not just star counts.
- **Email is cluttered**: Trends should be instant notification, not another unread email.
- **AI-Powered**: We use LLMs to tell you *what* a project does and *why* it matters.

## Features

- **🤖 AI Curation**: Llama 3 summarises READMEs into one-sentence value propositions.
- **📱 Telegram First**: Beautifully formatted reports sent to your chat.
- **🧠 Smart Deduplication**: Knows what it sent you yesterday. No more repetitive spam.
- **🌐 Minimalist Web**: A premium, noise-free web interface to browse past trends.
- **🔌 Pluggable**: Tracking `#claude-code` by default, but configurable for any topic.

## Usage

### 1. Prerequisites

- **GitHub Account**: For API access.
- **Telegram Bot**: Create one via [@BotFather](https://t.me/BotFather) to get a Token.
- **Nvidia API Key**: For the AI brains.

### 2. Setup (Local)

```bash
# Clone
git clone https://github.com/geekjourneyx/github-topics-trending.git
cd github-topics-trending

# Install
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env and add your keys:
# GH_TOKEN, NVIDIA_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
```

### 3. Run

```bash
python -m src.main
```

## Automate with GitHub Actions

This project is designed to run on GitHub Actions (Free Tier).

1. **Fork** this repository.
2. Go to **Settings > Secrets and variables > Actions**.
3. Add the following Repository Secrets:

| Secret | Description |
|--------|-------------|
| `GH_TOKEN` | Your GitHub Personal Access Token |
| `NVIDIA_API_KEY` | Your Nvidia NIM API Key |
| `TELEGRAM_BOT_TOKEN` | Token from BotFather |
| `TELEGRAM_CHAT_ID` | Your user or group Chat ID |

The workflow runs automatically every day at **02:00 UTC** (10:00 Beijing Time).

## Configuration

Modify `src/config.py` or set env vars to customize:

- `TOPIC`: The GitHub topic to track (default: `claude-code`).
- `DEDUPLICATE_DAYS`: How many days to silence repeated repos (default: `7`).
- `NVIDIA_MODEL`: Change the underlying LLM (default: `meta/llama3-70b-instruct`).

## Architecture

`Fetcher` -> `DB` -> `AI Summarizer` -> `Trend Analyzer` -> `Telegram Sender` + `Web Generator`

- **Database**: SQLite (local file, uploaded as artifact).
- **Frontend**: Vanilla CSS + Python Generator (Zero JS framework overhead).

## License

MIT © geekjourneyx
