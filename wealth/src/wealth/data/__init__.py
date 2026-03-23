"""Data sources for Wealth platform."""

from wealth.data.base import DataSource, MarketType, StockInfo, FundInfo, KlineData
from wealth.data.akshare_source import AKShareSource
from wealth.data.yfinance_source import YFinanceSource
from wealth.data.fund_source import FundSource
from wealth.data.eastmoney_crawler import EastMoneyCrawler

__all__ = [
    "DataSource",
    "MarketType",
    "StockInfo",
    "FundInfo",
    "KlineData",
    "AKShareSource",
    "YFinanceSource",
    "FundSource",
    "EastMoneyCrawler",
]
