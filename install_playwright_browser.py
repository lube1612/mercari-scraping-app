"""
Playwrightブラウザのインストールスクリプト

このスクリプトを実行すると、Playwrightのブラウザ（Chromium）が自動的にインストールされます。

【使い方】
1. Cursorでこのファイル（install_playwright_browser.py）を開く
2. 右上の「実行」ボタンをクリックするか、F5キーを押す
3. インストールが完了するまで待つ（数分かかることがあります）
"""

import subprocess
import sys
from pathlib import Path

def install_playwright_browser():
    """
    Playwrightのブラウザをインストール
    """
    print("=" * 60)
    print("Playwrightブラウザのインストールを開始します")
    print("=" * 60)
    print()
    
    try:
        # playwright install chromium を実行
        print("Chromiumブラウザをダウンロード中...")
        print("（これには数分かかることがあります）")
        print()
        
        # まず playwright install を実行（依存関係のインストール）
        print("1. Playwrightの依存関係をインストール中...")
        result1 = subprocess.run(
            [sys.executable, "-m", "playwright", "install"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result1.stdout:
            print(result1.stdout)
        if result1.stderr and "Installed" not in result1.stderr:
            print(result1.stderr)
        
        print()
        print("2. Chromiumブラウザをインストール中...")
        # すべてのブラウザをインストール（確実にインストールするため）
        result = subprocess.run(
            [sys.executable, "-m", "playwright", "install"],
            capture_output=True,
            text=True,
            check=False
        )
        
        # 出力を表示
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        print()
        print("3. Chromiumのみを再インストール中...")
        result2 = subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            capture_output=True,
            text=True,
            check=False
        )
        
        # 出力を表示
        if result2.stdout:
            print(result2.stdout)
        if result2.stderr:
            print(result2.stderr)
        
        result = result2  # 最後の結果を使用
        
        # 出力を表示
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            # エラーでも実際にはインストールされている場合があるので、すべて表示
            print(result.stderr)
        
        # インストールの確認
        print()
        print("4. インストールを確認中...")
        try:
            from playwright.sync_api import sync_playwright
            p = sync_playwright().start()
            browser = p.chromium.launch(headless=True)
            browser.close()
            p.stop()
            print("✓ ブラウザの起動に成功しました！")
            install_success = True
        except Exception as e:
            print(f"✗ ブラウザの起動に失敗しました: {e}")
            install_success = False
        
        if result.returncode == 0 or install_success:
            print()
            print("=" * 60)
            print("✓ インストールが完了しました！")
            print("=" * 60)
            print()
            print("次に、scrape_crowdworks.py を実行できます。")
            return True
        else:
            print()
            print("=" * 60)
            print("✗ インストール中にエラーが発生しました")
            print("=" * 60)
            print()
            print("エラー内容:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print()
        print("=" * 60)
        print("✗ エラーが発生しました")
        print("=" * 60)
        print(f"エラー内容: {e}")
        print()
        print("手動でインストールする場合は、以下のコマンドを実行してください:")
        print("  python3 -m playwright install chromium")
        return False


if __name__ == "__main__":
    install_playwright_browser()
