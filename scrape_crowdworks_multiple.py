"""
CrowdWorks案件情報スクレイピングスクリプト（複数件取得版）

【使用方法】
python3 scrape_crowdworks_multiple.py

【処理内容】
1. 複数件の案件情報を取得
2. CSVファイルに保存
3. 進捗状況を表示
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional, Any
import csv
import re
import time

# e2eフォルダのモジュールをインポート
from scrape_crowdworks import CrowdWorksScraperE2E


def main():
    """
    メイン処理（複数件取得版）
    """
    # スクレイピング対象URL
    target_url = "https://crowdworks.jp/public/jobs/group/ec"
    
    # 取得する案件数（変更可能）
    max_jobs = 5  # 5件取得する例
    
    print("=" * 60)
    print("CrowdWorks案件情報スクレイピング開始（複数件取得版）")
    print("=" * 60)
    print(f"対象URL: {target_url}")
    print(f"取得件数: {max_jobs}件")
    print(f"e2eモジュールを使用してスクレイピングを実行します")
    print()

    jobs_data = []

    try:
        with CrowdWorksScraperE2E(headless=False) as scraper:
            # 案件一覧ページから案件リンクを取得
            job_links = scraper.scrape_job_list(target_url)

            if not job_links:
                print("案件リンクが見つかりませんでした。")
                return

            print(f"\n{len(job_links)} 件の案件リンクを発見しました。")
            print(f"{min(max_jobs, len(job_links))} 件の案件情報を取得します...\n")

            # 複数件の案件情報を取得
            for i, job_url in enumerate(job_links[:max_jobs]):
                print(f"\n{'='*60}")
                print(f"案件 {i+1}/{min(max_jobs, len(job_links))} を取得中...")
                print(f"URL: {job_url}")
                print('='*60)
                
                job_info = scraper.scrape_job_detail(job_url)

                if job_info:
                    jobs_data.append(job_info)
                    print(f"\n✓ 取得完了: {job_info.get('title', 'タイトル不明')[:50]}")
                else:
                    print(f"\n✗ 取得失敗: {job_url}")

                # 次のリクエスト前に少し待機（サーバー負荷軽減）
                if i < min(max_jobs, len(job_links)) - 1:
                    print("\n3秒待機中...")
                    time.sleep(3)

            # 結果を表示
            print("\n" + "=" * 60)
            print("取得結果")
            print("=" * 60)
            print(f"取得件数: {len(jobs_data)}件")
            
            if jobs_data:
                # CSVに保存
                output_path = "crowdworks_jobs_multiple.csv"
                scraper.save_to_csv(jobs_data, output_path)
                
                print(f"\nCSVファイルを保存しました: {output_path}")
                print("\n取得した案件のタイトル:")
                for i, job in enumerate(jobs_data, 1):
                    title = job.get('title', 'タイトル不明')
                    price = job.get('price', '価格不明')
                    print(f"  {i}. {title[:50]}... (報酬: {price})")
            else:
                print("\n取得できたデータがありませんでした。")

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
