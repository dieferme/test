# Bot de trading XAU/USD

Este bot ejecuta una estrategia técnica básica sobre el par **XAUUSD** (oro frente al dólar estadounidense). Incluye:

- Descarga de datos desde [Alpha Vantage](https://www.alphavantage.co/) o generación de datos sintéticos para pruebas.
- Estrategia combinada de medias móviles simples (SMA) y RSI.
- Ejecutor en modo *paper trading* con control de `stop-loss` y `take-profit`.
- Backtests rápidos y modo en vivo con sondeo periódico.

## Requisitos

- Python 3.11+
- Dependencias listadas en `requirements.txt` (`pip install -r requirements.txt`)
- Una API key gratuita de Alpha Vantage para modo en vivo (`export ALPHA_VANTAGE_KEY=tu_key`)

## Ejecución

### Backtest sin API
```bash
cd /workspace
python -m xauusd_bot.bot --backtest --mock
```

### Backtest con datos reales
```bash
export ALPHA_VANTAGE_KEY=tu_key
python -m xauusd_bot.bot --backtest
```

### Modo en vivo (consulta puntual)
```bash
python -m xauusd_bot.bot
```

### Modo en vivo continuo
```bash
python -m xauusd_bot.bot --loop
```

Los parámetros (periodos, tamaños, niveles de TP/SL, intervalo de sondeo) pueden sobreescribirse con variables de entorno como `XAUUSD_FAST_MA`, `XAUUSD_TP_PCT`, etc. Revisa `config.py` para la lista completa.

## Pruebas
```bash
python -m unittest discover tests
```
