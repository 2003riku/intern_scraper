"""
インターン情報自動取得システム - ユーティリティ関数
"""

import os
import json
import logging
import time
import random
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from config import REQUEST_HEADERS, REQUEST_TIMEOUT, REQUEST_RETRY, REQUEST_DELAY, DATE_FORMAT, LOG_FILE, LOG_LEVEL

# ロギング設定
def setup_logger():
    """ロガーの設定を行う"""
    log_dir = os.path.dirname(LOG_FILE)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logger()

# リクエスト関連の関数
def make_request(url, headers=None, params=None, retries=REQUEST_RETRY):
    """指定されたURLにリクエストを送信し、レスポンスを返す"""
    if headers is None:
        headers = REQUEST_HEADERS
    
    for attempt in range(retries):
        try:
            logger.info(f"Requesting URL: {url}")
            response = requests.get(url, headers=headers, params=params, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            # リクエスト間隔を設定（サーバー負荷軽減のため）
            time.sleep(REQUEST_DELAY + random.uniform(0, 1))
            
            return response
        except requests.exceptions.RequestException as e:
            logger.warning(f"Request failed (attempt {attempt+1}/{retries}): {e}")
            if attempt < retries - 1:
                # 指数バックオフでリトライ
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                logger.info(f"Retrying in {wait_time:.2f} seconds...")
                time.sleep(wait_time)
            else:
                logger.error(f"Failed to fetch {url} after {retries} attempts")
                raise
    
    return None

def get_soup(url, headers=None, params=None):
    """指定されたURLのHTMLを取得し、BeautifulSoupオブジェクトを返す"""
    response = make_request(url, headers, params)
    if response:
        return BeautifulSoup(response.text, 'html.parser')
    return None

# データ保存関連の関数
def save_json(data, filepath):
    """データをJSON形式で保存する"""
    directory = os.path.dirname(filepath)
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Data saved to {filepath}")

def load_json(filepath):
    """JSON形式のファイルからデータを読み込む"""
    if not os.path.exists(filepath):
        logger.warning(f"File not found: {filepath}")
        return None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    logger.info(f"Data loaded from {filepath}")
    return data

# 日付処理関連の関数
def parse_date(date_str):
    """様々な形式の日付文字列を標準形式に変換する"""
    # 様々な日付形式に対応
    formats = [
        '%Y年%m月%d日',
        '%Y/%m/%d',
        '%Y-%m-%d',
        '%Y.%m.%d'
    ]
    
    for fmt in formats:
        try:
            date_obj = datetime.strptime(date_str.strip(), fmt)
            return date_obj.strftime(DATE_FORMAT)
        except ValueError:
            continue
    
    logger.warning(f"Failed to parse date: {date_str}")
    return None

def is_valid_date(date_str):
    """日付文字列が有効かどうかを検証する"""
    return parse_date(date_str) is not None

# ファクトチェック関連の関数
def compare_data_sources(data1, data2, key):
    """2つのデータソースから同じキーの値を比較し、一致度を返す"""
    if key not in data1 or key not in data2:
        return 0.0
    
    val1 = str(data1[key]).lower()
    val2 = str(data2[key]).lower()
    
    # 完全一致
    if val1 == val2:
        return 1.0
    
    # 部分一致（一方がもう一方に含まれる）
    if val1 in val2 or val2 in val1:
        return 0.7
    
    # 類似度計算（簡易版）
    # 実際のプロジェクトではより高度な類似度計算を実装することを推奨
    common_chars = set(val1) & set(val2)
    all_chars = set(val1) | set(val2)
    if not all_chars:
        return 0.0
    
    return len(common_chars) / len(all_chars)

def verify_internship_data(internship, sources):
    """インターンシップデータを複数のソースと照合して検証する"""
    verification_results = {}
    
    for key in internship:
        scores = []
        for source in sources:
            if key in source:
                score = compare_data_sources({key: internship[key]}, {key: source[key]}, key)
                scores.append(score)
        
        if scores:
            verification_results[key] = sum(scores) / len(scores)
        else:
            verification_results[key] = 0.0
    
    # 全体の信頼度スコアを計算
    if verification_results:
        overall_score = sum(verification_results.values()) / len(verification_results)
    else:
        overall_score = 0.0
    
    return {
        "overall_score": overall_score,
        "field_scores": verification_results
    }

# URLの正規化
def normalize_url(url):
    """URLを正規化する（プロトコルの追加、末尾のスラッシュの処理など）"""
    if not url:
        return None
    
    # プロトコルがない場合はhttpsを追加
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # 末尾のスラッシュを統一（あれば残す、なければ追加しない）
    return url.rstrip('/')
