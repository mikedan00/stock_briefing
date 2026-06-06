"""
config.py — 환경변수 및 상수 관리
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── HuggingFace Router ───────────────────────────────────────────────────────
HF_TOKEN = os.getenv("HF_TOKEN", "")
HF_MODEL = "google/gemma-3-27b-it"          # HF Router에서 사용 가능한 Gemma 모델
HF_API_URL = "https://router.huggingface.co/v1/chat/completions"

# ── Gmail SMTP ───────────────────────────────────────────────────────────────
GMAIL_USER = os.getenv("GMAIL_USER", "")    # 발신 Gmail 주소
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")  # Gmail 앱 비밀번호

# ── 뉴스 소스 ────────────────────────────────────────────────────────────────
NAVER_NEWS_RSS = "https://search.naver.com/rss?where=news&query={query}"
GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"
GOOGLE_NEWS_EN_RSS = "https://news.google.com/rss/search?q={query}&hl=en&gl=US&ceid=US:en"

# ── 주식 설정 ────────────────────────────────────────────────────────────────
MAX_STOCKS = 10
KR_MARKET_SUFFIX = ".KS"   # KOSPI
KQ_MARKET_SUFFIX = ".KQ"   # KOSDAQ
