"""Fund data source implementation."""

from datetime import datetime
from typing import Optional
import pandas as pd
import akshare as ak
from wealth.data.base import FundInfo, KlineData, RealtimeQuote, MarketType


class FundSource:
    def __init__(self):
        self._cache = {}

    def get_realtime_quote(self, symbol: str) -> RealtimeQuote:
        try:
            df = ak.fund_open_fund_info_em(symbol=symbol, indicator="单位净值走势")
            latest = df.iloc[-1]
            return RealtimeQuote(
                symbol=symbol,
                name=self.get_fund_info(symbol).name,
                current_price=float(latest["单位净值"]),
                change=float(latest.get("日增长率", 0)),
                change_pct=float(latest.get("日增长率", 0)),
                open=0,
                high=0,
                low=0,
                volume=0,
                amount=0,
                timestamp=pd.to_datetime(latest["净值日期"]).to_pydatetime(),
            )
        except Exception:
            return RealtimeQuote(
                symbol=symbol,
                name="",
                current_price=0,
                change=0,
                change_pct=0,
                open=0,
                high=0,
                low=0,
                volume=0,
                amount=0,
                timestamp=datetime.now(),
            )

    def get_fund_info(self, symbol: str) -> FundInfo:
        try:
            df = ak.fund_individual_basic_info_xq(symbol=symbol)
            info_dict = dict(zip(df["item"], df["value"]))
            return FundInfo(
                symbol=symbol,
                name=info_dict.get("基金名称", ""),
                fund_type=info_dict.get("基金类型", ""),
                nav=float(info_dict.get("单位净值", 0)),
                manager=info_dict.get("基金经理"),
                company=info_dict.get("基金公司"),
                min_purchase=float(info_dict.get("最小申购金额", 0)),
            )
        except Exception:
            return FundInfo(symbol=symbol, name="", fund_type="")

    def get_kline_data(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        period: str = "daily",
    ) -> list[KlineData]:
        try:
            if period == "daily":
                df = ak.fund_open_fund_info_em(symbol=symbol, indicator="单位净值走势")
            else:
                df = ak.fund_open_fund_info_em(symbol=symbol, indicator="累计净值走势")

            if start_date:
                df = df[df["净值日期"] >= start_date]
            if end_date:
                df = df[df["净值日期"] <= end_date]

            return [
                KlineData(
                    symbol=symbol,
                    timestamp=pd.to_datetime(row["净值日期"]).to_pydatetime(),
                    open=float(row["单位净值"]) if pd.notna(row["单位净值"]) else 0,
                    high=float(row["单位净值"]) if pd.notna(row["单位净值"]) else 0,
                    low=float(row["单位净值"]) if pd.notna(row["单位净值"]) else 0,
                    close=float(row["单位净值"]) if pd.notna(row["单位净值"]) else 0,
                    volume=0,
                    amount=0,
                )
                for _, row in df.iterrows()
            ]
        except Exception:
            return []

    def get_fund_NAV_history(self, symbol: str) -> pd.DataFrame:
        try:
            df = ak.fund_open_fund_info_em(symbol=symbol, indicator="累计净值走势")
            return df
        except Exception:
            return pd.DataFrame()

    def search_funds(self, keyword: str) -> list[FundInfo]:
        try:
            df = ak.fund_basic_and_similar()
            filtered = df[df["name"].str.contains(keyword, na=False)]
            return [
                FundInfo(
                    symbol=str(row["symbol"]),
                    name=row["name"],
                    fund_type=row.get("type", ""),
                )
                for _, row in filtered.head(20).iterrows()
            ]
        except Exception:
            return []

    def get_hot_funds(self) -> list[FundInfo]:
        try:
            df = ak.fund_hot_rank_em()
            return [
                FundInfo(
                    symbol=str(row["基金代码"]),
                    name=row["基金简称"],
                    fund_type=row.get("基金类型", ""),
                )
                for _, row in df.head(10).iterrows()
            ]
        except Exception:
            return []

    def get_fund_manager(self, manager_name: str) -> dict:
        try:
            df = ak.fund_manager_em()
            filtered = df[df["基金经理"].str.contains(manager_name, na=False)]
            if not filtered.empty:
                row = filtered.iloc[0]
                return {
                    "name": row["基金经理"],
                    "company": row["基金公司"],
                    "funds": row["代表基金"],
                }
            return {}
        except Exception:
            return {}

    def get_fund_industry_allocation(self, symbol: str) -> dict:
        try:
            df = ak.fund_individual_stock_position_xq(symbol=symbol)
            return {
                "stocks": [
                    {"symbol": row["股票代码"], "name": row["股票名称"], "percent": row["占净值比例"]}
                    for _, row in df.head(10).iterrows()
                ]
            }
        except Exception:
            return {}

    def get_fund_bond_allocation(self, symbol: str) -> dict:
        try:
            df = ak.fund_individual_bond_position_xq(symbol=symbol)
            return {
                "bonds": [
                    {"name": row["债券名称"], "percent": row["占净值比例"]}
                    for _, row in df.head(10).iterrows()
                ]
            }
        except Exception:
            return {}
