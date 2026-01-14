"""
設定ファイルの例

このファイルは設定値を管理するためのテンプレートです。
必要に応じて編集してください。
"""

# テスト設定
TEST_OUTPUT_DIR = "./test_results"
BASELINE_DIR = "./baseline"

# ブラウザ設定
HEADLESS_MODE = True
BROWSER_TYPE = "chromium"  # "chromium", "firefox", "webkit"

# ビューポート設定
DEFAULT_VIEWPORT = {
    "width": 1280,
    "height": 720
}

# 待機時間設定（ミリ秒）
DEFAULT_WAIT_TIME = 2000

# 差分許容率（%）
DIFFERENCE_THRESHOLD = 1.0
