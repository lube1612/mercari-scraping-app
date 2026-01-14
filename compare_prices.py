"""
Amazonとメルカリの価格を比較して、Amazonより安いポケモンカードを5つ取得するスクリプト
"""

import sys
from pathlib import Path
import time
import re

# 親ディレクトリのパスを追加
sys.path.insert(0, str(Path(__file__).parent))

from mercari.scraper import MercariScraper
from amazon.scraper import AmazonScraper
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


def compare_and_select_cheaper_items(mercari_items: list, amazon_items: list, max_items: int = 5) -> list:
    """
    Amazonとメルカリの価格を比較して、Amazonより安い商品を選ぶ
    
    Args:
        mercari_items: メルカリの商品リスト
        amazon_items: Amazonの商品リスト
        max_items: 取得する最大件数
    
    Returns:
        list: Amazonより安い商品リスト
    """
    cheaper_items = []
    
    # タイトルでマッチング（簡易版）
    for mercari_item in mercari_items:
        mercari_title = mercari_item.get('title', '').lower()
        mercari_price = extract_price(mercari_item.get('price', ''))
        
        if mercari_price == float('inf'):
            continue
        
        # Amazonの商品とタイトルを比較（キーワードマッチング）
        best_match = None
        best_price_diff = float('inf')
        
        for amazon_item in amazon_items:
            amazon_title = amazon_item.get('title', '').lower()
            amazon_price = extract_price(amazon_item.get('price', ''))
            
            if amazon_price == float('inf'):
                continue
            
            # タイトルに共通のキーワードがあるかチェック
            mercari_keywords = set(mercari_title.split())
            amazon_keywords = set(amazon_title.split())
            common_keywords = mercari_keywords & amazon_keywords
            
            # 共通キーワードが2つ以上ある場合、マッチとみなす
            if len(common_keywords) >= 2:
                price_diff = amazon_price - mercari_price
                if price_diff > 0 and price_diff < best_price_diff:
                    best_match = amazon_item
                    best_price_diff = price_diff
        
        # Amazonより安い場合
        if best_match:
            amazon_price = extract_price(best_match.get('price', ''))
            if mercari_price < amazon_price:
                item = mercari_item.copy()
                item['amazon_price'] = best_match.get('price', '')
                item['amazon_url'] = best_match.get('url', '')
                item['price_difference'] = f"¥{int(amazon_price - mercari_price)}"
                cheaper_items.append(item)
    
    # 価格差でソート（大きい順）
    cheaper_items.sort(key=lambda x: extract_price(x.get('price_difference', '¥0')), reverse=True)
    
    return cheaper_items[:max_items]


def main():
    """
    メイン処理
    """
    search_keyword = "ポケモンカード"
    
    print("=" * 60)
    print("Amazonとメルカリの価格比較スクレイピング")
    print("=" * 60)
    print(f"検索キーワード: {search_keyword}")
    print(f"取得件数: 5件（Amazonより安い商品）")
    print()
    
    mercari_items = []
    amazon_items = []
    
    try:
        # 環境変数を設定
        import os
        if os.path.exists(os.path.expanduser('~/playwright-browsers')):
            os.environ['PLAYWRIGHT_BROWSERS_PATH'] = os.path.expanduser('~/playwright-browsers')
        
        # メルカリから商品情報を取得
        print("=" * 60)
        print("1. メルカリから商品情報を取得中...")
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
                            if title and len(title) > 5:
                                mercari_items.append(item_info)
                                print(f"✓ 取得完了: {title[:50]}")
                    except Exception as e:
                        print(f"⚠️  エラー: {e}")
                    
                    time.sleep(2)
        
        # Amazonから商品情報を取得
        print("\n" + "=" * 60)
        print("2. Amazonから商品情報を取得中...")
        print("=" * 60)
        amazon_url = f"https://www.amazon.co.jp/s?k={search_keyword}"
        
        with AmazonScraper(headless=False) as amazon_scraper:
            item_links = amazon_scraper.scrape_list(amazon_url)
            
            if item_links:
                print(f"\n{len(item_links)} 件の商品リンクを発見しました。")
                print("10件の商品情報を取得します...\n")
                
                for i, item_url in enumerate(item_links[:10]):  # 最大10件
                    print(f"\n{'='*60}")
                    print(f"Amazon商品 {i+1}/10 を取得中...")
                    print('='*60)
                    
                    try:
                        item_info = amazon_scraper.scrape_detail(item_url)
                        if item_info:
                            title = item_info.get('title', '')
                            price = item_info.get('price', '')
                            if title and len(title) > 5 and price:
                                amazon_items.append(item_info)
                                print(f"✓ 取得完了: {title[:50]} ({price})")
                    except Exception as e:
                        print(f"⚠️  エラー: {e}")
                    
                    time.sleep(2)
        
        # 価格を比較して、Amazonより安い商品を選ぶ
        print("\n" + "=" * 60)
        print("3. 価格を比較中...")
        print("=" * 60)
        
        cheaper_items = compare_and_select_cheaper_items(mercari_items, amazon_items, max_items=5)
        
        # 結果を表示・保存
        if cheaper_items:
            output_path = Path(__file__).parent / "mercari" / "output" / "cheaper_items.csv"
            save_to_csv(cheaper_items, str(output_path))
            
            print("\n" + "=" * 60)
            print("取得結果")
            print("=" * 60)
            print(f"取得件数: {len(cheaper_items)}件")
            print(f"CSVファイル: {output_path}")
            print("\nAmazonより安い商品:")
            for i, item in enumerate(cheaper_items, 1):
                title = item.get('title', 'タイトル不明')
                price = item.get('price', '価格不明')
                amazon_price = item.get('amazon_price', '価格不明')
                price_diff = item.get('price_difference', '')
                print(f"  {i}. {title[:50]}...")
                print(f"     メルカリ: {price} | Amazon: {amazon_price} | 差額: {price_diff}")
        else:
            print("\n⚠️  Amazonより安い商品が見つかりませんでした。")
    
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
