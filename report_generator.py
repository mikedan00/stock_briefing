"""
report_generator.py — 주식 브리핑 리포트 생성
"""
from __future__ import annotations

from datetime import date
from llm_engine import call_llm, EXPERT_SYSTEM


def _format_investor(investor: dict) -> str:
    if not investor:
        return "수급 데이터 없음"
    lines = []
    label_map = {"외국인합계": "외국인", "기관합계": "기관", "개인": "개인"}
    for k, label in label_map.items():
        if k in investor:
            val = investor[k]
            sign = "+" if val >= 0 else ""
            lines.append(f"{label}: {sign}{val:,}원")
    return " | ".join(lines) if lines else "수급 데이터 없음"


def _news_summary(news_list: list[dict], max_items: int = 5) -> str:
    if not news_list:
        return "뉴스 없음"
    items = news_list[:max_items]
    return "\n".join(
        f"- [{i+1}] {n['title']} ({n.get('source','')})" for i, n in enumerate(items)
    )


def _history_summary(history: dict) -> str:
    lines = []
    for period, label in [("week", "이번주"), ("month", "이번달"), ("6month", "6개월")]:
        df = history.get(period)
        if df is not None and not df.empty and "close" in df.columns:
            start_p = float(df["close"].iloc[0])
            end_p = float(df["close"].iloc[-1])
            change = ((end_p - start_p) / start_p * 100) if start_p else 0
            sign = "+" if change >= 0 else ""
            lines.append(f"{label}: {start_p:,.0f}→{end_p:,.0f} ({sign}{change:.1f}%)")
        else:
            lines.append(f"{label}: 데이터 없음")
    return " | ".join(lines)


# ── 단일 종목 브리핑 ─────────────────────────────────────────────────────────

def generate_stock_brief(stock: dict, news: dict) -> str:
    """LLM으로 단일 종목 투자 브리핑 생성."""
    name = stock.get("name", stock["ticker"])
    close = stock.get("close")
    change = stock.get("change_rate")
    volume = stock.get("volume")
    market = stock.get("market", "")
    today = stock.get("date", date.today().isoformat())

    close_str = f"{close:,.0f}" if close else "N/A"
    change_str = f"{change:+.2f}%" if change is not None else "N/A"
    volume_str = f"{volume:,}" if volume else "N/A"

    investor_str = _format_investor(stock.get("investor", {}))
    history_str = _history_summary(stock.get("history", {}))

    domestic_news = _news_summary(news.get("domestic", []))
    intl_news = _news_summary(news.get("international", []))

    prompt = f"""
아래 데이터를 바탕으로 {name}({stock['ticker']}) 종목에 대한 전문 투자 브리핑을 작성해주세요.

## 기본 데이터 ({today} 기준)
- 시장: {market}
- 종가: {close_str}원/달러
- 등락률: {change_str}
- 거래량: {volume_str}
- 수급(당일): {investor_str}

## 주가 추이
{history_str}

## 국내 뉴스 (최근)
{domestic_news}

## 해외 뉴스 (최근)
{intl_news}

---
다음 항목을 포함한 전문 브리핑을 작성해주세요:

1. **종목 현황 요약** (2~3문장)
2. **주가 추이 분석** (이번주/이번달/6개월 흐름 해석)
3. **수급 분석** (외인·기관·개인 동향 해석, 국내주 한정)
4. **뉴스 임팩트 분석** (주요 뉴스가 주가에 미치는 영향)
5. **리스크 요인** (단기 하락 위험 요소)
6. **내일 매매 전략** (매수/매도/관망 중 판단 + 구체적 전략)
7. **내일 예상 방향** (상승/하락/횡보 + 예상 등락률 %)

전문적이고 실행 가능한 분석을 제공해주세요.
"""
    return call_llm(prompt, system=EXPERT_SYSTEM, max_tokens=1500)


# ── 전체 포트폴리오 브리핑 ───────────────────────────────────────────────────

def generate_portfolio_brief(stocks: list[dict], all_news: list[dict]) -> str:
    """LLM으로 전체 포트폴리오 종합 브리핑 생성."""
    today = date.today().isoformat()

    stock_lines = []
    for s in stocks:
        name = s.get("name", s["ticker"])
        close = s.get("close")
        change = s.get("change_rate")
        close_str = f"{close:,.0f}" if close else "N/A"
        change_str = f"{change:+.2f}%" if change is not None else "N/A"
        stock_lines.append(f"- {name}({s['ticker']}): {close_str} / {change_str}")

    stocks_text = "\n".join(stock_lines)

    prompt = f"""
오늘({today}) 아래 포트폴리오 전체에 대한 종합 투자 전략 리포트를 작성해주세요.

## 보유 종목 현황
{stocks_text}

---
다음 항목을 포함한 포트폴리오 종합 리포트를 작성해주세요:

1. **오늘 시장 총평** (국내외 시장 전반 흐름)
2. **포트폴리오 종합 평가** (전체 수익성·리스크 평가)
3. **섹터별 분석** (종목들이 속한 섹터 동향)
4. **내일 전체 투자 전략** (포트폴리오 관점의 매매 전략)
5. **Top Pick & Bottom Pick** (내일 가장 기대/우려되는 종목)
6. **리스크 관리 포인트** (손절/익절 기준 제안)

전문 투자자 시각에서 실행 가능한 전략을 구체적으로 제시해주세요.
"""
    return call_llm(prompt, system=EXPERT_SYSTEM, max_tokens=2000)


# ── 이메일용 전체 리포트 텍스트 ─────────────────────────────────────────────

def build_full_report_text(
    stocks: list[dict],
    all_news: list[dict],
    stock_briefs: list[str],
    portfolio_brief: str,
) -> str:
    today = date.today().isoformat()
    sep = "=" * 60

    sections = [
        f"📊 주식 투자 브리핑 리포트",
        f"기준일: {today}",
        sep,
        "【 포트폴리오 종합 전략 】",
        portfolio_brief,
        sep,
    ]

    for stock, brief in zip(stocks, stock_briefs):
        name = stock.get("name", stock["ticker"])
        sections.append(f"【 {name}({stock['ticker']}) 개별 분석 】")
        sections.append(brief)
        sections.append("-" * 40)

    sections.append(sep)
    sections.append("본 리포트는 AI 분석 기반이며 투자 결정은 본인 책임입니다.")

    return "\n\n".join(sections)
