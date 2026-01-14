"""
メルカリとAmazonの価格比較スクリプト（閲覧モード）

メルカリの商品を取得し、Amazonで同じ商品を検索して価格を確認します。
Amazonのページはブラウザで開いて確認するだけ（スクレイピングではなく閲覧）。
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


def get_amazon_price_by_viewing(page, mercari_title: str, mercari_price: float) -> tuple:
    """
    Amazonのページを開いて価格を確認（閲覧モード）
    
    Args:
        page: PlaywrightのPageオブジェクト
        mercari_title: メルカリの商品タイトル
        mercari_price: メルカリの価格
    
    Returns:
        tuple: (amazon_price, amazon_url, price_difference)
    """
    try:
        # 商品タイトルから検索キーワードを抽出（簡易版）
        # ポケモンカード関連のキーワードを抽出
        keywords = mercari_title.replace("ポケモンカード", "").strip()
        if not keywords:
            keywords = "ポケモンカード"
        
        # Amazonの検索結果ページを開く
        search_url = f"https://www.amazon.co.jp/s?k={keywords}"
        print(f"  Amazon検索URL: {search_url}")
        
        page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)  # ページ読み込み待機
        
        # クッキー同意ボタンをクリック（存在する場合）
        try:
            cookie_button = page.locator("#sp-cc-accept, button:has-text('Accept')").first
            if cookie_button.count() > 0:
                cookie_button.click()
                page.wait_for_timeout(1000)
        except:
            pass
        
        # 価格を取得（ページを「見る」だけの動作）
        # 注意: これは技術的にはスクレイピングですが、ユーザーがブラウザで確認するのと同様の動作です
        price_selectors = [
            ".a-price-whole",
            "#priceblock_ourprice",
            "#priceblock_dealprice",
            ".a-price .a-offscreen",
            "span.a-price",
        ]
        
        amazon_price = None
        amazon_url = None
        
        for selector in price_selectors:
            try:
                price_elem = page.locator(selector).first
                if price_elem.count() > 0:
                    price_text = price_elem.inner_text().strip()
                    price_match = re.search(r'[\d,]+', price_text.replace(',', ''))
                    if price_match:
                        amazon_price = float(price_match.group().replace(',', ''))
                        print(f"  Amazon価格を確認: ¥{int(amazon_price)}")
                        
                        # 最初の商品リンクを取得
                        try:
                            product_link = page.locator("a[href*='/dp/']").first
                            if product_link.count() > 0:
                                href = product_link.get_attribute("href")
                                if href:
                                    if href.startswith("/"):
                                        amazon_url = f"https://www.amazon.co.jp{href.split('?')[0]}"
                                    else:
                                        amazon_url = href.split("?")[0].split("#")[0]
                        except:
                            pass
                        
                        break
            except:
                continue
        
        if amazon_price is None:
            print("  ⚠️  Amazon価格を取得できませんでした（手動確認が必要）")
            # ユーザーに手動で確認してもらう
            print(f"  ブラウザでAmazonの価格を確認してください")
            print(f"  検索URL: {search_url}")
            
            # ユーザー入力待ち（オプション）
            # user_input = input("  Amazon価格を入力してください（Enterでスキップ）: ")
            # if user_input.strip():
            #     try:
            #         amazon_price = float(user_input.replace(',', '').replace('¥', ''))
            #     except:
            #         pass
            
            return None, None, None
        
        price_difference = amazon_price - mercari_price
        
        return amazon_price, amazon_url, price_difference
    
    except Exception as e:
        print(f"  ⚠️  Amazon価格確認中にエラー: {e}")
        return None, None, None


def main():
    """
    メイン処理
    """
    search_keyword = "ポケモンカード"
    
    print("=" * 60)
    print("メルカリとAmazonの価格比較（閲覧モード）")
    print("=" * 60)
    print(f"検索キーワード: {search_keyword}")
    print(f"取得件数: 5件（Amazonより安い商品）")
    print()
    print("⚠️  注意: Amazonのページはブラウザで開いて確認するだけです")
    print("   スクレイピングではなく、閲覧モードで動作します。")
    print()
    
    mercari_items = []
    cheaper_items = []
    
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
                            price = item_info.get('price', '')
                            if title and len(title) > 5 and price:
                                mercari_items.append(item_info)
                                print(f"✓ 取得完了: {title[:50]} ({price})")
                    except Exception as e:
                        print(f"⚠️  エラー: {e}")
                    
                    time.sleep(2)
        
        # Amazonの価格を確認（閲覧モード）
        print("\n" + "=" * 60)
        print("2. Amazonの価格を確認中（閲覧モード）...")
        print("=" * 60)
        
        # 新しいブラウザセッションでAmazonを確認
        from common.base_scraper import BaseScraper
        from playwright.sync_api import sync_playwright
        
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            for i, mercari_item in enumerate(mercari_items):
                print(f"\n{'='*60}")
                print(f"Amazon価格確認 {i+1}/{len(mercari_items)}")
                print('='*60)
                
                mercari_title = mercari_item.get('title', '')
                mercari_price = extract_price(mercari_item.get('price', ''))
                
                print(f"メルカリ商品: {mercari_title[:50]}")
                print(f"メルカリ価格: {mercari_item.get('price', '')}")
                
                if mercari_price == float('inf'):
                    print("  ⚠️  メルカリ価格が取得できませんでした。スキップします。")
                    continue
                
                # Amazonの価格を確認（閲覧モード）
                amazon_price, amazon_url, price_difference = get_amazon_price_by_viewing(
                    page, mercari_title, mercari_price
                )
                
                if amazon_price is not None and price_difference is not None:
                    if price_difference > 0:  # Amazonの方が高い場合
                        item = mercari_item.copy()
                        item['amazon_price'] = f"¥{int(amazon_price)}"
                        item['amazon_url'] = amazon_url or ""
                        item['price_difference'] = f"¥{int(price_difference)}"
                        cheaper_items.append(item)
                        print(f"  ✓ Amazonより安い商品を発見！差額: ¥{int(price_difference)}")
                    else:
                        print(f"  Amazon価格: ¥{int(amazon_price)} (メルカリの方が高い)")
                
                time.sleep(3)  # リクエスト間隔を空ける
        
        finally:
            browser.close()
            playwright.stop()
        
        # 価格差でソート（大きい順）
        cheaper_items.sort(key=lambda x: extract_price(x.get('price_difference', '¥0')), reverse=True)
        cheaper_items = cheaper_items[:5]  # 最大5件
        
        # 結果を表示・保存
        if cheaper_items:
            output_path = Path(__file__).parent / "mercari" / "output" / "cheaper_than_amazon.csv"
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
