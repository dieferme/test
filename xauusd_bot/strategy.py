from __future__ import annotations

from collections import deque
from statistics import fmean
from typing import Iterable

from .models import Candle, TradeSignal


class MovingAverageRsiStrategy:
    """Estrategia combinada SMA y RSI."""

    def __init__(
        self,
        fast_period: int = 5,
        slow_period: int = 20,
        rsi_period: int = 14,
        rsi_overbought: float = 70.0,
        rsi_oversold: float = 30.0,
    ) -> None:
        if fast_period >= slow_period:
            raise ValueError("fast_period debe ser menor que slow_period.")
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.rsi_period = rsi_period
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold

    def generate_signal(self, candles: Iterable[Candle]) -> TradeSignal:
        candles = list(candles)
        if len(candles) < self.slow_period + 1:
            return TradeSignal.HOLD
        closes = [c.close for c in candles]
        fast_ma = fmean(closes[-self.fast_period :])
        slow_ma = fmean(closes[-self.slow_period :])
        prev_fast_ma = fmean(
            closes[-self.fast_period - 1 : -1]
        )
        prev_slow_ma = fmean(
            closes[-self.slow_period - 1 : -1]
        )
        rsi = compute_rsi(closes[-(self.rsi_period * 2) :], self.rsi_period)

        bullish_cross = prev_fast_ma <= prev_slow_ma and fast_ma > slow_ma
        bearish_cross = prev_fast_ma >= prev_slow_ma and fast_ma < slow_ma

        if bullish_cross and rsi < self.rsi_overbought:
            return TradeSignal.BUY
        if bearish_cross and rsi > self.rsi_oversold:
            return TradeSignal.SELL
        return TradeSignal.HOLD


def compute_rsi(series: Iterable[float], period: int) -> float:
    data = list(series)
    if len(data) <= period:
        return 50.0
    gains = deque(maxlen=period)
    losses = deque(maxlen=period)
    for prev, curr in zip(data[:-1], data[1:]):
        delta = curr - prev
        if delta >= 0:
            gains.append(delta)
            losses.append(0.0)
        else:
            gains.append(0.0)
            losses.append(abs(delta))
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))
