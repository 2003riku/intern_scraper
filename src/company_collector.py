"""
インターン情報自動取得システム - 企業情報収集モジュール
"""

import os
import re
import time
import logging
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from config import JOB_SITES, LISTED_COMPANIES_URL, COMPANIES_FILE, MAX_COMPANIES
from utils import get_soup, save_json, load_json, logger

class CompanyCollector:
    """就活サイトから企業情報を収集するクラス"""
    
    def __init__(self):
        self.companies = []
        self.company_ids = set()  # 重複チェック用
    
    def collect_listed_companies(self):
        """上場企業の情報を収集する"""
        logger.info("Collecting listed companies information...")
        
        try:
            soup = get_soup(LISTED_COMPANIES_URL)
            if not soup:
                logger.error(f"Failed to fetch listed companies from {LISTED_COMPANIES_URL}")
                return
            
            # 上場企業データの抽出（JPXのサイト構造に合わせて調整が必要）
            # 注: 実際のサイト構造に合わせてセレクタを調整する必要があります
            table = soup.find('table', class_='')  # 適切なクラスを指定
            if not table:
                logger.warning("Listed companies table not found")
                return
            
            rows = table.find_all('tr')[1:]  # ヘッダー行をスキップ
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 4:  # 必要な列数を確認
                    code = cols[0].text.strip()
                    name = cols[1].text.strip()
                    market = cols[3].text.strip()
                    
                    company_id = f"listed_{code}"
                    
                    if company_id not in self.company_ids:
                        self.companies.append({
                            "id": company_id,
                            "name": name,
                            "stock_code": code,
                            "market": market,
                            "source": "JPX",
                            "official_site": None,  # 後で補完
                            "career_site": None,    # 後で補完
                        })
                        self.company_ids.add(company_id)
            
            logger.info(f"Collected {len(self.companies)} listed companies")
            
        except Exception as e:
            logger.error(f"Error collecting listed companies: {e}")
    
    def collect_from_mynavi(self, max_pages=50):
        """マイナビから企業情報を収集する"""
        logger.info("Collecting companies from Mynavi...")
        
        base_url = JOB_SITES["mynavi"]["url"]
        companies_collected = 0
        
        for page in range(1, max_pages + 1):
            if companies_collected >= MAX_COMPANIES:
                break
                
            try:
                # ページネーションURLを構築
                page_url = f"{base_url}?page={page}"
                soup = get_soup(page_url)
                
                if not soup:
                    logger.error(f"Failed to fetch page {page} from Mynavi")
                    continue
                
                # 企業リストの要素を取得
                # 注: 実際のサイト構造に合わせてセレクタを調整する必要があります
                company_elements = soup.select('.corp-box')
                
                if not company_elements:
                    logger.warning(f"No companies found on page {page}, stopping pagination")
                    break
                
                for element in company_elements:
                    # 企業IDと名前を抽出
                    company_link = element.select_one('a.corp-name')
                    if not company_link:
                        continue
                        
                    company_url = company_link.get('href', '')
                    company_name = company_link.text.strip()
                    
                    # URLから企業IDを抽出
                    company_id_match = re.search(r'/corp/([^/]+)', company_url)
                    if not company_id_match:
                        continue
                        
                    company_id = f"mynavi_{company_id_match.group(1)}"
                    
                    # 重複チェック
                    if company_id in self.company_ids:
                        continue
                    
                    # 企業情報を保存
                    internship_url = JOB_SITES["mynavi"]["internship_url_pattern"].format(company_id_match.group(1))
                    
                    self.companies.append({
                        "id": company_id,
                        "name": company_name,
                        "source": "マイナビ",
                        "job_site_url": urljoin(base_url, company_url),
                        "internship_url": internship_url,
                        "official_site": None,  # 後で補完
                        "career_site": None,    # 後で補完
                    })
                    self.company_ids.add(company_id)
                    companies_collected += 1
                    
                    if companies_collected >= MAX_COMPANIES:
                        break
                
                logger.info(f"Collected {len(company_elements)} companies from Mynavi page {page}")
                
                # 次のページがあるか確認
                next_button = soup.select_one('.next a')
                if not next_button:
                    logger.info("No more pages available on Mynavi")
                    break
                    
                # ページ間の待機時間
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error collecting companies from Mynavi page {page}: {e}")
    
    def collect_from_rikunabi(self, max_pages=50):
        """リクナビから企業情報を収集する"""
        logger.info("Collecting companies from Rikunabi...")
        
        base_url = JOB_SITES["rikunabi"]["url"]
        companies_collected = 0
        
        for page in range(1, max_pages + 1):
            if companies_collected >= MAX_COMPANIES:
                break
                
            try:
                # ページネーションURLを構築
                page_url = f"{base_url}?page={page}"
                soup = get_soup(page_url)
                
                if not soup:
                    logger.error(f"Failed to fetch page {page} from Rikunabi")
                    continue
                
                # 企業リストの要素を取得
                # 注: 実際のサイト構造に合わせてセレクタを調整する必要があります
                company_elements = soup.select('.rnn-jobOfferList__item')
                
                if not company_elements:
                    logger.warning(f"No companies found on page {page}, stopping pagination")
                    break
                
                for element in company_elements:
                    # 企業IDと名前を抽出
                    company_link = element.select_one('a.rnn-jobOfferList__title')
                    if not company_link:
                        continue
                        
                    company_url = company_link.get('href', '')
                    company_name = company_link.text.strip()
                    
                    # URLから企業IDを抽出
                    company_id_match = re.search(r'/company/([^/]+)', company_url)
                    if not company_id_match:
                        continue
                        
                    company_id = f"rikunabi_{company_id_match.group(1)}"
                    
                    # 重複チェック
                    if company_id in self.company_ids:
                        continue
                    
                    # 企業情報を保存
                    internship_url = JOB_SITES["rikunabi"]["internship_url_pattern"].format(company_id_match.group(1))
                    
                    self.companies.append({
                        "id": company_id,
                        "name": company_name,
                        "source": "リクナビ",
                        "job_site_url": company_url,
                        "internship_url": internship_url,
                        "official_site": None,  # 後で補完
                        "career_site": None,    # 後で補完
                    })
                    self.company_ids.add(company_id)
                    companies_collected += 1
                    
                    if companies_collected >= MAX_COMPANIES:
                        break
                
                logger.info(f"Collected {len(company_elements)} companies from Rikunabi page {page}")
                
                # 次のページがあるか確認
                next_button = soup.select_one('.rnn-pagination__next:not(.rnn-pagination__next--disabled)')
                if not next_button:
                    logger.info("No more pages available on Rikunabi")
                    break
                    
                # ページ間の待機時間
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error collecting companies from Rikunabi page {page}: {e}")
    
    def collect_from_career_tasu(self, max_pages=50):
        """キャリタス就活から企業情報を収集する"""
        logger.info("Collecting companies from Career-Tasu...")
        
        base_url = JOB_SITES["career_tasu"]["url"]
        companies_collected = 0
        
        for page in range(1, max_pages + 1):
            if companies_collected >= MAX_COMPANIES:
                break
                
            try:
                # ページネーションURLを構築
                page_url = f"{base_url}?page={page}"
                soup = get_soup(page_url)
                
                if not soup:
                    logger.error(f"Failed to fetch page {page} from Career-Tasu")
                    continue
                
                # 企業リストの要素を取得
                # 注: 実際のサイト構造に合わせてセレクタを調整する必要があります
                company_elements = soup.select('.corp-box')
                
                if not company_elements:
                    logger.warning(f"No companies found on page {page}, stopping pagination")
                    break
                
                for element in company_elements:
                    # 企業IDと名前を抽出
                    company_link = element.select_one('a.corp-name')
                    if not company_link:
                        continue
                        
                    company_url = company_link.get('href', '')
                    company_name = company_link.text.strip()
                    
                    # URLから企業IDを抽出
                    company_id_match = re.search(r'/corp/detail/([^/]+)', company_url)
                    if not company_id_match:
                        continue
                        
                    company_id = f"career_tasu_{company_id_match.group(1)}"
                    
                    # 重複チェック
                    if company_id in self.company_ids:
                        continue
                    
                    # 企業情報を保存
                    internship_url = JOB_SITES["career_tasu"]["internship_url_pattern"].format(company_id_match.group(1))
                    
                    self.companies.append({
                        "id": company_id,
                        "name": company_name,
                        "source": "キャリタス就活",
                        "job_site_url": company_url,
                        "internship_url": internship_url,
                        "official_site": None,  # 後で補完
                        "career_site": None,    # 後で補完
                    })
                    self.company_ids.add(company_id)
                    companies_collected += 1
                    
                    if companies_collected >= MAX_COMPANIES:
                        break
                
                logger.info(f"Collected {len(company_elements)} companies from Career-Tasu page {page}")
                
                # 次のページがあるか確認
                next_button = soup.select_one('.pagination .next:not(.disabled)')
                if not next_button:
                    logger.info("No more pages available on Career-Tasu")
                    break
                    
                # ページ間の待機時間
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error collecting companies from Career-Tasu page {page}: {e}")
    
    def enrich_company_data(self):
        """収集した企業情報を充実させる（公式サイトURLなどを追加）"""
        logger.info("Enriching company data...")
        
        for i, company in enumerate(self.companies):
            if i % 10 == 0:
                logger.info(f"Enriching company {i+1}/{len(self.companies)}")
            
            try:
                # 就活サイトの企業ページから公式サイトURLを取得
                if "job_site_url" in company and company["job_site_url"]:
                    soup = get_soup(company["job_site_url"])
                    
                    if soup:
                        # 公式サイトURLを探す（サイトごとに異なる可能性があるため、複数のパターンを試す）
                        # 注: 実際のサイト構造に合わせてセレクタを調整する必要があります
                        official_site_element = None
                        
                        # パターン1: リンクテキストで探す
                        for link in soup.find_all('a'):
                            link_text = link.text.strip().lower()
                            if '公式' in link_text or '企業' in link_text or 'ホームページ' in link_text:
                                official_site_element = link
                                break
                        
                        # パターン2: 特定のセクションで探す
                        if not official_site_element:
                            sections = soup.select('.company-info, .corp-data, .basic-info')
                            for section in sections:
                                links = section.find_all('a')
                                if links:
                                    official_site_element = links[0]  # 最初のリンクを使用
                                    break
                        
                        if official_site_element:
                            company["official_site"] = official_site_element.get('href')
                
                # 採用サイトURLを推測（公式サイトURLがある場合）
                if company["official_site"]:
                    # 一般的な採用サイトのパターンを試す
                    career_patterns = [
                        "/recruit",
                        "/careers",
                        "/recruitment",
                        "/job",
                        "/employment",
                        "/採用",
                        "/キャリア"
                    ]
                    
                    for pattern in career_patterns:
                        career_url = company["official_site"].rstrip('/') + pattern
                        try:
                            response = requests.head(career_url, timeout=5)
                            if response.status_code == 200:
                                company["career_site"] = career_url
                                break
                        except:
                            continue
            
            except Exception as e:
                logger.error(f"Error enriching data for company {company['name']}: {e}")
            
            # 処理間隔を空ける
            time.sleep(1)
    
    def run(self):
        """企業情報収集の実行"""
        # 既存のデータがあれば読み込む
        existing_data = load_json(COMPANIES_FILE)
        if existing_data:
            self.companies = existing_data
            self.company_ids = {company["id"] for company in self.companies}
            logger.info(f"Loaded {len(self.companies)} companies from existing data")
        
        # 各ソースから企業情報を収集
        self.collect_listed_companies()
        self.collect_from_mynavi()
        self.collect_from_rikunabi()
        self.collect_from_career_tasu()
        
        # 企業情報を充実させる
        self.enrich_company_data()
        
        # 結果を保存
        save_json(self.companies, COMPANIES_FILE)
        logger.info(f"Collected and saved {len(self.companies)} companies in total")
        
        return self.companies

if __name__ == "__main__":
    collector = CompanyCollector()
    collector.run()
