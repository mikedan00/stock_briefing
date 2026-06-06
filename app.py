"""
app.py — 주식 투자 브리핑 Streamlit 앱
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import date

# ── 페이지 설정 ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="주식 AI 브리핑",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 스타일 ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
}

.main { background: #0a0e1a; }

.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #0f1629 50%, #0a0e1a 100%);
}

/* 사이드바 */
.css-1d391kg, [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1117 0%, #161b2e 100%);
    border-right: 1px solid #1e3a5f;
}

/* 카드 스타일 */
.metric-card {
    background: linear-gradient(135deg, #111827 0%, #1a2540 100%);
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 16px 20px;
    margin: 6px 0;
    box-shadow: 0 4px 16px rgba(0,0,0,0.4);
}

.metric-card h3 {
    color: #64b5f6;
    font-size: 0.8rem;
    font-weight: 500;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin: 0 0 6px 0;
}

.metric-card .value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.6rem;
    font-weight: 700;
    color: #e2e8f0;
    margin: 0;
}

.metric-card .change-up { color: #ef5350; }
.metric-card .change-down { color: #42a5f5; }
.metric-card .change-flat { color: #90a4ae; }

/* 뉴스 아이템 */
.news-item {
    background: #111827;
    border-left: 3px solid #1565c0;
    border-radius: 0 8px 8px 0;
    padding: 10px 14px;
    margin: 6px 0;
    font-size: 0.88rem;
    color: #cfd8dc;
    line-height: 1.5;
}

.news-item .news-source {
    font-size: 0.75rem;
    color: #546e7a;
    margin-top: 4px;
}

.news-item a { color: #90caf9; text-decoration: none; }
.news-item a:hover { text-decoration: underline; }

/* 리포트 박스 */
.report-box {
    background: #0d1117;
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 24px;
    font-size: 0.92rem;
    line-height: 1.9;
    color: #cfd8dc;
    white-space: pre-wrap;
    font-family: 'Noto Sans KR', sans-serif;
}

/* 헤더 */
.page-header {
    background: linear-gradient(135deg, #0d1b4b 0%, #1a237e 50%, #0d47a1 100%);
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 24px;
    border: 1px solid #1565c0;
    box-shadow: 0 8px 32px rgba(13,71,161,0.3);
}

.page-header h1 {
    color: #ffffff;
    font-size: 1.8rem;
    font-weight: 900;
    margin: 0;
    letter-spacing: -0.5px;
}

.page-header p {
    color: #90caf9;
    margin: 6px 0 0 0;
    font-size: 0.95rem;
}

/* 탭 */
.stTabs [data-baseweb="tab-list"] {
    background: #111827;
    border-radius: 8px;
    padding: 4px;
    gap: 4px;
}

.stTabs [data-baseweb="tab"] {
    color: #90a4ae;
    border-radius: 6px;
    font-weight: 500;
}

.stTabs [aria-selected="true"] {
    background: #1565c0 !important;
    color: white !important;
}

/* 버튼 */
.stButton > button {
    background: linear-gradient(135deg, #1565c0, #0d47a1);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 10px 20px;
    font-family: 'Noto Sans KR', sans-serif;
    transition: all 0.2s;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #1976d2, #1565c0);
    box-shadow: 0 4px 16px rgba(21,101,192,0.4);
    transform: translateY(-1px);
}

/* 섹션 제목 */
.section-title {
    color: #64b5f6;
    font-size: 1.0rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    margin: 20px 0 10px 0;
    padding-bottom: 6px;
    border-bottom: 1px solid #1e3a5f;
}

/* 입력 필드 */
.stTextInput input, .stTextArea textarea {
    background: #111827 !important;
    color: #e2e8f0 !important;
    border-color: #1e3a5f !important;
    border-radius: 8px !important;
}

.stSelectbox select {
    background: #111827 !important;
    color: #e2e8f0 !important;
}

/* 태그 배지 */
.badge-up {
    background: rgba(239,83,80,0.15);
    color: #ef5350;
    border: 1px solid rgba(239,83,80,0.3);
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 0.8rem;
    font-weight: 600;
}
.badge-down {
    background: rgba(66,165,245,0.15);
    color: #42a5f5;
    border: 1px solid rgba(66,165,245,0.3);
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 0.8rem;
    font-weight: 600;
}
.badge-flat {
    background: rgba(144,164,174,0.15);
    color: #90a4ae;
    border: 1px solid rgba(144,164,174,0.3);
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 0.8rem;
}
</style>
""", unsafe_allow_html=True)


