"""
Amazon商品情報スクレイパー

共通のBaseScraperを継承してAmazon専用の実装を行います。
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional, Any
import re

# 親ディレクトリのパスを追加して共通モジュールをインポート
sys.path.insert(0, str(Path(__file__).parent.parent))
from common.base_scraper import BaseScraper


class AmazonScraper(BaseScraper):
    """
    Amazonの商品情報をスクレイピングするクラス
    """
    
    def scrape_list(self, url: str, wait_time: int = 3000) -> List[str]:
        """
        商品一覧ページから商品リンクを取得

        Input:
            url: 商品一覧ページのURL（検索結果ページなど）
            wait_time: 読み込み待機時間(ミリ秒)

        Output:
            List[str]: 商品詳細ページのURLリスト
        """
        page = self.get_page()
        item_links = []

        try:
            print(f"商品一覧ページにアクセス中: {url}")
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
            except Exception as e:
                print(f"  警告: ページ読み込みでエラーが発生しました: {e}")
                print("  続行します...")
            
            page.wait_for_timeout(wait_time * 2)
            
            # クッキー同意ボタンをクリック
            try:
                cookie_selectors = [
                    'button:has-text("Accept")',
                    'button:has-text("同意")',
                    '#sp-cc-accept',
                    '.a-button-primary:has-text("Accept")',
                ]
                for selector in cookie_selectors:
                    try:
                        cookie_button = page.locator(selector).first
                        if cookie_button.count() > 0:
                            cookie_button.click()
                            print("  クッキー同意ボタンをクリックしました")
                            page.wait_for_timeout(1000)
                            break
                    except:
                        continue
            except:
                pass
            
            # 商品リンクが表示されるまで待機
            print("  商品リンクの読み込みを待機中...")
            try:
                page.wait_for_selector("a[href*='/dp/'], a[href*='/gp/product/']", timeout=15000)
            except:
                print("  商品リンクの自動検出に失敗しました。追加の待機時間を設定します...")
                page.wait_for_timeout(5000)
            
            # Amazonの商品リンクを取得するセレクタ
            selectors = [
                "a[href*='/dp/']",           # Amazon商品ページの標準URL形式
                "a[href*='/gp/product/']",    # 別のURL形式
                "h2 a[href*='/dp/']",        # 商品タイトル内のリンク
                ".s-result-item a[href*='/dp/']",  # 検索結果内のリンク
            ]
            
            # 除外するURLパターン
            exclude_patterns = [
                "/help",
                "/gp/help",
                "/customer",
                "/ap/signin",
                "/ref=",
            ]
            
            for selector in selectors:
                try:
                    links = page.locator(selector).all()
                    if links:
                        print(f"セレクタ '{selector}' で {len(links)} 件のリンクを発見")
                        for link in links:
                            try:
                                href = link.get_attribute("href")
                                if not href:
                                    continue
                                
                                # デバッグ用：最初の数件のhrefを表示
                                if len(item_links) < 3:
                                    print(f"  デバッグ: href = {href}")
                                
                                # Amazon商品リンクパターンを検出
                                if "/dp/" in href or "/gp/product/" in href:
                                    # 除外パターンをチェック
                                    should_exclude = any(pattern in href for pattern in exclude_patterns)
                                    if should_exclude:
                                        continue
                                    
                                    # 商品IDパターンをチェック
                                    item_id_patterns = [
                                        r'/dp/([A-Z0-9]{10})',      # /dp/B08XXXXXXX
                                        r'/gp/product/([A-Z0-9]{10})',  # /gp/product/B08XXXXXXX
                                    ]
                                    
                                    matched = False
                                    for pattern in item_id_patterns:
                                        if re.search(pattern, href):
                                            matched = True
                                            break
                                    
                                    if matched:
                                        # フルURLに変換
                                        if href.startswith("http"):
                                            full_url = href.split("?")[0].split("#")[0]  # クエリパラメータを除去
                                        elif href.startswith("/"):
                                            full_url = f"https://www.amazon.co.jp{href.split('?')[0].split('#')[0]}"
                                        else:
                                            continue
                                        
                                        # 重複チェック
                                        if full_url not in item_links:
                                            item_links.append(full_url)
                                            print(f"  商品リンク {len(item_links)}: {full_url}")
                            
                            except Exception as e:
                                print(f"  リンク処理エラー: {e}")
                                continue
                        
                        if item_links:
                            print(f"合計 {len(item_links)} 件の商品リンクを発見")
                            break
                
                except Exception as e:
                    print(f"セレクタ '{selector}' でエラー: {e}")
                    continue
        
        except Exception as e:
            print(f"エラー: {e}")
            import traceback
            traceback.print_exc()
        finally:
            page.context.close()
        
        return item_links
    
    def scrape_detail(self, item_url: str, wait_time: int = 3000) -> Optional[Dict[str, Any]]:
        """
        商品詳細ページから情報を取得

        Input:
            item_url: 商品詳細ページのURL
            wait_time: 読み込み待機時間(ミリ秒)

        Output:
            Dict[str, Any]: 商品情報の辞書
        """
        page = self.get_page()
        
        try:
            print(f"\n商品詳細ページにアクセス中: {item_url}")
            try:
                page.goto(item_url, wait_until="domcontentloaded", timeout=60000)
            except Exception as e:
                print(f"  警告: ページ読み込みでエラーが発生しました: {e}")
                return None
            
            page.wait_for_timeout(wait_time)
            
            # クッキー同意ボタンをクリック
            try:
                cookie_selectors = [
                    'button:has-text("Accept")',
                    '#sp-cc-accept',
                ]
                for selector in cookie_selectors:
                    try:
                        cookie_button = page.locator(selector).first
                        if cookie_button.count() > 0:
                            cookie_button.click()
                            print("  クッキー同意ボタンをクリックしました")
                            page.wait_for_timeout(1000)
                            break
                    except:
                        continue
            except:
                pass
            
            item_info = {
                "url": item_url,
                "title": "",
                "price": "",
                "description": "",
                "image_url": "",
            }
            
            # タイトルを取得
            title_selectors = [
                "#productTitle",
                "h1.a-size-large",
                "h1",
            ]
            for selector in title_selectors:
                try:
                    title_elem = page.locator(selector).first
                    if title_elem.count() > 0:
                        item_info["title"] = title_elem.inner_text().strip()
                        print(f"タイトル取得: {item_info['title'][:50]}")
                        break
                except:
                    continue
            
            # 価格を取得
            price_selectors = [
                ".a-price-whole",
                "#priceblock_ourprice",
                "#priceblock_dealprice",
                ".a-price .a-offscreen",
                "span.a-price",
            ]
            for selector in price_selectors:
                try:
                    price_elem = page.locator(selector).first
                    if price_elem.count() > 0:
                        price_text = price_elem.inner_text().strip()
                        # 価格から数字を抽出
                        price_match = re.search(r'[\d,]+', price_text.replace(',', ''))
                        if price_match:
                            item_info["price"] = f"¥{price_match.group()}"
                            print(f"価格取得: {item_info['price']}")
                            break
                except:
                    continue
            
            # 画像URLを取得
            try:
                img_elem = page.locator("#landingImage, #imgBlkFront").first
                if img_elem.count() > 0:
                    item_info["image_url"] = img_elem.get_attribute("src") or ""
            except:
                pass
            
            return item_info
        
        except Exception as e:
            print(f"エラー: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            page.context.close()
