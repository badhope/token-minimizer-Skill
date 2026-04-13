"""Base data source interfaces and models."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class MarketType(str, Enum):
    A_STOCK = "A_STOCK"
    HK_STOCK = "HK_STOCK"
    US_STOCK = "US_STOCK"
    FUND = "FUND"
    FUTURES = "FUTURES"
    OPTIONS = "OPTIONS"
    CRYPTO = "CRYPTO"


@dataclass
class StockInfo:
    symbol: str
    name: str
    market: MarketType
    exchange: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class FundInfo:
    symbol: str
    name: str
    fund_type: str
    nav: Optional[float] = None
    nav_date: Optional[datetime] = None
    manager: Optional[str] = None
    company: Optional[str] = None
    min_purchase: Optional[float] = None
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class KlineData:
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    amount: Optional[float] = None
    turnover_rate: Optional[float] = None


@dataclass
class TickData:
    symbol: str
    timestamp: datetime
    last_price: float
    open: float
    high: float
    low: float
    volume: float
    amount: float
    bid1_price: float
    bid1_volume: float
    ask1_price: float
    ask1_volume: float


@dataclass
class RealtimeQuote:
    symbol: str
    name: str
    current_price: float
    change: float
    change_pct: float
    open: float
    high: float
    low: float
    volume: float
    amount: float
    timestamp: datetime


class DataSource(ABC):
    @abstractmethod
    def get_realtime_quote(self, symbol: str) -> RealtimeQuote:
        pass

    @abstractmethod
    def get_kline_data(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        period: str = "daily",
        adjust: str = "qfq",
    ) -> list[KlineData]:
        pass

    @abstractmethod
    def get_stock_info(self, symbol: str) -> StockInfo:
        pass

    @abstractmethod
    def search_stocks(self, keyword: str) -> list[StockInfo]:
        pass

    @abstractmethod
    def get_index_components(self, index_code: str) -> list[str]:
        pass
