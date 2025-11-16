from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from .models import Candle, Position, Trade, TradeSignal


@dataclass
class PaperBroker:
    position: Position = field(default_factory=Position)
    balance: float = 0.0
    trade_log: list[Trade] = field(default_factory=list)
    take_profit_pct: float = 0.6
    stop_loss_pct: float = 0.3
    position_size: float = 1.0
    reverse_on_signal: bool = True

    def on_signal(self, signal: TradeSignal, candle: Candle) -> None:
        """Ejecuta órdenes según la señal recibida."""
        self._check_protective_levels(candle)
        if signal is TradeSignal.HOLD:
            return
        if not self.position.is_open():
            self._open_position(signal, candle)
            return
        current_side = (
            TradeSignal.BUY if self.position.size > 0 else TradeSignal.SELL
        )
        if signal is current_side:
            # Ya estamos posicionados en esa dirección.
            return
        # Cerrar posición actual y abrir en sentido contrario si está permitido.
        self._close_position(candle, reason="Cambio de señal")
        if self.reverse_on_signal:
            self._open_position(signal, candle)

    def _open_position(self, signal: TradeSignal, candle: Candle) -> None:
        direction = 1 if signal is TradeSignal.BUY else -1
        entry_price = candle.close
        trade = Trade(
            opened_at=candle.timestamp,
            side=signal,
            entry_price=entry_price,
            size=self.position_size * direction,
        )
        self.trade_log.append(trade)

        take_profit = entry_price * (
            1 + self.take_profit_pct / 100 * direction
        )
        stop_loss = entry_price * (
            1 - self.stop_loss_pct / 100 * direction
        )
        self.position = Position(
            size=self.position_size * direction,
            entry_price=entry_price,
            take_profit=take_profit,
            stop_loss=stop_loss,
        )

    def _close_position(self, candle: Candle, reason: str) -> None:
        if not self.position.is_open():
            return
        exit_price = candle.close
        trade = self.trade_log[-1]
        trade.closed_at = candle.timestamp
        trade.exit_price = exit_price
        trade.pnl = (exit_price - trade.entry_price) * trade.size
        trade.notes = reason
        self.balance += trade.pnl
        self.position = Position()

    def _check_protective_levels(self, candle: Candle) -> None:
        if not self.position.is_open():
            return
        price = candle.close
        if self.position.size > 0:
            if self.position.take_profit and price >= self.position.take_profit:
                self._close_position(candle, reason="Take Profit")
            elif self.position.stop_loss and price <= self.position.stop_loss:
                self._close_position(candle, reason="Stop Loss")
        else:
            if self.position.take_profit and price <= self.position.take_profit:
                self._close_position(candle, reason="Take Profit")
            elif self.position.stop_loss and price >= self.position.stop_loss:
                self._close_position(candle, reason="Stop Loss")

    def summary(self) -> dict[str, float | int]:
        wins = sum(1 for t in self.trade_log if (t.pnl or 0) > 0)
        losses = sum(1 for t in self.trade_log if (t.pnl or 0) < 0)
        return {
            "trades": len(self.trade_log),
            "wins": wins,
            "losses": losses,
            "balance": round(self.balance, 2),
        }