# ── 세션 상태 초기화 ──────────────────────────────────────────────────────────
def init_session():
    defaults = {
        "stocks_data": [],
        "news_data": {},
        "stock_briefs": {},
        "portfolio_brief": "",
        "full_report": "",
        "data_loaded": False,
        "briefs_generated": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()


# ── 사이드바 ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ 설정")
    st.markdown("---")

    # HF Token
    st.markdown("### 🤖 AI 엔진")
    hf_token = st.text_input(
        "HuggingFace Token",
        type="password",
        value=os.getenv("HF_TOKEN", ""),
        help="HF Router 사용을 위한 토큰 (hf_...)",
        placeholder="hf_xxxxxxxxxxxx",
    )
    if hf_token:
        os.environ["HF_TOKEN"] = hf_token

    hf_model = st.selectbox(
        "모델 선택",
        options=[
            "google/gemma-3-27b-it",
            "google/gemma-3-12b-it",
            "google/gemma-2-27b-it",
            "mistralai/Mistral-7B-Instruct-v0.3",
            "meta-llama/Llama-3.3-70B-Instruct",
        ],
        index=0,
    )
    os.environ["HF_MODEL_OVERRIDE"] = hf_model

    st.markdown("---")
    st.markdown("### 📧 이메일 발송")
    gmail_user = st.text_input(
        "발신 Gmail 주소",
        value=os.getenv("GMAIL_USER", ""),
        placeholder="your@gmail.com",
    )
    gmail_pw = st.text_input(
        "Gmail 앱 비밀번호",
        type="password",
        value=os.getenv("GMAIL_APP_PASSWORD", ""),
        help="Google 계정 → 보안 → 앱 비밀번호",
        placeholder="xxxx xxxx xxxx xxxx",
    )
    to_email = st.text_input(
        "수신 이메일 주소",
        placeholder="recipient@email.com",
    )

    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.75rem; color:#546e7a; line-height:1.6;">
    <b>종목 입력 형식</b><br>
    • 국내: 6자리 코드 (예: 005930)<br>
    • 해외: 티커 (예: AAPL, TSLA)<br>
    • 최대 10종목 입력 가능<br><br>
    <b>HF Router 모델</b><br>
    • Gemma-3-27B 권장<br>
    </div>
    """, unsafe_allow_html=True)


# ── 메인 헤더 ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <h1>📊 주식 AI 브리핑 시스템</h1>
    <p>HuggingFace Router (Gemma) 기반 · 실시간 주가 · 뉴스 분석 · 투자 전략 리포트</p>
</div>
""", unsafe_allow_html=True)

today = date.today()
st.markdown(f"<p style='color:#546e7a; font-size:0.85rem;'>📅 기준일: {today.strftime('%Y년 %m월 %d일 (%A)')}</p>", unsafe_allow_html=True)


# ── 종목 입력 섹션 ────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">🔍 분석할 종목 입력</div>', unsafe_allow_html=True)

col_input, col_hint = st.columns([3, 1])
with col_input:
    ticker_input = st.text_area(
        "종목 코드 입력 (쉼표 또는 줄바꿈으로 구분, 최대 10개)",
        placeholder="005930, 000660, AAPL, TSLA\n삼성전자=005930, SK하이닉스=000660",
        height=100,
    )
with col_hint:
    st.markdown("""
    <div style="background:#111827; border:1px solid #1e3a5f; border-radius:8px; 
                padding:14px; font-size:0.8rem; color:#90a4ae; margin-top:24px;">
    <b style="color:#64b5f6;">예시 종목</b><br>
    🇰🇷 005930 (삼성전자)<br>
    🇰🇷 000660 (SK하이닉스)<br>
    🇰🇷 035420 (NAVER)<br>
    🇺🇸 AAPL (애플)<br>
    🇺🇸 NVDA (엔비디아)<br>
    🇺🇸 TSLA (테슬라)
    </div>
    """, unsafe_allow_html=True)

