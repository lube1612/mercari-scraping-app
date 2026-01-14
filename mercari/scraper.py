"""
メルカリ商品情報スクレイパー

共通のBaseScraperを継承してメルカリ専用の実装を行います。
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional, Any
import re

# 親ディレクトリのパスを追加して共通モジュールをインポート
sys.path.insert(0, str(Path(__file__).parent.parent))
from common.base_scraper import BaseScraper


class MercariScraper(BaseScraper):
    """
    メルカリの商品情報をスクレイピングするクラス
    
    【実装例】
    メルカリのサイト構造に合わせて、scrape_listとscrape_detailを実装してください。
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
            # networkidleは厳しすぎる可能性があるため、domcontentloadedに変更
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
            except Exception as e:
                print(f"  警告: ページ読み込みでエラーが発生しました: {e}")
                print("  続行します...")
            
            # ページの読み込みを待つ
            page.wait_for_timeout(wait_time * 2)  # 待機時間を2倍に
            
            # 商品リンクが表示されるまで待機
            print("  商品リンクの読み込みを待機中...")
            try:
                page.wait_for_load_state("networkidle", timeout=30000)
            except:
                # networkidleでタイムアウトしても続行
                print("  ネットワークアイドル待機をスキップしました")
                page.wait_for_timeout(3000)  # 追加で3秒待機
            
            # クッキー同意ボタンをクリック
            try:
                cookie_selectors = [
                    'button:has-text("Got it")',
                    'button:has-text("同意する")',
                    '[data-testid="cookie-banner-accept"]',
                    '.cookie-consent button',
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
            
            # 商品リンクが表示されるまで待機（より長い時間と複数のセレクタを試す）
            print("  商品リンクの読み込みを待機中...")
            wait_selectors = [
                "a[href*='/items/']",
                "a[href*='/jp/items/']",
                "section[data-testid='item-cell']",
                "[data-testid='item-cell']",
                "a[href*='mercari.com/jp/items/']",
                "a[href*='mercari.com/items/']",
            ]
            
            found_selector = False
            for wait_selector in wait_selectors:
                try:
                    page.wait_for_selector(wait_selector, timeout=15000)
                    print(f"  商品リンクが見つかりました（セレクタ: {wait_selector}）")
                    found_selector = True
                    break
                except:
                    continue
            
            if not found_selector:
                print("  商品リンクの自動検出に失敗しました。追加の待機時間を設定します...")
                page.wait_for_timeout(5000)  # 追加で5秒待機
            
            # スクロールして商品を読み込む（無限スクロール対応）
            try:
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(2000)
                page.evaluate("window.scrollTo(0, 0)")
                page.wait_for_timeout(1000)
            except:
                pass

            # メルカリの商品リンクを取得するセレクタ（複数のパターンを試す）
            # jp.mercari.com と www.mercari.com の両方に対応
            selectors = [
                "a[href*='jp.mercari.com/jp/items/']",  # jp.mercari.com形式（優先）
                "a[href*='mercari.com/jp/items/']",     # フルURL形式
                "a[href*='mercari.com/items/']",        # フルURL形式
                "a[href*='/jp/items/']",                 # 相対パス形式（優先）
                "a[href*='/items/']",                    # 相対パス形式
                "section[data-testid='item-cell'] a",   # 商品セル内のリンク
                "[data-testid='item-cell'] a",          # テストIDを使用したリンク
                "a[data-testid='item-cell-link']",      # 商品セルリンクの直接セレクタ
                ".items-box a",                         # 商品ボックス内のリンク
                "a[href^='/jp/items/']",                # 絶対パスで始まるリンク
            ]

            # 除外するURLパターン
            exclude_patterns = [
                "/help",
                "/guide",
                "/login",
                "/signup",
                "/search",
                "/categories",
                "eagle-insight.com",  # トラッキングリンクを除外
                "redirect",           # リダイレクトリンクを除外
                "rurl=",              # リダイレクトパラメータを含むリンクを除外
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
                                
                                # メルカリの商品リンクパターンを検出
                                # /item/m12345678901 形式も商品リンクとして認識
                                # /jp/items/ を優先的に探す（メルカリの正しいURL形式）
                                # jp.mercari.com と www.mercari.com の両方に対応
                                is_item_link = (
                                    "/jp/items/" in href or 
                                    "/items/" in href or 
                                    "/item/m" in href or  # /item/m12345678901 形式
                                    "/item/" in href or   # その他の /item/ 形式
                                    "mercari.com/jp/items/" in href or 
                                    "jp.mercari.com/jp/items/" in href
                                )
                                
                                if is_item_link:
                                    # 除外パターンをチェック
                                    should_exclude = any(pattern in href for pattern in exclude_patterns)
                                    if should_exclude:
                                        continue

                                    # 商品IDパターンをチェック（/jp/items/数字、/items/数字、/item/m数字 の形式）
                                    item_id_patterns = [
                                        r'/jp/items/([a-zA-Z0-9]+)',  # 優先: /jp/items/m12345678901
                                        r'/items/([a-zA-Z0-9]+)',     # /items/m12345678901
                                        r'/item/m([0-9]+)',           # /item/m12345678901 形式
                                        r'/item/([a-zA-Z0-9]+)',      # その他の /item/ 形式
                                    ]
                                    
                                    matched = False
                                    for pattern in item_id_patterns:
                                        if re.search(pattern, href):
                                            matched = True
                                            break
                                    
                                    # 商品リンクパターンに一致する場合は商品リンクとみなす
                                    if matched:
                                        # フルURLに変換（jp.mercari.com と www.mercari.com の両方に対応）
                                        if href.startswith("http"):
                                            # 既にフルURLの場合はそのまま使用
                                            full_url = href
                                            # jp.mercari.com の場合は www.mercari.com に統一
                                            if "jp.mercari.com" in full_url:
                                                full_url = full_url.replace("jp.mercari.com", "www.mercari.com")
                                        elif href.startswith("/"):
                                            # /item/m12345678901 形式を /jp/items/m12345678901 に変換
                                            if href.startswith("/item/m") or href.startswith("/item/"):
                                                # /item/m12345678901 → /jp/items/m12345678901
                                                full_url = href.replace("/item/", "/jp/items/")
                                                if not full_url.startswith("http"):
                                                    full_url = f"https://www.mercari.com{full_url}"
                                            # /jp/items/ で始まる場合はそのまま
                                            elif href.startswith("/jp/items/"):
                                                full_url = f"https://www.mercari.com{href}"
                                            # /items/ を /jp/items/ に変換
                                            elif href.startswith("/items/"):
                                                full_url = href.replace("/items/", "/jp/items/")
                                                if not full_url.startswith("http"):
                                                    full_url = f"https://www.mercari.com{full_url}"
                                            else:
                                                full_url = f"https://www.mercari.com{href}"
                                        else:
                                            full_url = f"https://www.mercari.com/{href}"
                                        
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
                    import traceback
                    traceback.print_exc()
                    continue

            # リンクが見つからない場合、ページの構造を確認
            if not item_links:
                print("\n⚠️  商品リンクが見つかりません。ページ構造を確認します...")
                print(f"現在のURL: {page.url}")
                print(f"ページタイトル: {page.title()}")
                
                # すべてのリンクを取得してデバッグ
                print("\n=== デバッグ: ページ内のすべてのリンクを確認 ===")
                all_links = page.locator("a").all()
                print(f"見つかったリンクの総数: {len(all_links)}")
                
                item_related_links = []
                for i, link in enumerate(all_links[:20]):  # 最初の20件だけ表示
                    try:
                        href = link.get_attribute("href")
                        if href and ("item" in href.lower() or "mercari" in href.lower()):
                            item_related_links.append(href)
                            if len(item_related_links) <= 10:
                                print(f"  {len(item_related_links)}. {href}")
                    except:
                        pass
                
                if item_related_links:
                    print(f"\n{len(item_related_links)} 件のitem関連リンクが見つかりました")
                    print("これらのリンクから商品リンクを抽出します...")
                    # 見つかったリンクから商品リンクを抽出
                    for href in item_related_links:
                        # リダイレクトリンクを除外
                        if "eagle-insight.com" in href or "redirect" in href.lower() or "rurl=" in href:
                            continue
                        
                        # URLから実際の商品URLを抽出（リダイレクトパラメータから）
                        actual_url = href
                        if "rurl=" in href:
                            import urllib.parse
                            try:
                                parsed = urllib.parse.urlparse(href)
                                params = urllib.parse.parse_qs(parsed.query)
                                if "rurl" in params:
                                    actual_url = params["rurl"][0]
                                    print(f"  リダイレクトURLから抽出: {actual_url}")
                            except:
                                pass
                        
                        # /item/m 形式も含めて商品リンクを検出
                        if "/jp/items/" in actual_url or "/items/" in actual_url or "/item/m" in actual_url or "/item/" in actual_url or "mercari.com/jp/items/" in actual_url or "jp.mercari.com/jp/items/" in actual_url:
                            # 商品IDパターンをチェック
                            if (re.search(r'/jp/items/([a-zA-Z0-9]+)', actual_url) or 
                                re.search(r'/items/([a-zA-Z0-9]+)', actual_url) or
                                re.search(r'/item/m([0-9]+)', actual_url) or
                                re.search(r'/item/([a-zA-Z0-9]+)', actual_url)):
                                if actual_url.startswith("http"):
                                    full_url = actual_url
                                    # jp.mercari.com の場合は www.mercari.com に統一
                                    if "jp.mercari.com" in full_url:
                                        full_url = full_url.replace("jp.mercari.com", "www.mercari.com")
                                    # /item/m 形式の場合は /jp/items/ に変換
                                    if "/item/m" in full_url or "/item/" in full_url:
                                        full_url = full_url.replace("/item/", "/jp/items/")
                                elif actual_url.startswith("/"):
                                    # /item/m 形式を /jp/items/ に変換
                                    if actual_url.startswith("/item/m") or actual_url.startswith("/item/"):
                                        full_url = actual_url.replace("/item/", "/jp/items/")
                                        full_url = f"https://www.mercari.com{full_url}"
                                    else:
                                        full_url = f"https://www.mercari.com{actual_url}"
                                else:
                                    continue
                                
                                if full_url not in item_links:
                                    item_links.append(full_url)
                                    print(f"  商品リンク {len(item_links)}: {full_url}")
                
                # HTMLの一部を保存して確認（デバッグ用）
                html_content = page.content()
                output_dir = Path(__file__).parent.parent.parent / "98_tmp"
                output_dir.mkdir(parents=True, exist_ok=True)
                html_file = output_dir / "mercari_page_structure.html"
                with open(html_file, "w", encoding="utf-8") as f:
                    f.write(html_content)
                print(f"\nHTMLを保存しました: {html_file}")
                print("このHTMLファイルを確認して、正しいセレクタを見つけてください。")

        except Exception as e:
            print(f"エラー: {e}")
            import traceback
            traceback.print_exc()
        finally:
            page.context.close()

        return item_links

    def scrape_detail(self, item_url: str, wait_time: int = 3000) -> Optional[Dict[str, Any]]:
        """
        商品詳細ページから情報を取得（ポケモンカード専用）

        Input:
            item_url: 商品詳細ページのURL
            wait_time: 読み込み待機時間(ミリ秒)

        Output:
            Dict[str, Any]: 商品情報の辞書
        """
        page = self.get_page()

        try:
            print(f"\n商品詳細ページにアクセス中: {item_url}")
            # URLが /item/ 形式の場合は /jp/items/ に変換（404エラーを防ぐため）
            if "/item/" in item_url and "/jp/items/" not in item_url:
                item_url = item_url.replace("/item/", "/jp/items/")
                print(f"  URLを修正しました: {item_url}")
            
            # ページが完全に読み込まれるまで待つ（タイムアウトを短く設定）
            try:
                page.goto(item_url, wait_until="domcontentloaded", timeout=60000)
            except:
                # domcontentloadedでタイムアウトした場合はcommitで試す
                try:
                    page.goto(item_url, wait_until="commit", timeout=30000)
                except:
                    print("  ⚠️  ページの読み込みに失敗しました")
                    return None
            
            page.wait_for_timeout(wait_time)  # 待機時間
            
            # Google翻訳のポップアップを閉じる（タイムアウト付き）
            try:
                page.wait_for_timeout(1000)  # 少し待ってからポップアップを閉じる
                # Google翻訳のポップアップを閉じる（複数のパターンを試す）
                translate_close_selectors = [
                    "button[aria-label='Close']",
                    ".goog-te-banner-frame + button",
                    "button:has-text('×')",
                    "button:has-text('X')",
                    "[class*='translate'] button[aria-label*='Close']",
                    "[id*='google'] button",
                    "//button[@aria-label='Close']",  # XPath形式
                ]
                for selector in translate_close_selectors:
                    try:
                        if selector.startswith("//"):
                            close_button = page.locator(f"xpath={selector}")
                        else:
                            close_button = page.locator(selector).first
                        
                        if close_button.count() > 0:
                            try:
                                if close_button.is_visible(timeout=1000):
                                    close_button.click(timeout=2000)
                                    print("  Google翻訳のポップアップを閉じました")
                                    page.wait_for_timeout(500)
                                    break
                            except:
                                # 可視性チェックなしでクリックを試す
                                try:
                                    close_button.click(timeout=2000)
                                    print("  Google翻訳のポップアップを閉じました（可視性チェックなし）")
                                    page.wait_for_timeout(500)
                                    break
                                except:
                                    continue
                    except:
                        continue
            except Exception as e:
                # エラーが発生しても続行
                pass
            
            # 404エラーチェック（ページタイトルとURLも確認）
            # まずページが完全に読み込まれるまで待機
            try:
                page.wait_for_load_state("networkidle", timeout=5000)
            except:
                pass
            
            page_title = page.title()
            page_text = page.inner_text("body")
            current_url = page.url
            
            # 404エラーのパターンをチェック（より確実に）
            is_404 = (
                "404" in page_text or 
                "Sorry this page couldn't be found" in page_text or 
                "ページが見つかりません" in page_text or
                "404" in page_title or
                "/404" in current_url or
                "error" in page_title.lower() or
                "Not found" in page_text or
                "couldn't be found" in page_text.lower() or
                "404 error" in page_text.lower()
            )
            
            # CAPTCHA（人間確認）のチェック
            is_captcha = (
                "あなたが人間であることを確認してください" in page_text or
                "I'm not a robot" in page_text or
                "reCAPTCHA" in page_text or
                "captcha" in page_text.lower() or
                "verify you are human" in page_text.lower() or
                "verify" in page_text.lower() and "human" in page_text.lower()
            )
            
            if is_404:
                print("  ⚠️  404エラー: この商品は存在しないか削除されています")
                print(f"  URL: {item_url}")
                print(f"  ページタイトル: {page_title}")
                return None
            
            if is_captcha:
                print("  ⚠️  CAPTCHA（人間確認）が表示されています")
                print("  この商品はスキップします")
                print(f"  URL: {item_url}")
                return None
            
            # Google翻訳のポップアップを再度閉じる（クッキー同意前に表示される場合がある）
            try:
                page.wait_for_timeout(1000)
                # iframe内のGoogle翻訳を閉じる
                frames = page.frames
                for frame in frames:
                    try:
                        close_btn = frame.locator("button[aria-label='Close'], button:has-text('×'), button:has-text('X')").first
                        if close_btn.count() > 0:
                            close_btn.click(timeout=2000)
                            print("  Google翻訳のポップアップを閉じました（iframe内）")
                            page.wait_for_timeout(500)
                    except:
                        continue
            except:
                pass
            
            # クッキー同意ボタンがあればクリック（メルカリのクッキー同意をスキップ）
            cookie_selectors = [
                "button:has-text('Got it')",
                "button:has-text('同意する')",
                "button:has-text('OK')",
                "button:has-text('Accept')",
                "[data-testid='cookie-accept']",
                ".cookie-accept-button",
                "//button[contains(text(), 'Got it')]",  # XPath形式も試す
            ]
            
            cookie_clicked = False
            for selector in cookie_selectors:
                try:
                    if selector.startswith("//"):
                        # XPath形式
                        cookie_button = page.locator(f"xpath={selector}")
                    else:
                        cookie_button = page.locator(selector).first
                    
                    if cookie_button.count() > 0:
                        # 可視性をチェック（タイムアウト付き）
                        try:
                            if cookie_button.is_visible(timeout=2000):
                                cookie_button.click(timeout=3000)
                                print("  クッキー同意ボタンをクリックしました")
                                page.wait_for_timeout(2000)  # クッキー同意後の待機
                                cookie_clicked = True
                                break
                        except:
                            # 可視性チェックが失敗してもクリックを試す
                            try:
                                cookie_button.click(timeout=3000)
                                print("  クッキー同意ボタンをクリックしました（可視性チェックなし）")
                                page.wait_for_timeout(2000)
                                cookie_clicked = True
                                break
                            except:
                                continue
                except Exception as e:
                    continue
            
            # クッキー同意後にページを再読み込み（商品情報が表示されるように）
            if cookie_clicked:
                try:
                    page.reload(wait_until="networkidle", timeout=30000)
                    page.wait_for_timeout(2000)
                except:
                    pass
            
            # 商品情報が表示されるまで待つ
            try:
                # 商品名または価格が表示されるまで待機
                page.wait_for_selector("h1, [data-testid='item-name'], .item-name, .item-detail-name", timeout=10000)
            except:
                pass
            
            # ページを再読み込み（クッキー同意後）
            page.wait_for_timeout(1000)

            # ポケモンカードに特化した情報項目
            item_info = {
                "url": item_url,
                "title": "",              # カード名・タイトル
                "price": "",              # 価格
                "description": "",        # 説明
                "condition": "",          # 商品の状態（美品、未使用など）
                "shipping": "",           # 送料
                "seller": "",            # 出品者
                "category": "",          # カテゴリー
                # ポケモンカード特有の情報
                "card_name": "",         # カード名（タイトルから抽出）
                "rarity": "",            # レアリティ（SR、UR、HRなど）
                "set_name": "",          # セット名
                "card_number": "",       # カード番号
                "pokemon_type": "",      # ポケモンのタイプ（炎、水など）
                "image_url": "",         # 画像URL
                "posted_date": "",       # 出品日
                "sold_status": "",       # 売却状況
            }

            # ページ全体のテキストを取得（フォールバック用）
            page_text = page.inner_text("body")

            # タイトルを取得（複数のセレクタを試す）
            # メルカリの実際の構造に合わせたセレクタ
            title_selectors = [
                "h1[data-testid='item-name']",
                "h1.item-name",
                "h1.item-detail-name",
                "h1",
                "[data-testid='item-name']",
                ".item-name",
                "section[data-testid='item-name'] h1",
                "section[data-testid='item-name']",
                ".item-detail-name",
                "article h1",
                "main h1",
            ]
            for selector in title_selectors:
                try:
                    title_elem = page.locator(selector).first
                    if title_elem.count() > 0:
                        title_text = title_elem.inner_text().strip()
                        # 「Privacy settings」などの不要なテキストを除外
                        if title_text and len(title_text) > 0 and "Privacy" not in title_text and "メルカリ" not in title_text:
                            item_info["title"] = title_text
                            item_info["card_name"] = title_text  # カード名としても保存
                            print(f"  タイトル取得: {title_text[:50]}")
                            break
                except Exception as e:
                    continue

            # タイトルが取得できなかった場合、ページ全体から探す
            if not item_info["title"] or item_info["title"] == "Privacy settings" or "cookies" in item_info.get("title", "").lower():
                try:
                    # ページ全体のテキストから商品名らしい部分を探す
                    page_text = page.inner_text("body")
                    
                    # クッキーメッセージやプライバシー設定を除外
                    lines = page_text.split("\n")
                    for line in lines:
                        line = line.strip()
                        # 商品名らしい行を探す（長さが5文字以上で、クッキーやプライバシー関連でない）
                        if (len(line) > 5 and 
                            "cookie" not in line.lower() and 
                            "privacy" not in line.lower() and
                            "同意" not in line and
                            "メルカリ" not in line and
                            "ログイン" not in line and
                            "会員登録" not in line):
                            item_info["title"] = line[:200]
                            item_info["card_name"] = item_info["title"]
                            print(f"  タイトル取得（フォールバック）: {item_info['title'][:50]}")
                            break
                except Exception as e:
                    print(f"  タイトル取得エラー: {e}")
                    pass

            # 価格を取得
            price_selectors = [
                "[data-testid='price']",
                ".item-price",
                ".price",
                "[class*='price']",
                "span:has-text('¥')",
                "span:has-text('円')",
                "div:has-text('¥')",
                "section[data-testid='price']",
            ]
            for selector in price_selectors:
                try:
                    price_elem = page.locator(selector).first
                    if price_elem.count() > 0:
                        price_text = price_elem.inner_text().strip()
                        if price_text and ("¥" in price_text or "円" in price_text or re.search(r'[0-9,]+', price_text)):
                            # 価格の数値部分を抽出
                            price_match = re.search(r'([¥¥]?[0-9,]+)', price_text.replace(',', ''))
                            if price_match:
                                item_info["price"] = price_match.group(1)
                                print(f"  価格取得: {item_info['price']}")
                            else:
                                item_info["price"] = price_text
                            if item_info["price"]:
                                break
                except:
                    continue
            
            # 価格が取得できなかった場合、ページ全体から探す
            if not item_info["price"]:
                try:
                    page_text = page.inner_text("body")
                    # 価格パターンを探す
                    price_patterns = [
                        r'¥\s*([0-9,]+)',
                        r'([0-9,]+)\s*円',
                        r'現在\s*¥\s*([0-9,]+)',
                    ]
                    for pattern in price_patterns:
                        match = re.search(pattern, page_text)
                        if match:
                            item_info["price"] = f"¥{match.group(1)}"
                            print(f"  価格取得（フォールバック）: {item_info['price']}")
                            break
                except:
                    pass

            # 説明を取得
            desc_selectors = [
                "[data-testid='item-description']",
                ".item-description",
                ".description",
                "[class*='description']",
                ".item-detail-description",
            ]
            for selector in desc_selectors:
                try:
                    desc_elem = page.locator(selector).first
                    if desc_elem.count() > 0:
                        desc_text = desc_elem.inner_text().strip()
                        if desc_text and len(desc_text) > 10:
                            item_info["description"] = desc_text[:5000]  # 最大5000文字
                            if item_info["description"]:
                                break
                except:
                    continue

            # 商品の状態を取得
            condition_selectors = [
                "[data-testid='item-condition']",
                ".item-condition",
                "text=商品の状態",
            ]
            for selector in condition_selectors:
                try:
                    if selector.startswith("text="):
                        condition_elem = page.locator(selector).first
                        if condition_elem.count() > 0:
                            parent = condition_elem.locator("..")
                            if parent.count() > 0:
                                condition_text = parent.inner_text().strip()
                                if "商品の状態" in condition_text:
                                    parts = condition_text.split("商品の状態")
                                    if len(parts) > 1:
                                        item_info["condition"] = parts[1].strip()[:100]
                    else:
                        condition_elem = page.locator(selector).first
                        if condition_elem.count() > 0:
                            item_info["condition"] = condition_elem.inner_text().strip()
                            if item_info["condition"]:
                                break
                except:
                    continue

            # 送料情報を取得
            shipping_selectors = [
                "[data-testid='shipping-fee']",
                "text=送料",
                ".shipping-fee",
            ]
            for selector in shipping_selectors:
                try:
                    if selector.startswith("text="):
                        shipping_elem = page.locator(selector).first
                        if shipping_elem.count() > 0:
                            parent = shipping_elem.locator("..")
                            if parent.count() > 0:
                                shipping_text = parent.inner_text().strip()
                                if "送料" in shipping_text:
                                    parts = shipping_text.split("送料")
                                    if len(parts) > 1:
                                        item_info["shipping"] = parts[1].strip()[:100]
                    else:
                        shipping_elem = page.locator(selector).first
                        if shipping_elem.count() > 0:
                            item_info["shipping"] = shipping_elem.inner_text().strip()
                            if item_info["shipping"]:
                                break
                except:
                    continue

            # カテゴリーを取得
            category_selectors = [
                "[data-testid='category']",
                ".item-category",
                "text=カテゴリー",
            ]
            for selector in category_selectors:
                try:
                    if selector.startswith("text="):
                        category_elem = page.locator(selector).first
                        if category_elem.count() > 0:
                            parent = category_elem.locator("..")
                            if parent.count() > 0:
                                category_text = parent.inner_text().strip()
                                if "カテゴリー" in category_text:
                                    parts = category_text.split("カテゴリー")
                                    if len(parts) > 1:
                                        item_info["category"] = parts[1].strip()[:200]
                    else:
                        category_elem = page.locator(selector).first
                        if category_elem.count() > 0:
                            item_info["category"] = category_elem.inner_text().strip()
                            if item_info["category"]:
                                break
                except:
                    continue

            # 画像URLを取得
            image_selectors = [
                "[data-testid='item-image'] img",
                ".item-image img",
                ".item-photo img",
                "img[alt*='商品画像']",
                ".item-detail-image img",
            ]
            for selector in image_selectors:
                try:
                    img_elem = page.locator(selector).first
                    if img_elem.count() > 0:
                        img_src = img_elem.get_attribute("src")
                        if img_src:
                            item_info["image_url"] = img_src
                            break
                except:
                    continue

            # ポケモンカード特有の情報を説明から抽出
            if item_info.get("description"):
                desc_text = item_info["description"]
                
                # レアリティを抽出（SR、UR、HR、RR、Rなど）
                rarity_patterns = [
                    r'(SR|UR|HR|RR|R|SRR|URR|HRR|PR|SRR|CSR|SAR)',
                    r'レアリティ[：:]\s*([^\s]+)',
                    r'レア度[：:]\s*([^\s]+)',
                ]
                for pattern in rarity_patterns:
                    match = re.search(pattern, desc_text, re.IGNORECASE)
                    if match:
                        item_info["rarity"] = match.group(1) if match.lastindex else match.group(0)
                        break

                # セット名を抽出
                set_patterns = [
                    r'セット[：:]\s*([^\n]+)',
                    r'拡張パック[：:]\s*([^\n]+)',
                    r'([^\s]+拡張パック)',
                ]
                for pattern in set_patterns:
                    match = re.search(pattern, desc_text)
                    if match:
                        item_info["set_name"] = match.group(1) if match.lastindex else match.group(0)
                        break

                # カード番号を抽出
                card_number_patterns = [
                    r'カード番号[：:]\s*([^\s]+)',
                    r'No\.\s*([0-9]+)',
                    r'#([0-9]+)',
                ]
                for pattern in card_number_patterns:
                    match = re.search(pattern, desc_text)
                    if match:
                        item_info["card_number"] = match.group(1) if match.lastindex else match.group(0)
                        break

            # タイトルからも情報を抽出
            if item_info.get("title"):
                title_text = item_info["title"]
                
                # レアリティがまだ取得できていない場合、タイトルから抽出
                if not item_info.get("rarity"):
                    rarity_match = re.search(r'(SR|UR|HR|RR|R|SRR|URR|HRR|PR)', title_text, re.IGNORECASE)
                    if rarity_match:
                        item_info["rarity"] = rarity_match.group(1)

            return item_info

        except Exception as e:
            print(f"商品詳細の取得でエラー: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            page.context.close()
