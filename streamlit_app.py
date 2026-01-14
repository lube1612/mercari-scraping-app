"""
StreamlitベースのWebアプリケーション

スプレッドシート風のUIで条件を入力してスクレイピングを実行できます。
"""

import streamlit as st
import sys
from pathlib import Path
import os
import pandas as pd

# 親ディレクトリのパスを追加
sys.path.insert(0, str(Path(__file__).parent))

from mercari.scraper import MercariScraper
from common.utils import save_to_csv
import time
import re


def extract_price(price_str: str) -> float:
    """価格文字列から数値を抽出"""
    if not price_str:
        return float('inf')
    price_match = re.search(r'[\d,]+', price_str.replace(',', ''))
    if price_match:
        try:
            return float(price_match.group().replace(',', ''))
        except:
            return float('inf')
    return float('inf')


def run_scraping(search_keyword: str, max_items: int, compare_with_amazon: bool):
    """
    スクレイピングを実行
    
    Args:
        search_keyword: 検索キーワード
        max_items: 取得件数
        compare_with_amazon: Amazonと比較するか
    """
    # 環境変数を設定
    if os.path.exists(os.path.expanduser('~/playwright-browsers')):
        os.environ['PLAYWRIGHT_BROWSERS_PATH'] = os.path.expanduser('~/playwright-browsers')
    
    items_data = []
    
    try:
        with MercariScraper(headless=True) as scraper:  # Streamlitではheadless=True推奨
            # 商品一覧ページから商品リンクを取得
            target_url = f"https://www.mercari.com/jp/search/?keyword={search_keyword}"
            
            st.info(f"商品一覧ページにアクセス中: {target_url}")
            item_links = scraper.scrape_list(target_url)
            
            if not item_links:
                st.error("商品リンクが見つかりませんでした。")
                return None
            
            st.success(f"{len(item_links)} 件の商品リンクを発見しました。")
            
            # プログレスバーを作成
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # 商品情報を取得
            successful_count = 0
            for i, item_url in enumerate(item_links[:max_items * 2]):  # 余裕を持って取得
                if successful_count >= max_items:
                    break
                
                status_text.text(f"商品 {successful_count + 1}/{max_items} を取得中... ({i+1}/{len(item_links)})")
                progress_bar.progress((i + 1) / min(len(item_links), max_items * 2))
                
                try:
                    item_info = scraper.scrape_detail(item_url)
                    if item_info:
                        title = item_info.get('title', '')
                        if title and len(title) > 5:
                            items_data.append(item_info)
                            successful_count += 1
                except Exception as e:
                    st.warning(f"エラー: {e}")
                    continue
                
                time.sleep(1)  # リクエスト間隔
            
            progress_bar.progress(1.0)
            status_text.text("完了！")
        
        return items_data
    
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
        import traceback
        st.code(traceback.format_exc())
        return None


# Streamlitアプリの設定
st.set_page_config(
    page_title="メルカリスクレイピングシステム",
    page_icon="🛒",
    layout="wide"
)

st.title("🛒 メルカリスクレイピングシステム")
st.markdown("---")

# サイドバーに設定フォーム
with st.sidebar:
    st.header("⚙️ 設定")
    
    search_keyword = st.text_input(
        "検索キーワード",
        value="ポケモンカード",
        help="メルカリで検索するキーワードを入力してください"
    )
    
    max_items = st.number_input(
        "取得件数",
        min_value=1,
        max_value=20,
        value=5,
        help="取得する商品の最大件数"
    )
    
    compare_with_amazon = st.checkbox(
        "Amazonと価格比較",
        value=False,
        help="Amazonの価格と比較する場合はチェック（閲覧モード）"
    )
    
    st.markdown("---")
    st.info("💡 ヒント:\n- 検索キーワードを変更して実行できます\n- 取得件数を調整できます\n- Amazon比較は時間がかかります")

# メインエリア
col1, col2 = st.columns([3, 1])

with col1:
    st.header("📋 実行条件")
    
    # 条件を表示
    st.write(f"**検索キーワード:** {search_keyword}")
    st.write(f"**取得件数:** {max_items}件")
    st.write(f"**Amazon比較:** {'有効' if compare_with_amazon else '無効'}")

with col2:
    st.header("🚀 実行")
    
    if st.button("▶️ スクレイピング実行", type="primary", use_container_width=True):
        # 実行中メッセージ
        with st.spinner("スクレイピングを実行中..."):
            items_data = run_scraping(search_keyword, max_items, compare_with_amazon)
        
        if items_data:
            st.success(f"✅ {len(items_data)}件の商品情報を取得しました！")
            
            # 結果を表示
            st.header("📊 取得結果")
            
            # データフレームに変換
            df = pd.DataFrame(items_data)
            
            # 表示用にカラムを選択
            display_columns = ['title', 'price', 'url']
            if 'amazon_price' in df.columns:
                display_columns.extend(['amazon_price', 'price_difference'])
            
            if display_columns:
                st.dataframe(df[display_columns], use_container_width=True)
            
            # CSVダウンロードボタン
            csv_data = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 CSVファイルをダウンロード",
                data=csv_data,
                file_name=f"mercari_items_{search_keyword}_{int(time.time())}.csv",
                mime="text/csv"
            )
            
            # ファイルに保存
            output_path = Path(__file__).parent / "mercari" / "output" / f"mercari_items_{search_keyword}_{int(time.time())}.csv"
            save_to_csv(items_data, str(output_path))
            st.info(f"💾 ファイルに保存しました: `{output_path}`")
        else:
            st.error("商品情報の取得に失敗しました。")

# 履歴セクション
st.markdown("---")
st.header("📁 過去の実行結果")

# 出力ディレクトリからCSVファイルを一覧表示
output_dir = Path(__file__).parent / "mercari" / "output"
if output_dir.exists():
    csv_files = list(output_dir.glob("*.csv"))
    if csv_files:
        csv_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        for csv_file in csv_files[:5]:  # 最新5件
            with st.expander(f"📄 {csv_file.name}"):
                try:
                    df = pd.read_csv(csv_file)
                    st.dataframe(df, use_container_width=True)
                    
                    # ダウンロードボタン
                    with open(csv_file, 'rb') as f:
                        st.download_button(
                            label=f"📥 {csv_file.name} をダウンロード",
                            data=f.read(),
                            file_name=csv_file.name,
                            mime="text/csv",
                            key=f"download_{csv_file.name}"
                        )
                except Exception as e:
                    st.error(f"ファイルの読み込みエラー: {e}")
