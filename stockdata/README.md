# stockdata app

This app provides a tiny proxy and client for stockdata.org.

Usage

- Set environment variable `STOCKDATA_API_KEY` to your API key.
- Query the proxy endpoint:

  GET /api/stockdata/ohlc/?symbol=MSFT&start=2025-01-01&end=2025-01-31

Notes

- This is a thin wrapper. Error handling is minimal; adapt to your needs.
