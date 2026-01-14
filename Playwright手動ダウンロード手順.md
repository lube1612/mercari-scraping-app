# Playwright ブラウザ手動ダウンロード手順

## 📋 現在の環境情報

- **Playwrightバージョン**: 1.57.0
- **必要なブラウザ**: Chromium 1200
- **OS**: macOS
- **保存先**: `/Users/shimadaeiji/Library/Caches/ms-playwright/chromium-1200/chrome-mac-x64/`

## 🔗 ダウンロードURL

### Chromium (macOS用)

**直接ダウンロードURL:**
```
https://playwright.azureedge.net/builds/chromium/1200/chromium-mac-x64.zip
```

**ブラウザ一覧ページ:**
```
https://playwright.azureedge.net/builds/chromium/
```

## 📥 手動ダウンロード手順

### ステップ1: ZIPファイルをダウンロード

**方法A: ターミナルからダウンロード（推奨・最も簡単）**

以下のコマンドをターミナルで実行：

```bash
cd /Users/shimadaeiji/Documents/Cursor/e2e
./download_chromium.sh
```

または、直接curlコマンドで：

```bash
mkdir -p ~/Library/Caches/ms-playwright/chromium-1200/chrome-mac-x64
cd ~/Downloads
curl -L -o chromium-mac-x64.zip https://playwright.azureedge.net/builds/chromium/1200/chromium-mac-x64.zip
```

**方法B: ブラウザからダウンロード**

1. ブラウザで以下のURLを開く：
   ```
   https://playwright.azureedge.net/builds/chromium/1200/chromium-mac-x64.zip
   ```

2. **ダウンロードが始まらない場合：**
   - **Safari**: URLを右クリック → 「リンク先をダウンロード」
   - **Chrome**: URLを右クリック → 「リンク先を名前を付けて保存」
   - **Firefox**: URLを右クリック → 「リンクを名前を付けて保存」

3. ZIPファイルがダウンロードされます
   - ファイル名: `chromium-mac-x64.zip`
   - サイズ: 約150-200MB（ダウンロードに数分かかる場合があります）

### ステップ2: 保存先ディレクトリを作成

**ターミナルで以下のコマンドを実行：**

```bash
mkdir -p ~/Library/Caches/ms-playwright/chromium-1200/chrome-mac-x64
```

### ステップ3: ZIPファイルを解凍

**ターミナルで以下のコマンドを実行：**

```bash
# ダウンロードフォルダに移動（通常は ~/Downloads）
cd ~/Downloads

# ZIPファイルを解凍
unzip chromium-mac-x64.zip -d ~/Library/Caches/ms-playwright/chromium-1200/chrome-mac-x64/
```

または、Finderで：
1. `chromium-mac-x64.zip` をダブルクリックして解凍
2. 解凍されたフォルダを `~/Library/Caches/ms-playwright/chromium-1200/chrome-mac-x64/` に移動

### ステップ4: 実行権限を付与

**ターミナルで以下のコマンドを実行：**

```bash
chmod +x ~/Library/Caches/ms-playwright/chromium-1200/chrome-mac-x64/"Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
```

### ステップ5: ディレクトリ構造の確認

正しく配置されているか確認：

```bash
ls -la ~/Library/Caches/ms-playwright/chromium-1200/chrome-mac-x64/
```

以下のような構造になっているはずです：
```
chrome-mac-x64/
└── Google Chrome for Testing.app/
    └── Contents/
        └── MacOS/
            └── Google Chrome for Testing  (実行ファイル)
```

## ✅ インストール確認

インストールが成功したか確認するには、以下のコマンドを実行：

```bash
python3 -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); browser = p.chromium.launch(headless=True); print('✓ ブラウザの起動に成功しました！'); browser.close(); p.stop()"
```

または、以下のPythonスクリプトを実行：

```python
from playwright.sync_api import sync_playwright

try:
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    print("✓ ブラウザの起動に成功しました！")
    browser.close()
    p.stop()
except Exception as e:
    print(f"✗ エラー: {e}")
```

## 🔍 トラブルシューティング

### 問題1: ZIPファイルがダウンロードできない

**解決方法:**
- ブラウザのダウンロード設定を確認
- 別のブラウザで試す
- 直接URLをコピーしてダウンロードマネージャーでダウンロード

### 問題2: 解凍後のファイルが見つからない

**確認コマンド:**
```bash
find ~/Library/Caches/ms-playwright -name "Google Chrome for Testing" -type f
```

### 問題3: 実行権限エラー

**解決方法:**
```bash
chmod +x ~/Library/Caches/ms-playwright/chromium-1200/chrome-mac-x64/"Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
```

### 問題4: パスが正しくない

**確認コマンド:**
```bash
ls -la ~/Library/Caches/ms-playwright/chromium-1200/chrome-mac-x64/"Google Chrome for Testing.app/Contents/MacOS/"
```

## 📝 一括実行コマンド（コピー&ペースト用）

以下のコマンドを順番に実行してください：

```bash
# 1. ディレクトリ作成
mkdir -p ~/Library/Caches/ms-playwright/chromium-1200/chrome-mac-x64

# 2. ZIPファイルをダウンロード（ブラウザで手動）
# https://playwright.azureedge.net/builds/chromium/1200/chromium-mac-x64.zip

# 3. ZIPファイルを解凍（ダウンロードフォルダに保存した場合）
cd ~/Downloads && unzip chromium-mac-x64.zip -d ~/Library/Caches/ms-playwright/chromium-1200/chrome-mac-x64/

# 4. 実行権限を付与
chmod +x ~/Library/Caches/ms-playwright/chromium-1200/chrome-mac-x64/"Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"

# 5. 確認
ls -la ~/Library/Caches/ms-playwright/chromium-1200/chrome-mac-x64/"Google Chrome for Testing.app/Contents/MacOS/"
```

## 🚀 インストール後の次のステップ

インストールが完了したら、以下のコマンドでスクレイピングを開始できます：

```bash
python3 mercari/scrape.py
```

## 📚 参考リンク

- Playwright公式ドキュメント: https://playwright.dev/python/docs/browsers
- Playwright GitHub: https://github.com/microsoft/playwright
- ブラウザビルド一覧: https://playwright.azureedge.net/builds/chromium/
