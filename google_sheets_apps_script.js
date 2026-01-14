/**
 * Google Apps Script for Googleスプレッドシート連携
 * 
 * スプレッドシートに条件を入力して、スクレイピングを実行できます。
 * 
 * 【セットアップ手順】
 * 1. Googleスプレッドシートを開く
 * 2. 拡張機能 > Apps Script を開く
 * 3. このコードを貼り付ける
 * 4. 保存して実行
 * 
 * 【使い方】
 * 1. スプレッドシートに条件を入力（A1: 検索キーワード、B1: 取得件数）
 * 2. メニューから「スクレイピング実行」を選択
 * 3. 結果がスプレッドシートに出力されます
 */

/**
 * メニューを追加
 */
function onOpen() {
  var ui = SpreadsheetApp.getUi();
  ui.createMenu('スクレイピング')
    .addItem('スクレイピング実行', 'runScraping')
    .addToUi();
}

/**
 * スクレイピングを実行
 */
function runScraping() {
  var sheet = SpreadsheetApp.getActiveSheet();
  
  // 条件を取得（A1: 検索キーワード、B1: 取得件数）
  var searchKeyword = sheet.getRange('A1').getValue() || 'ポケモンカード';
  var maxItems = sheet.getRange('B1').getValue() || 5;
  
  // ヘッダーを設定
  var headers = ['タイトル', '価格', 'URL', '説明', '画像URL'];
  sheet.getRange(3, 1, 1, headers.length).setValues([headers]);
  sheet.getRange(3, 1, 1, headers.length).setFontWeight('bold');
  
  // 結果エリアをクリア
  sheet.getRange(4, 1, sheet.getLastRow() - 3, headers.length).clear();
  
  // 実行中メッセージ
  SpreadsheetApp.getUi().alert('スクレイピングを実行中です。\n完了までしばらくお待ちください。');
  
  // 注意: Google Apps Scriptから直接Pythonスクリプトを実行することはできません
  // 以下の方法を検討してください：
  // 1. Google Cloud Functionsを使用してPythonスクリプトを実行
  // 2. Webアプリケーション（Streamlit）を使用
  // 3. Google Apps Scriptから外部APIを呼び出す
  
  // ここでは、スプレッドシートにメッセージを表示するだけの例です
  sheet.getRange(4, 1).setValue('⚠️ Google Apps Scriptから直接Pythonスクリプトを実行することはできません。');
  sheet.getRange(5, 1).setValue('Streamlitアプリケーションを使用することを推奨します。');
  sheet.getRange(6, 1).setValue('実行方法: streamlit run streamlit_app.py');
}

/**
 * 外部APIを呼び出す例（Webアプリケーション経由）
 */
function callScrapingAPI(searchKeyword, maxItems) {
  // WebアプリケーションのURL（Streamlitアプリをデプロイした場合）
  var apiUrl = 'https://your-streamlit-app.herokuapp.com/api/scrape';
  
  var payload = {
    'keyword': searchKeyword,
    'max_items': maxItems
  };
  
  var options = {
    'method': 'post',
    'contentType': 'application/json',
    'payload': JSON.stringify(payload)
  };
  
  try {
    var response = UrlFetchApp.fetch(apiUrl, options);
    var result = JSON.parse(response.getContentText());
    return result;
  } catch (e) {
    Logger.log('エラー: ' + e);
    return null;
  }
}
