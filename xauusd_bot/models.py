from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto


class TradeSignal(Enum):
    BUY = auto()
    SELL = auto()
    HOLD = auto()


@dataclass(slots=True)
class Candle:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float


@dataclass(slots=True)
class Position:
    size: float = 0.0
    entry_price: float | None = None
    take_profit: float | None = None
    stop_loss: float | None = None

    def is_open(self) -> bool:
        return self.size != 0 and self.entry_price is not None


@dataclass(slots=True)
class Trade:
    opened_at: datetime
    closed_at: datetime | None = None
    side: TradeSignal | None = None
    entry_price: float = 0.0
    exit_price: float | None = None
    size: float = 0.0
    pnl: float | None = None
    notes: str = ""
    metadata: dict[str, str] = field(default_factory=dict)
