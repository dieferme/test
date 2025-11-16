from __future__ import annotations

import argparse
import sys
import time
from collections import deque

from .config import BotConfig
from .data_provider import AlphaVantageClient, MarketDataError, generate_mock_data
from .models import Candle
from .strategy import MovingAverageRsiStrategy
from .trader import PaperBroker


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bot de trading simple para XAUUSD"
    )
    parser.add_argument(
        "--backtest",
        action="store_true",
        help="Ejecuta un backtest con datos históricos.",
    )
    parser.add_argument(
        "--loop",
        action="store_true",
        help="En modo live, vuelve a consultar el precio periódicamente.",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Usa datos sintéticos incluso si se dispone de API key.",
    )
    return parser.parse_args()


def run_backtest(config: BotConfig, candles: list[Candle]) -> dict[str, float | int]:
    strategy = MovingAverageRsiStrategy(
        fast_period=config.fast_ma,
        slow_period=config.slow_ma,
        rsi_period=config.rsi_period,
        rsi_overbought=config.rsi_overbought,
        rsi_oversold=config.rsi_oversold,
    )
    broker = PaperBroker(
        position_size=config.position_size,
        take_profit_pct=config.take_profit_pct,
        stop_loss_pct=config.stop_loss_pct,
    )
    history = deque(candles, maxlen=config.slow_ma * 2)
    for candle in history:
        signal = strategy.generate_signal(history)
        broker.on_signal(signal, candle)
    return broker.summary()


def run_live(config: BotConfig, loop: bool) -> None:
    if not config.alpha_vantage_key:
        raise SystemExit(
            "Se requiere ALPHA_VANTAGE_KEY en modo live. "
            "Ejecuta en modo --backtest o usa --mock."
        )
    client = AlphaVantageClient(
        api_key=config.alpha_vantage_key,
        from_symbol=config.from_symbol,
        to_symbol=config.to_symbol,
    )
    candles = client.fetch_daily()
    history = deque(candles[-config.slow_ma * 2 :], maxlen=config.slow_ma * 2)
    strategy = MovingAverageRsiStrategy(
        fast_period=config.fast_ma,
        slow_period=config.slow_ma,
        rsi_period=config.rsi_period,
        rsi_overbought=config.rsi_overbought,
        rsi_oversold=config.rsi_oversold,
    )
    broker = PaperBroker(
        position_size=config.position_size,
        take_profit_pct=config.take_profit_pct,
        stop_loss_pct=config.stop_loss_pct,
    )
    while True:
        candle = client.latest_price()
        history.append(candle)
        signal = strategy.generate_signal(history)
        broker.on_signal(signal, candle)
        summary = broker.summary()
        print(
            f"[{candle.timestamp.isoformat()}] Precio: {candle.close:.2f} | "
            f"Señal: {signal.name} | PnL acumulado: {summary['balance']:.2f}"
        )
        if not loop:
            break
        time.sleep(config.poll_interval.total_seconds())


def main() -> None:
    args = parse_args()
    config = BotConfig.from_env()
    if args.backtest or args.mock:
        candles = (
            generate_mock_data()
            if args.mock or not config.alpha_vantage_key
            else _safe_fetch_daily(config)
        )
        summary = run_backtest(config, candles)
        print("Resumen backtest:", summary)
        return
    run_live(config, loop=args.loop)


def _safe_fetch_daily(config: BotConfig) -> list[Candle]:
    if not config.alpha_vantage_key:
        return generate_mock_data()
    client = AlphaVantageClient(
        api_key=config.alpha_vantage_key,
        from_symbol=config.from_symbol,
        to_symbol=config.to_symbol,
    )
    return client.fetch_daily(outputsize="full")


if __name__ == "__main__":
    try:
        main()
    except MarketDataError as exc:
        print(f"Error al obtener datos: {exc}", file=sys.stderr)
        sys.exit(2)
    except KeyboardInterrupt:
        print("Ejecución interrumpida por el usuario.")
