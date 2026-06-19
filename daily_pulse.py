#!/usr/bin/env python3
"""
DailyPulse — Your personal AI morning brief.
Fetches HackerNews, RSS feeds, and Reddit, summarizes with local LLM or API.
"""

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import httpx
import yaml

CONFIG_PATH = Path.home() / ".config" / "daily-pulse" / "config.yaml"
DEFAULT_CONFIG = {
    "sources": {
        "hackernews": {"enabled": True, "limit": 10},
        "rss": [
            {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml"},
            {"name": "TechCrunch", "url": "https://techcrunch.com/feed/"},
        ],
        "reddit": [
            {"subreddit": "programming", "limit": 5},
            {"subreddit": "machinelearning", "limit": 5},
        ],
    },
    "ai": {
        "provider": "ollama",          # "ollama" or "claude"
        "ollama_model": "llama3.2",
        "ollama_url": "http://localhost:11434",
        "claude_api_key": "",          # set via ANTHROPIC_API_KEY env var
        "claude_model": "claude-haiku-4-5-20251001",
    },
    "output": {
        "format": "markdown",          # "markdown" or "html"
        "max_items": 10,
        "language": "en",              # "en" or "ja"
    },
}


# ── Config ────────────────────────────────────────────────────────────────────

def load_config() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            user = yaml.safe_load(f) or {}
        return deep_merge(DEFAULT_CONFIG, user)
    return DEFAULT_CONFIG


def deep_merge(base: dict, override: dict) -> dict:
    result = base.copy()
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(result.get(k), dict):
            result[k] = deep_merge(result[k], v)
        else:
            result[k] = v
    return result


# ── Fetchers ──────────────────────────────────────────────────────────────────

def fetch_hackernews(limit: int = 10) -> list[dict]:
    """Fetch top stories from HackerNews API."""
    print("  📡 Fetching HackerNews...", file=sys.stderr)
    try:
        r = httpx.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10)
        ids = r.json()[:limit]
        items = []
        for story_id in ids:
            r2 = httpx.get(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json", timeout=10)
            item = r2.json()
            if item and item.get("title"):
                items.append({
                    "source": "HackerNews",
                    "title": item.get("title", ""),
                    "url": item.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
                    "score": item.get("score", 0),
                    "comments": item.get("descendants", 0),
                })
        return items
    except Exception as e:
        print(f"  ⚠️  HackerNews error: {e}", file=sys.stderr)
        return []


def fetch_rss(feeds: list[dict]) -> list[dict]:
    """Fetch items from RSS/Atom feeds."""
    items = []
    for feed in feeds:
        name = feed.get("name", "RSS")
        url = feed.get("url", "")
        print(f"  📡 Fetching {name}...", file=sys.stderr)
        try:
            r = httpx.get(url, timeout=10, follow_redirects=True)
            root = ET.fromstring(r.text)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            # RSS 2.0
            for entry in root.findall(".//item")[:5]:
                title = entry.findtext("title", "")
                link = entry.findtext("link", "")
                items.append({"source": name, "title": title.strip(), "url": link.strip()})
            # Atom
            for entry in root.findall(".//atom:entry", ns)[:5]:
                title = entry.findtext("atom:title", "", ns)
                link_el = entry.find("atom:link", ns)
                link = link_el.get("href", "") if link_el is not None else ""
                items.append({"source": name, "title": title.strip(), "url": link.strip()})
        except Exception as e:
            print(f"  ⚠️  RSS error ({name}): {e}", file=sys.stderr)
    return items


def fetch_reddit(subreddits: list[dict]) -> list[dict]:
    """Fetch hot posts from Reddit."""
    items = []
    headers = {"User-Agent": "DailyPulse/1.0"}
    for sub in subreddits:
        name = sub.get("subreddit", "")
        limit = sub.get("limit", 5)
        print(f"  📡 Fetching r/{name}...", file=sys.stderr)
        try:
            r = httpx.get(
                f"https://www.reddit.com/r/{name}/hot.json?limit={limit}",
                headers=headers, timeout=10,
            )
            posts = r.json()["data"]["children"]
            for post in posts:
                d = post["data"]
                items.append({
                    "source": f"r/{name}",
                    "title": d.get("title", ""),
                    "url": d.get("url", ""),
                    "score": d.get("score", 0),
                })
        except Exception as e:
            print(f"  ⚠️  Reddit error (r/{name}): {e}", file=sys.stderr)
    return items


# ── AI Summarizer ─────────────────────────────────────────────────────────────

def build_prompt(items: list[dict], language: str = "en") -> str:
    lines = [f"- [{i['source']}] {i['title']}" for i in items if i.get("title")]
    bullet_list = "\n".join(lines)

    if language == "ja":
        return f"""以下は今日のテクノロジーニュースの見出しリストです。
重要なトピックを3〜5個選び、それぞれを2〜3文で日本語で要約してください。
最後に「今日のキーワード」を3〜5個挙げてください。

見出し:
{bullet_list}

出力形式:
## 📰 今日のトップニュース

### 1. [タイトル]
[要約]

...

## 🔑 今日のキーワード
キーワード1、キーワード2、...
"""
    else:
        return f"""Here are today's tech news headlines. Pick 3-5 important topics and summarize each in 2-3 sentences.
End with 3-5 "Keywords of the Day".

Headlines:
{bullet_list}

Output format:
## 📰 Top Stories Today

### 1. [Title]
[Summary]

...

## 🔑 Keywords of the Day
keyword1, keyword2, ...
"""


def summarize_ollama(prompt: str, model: str, base_url: str) -> str:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }
    r = httpx.post(f"{base_url}/api/generate", json=payload, timeout=120)
    return r.json().get("response", "")


