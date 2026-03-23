"""Trading strategies module."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, List
import pandas as pd
import numpy as np

from wealth.engine.indicators import TechnicalIndicators


class SignalType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass
class TradingSignal:
    timestamp: datetime
    symbol: str
    signal: SignalType
    price: float
    strength: float
    strategy: str
    metadata: dict


class Strategy(ABC):
    def __init__(self, name: str):
        self.name = name
        self.indicators = TechnicalIndicators()

    @abstractmethod
    def generate_signals(self, df: pd.DataFrame, symbol: str = "") -> List[TradingSignal]:
        pass

    def prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        if "Close" in df.columns and "close" not in df.columns:
            df["close"] = df["Close"]
        if "Open" in df.columns and "open" not in df.columns:
            df["open"] = df["Open"]
        if "High" in df.columns and "high" not in df.columns:
            df["high"] = df["High"]
        if "Low" in df.columns and "low" not in df.columns:
            df["low"] = df["Low"]
        if "Volume" in df.columns and "volume" not in df.columns:
            df["volume"] = df["Volume"]
        return df


class MACDStrategy(Strategy):
    def __init__(
        self,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
        threshold: float = 0.0,
    ):
        super().__init__("MACD")
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
        self.threshold = threshold

    def generate_signals(self, df: pd.DataFrame, symbol: str = "") -> List[TradingSignal]:
        df = self.prepare_data(df)
        close = df["close"]

        dif, dea, macd_bar = self.indicators.macd(close, self.fast_period, self.slow_period, self.signal_period)
        df["dif"] = dif
        df["dea"] = dea
        df["macd_bar"] = macd_bar

        signals = []
        for i in range(1, len(df)):
            if pd.isna(df["dif"].iloc[i]) or pd.isna(df["dea"].iloc[i]):
                continue

            prev_diff = df["dif"].iloc[i - 1] - df["dea"].iloc[i - 1]
            curr_diff = df["dif"].iloc[i] - df["dea"].iloc[i]

            if prev_diff < self.threshold < curr_diff:
                strength = min(abs(curr_diff - prev_diff) * 10, 1.0)
                signals.append(TradingSignal(
                    timestamp=df.index[i] if isinstance(df.index[i], datetime) else datetime.now(),
                    symbol=symbol,
                    signal=SignalType.BUY,
                    price=df["close"].iloc[i],
                    strength=strength,
                    strategy=self.name,
                    metadata={"dif": curr_diff, "dea": df["dea"].iloc[i]},
                ))
            elif prev_diff > self.threshold > curr_diff:
                strength = min(abs(prev_diff - curr_diff) * 10, 1.0)
                signals.append(TradingSignal(
                    timestamp=df.index[i] if isinstance(df.index[i], datetime) else datetime.now(),
                    symbol=symbol,
                    signal=SignalType.SELL,
                    price=df["close"].iloc[i],
                    strength=strength,
                    strategy=self.name,
                    metadata={"dif": curr_diff, "dea": df["dea"].iloc[i]},
                ))

        return signals


class KDJStrategy(Strategy):
    def __init__(
        self,
        period: int = 9,
        k_threshold: float = 80,
        d_threshold: float = 80,
        oversold: float = 20,
    ):
        super().__init__("KDJ")
        self.period = period
        self.k_threshold = k_threshold
        self.d_threshold = d_threshold
        self.oversold = oversold

    def generate_signals(self, df: pd.DataFrame, symbol: str = "") -> List[TradingSignal]:
        df = self.prepare_data(df)
        high = df["high"]
        low = df["low"]
        close = df["close"]

        k, d, j = self.indicators.kdj(high, low, close, self.period)

        signals = []
        for i in range(1, len(df)):
            if pd.isna(k.iloc[i]) or pd.isna(d.iloc[i]):
                continue

            if k.iloc[i-1] < d.iloc[i-1] and k.iloc[i] >= d.iloc[i] and j.iloc[i] < self.k_threshold:
                strength = (k.iloc[i] - k.iloc[i-1]) / 100
                signals.append(TradingSignal(
                    timestamp=df.index[i] if isinstance(df.index[i], datetime) else datetime.now(),
                    symbol=symbol,
                    signal=SignalType.BUY,
                    price=df["close"].iloc[i],
                    strength=min(strength, 1.0),
                    strategy=self.name,
                    metadata={"k": k.iloc[i], "d": d.iloc[i], "j": j.iloc[i]},
                ))
            elif k.iloc[i-1] > d.iloc[i-1] and k.iloc[i] <= d.iloc[i] and j.iloc[i] > self.d_threshold:
                strength = (k.iloc[i-1] - k.iloc[i]) / 100
                signals.append(TradingSignal(
                    timestamp=df.index[i] if isinstance(df.index[i], datetime) else datetime.now(),
                    symbol=symbol,
                    signal=SignalType.SELL,
                    price=df["close"].iloc[i],
                    strength=min(strength, 1.0),
                    strategy=self.name,
                    metadata={"k": k.iloc[i], "d": d.iloc[i], "j": j.iloc[i]},
                ))

        return signals


class BollingerStrategy(Strategy):
    def __init__(
        self,
        period: int = 20,
        std_dev: float = 2.0,
        position_threshold: float = 0.2,
    ):
        super().__init__("BollingerBands")
        self.period = period
        self.std_dev = std_dev
        self.position_threshold = position_threshold

    def generate_signals(self, df: pd.DataFrame, symbol: str = "") -> List[TradingSignal]:
        df = self.prepare_data(df)
        close = df["close"]

        upper, middle, lower, bandwidth, percent = self.indicators.bollinger_bands(close, self.period, self.std_dev)

        signals = []
        for i in range(self.period, len(df)):
            if pd.isna(percent.iloc[i]):
                continue

            if percent.iloc[i] < self.position_threshold:
                strength = (self.position_threshold - percent.iloc[i]) / self.position_threshold
                signals.append(TradingSignal(
                    timestamp=df.index[i] if isinstance(df.index[i], datetime) else datetime.now(),
                    symbol=symbol,
                    signal=SignalType.BUY,
                    price=df["close"].iloc[i],
                    strength=min(strength, 1.0),
                    strategy=self.name,
                    metadata={"percent": percent.iloc[i], "bb_lower": lower.iloc[i]},
                ))
            elif percent.iloc[i] > (1 - self.position_threshold):
                strength = (percent.iloc[i] - (1 - self.position_threshold)) / self.position_threshold
                signals.append(TradingSignal(
                    timestamp=df.index[i] if isinstance(df.index[i], datetime) else datetime.now(),
                    symbol=symbol,
                    signal=SignalType.SELL,
                    price=df["close"].iloc[i],
                    strength=min(strength, 1.0),
                    strategy=self.name,
                    metadata={"percent": percent.iloc[i], "bb_upper": upper.iloc[i]},
                ))

        return signals


class MeanReversionStrategy(Strategy):
    def __init__(
        self,
        period: int = 20,
        std_threshold: float = 2.0,
        holding_period: int = 5,
    ):
        super().__init__("MeanReversion")
        self.period = period
        self.std_threshold = std_threshold
        self.holding_period = holding_period
        self._position_entry = None

    def generate_signals(self, df: pd.DataFrame, symbol: str = "") -> List[TradingSignal]:
        df = self.prepare_data(df)
        close = df["close"]

        sma = self.indicators.sma(close, self.period)
        std = close.rolling(window=self.period).std()

        upper_band = sma + (std * self.std_threshold)
        lower_band = sma - (std * self.std_threshold)

        signals = []
        for i in range(self.period, len(df)):
            if pd.isna(sma.iloc[i]) or pd.isna(upper_band.iloc[i]):
                continue

            if close.iloc[i] < lower_band.iloc[i]:
                signals.append(TradingSignal(
                    timestamp=df.index[i] if isinstance(df.index[i], datetime) else datetime.now(),
                    symbol=symbol,
                    signal=SignalType.BUY,
                    price=df["close"].iloc[i],
                    strength=0.8,
                    strategy=self.name,
                    metadata={"sma": sma.iloc[i], "z_score": -self.std_threshold},
                ))
            elif close.iloc[i] > upper_band.iloc[i]:
                signals.append(TradingSignal(
                    timestamp=df.index[i] if isinstance(df.index[i], datetime) else datetime.now(),
                    symbol=symbol,
                    signal=SignalType.SELL,
                    price=df["close"].iloc[i],
                    strength=0.8,
                    strategy=self.name,
                    metadata={"sma": sma.iloc[i], "z_score": self.std_threshold},
                ))

        return signals


class RSIStrategy(Strategy):
    def __init__(
        self,
        period: int = 14,
        overbought: float = 70,
        oversold: float = 30,
    ):
        super().__init__("RSI")
        self.period = period
        self.overbought = overbought
        self.oversold = oversold

    def generate_signals(self, df: pd.DataFrame, symbol: str = "") -> List[TradingSignal]:
        df = self.prepare_data(df)
        close = df["close"]
        rsi = self.indicators.rsi(close, self.period)

        signals = []
        for i in range(1, len(df)):
            if pd.isna(rsi.iloc[i]):
                continue

            if rsi.iloc[i-1] < self.oversold and rsi.iloc[i] >= self.oversold:
                strength = (rsi.iloc[i] - self.oversold) / (100 - self.oversold)
                signals.append(TradingSignal(
                    timestamp=df.index[i] if isinstance(df.index[i], datetime) else datetime.now(),
                    symbol=symbol,
                    signal=SignalType.BUY,
                    price=df["close"].iloc[i],
                    strength=min(strength, 1.0),
                    strategy=self.name,
                    metadata={"rsi": rsi.iloc[i]},
                ))
            elif rsi.iloc[i-1] > self.overbought and rsi.iloc[i] <= self.overbought:
                strength = (self.overbought - rsi.iloc[i]) / self.overbought
                signals.append(TradingSignal(
                    timestamp=df.index[i] if isinstance(df.index[i], datetime) else datetime.now(),
                    symbol=symbol,
                    signal=SignalType.SELL,
                    price=df["close"].iloc[i],
                    strength=min(strength, 1.0),
                    strategy=self.name,
                    metadata={"rsi": rsi.iloc[i]},
                ))

        return signals


class TrendFollowingStrategy(Strategy):
    def __init__(
        self,
        short_period: int = 10,
        long_period: int = 50,
    ):
        super().__init__("TrendFollowing")
        self.short_period = short_period
        self.long_period = long_period

    def generate_signals(self, df: pd.DataFrame, symbol: str = "") -> List[TradingSignal]:
        df = self.prepare_data(df)
        close = df["close"]

        ema_short = self.indicators.ema(close, self.short_period)
        ema_long = self.indicators.ema(close, self.long_period)

        signals = []
        for i in range(1, len(df)):
            if pd.isna(ema_short.iloc[i]) or pd.isna(ema_long.iloc[i]):
                continue

            if ema_short.iloc[i-1] < ema_long.iloc[i-1] and ema_short.iloc[i] > ema_long.iloc[i]:
                slope = (ema_short.iloc[i] - ema_short.iloc[i-1]) / ema_short.iloc[i-1]
                signals.append(TradingSignal(
                    timestamp=df.index[i] if isinstance(df.index[i], datetime) else datetime.now(),
                    symbol=symbol,
                    signal=SignalType.BUY,
                    price=df["close"].iloc[i],
                    strength=min(abs(slope) * 100, 1.0),
                    strategy=self.name,
                    metadata={"ema_short": ema_short.iloc[i], "ema_long": ema_long.iloc[i]},
                ))
            elif ema_short.iloc[i-1] > ema_long.iloc[i-1] and ema_short.iloc[i] < ema_long.iloc[i]:
                slope = (ema_short.iloc[i-1] - ema_short.iloc[i]) / ema_short.iloc[i-1]
                signals.append(TradingSignal(
                    timestamp=df.index[i] if isinstance(df.index[i], datetime) else datetime.now(),
                    symbol=symbol,
                    signal=SignalType.SELL,
                    price=df["close"].iloc[i],
                    strength=min(abs(slope) * 100, 1.0),
                    strategy=self.name,
                    metadata={"ema_short": ema_short.iloc[i], "ema_long": ema_long.iloc[i]},
                ))

        return signals


class SuperTrendStrategy(Strategy):
    def __init__(
        self,
        period: int = 10,
        multiplier: float = 3.0,
    ):
        super().__init__("SuperTrend")
        self.period = period
        self.multiplier = multiplier

    def generate_signals(self, df: pd.DataFrame, symbol: str = "") -> List[TradingSignal]:
        df = self.prepare_data(df)
        high = df["high"]
        low = df["low"]
        close = df["close"]

        supertrend, direction = self.indicators.supertrend(high, low, close, self.period, self.multiplier)

        signals = []
        for i in range(1, len(df)):
            if pd.isna(supertrend.iloc[i]) or pd.isna(direction.iloc[i]):
                continue

            if direction.iloc[i] == 1 and direction.iloc[i-1] == -1:
                signals.append(TradingSignal(
                    timestamp=df.index[i] if isinstance(df.index[i], datetime) else datetime.now(),
                    symbol=symbol,
                    signal=SignalType.BUY,
                    price=df["close"].iloc[i],
                    strength=0.8,
                    strategy=self.name,
                    metadata={"supertrend": supertrend.iloc[i]},
                ))
            elif direction.iloc[i] == -1 and direction.iloc[i-1] == 1:
                signals.append(TradingSignal(
                    timestamp=df.index[i] if isinstance(df.index[i], datetime) else datetime.now(),
                    symbol=symbol,
                    signal=SignalType.SELL,
                    price=df["close"].iloc[i],
                    strength=0.8,
                    strategy=self.name,
                    metadata={"supertrend": supertrend.iloc[i]},
                ))

        return signals


class CompositeStrategy(Strategy):
    def __init__(self, strategies: List[Strategy], weights: Optional[List[float]] = None):
        super().__init__("Composite")
        self.strategies = strategies
        self.weights = weights or [1.0 / len(strategies)] * len(strategies)

    def generate_signals(self, df: pd.DataFrame, symbol: str = "") -> List[TradingSignal]:
        all_signals = []
        for strategy in self.strategies:
            signals = strategy.generate_signals(df, symbol)
            all_signals.extend(signals)

        all_signals.sort(key=lambda x: x.timestamp)
        return all_signals


def get_strategy(strategy_name: str, **kwargs) -> Strategy:
    strategy_map = {
        "macd": MACDStrategy,
        "kdj": KDJStrategy,
        "bollinger": BollingerStrategy,
        "mean_reversion": MeanReversionStrategy,
        "rsi": RSIStrategy,
        "trend_following": TrendFollowingStrategy,
        "supertrend": SuperTrendStrategy,
    }

    strategy_class = strategy_map.get(strategy_name.lower())
    if strategy_class is None:
        raise ValueError(f"Unknown strategy: {strategy_name}")
    return strategy_class(**kwargs)
