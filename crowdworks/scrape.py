"""
CrowdWorksスクレイピング実行スクリプト

【使用方法】
python3 crowdworks/scrape.py
"""

import sys
from pathlib import Path
import time

# 親ディレクトリのパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from crowdworks.scraper import CrowdWorksScraper
from common.utils import save_to_csv


def main():
    """
    メイン処理
    """
    # スクレイピング対象URL
    target_url = "https://crowdworks.jp/public/jobs/group/ec"
    
    # 取得する案件数
    max_jobs = 1  # 1件取得して確認

    print("=" * 60)
    print("CrowdWorks案件情報スクレイピング開始")
    print("=" * 60)
    print(f"対象URL: {target_url}")
    print(f"取得件数: {max_jobs}件")
    print()

    jobs_data = []

    try:
        with CrowdWorksScraper(headless=False) as scraper:
            # 案件一覧ページから案件リンクを取得
            job_links = scraper.scrape_list(target_url)

            if not job_links:
                print("案件リンクが見つかりませんでした。")
                return

            print(f"\n{len(job_links)} 件の案件リンクを発見しました。")
            print(f"{min(max_jobs, len(job_links))} 件の案件情報を取得します...\n")

            # 案件情報を取得
            for i, job_url in enumerate(job_links[:max_jobs]):
                print(f"\n{'='*60}")
                print(f"案件 {i+1}/{min(max_jobs, len(job_links))} を取得中...")
                print('='*60)
                
                job_info = scraper.scrape_detail(job_url)

                if job_info:
                    jobs_data.append(job_info)
                    print(f"\n✓ 取得完了: {job_info.get('title', 'タイトル不明')[:50]}")

            # 結果を表示・保存
            if jobs_data:
                output_path = Path(__file__).parent / "output" / "crowdworks_jobs.csv"
                save_to_csv(jobs_data, str(output_path))
                
                print("\n" + "=" * 60)
                print("取得結果")
                print("=" * 60)
                print(f"取得件数: {len(jobs_data)}件")
                print(f"CSVファイル: {output_path}")
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