def summarize_claude(prompt: str, model: str, api_key: str) -> str:
    import os
    key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        raise ValueError("Claude API key not set. Use ANTHROPIC_API_KEY env var or config.")
    headers = {
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload = {
        "model": model,
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}],
    }
    r = httpx.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload, timeout=60)
    return r.json()["content"][0]["text"]


def summarize(items: list[dict], config: dict) -> str:
    ai = config["ai"]
    lang = config["output"].get("language", "en")
    prompt = build_prompt(items, lang)
    provider = ai.get("provider", "ollama")
    print(f"  🤖 Summarizing with {provider}...", file=sys.stderr)
    if provider == "claude":
        return summarize_claude(prompt, ai["claude_model"], ai.get("claude_api_key", ""))
    else:
        return summarize_ollama(prompt, ai["ollama_model"], ai["ollama_url"])


# ── Output ────────────────────────────────────────────────────────────────────

def render_markdown(summary: str, items: list[dict], date_str: str) -> str:
    header = f"# 🌅 DailyPulse — {date_str}\n\n"
    sources_section = "\n\n---\n\n## 🔗 All Sources\n\n"
    for item in items:
        title = item.get("title", "")
        url = item.get("url", "")
        source = item.get("source", "")
        if title and url:
            sources_section += f"- **[{source}]** [{title}]({url})\n"
    footer = "\n\n---\n*Generated by [DailyPulse](https://github.com/CHUNK-jp/daily-pulse) · No cloud. No subscription.*\n"
    return header + summary + sources_section + footer


