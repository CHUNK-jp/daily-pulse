# chunk-jp.github.io への追加手順

`chunk-jp.github.io` リポジトリの `index.html` に、
以下の DailyPulse カードを attic カードと同じスタイルで追加してください。

## 追加するHTMLスニペット

```html
<!-- DailyPulse Card — chunk-jp.github.io/daily-pulse/ -->
<a class="project-card" href="https://chunk-jp.github.io/daily-pulse/">
  <div class="card-icon">🌅</div>
  <div class="card-body">
    <h3>DailyPulse</h3>
    <p>Your personal AI morning brief. HackerNews + RSS + Reddit, summarized locally. No cloud.</p>
    <div class="card-tags">
      <span>Python</span>
      <span>Ollama</span>
      <span>Privacy</span>
    </div>
  </div>
</a>
```

## GitHub Pages の設定（daily-pulse リポジトリ）

1. GitHub で `CHUNK-jp/daily-pulse` リポジトリを作成
2. このフォルダの中身を全部 push
3. Settings → Pages → Source: `main` branch, `/docs` folder
4. URL: `https://chunk-jp.github.io/daily-pulse/` で公開される
