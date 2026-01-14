# CrowdWorksスクレイピングツール 使い方ガイド

## 📋 目次
1. [CSVファイルの確認方法](#csvファイルの確認方法)
2. [スクリプトの拡張方法](#スクリプトの拡張方法)
3. [データ分析の方法](#データ分析の方法)
4. [定期実行の設定](#定期実行の設定)
5. [トラブルシューティング](#トラブルシューティング)

---

## 📊 CSVファイルの確認方法

### Excelで開く
1. `crowdworks_jobs.csv` をダブルクリック
2. Excelが自動で開きます
3. データが正しく表示されているか確認

### Googleスプレッドシートで開く
1. Googleドライブに `crowdworks_jobs.csv` をアップロード
2. 右クリック → 「Googleスプレッドシートで開く」
3. データを分析・共有できます

### 取得できるデータ項目
- **title**: 案件タイトル
- **description**: 案件の詳細説明
- **price**: 報酬・予算
- **deadline**: 応募期限
- **posted_date**: 掲載日
- **applicants**: 応募者数
- **category**: カテゴリー
- **client_info**: クライアント情報
- **url**: 案件URL
- **skills**: 必要なスキル
- **status**: ステータス

---

## 🔧 スクリプトの拡張方法

### 1. 複数件の案件を取得する

`scrape_crowdworks.py` の `main()` 関数を修正：

```python
# 現在は1件のみ取得
job_info = scraper.scrape_job_detail(job_links[0])

# 複数件取得する場合（例：10件）
max_jobs = 10
for i, job_url in enumerate(job_links[:max_jobs]):
    print(f"\n案件 {i+1}/{max_jobs} を取得中...")
    job_info = scraper.scrape_job_detail(job_url)
    if job_info:
        jobs_data.append(job_info)
```

### 2. 特定の条件でフィルタリング

価格やカテゴリーでフィルタリングする例：

```python
# 価格が10,000円以上の案件のみ取得
if job_info and "price" in job_info:
    price_text = job_info["price"]
    # 価格を数値に変換して比較
    if "10000" in price_text or "1万" in price_text:
        jobs_data.append(job_info)
```

### 3. 別のURLをスクレイピングする

`scrape_crowdworks.py` の `main()` 関数でURLを変更：

```python
# 例：Web制作カテゴリー
target_url = "https://crowdworks.jp/public/jobs/group/web"

# 例：データ入力カテゴリー
target_url = "https://crowdworks.jp/public/jobs/group/data-entry"
```

### 4. ヘッドレスモードで実行（ブラウザを表示しない）

```python
# headless=True に変更
with CrowdWorksScraperE2E(headless=True) as scraper:
```

---

## 📈 データ分析の方法

### Pythonでデータ分析

新しいファイル `analyze_jobs.py` を作成：

```python
import pandas as pd
import csv

# CSVファイルを読み込む
df = pd.read_csv('crowdworks_jobs.csv')

# 基本統計
print("=== 基本統計 ===")
print(f"総案件数: {len(df)}")
print(f"平均応募者数: {df['applicants'].mean() if 'applicants' in df.columns else 'N/A'}")

# カテゴリー別の集計
if 'category' in df.columns:
    print("\n=== カテゴリー別案件数 ===")
    print(df['category'].value_counts())

# 価格帯の分析
if 'price' in df.columns:
    print("\n=== 価格情報 ===")
    print(df['price'].value_counts())
```

### Excelでピボットテーブルを作成

1. ExcelでCSVファイルを開く
2. 「挿入」→「ピボットテーブル」
3. カテゴリーや価格帯で集計

---

## ⏰ 定期実行の設定

### Macの場合（cronを使用）

1. ターミナルを開く
2. 以下を実行：
```bash
crontab -e
```

3. 以下を追加（毎日午前9時に実行する例）：
```
0 9 * * * cd /Users/shimadaeiji/Documents/Cursor/e2e && /usr/bin/python3 scrape_crowdworks.py
```

### Windowsの場合（タスクスケジューラ）

1. 「タスクスケジューラ」を開く
2. 「基本タスクの作成」を選択
3. トリガーを設定（例：毎日）
4. 操作で「プログラムの開始」を選択
5. プログラム: `python3`
6. 引数: `scrape_crowdworks.py`
7. 開始場所: `/Users/shimadaeiji/Documents/Cursor/e2e`

---

## 🎯 実用的な活用例

### 例1: 高単価案件の監視
- 10,000円以上の案件を自動で取得
- 毎日実行して新しい案件をチェック

### 例2: 特定カテゴリーの案件追跡
- 自分の得意分野のカテゴリーのみ取得
- 応募者数が少ない案件を優先的に確認

### 例3: クライアント評価の分析
- クライアント情報を集計
- 評価の高いクライアントの案件を優先

---

## 🛠️ トラブルシューティング

### CSVファイルが正しく開けない場合
- Excelで開く際に「データ」→「テキストファイル」から開く
- 文字コードを「UTF-8」に設定

### スクレイピングが失敗する場合
- インターネット接続を確認
- ブラウザが正しくインストールされているか確認
- `install_playwright_browser.py` を再実行

### データが取得できない場合
- CrowdWorksのサイト構造が変更された可能性
- セレクタを確認・修正する必要がある

---

## 📝 次のステップ

1. ✅ CSVファイルの確認
2. ⬜ 複数件の案件を取得するように拡張
3. ⬜ データ分析スクリプトを作成
4. ⬜ 定期実行を設定
5. ⬜ フィルタリング機能を追加

---

## 💡 ヒント

- スクレイピングは適度な間隔を空けて実行してください
- 取得したデータは定期的にバックアップを取ることをおすすめします
- 大量のデータを取得する場合は、サーバーの負荷を考慮してください
