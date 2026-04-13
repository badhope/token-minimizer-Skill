"""EastMoney web crawler for real-time stock data."""

from datetime import datetime
from typing import Optional
import httpx
import pandas as pd
from wealth.data.base import RealtimeQuote, MarketType


class EastMoneyCrawler:
    BASE_URL = "https://push2.eastmoney.com"

    def __init__(self):
        self._client = httpx.Client(timeout=30.0)

    def _get_realtime_data(self, symbols: list[str]) -> pd.DataFrame:
        if not symbols:
            return pd.DataFrame()

        security_ids = ",".join(symbols)
        fields = (
            "f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13,"
            "f14,f15,f16,f17,f18,f20,f21,f22,f23,f24,f25,f26,"
            "f27,f28,f30,f31,f32,f33,f34,f35,f36,f37,f38,f39,f40"
        )

        url = f"{self.BASE_URL}/api/qt/ulist.np/get"
        params = {
            "fltt": 2,
            "invt": 2,
            "fields": fields,
            "secids": security_ids,
        }

        try:
            response = self._client.get(url, params=params)
            data = response.json()

            if data.get("data") and data["data"].get("diff"):
                df = pd.DataFrame(data["data"]["diff"])
                return df
            return pd.DataFrame()
        except Exception:
            return pd.DataFrame()

    def get_realtime_quotes(self, symbols: list[str]) -> list[RealtimeQuote]:
        if isinstance(symbols, str):
            symbols = [symbols]

        market_map = {
            "sh": MarketType.A_STOCK,
            "sz": MarketType.A_STOCK,
            "hk": MarketType.HK_STOCK,
        }

        df = self._get_realtime_data(symbols)
        if df.empty:
            return []

        quotes = []
        for _, row in df.iterrows():
            sec_id = str(row.get("f13", ""))
            market = "sh" if sec_id.startswith("1") or sec_id.startswith("5") else "sz"

            try:
                quote = RealtimeQuote(
                    symbol=str(row.get("f12", "")),
                    name=str(row.get("f14", "")),
                    current_price=float(row.get("f2", 0)) if row.get("f2", 0) != "-" else 0,
                    change=float(row.get("f3", 0)),
                    change_pct=float(row.get("f3", 0)),
                    open=float(row.get("f4", 0)) if row.get("f4", 0) != "-" else 0,
                    high=float(row.get("f15", 0)) if row.get("f15", 0) != "-" else 0,
                    low=float(row.get("f16", 0)) if row.get("f16", 0) != "-" else 0,
                    volume=float(row.get("f5", 0)),
                    amount=float(row.get("f6", 0)),
                    timestamp=datetime.now(),
                )
                quotes.append(quote)
            except (ValueError, TypeError):
                continue

        return quotes

    def get_stock_board(self, board_code: str) -> list[str]:
        url = f"{self.BASE_URL}/api/qt/clist/get"
        params = {
            "fltt": 2,
            "invt": 2,
            "fields": "f12,f14",
            "pn": 1,
            "pz": 1000,
            "fid": "f3",
            "fs": f"b:{board_code}+b:+f+!50",
        }

        try:
            response = self._client.get(url, params=params)
            data = response.json()
            if data.get("data") and data["data"].get("diff"):
                return [str(item["f12"]) for item in data["data"]["diff"]]
            return []
        except Exception:
            return []

    def get_industry_leaderboard(self) -> pd.DataFrame:
        url = f"{self.BASE_URL}/api/qt/clist/get"
        params = {
            "fltt": 2,
            "invt": 2,
            "fields": "f12,f14,f3,f4,f8",
            "pn": 1,
            "pz": 50,
            "fid": "f3",
            "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23",
        }

        try:
            response = self._client.get(url, params=params)
            data = response.json()
            if data.get("data") and data["data"].get("diff"):
                return pd.DataFrame(data["data"]["diff"])
            return pd.DataFrame()
        except Exception:
            return pd.DataFrame()

    def get_limit_up_stocks(self) -> list[RealtimeQuote]:
        url = f"{self.BASE_URL}/api/qt/clist/get"
        params = {
            "fltt": 2,
            "invt": 2,
            "fields": "f12,f14,f3,f4,f8",
            "pn": 1,
            "pz": 100,
            "fid": "f3",
            "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23",
        }

        try:
            response = self._client.get(url, params=params)
            data = response.json()
            if data.get("data") and data["data"].get("diff"):
                df = pd.DataFrame(data["data"]["diff"])
                limit_up = df[df["f3"] >= 9.9]
                symbols = [str(x) for x in limit_up["f12"].tolist()]
                return self.get_realtime_quotes(symbols)
            return []
        except Exception:
            return []

    def get_volume_ratio_stocks(self, min_ratio: float = 5.0) -> pd.DataFrame:
        url = f"{self.BASE_URL}/api/qt/clist/get"
        params = {
            "fltt": 2,
            "invt": 2,
            "fields": "f12,f14,f3,f8,f10,f15,f16",
            "pn": 1,
            "pz": 100,
            "fid": "f10",
            "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23",
        }

        try:
            response = self._client.get(url, params=params)
            data = response.json()
            if data.get("data") and data["data"].get("diff"):
                df = pd.DataFrame(data["data"]["diff"])
                df.columns = ["symbol", "name", "change_pct", "volume_ratio", "turnover", "high", "low"]
                return df[df["volume_ratio"] >= min_ratio]
            return pd.DataFrame()
        except Exception:
            return pd.DataFrame()

    def close(self):
        self._client.close()
