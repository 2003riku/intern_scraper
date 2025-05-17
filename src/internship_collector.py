"""
インターン情報自動取得システム - インターンシップ情報収集モジュール
"""

import os
import re
import time
import logging
from datetime import datetime
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from config import INTERNSHIPS_FILE, DATA_DIR
from utils import get_soup, save_json, load_json, parse_date, verify_internship_data, logger

class InternshipCollector:
    """企業の公式採用ページからインターンシップ情報を収集するクラス"""
    
    def __init__(self, companies):
        self.companies = companies
        self.internships = []
        self.internship_ids = set()  # 重複チェック用
    
    def extract_internship_info_from_job_site(self, company):
        """就活サイトの企業インターンシップページから情報を抽出する"""
        internships = []
        
        if "internship_url" not in company or not company["internship_url"]:
            return internships
        
        try:
            soup = get_soup(company["internship_url"])
            if not soup:
                logger.error(f"Failed to fetch internship page for {company['name']}")
                return internships
            
            # インターンシップ情報を抽出（サイトごとに異なる構造に対応）
            # 注: 実際のサイト構造に合わせてセレクタを調整する必要があります
            
            # マイナビの場合
            if "mynavi" in company["id"]:
                internship_elements = soup.select('.internship-box')
                
                for element in internship_elements:
                    title_elem = element.select_one('.internship-name')
                    period_elem = element.select_one('.period')
                    date_elem = element.select_one('.date')
                    target_elem = element.select_one('.target')
                    link_elem = element.select_one('a.more-info')
                    
                    if not title_elem:
                        continue
                    
                    title = title_elem.text.strip()
                    period = period_elem.text.strip() if period_elem else None
                    date_info = date_elem.text.strip() if date_elem else None
                    target = target_elem.text.strip() if target_elem else None
                    link = link_elem.get('href') if link_elem else None
                    
                    # 日付情報を解析
                    start_date = None
                    end_date = None
                    if date_info:
                        date_match = re.search(r'(\d{4}[年/.-]\d{1,2}[月/.-]\d{1,2}日?).*?(\d{4}[年/.-]\d{1,2}[月/.-]\d{1,2}日?)', date_info)
                        if date_match:
                            start_date = parse_date(date_match.group(1))
                            end_date = parse_date(date_match.group(2))
                    
                    internship_id = f"{company['id']}_{len(internships)}"
                    
                    internships.append({
                        "id": internship_id,
                        "company_id": company["id"],
                        "company_name": company["name"],
                        "title": title,
                        "period": period,
                        "start_date": start_date,
                        "end_date": end_date,
                        "target": target,
                        "application_url": urljoin(company["internship_url"], link) if link else company["internship_url"],
                        "source": "マイナビ",
                        "last_updated": datetime.now().strftime("%Y-%m-%d")
                    })
            
            # リクナビの場合
            elif "rikunabi" in company["id"]:
                internship_elements = soup.select('.internshipBox')
                
                for element in internship_elements:
                    title_elem = element.select_one('.internshipTitle')
                    period_elem = element.select_one('.period')
                    date_elem = element.select_one('.date')
                    target_elem = element.select_one('.target')
                    link_elem = element.select_one('a.more')
                    
                    if not title_elem:
                        continue
                    
                    title = title_elem.text.strip()
                    period = period_elem.text.strip() if period_elem else None
                    date_info = date_elem.text.strip() if date_elem else None
                    target = target_elem.text.strip() if target_elem else None
                    link = link_elem.get('href') if link_elem else None
                    
                    # 日付情報を解析
                    start_date = None
                    end_date = None
                    if date_info:
                        date_match = re.search(r'(\d{4}[年/.-]\d{1,2}[月/.-]\d{1,2}日?).*?(\d{4}[年/.-]\d{1,2}[月/.-]\d{1,2}日?)', date_info)
                        if date_match:
                            start_date = parse_date(date_match.group(1))
                            end_date = parse_date(date_match.group(2))
                    
                    internship_id = f"{company['id']}_{len(internships)}"
                    
                    internships.append({
                        "id": internship_id,
                        "company_id": company["id"],
                        "company_name": company["name"],
                        "title": title,
                        "period": period,
                        "start_date": start_date,
                        "end_date": end_date,
                        "target": target,
                        "application_url": urljoin(company["internship_url"], link) if link else company["internship_url"],
                        "source": "リクナビ",
                        "last_updated": datetime.now().strftime("%Y-%m-%d")
                    })
            
            # キャリタス就活の場合
            elif "career_tasu" in company["id"]:
                internship_elements = soup.select('.internship-item')
                
                for element in internship_elements:
                    title_elem = element.select_one('.title')
                    period_elem = element.select_one('.period')
                    date_elem = element.select_one('.application-period')
                    target_elem = element.select_one('.target')
                    link_elem = element.select_one('a.detail-link')
                    
                    if not title_elem:
                        continue
                    
                    title = title_elem.text.strip()
                    period = period_elem.text.strip() if period_elem else None
                    date_info = date_elem.text.strip() if date_elem else None
                    target = target_elem.text.strip() if target_elem else None
                    link = link_elem.get('href') if link_elem else None
                    
                    # 日付情報を解析
                    start_date = None
                    end_date = None
                    if date_info:
                        date_match = re.search(r'(\d{4}[年/.-]\d{1,2}[月/.-]\d{1,2}日?).*?(\d{4}[年/.-]\d{1,2}[月/.-]\d{1,2}日?)', date_info)
                        if date_match:
                            start_date = parse_date(date_match.group(1))
                            end_date = parse_date(date_match.group(2))
                    
                    internship_id = f"{company['id']}_{len(internships)}"
                    
                    internships.append({
                        "id": internship_id,
                        "company_id": company["id"],
                        "company_name": company["name"],
                        "title": title,
                        "period": period,
                        "start_date": start_date,
                        "end_date": end_date,
                        "target": target,
                        "application_url": urljoin(company["internship_url"], link) if link else company["internship_url"],
                        "source": "キャリタス就活",
                        "last_updated": datetime.now().strftime("%Y-%m-%d")
                    })
        
        except Exception as e:
            logger.error(f"Error extracting internship info from job site for {company['name']}: {e}")
        
        return internships
    
    def extract_internship_info_from_career_site(self, company):
        """企業の採用サイトからインターンシップ情報を抽出する"""
        internships = []
        
        if "career_site" not in company or not company["career_site"]:
            return internships
        
        try:
            soup = get_soup(company["career_site"])
            if not soup:
                logger.error(f"Failed to fetch career site for {company['name']}")
                return internships
            
            # インターンシップ関連のページを探す
            internship_links = []
            
            # キーワードを含むリンクを探す
            keywords = ["インターン", "intern", "インターンシップ", "internship", "就業体験"]
            for link in soup.find_all('a'):
                link_text = link.text.strip().lower()
                link_href = link.get('href', '')
                
                if any(keyword in link_text.lower() for keyword in keywords) or any(keyword in link_href.lower() for keyword in keywords):
                    internship_links.append(link.get('href'))
            
            # インターンシップページが見つからない場合は現在のページを使用
            if not internship_links:
                internship_links = [company["career_site"]]
            
            # 各インターンシップページから情報を抽出
            for link in internship_links[:3]:  # 最大3ページまで
                try:
                    full_url = urljoin(company["career_site"], link)
                    intern_soup = get_soup(full_url)
                    
                    if not intern_soup:
                        continue
                    
                    # インターンシップ情報を抽出
                    # 注: 企業サイトは構造が多様なため、一般的なパターンを探す
                    
                    # 1. テーブル内の情報を探す
                    tables = intern_soup.find_all('table')
                    for table in tables:
                        rows = table.find_all('tr')
                        internship_data = {}
                        
                        for row in rows:
                            header = row.find('th')
                            data = row.find('td')
                            
                            if header and data:
                                header_text = header.text.strip()
                                data_text = data.text.strip()
                                
                                if "タイトル" in header_text or "名称" in header_text:
                                    internship_data["title"] = data_text
                                elif "期間" in header_text:
                                    internship_data["period"] = data_text
                                elif "開始" in header_text or "募集開始" in header_text:
                                    internship_data["start_date"] = parse_date(data_text)
                                elif "締切" in header_text or "募集締切" in header_text or "応募締切" in header_text:
                                    internship_data["end_date"] = parse_date(data_text)
                                elif "対象" in header_text:
                                    internship_data["target"] = data_text
                        
                        if internship_data and "title" in internship_data:
                            internship_id = f"{company['id']}_career_{len(internships)}"
                            
                            internships.append({
                                "id": internship_id,
                                "company_id": company["id"],
                                "company_name": company["name"],
                                "title": internship_data.get("title", "企業サイトのインターンシップ"),
                                "period": internship_data.get("period"),
                                "start_date": internship_data.get("start_date"),
                                "end_date": internship_data.get("end_date"),
                                "target": internship_data.get("target"),
                                "application_url": full_url,
                                "source": "企業採用サイト",
                                "last_updated": datetime.now().strftime("%Y-%m-%d")
                            })
                    
                    # 2. 特定のクラスやIDを持つ要素を探す
                    internship_sections = intern_soup.select('.internship, .intern, #internship, #intern')
                    for section in internship_sections:
                        title_elem = section.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', '.title', '.heading'])
                        
                        if title_elem:
                            title = title_elem.text.strip()
                            
                            # 日付情報を探す
                            date_pattern = r'(\d{4}[年/.-]\d{1,2}[月/.-]\d{1,2}日?).*?(\d{4}[年/.-]\d{1,2}[月/.-]\d{1,2}日?)'
                            date_matches = re.findall(date_pattern, section.text)
                            
                            start_date = None
                            end_date = None
                            if date_matches:
                                start_date = parse_date(date_matches[0][0])
                                end_date = parse_date(date_matches[0][1])
                            
                            internship_id = f"{company['id']}_career_{len(internships)}"
                            
                            internships.append({
                                "id": internship_id,
                                "company_id": company["id"],
                                "company_name": company["name"],
                                "title": title,
                                "period": None,
                                "start_date": start_date,
                                "end_date": end_date,
                                "target": None,
                                "application_url": full_url,
                                "source": "企業採用サイト",
                                "last_updated": datetime.now().strftime("%Y-%m-%d")
                            })
                
                except Exception as e:
                    logger.error(f"Error processing internship page {link} for {company['name']}: {e}")
                
                # ページ間の待機時間
                time.sleep(2)
        
        except Exception as e:
            logger.error(f"Error extracting internship info from career site for {company['name']}: {e}")
        
        return internships
    
    def verify_and_merge_internship_data(self, job_site_internships, career_site_internships):
        """就活サイトと企業サイトから取得したインターンシップ情報を検証・マージする"""
        verified_internships = []
        
        # 就活サイトの情報をベースにする
        for job_internship in job_site_internships:
            # 同じインターンシップを企業サイトから探す
            matching_internships = []
            
            for career_internship in career_site_internships:
                # タイトルの類似性でマッチング
                if job_internship["title"] in career_internship["title"] or career_internship["title"] in job_internship["title"]:
                    matching_internships.append(career_internship)
            
            # 検証結果
            if matching_internships:
                verification_result = verify_internship_data(job_internship, matching_internships)
                
                # 信頼度が高い場合、情報をマージ
                if verification_result["overall_score"] > 0.5:
                    # 最もマッチする企業サイトの情報
                    best_match = matching_internships[0]
                    
                    # 情報をマージ（就活サイトの情報を優先）
                    merged_internship = job_internship.copy()
                    
                    # 企業サイトにしか情報がない場合は補完
                    for key in ["period", "start_date", "end_date", "target"]:
                        if not merged_internship.get(key) and best_match.get(key):
                            merged_internship[key] = best_match[key]
                    
                    # 検証結果を追加
                    merged_internship["verification"] = {
                        "score": verification_result["overall_score"],
                        "sources": ["就活サイト", "企業採用サイト"],
                        "verified": True
                    }
                    
                    verified_internships.append(merged_internship)
                else:
                    # 信頼度が低い場合、就活サイトの情報のみを使用
                    job_internship["verification"] = {
                        "score": verification_result["overall_score"],
                        "sources": ["就活サイト"],
                        "verified": False
                    }
                    verified_internships.append(job_internship)
            else:
                # マッチする企業サイトの情報がない場合
                job_internship["verification"] = {
                    "score": 0.0,
                    "sources": ["就活サイト"],
                    "verified": False
                }
                verified_internships.append(job_internship)
        
        # 就活サイトに存在しない企業サイトのインターンシップ情報を追加
        for career_internship in career_site_internships:
            is_new = True
            
            for verified in verified_internships:
                if career_internship["title"] in verified["title"] or verified["title"] in career_internship["title"]:
                    is_new = False
                    break
            
            if is_new:
                career_internship["verification"] = {
                    "score": 0.0,
                    "sources": ["企業採用サイト"],
                    "verified": False
                }
                verified_internships.append(career_internship)
        
        return verified_internships
    
    def collect_internships(self):
        """全企業のインターンシップ情報を収集する"""
        # 既存のデータがあれば読み込む
        existing_data = load_json(INTERNSHIPS_FILE)
        if existing_data:
            self.internships = existing_data
            self.internship_ids = {internship["id"] for internship in self.internships}
            logger.info(f"Loaded {len(self.internships)} internships from existing data")
        
        # 各企業のインターンシップ情報を収集
        for i, company in enumerate(self.companies):
            if i % 10 == 0:
                logger.info(f"Collecting internships for company {i+1}/{len(self.companies)}: {company['name']}")
            
            try:
                # 就活サイトからインターンシップ情報を取得
                job_site_internships = self.extract_internship_info_from_job_site(company)
                logger.info(f"Found {len(job_site_internships)} internships from job site for {company['name']}")
                
                # 企業の採用サイトからインターンシップ情報を取得
                career_site_internships = self.extract_internship_info_from_career_site(company)
                logger.info(f"Found {len(career_site_internships)} internships from career site for {company['name']}")
                
                # 情報を検証・マージ
                verified_internships = self.verify_and_merge_internship_data(job_site_internships, career_site_internships)
                
                # 新しいインターンシップ情報を追加
                for internship in verified_internships:
                    if internship["id"] not in self.internship_ids:
                        self.internships.append(internship)
                        self.internship_ids.add(internship["id"])
                
                # 既存のインターンシップ情報を更新
                for i, existing in enumerate(self.internships):
                    if existing["company_id"] == company["id"]:
                        for new_internship in verified_internships:
                            if existing["title"] == new_internship["title"]:
                                self.internships[i] = new_internship
                                break
            
            except Exception as e:
                logger.error(f"Error collecting internships for {company['name']}: {e}")
            
            # 企業間の待機時間
            time.sleep(2)
        
        # 結果を保存
        save_json(self.internships, INTERNSHIPS_FILE)
        logger.info(f"Collected and saved {len(self.internships)} internships in total")
        
        return self.internships
    
    def run(self):
        """インターンシップ情報収集の実行"""
        return self.collect_internships()

