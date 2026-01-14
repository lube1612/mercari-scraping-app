# Googleスプレッドシート連携セットアップ手順

## 📋 セットアップの全体像

1. **APIサーバーを起動**（ローカルまたはクラウド）
2. **Googleスプレッドシートを作成**
3. **Google Apps Scriptを設定**
4. **ボタンを配置**
5. **動作確認**

## 🚀 ステップ1: APIサーバーの起動

### ローカル環境で起動

**Cursorのターミナルで：**

```bash
cd /Users/shimadaeiji/Documents/Cursor/e2e

# Flaskをインストール（初回のみ）
pip3 install flask flask-cors

# APIサーバーを起動
python3 api_server.py
```

**APIサーバーが起動したら：**
- URL: `http://localhost:5000`
- ヘルスチェック: `http://localhost:5000/api/health`

### 外部からアクセスできるようにする（ngrok使用）

**別のターミナルで：**

```bash
# ngrokをインストール（初回のみ）
# https://ngrok.com/ からダウンロード

# ngrokでトンネルを作成
ngrok http 5000
```

**ngrokのURLをコピー**（例: `https://abc123.ngrok.io`）

## 📊 ステップ2: Googleスプレッドシートの作成

1. **Googleスプレッドシートを開く**
   - https://sheets.google.com/

2. **スプレッドシートのレイアウトを設定**

   ```
   A1: 検索キーワード
   B1: ポケモンカード
   
   A2: 取得件数
   B2: 5
   
   A3: [スタート] ← ここにボタンを配置
   
   A5: タイトル
   B5: 価格
   C5: URL
   D5: 説明
   E5: 画像URL
   ```

3. **ボタンを作成**
   - 挿入 > 図形 > 四角形
   - 「スタート」とテキストを入力
   - 色を設定（例: 緑色）

## 🔧 ステップ3: Google Apps Scriptの設定

1. **拡張機能 > Apps Script を開く**

2. **以下のコードを貼り付け：**

