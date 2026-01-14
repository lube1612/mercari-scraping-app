"""
CrowdWorks案件情報スクレイピングスクリプト（e2eモジュール使用版）

【使用方法】
python scrape_crowdworks.py

【処理内容】
1. e2eフォルダのモジュールを使用してPlaywrightでページにアクセス
2. 案件一覧ページから案件リンクを取得
3. 各案件の詳細ページから情報を取得
4. 1件取得したら停止して確認を求める
5. CSVファイルに出力
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional, Any
import csv
import re
import time

# e2eフォルダのモジュールをインポート
from dom_xpath_handler import DomXPathHandler
from playwright.sync_api import sync_playwright, Page, Browser


class CrowdWorksScraperE2E:
    """
    e2eモジュールを使用してCrowdWorksの案件情報をスクレイピングするクラス
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
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        return context.new_page()

    def scrape_job_list(self, url: str, wait_time: int = 3000) -> List[str]:
        """
        案件一覧ページから案件リンクを取得

        Input:
            url: 案件一覧ページのURL
            wait_time: 読み込み待機時間(ミリ秒)

        Output:
            List[str]: 案件詳細ページのURLリスト
        """
        page = self.get_page()
        job_links = []

        try:
            print(f"案件一覧ページにアクセス中: {url}")
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(wait_time)

            # ページのHTMLを取得して構造を確認
            html_content = page.content()
            print(f"ページHTMLの長さ: {len(html_content)} 文字")

            # 案件リンクを探す（複数のセレクタを試す）
            selectors = [
                "a[href*='/public/jobs/']",
                "a[href*='/jobs/']",
                ".job-item a",
                ".job-list-item a",
                "[data-job-id] a",
                "article a",
                ".card a"
            ]

            # 除外するURLパターン
            exclude_patterns = [
                "/category/",
                "/group/",
                "/search",
                "/login",
                "/signup",
                "/help",
                "/about"
            ]

            for selector in selectors:
                try:
                    links = page.locator(selector).all()
                    if links:
                        print(f"セレクタ '{selector}' で {len(links)} 件のリンクを発見")
                        for link in links:
                            href = link.get_attribute("href")
                            if href and "/jobs/" in href:
                                # 除外パターンをチェック
                                should_exclude = any(pattern in href for pattern in exclude_patterns)
                                if should_exclude:
                                    continue

                                # 案件詳細ページのURLパターンをチェック
                                job_id_pattern = r'/jobs/(\d+)(?:/|$)'
                                if re.search(job_id_pattern, href):
                                    full_url = href if href.startswith("http") else f"https://crowdworks.jp{href}"
                                    if full_url not in job_links:
                                        job_links.append(full_url)
                                        print(f"  案件リンク: {full_url}")

                        if job_links:
                            print(f"合計 {len(job_links)} 件の案件リンクを発見")
                            break
                except Exception as e:
                    print(f"セレクタ '{selector}' でエラー: {e}")
                    continue

            # リンクが見つからない場合
            if not job_links:
                print("案件リンクが見つかりません。ページ構造を確認します...")
                page_text = page.inner_text("body")
                print(f"ページテキストの最初の500文字:\n{page_text[:500]}")

        finally:
            page.context.close()

        return job_links

    def scrape_job_detail(self, job_url: str, wait_time: int = 3000) -> Optional[Dict[str, Any]]:
        """
        案件詳細ページから情報を取得

        Input:
            job_url: 案件詳細ページのURL
            wait_time: 読み込み待機時間(ミリ秒)

        Output:
            Dict[str, Any]: 案件情報の辞書
        """
        page = self.get_page()

        try:
            print(f"\n案件詳細ページにアクセス中: {job_url}")
            page.goto(job_url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(wait_time)

            job_info = {
                "url": job_url,
                "title": "",
                "description": "",
                "price": "",
                "deadline": "",
                "category": "",
                "skills": "",
                "client_info": "",
                "posted_date": "",
                "applicants": "",
                "status": "",
            }

            # タイトルを取得
            title_selectors = [
                "h1.job-title",
                "h1",
                ".job-title",
                "[data-job-title]",
            ]
            for selector in title_selectors:
                try:
                    title_elem = page.locator(selector).first
                    if title_elem.count() > 0:
                        title_text = title_elem.inner_text().strip()
                        if title_text and "クラウドワークス" not in title_text:
                            job_info["title"] = title_text
                            if job_info["title"]:
                                break
                except Exception as e:
                    continue

            # タイトルが取得できなかった場合、titleタグから取得
            if not job_info["title"] or "クラウドワークス" in job_info["title"]:
                try:
                    title_tag = page.title()
                    if "のお仕事" in title_tag:
                        job_info["title"] = title_tag.split("のお仕事")[0].strip()
                    elif "|" in title_tag:
                        job_info["title"] = title_tag.split("|")[0].strip()
                except:
                    pass

            # 説明を取得
            desc_selectors = [
                ".job-description",
                ".description",
                "[data-description]",
                ".job-detail",
                ".detail-content",
                "article .content",
                ".content-body",
                ".job-detail-content",
                "#job-detail",
                "[class*='detail']",
                "[class*='description']"
            ]
            for selector in desc_selectors:
                try:
                    desc_elem = page.locator(selector).first
                    if desc_elem.count() > 0:
                        desc_text = desc_elem.inner_text().strip()
                        if desc_text and len(desc_text) > 50:
                            job_info["description"] = desc_text[:5000]  # 最大5000文字
                            if job_info["description"]:
                                break
                except:
                    continue

            # 価格を取得
            page_text = page.inner_text("body")
            price_selectors = [
                "[data-price]",
                ".price",
                ".budget",
                ".job-budget",
                "span:has-text('円')",
                "span:has-text('¥')",
                "dd:has-text('円')",
                "dt:has-text('予算') + dd",
                "dt:has-text('報酬') + dd",
                "[class*='budget']",
                "[class*='price']"
            ]
            for selector in price_selectors:
                try:
                    price_elem = page.locator(selector).first
                    if price_elem.count() > 0:
                        price_text = price_elem.inner_text().strip()
                        if price_text and ("円" in price_text or "¥" in price_text or "万円" in price_text):
                            price_match = re.search(r'([0-9,]+[万円円]+)', price_text)
                            if price_match:
                                job_info["price"] = price_match.group(1)
                            else:
                                job_info["price"] = price_text
                            if job_info["price"]:
                                break
                except:
                    continue

            # テキストから価格を抽出
            if not job_info["price"]:
                price_patterns = [
                    r'予算[：:]\s*([0-9,]+[万円円]+)',
                    r'報酬[：:]\s*([0-9,]+[万円円]+)',
                    r'([0-9,]+[万円円]+)',
                ]
                for pattern in price_patterns:
                    match = re.search(pattern, page_text)
                    if match:
                        job_info["price"] = match.group(1) if match.lastindex else match.group(0)
                        break

            # 応募期限を取得
            try:
                deadline_elem = page.locator("text=応募期限").first
                if deadline_elem.count() > 0:
                    parent = deadline_elem.locator("..")
                    if parent.count() > 0:
                        deadline_text = parent.inner_text().strip()
                        date_match = re.search(r'応募期限\s*(\d{4}年\d{1,2}月\d{1,2}日|\d{1,2}/\d{1,2}|\d{1,2}月\d{1,2}日)', deadline_text)
                        if date_match:
                            job_info["deadline"] = date_match.group(1)
                        elif "応募期限" in deadline_text:
                            parts = deadline_text.split("応募期限")
                            if len(parts) > 1:
                                date_match = re.search(r'(\d{4}年\d{1,2}月\d{1,2}日|\d{1,2}/\d{1,2}|\d{1,2}月\d{1,2}日)', parts[1])
                                if date_match:
                                    job_info["deadline"] = date_match.group(1)
                                else:
                                    job_info["deadline"] = parts[1].strip()[:100]
            except:
                pass

            # 掲載日を取得
            try:
                posted_elem = page.locator("text=掲載日").first
                if posted_elem.count() > 0:
                    parent = posted_elem.locator("..")
                    if parent.count() > 0:
                        posted_text = parent.inner_text().strip()
                        date_match = re.search(r'掲載日\s*(\d{4}年\d{1,2}月\d{1,2}日|\d{1,2}/\d{1,2}|\d{1,2}月\d{1,2}日)', posted_text)
                        if date_match:
                            job_info["posted_date"] = date_match.group(1)
            except:
                pass

            # 応募者数を取得
            try:
                applicants_elem = page.locator("text=応募した人").first
                if applicants_elem.count() > 0:
                    parent = applicants_elem.locator("..")
                    if parent.count() > 0:
                        applicants_text = parent.inner_text().strip()
                        match = re.search(r'応募した人\s*(\d+)\s*人', applicants_text)
                        if match:
                            job_info["applicants"] = f"{match.group(1)}人"
            except:
                pass

            # カテゴリーを取得
            try:
                category_elem = page.locator("text=カテゴリ").first
                if category_elem.count() > 0:
                    parent = category_elem.locator("..")
                    if parent.count() > 0:
                        category_text = parent.inner_text().strip()
                        if "カテゴリ" in category_text:
                            parts = category_text.split("カテゴリ")
                            if len(parts) > 1:
                                job_info["category"] = parts[1].strip()[:200]
            except:
                pass

            # クライアント情報を取得
            try:
                client_elem = page.locator("text=クライアント").first
                if client_elem.count() > 0:
                    parent = client_elem.locator("..")
                    if parent.count() > 0:
                        client_text = parent.inner_text().strip()
                        if "クライアント" in client_text:
                            parts = client_text.split("クライアント")
                            if len(parts) > 1:
                                job_info["client_info"] = parts[1].strip()[:200]
            except:
                pass

            # ページ全体のテキストから追加情報を抽出
            if not job_info.get("deadline"):
                deadline_match = re.search(r'応募期限\s*(\d{4}年\d{1,2}月\d{1,2}日|\d{1,2}/\d{1,2}|\d{1,2}月\d{1,2}日)', page_text)
                if deadline_match:
                    job_info["deadline"] = deadline_match.group(1)

            if not job_info.get("posted_date"):
                posted_match = re.search(r'掲載日\s*(\d{4}年\d{1,2}月\d{1,2}日|\d{1,2}/\d{1,2}|\d{1,2}月\d{1,2}日)', page_text)
                if posted_match:
                    job_info["posted_date"] = posted_match.group(1)

            if not job_info.get("applicants"):
                applicants_match = re.search(r'応募した人\s*(\d+)\s*人', page_text)
                if applicants_match:
                    job_info["applicants"] = f"{applicants_match.group(1)}人"

            return job_info

        except Exception as e:
            print(f"案件詳細の取得でエラー: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            page.context.close()

    def save_to_csv(self, jobs_data: List[Dict[str, Any]], output_path: str, encoding: str = "utf-8-sig") -> str:
        """
        案件情報をCSVファイルに保存

        Input:
            jobs_data: 案件情報のリスト
            output_path: 出力ファイルパス
            encoding: エンコーディング（デフォルト: utf-8-sig for Excel）

        Output:
            str: 保存されたファイルのパス
        """
        if not jobs_data:
            print("保存するデータがありません。")
            return ""

        output_path_obj = Path(output_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)

        # すべてのキーを取得
        all_keys = set()
        for job in jobs_data:
            all_keys.update(job.keys())

        fieldnames = sorted(list(all_keys))

        with open(output_path, "w", newline="", encoding=encoding) as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for job in jobs_data:
                row = {key: job.get(key, "") for key in fieldnames}
                writer.writerow(row)

        print(f"\nCSVファイルを保存しました: {output_path}")
        return str(output_path_obj.absolute())

    def format_job_data(self, job_data: Dict[str, Any]) -> str:
        """
        案件データを読みやすい形式でフォーマット

        Input:
            job_data: 案件情報の辞書

        Output:
            str: フォーマットされた文字列
        """
        lines = []
        for key, value in job_data.items():
            if value:  # 空でない値のみ表示
                lines.append(f"{key}: {value}")
        return "\n".join(lines)


def main():
    """
    メイン処理
    """
    # スクレイピング対象URL（ここを変更してください）
    target_url = "https://crowdworks.jp/public/jobs/group/ec"

    print("=" * 60)
    print("CrowdWorks案件情報スクレイピング開始")
    print("=" * 60)
    print(f"対象URL: {target_url}")
    print(f"e2eモジュールを使用してスクレイピングを実行します")
    print()

    jobs_data = []

    try:
        with CrowdWorksScraperE2E(headless=False) as scraper:
            # 案件一覧ページから案件リンクを取得
            job_links = scraper.scrape_job_list(target_url)

            if not job_links:
                print("案件リンクが見つかりませんでした。")
                return

            print(f"\n{len(job_links)} 件の案件リンクを発見しました。")
            print("1件目の案件情報を取得します...\n")

            # 1件目の案件情報を取得
            job_info = scraper.scrape_job_detail(job_links[0])

            if job_info:
                jobs_data.append(job_info)

                # 取得したデータを表示
                print("\n" + "=" * 60)
                print("取得した案件情報:")
                print("=" * 60)
                print(scraper.format_job_data(job_info))
                print("=" * 60)

                # CSVに保存
                output_path = "crowdworks_jobs.csv"
                scraper.save_to_csv(jobs_data, output_path)

                print("\n" + "=" * 60)
                print("1件のデータを取得しました。")
                print("=" * 60)
                print("データの確認をお願いします。")
                print(f"CSVファイル: {output_path}")
                print("\n続行する場合は、スクリプトを再実行してください。")
                print("=" * 60)

            else:
                print("案件情報の取得に失敗しました。")

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
