"""Portfolio management module."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict
import pandas as pd
import numpy as np

from wealth.engine.backtest import Trade


@dataclass
class Position:
    symbol: str
    name: str
    quantity: int
    avg_cost: float
    current_price: float
    market_value: float
    unrealized_pnl: float
    unrealized_pnl_pct: float
    weight: float
    entry_date: datetime
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Portfolio:
    name: str
    initial_value: float
    cash: float
    positions: List[Position] = field(default_factory=list)
    total_value: float = 0
    total_pnl: float = 0
    total_pnl_pct: float = 0
    updated_at: datetime = field(default_factory=datetime.now)

    def update_market_value(self, current_prices: Dict[str, float]):
        self.total_value = self.cash
        for pos in self.positions:
            if pos.symbol in current_prices:
                pos.current_price = current_prices[pos.symbol]
            pos.market_value = pos.quantity * pos.current_price
            pos.unrealized_pnl = (pos.current_price - pos.avg_cost) * pos.quantity
            pos.unrealized_pnl_pct = (pos.current_price - pos.avg_cost) / pos.avg_cost * 100
            self.total_value += pos.market_value

        for pos in self.positions:
            pos.weight = pos.market_value / self.total_value * 100 if self.total_value > 0 else 0

        self.total_pnl = self.total_value - self.initial_value
        self.total_pnl_pct = (self.total_value - self.initial_value) / self.initial_value * 100
        self.updated_at = datetime.now()

    def add_position(
        self,
        symbol: str,
        name: str,
        quantity: int,
        price: float,
        date: Optional[datetime] = None,
    ):
        existing = self.get_position(symbol)
        if existing:
            total_quantity = existing.quantity + quantity
            existing.avg_cost = (existing.avg_cost * existing.quantity + price * quantity) / total_quantity
            existing.quantity = total_quantity
            existing.entry_date = date or existing.entry_date
        else:
            position = Position(
                symbol=symbol,
                name=name,
                quantity=quantity,
                avg_cost=price,
                current_price=price,
                market_value=quantity * price,
                unrealized_pnl=0,
                unrealized_pnl_pct=0,
                weight=0,
                entry_date=date or datetime.now(),
            )
            self.positions.append(position)

        self.cash -= price * quantity

    def remove_position(self, symbol: str, quantity: int, price: float) -> float:
        position = self.get_position(symbol)
        if not position:
            return 0

        if quantity >= position.quantity:
            self.cash += position.quantity * price
            pnl = (price - position.avg_cost) * position.quantity
            self.positions.remove(position)
            return pnl
        else:
            self.cash += quantity * price
            position.quantity -= quantity
            return (price - position.avg_cost) * quantity

    def get_position(self, symbol: str) -> Optional[Position]:
        for pos in self.positions:
            if pos.symbol == symbol:
                return pos
        return None

    def get_summary(self) -> dict:
        return {
            "name": self.name,
            "initial_value": self.initial_value,
            "total_value": self.total_value,
            "cash": self.cash,
            "total_pnl": self.total_pnl,
            "total_pnl_pct": self.total_pnl_pct,
            "position_count": len(self.positions),
            "updated_at": self.updated_at.isoformat(),
        }


class PortfolioOptimizer:
    @staticmethod
    def calculate_returns(price_data: pd.DataFrame) -> pd.DataFrame:
        return price_data.pct_change().dropna()

    @staticmethod
    def calculate_cumulative_returns(returns: pd.DataFrame) -> pd.DataFrame:
        return (1 + returns).cumprod() - 1

    @staticmethod
    def calculate_volatility(returns: pd.DataFrame, window: int = 20) -> pd.DataFrame:
        return returns.rolling(window=window).std() * np.sqrt(252)

    @staticmethod
    def calculate_sharpe_ratio(
        returns: pd.DataFrame,
        risk_free_rate: float = 0.03,
    ) -> pd.Series:
        mean_returns = returns.mean() * 252
        volatility = returns.std() * np.sqrt(252)
        return (mean_returns - risk_free_rate) / volatility

    @staticmethod
    def calculate_max_drawdown(cumulative_returns: pd.DataFrame) -> pd.Series:
        rolling_max = cumulative_returns.cummax()
        drawdown = cumulative_returns - rolling_max
        return drawdown.min()

    @staticmethod
    def risk_parity_weights(covariance: pd.DataFrame) -> pd.Series:
        inv_vol = 1 / np.sqrt(np.diag(covariance))
        weights = inv_vol / inv_vol.sum()
        return pd.Series(weights, index=covariance.index)

    @staticmethod
    def mean_variance_optimization(
        returns: pd.DataFrame,
        risk_aversion: float = 1.0,
    ) -> pd.Series:
        mean_returns = returns.mean() * 252
        cov_matrix = returns.cov() * 252

        n_assets = len(mean_returns)
        ones = np.ones(n_assets)

        try:
            inv_cov = np.linalg.inv(cov_matrix.values)
            numerator = inv_cov @ ones
            denominator = ones @ inv_cov @ ones
            min_var_weights = numerator / denominator

            target_return = mean_returns.max() * 0.5
            delta = (mean_returns.values @ min_var_weights - target_return) / (ones @ inv_cov @ mean_returns.values)
            weights = min_var_weights - delta * (inv_cov @ mean_returns)

            return pd.Series(weights, index=mean_returns.index)
        except np.linalg.LinAlgError:
            return pd.Series(1/n_assets, index=mean_returns.index)

    @staticmethod
    def calculate_portfolio_metrics(
        weights: pd.Series,
        returns: pd.DataFrame,
        risk_free_rate: float = 0.03,
    ) -> dict:
        portfolio_returns = (returns * weights).sum(axis=1)
        cumulative_returns = (1 + portfolio_returns).cumprod() - 1

        total_return = cumulative_returns.iloc[-1] if len(cumulative_returns) > 0 else 0
        volatility = portfolio_returns.std() * np.sqrt(252)
        sharpe = (portfolio_returns.mean() * 252 - risk_free_rate) / volatility if volatility > 0 else 0
        max_dd = PortfolioOptimizer.calculate_max_drawdown(cumulative_returns)

        return {
            "total_return": total_return * 100,
            "annualized_return": portfolio_returns.mean() * 252 * 100,
            "volatility": volatility * 100,
            "sharpe_ratio": sharpe,
            "max_drawdown": max_dd * 100,
        }

    @staticmethod
    def performance_attribution(
        trades: List[Trade],
        positions: List[Position],
    ) -> pd.DataFrame:
        if not trades:
            return pd.DataFrame()

        trade_records = []
        for trade in trades:
            trade_records.append({
                "symbol": trade.symbol,
                "entry_date": trade.entry_date,
                "exit_date": trade.exit_date,
                "pnl": trade.pnl,
                "pnl_pct": trade.pnl_pct,
                "holding_days": trade.holding_days,
                "strategy": trade.strategy,
            })

        df = pd.DataFrame(trade_records)
        if df.empty:
            return df

        summary = df.groupby("symbol").agg({
            "pnl": "sum",
            "pnl_pct": "mean",
            "holding_days": "mean",
            "strategy": "first",
        }).round(2)

        return summary.sort_values("pnl", ascending=False)
