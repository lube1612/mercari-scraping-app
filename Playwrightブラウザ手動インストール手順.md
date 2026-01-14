# Playwrightブラウザ手動インストール手順

## 📍 ブラウザの保存場所

Playwrightのブラウザは以下の場所に保存されます：

**macOSの場合:**
```
~/Library/Caches/ms-playwright/
```

**現在のエラーメッセージから:**
```
/Users/shimadaeiji/Library/Caches/ms-playwright/chromium-1200/chrome-mac-x64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing
```

## 🚀 推奨方法：コマンドラインでインストール（最も簡単）

### 方法1: Pythonから実行（推奨）

**ターミナルで以下のコマンドを実行してください：**

```bash
python3 -m playwright install chromium
```

または、すべてのブラウザをインストールする場合：

```bash
python3 -m playwright install
```

### 方法2: 直接playwrightコマンドを使用

```bash
playwright install chromium
```

## 📥 手動ダウンロード方法（上級者向け）

Playwrightのブラウザは特定のバージョンと構造が必要です。通常のChromiumとは異なります。

### 1. Playwrightのブラウザリポジトリからダウンロード

Playwrightのブラウザは以下のリポジトリからダウンロードできます：

**Chromium (macOS用):**
- リポジトリ: https://github.com/microsoft/playwright
- ブラウザのダウンロードURLはバージョンによって異なります

### 2. 現在のPlaywrightバージョンを確認

```bash
python3 -m playwright --version
```

### 3. ブラウザのダウンロードURLを確認

Playwrightのバージョンに応じて、ブラウザのダウンロードURLが決まります。

**例：Playwright 1.40.0の場合**
- Chromium 1200: `https://playwright.azureedge.net/builds/chromium/1200/chromium-mac-x64.zip`

### 4. ダウンロードと配置手順

1. **ブラウザのZIPファイルをダウンロード**
   - 上記のURLからZIPファイルをダウンロード

2. **保存先ディレクトリを作成**
   ```bash
   mkdir -p ~/Library/Caches/ms-playwright/chromium-1200/chrome-mac-x64
   ```

3. **ZIPファイルを解凍**
   ```bash
   cd ~/Library/Caches/ms-playwright/chromium-1200/chrome-mac-x64
   unzip ~/Downloads/chromium-mac-x64.zip
   ```

4. **実行権限を付与**
   ```bash
   chmod +x "Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
   ```

## ⚠️ 注意事項

1. **バージョンの一致**: Playwrightのバージョンとブラウザのバージョンが一致している必要があります
2. **パスの正確性**: ディレクトリ構造とファイル名が正確である必要があります
3. **権限**: 実行ファイルに実行権限が必要です

## 🔍 インストール確認方法

インストールが成功したか確認するには、以下のPythonスクリプトを実行してください：

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

## 📝 最も簡単な方法（推奨）

**ターミナルで以下のコマンドを1つ実行するだけ：**

```bash
python3 -m playwright install chromium
```

このコマンドが最も確実で簡単です。手動ダウンロードは複雑で、バージョンの不一致などの問題が発生する可能性があります。

## 🔗 参考リンク

- Playwright公式ドキュメント: https://playwright.dev/python/docs/browsers
- Playwright GitHub: https://github.com/microsoft/playwright
