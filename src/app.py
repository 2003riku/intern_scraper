"""
インターン情報自動取得システム - Webアプリケーション
"""

import os
import json
from datetime import datetime
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# データファイルのパス
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
COMBINED_DATA_FILE = os.path.join(DATA_DIR, "combined_data.json")

# データ読み込み関数
def load_data():
    try:
        with open(COMBINED_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading data: {e}")
        return {"companies": [], "meta": {"last_updated": "N/A", "total_companies": 0, "total_internships": 0}}

@app.route('/')
def index():
    """トップページを表示"""
    data = load_data()
    meta = data.get("meta", {})
    
    return render_template('index.html', 
                          last_updated=meta.get("last_updated", "N/A"),
                          total_companies=meta.get("total_companies", 0),
                          total_internships=meta.get("total_internships", 0))

@app.route('/api/companies')
def get_companies():
    """企業一覧を返すAPI"""
    data = load_data()
    companies = data.get("companies", [])
    
    # シンプルな企業リストを作成（インターンシップ情報は含めない）
    simple_companies = []
    for company in companies:
        simple_companies.append({
            "id": company.get("id", ""),
            "name": company.get("name", ""),
            "market": company.get("market", ""),
            "industry": company.get("industry", ""),
            "internship_count": len(company.get("internships", []))
        })
    
    return jsonify(simple_companies)

@app.route('/api/internships')
def get_internships():
    """インターンシップ一覧を返すAPI"""
    data = load_data()
    companies = data.get("companies", [])
    
    # フィルタリングパラメータ
    company_id = request.args.get('company_id')
    
    # 全インターンシップリストを作成
    all_internships = []
    for company in companies:
        # 企業IDでフィルタリング
        if company_id and company.get("id") != company_id:
            continue
            
        for internship in company.get("internships", []):
            all_internships.append({
                "id": internship.get("id", ""),
                "company_id": company.get("id", ""),
                "company_name": company.get("name", ""),
                "title": internship.get("title", ""),
                "period": internship.get("period", ""),
                "start_date": internship.get("start_date", ""),
                "end_date": internship.get("end_date", ""),
                "target": internship.get("target", ""),
                "application_url": internship.get("application_url", ""),
                "source": internship.get("source", ""),
                "last_updated": internship.get("last_updated", "")
            })
    
    return jsonify(all_internships)

@app.route('/api/company/<company_id>')
def get_company(company_id):
    """特定の企業情報を返すAPI"""
    data = load_data()
    companies = data.get("companies", [])
    
    for company in companies:
        if company.get("id") == company_id:
            return jsonify(company)
    
    return jsonify({"error": "Company not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
