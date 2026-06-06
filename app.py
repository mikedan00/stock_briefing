"""
app.py — 주식 AI 브리핑 Streamlit 앱
모델: google/gemma-4-26B-A4B-it:deepinfra (기본)
종목명 입력 지원 (예: 삼성전자, SK하이닉스, AAPL)
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import date

# ── 페이지 설정 ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="주식 AI 브리핑",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&family=JetBrains+Mono:wght@400;600&display=swap');
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
.stApp { background: linear-gradient(135deg, #0a0e1a 0%, #0f1629 50%, #0a0e1a 100%); }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0d1117 0%, #161b2e 100%); border-right: 1px solid #1e3a5f; }
.metric-card { background: linear-gradient(135deg,#111827,#1a2540); border:1px solid #1e3a5f; border-radius:12px; padding:16px 20px; margin:6px 0; box-shadow:0 4px 16px rgba(0,0,0,.4); }
.metric-card h3 { color:#64b5f6; font-size:.8rem; font-weight:500; letter-spacing:1px; text-transform:uppercase; margin:0 0 6px 0; }
.metric-card .value { font-family:'JetBrains Mono',monospace; font-size:1.6rem; font-weight:700; color:#e2e8f0; margin:0; }
.news-item { background:#111827; border-left:3px solid #1565c0; border-radius:0 8px 8px 0; padding:10px 14px; margin:6px 0; font-size:.88rem; color:#cfd8dc; line-height:1.5; }
.news-item .news-source { font-size:.75rem; color:#546e7a; margin-top:4px; }
.news-item a { color:#90caf9; text-decoration:none; }
.news-item a:hover { text-decoration:underline; }
.report-box { background:#0d1117; border:1px solid #1e3a5f; border-radius:12px; padding:24px; font-size:.92rem; line-height:1.9; color:#cfd8dc; white-space:pre-wrap; font-family:'Noto Sans KR',sans-serif; }
.page-header { background:linear-gradient(135deg,#0d1b4b,#1a237e,#0d47a1); border-radius:16px; padding:28px 32px; margin-bottom:24px; border:1px solid #1565c0; box-shadow:0 8px 32px rgba(13,71,161,.3); }
.page-header h1 { color:#fff; font-size:1.8rem; font-weight:900; margin:0; }
.page-header p { color:#90caf9; margin:6px 0 0 0; font-size:.95rem; }
.stTabs [data-baseweb="tab-list"] { background:#111827; border-radius:8px; padding:4px; gap:4px; }
.stTabs [data-baseweb="tab"] { color:#90a4ae; border-radius:6px; font-weight:500; }
.stTabs [aria-selected="true"] { background:#1565c0 !important; color:white !important; }
.stButton>button { background:linear-gradient(135deg,#1565c0,#0d47a1); color:white; border:none; border-radius:8px; font-weight:600; padding:10px 20px; font-family:'Noto Sans KR',sans-serif; transition:all .2s; }
.stButton>button:hover { background:linear-gradient(135deg,#1976d2,#1565c0); box-shadow:0 4px 16px rgba(21,101,192,.4); transform:translateY(-1px); }
.section-title { color:#64b5f6; font-size:1.0rem; font-weight:700; letter-spacing:.5px; margin:20px 0 10px 0; padding-bottom:6px; border-bottom:1px solid #1e3a5f; }
.stTextInput input,.stTextArea textarea { background:#111827 !important; color:#e2e8f0 !important; border-color:#1e3a5f !important; border-radius:8px !important; }
.badge-up { background:rgba(239,83,80,.15); color:#ef5350; border:1px solid rgba(239,83,80,.3); border-radius:4px; padding:2px 8px; font-size:.8rem; font-weight:600; }
.badge-down { background:rgba(66,165,245,.15); color:#42a5f5; border:1px solid rgba(66,165,245,.3); border-radius:4px; padding:2px 8px; font-size:.8rem; font-weight:600; }
.badge-flat { background:rgba(144,164,174,.15); color:#90a4ae; border:1px solid rgba(144,164,174,.3); border-radius:4px; padding:2px 8px; font-size:.8rem; }
.model-badge { background:rgba(21,101,192,.2); color:#64b5f6; border:1px solid #1565c0; border-radius:6px; padding:4px 10px; font-size:.78rem; font-family:'JetBrains Mono',monospace; }
</style>
""", unsafe_allow_html=True)

