# メルカリ ポケモンカードスクレイピングモジュール

## 📋 概要

メルカリのポケモンカード情報をスクレイピングするためのモジュールです。
ポケモンカードに特化した情報（レアリティ、セット名、カード番号など）を取得できます。

## 🚀 使い方

### 1. 基本的な実行

```bash
python3 mercari/scrape.py
```

### 2. 検索キーワードを変更する

`mercari/scrape.py` の以下の部分を変更：

```python
target_url = "https://www.mercari.com/jp/search/?keyword=ポケモンカード"
```

例：
- `keyword=ポケモンカード SR` - SRレアリティのカードを検索
- `keyword=ポケモンカード 拡張パック` - 拡張パックを検索
- `keyword=ポケモンカード ピカチュウ` - ピカチュウのカードを検索

### 3. 取得件数を変更する

```python
max_items = 10  # 10件取得する場合
```

### 4. 設定ファイルを使用する

`mercari/config.py` で詳細な設定が可能です。

## 📊 取得できる情報

### 基本情報
- **title**: 商品タイトル
- **price**: 価格
- **description**: 商品説明
- **condition**: 商品の状態（美品、未使用など）
- **shipping**: 送料情報
- **category**: カテゴリー
- **image_url**: 商品画像URL

### ポケモンカード特有の情報
- **card_name**: カード名
- **rarity**: レアリティ（SR、UR、HRなど）
- **set_name**: セット名・拡張パック名
- **card_number**: カード番号
- **pokemon_type**: ポケモンのタイプ（今後実装予定）

## 📝 実装例

### 商品リンクの取得例

```python
def scrape_list(self, url: str, wait_time: int = 3000) -> List[str]:
    page = self.get_page()
    item_links = []
    
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(wait_time)
        
        # メルカリの商品リンクセレクタ（例）
        links = page.locator("a[href*='/items/']").all()
        for link in links:
            href = link.get_attribute("href")
            if href:
                full_url = href if href.startswith("http") else f"https://www.mercari.com{href}"
                item_links.append(full_url)
    finally:
        page.context.close()
    
    return item_links
```

### 商品情報の取得例

```python
def scrape_detail(self, item_url: str, wait_time: int = 3000) -> Optional[Dict[str, Any]]:
    page = self.get_page()
    
    try:
        page.goto(item_url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(wait_time)
        
        item_info = {
            "url": item_url,
            "title": "",
            "price": "",
            "description": "",
        }
        
        # タイトルを取得（例）
        title_elem = page.locator("h1.item-name").first
        if title_elem.count() > 0:
            item_info["title"] = title_elem.inner_text().strip()
        
        # 価格を取得（例）
        price_elem = page.locator(".item-price").first
        if price_elem.count() > 0:
            item_info["price"] = price_elem.inner_text().strip()
        
        return item_info
    finally:
        page.context.close()
```

## ⚠️ 注意事項

- メルカリの利用規約を確認してください
- 過度なリクエストは避けてください
- 適切な待機時間を設定してください
