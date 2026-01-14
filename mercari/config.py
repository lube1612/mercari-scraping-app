"""
メルカリスクレイピング設定ファイル

ポケモンカードの検索に特化した設定
"""

# 検索キーワード（複数指定可能）
SEARCH_KEYWORDS = [
    "ポケモンカード",
    "ポケカ",
    "ポケモンカードゲーム",
    "ポケモンカード 拡張パック",
]

# 検索URLのテンプレート
SEARCH_URL_TEMPLATE = "https://www.mercari.com/jp/search/?keyword={keyword}"

# スクレイピング設定
SCRAPING_CONFIG = {
    "max_items_per_keyword": 10,  # キーワードごとの最大取得件数
    "wait_time": 3000,            # ページ読み込み待機時間（ミリ秒）
    "delay_between_items": 3,    # 商品間の待機時間（秒）
    "headless": False,            # ヘッドレスモード（False=ブラウザを表示）
}

# 出力設定
OUTPUT_CONFIG = {
    "output_dir": "output",
    "filename_template": "mercari_pokemon_{keyword}_{timestamp}.csv",
    "encoding": "utf-8-sig",     # Excelで開きやすい形式
}

# ポケモンカード特有の設定
POKEMON_CARD_CONFIG = {
    "extract_rarity": True,       # レアリティを抽出するか
    "extract_set_name": True,     # セット名を抽出するか
    "extract_card_number": True,  # カード番号を抽出するか
}
