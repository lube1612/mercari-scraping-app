"""
メルカリのみで価格分析を行うスクリプト（安全版）

Amazonスクレイパーを使用せず、メルカリ内での価格比較を行います。
"""

import sys
from pathlib import Path
import time
import re

# 親ディレクトリのパスを追加
sys.path.insert(0, str(Path(__file__).parent))

from mercari.scraper import MercariScraper
from common.utils import save_to_csv


def extract_price(price_str: str) -> float:
    """
    価格文字列から数値を抽出
    
    Args:
        price_str: 価格文字列（例: "¥400", "¥1,222"）
    
    Returns:
        float: 価格の数値
    """
    if not price_str:
        return float('inf')
    
    # 数字とカンマを抽出
    price_match = re.search(r'[\d,]+', price_str.replace(',', ''))
    if price_match:
        try:
            return float(price_match.group().replace(',', ''))
        except:
            return float('inf')
    
    return float('inf')


def analyze_mercari_prices(items: list, max_items: int = 5) -> list:
    """
    メルカリの商品を価格順にソートして、安い順に選ぶ
    
    Args:
        items: メルカリの商品リスト
        max_items: 取得する最大件数
    
    Returns:
        list: 価格が安い順の商品リスト
    """
    # 価格でソート（安い順）
    sorted_items = sorted(items, key=lambda x: extract_price(x.get('price', '')))
    
    return sorted_items[:max_items]


def main():
    """
    メイン処理（メルカリのみで価格分析）
    """
    search_keyword = "ポケモンカード"
    
    print("=" * 60)
    print("メルカリ ポケモンカード価格分析スクレイピング")
    print("=" * 60)
    print(f"検索キーワード: {search_keyword}")
    print(f"取得件数: 5件（価格が安い順）")
    print()
    print("⚠️  注意: Amazonスクレイパーは使用しません（規約上のリスク回避）")
    print("   メルカリ内での価格分析のみを行います。")
    print()
    
    mercari_items = []
    
    try:
        # 環境変数を設定
        import os
        if os.path.exists(os.path.expanduser('~/playwright-browsers')):
            os.environ['PLAYWRIGHT_BROWSERS_PATH'] = os.path.expanduser('~/playwright-browsers')
        
        # メルカリから商品情報を取得
        print("=" * 60)
        print("メルカリから商品情報を取得中...")
        print("=" * 60)
        mercari_url = f"https://www.mercari.com/jp/search/?keyword={search_keyword}"
        
        with MercariScraper(headless=False) as mercari_scraper:
            item_links = mercari_scraper.scrape_list(mercari_url)
            
            if item_links:
                print(f"\n{len(item_links)} 件の商品リンクを発見しました。")
                print("10件の商品情報を取得します...\n")
                
                for i, item_url in enumerate(item_links[:10]):  # 最大10件
                    print(f"\n{'='*60}")
                    print(f"メルカリ商品 {i+1}/10 を取得中...")
                    print('='*60)
                    
                    try:
                        item_info = mercari_scraper.scrape_detail(item_url)
                        if item_info:
                            title = item_info.get('title', '')
                            price = item_info.get('price', '')
                            if title and len(title) > 5 and price:
                                mercari_items.append(item_info)
                                print(f"✓ 取得完了: {title[:50]} ({price})")
                    except Exception as e:
                        print(f"⚠️  エラー: {e}")
                    
                    time.sleep(2)
        
        # 価格でソートして、安い順に5件選ぶ
        print("\n" + "=" * 60)
        print("価格を分析中...")
        print("=" * 60)
        
        cheaper_items = analyze_mercari_prices(mercari_items, max_items=5)
        
        # 結果を表示・保存
        if cheaper_items:
            output_path = Path(__file__).parent / "mercari" / "output" / "cheap_items.csv"
            save_to_csv(cheaper_items, str(output_path))
            
            print("\n" + "=" * 60)
            print("取得結果")
            print("=" * 60)
            print(f"取得件数: {len(cheaper_items)}件")
            print(f"CSVファイル: {output_path}")
            print("\n価格が安い順の商品:")
            for i, item in enumerate(cheaper_items, 1):
                title = item.get('title', 'タイトル不明')
                price = item.get('price', '価格不明')
                print(f"  {i}. {title[:50]}... (価格: {price})")
        else:
            print("\n⚠️  商品が見つかりませんでした。")
    
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
