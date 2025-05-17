"""
インターン情報自動取得システム - 設定ファイル
"""

# 対象とする就活サイト
JOB_SITES = {
    "mynavi": {
        "name": "マイナビ",
        "url": "https://job.mynavi.jp/26/pc/corpinfo/displayCorpSearch/index",
        "internship_url_pattern": "https://job.mynavi.jp/26/pc/search/corp/{}/internship",
    },
    "rikunabi": {
        "name": "リクナビ",
        "url": "https://job.rikunabi.com/2026/search/",
        "internship_url_pattern": "https://job.rikunabi.com/2026/company/internship/{}/",
    },
    "career_tasu": {
        "name": "キャリタス就活",
        "url": "https://job.career-tasu.jp/2026/search/",
        "internship_url_pattern": "https://job.career-tasu.jp/2026/corp/detail/{}/internship/",
    }
}

# 上場企業情報取得用URL
LISTED_COMPANIES_URL = "https://www.jpx.co.jp/markets/statistics-equities/misc/01.html"

# データ保存先
DATA_DIR = "../data"
COMPANIES_FILE = f"{DATA_DIR}/companies.json"
INTERNSHIPS_FILE = f"{DATA_DIR}/internships.json"
COMBINED_DATA_FILE = f"{DATA_DIR}/combined_data.json"

# スクレイピング設定
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
REQUEST_TIMEOUT = 10  # 秒
REQUEST_RETRY = 3     # リトライ回数
REQUEST_DELAY = 1     # リクエスト間隔（秒）

# 企業情報取得数の上限
MAX_COMPANIES = 1000

# 日付フォーマット
DATE_FORMAT = "%Y-%m-%d"

# ログ設定
LOG_FILE = "../logs/scraper.log"
LOG_LEVEL = "INFO"
