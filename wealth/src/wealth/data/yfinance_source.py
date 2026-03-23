"""Yahoo Finance data source implementation."""

from datetime import datetime
from typing import Optional
import yfinance as yf
from wealth.data.base import (
    DataSource,
    MarketType,
    StockInfo,
    FundInfo,
    KlineData,
    RealtimeQuote,
)


class YFinanceSource(DataSource):
    def __init__(self):
        self._cache = {}

    def _parse_market(self, symbol: str) -> MarketType:
        if symbol.endswith(".HK"):
            return MarketType.HK_STOCK
        elif symbol.isupper() and len(symbol) <= 5:
            return MarketType.US_STOCK
        return MarketType.US_STOCK

    def get_realtime_quote(self, symbol: str) -> RealtimeQuote:
        ticker = yf.Ticker(symbol)
        info = ticker.fast_info
        price = info.last_price or 0
        prev_close = info.previous_close or price
        change = price - prev_close
        change_pct = (change / prev_close * 100) if prev_close else 0

        return RealtimeQuote(
            symbol=symbol,
            name=info.long_name or symbol,
            current_price=price,
            change=change,
            change_pct=change_pct,
            open=info.open or price,
            high=info.day_high or price,
            low=info.day_low or price,
            volume=info.last_volume or 0,
            amount=0,
            timestamp=datetime.now(),
        )

    def get_kline_data(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        period: str = "daily",
        adjust: str = "qfq",
    ) -> list[KlineData]:
        ticker = yf.Ticker(symbol)

        period_map = {
            "daily": "1d",
            "weekly": "1wk",
            "monthly": "1mo",
            "60min": "60m",
            "30min": "30m",
            "15min": "15m",
            "5min": "5m",
        }

        if start_date and end_date:
            df = ticker.history(start=start_date, end=end_date, interval=period_map.get(period, "1d"))
        else:
            df = ticker.history(period=period if period in ["1d", "5d", "1wk", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"] else "1y")

        adjust_ratio = 1.0
        if adjust == "hfq":
            splits = ticker.splits
            if not splits.empty:
                cumulative = 1.0
                for idx in splits.index:
                    if idx >= df.index[0]:
                        cumulative *= splits.loc[idx].item()
                adjust_ratio = cumulative

        return [
            KlineData(
                symbol=symbol,
                timestamp=idx.to_pydatetime(),
                open=row["Open"] * adjust_ratio,
                high=row["High"] * adjust_ratio,
                low=row["Low"] * adjust_ratio,
                close=row["Close"] * adjust_ratio,
                volume=float(row["Volume"]),
                amount=float(row["Close"] * row["Volume"]) if "Volume" in row else 0,
            )
            for idx, row in df.iterrows()
        ]

    def get_stock_info(self, symbol: str) -> StockInfo:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        market = self._parse_market(symbol)
        return StockInfo(
            symbol=symbol,
            name=info.get("longName", info.get("shortName", symbol)),
            market=market,
            sector=info.get("sector"),
            industry=info.get("industry"),
            market_cap=info.get("marketCap"),
            pe_ratio=info.get("trailingPE"),
            pb_ratio=info.get("priceToBook"),
            dividend_yield=info.get("dividendYield"),
        )

    def search_stocks(self, keyword: str) -> list[StockInfo]:
        try:
            tickers = yf.search(keyword, max_results=10)
            return [
                StockInfo(
                    symbol=t["symbol"],
                    name=t.get("longName", t.get("shortName", t["symbol"])),
                    market=MarketType.US_STOCK,
                )
                for t in tickers["quotes"] if t.get("quoteType") == "EQUITY"
            ]
        except Exception:
            return []

    def get_index_components(self, index_code: str) -> list[str]:
        return []

    def get_us_stock_sectors(self) -> dict:
        try:
            tickers = yf.SectorTickers()
            return dict(tickers.sector_tickers)
        except Exception:
            return {}

    def get_market_overview(self) -> dict:
        try:
            indices = {
                "^GSPC": "S&P 500",
                "^DJI": "Dow Jones",
                "^IXIC": "NASDAQ",
            }
            overview = {}
            for symbol, name in indices.items():
                ticker = yf.Ticker(symbol)
                info = ticker.fast_info
                price = info.last_price or 0
                prev_close = info.previous_close or price
                change_pct = ((price - prev_close) / prev_close * 100) if prev_close else 0
                overview[symbol] = {
                    "name": name,
                    "price": price,
                    "change_pct": change_pct,
                }
            return overview
        except Exception:
            return {}