# 입력 파싱
def parse_tickers(raw: str) -> list[str]:
    import re
    raw = re.sub(r"[=\s]+\S+", "", raw)  # "삼성전자=005930" → "005930"... 아니면 그냥 split
    # 다시: 쉼표+줄바꿈으로 split, 6자리숫자 또는 영문 티커 추출
    tokens = re.split(r"[,\n\s]+", raw.strip())
    tickers = []
    for t in tokens:
        t = t.strip()
        clean = re.sub(r".*=", "", t)   # "삼성전자=005930" → "005930"
        clean = re.sub(r"[^A-Za-z0-9.]", "", clean)
        if clean and len(clean) >= 2:
            tickers.append(clean)
    return list(dict.fromkeys(tickers))[:10]  # 중복제거, 최대10개


col_btn1, col_btn2, col_btn3 = st.columns([1.5, 1.5, 3])
with col_btn1:
    btn_load = st.button("📥 데이터 수집", type="primary", use_container_width=True)
with col_btn2:
    btn_report = st.button("🤖 AI 리포트 생성", use_container_width=True,
                           disabled=not st.session_state.data_loaded)
with col_btn3:
    pass


# ── 데이터 수집 ──────────────────────────────────────────────────────────────
if btn_load:
    tickers = parse_tickers(ticker_input)
    if not tickers:
        st.error("종목 코드를 입력해주세요.")
    else:
        from stock_data import fetch_all_stocks
        from news_fetcher import fetch_all_news

        with st.spinner(f"📡 {len(tickers)}개 종목 데이터 수집 중..."):
            st.session_state.stocks_data = fetch_all_stocks(tickers)

        with st.spinner("📰 뉴스 수집 중..."):
            news_data = {}
            for stock in st.session_state.stocks_data:
                with st.spinner(f"  {stock['name']} 뉴스 수집..."):
                    news_data[stock["ticker"]] = fetch_all_news(stock)
            st.session_state.news_data = news_data

        st.session_state.data_loaded = True
        st.session_state.briefs_generated = False
        st.session_state.stock_briefs = {}
        st.session_state.portfolio_brief = ""
        st.session_state.full_report = ""
        st.success(f"✅ {len(tickers)}개 종목 데이터 수집 완료!")
        st.rerun()


# ── AI 리포트 생성 ────────────────────────────────────────────────────────────
if btn_report and st.session_state.data_loaded:
    # 모델 오버라이드 반영
    import config as cfg
    override = os.environ.get("HF_MODEL_OVERRIDE", "")
    if override:
        cfg.HF_MODEL = override
        import llm_engine
        llm_engine.HF_MODEL = override  # 직접 패치

    from report_generator import (
        generate_stock_brief,
        generate_portfolio_brief,
        build_full_report_text,
    )

    stocks = st.session_state.stocks_data
    news_data = st.session_state.news_data

    # 개별 브리핑
    stock_briefs = {}
    progress = st.progress(0, text="AI 분석 시작...")
    for i, stock in enumerate(stocks):
        ticker = stock["ticker"]
        with st.spinner(f"🤖 {stock['name']} 분석 중..."):
            brief = generate_stock_brief(stock, news_data.get(ticker, {}))
            stock_briefs[ticker] = brief
        progress.progress((i + 1) / (len(stocks) + 1), text=f"{stock['name']} 분석 완료")

    # 포트폴리오 종합
    with st.spinner("📋 포트폴리오 종합 분석 중..."):
        portfolio_brief = generate_portfolio_brief(stocks, [])
    progress.progress(1.0, text="완료!")

    # 전체 리포트 텍스트
    full_report = build_full_report_text(
        stocks, [], list(stock_briefs.values()), portfolio_brief
    )

    st.session_state.stock_briefs = stock_briefs
    st.session_state.portfolio_brief = portfolio_brief
    st.session_state.full_report = full_report
    st.session_state.briefs_generated = True
    st.success("✅ AI 리포트 생성 완료!")
    st.rerun()


