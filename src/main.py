"""
インターン情報自動取得システム - メインスクリプト
"""

import os
import logging
import argparse
from datetime import datetime

from config import COMPANIES_FILE, INTERNSHIPS_FILE, COMBINED_DATA_FILE, DATA_DIR
from company_collector import CompanyCollector
from internship_collector import InternshipCollector, combine_data
from utils import setup_logger

# ロガーの設定
logger = setup_logger()

def ensure_data_dir():
    """データディレクトリが存在することを確認"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        logger.info(f"Created data directory: {DATA_DIR}")

def run_collection(args):
    """データ収集処理を実行"""
    start_time = datetime.now()
    logger.info(f"Starting data collection at {start_time}")
    
    # データディレクトリの確認
    ensure_data_dir()
    
    # 企業情報の収集
    if not args.skip_companies:
        logger.info("Collecting company information...")
        company_collector = CompanyCollector()
        companies = company_collector.run()
        logger.info(f"Collected {len(companies)} companies")
    else:
        logger.info("Skipping company collection")
        companies = []
    
    # インターンシップ情報の収集
    if not args.skip_internships:
        logger.info("Collecting internship information...")
        # 企業情報を読み込む
        if not companies and os.path.exists(COMPANIES_FILE):
            from utils import load_json
            companies = load_json(COMPANIES_FILE)
            if not companies:
                logger.error("No company data available. Cannot collect internships.")
                return False
        
        internship_collector = InternshipCollector(companies)
        internships = internship_collector.run()
        logger.info(f"Collected {len(internships)} internships")
    else:
        logger.info("Skipping internship collection")
    
    # データの結合
    if not args.skip_combine:
        logger.info("Combining company and internship data...")
        success = combine_data(COMPANIES_FILE, INTERNSHIPS_FILE, COMBINED_DATA_FILE)
        if success:
            logger.info("Data combination completed successfully")
        else:
            logger.error("Failed to combine data")
            return False
    else:
        logger.info("Skipping data combination")
    
    end_time = datetime.now()
    duration = end_time - start_time
    logger.info(f"Data collection completed at {end_time}")
    logger.info(f"Total duration: {duration}")
    
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Intern information collection system")
    parser.add_argument("--skip-companies", action="store_true", help="Skip company collection")
    parser.add_argument("--skip-internships", action="store_true", help="Skip internship collection")
    parser.add_argument("--skip-combine", action="store_true", help="Skip data combination")
    args = parser.parse_args()
    
    success = run_collection(args)
    
    if success:
        logger.info("Script executed successfully")
    else:
        logger.error("Script execution failed")
