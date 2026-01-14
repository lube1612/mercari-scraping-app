#!/bin/bash
# Playwright Chromium ブラウザのダウンロードスクリプト

echo "=========================================="
echo "Playwright Chromium ブラウザのダウンロード"
echo "=========================================="
echo ""

# ダウンロードURL
DOWNLOAD_URL="https://playwright.azureedge.net/builds/chromium/1200/chromium-mac-x64.zip"

# 保存先ディレクトリ
INSTALL_DIR="$HOME/Library/Caches/ms-playwright/chromium-1200/chrome-mac-x64"
ZIP_FILE="$HOME/Downloads/chromium-mac-x64.zip"

echo "1. 保存先ディレクトリを作成中..."
mkdir -p "$INSTALL_DIR"

echo "2. ZIPファイルをダウンロード中..."
echo "   URL: $DOWNLOAD_URL"
echo "   保存先: $ZIP_FILE"
echo "   （これには数分かかることがあります）"
echo ""

# curlでダウンロード（進捗表示とリダイレクト追従）
curl -L --progress-bar -o "$ZIP_FILE" "$DOWNLOAD_URL" --fail

# ダウンロードが成功したか確認
if [ $? -eq 0 ] && [ -f "$ZIP_FILE" ]; then
    # ファイルサイズを確認
    FILE_SIZE=$(stat -f%z "$ZIP_FILE" 2>/dev/null || stat -c%s "$ZIP_FILE" 2>/dev/null || echo "0")
    echo ""
    echo "✓ ダウンロードが完了しました"
    echo "  ファイルサイズ: $(numfmt --to=iec-i --suffix=B $FILE_SIZE 2>/dev/null || echo "${FILE_SIZE} bytes")"
    
    # ZIPファイルかどうか確認
    if ! file "$ZIP_FILE" | grep -q "Zip archive"; then
        echo ""
        echo "⚠️  警告: ダウンロードされたファイルがZIPファイルではない可能性があります"
        echo "  ファイルタイプ: $(file "$ZIP_FILE")"
        echo ""
        echo "  ファイルの内容を確認します..."
        head -c 200 "$ZIP_FILE" | cat -A
        echo ""
        echo ""
        echo "  手動でダウンロードする場合は、以下のURLをブラウザで開いてください:"
        echo "  $DOWNLOAD_URL"
        echo "  右クリックして「リンク先をダウンロード」を選択してください"
        exit 1
    fi
    
    echo ""
    
    echo "3. ZIPファイルを解凍中..."
    cd "$INSTALL_DIR"
    
    # ZIPファイルの整合性を確認
    if ! unzip -t "$ZIP_FILE" > /dev/null 2>&1; then
        echo "✗ ZIPファイルが破損しているか、有効なZIPファイルではありません"
        echo "  ファイルを削除して再ダウンロードしてください"
        rm -f "$ZIP_FILE"
        exit 1
    fi
    
    unzip -q "$ZIP_FILE" -d .
    
    if [ $? -eq 0 ]; then
        echo "✓ 解凍が完了しました"
        echo ""
        
        echo "4. 実行権限を付与中..."
        chmod +x "$INSTALL_DIR/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
        
        if [ $? -eq 0 ]; then
            echo "✓ 実行権限を付与しました"
            echo ""
            
            echo "5. インストール確認中..."
            if [ -f "$INSTALL_DIR/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing" ]; then
                echo "✓ インストールが完了しました！"
                echo ""
                echo "ファイルの場所:"
                echo "$INSTALL_DIR/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
                echo ""
                echo "次のステップ:"
                echo "  python3 mercari/scrape.py"
            else
                echo "✗ 実行ファイルが見つかりません"
            fi
        else
            echo "✗ 実行権限の付与に失敗しました"
        fi
    else
        echo "✗ 解凍に失敗しました"
    fi
    
    echo ""
    echo "6. 一時ファイルを削除中..."
    rm -f "$ZIP_FILE"
    echo "✓ 完了"
else
    echo ""
    echo "✗ ダウンロードに失敗しました"
    echo "手動でダウンロードする場合は、以下のURLをブラウザで開いてください:"
    echo "$DOWNLOAD_URL"
    echo ""
    echo "または、右クリックして「リンク先を保存」を選択してください"
fi
