import unittest
from datetime import UTC, datetime

from xauusd_bot.models import Candle, TradeSignal
from xauusd_bot.trader import PaperBroker


def _candle(price: float) -> Candle:
    return Candle(
        timestamp=datetime.now(UTC),
        open=price,
        high=price,
        low=price,
        close=price,
    )


class PaperBrokerTestCase(unittest.TestCase):
    def test_open_and_close_long_trade(self) -> None:
        broker = PaperBroker(
            position_size=1.0,
            take_profit_pct=10.0,
            stop_loss_pct=10.0,
            reverse_on_signal=False,
        )
        broker.on_signal(TradeSignal.BUY, _candle(2000))
        self.assertTrue(broker.position.is_open())

        broker.on_signal(TradeSignal.SELL, _candle(2015))
        self.assertFalse(broker.position.is_open())
        self.assertEqual(1, len(broker.trade_log))
        self.assertGreater(broker.trade_log[-1].pnl, 0)

    def test_stop_loss_triggers(self) -> None:
        broker = PaperBroker(
            position_size=1.0,
            take_profit_pct=10.0,
            stop_loss_pct=0.5,
            reverse_on_signal=False,
        )
        broker.on_signal(TradeSignal.BUY, _candle(2000))
        broker.on_signal(TradeSignal.HOLD, _candle(1990))
        self.assertFalse(broker.position.is_open())


if __name__ == "__main__":
    unittest.main()
