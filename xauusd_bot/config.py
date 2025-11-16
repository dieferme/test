from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import timedelta


@dataclass(frozen=True)
class BotConfig:
    """Configuración inmutable del bot."""

    from_symbol: str = "XAU"
    to_symbol: str = "USD"
    alpha_vantage_key: str | None = None
    fast_ma: int = 5
    slow_ma: int = 20
    rsi_period: int = 14
    rsi_overbought: float = 70.0
    rsi_oversold: float = 30.0
    position_size: float = 1.0
    take_profit_pct: float = 0.6  # %
    stop_loss_pct: float = 0.3  # %
    poll_interval: timedelta = timedelta(minutes=5)

    @classmethod
    def from_env(cls) -> "BotConfig":
        """Carga la configuración leyendo variables de entorno."""

        def _get_float(name: str, default: float) -> float:
            raw = os.getenv(name)
            return float(raw) if raw not in (None, "") else default

        def _get_int(name: str, default: int) -> int:
            raw = os.getenv(name)
            return int(raw) if raw not in (None, "") else default

        return cls(
            from_symbol=os.getenv("XAUUSD_FROM_SYMBOL", "XAU").upper(),
            to_symbol=os.getenv("XAUUSD_TO_SYMBOL", "USD").upper(),
            alpha_vantage_key=os.getenv("ALPHA_VANTAGE_KEY"),
            fast_ma=_get_int("XAUUSD_FAST_MA", 5),
            slow_ma=_get_int("XAUUSD_SLOW_MA", 20),
            rsi_period=_get_int("XAUUSD_RSI_PERIOD", 14),
            rsi_overbought=_get_float("XAUUSD_RSI_OVERBOUGHT", 70.0),
            rsi_oversold=_get_float("XAUUSD_RSI_OVERSOLD", 30.0),
            position_size=_get_float("XAUUSD_POSITION_SIZE", 1.0),
            take_profit_pct=_get_float("XAUUSD_TP_PCT", 0.6),
            stop_loss_pct=_get_float("XAUUSD_SL_PCT", 0.3),
            poll_interval=timedelta(
                minutes=_get_int("XAUUSD_POLL_MINUTES", 5)
            ),
        )
