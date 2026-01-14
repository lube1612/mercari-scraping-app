# E2Eスクレイピングプロジェクト

メルカリやCrowdWorksなどのサイトから情報をスクレイピングするプロジェクトです。

## 🚀 Streamlitアプリ（Webアプリ）

このプロジェクトには、ブラウザで使えるStreamlitアプリが含まれています。

### 起動方法

```bash
streamlit run streamlit_app.py
```

ブラウザで http://localhost:8501 にアクセスすると、メルカリスクレイピングのWebアプリが使えます。

### 公開方法

Streamlit Cloudで公開する場合は、`GitHub公開手順.md` を参照してください。

---

## 📁 プロジェクト構造

```
e2e/
├── common/                    # 共通モジュール
│   ├── base_scraper.py        # ベーススクレイパークラス
│   └── utils.py               # 共通ユーティリティ
│
├── crowdworks/                # CrowdWorks用
│   ├── scraper.py             # CrowdWorks専用スクレイパー
│   ├── scrape.py              # 実行スクリプト
│   └── output/               # 出力ファイル（CSVなど）
│
├── mercari/                    # メルカリ用
│   ├── scraper.py             # メルカリ専用スクレイパー（実装が必要）
│   ├── scrape.py              # 実行スクリプト
│   ├── README.md              # メルカリ用の説明
│   └── output/                # 出力ファイル（CSVなど）
│
└── [e2eモジュール]             # Playwright関連の共通モジュール
    ├── dom_xpath_handler.py
    ├── playwright_capture.py
    └── ...
```

## 🚀 使い方

### CrowdWorksのスクレイピング

```bash
# 1件取得して確認
python3 crowdworks/scrape.py

# または、直接実行
cd crowdworks
python3 scrape.py
```

### メルカリのスクレイピング

1. **まず実装が必要**: `mercari/scraper.py` を実装してください
2. **実行**: `python3 mercari/scrape.py`

詳細は `mercari/README.md` を参照してください。

## 📝 新しいサイトを追加する方法

### ステップ1: フォルダを作成

```bash
mkdir -p 新しいサイト名/output
```

### ステップ2: 必要なファイルを作成

1. `__init__.py` - モジュールの初期化ファイル
2. `scraper.py` - スクレイパークラス（BaseScraperを継承）
3. `scrape.py` - 実行スクリプト
4. `README.md` - そのサイト用の説明（オプション）

### ステップ3: 実装

`scraper.py` で以下のメソッドを実装：

```python
from common.base_scraper import BaseScraper

class 新しいサイトScraper(BaseScraper):
    def scrape_list(self, url: str, **kwargs) -> List[str]:
        # 一覧ページからリンクを取得
        pass
    
    def scrape_detail(self, item_url: str, **kwargs) -> Optional[Dict[str, Any]]:
        # 詳細ページから情報を取得
        pass
```

## 🎯 この構造のメリット

1. **整理しやすい**: 各サイトのコードが分離されている
2. **拡張しやすい**: 新しいサイトを追加するのが簡単
3. **保守しやすい**: 各サイトの変更が他に影響しない
4. **再利用可能**: 共通機能を`common/`で共有

## 📚 参考資料

- `プロジェクト構造.md` - 詳細な構造説明
- `crowdworks/` - CrowdWorksの実装例
- `mercari/README.md` - メルカリの実装ガイド

## ⚠️ 注意事項

- 各サイトの利用規約を確認してください
- 過度なリクエストは避けてください
- 適切な待機時間を設定してください
