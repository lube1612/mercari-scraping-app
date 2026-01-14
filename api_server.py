"""
メルカリスクレイピングAPIサーバー

スプレッドシートから呼び出せるREST APIを提供します。
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
from pathlib import Path
import time

# 親ディレクトリのパスを追加
sys.path.insert(0, str(Path(__file__).parent))

from mercari.scraper import MercariScraper

app = Flask(__name__)
CORS(app)  # クロスオリジンリクエストを許可（スプレッドシートから呼び出すため）


@app.route('/api/scrape', methods=['POST'])
def scrape_mercari():
    """
    メルカリスクレイピングAPI
    
    Request Body:
    {
        "keyword": "ポケモンカード",
        "max_items": 5
    }
    
    Response:
    {
        "success": true,
        "items": [
            {
                "title": "商品タイトル",
                "price": "¥400",
                "url": "https://...",
                ...
            }
        ],
        "count": 5
    }
    """
    try:
        # リクエストデータを取得
        data = request.get_json(silent=True) or {}
        keyword = data.get('keyword', 'ポケモンカード')
        max_items = int(data.get('max_items', 5))
        
        # 環境変数を設定
        if os.path.exists(os.path.expanduser('~/playwright-browsers')):
            os.environ['PLAYWRIGHT_BROWSERS_PATH'] = os.path.expanduser('~/playwright-browsers')
        
        items_data = []
        
        with MercariScraper(headless=True) as scraper:
            target_url = f"https://www.mercari.com/jp/search/?keyword={keyword}"
            item_links = scraper.scrape_list(target_url)
            
            if not item_links:
                return jsonify({
                    "success": False,
                    "error": "商品リンクが見つかりませんでした。"
                }), 404
            
            # 商品情報を取得
            for i, item_url in enumerate(item_links[:max_items * 2]):  # 余裕を持って取得
                if len(items_data) >= max_items:
                    break
                
                try:
                    item_info = scraper.scrape_detail(item_url)
                    if item_info:
                        title = item_info.get('title', '')
                        if title and len(title) > 5:
                            items_data.append(item_info)
                except Exception as e:
                    continue
                
                time.sleep(1)  # リクエスト間隔
        
        return jsonify({
            "success": True,
            "items": items_data,
            "count": len(items_data)
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """ヘルスチェック用エンドポイント"""
    return jsonify({
        "status": "ok",
        "message": "APIサーバーは正常に動作しています。"
    })


if __name__ == '__main__':
    print("=" * 60)
    print("メルカリスクレイピングAPIサーバー")
    print("=" * 60)
    print("APIエンドポイント: http://localhost:5000/api/scrape")
    print("ヘルスチェック: http://localhost:5000/api/health")
    print()
    print("スプレッドシートから呼び出す場合は、このサーバーを起動したままにしてください。")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
