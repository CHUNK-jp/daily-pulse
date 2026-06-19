# 🌅 DailyPulse

**Your Personal AI Morning Brief.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Powered by Ollama](https://img.shields.io/badge/Powered%20by-Ollama-black?style=flat)](https://ollama.com/)
[![No Cloud](https://img.shields.io/badge/Cloud-None-lightgrey?style=flat)](#)

> Aggregates HackerNews, RSS feeds, and Reddit — then summarizes everything with a local LLM.
> One command. No subscriptions. No tracking. Just your brief.

## 🚀 Quick Start

```bash
pip install -r requirements.txt

# Option A: Local LLM (free, private)
ollama pull llama3.2
python3 daily_pulse.py run

# Option B: Claude API
ANTHROPIC_API_KEY=sk-... python3 daily_pulse.py run --provider claude

# Save to file
python3 daily_pulse.py run -o brief.md

# Japanese output
python3 daily_pulse.py run --lang ja
```

## 📖 Commands

| Command | Description |
|---|---|
| `run` | Fetch sources, summarize, print brief |
| `run -o FILE` | Save brief to a file |
| `run --format html` | Output as HTML |
| `run --lang ja` | Summarize in Japanese |
| `run --provider claude` | Use Claude API instead of Ollama |
| `init` | Create config at `~/.config/daily-pulse/config.yaml` |
| `sources` | List all configured sources |

## ⚙️ Configuration

```bash
python3 daily_pulse.py init        # creates ~/.config/daily-pulse/config.yaml
```

Or copy `config.example.yaml` to `~/.config/daily-pulse/config.yaml` and edit:

```yaml
sources:
  hackernews:
    enabled: true
    limit: 10
  rss:
    - name: The Verge
      url: https://www.theverge.com/rss/index.xml
  reddit:
    - subreddit: programming
      limit: 5

ai:
  provider: ollama          # or "claude"
  ollama_model: llama3.2

output:
  language: en              # or "ja"
  format: markdown          # or "html"
```

## 🔁 Automate It

**macOS / Linux (cron):**
```bash
# Every morning at 7:00 AM
0 7 * * * cd /path/to/daily-pulse && python3 daily_pulse.py run -o ~/brief-$(date +%F).md
```

**GitHub Actions:**
```yaml
on:
  schedule:
    - cron: "0 22 * * *"   # 7 AM JST
jobs:
  brief:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r requirements.txt
      - run: python3 daily_pulse.py run --provider claude -o brief.md
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

## 🧠 How It Works

```
HackerNews API ──┐
RSS Feeds ───────┼──► Collect headlines ──► Local LLM / Claude ──► Markdown Brief
Reddit JSON ─────┘
```

## 📁 Sources

| Source | Auth needed? | Cost |
|---|---|---|
| HackerNews | No | Free |
| RSS / Atom | No | Free |
| Reddit | No | Free |
| Ollama LLM | No | Free (local) |
| Claude API | API key | Pay-per-use |

## 📄 License

MIT — free to use, modify, and distribute.

---

*Built by [CHUNK-jp](https://github.com/CHUNK-jp) · No cloud. No subscription. Just your brief.*
