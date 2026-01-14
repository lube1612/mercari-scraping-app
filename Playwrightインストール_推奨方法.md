# Playwrightブラウザインストール - 推奨方法

## ⚠️ 手動ダウンロードでエラーが発生した場合

`GatewayExceptionResponse`エラーが発生した場合、サーバー側の問題の可能性があります。
**最も確実な方法は、Playwrightの公式インストールコマンドを使用することです。**

## 🚀 推奨方法：公式インストールコマンド（最も簡単）

### 方法1: Pythonスクリプトから実行

**Cursorのターミナルで以下のコマンドを実行：**

```bash
cd /Users/shimadaeiji/Documents/Cursor/e2e
python3 install_playwright_simple.py
```

このスクリプトが自動的にブラウザをインストールします。

### 方法2: 直接コマンドを実行

**ターミナルで以下のコマンドを実行：**

```bash
python3 -m playwright install chromium
```

このコマンドが最も確実で簡単です。

## 📋 インストール手順（詳細）

1. **ターミナルを開く**
   - Cursorのターミナルを使用

2. **インストールコマンドを実行**
   ```bash
   python3 -m playwright install chromium
   ```

3. **インストールの進行**
   - ダウンロードが開始されます（約150-200MB）
   - 数分かかる場合があります
   - 進捗が表示されます

4. **インストール確認**
   ```bash
   python3 -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); browser = p.chromium.launch(headless=True); print('✓ 成功'); browser.close(); p.stop()"
   ```

## ✅ インストールが完了したら

以下のコマンドでスクレイピングを開始できます：

```bash
python3 mercari/scrape.py
```

## 🔍 トラブルシューティング

### 問題1: ネットワークエラーが発生する

**解決方法:**
- インターネット接続を確認
- ファイアウォールやプロキシの設定を確認
- しばらく時間をおいて再試行

### 問題2: 権限エラーが発生する

**解決方法:**
```bash
# 保存先ディレクトリの権限を確認
ls -la ~/Library/Caches/ms-playwright/

# 必要に応じて権限を変更
chmod -R 755 ~/Library/Caches/ms-playwright/
```

### 問題3: インストールが途中で止まる

**解決方法:**
- ターミナルで `Ctrl + C` で中断
- 以下を実行して再試行：
  ```bash
  python3 -m playwright install chromium
  ```

## 📝 なぜ公式コマンドが推奨されるのか

1. **自動的に正しいバージョンをダウンロード**
   - Playwrightのバージョンとブラウザのバージョンが自動的に一致

2. **正しい場所に自動配置**
   - 必要なディレクトリ構造を自動的に作成

3. **エラーハンドリング**
   - ネットワークエラーや権限エラーを適切に処理

4. **メンテナンスが簡単**
   - アップデート時も同じコマンドで対応可能

## 🎯 まとめ

**最も簡単で確実な方法：**

```bash
python3 -m playwright install chromium
```

この1つのコマンドで、すべてが自動的に設定されます。
