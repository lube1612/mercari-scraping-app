"""
CrowdWorks案件データ分析スクリプト

【使用方法】
python3 analyze_jobs.py

【処理内容】
1. CSVファイルを読み込む
2. データを分析・集計
3. 結果を表示
"""

import csv
from pathlib import Path
from collections import Counter
import re


def read_csv(file_path: str) -> list:
    """
    CSVファイルを読み込む
    
    Input:
        file_path: CSVファイルのパス
    
    Output:
        list: 案件データのリスト
    """
    jobs = []
    csv_path = Path(file_path)
    
    if not csv_path.exists():
        print(f"エラー: {file_path} が見つかりません。")
        return jobs
    
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                jobs.append(row)
        print(f"✓ {len(jobs)}件のデータを読み込みました。")
    except Exception as e:
        print(f"エラー: CSVファイルの読み込みに失敗しました: {e}")
    
    return jobs


def extract_price_number(price_str: str) -> float:
    """
    価格文字列から数値を抽出
    
    Input:
        price_str: 価格文字列（例: "10000円", "1万円"）
    
    Output:
        float: 価格の数値（円単位）
    """
    if not price_str:
        return 0.0
    
    # 数字と「万」「円」を抽出
    match = re.search(r'([0-9,]+)', price_str.replace(',', ''))
    if match:
        number = float(match.group(1))
        if '万' in price_str:
            number *= 10000
        return number
    return 0.0


def analyze_jobs(jobs: list):
    """
    案件データを分析
    
    Input:
        jobs: 案件データのリスト
    """
    if not jobs:
        print("分析するデータがありません。")
        return
    
    print("\n" + "=" * 60)
    print("データ分析結果")
    print("=" * 60)
    
    # 基本統計
    print("\n【基本統計】")
    print(f"総案件数: {len(jobs)}件")
    
    # カテゴリー別集計
    categories = [job.get('category', '不明') for job in jobs if job.get('category')]
    if categories:
        print("\n【カテゴリー別案件数】")
        category_counts = Counter(categories)
        for category, count in category_counts.most_common():
            print(f"  {category}: {count}件")
    
    # 価格分析
    prices = [extract_price_number(job.get('price', '')) for job in jobs]
    prices = [p for p in prices if p > 0]
    
    if prices:
        print("\n【価格分析】")
        print(f"  平均価格: {sum(prices)/len(prices):,.0f}円")
        print(f"  最高価格: {max(prices):,.0f}円")
        print(f"  最低価格: {min(prices):,.0f}円")
        
        # 価格帯別集計
        price_ranges = {
            "5,000円未満": 0,
            "5,000円〜10,000円": 0,
            "10,000円〜50,000円": 0,
            "50,000円以上": 0
        }
        
        for price in prices:
            if price < 5000:
                price_ranges["5,000円未満"] += 1
            elif price < 10000:
                price_ranges["5,000円〜10,000円"] += 1
            elif price < 50000:
                price_ranges["10,000円〜50,000円"] += 1
            else:
                price_ranges["50,000円以上"] += 1
        
        print("\n【価格帯別案件数】")
        for range_name, count in price_ranges.items():
            if count > 0:
                print(f"  {range_name}: {count}件")
    
    # 応募者数分析
    applicants_list = []
    for job in jobs:
        applicants_str = job.get('applicants', '')
        if applicants_str:
            match = re.search(r'(\d+)', applicants_str)
            if match:
                applicants_list.append(int(match.group(1)))
    
    if applicants_list:
        print("\n【応募者数分析】")
        print(f"  平均応募者数: {sum(applicants_list)/len(applicants_list):.1f}人")
        print(f"  最多応募者数: {max(applicants_list)}人")
        print(f"  最少応募者数: {min(applicants_list)}人")
    
    # タイトル分析（キーワード抽出）
    print("\n【よく使われるキーワード】")
    all_titles = ' '.join([job.get('title', '') for job in jobs])
    # 簡単なキーワード抽出（実際にはもっと高度な分析が可能）
    keywords = ['制作', '開発', '作成', 'リサーチ', 'デザイン', '運用', '分析']
    keyword_counts = {}
    for keyword in keywords:
        count = all_titles.count(keyword)
        if count > 0:
            keyword_counts[keyword] = count
    
    if keyword_counts:
        for keyword, count in sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {keyword}: {count}回")
    
    print("\n" + "=" * 60)


def main():
    """
    メイン処理
    """
    # 分析するCSVファイル（複数のファイルを指定可能）
    csv_files = [
        "crowdworks_jobs.csv",
        "crowdworks_jobs_multiple.csv"
    ]
    
    print("=" * 60)
    print("CrowdWorks案件データ分析")
    print("=" * 60)
    
    # 存在するCSVファイルを探す
    found_files = []
    for csv_file in csv_files:
        if Path(csv_file).exists():
            found_files.append(csv_file)
    
    if not found_files:
        print("\nエラー: 分析するCSVファイルが見つかりません。")
        print("以下のファイルのいずれかが必要です:")
        for f in csv_files:
            print(f"  - {f}")
        return
    
    # すべてのCSVファイルを読み込んで結合
    all_jobs = []
    for csv_file in found_files:
        print(f"\n読み込み中: {csv_file}")
        jobs = read_csv(csv_file)
        all_jobs.extend(jobs)
    
    # 分析実行
    if all_jobs:
        analyze_jobs(all_jobs)
    else:
        print("\n分析するデータがありません。")


if __name__ == "__main__":
    main()
