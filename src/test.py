"""
インターン情報自動取得システム - テストスクリプト
"""

import os
import json
import logging
from datetime import datetime

from config import COMPANIES_FILE, INTERNSHIPS_FILE, COMBINED_DATA_FILE, DATA_DIR
from utils import setup_logger, load_json, save_json

# ロガーの設定
logger = setup_logger()

def create_test_data():
    """テスト用のデータを作成する"""
    logger.info("Creating test data...")
    
    # データディレクトリの確認
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    # テスト用の企業データ
    test_companies = [
        {
            "id": "test_company_1",
            "name": "テスト企業1",
            "stock_code": "1234",
            "market": "プライム",
            "source": "テスト",
            "official_site": "https://example.com/company1",
            "career_site": "https://example.com/company1/recruit"
        },
        {
            "id": "test_company_2",
            "name": "テスト企業2",
            "stock_code": "5678",
            "market": "スタンダード",
            "source": "テスト",
            "official_site": "https://example.com/company2",
            "career_site": "https://example.com/company2/recruit"
        },
        {
            "id": "test_company_3",
            "name": "テスト企業3",
            "stock_code": "9012",
            "market": "グロース",
            "source": "テスト",
            "official_site": "https://example.com/company3",
            "career_site": "https://example.com/company3/recruit"
        }
    ]
    
    # テスト用のインターンシップデータ
    test_internships = [
        {
            "id": "test_company_1_intern_1",
            "company_id": "test_company_1",
            "company_name": "テスト企業1",
            "title": "サマーインターンシップ2025",
            "period": "2週間",
            "start_date": "2025-08-01",
            "end_date": "2025-08-15",
            "target": "大学3年生、修士1年生",
            "application_url": "https://example.com/company1/intern/summer",
            "source": "企業採用サイト",
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "verification": {
                "score": 0.8,
                "sources": ["企業採用サイト"],
                "verified": True
            }
        },
        {
            "id": "test_company_1_intern_2",
            "company_id": "test_company_1",
            "company_name": "テスト企業1",
            "title": "冬季インターンシップ2025",
            "period": "1週間",
            "start_date": "2025-12-01",
            "end_date": "2025-12-07",
            "target": "大学3年生、修士1年生",
            "application_url": "https://example.com/company1/intern/winter",
            "source": "企業採用サイト",
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "verification": {
                "score": 0.7,
                "sources": ["企業採用サイト"],
                "verified": True
            }
        },
        {
            "id": "test_company_2_intern_1",
            "company_id": "test_company_2",
            "company_name": "テスト企業2",
            "title": "1Dayインターンシップ",
            "period": "1日",
            "start_date": "2025-07-15",
            "end_date": "2025-07-15",
            "target": "大学2年生以上",
            "application_url": "https://example.com/company2/intern/oneday",
            "source": "マイナビ",
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "verification": {
                "score": 0.6,
                "sources": ["マイナビ", "企業採用サイト"],
                "verified": True
            }
        },
        {
            "id": "test_company_3_intern_1",
            "company_id": "test_company_3",
            "company_name": "テスト企業3",
            "title": "長期インターンシップ",
            "period": "3ヶ月",
            "start_date": "2025-09-01",
            "end_date": "2025-11-30",
            "target": "大学3年生、修士1年生",
            "application_url": "https://example.com/company3/intern/long",
            "source": "リクナビ",
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "verification": {
                "score": 0.9,
                "sources": ["リクナビ", "企業採用サイト"],
                "verified": True
            }
        }
    ]
    
    # データを保存
    save_json(test_companies, COMPANIES_FILE)
    save_json(test_internships, INTERNSHIPS_FILE)
    
    logger.info(f"Created test data: {len(test_companies)} companies and {len(test_internships)} internships")
    
    return test_companies, test_internships

def test_data_combination():
    """データ結合機能をテストする"""
    logger.info("Testing data combination...")
    
    from internship_collector import combine_data
    
    # データ結合を実行
    success = combine_data(COMPANIES_FILE, INTERNSHIPS_FILE, COMBINED_DATA_FILE)
    
    if success:
        logger.info("Data combination test passed")
        
        # 結合データを検証
        combined_data = load_json(COMBINED_DATA_FILE)
        
        if combined_data:
            companies_count = len(combined_data["companies"])
            internships_count = sum(len(company.get("internships", [])) for company in combined_data["companies"])
            
            logger.info(f"Combined data contains {companies_count} companies and {internships_count} internships")
            
            # メタデータを検証
            if "meta" in combined_data:
                meta = combined_data["meta"]
                logger.info(f"Meta data: last_updated={meta.get('last_updated')}, total_companies={meta.get('total_companies')}, total_internships={meta.get('total_internships')}")
            
            return True
        else:
            logger.error("Failed to load combined data")
            return False
    else:
        logger.error("Data combination test failed")
        return False

def validate_data_structure():
    """データ構造を検証する"""
    logger.info("Validating data structure...")
    
    # 企業データを検証
    companies = load_json(COMPANIES_FILE)
    if not companies:
        logger.error("Failed to load company data")
        return False
    
    # 必須フィールドを確認
    required_company_fields = ["id", "name", "official_site"]
    for company in companies:
        missing_fields = [field for field in required_company_fields if field not in company]
        if missing_fields:
            logger.warning(f"Company {company.get('name', 'Unknown')} is missing required fields: {missing_fields}")
    
    # インターンシップデータを検証
    internships = load_json(INTERNSHIPS_FILE)
    if not internships:
        logger.error("Failed to load internship data")
        return False
    
    # 必須フィールドを確認
    required_internship_fields = ["id", "company_id", "company_name", "title", "application_url"]
    for internship in internships:
        missing_fields = [field for field in required_internship_fields if field not in internship]
        if missing_fields:
            logger.warning(f"Internship {internship.get('title', 'Unknown')} is missing required fields: {missing_fields}")
    
    # 結合データを検証
    combined_data = load_json(COMBINED_DATA_FILE)
    if not combined_data:
        logger.error("Failed to load combined data")
        return False
    
    # 構造を確認
    if "companies" not in combined_data or "meta" not in combined_data:
        logger.error("Combined data is missing required sections")
        return False
    
    logger.info("Data structure validation completed")
    return True

def run_tests():
    """全テストを実行する"""
    logger.info("Starting tests...")
    
    # テストデータを作成
    create_test_data()
    
    # データ結合をテスト
    combination_result = test_data_combination()
    
    # データ構造を検証
    structure_result = validate_data_structure()
    
    # テスト結果をまとめる
    test_results = {
        "data_combination": combination_result,
        "data_structure": structure_result,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # テスト結果を保存
    save_json(test_results, f"{DATA_DIR}/test_results.json")
    
    logger.info("Tests completed")
    return all(test_results.values())

if __name__ == "__main__":
    success = run_tests()
    
    if success:
        logger.info("All tests passed")
    else:
        logger.error("Some tests failed")
