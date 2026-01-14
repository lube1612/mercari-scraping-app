"""
Playwrightブラウザの簡単インストールスクリプト

このスクリプトは、Playwrightの公式インストールコマンドを使用して
ブラウザをインストールします。
"""

import subprocess
import sys
import os

def install_playwright_browser():
    """
    Playwrightのブラウザをインストール
    """
    print("=" * 60)
    print("Playwrightブラウザのインストール")
    print("=" * 60)
    print()
    print("このスクリプトは、Playwrightの公式インストールコマンドを使用します。")
    print("数分かかる場合がありますので、しばらくお待ちください。")
    print()
    
    try:
        # playwright install chromium を実行
        print("Chromiumブラウザをインストール中...")
        print()
        
        # Pythonから直接playwright installを実行
        result = subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            capture_output=False,  # リアルタイムで出力を表示
            text=True
        )
        
        if result.returncode == 0:
            print()
            print("=" * 60)
            print("✓ インストールが完了しました！")
            print("=" * 60)
            print()
            
            # インストール確認
            print("インストールを確認中...")
            try:
                from playwright.sync_api import sync_playwright
                p = sync_playwright().start()
                browser = p.chromium.launch(headless=True)
                print("✓ ブラウザの起動に成功しました！")
                browser.close()
                p.stop()
                
                print()
                print("次のステップ:")
                print("  python3 mercari/scrape.py")
                return True
            except Exception as e:
                print(f"⚠️  警告: ブラウザの起動確認中にエラーが発生しました: {e}")
                print("ただし、インストール自体は成功している可能性があります。")
                print("実際にスクレイピングスクリプトを実行して確認してください。")
                return True
        else:
            print()
            print("=" * 60)
            print("✗ インストール中にエラーが発生しました")
            print("=" * 60)
            print()
            print("手動でインストールする場合は、以下のコマンドを実行してください:")
            print("  python3 -m playwright install chromium")
            return False
            
    except KeyboardInterrupt:
        print()
        print("\nインストールが中断されました。")
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
    success = install_playwright_browser()
    sys.exit(0 if success else 1)
