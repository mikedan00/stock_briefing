# 📊 주식 AI 브리핑 시스템

HuggingFace Router (Gemma) 기반 실시간 주식 분석 · 뉴스 수집 · 투자 전략 리포트 · Gmail 발송

---

## 기능 요약

| 기능 | 설명 |
|------|------|
| 📈 실시간 주가 | pykrx(국내) + yfinance(해외), 오늘 종가 / 주말→금요일 자동 처리 |
| 📰 뉴스 수집 | 네이버뉴스 · 구글뉴스(KR) · 구글뉴스(EN→번역) · yfinance, 각 10건 |
| 🤖 AI 브리핑 | HF Router Gemma-3-27B, 개별 종목 + 포트폴리오 종합 전략 |
| 📊 주가 차트 | 이번주 · 이번달 · 6개월 추이, 추세선 포함 |
| 💹 수급 분석 | 외국인·기관·개인 순매수 (국내 종목) |
| 📋 최종 리포트 | 내일 예상 방향 · 매매 전략 · 리스크 분석 |
| 📧 Gmail 발송 | 완성된 리포트를 원하는 이메일로 HTML 발송 |

---

## 빠른 시작

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

```bash
cp .env.example .env
```

`.env` 파일을 열어 아래 값을 채웁니다:

```env
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
```

**HF_TOKEN 발급:**
1. https://huggingface.co → Settings → Access Tokens
2. `Read` 권한 토큰 생성

**Gmail 앱 비밀번호:**
1. Google 계정 → 보안 → 2단계 인증 (활성화 필수)
2. 앱 비밀번호 → 앱: 메일, 기기: 기타(직접 입력) → 생성
3. 표시된 16자리 비밀번호 복사

### 3. 실행

```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 열기

---

## 종목 입력 형식

| 유형 | 입력 예시 |
|------|-----------|
| 국내 (KOSPI/KOSDAQ) | `005930`, `000660`, `035420` |
| 해외 | `AAPL`, `NVDA`, `TSLA`, `MSFT` |
| 혼합 | `005930, 000660, AAPL, TSLA` |

- 최대 **10종목** 동시 분석
- 쉼표(`,`) 또는 줄바꿈으로 구분

### 주요 국내 종목 코드

| 코드 | 종목명 |
|------|--------|
| 005930 | 삼성전자 |
| 000660 | SK하이닉스 |
| 035420 | NAVER |
| 035720 | 카카오 |
| 005380 | 현대차 |
| 000270 | 기아 |
| 051910 | LG화학 |
| 006400 | 삼성SDI |
| 068270 | 셀트리온 |
| 207940 | 삼성바이오로직스 |

---

## 파일 구조

```
stock_briefing/
├── app.py               # Streamlit 메인 UI
├── config.py            # 환경변수 · 상수
├── stock_data.py        # pykrx + yfinance 주가 수집
├── news_fetcher.py      # 뉴스 수집 + 번역
├── llm_engine.py        # HF Router LLM 연동
├── report_generator.py  # AI 리포트 생성
├── email_sender.py      # Gmail SMTP 발송
├── requirements.txt     # 의존성
├── .env.example         # 환경변수 템플릿
└── README.md
```

---

## HuggingFace Router 모델 옵션

앱 사이드바에서 변경 가능:

| 모델 | 특징 |
|------|------|
| `google/gemma-3-27b-it` | 기본값, 높은 정확도 (권장) |
| `google/gemma-3-12b-it` | 빠른 응답 |
| `meta-llama/Llama-3.3-70B-Instruct` | 최고 성능, 느림 |
| `mistralai/Mistral-7B-Instruct-v0.3` | 경량, 빠름 |

---

## 주의사항

- **투자 면책**: 본 리포트는 AI 생성 참고자료이며, 투자 결정은 본인 책임입니다.
- **API 비용**: HuggingFace PRO 요금제 또는 HF Router 크레딧 필요
- **뉴스 번역**: Google Translate 무료 API 사용, 건당 500자 제한
- **pykrx 제한**: 당일 데이터는 장 마감(오후 3:30) 이후 정확
- **yfinance**: 해외 주식 실시간 데이터는 15~20분 지연
