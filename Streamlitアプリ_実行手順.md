# Streamlitアプリケーション実行手順

## 📋 概要

スプレッドシート風のUIで条件を入力してスクレイピングを実行できるWebアプリケーションです。

## 🚀 セットアップ

### 1. Streamlitのインストール

**Cursorのターミナルで以下のコマンドを実行：**

```bash
cd /Users/shimadaeiji/Documents/Cursor/e2e
pip3 install streamlit pandas
```

または、requirementsファイルからインストール：

```bash
pip3 install -r requirements_streamlit.txt
```

### 2. アプリケーションの起動

**Cursorのターミナルで以下のコマンドを実行：**

```bash
cd /Users/shimadaeiji/Documents/Cursor/e2e
export PLAYWRIGHT_BROWSERS_PATH=~/playwright-browsers
streamlit run streamlit_app.py
```

### 3. ブラウザで開く

コマンドを実行すると、自動的にブラウザが開きます。
URLは通常 `http://localhost:8501` です。

## 📊 使い方

### 1. 左側のサイドバーで設定

- **検索キーワード**: メルカリで検索するキーワードを入力
- **取得件数**: 取得する商品の最大件数（1-20件）
- **Amazonと価格比較**: Amazonの価格と比較する場合はチェック

### 2. 「スクレイピング実行」ボタンをクリック

- 実行中はプログレスバーが表示されます
- 完了すると結果が表示されます

### 3. 結果の確認とダウンロード

- 取得した商品情報がテーブル形式で表示されます
- 「CSVファイルをダウンロード」ボタンでCSVファイルをダウンロードできます
- 過去の実行結果も確認できます

## 🎯 機能

### 主な機能

1. **条件入力**
   - 検索キーワード
   - 取得件数
   - Amazon比較の有効/無効

2. **実行ボタン**
   - ワンクリックでスクレイピング実行
   - プログレスバーで進捗表示

3. **結果表示**
   - テーブル形式で結果を表示
   - CSVダウンロード機能

4. **履歴表示**
   - 過去の実行結果を確認
   - 過去のCSVファイルをダウンロード

## ⚠️ 注意事項

1. **ブラウザ表示**
   - Streamlitアプリはブラウザで開きます
   - スクレイピングはheadlessモードで実行されます（ブラウザウィンドウは表示されません）

2. **実行時間**
   - 取得件数によって実行時間が変わります
   - 1件あたり約3-5秒かかります

3. **Amazon比較**
   - Amazon比較を有効にすると、実行時間が長くなります
   - 各商品についてAmazonのページを確認します

## 🔧 トラブルシューティング

### 問題1: Streamlitがインストールできない

**解決方法:**
```bash
pip3 install --upgrade pip
pip3 install streamlit
```

### 問題2: アプリが起動しない

**解決方法:**
- ポート8501が使用中の場合は、別のポートを指定：
  ```bash
  streamlit run streamlit_app.py --server.port 8502
  ```

### 問題3: スクレイピングが失敗する

**解決方法:**
- Playwrightブラウザがインストールされているか確認
- 環境変数が正しく設定されているか確認

## 📝 カスタマイズ

### デフォルト値を変更する場合

`streamlit_app.py` の以下の部分を変更：

```python
search_keyword = st.text_input(
    "検索キーワード",
    value="ポケモンカード",  # デフォルト値を変更
    ...
)

max_items = st.number_input(
    "取得件数",
    min_value=1,
    max_value=20,
    value=5,  # デフォルト値を変更
    ...
)
```

## 🎨 UIのカスタマイズ

StreamlitのUIは簡単にカスタマイズできます：

- 色やレイアウトの変更
- 追加の入力フィールド
- グラフやチャートの追加

詳細は [Streamlit公式ドキュメント](https://docs.streamlit.io/) を参照してください。
