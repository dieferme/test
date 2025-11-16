import unittest
from datetime import datetime, timedelta

from xauusd_bot.models import Candle, TradeSignal
from xauusd_bot.strategy import MovingAverageRsiStrategy, compute_rsi


def _make_candles(prices: list[float]) -> list[Candle]:
    start = datetime(2024, 1, 1)
    return [
        Candle(
            timestamp=start + timedelta(days=idx),
            open=price,
            high=price + 1,
            low=price - 1,
            close=price,
        )
        for idx, price in enumerate(prices)
    ]


class StrategyTestCase(unittest.TestCase):
    def test_buy_signal_when_fast_crosses_above(self) -> None:
        prices = [1900] * 20 + [1950]
        candles = _make_candles(prices)
        strategy = MovingAverageRsiStrategy(
            fast_period=3,
            slow_period=7,
            rsi_period=5,
            rsi_overbought=101,
        )
        signal = strategy.generate_signal(candles)
        self.assertEqual(TradeSignal.BUY, signal)

    def test_sell_signal_when_fast_crosses_below(self) -> None:
        prices = [2000] * 20 + [1950]
        candles = _make_candles(prices)
        strategy = MovingAverageRsiStrategy(
            fast_period=3,
            slow_period=7,
            rsi_period=5,
            rsi_oversold=-1,
        )
        signal = strategy.generate_signal(candles)
        self.assertEqual(TradeSignal.SELL, signal)

    def test_rsi_bounds(self) -> None:
        prices = [2000 + (idx % 2) for idx in range(20)]
        rsi = compute_rsi(prices, period=5)
        self.assertTrue(0 <= rsi <= 100)


if __name__ == "__main__":
    unittest.main()