```javascript
/**
 * スクレイピング実行関数
 */
function runScraping() {
  var sheet = SpreadsheetApp.getActiveSheet();
  
  // 入力値を取得
  var keyword = sheet.getRange('B1').getValue();
  var maxItems = sheet.getRange('B2').getValue();
  
  if (!keyword) {
    SpreadsheetApp.getUi().alert('検索キーワードを入力してください。');
    return;
  }
  
  if (!maxItems || maxItems < 1) {
    SpreadsheetApp.getUi().alert('取得件数を1以上で入力してください。');
    return;
  }
  
  // APIエンドポイント（ローカル環境の場合）
  // var apiUrl = 'http://localhost:5000/api/scrape';  // ローカルのみ
  // var apiUrl = 'https://YOUR-NGROK-URL.ngrok.io/api/scrape';  // ngrok使用時
  var apiUrl = 'https://YOUR-CLOUD-FUNCTIONS-URL.cloudfunctions.net/scrape_mercari';  // Cloud Functions使用時
  
  // リクエストデータ
  var payload = {
    'keyword': keyword,
    'max_items': maxItems
  };
  
  var options = {
    'method': 'post',
    'contentType': 'application/json',
    'payload': JSON.stringify(payload),
    'muteHttpExceptions': true
  };
  
  try {
    // 実行中メッセージ
    SpreadsheetApp.getUi().alert('スクレイピングを実行中です。\n完了までしばらくお待ちください。\n（1件あたり3-5秒かかります）');
    
    // APIを呼び出し
    var response = UrlFetchApp.fetch(apiUrl, options);
    var responseCode = response.getResponseCode();
    var responseText = response.getContentText();
    
    if (responseCode !== 200) {
      throw new Error('APIエラー: ' + responseCode + '\n' + responseText);
    }
    
    var result = JSON.parse(responseText);
    
    if (result.success) {
      // 結果をスプレッドシートに書き込む
      writeResultsToSheet(sheet, result.items);
      SpreadsheetApp.getUi().alert('完了しました！\n' + result.count + '件の商品情報を取得しました。');
    } else {
      SpreadsheetApp.getUi().alert('エラーが発生しました:\n' + (result.error || '不明なエラー'));
    }
  } catch (e) {
    SpreadsheetApp.getUi().alert('エラーが発生しました:\n' + e.toString());
    Logger.log('エラー詳細: ' + e);
  }
}

/**
 * 結果をスプレッドシートに書き込む
 */
function writeResultsToSheet(sheet, items) {
  // ヘッダーを設定
  var headers = ['タイトル', '価格', 'URL', '説明', '画像URL'];
  sheet.getRange(5, 1, 1, headers.length).setValues([headers]);
  sheet.getRange(5, 1, 1, headers.length).setFontWeight('bold');
  
  // 既存のデータをクリア
  var lastRow = sheet.getLastRow();
  if (lastRow > 5) {
    sheet.getRange(6, 1, lastRow - 5, headers.length).clear();
  }
  
  // データを書き込む
  if (items && items.length > 0) {
    var data = [];
    for (var i = 0; i < items.length; i++) {
      var item = items[i];
      data.push([
        item.title || '',
        item.price || '',
        item.url || '',
        item.description || '',
        item.image_url || ''
      ]);
    }
    
    if (data.length > 0) {
      sheet.getRange(6, 1, data.length, headers.length).setValues(data);
      
      // URLをリンクとして設定
      for (var i = 0; i < data.length; i++) {
        var urlCell = sheet.getRange(6 + i, 3);
        if (data[i][2]) {
          urlCell.setFormula('=HYPERLINK("' + data[i][2] + '","' + data[i][2] + '")');
        }
      }
      
      // 列幅を自動調整
      sheet.autoResizeColumns(1, headers.length);
    }
  } else {
    sheet.getRange(6, 1).setValue('商品が見つかりませんでした。');
  }
}

/**
 * メニューを追加
 */
function onOpen() {
  var ui = SpreadsheetApp.getUi();
  ui.createMenu('スクレイピング')
    .addItem('スタート', 'runScraping')
    .addSeparator()
    .addItem('ヘルプ', 'showHelp')
    .addToUi();
}

/**
 * ヘルプを表示
 */
function showHelp() {
  var message = '【使い方】\n\n';
  message += '1. B1セルに検索キーワードを入力\n';
  message += '2. B2セルに取得件数を入力\n';
  message += '3. 「スタート」ボタンをクリック\n';
  message += '4. 結果が5行目以降に表示されます\n\n';
  message += '【注意】\n';
  message += '- APIサーバーが起動している必要があります\n';
  message += '- 1件あたり3-5秒かかります';
  
  SpreadsheetApp.getUi().alert(message);
}
```

3. **保存**（Ctrl+S または Cmd+S）

4. **API URLを設定**
   - `apiUrl` の行を編集
   - ローカル環境: `http://localhost:5000/api/scrape`
   - ngrok使用: `https://YOUR-NGROK-URL.ngrok.io/api/scrape`
   - Cloud Functions使用: `https://YOUR-REGION-YOUR-PROJECT.cloudfunctions.net/scrape_mercari`

## 🔘 ステップ4: ボタンの設定

1. **図形を右クリック**
2. **「スクリプトを割り当て」を選択**
3. **`runScraping` と入力**
4. **OKをクリック**

## ✅ ステップ5: 動作確認

1. **B1セルに検索キーワードを入力**（例: "ポケモンカード"）
2. **B2セルに取得件数を入力**（例: 5）
3. **「スタート」ボタンをクリック**
4. **結果が5行目以降に表示されることを確認**

## 🔧 トラブルシューティング

### 問題1: APIサーバーに接続できない

**解決方法:**
- APIサーバーが起動しているか確認
- URLが正しいか確認
- ngrokを使用している場合、URLが変更されていないか確認

### 問題2: CORSエラーが発生する

**解決方法:**
- `api_server.py` で `CORS(app)` が設定されているか確認
- `flask-cors` がインストールされているか確認

### 問題3: 結果が表示されない

**解決方法:**
- Apps Scriptのログを確認（表示 > ログ）
- APIのレスポンスを確認
- スプレッドシートの5行目以降が空いているか確認

## 📝 次のステップ

1. **ローカル環境で動作確認**
2. **必要に応じてクラウドにデプロイ**
3. **機能を拡張**（エラーハンドリング、進捗表示など）