def render_html(summary: str, items: list[dict], date_str: str) -> str:
    md_body = render_markdown(summary, items, date_str)
    # Simple HTML wrapper
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DailyPulse — {date_str}</title>
<style>
  body {{ font-family: -apple-system, sans-serif; max-width: 720px; margin: 40px auto; padding: 0 20px; line-height: 1.6; color: #24292e; }}
  h1 {{ color: #0366d6; }} h2 {{ border-bottom: 1px solid #eee; padding-bottom: 4px; }}
  a {{ color: #0366d6; }} code {{ background: #f6f8fa; padding: 2px 5px; border-radius: 3px; }}
  pre {{ background: #f6f8fa; padding: 16px; border-radius: 6px; overflow-x: auto; }}
</style>
</head>
<body>
<pre>{md_body}</pre>
</body>
</html>"""


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_run(args, config: dict):
    """Fetch all sources, summarize, and output the brief."""
    print("🌅 DailyPulse starting...", file=sys.stderr)
    items: list[dict] = []

    src = config["sources"]
    if src.get("hackernews", {}).get("enabled", True):
        limit = src["hackernews"].get("limit", 10)
        items += fetch_hackernews(limit)

    if src.get("rss"):
        items += fetch_rss(src["rss"])

    if src.get("reddit"):
        items += fetch_reddit(src["reddit"])

    max_items = config["output"].get("max_items", 20)
    items = items[:max_items]

    if not items:
        print("❌ No items fetched. Check your network or config.", file=sys.stderr)
        sys.exit(1)

    print(f"  ✅ Collected {len(items)} items", file=sys.stderr)

    try:
        summary = summarize(items, config)
    except Exception as e:
        print(f"  ⚠️  AI summarization failed: {e}", file=sys.stderr)
        summary = "\n".join(f"- [{i['source']}] {i['title']}" for i in items)

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    fmt = config["output"].get("format", "markdown")

    if fmt == "html":
        output = render_html(summary, items, date_str)
    else:
        output = render_markdown(summary, items, date_str)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"  💾 Saved to {args.output}", file=sys.stderr)
    else:
        print(output)

    print("✅ Done!", file=sys.stderr)


def cmd_init(args, config: dict):
    """Write default config file."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if CONFIG_PATH.exists() and not args.force:
        print(f"Config already exists at {CONFIG_PATH}. Use --force to overwrite.")
        return
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False, allow_unicode=True)
    print(f"✅ Config written to {CONFIG_PATH}")
    print("   Edit it to add your own RSS feeds, subreddits, and AI provider.")


def cmd_sources(args, config: dict):
    """List configured sources."""
    src = config["sources"]
    print("\n📡 Configured Sources\n")
    if src.get("hackernews", {}).get("enabled"):
        print(f"  • HackerNews  (top {src['hackernews'].get('limit', 10)} stories)")
    for feed in src.get("rss", []):
        print(f"  • RSS: {feed.get('name')}  →  {feed.get('url')}")
    for sub in src.get("reddit", []):
        print(f"  • r/{sub.get('subreddit')}  (top {sub.get('limit', 5)})")
    print()


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="daily-pulse",
        description="🌅 DailyPulse — Your personal AI morning brief",
    )
    sub = parser.add_subparsers(dest="command")

    p_run = sub.add_parser("run", help="Fetch news and generate brief (default)")
    p_run.add_argument("-o", "--output", help="Save output to file (default: stdout)")
    p_run.add_argument("--format", choices=["markdown", "html"], help="Output format")
    p_run.add_argument("--lang", choices=["en", "ja"], help="Output language")
    p_run.add_argument("--provider", choices=["ollama", "claude"], help="AI provider")

    p_init = sub.add_parser("init", help="Create default config file")
    p_init.add_argument("--force", action="store_true", help="Overwrite existing config")

    sub.add_parser("sources", help="List configured sources")

    args = parser.parse_args()
    config = load_config()

    # CLI overrides
    if hasattr(args, "format") and args.format:
        config["output"]["format"] = args.format
    if hasattr(args, "lang") and args.lang:
        config["output"]["language"] = args.lang
    if hasattr(args, "provider") and args.provider:
        config["ai"]["provider"] = args.provider

    if args.command == "init":
        cmd_init(args, config)
    elif args.command == "sources":
        cmd_sources(args, config)
    else:
        # Default: run
        cmd_run(args if args.command else argparse.Namespace(output=None), config)


if __name__ == "__main__":
    main()
