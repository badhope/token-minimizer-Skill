"""Technical indicators calculation module."""

import pandas as pd
import numpy as np
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class IndicatorResult:
    name: str
    value: float
    signal: str
    timestamp: pd.Timestamp


class TechnicalIndicators:
    @staticmethod
    def sma(close: pd.Series, period: int) -> pd.Series:
        return close.rolling(window=period).mean()

    @staticmethod
    def ema(close: pd.Series, period: int) -> pd.Series:
        return close.ewm(span=period, adjust=False).mean()

    @staticmethod
    def macd(
        close: pd.Series,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        ema_fast = close.ewm(span=fast_period, adjust=False).mean()
        ema_slow = close.ewm(span=slow_period, adjust=False).mean()
        dif = ema_fast - ema_slow
        dea = dif.ewm(span=signal_period, adjust=False).mean()
        macd_bar = (dif - dea) * 2
        return dif, dea, macd_bar

    @staticmethod
    def kdj(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 9,
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        lowest_low = low.rolling(window=period).min()
        highest_high = high.rolling(window=period).max()
        rsv = (close - lowest_low) / (highest_high - lowest_low) * 100
        rsv = rsv.fillna(50)

        k = rsv.ewm(alpha=1/3, adjust=False).mean()
        d = k.ewm(alpha=1/3, adjust=False).mean()
        j = 3 * k - 2 * d
        return k, d, j

    @staticmethod
    def rsi(close: pd.Series, period: int = 14) -> pd.Series:
        delta = close.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def bollinger_bands(
        close: pd.Series,
        period: int = 20,
        std_dev: float = 2.0,
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        middle = close.rolling(window=period).mean()
        std = close.rolling(window=period).std()
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        bandwidth = (upper - lower) / middle * 100
        percent = (close - lower) / (upper - lower) * 100
        return upper, middle, lower, bandwidth, percent

    @staticmethod
    def keltner_channels(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        ema_period: int = 20,
        atr_period: int = 10,
        multiplier: float = 2.0,
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        middle = close.ewm(span=ema_period, adjust=False).mean()
        tr = pd.concat([
            high - low,
            (high - close.shift()).abs(),
            (low - close.shift()).abs(),
        ], axis=1).max(axis=1)
        atr = tr.rolling(window=atr_period).mean()
        upper = middle + multiplier * atr
        lower = middle - multiplier * atr
        return upper, middle, lower

    @staticmethod
    def donchian_channels(
        high: pd.Series,
        low: pd.Series,
        period: int = 20,
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        upper = high.rolling(window=period).max()
        middle = (upper + low.rolling(window=period).min()) / 2
        lower = low.rolling(window=period).min()
        return upper, middle, lower

    @staticmethod
    def atr(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 14,
    ) -> pd.Series:
        tr = pd.concat([
            high - low,
            (high - close.shift()).abs(),
            (low - close.shift()).abs(),
        ], axis=1).max(axis=1)
        return tr.rolling(window=period).mean()

    @staticmethod
    def adx(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 14,
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        plus_dm = high.diff()
        minus_dm = -low.diff()
        plus_dm = plus_dm.where(plus_dm > minus_dm, 0)
        plus_dm = plus_dm.where(plus_dm > 0, 0)
        minus_dm = minus_dm.where(minus_dm > plus_dm, 0)
        minus_dm = minus_dm.where(minus_dm > 0, 0)

        tr = pd.concat([
            high - low,
            (high - close.shift()).abs(),
            (low - close.shift()).abs(),
        ], axis=1).max(axis=1)

        plus_di = 100 * (plus_dm.ewm(alpha=1/period, adjust=False).mean() / tr.ewm(alpha=1/period, adjust=False).mean())
        minus_di = 100 * (minus_dm.ewm(alpha=1/period, adjust=False).mean() / tr.ewm(alpha=1/period, adjust=False).mean())
        dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
        adx = dx.ewm(alpha=1/period, adjust=False).mean()

        return adx, plus_di, minus_di

    @staticmethod
    def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
        direction = np.sign(close.diff())
        obv = (direction * volume).cumsum()
        return obv

    @staticmethod
    def vwap(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        volume: pd.Series,
    ) -> pd.Series:
        typical_price = (high + low + close) / 3
        return (typical_price * volume).cumsum() / volume.cumsum()

    @staticmethod
    def mfi(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        volume: pd.Series,
        period: int = 14,
    ) -> pd.Series:
        typical_price = (high + low + close) / 3
        money_flow = typical_price * volume

        positive_flow = money_flow.where(typical_price > typical_price.shift(), 0)
        negative_flow = money_flow.where(typical_price < typical_price.shift(), 0)

        positive_mf = positive_flow.rolling(window=period).sum()
        negative_mf = negative_flow.rolling(window=period).sum()

        mfi = 100 - (100 / (1 + positive_mf / negative_mf))
        return mfi

    @staticmethod
    def stoch(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        k_period: int = 14,
        d_period: int = 3,
    ) -> Tuple[pd.Series, pd.Series]:
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        fast_k = (close - lowest_low) / (highest_high - lowest_low) * 100
        slow_k = fast_k.rolling(window=d_period).mean()
        slow_d = slow_k.rolling(window=d_period).mean()
        return slow_k, slow_d

    @staticmethod
    def cci(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 20,
    ) -> pd.Series:
        typical_price = (high + low + close) / 3
        sma = typical_price.rolling(window=period).mean()
        mad = typical_price.rolling(window=period).apply(lambda x: np.abs(x - x.mean()).mean())
        cci = (typical_price - sma) / (0.015 * mad)
        return cci

    @staticmethod
    def williams_r(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 14,
    ) -> pd.Series:
        highest_high = high.rolling(window=period).max()
        lowest_low = low.rolling(window=period).min()
        wr = -100 * (highest_high - close) / (highest_high - lowest_low)
        return wr

    @staticmethod
    def ichimoku(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        tenkan_period: int = 9,
        kijun_period: int = 26,
        senkou_b_period: int = 52,
    ) -> dict:
        tenkan_sen = (high.rolling(window=tenkan_period).max() + low.rolling(window=tenkan_period).min()) / 2
        kijun_sen = (high.rolling(window=kijun_period).max() + low.rolling(window=kijun_period).min()) / 2
        senkou_a = (tenkan_sen + kijun_sen) / 2
        senkou_b = (high.rolling(window=senkou_b_period).max() + low.rolling(window=senkou_b_period).min()) / 2
        chikou_span = close.shift(-26)
        return {
            "tenkan_sen": tenkan_sen,
            "kijun_sen": kijun_sen,
            "senkou_a": senkou_a,
            "senkou_b": senkou_b,
            "chikou_span": chikou_span,
        }

    @staticmethod
    def pivots(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.DataFrame:
        pivot = (high + low + close) / 3
        r1 = 2 * pivot - low
        s1 = 2 * pivot - high
        r2 = pivot + (high - low)
        s2 = pivot - (high - low)
        r3 = high + 2 * (pivot - low)
        s3 = low - 2 * (high - pivot)
        return pd.DataFrame({
            "pivot": pivot,
            "r1": r1, "r2": r2, "r3": r3,
            "s1": s1, "s2": s2, "s3": s3,
        })

    @staticmethod
    def fibonacci_retracement(
        high: pd.Series,
        low: pd.Series,
    ) -> dict:
        diff = high - low
        return {
            "level_0": high,
            "level_236": high - diff * 0.236,
            "level_382": high - diff * 0.382,
            "level_500": high - diff * 0.500,
            "level_618": high - diff * 0.618,
            "level_786": high - diff * 0.786,
            "level_100": low,
        }

    @staticmethod
    def ema_slope(close: pd.Series, period: int = 20) -> pd.Series:
        ema = close.ewm(span=period, adjust=False).mean()
        return ema.pct_change()

    @staticmethod
    def adl(high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series) -> pd.Series:
        mfm = ((close - low) - (high - close)) / (high - low)
        mfm = mfm.fillna(0)
        mfv = mfm * volume
        return mfv.cumsum()

    @staticmethod
    def supertrend(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 10,
        multiplier: float = 3.0,
    ) -> Tuple[pd.Series, pd.Series]:
        atr = TechnicalIndicators.atr(high, low, close, period)
        hl2 = (high + low) / 2
        upper_band = hl2 + multiplier * atr
        lower_band = hl2 - multiplier * atr

        supertrend = pd.Series(index=close.index, dtype=float)
        direction = pd.Series(index=close.index, dtype=int)

        for i in range(len(close)):
            if i == 0:
                supertrend.iloc[i] = lower_band.iloc[i]
                direction.iloc[i] = 1
            else:
                if close.iloc[i] > upper_band.iloc[i-1]:
                    direction.iloc[i] = 1
                    supertrend.iloc[i] = lower_band.iloc[i]
                elif close.iloc[i] < lower_band.iloc[i-1]:
                    direction.iloc[i] = -1
                    supertrend.iloc[i] = upper_band.iloc[i]
                else:
                    direction.iloc[i] = direction.iloc[i-1]
                    if direction.iloc[i] == 1:
                        supertrend.iloc[i] = max(lower_band.iloc[i], supertrend.iloc[i-1])
                    else:
                        supertrend.iloc[i] = min(upper_band.iloc[i], supertrend.iloc[i-1])

        return supertrend, direction

    @classmethod
    def calculate_all(cls, df: pd.DataFrame) -> pd.DataFrame:
        result = df.copy()
        high = df["high"] if "high" in df else df["High"]
        low = df["low"] if "low" in df else df["Low"]
        close = df["close"] if "close" in df else df["Close"]
        volume = df["volume"] if "volume" in df else df["Volume"]

        dif, dea, macd_bar = cls.macd(close)
        result["macd_dif"] = dif
        result["macd_dea"] = dea
        result["macd_bar"] = macd_bar

        k, d, j = cls.kdj(high, low, close)
        result["kdj_k"] = k
        result["kdj_d"] = d
        result["kdj_j"] = j

        result["rsi"] = cls.rsi(close)

        upper, middle, lower, bandwidth, percent = cls.bollinger_bands(close)
        result["bb_upper"] = upper
        result["bb_middle"] = middle
        result["bb_lower"] = lower
        result["bb_bandwidth"] = bandwidth
        result["bb_percent"] = percent

        result["atr"] = cls.atr(high, low, close)

        adx, plus_di, minus_di = cls.adx(high, low, close)
        result["adx"] = adx
        result["plus_di"] = plus_di
        result["minus_di"] = minus_di

        result["obv"] = cls.obv(close, volume)
        result["vwap"] = cls.vwap(high, low, close, volume)
        result["mfi"] = cls.mfi(high, low, close, volume)

        slow_k, slow_d = cls.stoch(high, low, close)
        result["stoch_k"] = slow_k
        result["stoch_d"] = slow_d

        result["cci"] = cls.cci(high, low, close)
        result["williams_r"] = cls.williams_r(high, low, close)

        result["ema_5"] = cls.ema(close, 5)
        result["ema_10"] = cls.ema(close, 10)
        result["ema_20"] = cls.ema(close, 20)
        result["ema_60"] = cls.ema(close, 60)

        result["sma_5"] = cls.sma(close, 5)
        result["sma_10"] = cls.sma(close, 10)
        result["sma_20"] = cls.sma(close, 20)
        result["sma_60"] = cls.sma(close, 60)

        return result
