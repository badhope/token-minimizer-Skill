"""AKShare data source implementation."""

from datetime import datetime
from typing import Optional
import pandas as pd
import akshare as ak
from wealth.data.base import (
    DataSource,
    MarketType,
    StockInfo,
    FundInfo,
    KlineData,
    RealtimeQuote,
)


class AKShareSource(DataSource):
    def __init__(self):
        self._cache = {}
        self._cache_ttl = 60

    def get_realtime_quote(self, symbol: str) -> RealtimeQuote:
        try:
            df = ak.stock_zh_a_spot_em()
            row = df[df["代码"] == symbol].iloc[0]
            return RealtimeQuote(
                symbol=symbol,
                name=row["名称"],
                current_price=float(row["最新价"]),
                change=float(row["涨跌额"]),
                change_pct=float(row["涨跌幅"]),
                open=float(row["开盘"]),
                high=float(row["最高"]),
                low=float(row["最低"]),
                volume=float(row["成交量"]),
                amount=float(row["成交额"]),
                timestamp=datetime.now(),
            )
        except Exception as e:
            raise RuntimeError(f"Failed to get realtime quote for {symbol}: {e}")

    def get_kline_data(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        period: str = "daily",
        adjust: str = "qfq",
    ) -> list[KlineData]:
        period_map = {
            "daily": "daily",
            "weekly": "weekly",
            "monthly": "monthly",
            "60min": "60min",
            "30min": "30min",
            "15min": "15min",
            "5min": "5min",
        }
        adjust_map = {"qfq": "qfq", "hfq": "hfq", "none": "None"}

        try:
            df = ak.stock_zh_a_hist(
                symbol=symbol,
                period=period_map.get(period, "daily"),
                start_date=start_date,
                end_date=end_date,
                adjust=adjust_map.get(adjust, "qfq"),
            )
            df.columns = [
                "date", "open", "close", "high", "low", "volume", "amount", "turnover"
            ]
            return [
                KlineData(
                    symbol=symbol,
                    timestamp=pd.to_datetime(row["date"]).to_pydatetime(),
                    open=float(row["open"]),
                    high=float(row["high"]),
                    low=float(row["low"]),
                    close=float(row["close"]),
                    volume=float(row["volume"]),
                    amount=float(row["amount"]) if pd.notna(row["amount"]) else None,
                    turnover_rate=float(row["turnover"]) if pd.notna(row["turnover"]) else None,
                )
                for _, row in df.iterrows()
            ]
        except Exception as e:
            raise RuntimeError(f"Failed to get kline data for {symbol}: {e}")

    def get_stock_info(self, symbol: str) -> StockInfo:
        try:
            df = ak.stock_individual_info_em(symbol=symbol)
            info_dict = dict(zip(df["item"], df["value"]))
            return StockInfo(
                symbol=symbol,
                name=info_dict.get("股票简称", ""),
                market=MarketType.A_STOCK,
                sector=info_dict.get("行业"),
                industry=info_dict.get("细分行业"),
            )
        except Exception:
            return StockInfo(symbol=symbol, name="", market=MarketType.A_STOCK)

    def search_stocks(self, keyword: str) -> list[StockInfo]:
        try:
            df = ak.stock_zh_a_spot_em()
            filtered = df[df["名称"].str.contains(keyword, na=False)]
            return [
                StockInfo(
                    symbol=row["代码"],
                    name=row["名称"],
                    market=MarketType.A_STOCK,
                )
                for _, row in filtered.head(20).iterrows()
            ]
        except Exception as e:
            raise RuntimeError(f"Failed to search stocks: {e}")

    def get_index_components(self, index_code: str) -> list[str]:
        index_map = {
            "000001": "sh000001",
            "399001": "sz399001",
            "399006": "sz399006",
        }
        code = index_map.get(index_code, index_code)

        try:
            if code.startswith("sh") or code.startswith("sz"):
                df = ak.index_zh_a_hist_min_em(symbol=code, period="daily")
            else:
                df = ak.index_zh_a_hist_min_em(symbol=code, period="daily")
            return df["代码"].tolist()[:100]
        except Exception:
            return []

    def get_market_turnover(self) -> dict:
        try:
            df = ak.stock_market_day_em()
            latest = df.iloc[-1]
            return {
                "date": latest["日期"],
                "volume": float(latest["成交额"]),
                "上涨": int(latest["上涨"]),
                "下跌": int(latest["下跌"]),
                "平盘": int(latest["平盘"]),
            }
        except Exception:
            return {}

    def get_stock_financial_analysis(self, symbol: str) -> dict:
        try:
            df = ak.stock_financial_analysis_indicator(symbol=symbol)
            latest = df.iloc[0]
            return {
                "roe": float(latest.get("净资产收益率(%)", 0)),
                "gross_margin": float(latest.get("销售毛利率(%)", 0)),
                "net_margin": float(latest.get("销售净利率(%)", 0)),
                "debt_ratio": float(latest.get("资产负债率(%)", 0)),
            }
        except Exception:
            return {}
