"""
stock_data.py — pykrx + yfinance 주가 데이터 수집
"""
from __future__ import annotations

import re
from datetime import date, timedelta
from typing import Optional

import pandas as pd

# ── 날짜 헬퍼 ────────────────────────────────────────────────────────────────

def last_trading_day(d: Optional[date] = None) -> date:
    """오늘이 토/일이면 직전 금요일 반환."""
    d = d or date.today()
    while d.weekday() >= 5:  # 5=토, 6=일
        d -= timedelta(days=1)
    return d


def date_range_for_period(period: str) -> tuple[date, date]:
    """period: 'week' | 'month' | '6month'"""
    end = last_trading_day()
    if period == "week":
        start = end - timedelta(weeks=1)
    elif period == "month":
        start = end - timedelta(days=30)
    else:  # 6month
        start = end - timedelta(days=183)
    return start, end


# ── 종목 구분 헬퍼 ───────────────────────────────────────────────────────────

def is_kr_code(ticker: str) -> bool:
    """6자리 숫자면 국내 종목으로 판단."""
    return bool(re.fullmatch(r"\d{6}", ticker.strip()))


def kr_to_yf(ticker: str) -> str:
    """pykrx 코드 → yfinance 티커 (KOSPI .KS / KOSDAQ .KQ 자동 추론)."""
    from pykrx import stock as px
    try:
        market = px.get_market_ticker_market(ticker.strip())
        suffix = ".KS" if market == "KOSPI" else ".KQ"
    except Exception:
        suffix = ".KS"
    return ticker.strip() + suffix


# ── 국내 종목 데이터 (pykrx) ─────────────────────────────────────────────────

def fetch_kr_stock(ticker: str) -> dict:
    """pykrx로 오늘 종가·등락·수급 데이터 반환."""
    from pykrx import stock as px

    td = last_trading_day()
    td_str = td.strftime("%Y%m%d")

    try:
        name = px.get_market_ticker_name(ticker)
    except Exception:
        name = ticker

    # 종가
    try:
        ohlcv = px.get_market_ohlcv(td_str, td_str, ticker)
        if ohlcv.empty:
            # 1주일 이내로 확장
            w_start = (td - timedelta(days=7)).strftime("%Y%m%d")
            ohlcv = px.get_market_ohlcv(w_start, td_str, ticker)
        row = ohlcv.iloc[-1] if not ohlcv.empty else None
    except Exception:
        row = None

    close = float(row["종가"]) if row is not None and "종가" in row else None
    change_rate = float(row["등락률"]) if row is not None and "등락률" in row else None
    volume = int(row["거래량"]) if row is not None and "거래량" in row else None

    # 수급 (외인·기관·개인)
    investor = {}
    try:
        inv_df = px.get_market_trading_value_by_investor(td_str, td_str, ticker)
        if not inv_df.empty:
            for label in ["외국인합계", "기관합계", "개인"]:
                if label in inv_df.index:
                    investor[label] = int(inv_df.loc[label, "순매수"])
    except Exception:
        pass

    # 기간별 OHLCV
    history = {}
    for period in ("week", "month", "6month"):
        start, end = date_range_for_period(period)
        try:
            df = px.get_market_ohlcv(
                start.strftime("%Y%m%d"), end.strftime("%Y%m%d"), ticker
            )
            history[period] = df[["종가"]].rename(columns={"종가": "close"}) if not df.empty else pd.DataFrame()
        except Exception:
            history[period] = pd.DataFrame()

    return {
        "ticker": ticker,
        "name": name,
        "market": "KR",
        "close": close,
        "change_rate": change_rate,
        "volume": volume,
        "date": td.isoformat(),
        "investor": investor,
        "history": history,
    }


# ── 해외 종목 데이터 (yfinance) ──────────────────────────────────────────────

def fetch_us_stock(ticker: str) -> dict:
    """yfinance로 해외 종목 종가·수급 데이터 반환."""
    import yfinance as yf

    td = last_trading_day()
    yf_ticker = ticker.strip().upper()
    obj = yf.Ticker(yf_ticker)

    try:
        info = obj.info
        name = info.get("longName") or info.get("shortName") or yf_ticker
    except Exception:
        name = yf_ticker
        info = {}

    # 종가
    try:
        hist_1d = obj.history(period="5d")
        row = hist_1d.iloc[-1] if not hist_1d.empty else None
    except Exception:
        row = None

    close = float(row["Close"]) if row is not None else None
    prev_close = float(hist_1d.iloc[-2]["Close"]) if (row is not None and len(hist_1d) > 1) else None
    change_rate = ((close - prev_close) / prev_close * 100) if (close and prev_close) else None
    volume = int(row["Volume"]) if row is not None else None

    # 기간별 OHLCV
    history = {}
    period_map = {"week": "5d", "month": "1mo", "6month": "6mo"}
    for period, yf_period in period_map.items():
        try:
            df = obj.history(period=yf_period)[["Close"]].rename(columns={"Close": "close"})
            history[period] = df
        except Exception:
            history[period] = pd.DataFrame()

    return {
        "ticker": yf_ticker,
        "name": name,
        "market": "US",
        "close": close,
        "change_rate": change_rate,
        "volume": volume,
        "date": td.isoformat(),
        "investor": {},   # yfinance는 국내 수급 없음
        "history": history,
    }


# ── 통합 수집 ────────────────────────────────────────────────────────────────

def fetch_stock(ticker: str) -> dict:
    ticker = ticker.strip()
    if is_kr_code(ticker):
        return fetch_kr_stock(ticker)
    else:
        return fetch_us_stock(ticker)


def fetch_all_stocks(tickers: list[str]) -> list[dict]:
    results = []
    for t in tickers[:10]:   # 최대 10종목
        try:
            results.append(fetch_stock(t))
        except Exception as e:
            results.append({
                "ticker": t, "name": t, "market": "?",
                "close": None, "change_rate": None, "volume": None,
                "date": last_trading_day().isoformat(),
                "investor": {}, "history": {},
                "error": str(e),
            })
    return results
