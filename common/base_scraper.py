"""
ベーススクレイパークラス

すべてのサイトスクレイパーの基底クラス
"""

from playwright.sync_api import sync_playwright, Page, Browser
from typing import Optional, Dict, List, Any
from abc import ABC, abstractmethod


class BaseScraper(ABC):
    """
    すべてのサイトスクレイパーの基底クラス
    
    各サイトのスクレイパーはこのクラスを継承して実装します。
    """

    def __init__(self, headless: bool = False, browser_type: str = "chromium"):
        """
        初期化

        Args:
            headless: ヘッドレスモードで実行するか
            browser_type: ブラウザタイプ ("chromium", "firefox", "webkit")
        """
        self.headless = headless
        self.browser_type = browser_type
        self.playwright = None
        self.browser: Optional[Browser] = None

    def __enter__(self):
        """コンテキストマネージャー開始"""
        self.playwright = sync_playwright().start()

        if self.browser_type == "chromium":
            self.browser = self.playwright.chromium.launch(headless=self.headless)
        elif self.browser_type == "firefox":
            self.browser = self.playwright.firefox.launch(headless=self.headless)
        elif self.browser_type == "webkit":
            self.browser = self.playwright.webkit.launch(headless=self.headless)
        else:
            raise ValueError(f"Unknown browser type: {self.browser_type}")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャー終了"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def get_page(self, viewport_size: Optional[Dict[str, int]] = None) -> Page:
        """
        新しいページを作成

        Input:
            viewport_size: ビューポートサイズ {"width": 1280, "height": 720}

        Output:
            Page: PlaywrightのPageオブジェクト
        """
        if not self.browser:
            raise RuntimeError("Browser not initialized. Use context manager (with statement)")

        context = self.browser.new_context(
            viewport=viewport_size or {"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            # Google翻訳を無効にする
            locale="ja-JP",
            timezone_id="Asia/Tokyo",
            # 拡張機能を無効にする（翻訳拡張機能を避けるため）
            ignore_https_errors=True
        )
        return context.new_page()

    @abstractmethod
    def scrape_list(self, url: str, **kwargs) -> List[str]:
        """
        一覧ページからアイテムのリンクを取得
        
        各サイトで実装する必要があります。
        
        Input:
            url: 一覧ページのURL
            **kwargs: 追加の引数
        
        Output:
            List[str]: アイテム詳細ページのURLリスト
        """
        pass

    @abstractmethod
    def scrape_detail(self, item_url: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        詳細ページから情報を取得
        
        各サイトで実装する必要があります。
        
        Input:
            item_url: アイテム詳細ページのURL
            **kwargs: 追加の引数
        
        Output:
            Dict[str, Any]: アイテム情報の辞書
        """
        pass
