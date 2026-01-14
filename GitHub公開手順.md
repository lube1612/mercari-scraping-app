# GitHub公開手順ガイド

このガイドに従って、StreamlitアプリをGitHubに公開し、Streamlit Cloudでデプロイします。

## 📋 事前準備

- ✅ GitHubアカウントを持っている
- ✅ Gitがインストールされている（確認: `git --version`）

---

## ステップ1: Gitリポジトリを初期化

ターミナルでプロジェクトフォルダに移動して、以下のコマンドを実行：

```bash
cd /Users/shimadaeiji/Documents/Cursor/e2e
git init
```

---

## ステップ2: ファイルをステージング

```bash
git add .
```

**注意**: `.gitignore`ファイルで以下のファイルは除外されます：
- `__pycache__/` フォルダ
- `*.csv` ファイル（出力ファイル）
- `playwright-browsers/` フォルダ
- その他の一時ファイル

---

## ステップ3: 初回コミット

```bash
git commit -m "Initial commit: Streamlit app for Mercari scraping"
```

---

## ステップ4: GitHubでリポジトリを作成

1. **GitHubにログイン**
   - https://github.com にアクセス
   - ログイン

2. **新しいリポジトリを作成**
   - 右上の「+」ボタンをクリック
   - 「New repository」を選択

3. **リポジトリの設定**
   - **Repository name**: `mercari-scraping-app`（お好みの名前）
   - **Description**: `メルカリスクレイピング用のStreamlitアプリ`
   - **Public** を選択（Streamlit Cloudで公開するため）
   - ⚠️ **重要**: 「Initialize this repository with a README」は**チェックしない**
   - 「Create repository」をクリック

4. **リモートリポジトリのURLをコピー**
   - 作成後、表示されるページでURLをコピー
   - 例: `https://github.com/あなたのユーザー名/mercari-scraping-app.git`

---

## ステップ5: リモートリポジトリを追加してプッシュ

ターミナルで以下を実行（URLは実際のものに置き換えてください）：

```bash
# リモートリポジトリを追加
git remote add origin https://github.com/あなたのユーザー名/mercari-scraping-app.git

# ブランチ名をmainに変更（必要に応じて）
git branch -M main

# GitHubにプッシュ
git push -u origin main
```

**認証が必要な場合**:
- GitHubのユーザー名とパスワード（またはPersonal Access Token）を入力
- Personal Access Tokenが必要な場合は、以下を参照：
  - https://github.com/settings/tokens

---

## ステップ6: Streamlit Cloudでデプロイ

### 6-1. Streamlit Cloudにアクセス

1. https://streamlit.io/cloud にアクセス
2. 「Sign up」または「Sign in」をクリック
3. 「Continue with GitHub」をクリック
4. GitHubアカウントで認証

### 6-2. アプリをデプロイ

1. **「New app」をクリック**

2. **リポジトリを選択**
   - 「Repository」で先ほど作成したリポジトリを選択
   - 例: `あなたのユーザー名/mercari-scraping-app`

3. **ブランチを選択**
   - 「Branch」で `main` を選択

4. **メインファイルを指定**
   - 「Main file path」に `streamlit_app.py` を入力

5. **「Deploy」をクリック**

### 6-3. デプロイの完了を待つ

- 初回デプロイには数分かかります
- 「Deploying...」から「Running」に変われば完了です

---

## ステップ7: アプリのURLを取得

デプロイが完了すると、以下のようなURLが表示されます：

```
https://your-app-name.streamlit.app
```

または

```
https://mercari-scraping-app.streamlit.app
```

このURLをコピーして、他の人と共有できます！

---

## 🔧 トラブルシューティング

### 問題1: Git pushで認証エラーが出る

**解決方法**:
1. Personal Access Tokenを作成
   - https://github.com/settings/tokens
   - 「Generate new token (classic)」
   - `repo` スコープを選択
   - トークンをコピー
2. パスワードの代わりにトークンを使用

### 問題2: Streamlit CloudでPlaywrightが動かない

**解決方法**:
- `requirements.txt` に `playwright>=1.40.0` が含まれていることを確認
- Streamlit Cloudは自動的にブラウザをインストールします

### 問題3: デプロイが失敗する

**確認事項**:
- `requirements.txt` が存在するか
- `streamlit_app.py` が正しいパスにあるか
- エラーログを確認（Streamlit Cloudの管理画面で）

---

## 📝 今後の更新方法

コードを更新したら、以下のコマンドでGitHubに反映：

```bash
git add .
git commit -m "更新内容の説明"
git push
```

Streamlit Cloudは自動的に再デプロイされます。

---

## ✅ チェックリスト

公開前の確認：

- [ ] `.gitignore` で機密情報を除外している
- [ ] `requirements.txt` が最新である
- [ ] `streamlit_app.py` が正しく動作する
- [ ] README.mdに説明がある（オプション）

---

## 🎉 完了！

これで、世界中の誰でもあなたのアプリにアクセスできるようになりました！

URLを共有して、みんなに使ってもらいましょう。
