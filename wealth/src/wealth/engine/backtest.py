"""Backtesting engine for strategy validation."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
import pandas as pd
import numpy as np
from loguru import logger

from wealth.engine.strategies import Strategy, TradingSignal, SignalType


@dataclass
class Position:
    symbol: str
    entry_price: float
    entry_date: datetime
    quantity: int
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None


@dataclass
class Trade:
    trade_id: int
    symbol: str
    entry_date: datetime
    exit_date: Optional[datetime]
    entry_price: float
    exit_price: Optional[float]
    quantity: int
    pnl: float
    pnl_pct: float
    holding_days: int
    strategy: str


@dataclass
class PortfolioStats:
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


@dataclass
class BacktestResult:
    strategy_name: str
    symbol: str
    start_date: datetime
    end_date: datetime
    initial_capital: float
    final_value: float
    portfolio_stats: PortfolioStats
    trades: List[Trade]
    equity_curve: pd.DataFrame
    drawdown_curve: pd.DataFrame
    monthly_returns: pd.DataFrame


class BacktestEngine:
    def __init__(
        self,
        initial_capital: float = 100000.0,
        commission_rate: float = 0.0003,
        slippage: float = 0.0,
        position_size: float = 1.0,
    ):
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.slippage = slippage
        self.position_size = position_size

    def run(
        self,
        strategy: Strategy,
        data: pd.DataFrame,
        symbol: str = "",
        stop_loss_pct: Optional[float] = None,
        take_profit_pct: Optional[float] = None,
    ) -> BacktestResult:
        if data.empty:
            raise ValueError("Data cannot be empty")

        data = strategy.prepare_data(data)
        data = data.copy()
        data.index = pd.to_datetime(data.index)

        signals = strategy.generate_signals(data, symbol)
        logger.info(f"Generated {len(signals)} signals for {symbol}")

        cash = self.initial_capital
        position: Optional[Position] = None
        trades: List[Trade] = []
        equity_curve = []
        trade_id = 0

        for i, row in data.iterrows():
            current_price = row["close"]
            current_date = row.name if isinstance(row.name, datetime) else datetime.now()

            if position is not None:
                if stop_loss_pct and current_price <= position.entry_price * (1 - stop_loss_pct):
                    exit_price = position.entry_price * (1 - stop_loss_pct)
                    self._close_position(position, exit_price, current_date, trade_id, strategy.name, trades)
                    trade_id += 1
                    position = None
                    cash = trades[-1].exit_price * trades[-1].quantity * (1 - self.commission_rate)
                elif take_profit_pct and current_price >= position.entry_price * (1 + take_profit_pct):
                    exit_price = position.entry_price * (1 + take_profit_pct)
                    self._close_position(position, exit_price, current_date, trade_id, strategy.name, trades)
                    trade_id += 1
                    position = None
                    cash = trades[-1].exit_price * trades[-1].quantity * (1 - self.commission_rate)

            signal = self._get_signal_at_date(signals, current_date)
            if signal:
                if signal.signal == SignalType.BUY and position is None:
                    buy_price = signal.price * (1 + self.slippage)
                    quantity = int(cash * self.position_size / buy_price / 100) * 100
                    if quantity > 0:
                        commission = buy_price * quantity * self.commission_rate
                        cash -= buy_price * quantity + commission
                        position = Position(
                            symbol=symbol,
                            entry_price=buy_price,
                            entry_date=current_date,
                            quantity=quantity,
                            stop_loss=buy_price * (1 - stop_loss_pct) if stop_loss_pct else None,
                            take_profit=buy_price * (1 + take_profit_pct) if take_profit_pct else None,
                        )
                elif signal.signal == SignalType.SELL and position is not None:
                    sell_price = signal.price * (1 - self.slippage)
                    self._close_position(position, sell_price, current_date, trade_id, strategy.name, trades)
                    trade_id += 1
                    position = None
                    cash = trades[-1].exit_price * trades[-1].quantity * (1 - self.commission_rate)

            portfolio_value = cash
            if position:
                portfolio_value += position.quantity * current_price

            equity_curve.append({
                "date": current_date,
                "value": portfolio_value,
                "cash": cash,
                "position_value": portfolio_value - cash if position else 0,
            })

        if position is not None:
            last_price = data.iloc[-1]["close"]
            self._close_position(position, last_price, data.index[-1], trade_id, strategy.name, trades)

        equity_df = pd.DataFrame(equity_curve)
        equity_df.set_index("date", inplace=True)

        final_value = equity_df.iloc[-1]["value"] if len(equity_df) > 0 else self.initial_capital
        portfolio_stats = self._calculate_stats(equity_df, trades)
        drawdown_df = self._calculate_drawdown(equity_df)
        monthly_df = self._calculate_monthly_returns(equity_df)

        return BacktestResult(
            strategy_name=strategy.name,
            symbol=symbol,
            start_date=data.index[0],
            end_date=data.index[-1],
            initial_capital=self.initial_capital,
            final_value=final_value,
            portfolio_stats=portfolio_stats,
            trades=trades,
            equity_curve=equity_df,
            drawdown_curve=drawdown_df,
            monthly_returns=monthly_df,
        )

    def _get_signal_at_date(
        self,
        signals: List[TradingSignal],
        date: datetime,
    ) -> Optional[TradingSignal]:
        for signal in signals:
            if abs((signal.timestamp - date).total_seconds()) < 86400:
                return signal
        return None

    def _close_position(
        self,
        position: Position,
        exit_price: float,
        exit_date: datetime,
        trade_id: int,
        strategy_name: str,
        trades: List[Trade],
    ):
        pnl = (exit_price - position.entry_price) * position.quantity
        pnl_pct = (exit_price - position.entry_price) / position.entry_price * 100
        holding_days = (exit_date - position.entry_date).days

        trades.append(Trade(
            trade_id=trade_id,
            symbol=position.symbol,
            entry_date=position.entry_date,
            exit_date=exit_date,
            entry_price=position.entry_price,
            exit_price=exit_price,
            quantity=position.quantity,
            pnl=pnl,
            pnl_pct=pnl_pct,
            holding_days=holding_days,
            strategy=strategy_name,
        ))

    def _calculate_stats(self, equity_df: pd.DataFrame, trades: List[Trade]) -> PortfolioStats:
        if equity_df.empty:
            return PortfolioStats(
                total_return=0, annualized_return=0, volatility=0,
                sharpe_ratio=0, max_drawdown=0, max_drawdown_duration=0,
                win_rate=0, profit_loss_ratio=0, total_trades=0,
                winning_trades=0, losing_trades=0, avg_holding_days=0,
            )

        total_return = (equity_df.iloc[-1]["value"] - self.initial_capital) / self.initial_capital * 100

        days = (equity_df.index[-1] - equity_df.index[0]).days
        years = days / 365 if days > 0 else 1
        annualized_return = ((1 + total_return / 100) ** (1 / years) - 1) * 100 if years > 0 else 0

        returns = equity_df["value"].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252) * 100 if len(returns) > 0 else 0

        risk_free_rate = 3.0
        sharpe_ratio = (annualized_return - risk_free_rate) / volatility if volatility > 0 else 0

        drawdown = self._calculate_drawdown(equity_df)
        max_drawdown = drawdown["drawdown"].max() if not drawdown.empty else 0

        drawdown_periods = drawdown[drawdown["drawdown"] > 0]
        max_drawdown_duration = 0
        if not drawdown_periods.empty:
            current_duration = 0
            for i in range(1, len(drawdown_periods)):
                if (drawdown_periods.index[i] - drawdown_periods.index[i-1]).days == 1:
                    current_duration += 1
                    max_drawdown_duration = max(max_drawdown_duration, current_duration)
                else:
                    current_duration = 0

        winning_trades = [t for t in trades if t.pnl > 0]
        losing_trades = [t for t in trades if t.pnl <= 0]

        win_rate = len(winning_trades) / len(trades) * 100 if trades else 0

        avg_win = np.mean([t.pnl for t in winning_trades]) if winning_trades else 0
        avg_loss = abs(np.mean([t.pnl for t in losing_trades])) if losing_trades else 1
        profit_loss_ratio = avg_win / avg_loss if avg_loss > 0 else 0

        total_trades = len(trades)
        avg_holding_days = np.mean([t.holding_days for t in trades]) if trades else 0

        return PortfolioStats(
            total_return=total_return,
            annualized_return=annualized_return,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            max_drawdown_duration=max_drawdown_duration,
            win_rate=win_rate,
            profit_loss_ratio=profit_loss_ratio,
            total_trades=total_trades,
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            avg_holding_days=avg_holding_days,
        )

    def _calculate_drawdown(self, equity_df: pd.DataFrame) -> pd.DataFrame:
        if equity_df.empty:
            return pd.DataFrame()

        cumulative_max = equity_df["value"].cummax()
        drawdown = (equity_df["value"] - cumulative_max) / cumulative_max * 100

        return pd.DataFrame({
            "value": equity_df["value"],
            "cummax": cumulative_max,
            "drawdown": drawdown,
        })

    def _calculate_monthly_returns(self, equity_df: pd.DataFrame) -> pd.DataFrame:
        if equity_df.empty or len(equity_df) < 2:
            return pd.DataFrame()

        monthly = equity_df["value"].resample("M").last()
        monthly_returns = monthly.pct_change() * 100

        return pd.DataFrame({
            "month": monthly.index,
            "value": monthly.values,
            "return": monthly_returns.values,
        })

    def compare_strategies(
        self,
        strategies: List[Strategy],
        data: pd.DataFrame,
        symbol: str = "",
    ) -> Dict[str, BacktestResult]:
        results = {}
        for strategy in strategies:
            logger.info(f"Running backtest for {strategy.name}")
            try:
                result = self.run(strategy, data, symbol)
                results[strategy.name] = result
            except Exception as e:
                logger.error(f"Failed to run backtest for {strategy.name}: {e}")
                results[strategy.name] = None
        return results
