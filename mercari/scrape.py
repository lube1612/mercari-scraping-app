"""
メルカリスクレイピング実行スクリプト

【使用方法】
python3 mercari/scrape.py

【注意】
メルカリのサイト構造に合わせて、mercari/scraper.py を実装してください。
"""

import sys
import os
from pathlib import Path
import time

# 親ディレクトリのパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent))

# Playwrightブラウザのパスを設定（環境変数が設定されている場合）
if 'PLAYWRIGHT_BROWSERS_PATH' in os.environ:
    # 既に設定されている場合はそのまま使用
    pass
elif os.path.exists(os.path.expanduser('~/playwright-browsers')):
    # playwright-browsersディレクトリが存在する場合は設定
    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = os.path.expanduser('~/playwright-browsers')

from mercari.scraper import MercariScraper
from common.utils import save_to_csv


def main():
    """
    メイン処理
    """
    # スクレイピング対象URL（ポケモンカードの検索結果ページ）
    # ポケモンカードで検索
    target_url = "https://www.mercari.com/jp/search/?keyword=ポケモンカード"  # ポケモンカード検索
    
    # 取得する商品数
    max_items = 2  # 2件取得

    print("=" * 60)
    print("メルカリ ポケモンカード情報スクレイピング開始")
    print("=" * 60)
    print(f"対象URL: {target_url}")
    print(f"取得件数: {max_items}件")
    print()

    items_data = []

    try:
        # 通常モードで実行（ブラウザを表示）
        with MercariScraper(headless=False) as scraper:
            # 商品一覧ページから商品リンクを取得
            item_links = scraper.scrape_list(target_url)

            if not item_links:
                print("商品リンクが見つかりませんでした。")
                print("mercari/scraper.py の scrape_list メソッドを実装してください。")
                return

            print(f"\n{len(item_links)} 件の商品リンクを発見しました。")
            print(f"{min(max_items, len(item_links))} 件の商品情報を取得します...\n")

            # 商品情報を取得（404エラーの場合は次の商品を試す）
            successful_count = 0
            attempt_count = 0
            max_attempts = max_items * 3  # 最大試行回数（404エラーを考慮）
            
            for i, item_url in enumerate(item_links):
                if successful_count >= max_items:
                    break
                
                attempt_count += 1
                if attempt_count > max_attempts:
                    print(f"\n⚠️  最大試行回数に達しました。{successful_count}件のデータを取得しました。")
                    break
                
                print(f"\n{'='*60}")
                print(f"商品 {successful_count + 1}/{max_items} を取得中... (試行 {attempt_count})")
                print('='*60)
                
                try:
                    item_info = scraper.scrape_detail(item_url)
                except Exception as e:
                    print(f"\n⚠️  エラーが発生しました: {e}")
                    item_info = None

                if item_info:
                    # タイトルがクッキーメッセージでないか確認
                    title = item_info.get('title', '')
                    if title and "cookie" not in title.lower() and "privacy" not in title.lower() and len(title) > 5:
                        items_data.append(item_info)
                        successful_count += 1
                        print(f"\n✓ 取得完了: {item_info.get('title', 'タイトル不明')[:50]}")
                    else:
                        print(f"\n⚠️  商品情報が正しく取得できませんでした（タイトル: {title[:50]}）")
                else:
                    print(f"\n⚠️  商品情報の取得に失敗しました（404エラー、CAPTCHA、またはその他の問題）")

                # 次のリクエスト前に少し待機
                if successful_count < max_items:
                    print("\n3秒待機中...")
                    time.sleep(3)

            # 結果を表示・保存
            if items_data:
                output_path = Path(__file__).parent / "output" / "mercari_items.csv"
                save_to_csv(items_data, str(output_path))
                
                print("\n" + "=" * 60)
                print("取得結果")
                print("=" * 60)
                print(f"取得件数: {len(items_data)}件")
                print(f"CSVファイル: {output_path}")
                print("\n取得した商品のタイトル:")
                for i, item in enumerate(items_data, 1):
                    title = item.get('title', 'タイトル不明')
                    price = item.get('price', '価格不明')
                    print(f"  {i}. {title[:50]}... (価格: {price})")
            else:
                print("\n取得できたデータがありませんでした。")
                print("mercari/scraper.py の scrape_detail メソッドを実装してください。")

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