def combine_data(companies_file, internships_file, output_file):
    """企業情報とインターンシップ情報を結合する"""
    companies = load_json(companies_file)
    internships = load_json(internships_file)
    
    if not companies or not internships:
        logger.error("Failed to load company or internship data")
        return False
    
    # 企業IDごとにインターンシップをグループ化
    internships_by_company = {}
    for internship in internships:
        company_id = internship["company_id"]
        if company_id not in internships_by_company:
            internships_by_company[company_id] = []
        internships_by_company[company_id].append(internship)
    
    # 結合データを作成
    combined_data = {
        "companies": [],
        "meta": {
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "total_companies": len(companies),
            "total_internships": len(internships)
        }
    }
    
    for company in companies:
        company_data = company.copy()
        company_data["internships"] = internships_by_company.get(company["id"], [])
        combined_data["companies"].append(company_data)
    
    # 結果を保存
    save_json(combined_data, output_file)
    logger.info(f"Combined data saved to {output_file}")
    
    return True

if __name__ == "__main__":
    from company_collector import CompanyCollector
    from config import COMPANIES_FILE, INTERNSHIPS_FILE, COMBINED_DATA_FILE
    
    # 企業情報を収集
    company_collector = CompanyCollector()
    companies = company_collector.run()
    
    # インターンシップ情報を収集
    internship_collector = InternshipCollector(companies)
    internships = internship_collector.run()
    
    # データを結合
    combine_data(COMPANIES_FILE, INTERNSHIPS_FILE, COMBINED_DATA_FILE)
