from __future__ import annotations

import math
import random
from datetime import datetime, timedelta
from typing import Iterable

import requests

from .models import Candle


class MarketDataError(RuntimeError):
    """Error específico de obtención de datos."""


class AlphaVantageClient:
    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(
        self,
        api_key: str,
        from_symbol: str = "XAU",
        to_symbol: str = "USD",
        session: requests.Session | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("Se requiere un API key de Alpha Vantage.")

        self.api_key = api_key
        self.from_symbol = from_symbol.upper()
        self.to_symbol = to_symbol.upper()
        self.session = session or requests.Session()

    def _request(self, params: dict[str, str]) -> dict:
        try:
            response = self.session.get(
                self.BASE_URL, params=params, timeout=15
            )
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            raise MarketDataError(
                f"No se pudo contactar a Alpha Vantage: {exc}"
            ) from exc

        if "Error Message" in data:
            raise MarketDataError(data["Error Message"])
        if "Note" in data:
            raise MarketDataError(
                "Alpha Vantage respondió con una nota (probable límite de "
                "peticiones superado): "
                f"{data['Note']}"
            )
        return data

    def fetch_daily(self, outputsize: str = "compact") -> list[Candle]:
        """Obtiene velas diarias para el par configurado."""
        payload = dict(
            function="FX_DAILY",
            from_symbol=self.from_symbol,
            to_symbol=self.to_symbol,
            outputsize=outputsize,
            apikey=self.api_key,
        )
        data = self._request(payload)
        time_series = data.get("Time Series FX (Daily)")
        if not time_series:
            raise MarketDataError(
                "Respuesta inesperada al solicitar series diarias."
            )
        return _candles_from_dict(time_series.items())

    def latest_price(self) -> Candle:
        payload = dict(
            function="CURRENCY_EXCHANGE_RATE",
            from_currency=self.from_symbol,
            to_currency=self.to_symbol,
            apikey=self.api_key,
        )
        data = self._request(payload)
        price_block = data.get("Realtime Currency Exchange Rate")
        if not price_block:
            raise MarketDataError(
                "Respuesta inesperada al solicitar la cotización en tiempo real."
            )
        timestamp = _parse_datetime(price_block["6. Last Refreshed"])
        price = float(price_block["5. Exchange Rate"])
        return Candle(
            timestamp=timestamp,
            open=price,
            high=price,
            low=price,
            close=price,
        )


def generate_mock_data(
    points: int = 200, seed: int = 42, start_price: float = 2000.0
) -> list[Candle]:
    """Genera datos sintéticos para ejecutar pruebas/backtests sin API real."""
    random.seed(seed)
    now = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    candles: list[Candle] = []
    price = start_price
    for idx in range(points):
        ts = now - timedelta(days=points - idx)
        drift = math.sin(idx / 15) * 5
        noise = random.uniform(-3, 3)
        close = max(1.0, price + drift + noise)
        high = close + random.uniform(0, 2)
        low = close - random.uniform(0, 2)
        open_price = price
        candles.append(
            Candle(
                timestamp=ts,
                open=open_price,
                high=high,
                low=low,
                close=close,
            )
        )
        price = close
    return candles


def _candles_from_dict(
    raw_items: Iterable[tuple[str, dict[str, str]]]
) -> list[Candle]:
    candles = []
    for timestamp, values in raw_items:
        candles.append(
            Candle(
                timestamp=_parse_datetime(timestamp),
                open=float(values["1. open"]),
                high=float(values["2. high"]),
                low=float(values["3. low"]),
                close=float(values["4. close"]),
            )
        )
    return sorted(candles, key=lambda c: c.timestamp)


def _parse_datetime(value: str) -> datetime:
    """Alpha Vantage devuelve formatos distintos: YYYY-MM-DD o con hora."""
    formats = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d")
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise ValueError(f"No se pudo parsear la fecha: {value}")
