"""
CrowdWorks案件情報スクレイパー

共通のBaseScraperを継承してCrowdWorks専用の実装を行います。
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional, Any
import re

# 親ディレクトリのパスを追加して共通モジュールをインポート
sys.path.insert(0, str(Path(__file__).parent.parent))
from common.base_scraper import BaseScraper


class CrowdWorksScraper(BaseScraper):
    """
    CrowdWorksの案件情報をスクレイピングするクラス
    """

    def scrape_list(self, url: str, wait_time: int = 3000) -> List[str]:
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

            # 案件リンクを探す
            selectors = [
                "a[href*='/public/jobs/']",
                "a[href*='/jobs/']",
                ".job-item a",
                ".job-list-item a",
                "[data-job-id] a",
                "article a",
                ".card a"
            ]

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
                                should_exclude = any(pattern in href for pattern in exclude_patterns)
                                if should_exclude:
                                    continue

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

        finally:
            page.context.close()

        return job_links

    def scrape_detail(self, job_url: str, wait_time: int = 3000) -> Optional[Dict[str, Any]]:
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
            title_selectors = ["h1.job-title", "h1", ".job-title", "[data-job-title]"]
            for selector in title_selectors:
                try:
                    title_elem = page.locator(selector).first
                    if title_elem.count() > 0:
                        title_text = title_elem.inner_text().strip()
                        if title_text and "クラウドワークス" not in title_text:
                            job_info["title"] = title_text
                            if job_info["title"]:
                                break
                except:
                    continue

            if not job_info["title"]:
                try:
                    title_tag = page.title()
                    if "のお仕事" in title_tag:
                        job_info["title"] = title_tag.split("のお仕事")[0].strip()
                except:
                    pass

            # 説明を取得
            desc_selectors = [
                ".job-description", ".description", "[data-description]",
                ".job-detail", ".detail-content", "article .content"
            ]
            for selector in desc_selectors:
                try:
                    desc_elem = page.locator(selector).first
                    if desc_elem.count() > 0:
                        desc_text = desc_elem.inner_text().strip()
                        if desc_text and len(desc_text) > 50:
                            job_info["description"] = desc_text[:5000]
                            if job_info["description"]:
                                break
                except:
                    continue

            # 価格を取得
            page_text = page.inner_text("body")
            price_selectors = [
                "[data-price]", ".price", ".budget", ".job-budget",
                "span:has-text('円')", "dd:has-text('円')"
            ]
            for selector in price_selectors:
                try:
                    price_elem = page.locator(selector).first
                    if price_elem.count() > 0:
                        price_text = price_elem.inner_text().strip()
                        if price_text and ("円" in price_text or "¥" in price_text):
                            price_match = re.search(r'([0-9,]+[万円円]+)', price_text)
                            if price_match:
                                job_info["price"] = price_match.group(1)
                            else:
                                job_info["price"] = price_text
                            if job_info["price"]:
                                break
                except:
                    continue

            # その他の情報を取得
            if not job_info["price"]:
                price_match = re.search(r'([0-9,]+[万円円]+)', page_text)
                if price_match:
                    job_info["price"] = price_match.group(1)

            # 応募期限、掲載日、応募者数などを取得
            try:
                deadline_elem = page.locator("text=応募期限").first
                if deadline_elem.count() > 0:
                    parent = deadline_elem.locator("..")
                    if parent.count() > 0:
                        deadline_text = parent.inner_text().strip()
                        date_match = re.search(r'応募期限\s*(\d{4}年\d{1,2}月\d{1,2}日)', deadline_text)
                        if date_match:
                            job_info["deadline"] = date_match.group(1)
            except:
                pass

            return job_info

        except Exception as e:
            print(f"案件詳細の取得でエラー: {e}")
            return None
        finally:
            page.context.close()