# ── 결과 표시 ─────────────────────────────────────────────────────────────────
if st.session_state.data_loaded and st.session_state.stocks_data:
    stocks = st.session_state.stocks_data
    news_data = st.session_state.news_data

    tabs = st.tabs(["📈 주가 현황", "📰 뉴스", "📊 차트", "🤖 AI 브리핑", "📋 최종 리포트"])

    # ── 탭1: 주가 현황 ───────────────────────────────────────────────────────
    with tabs[0]:
        st.markdown('<div class="section-title">📈 오늘 종가 현황</div>', unsafe_allow_html=True)

        cols_per_row = 3
        for i in range(0, len(stocks), cols_per_row):
            row_stocks = stocks[i:i + cols_per_row]
            cols = st.columns(cols_per_row)
            for col, stock in zip(cols, row_stocks):
                with col:
                    name = stock.get("name", stock["ticker"])
                    close = stock.get("close")
                    change = stock.get("change_rate")
                    market = stock.get("market", "")
                    volume = stock.get("volume")

                    close_str = f"{close:,.0f}" if close else "N/A"
                    currency = "원" if market == "KR" else "$"

                    if change is not None:
                        if change > 0:
                            badge = f'<span class="badge-up">▲ {change:+.2f}%</span>'
                            val_color = "#ef5350"
                        elif change < 0:
                            badge = f'<span class="badge-down">▼ {change:.2f}%</span>'
                            val_color = "#42a5f5"
                        else:
                            badge = '<span class="badge-flat">─ 0.00%</span>'
                            val_color = "#90a4ae"
                    else:
                        badge = '<span class="badge-flat">N/A</span>'
                        val_color = "#90a4ae"

                    flag = "🇰🇷" if market == "KR" else "🇺🇸"
                    vol_str = f"{volume:,}" if volume else "-"

                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>{flag} {stock['ticker']} · {market}</h3>
                        <div style="font-weight:700; font-size:1.1rem; color:#e2e8f0; margin-bottom:4px;">{name}</div>
                        <div class="value" style="color:{val_color};">{close_str} {currency}</div>
                        <div style="margin-top:8px;">{badge}</div>
                        <div style="margin-top:6px; font-size:0.78rem; color:#546e7a;">거래량: {vol_str}</div>
                        <div style="font-size:0.78rem; color:#546e7a;">기준: {stock.get('date','')}</div>
                    </div>
                    """, unsafe_allow_html=True)

        # 수급 현황 (국내 종목)
        kr_stocks = [s for s in stocks if s.get("market") == "KR" and s.get("investor")]
        if kr_stocks:
            st.markdown('<div class="section-title">💹 수급 현황 (국내 종목)</div>', unsafe_allow_html=True)
            inv_rows = []
            for s in kr_stocks:
                row = {"종목": s.get("name", s["ticker"]), "코드": s["ticker"]}
                inv = s.get("investor", {})
                for k, label in [("외국인합계", "외국인"), ("기관합계", "기관"), ("개인", "개인")]:
                    val = inv.get(k)
                    row[label] = f"{val:+,}" if val is not None else "-"
                inv_rows.append(row)
            df_inv = pd.DataFrame(inv_rows)
            st.dataframe(df_inv, use_container_width=True, hide_index=True)

    # ── 탭2: 뉴스 ───────────────────────────────────────────────────────────
    with tabs[1]:
        if not news_data:
            st.info("데이터 수집 후 뉴스가 표시됩니다.")
        else:
            selected_ticker = st.selectbox(
                "종목 선택",
                options=[s["ticker"] for s in stocks],
                format_func=lambda t: next(
                    (f"{s['name']} ({t})" for s in stocks if s["ticker"] == t), t
                ),
            )

            if selected_ticker and selected_ticker in news_data:
                nd = news_data[selected_ticker]

                col_d, col_i = st.columns(2)
                with col_d:
                    st.markdown('<div class="section-title">🇰🇷 국내 뉴스</div>', unsafe_allow_html=True)
                    domestic = nd.get("domestic", [])
                    if domestic:
                        for n in domestic:
                            st.markdown(f"""
                            <div class="news-item">
                                <a href="{n.get('link','#')}" target="_blank">{n.get('title','')}</a>
                                <div class="news-source">{n.get('source','')} · {n.get('published','')[:16]}</div>
                                {f"<div style='margin-top:4px; font-size:0.8rem; color:#607d8b;'>{n.get('summary','')[:120]}...</div>" if n.get('summary') else ''}
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("국내 뉴스를 찾을 수 없습니다.")

                with col_i:
                    st.markdown('<div class="section-title">🌐 해외 뉴스 (번역)</div>', unsafe_allow_html=True)
                    intl = nd.get("international", [])
                    if intl:
                        for n in intl:
                            st.markdown(f"""
                            <div class="news-item">
                                <a href="{n.get('link','#')}" target="_blank">{n.get('title','')}</a>
                                <div class="news-source">{n.get('source','')} · {n.get('published','')[:16]}</div>
                                {f"<div style='margin-top:4px; font-size:0.8rem; color:#607d8b;'>{n.get('summary','')[:120]}...</div>" if n.get('summary') else ''}
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("해외 뉴스를 찾을 수 없습니다.")

    # ── 탭3: 차트 ───────────────────────────────────────────────────────────
    with tabs[2]:
        selected_ticker2 = st.selectbox(
            "차트 종목 선택",
            options=[s["ticker"] for s in stocks],
            format_func=lambda t: next(
                (f"{s['name']} ({t})" for s in stocks if s["ticker"] == t), t
            ),
            key="chart_ticker",
        )
        period_select = st.radio(
            "기간",
            options=["week", "month", "6month"],
            format_func={"week": "이번주", "month": "이번달", "6month": "6개월"}.get,
            horizontal=True,
        )

        stock_selected = next((s for s in stocks if s["ticker"] == selected_ticker2), None)
        if stock_selected:
            hist = stock_selected.get("history", {}).get(period_select, pd.DataFrame())
            name = stock_selected.get("name", selected_ticker2)

            if hist is not None and not hist.empty and "close" in hist.columns:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=hist.index,
                    y=hist["close"],
                    mode="lines",
                    name=name,
                    line=dict(color="#42a5f5", width=2),
                    fill="tozeroy",
                    fillcolor="rgba(66,165,245,0.07)",
                ))

                # 추세선
                import numpy as np
                x_num = np.arange(len(hist))
                if len(x_num) > 1:
                    z = np.polyfit(x_num, hist["close"].values, 1)
                    p = np.poly1d(z)
                    trend_color = "#ef5350" if z[0] > 0 else "#1976d2"
                    fig.add_trace(go.Scatter(
                        x=hist.index,
                        y=p(x_num),
                        mode="lines",
                        name="추세선",
                        line=dict(color=trend_color, width=1.5, dash="dash"),
                    ))

                period_label = {"week": "이번주", "month": "이번달", "6month": "6개월"}[period_select]
                fig.update_layout(
                    title=dict(text=f"{name} 주가 추이 ({period_label})", font=dict(color="#e2e8f0", size=16)),
                    plot_bgcolor="#0d1117",
                    paper_bgcolor="#0d1117",
                    font=dict(color="#90a4ae"),
                    xaxis=dict(gridcolor="#1e3a5f", linecolor="#1e3a5f"),
                    yaxis=dict(gridcolor="#1e3a5f", linecolor="#1e3a5f", tickformat=","),
                    legend=dict(bgcolor="#111827", bordercolor="#1e3a5f"),
                    height=420,
                    margin=dict(l=10, r=10, t=40, b=10),
                )
                st.plotly_chart(fig, use_container_width=True)

                # 기간 요약
                start_p = float(hist["close"].iloc[0])
                end_p = float(hist["close"].iloc[-1])
                ch = ((end_p - start_p) / start_p * 100) if start_p else 0
                currency = "원" if stock_selected.get("market") == "KR" else "$"
                col_s, col_e, col_c = st.columns(3)
                col_s.metric("기간 시작가", f"{start_p:,.0f}{currency}")
                col_e.metric("현재가", f"{end_p:,.0f}{currency}")
                col_c.metric("기간 수익률", f"{ch:+.2f}%")
            else:
                st.info("해당 기간 차트 데이터가 없습니다.")

    # ── 탭4: AI 개별 브리핑 ──────────────────────────────────────────────────
    with tabs[3]:
        if not st.session_state.briefs_generated:
            st.info("상단의 **🤖 AI 리포트 생성** 버튼을 눌러 브리핑을 생성하세요.")
        else:
            selected_ticker3 = st.selectbox(
                "브리핑 종목 선택",
                options=[s["ticker"] for s in stocks],
                format_func=lambda t: next(
                    (f"{s['name']} ({t})" for s in stocks if s["ticker"] == t), t
                ),
                key="brief_ticker",
            )
            brief_text = st.session_state.stock_briefs.get(selected_ticker3, "")
            if brief_text:
                stock_info = next((s for s in stocks if s["ticker"] == selected_ticker3), {})
                name = stock_info.get("name", selected_ticker3)
                close = stock_info.get("close")
                change = stock_info.get("change_rate")
                currency = "원" if stock_info.get("market") == "KR" else "$"

                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"### {name} ({selected_ticker3}) 투자 분석")
                with c2:
                    if close:
                        chg_color = "#ef5350" if (change or 0) > 0 else "#42a5f5"
                        st.markdown(f"""
                        <div style="text-align:right;">
                            <div style="font-size:1.3rem; font-weight:700; color:{chg_color};">
                                {close:,.0f}{currency}
                            </div>
                            <div style="font-size:0.9rem; color:{chg_color};">
                                {f'{change:+.2f}%' if change else 'N/A'}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                st.markdown(f'<div class="report-box">{brief_text}</div>', unsafe_allow_html=True)

            # 포트폴리오 종합
            if st.session_state.portfolio_brief:
                st.markdown("---")
                st.markdown("### 📋 포트폴리오 종합 전략")
                st.markdown(f'<div class="report-box">{st.session_state.portfolio_brief}</div>',
                            unsafe_allow_html=True)

    # ── 탭5: 최종 리포트 & 이메일 ────────────────────────────────────────────
    with tabs[4]:
        if not st.session_state.full_report:
            st.info("AI 리포트를 먼저 생성해주세요.")
        else:
            st.markdown('<div class="section-title">📋 최종 브리핑 리포트</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="report-box">{st.session_state.full_report}</div>',
                unsafe_allow_html=True,
            )

            # 다운로드
            st.download_button(
                label="📥 리포트 다운로드 (.txt)",
                data=st.session_state.full_report.encode("utf-8"),
                file_name=f"stock_briefing_{date.today().isoformat()}.txt",
                mime="text/plain",
                use_container_width=True,
            )

            # 이메일 발송
            st.markdown("---")
            st.markdown('<div class="section-title">📧 이메일 발송</div>', unsafe_allow_html=True)

            col_email, col_send = st.columns([3, 1])
            with col_email:
                recipient = st.text_input(
                    "수신 이메일",
                    value=to_email,
                    placeholder="recipient@email.com",
                    key="final_to_email",
                )
            with col_send:
                st.markdown("<br>", unsafe_allow_html=True)
                btn_send = st.button("📤 이메일 발송", type="primary", use_container_width=True)

            if btn_send:
                from email_sender import send_report_email
                with st.spinner("이메일 발송 중..."):
                    success, msg = send_report_email(
                        to_address=recipient,
                        report_text=st.session_state.full_report,
                        gmail_user=gmail_user,
                        gmail_password=gmail_pw,
                    )
                if success:
                    st.success(msg)
                else:
                    st.error(msg)
                    st.markdown("""
                    **Gmail 앱 비밀번호 설정 방법:**
                    1. Google 계정 → 보안 → 2단계 인증 활성화
                    2. 앱 비밀번호 생성 → 앱: 메일, 기기: 기타
                    3. 생성된 16자리 비밀번호를 사이드바에 입력
                    """)
