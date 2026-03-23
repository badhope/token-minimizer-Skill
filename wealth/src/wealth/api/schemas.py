"""Pydantic schemas for API."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class StockSearchRequest(BaseModel):
    keyword: str
    market: Optional[str] = None


class StockSearchResponse(BaseModel):
    symbol: str
    name: str
    market: str
    sector: Optional[str] = None


class KlineRequest(BaseModel):
    symbol: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    period: str = "daily"
    adjust: str = "qfq"


class KlineResponse(BaseModel):
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    amount: Optional[float] = None


class RealtimeQuoteResponse(BaseModel):
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
    timestamp: str


class StrategyBacktestRequest(BaseModel):
    symbol: str
    strategy: str
    start_date: str
    end_date: str
    initial_capital: float = 100000.0
    commission_rate: float = 0.0003
    stop_loss_pct: Optional[float] = None
    take_profit_pct: Optional[float] = None


class StrategyParameter(BaseModel):
    name: str
    value: Any
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    step: Optional[float] = None


class StrategyConfig(BaseModel):
    strategy_name: str
    parameters: List[StrategyParameter] = []


class BacktestResponse(BaseModel):
    strategy_name: str
    symbol: str
    start_date: str
    end_date: str
    initial_capital: float
    final_value: float
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    max_drawdown_duration: int
    win_rate: float
    profit_loss_ratio: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_holding_days: float


class TradeResponse(BaseModel):
    trade_id: int
    symbol: str
    entry_date: str
    exit_date: Optional[str]
    entry_price: float
    exit_price: Optional[float]
    quantity: int
    pnl: float
    pnl_pct: float
    holding_days: int
    strategy: str


class EquityCurvePoint(BaseModel):
    date: str
    value: float
    cash: float
    position_value: float


class StrategyCompareRequest(BaseModel):
    symbol: str
    strategies: List[str]
    start_date: str
    end_date: str
    initial_capital: float = 100000.0


class StrategyCompareResponse(BaseModel):
    results: Dict[str, BacktestResponse]


class AlertCreateRequest(BaseModel):
    symbol: str
    alert_type: str
    condition: str
    threshold_value: float
    level: str = "WARNING"


class AlertResponse(BaseModel):
    alert_id: str
    symbol: str
    alert_type: str
    level: str
    condition: str
    current_value: float
    message: str
    created_at: str
    triggered_at: Optional[str] = None
    is_active: bool


class AlertListResponse(BaseModel):
    alerts: List[AlertResponse]


class PortfolioPosition(BaseModel):
    symbol: str
    name: str
    quantity: int
    avg_cost: float
    current_price: float
    market_value: float
    unrealized_pnl: float
    unrealized_pnl_pct: float
    weight: float


class PortfolioResponse(BaseModel):
    name: str
    initial_value: float
    total_value: float
    cash: float
    total_pnl: float
    total_pnl_pct: float
    position_count: int
    positions: List[PortfolioPosition]


class MarketOverviewResponse(BaseModel):
    indices: Dict[str, Dict[str, Any]]
    hot_stocks: List[Dict[str, Any]]
    limit_up_count: int
    limit_down_count: int


class IndicatorResponse(BaseModel):
    name: str
    value: float
    signal: str


class IndicatorsRequest(BaseModel):
    symbol: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    indicators: List[str] = []


class IndicatorsResponse(BaseModel):
    symbol: str
    data: List[Dict[str, Any]]


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str