# ── 세션 초기화 ──────────────────────────────────────────────────────────────
for k, v in {
    "stocks_data": [], "news_data": {}, "stock_briefs": {},
    "portfolio_brief": "", "full_report": "",
    "data_loaded": False, "briefs_generated": False,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── 사이드바 ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ 설정")
    st.markdown("---")

    st.markdown("### 🤖 AI 엔진")
    hf_token = st.text_input(
        "HuggingFace Token",
        type="password",
        value=os.getenv("HF_TOKEN", ""),
        placeholder="hf_xxxxxxxxxxxx",
        help="https://huggingface.co/settings/tokens",
    )
    if hf_token:
        os.environ["HF_TOKEN"] = hf_token

    import config as cfg
    selected_model = st.selectbox(
        "모델 선택",
        options=cfg.HF_MODEL_CANDIDATES,
        index=0,
        help="HF Router 경유 모델. 기본: gemma-4-26B:deepinfra",
    )
    os.environ["HF_MODEL_OVERRIDE"] = selected_model

    st.markdown(f'<div class="model-badge">▶ {selected_model}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📧 Gmail 발송")
    gmail_user = st.text_input("발신 Gmail", value=os.getenv("GMAIL_USER", ""), placeholder="your@gmail.com")
    gmail_pw = st.text_input("앱 비밀번호", type="password", value=os.getenv("GMAIL_APP_PASSWORD", ""), placeholder="xxxx xxxx xxxx xxxx")
    to_email = st.text_input("수신 이메일", placeholder="recipient@email.com")

    st.markdown("---")
    st.markdown("""
    <div style="font-size:.75rem;color:#546e7a;line-height:1.7;">
    <b style="color:#64b5f6;">종목 입력 예시</b><br>
    🇰🇷 종목명: 삼성전자, SK하이닉스<br>
    🇰🇷 코드: 005930, 000660<br>
    🇺🇸 티커: AAPL, NVDA, TSLA<br>
    ※ 쉼표 또는 줄바꿈으로 구분<br>
    ※ 최대 10종목
    </div>
    """, unsafe_allow_html=True)

# ── 헤더 ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <h1>📊 주식 AI 브리핑 시스템</h1>
    <p>HuggingFace Router · Gemma-4 26B · 실시간 주가 · 뉴스 · 투자 전략 리포트</p>
</div>
""", unsafe_allow_html=True)
st.markdown(f"<p style='color:#546e7a;font-size:.85rem;'>📅 {date.today().strftime('%Y년 %m월 %d일')}</p>", unsafe_allow_html=True)

# ── 종목 입력 ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">🔍 분석 종목 입력 (종목명 또는 코드/티커)</div>', unsafe_allow_html=True)

col_in, col_hint = st.columns([3, 1])
with col_in:
    ticker_input = st.text_area(
        "종목 입력 (쉼표·줄바꿈 구분, 최대 10개)",
        placeholder="삼성전자, SK하이닉스, AAPL, NVDA\n또는\n005930, 000660, TSLA",
        height=100,
    )
with col_hint:
    st.markdown("""
    <div style="background:#111827;border:1px solid #1e3a5f;border-radius:8px;padding:14px;font-size:.78rem;color:#90a4ae;margin-top:24px;">
    <b style="color:#64b5f6;">자주 쓰는 종목</b><br>
    삼성전자 · SK하이닉스<br>
    네이버 · 카카오<br>
    현대차 · 기아<br>
    AAPL · NVDA · TSLA<br>
    MSFT · META · AMZN
    </div>
    """, unsafe_allow_html=True)


def parse_inputs(raw: str) -> list[str]:
    """쉼표·줄바꿈으로 구분, 빈값·중복 제거, 최대 10개."""
    import re
    tokens = re.split(r"[,\n]+", raw.strip())
    seen, result = set(), []
    for t in tokens:
        t = t.strip()
        if t and t not in seen:
            seen.add(t)
            result.append(t)
    return result[:10]


col_b1, col_b2, _ = st.columns([1.5, 1.5, 3])
with col_b1:
    btn_load = st.button("📥 데이터 수집", type="primary", use_container_width=True)
with col_b2:
    btn_report = st.button(
        "🤖 AI 리포트 생성",
        use_container_width=True,
        disabled=not st.session_state.data_loaded,
        help="데이터 수집 후 활성화됩니다",
    )

# ── 데이터 수집 ──────────────────────────────────────────────────────────────
if btn_load:
    inputs = parse_inputs(ticker_input)
    if not inputs:
        st.error("종목을 입력해주세요.")
    else:
        from stock_data import fetch_all_stocks
        from news_fetcher import fetch_all_news

        with st.spinner(f"📡 {len(inputs)}개 종목 주가 수집 중..."):
            stocks = fetch_all_stocks(inputs)
            st.session_state.stocks_data = stocks

        progress = st.progress(0, text="📰 뉴스 수집 중...")
        news_data = {}
        for i, stock in enumerate(stocks):
            progress.progress((i + 1) / len(stocks), text=f"📰 {stock['name']} 뉴스 수집 중...")
            news_data[stock["ticker"]] = fetch_all_news(stock)
        st.session_state.news_data = news_data

        st.session_state.data_loaded = True
        st.session_state.briefs_generated = False
        st.session_state.stock_briefs = {}
        st.session_state.portfolio_brief = ""
        st.session_state.full_report = ""

        success = [s for s in stocks if s.get("close") is not None]
        fail = [s for s in stocks if s.get("close") is None]
        st.success(f"✅ {len(success)}개 종목 수집 완료!" + (f" ({len(fail)}개 실패)" if fail else ""))
        if fail:
            st.warning("수집 실패: " + ", ".join(f"{s['name']}({s.get('error','?')})" for s in fail))
        st.rerun()

# ── AI 리포트 생성 ────────────────────────────────────────────────────────────
if btn_report:
    if not st.session_state.data_loaded or not st.session_state.stocks_data:
        st.error("먼저 데이터를 수집해주세요.")
    else:
        token_check = os.environ.get("HF_TOKEN") or cfg.HF_TOKEN
        if not token_check:
            st.error("❌ HuggingFace Token이 없습니다. 사이드바에서 입력해주세요.")
        else:
            from report_generator import generate_stock_brief, generate_portfolio_brief, build_full_report_text

            stocks = st.session_state.stocks_data
            news_data = st.session_state.news_data
            stock_briefs = {}

            total = len(stocks) + 1
            progress = st.progress(0, text="🤖 AI 분석 시작...")

            for i, stock in enumerate(stocks):
                ticker = stock["ticker"]
                name = stock.get("name", ticker)
                progress.progress(i / total, text=f"🤖 {name} 분석 중... ({i+1}/{len(stocks)})")
                with st.spinner(f"{name} AI 브리핑 생성 중..."):
                    brief = generate_stock_brief(stock, news_data.get(ticker, {}))
                stock_briefs[ticker] = brief

            progress.progress(len(stocks) / total, text="📋 포트폴리오 종합 분석 중...")
            with st.spinner("포트폴리오 종합 리포트 생성 중..."):
                portfolio_brief = generate_portfolio_brief(stocks, [])

            progress.progress(1.0, text="✅ 완료!")

            full_report = build_full_report_text(
                stocks, [], list(stock_briefs.values()), portfolio_brief
            )

            st.session_state.stock_briefs = stock_briefs
            st.session_state.portfolio_brief = portfolio_brief
            st.session_state.full_report = full_report
            st.session_state.briefs_generated = True
            st.success("✅ AI 리포트 생성 완료! 'AI 브리핑' 탭에서 확인하세요.")
            st.rerun()

# ── 결과 탭 ──────────────────────────────────────────────────────────────────
if st.session_state.data_loaded and st.session_state.stocks_data:
    stocks = st.session_state.stocks_data
    news_data = st.session_state.news_data

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 주가 현황", "📰 뉴스", "📊 차트", "🤖 AI 브리핑", "📋 최종 리포트"])

    # ── 탭1: 주가 현황 ───────────────────────────────────────────────────────
    with tab1:
        st.markdown('<div class="section-title">📈 오늘 종가 현황</div>', unsafe_allow_html=True)
        for i in range(0, len(stocks), 3):
            cols = st.columns(3)
            for col, stock in zip(cols, stocks[i:i+3]):
                with col:
                    name = stock.get("name", stock["ticker"])
                    close = stock.get("close")
                    change = stock.get("change_rate")
                    market = stock.get("market", "")
                    volume = stock.get("volume")
                    currency = "원" if market == "KR" else "$"
                    flag = "🇰🇷" if market == "KR" else "🇺🇸"
                    close_str = f"{close:,.0f}" if close else "N/A"
                    vol_str = f"{volume:,}" if volume else "-"
                    if change is not None:
                        badge = (f'<span class="badge-up">▲ {change:+.2f}%</span>' if change > 0
                                 else f'<span class="badge-down">▼ {change:.2f}%</span>' if change < 0
                                 else '<span class="badge-flat">─ 0.00%</span>')
                        val_color = "#ef5350" if change > 0 else "#42a5f5" if change < 0 else "#90a4ae"
                    else:
                        badge = '<span class="badge-flat">데이터 없음</span>'
                        val_color = "#90a4ae"
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>{flag} {stock['ticker']} · {market}</h3>
                        <div style="font-weight:700;font-size:1.05rem;color:#e2e8f0;margin-bottom:4px;">{name}</div>
                        <div class="value" style="color:{val_color};">{close_str} {currency}</div>
                        <div style="margin-top:8px;">{badge}</div>
                        <div style="margin-top:6px;font-size:.76rem;color:#546e7a;">거래량: {vol_str} | {stock.get('date','')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if stock.get("error"):
                        st.caption(f"⚠️ {stock['error'][:80]}")

        kr_inv = [s for s in stocks if s.get("market") == "KR" and s.get("investor")]
        if kr_inv:
            st.markdown('<div class="section-title">💹 외인·기관·개인 수급 (당일)</div>', unsafe_allow_html=True)
            rows = []
            for s in kr_inv:
                inv = s.get("investor", {})
                def fmt(v): return f"{v:+,}" if v is not None else "-"
                rows.append({
                    "종목": s.get("name", s["ticker"]),
                    "코드": s["ticker"],
                    "외국인(원)": fmt(inv.get("외국인합계")),
                    "기관(원)": fmt(inv.get("기관합계")),
                    "개인(원)": fmt(inv.get("개인")),
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # ── 탭2: 뉴스 ───────────────────────────────────────────────────────────
    with tab2:
        if not news_data:
            st.info("데이터 수집 후 뉴스가 표시됩니다.")
        else:
            sel = st.selectbox("종목 선택", [s["ticker"] for s in stocks],
                               format_func=lambda t: next((f"{s['name']} ({t})" for s in stocks if s["ticker"]==t), t))
            if sel in news_data:
                nd = news_data[sel]
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown('<div class="section-title">🇰🇷 국내 뉴스 (네이버·구글)</div>', unsafe_allow_html=True)
                    for n in nd.get("domestic", []) or [st.info("국내 뉴스 없음")]:
                        if isinstance(n, dict):
                            st.markdown(f"""<div class="news-item">
                                <a href="{n.get('link','#')}" target="_blank">{n.get('title','')}</a>
                                <div class="news-source">{n.get('source','')} · {str(n.get('published',''))[:16]}</div>
                            </div>""", unsafe_allow_html=True)
                with c2:
                    st.markdown('<div class="section-title">🌐 해외 뉴스 (번역됨)</div>', unsafe_allow_html=True)
                    for n in nd.get("international", []) or [st.info("해외 뉴스 없음")]:
                        if isinstance(n, dict):
                            st.markdown(f"""<div class="news-item">
                                <a href="{n.get('link','#')}" target="_blank">{n.get('title','')}</a>
                                <div class="news-source">{n.get('source','')} · {str(n.get('published',''))[:16]}</div>
                            </div>""", unsafe_allow_html=True)

    # ── 탭3: 차트 ───────────────────────────────────────────────────────────
    with tab3:
        sel2 = st.selectbox("차트 종목", [s["ticker"] for s in stocks],
                            format_func=lambda t: next((f"{s['name']} ({t})" for s in stocks if s["ticker"]==t), t),
                            key="chart_sel")
        period_sel = st.radio("기간", ["week","month","6month"],
                              format_func={"week":"이번주","month":"이번달","6month":"6개월"}.get,
                              horizontal=True)
        s_info = next((s for s in stocks if s["ticker"]==sel2), None)
        if s_info:
            hist = s_info.get("history", {}).get(period_sel, pd.DataFrame())
            name = s_info.get("name", sel2)
            if hist is not None and not hist.empty and "close" in hist.columns:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=hist.index, y=hist["close"], mode="lines", name=name,
                                         line=dict(color="#42a5f5", width=2),
                                         fill="tozeroy", fillcolor="rgba(66,165,245,0.07)"))
                xn = np.arange(len(hist))
                if len(xn) > 1:
                    z = np.polyfit(xn, hist["close"].values, 1)
                    p = np.poly1d(z)
                    tc = "#ef5350" if z[0] > 0 else "#1976d2"
                    fig.add_trace(go.Scatter(x=hist.index, y=p(xn), mode="lines", name="추세선",
                                             line=dict(color=tc, width=1.5, dash="dash")))
                label = {"week":"이번주","month":"이번달","6month":"6개월"}[period_sel]
                currency = "원" if s_info.get("market")=="KR" else "$"
                fig.update_layout(
                    title=dict(text=f"{name} 주가 추이 ({label})", font=dict(color="#e2e8f0", size=16)),
                    plot_bgcolor="#0d1117", paper_bgcolor="#0d1117",
                    font=dict(color="#90a4ae"),
                    xaxis=dict(gridcolor="#1e3a5f", linecolor="#1e3a5f"),
                    yaxis=dict(gridcolor="#1e3a5f", linecolor="#1e3a5f", tickformat=","),
                    legend=dict(bgcolor="#111827", bordercolor="#1e3a5f"),
                    height=420, margin=dict(l=10,r=10,t=40,b=10),
                )
                st.plotly_chart(fig, use_container_width=True)
                sp = float(hist["close"].iloc[0])
                ep = float(hist["close"].iloc[-1])
                ch = (ep-sp)/sp*100 if sp else 0
                c1,c2,c3 = st.columns(3)
                c1.metric("시작가", f"{sp:,.0f}{currency}")
                c2.metric("현재가", f"{ep:,.0f}{currency}")
                c3.metric("기간 수익률", f"{ch:+.2f}%")
            else:
                st.info("차트 데이터가 없습니다.")

    # ── 탭4: AI 브리핑 ───────────────────────────────────────────────────────
    with tab4:
        if not st.session_state.briefs_generated:
            st.info("⬆️ 상단 **🤖 AI 리포트 생성** 버튼을 눌러주세요.")
            st.markdown("""
            <div style="background:#111827;border:1px solid #1565c0;border-radius:10px;padding:16px;margin-top:10px;font-size:.88rem;color:#90a4ae;">
            <b style="color:#64b5f6;">AI 브리핑 포함 내용</b><br>
            ① 종목 현황 요약 &nbsp;② 주가 추이 분석<br>
            ③ 외인·기관·개인 수급 분석 &nbsp;④ 뉴스 임팩트<br>
            ⑤ 리스크 요인 &nbsp;⑥ 내일 매매 전략<br>
            ⑦ 내일 예상 방향 & 등락률
            </div>
            """, unsafe_allow_html=True)
        else:
            sel3 = st.selectbox("브리핑 종목", [s["ticker"] for s in stocks],
                                format_func=lambda t: next((f"{s['name']} ({t})" for s in stocks if s["ticker"]==t), t),
                                key="brief_sel")
            brief = st.session_state.stock_briefs.get(sel3, "")
            if brief:
                si = next((s for s in stocks if s["ticker"]==sel3), {})
                name = si.get("name", sel3)
                close = si.get("close")
                change = si.get("change_rate")
                currency = "원" if si.get("market")=="KR" else "$"
                chg_color = "#ef5350" if (change or 0) > 0 else "#42a5f5"
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.markdown(f"### 📌 {name} ({sel3}) 투자 분석")
                with c2:
                    if close:
                        st.markdown(f"""<div style="text-align:right;">
                            <div style="font-size:1.3rem;font-weight:700;color:{chg_color};">{close:,.0f}{currency}</div>
                            <div style="font-size:.9rem;color:{chg_color};">{f'{change:+.2f}%' if change else 'N/A'}</div>
                        </div>""", unsafe_allow_html=True)
                # 오류 여부 확인
                if brief.startswith("[LLM") or brief.startswith("[오류"):
                    st.error(f"AI 오류: {brief}")
                    st.info("💡 HF_TOKEN 확인, 모델 변경 후 재시도해주세요.")
                else:
                    st.markdown(f'<div class="report-box">{brief}</div>', unsafe_allow_html=True)

            if st.session_state.portfolio_brief:
                st.markdown("---")
                st.markdown("### 📋 포트폴리오 종합 전략")
                pb = st.session_state.portfolio_brief
                if pb.startswith("[LLM") or pb.startswith("[오류"):
                    st.error(pb)
                else:
                    st.markdown(f'<div class="report-box">{pb}</div>', unsafe_allow_html=True)

    # ── 탭5: 최종 리포트 & 이메일 ────────────────────────────────────────────
    with tab5:
        if not st.session_state.full_report:
            st.info("AI 리포트를 먼저 생성해주세요.")
        else:
            st.markdown('<div class="section-title">📋 최종 브리핑 리포트</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="report-box">{st.session_state.full_report}</div>', unsafe_allow_html=True)
            st.download_button(
                "📥 리포트 다운로드 (.txt)",
                data=st.session_state.full_report.encode("utf-8"),
                file_name=f"stock_briefing_{date.today()}.txt",
                mime="text/plain",
                use_container_width=True,
            )
            st.markdown("---")
            st.markdown('<div class="section-title">📧 이메일 발송</div>', unsafe_allow_html=True)
            c1, c2 = st.columns([3,1])
            with c1:
                recipient = st.text_input("수신 이메일", value=to_email, placeholder="recipient@email.com", key="send_to")
            with c2:
                st.markdown("<br>", unsafe_allow_html=True)
                btn_send = st.button("📤 발송", type="primary", use_container_width=True)
            if btn_send:
                from email_sender import send_report_email
                with st.spinner("이메일 발송 중..."):
                    ok, msg = send_report_email(recipient, st.session_state.full_report, gmail_user, gmail_pw)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)
                    with st.expander("Gmail 앱 비밀번호 설정 방법"):
                        st.markdown("""
                        1. myaccount.google.com → **보안** 탭
                        2. **2단계 인증** 활성화 (필수)
                        3. 검색창에 **앱 비밀번호** 검색
                        4. 앱: `메일`, 기기: `기타` → **생성**
                        5. 표시된 **16자리** 비밀번호를 사이드바에 입력
                        """)
