# DailyPulse を GitHub に公開する手順

## 全体の流れ

```
① ファイルをまとめる
    ↓
② GitHubにリポジトリを作る
    ↓
③ ファイルをアップロードする
    ↓
④ ウェブサイト（GitHub Pages）を有効にする
    ↓
⑤ chunk-jp.github.io にリンクを追加する
```

---

## ① ファイルの準備

Claude が作ったファイルは以下の6つです。
すべて `daily-pulse` というフォルダに入っています。

```
daily-pulse/
├── daily_pulse.py        ← ツール本体
├── requirements.txt      ← 必要なライブラリのリスト
├── config.example.yaml   ← 設定ファイルのサンプル
├── README.md             ← GitHubに表示される説明文
├── docs/
│   └── index.html        ← 紹介ウェブサイト
└── ORG_INDEX_PATCH.md    ← chunk-jp.github.io に追加するコード
```

---

## ② GitHubにリポジトリを作る

1. ブラウザで https://github.com/CHUNK-jp を開く
2. 右上の緑の **「New」** ボタンをクリック
3. 以下のように入力する：
   - **Repository name**（リポジトリ名）: `daily-pulse`
   - **Description**: `Your personal AI morning brief. No cloud. No subscription.`
   - **Public**（公開）を選ぶ
   - ⚠️ 「Add a README file」には **チェックを入れない**
4. 緑の **「Create repository」** をクリック

---

## ③ ファイルをアップロードする

リポジトリが作られたら、空のページが表示されます。

1. 「**uploading an existing file**」というリンクをクリック
2. `daily-pulse` フォルダの中身を **全部ドラッグ＆ドロップ**
   - ⚠️ `docs` フォルダも忘れずに！
3. ページ下部の **「Commit changes」** ボタンをクリック

> **ターミナルが使える場合**（より確実な方法）:
> ```bash
> cd daily-pulseフォルダのパス
> git init
> git add .
> git commit -m "🌅 Initial release"
> git remote add origin https://github.com/CHUNK-jp/daily-pulse.git
> git push -u origin main
> ```

---

## ④ ウェブサイトを有効にする（GitHub Pages）

1. リポジトリのページ上部の **「Settings」** タブをクリック
2. 左メニューの **「Pages」** をクリック
3. **「Source」** のところで：
   - Branch: `main` を選ぶ
   - フォルダ: `/ (root)` から **`/docs`** に変更
4. **「Save」** をクリック
5. しばらく待つと（1〜3分）、上部に URL が表示される

```
✅ Your site is published at https://chunk-jp.github.io/daily-pulse/
```

---

## ⑤ chunk-jp.github.io にリンクを追加する

`chunk-jp.github.io` リポジトリ（https://github.com/CHUNK-jp/CHUNK-jp.github.io）の `index.html` を開いて、
attic のカードの近くに以下を貼り付けます。

```html
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

**GitHubの画面で直接編集する方法：**
1. `index.html` を開く
2. 右上の ✏️（鉛筆マーク）をクリック
3. 上のコードを貼り付ける
4. 「Commit changes」をクリック

---

## ✅ 完了後の確認

| URL | 内容 |
|-----|------|
| `https://github.com/CHUNK-jp/daily-pulse` | GitHubリポジトリ（コード） |
| `https://chunk-jp.github.io/daily-pulse/` | 紹介ウェブサイト |
| `https://chunk-jp.github.io/` | CHUNK-jpのトップ（ここにリンクが追加される） |

---

## 困ったときは

- ファイルのアップロードがうまくいかない → Claude に「GitHubにファイルをアップロードしたい」と相談
- GitHub Pages が表示されない → Settings → Pages を再確認（数分かかることがある）
- `docs` フォルダが見当たらない → アップロード時に `docs` フォルダごとドラッグ
