#!/bin/bash
# Streamlit Cloud用のセットアップスクリプト
# デプロイ時にPlaywrightブラウザをインストール

echo "Installing Playwright browsers..."
python -m playwright install chromium
python -m playwright install-deps chromium
