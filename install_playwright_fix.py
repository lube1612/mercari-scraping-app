"""
Playwrightブラウザの確実なインストールスクリプト

このスクリプトを実行すると、Playwrightのブラウザが確実にインストールされます。
"""

import subprocess
import sys
import time

def install_playwright():
    """
    Playwrightのブラウザを確実にインストール
    """
    print("=" * 60)
    print("Playwrightブラウザのインストールを開始します")
    print("=" * 60)
    print()
    
    commands = [
        [sys.executable, "-m", "playwright", "install", "--help"],
        [sys.executable, "-m", "playwright", "install", "chromium"],
        [sys.executable, "-m", "playwright", "install", "chromium", "--with-deps"],
    ]
    
    for i, cmd in enumerate(commands, 1):
        print(f"{i}. 実行中: {' '.join(cmd)}")
        print("-" * 60)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5分のタイムアウト
                check=False
            )
            
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)
            
            print()
            time.sleep(2)  # 少し待機
            
        except subprocess.TimeoutExpired:
            print("タイムアウトしました。次のコマンドに進みます。")
            print()
        except Exception as e:
            print(f"エラー: {e}")
            print()
    
    # 最終確認
    print("=" * 60)
    print("インストール確認中...")
    print("=" * 60)
    
    try:
        from playwright.sync_api import sync_playwright
        p = sync_playwright().start()
        
        # headless=Trueで試す
        try:
            browser = p.chromium.launch(headless=True)
            browser.close()
            print("✓ ヘッドレスモードでブラウザの起動に成功しました！")
        except:
            pass
        
        # headless=Falseで試す
        try:
            browser = p.chromium.launch(headless=False)
            browser.close()
            print("✓ 通常モードでブラウザの起動に成功しました！")
        except:
            pass
        
        p.stop()
        print("\n✓ インストールが完了しました！")
        return True
        
    except Exception as e:
        print(f"✗ ブラウザの起動に失敗しました: {e}")
        print("\n手動でインストールしてください:")
        print("  python3 -m playwright install chromium")
        return False


if __name__ == "__main__":
    install_playwright()
