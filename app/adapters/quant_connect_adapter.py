from __future__ import annotations

import csv
import gzip
import json
from dataclasses import asdict
from datetime import datetime as _dt
from pathlib import Path
from typing import Iterator, Iterable, Dict, Any, Optional, Set

from app.adapters.base_adapter import BaseAdapter, Period
from app.models import Symbol
from app.adapters.factory import register_adapter


class QuantConnectAdapter(BaseAdapter):
    """Adapter for local QuantConnect/Lean dataset files.

    This adapter operates on files or directories specified by the
    datasource.config `path`. It supports CSV and JSONL (NDJSON)
    formats and common timestamp/ohlc field names. It intentionally
    avoids any network calls and is suitable for local backtests.

    Config options:
      - path: Path to a file or directory containing data files.
      - format: "csv" or "jsonl" (optional, auto-detected by fileext)
      - field_map: optional mapping of canonical names to file fields
          e.g. {"timestamp":"time","open":"o"}
      - periods: optional list of supported period strings
    """

    def __init__(
        self,
        path: str | Path,
        fmt: Optional[str] = None,
        field_map: Optional[Dict[str, str]] = None,
        periods: Optional[Set[str]] = None,
    ) -> None:
        self.path = Path(path)
        self.fmt = fmt
        self.field_map = field_map or {}
        self.periods = periods or {
            p.value for p in (
                Period.ONE_MINUTE,
                Period.FIVE_MINUTES,
                Period.ONE_DAY,
            )
        }

    def list_symbols(self) -> Iterable[Symbol]:
        # If path is a file, return its basename as a single symbol
        if self.path.is_file():
            name = self.path.stem
            yield Symbol(symbol=name, name=name, periods=self.periods)
            return

        # Otherwise scan directory for files like SYMBOL[_PERIOD].ext
        if self.path.is_dir():
            for p in sorted(self.path.iterdir()):
                if not p.is_file():
                    continue
                if p.suffix.lower() not in ('.csv', '.jsonl', '.gz'):
                    continue
                # derive symbol from filename (before first underscore)
                base = p.stem
                symbol = base.split('_', 1)[0]
                yield Symbol(symbol=symbol, name=symbol, periods=self.periods)

    def _open(self, p: Path):
        if p.suffix == '.gz':
            return gzip.open(p, mode='rt', encoding='utf-8')
        return open(p, 'rt', encoding='utf-8', newline='')

    def _find_file_for(self, symbol: str, period: str | Period) -> Optional[Path]:
        # If configured path is a file, return it when symbol matches
        if self.path.is_file():
            if self.path.stem.startswith(symbol):
                return self.path
            return None

        # search directory for common filename patterns
        per = period.value if isinstance(period, Period) else str(period)
        candidates = [
            f"{symbol}_{per}.csv",
            f"{symbol}_{per}.jsonl",
            f"{symbol}.csv",
            f"{symbol}.jsonl",
        ]
        for name in candidates:
            p = self.path / name
            if p.exists():
                return p
        # try case-insensitive match
        for p in self.path.iterdir():
            if not p.is_file():
                continue
            if p.stem.lower().startswith(symbol.lower()):
                return p
        return None

    def fetch_ohlc(
        self,
        symbol: str,
        period: Period | str,
        start: _dt = None,
        end: _dt = None,
    ) -> Iterator[Dict[str, Any]]:
        p = self._find_file_for(symbol, period)
        if not p:
            return iter(())

        # detect format
        suffix = p.suffix.lower()
        if suffix == '.gz':
            # inspect inner name
            inner = p.with_suffix('').suffix.lower()
            fmt = 'jsonl' if inner == '.jsonl' else 'csv'
        else:
            fmt = 'jsonl' if suffix == '.jsonl' else 'csv'

        # dispatch readers
        if fmt == 'csv':
            with self._open(p) as fh:
                reader = csv.DictReader(fh)
                for row in reader:
                    ts_raw = row.get(self.field_map.get('timestamp', 'time')) or row.get('time') or row.get('timestamp')
                    if not ts_raw:
                        continue
                    try:
                        ts = _dt.fromisoformat(ts_raw)
                    except Exception:
                        try:
                            ts = _dt.fromtimestamp(float(ts_raw))
                        except Exception:
                            continue
                    item = {
                        'timestamp': ts,
                        'open': float(row.get(self.field_map.get('open', 'open') or 'open')),
                        'high': float(row.get(self.field_map.get('high', 'high') or 'high')),
                        'low': float(row.get(self.field_map.get('low', 'low') or 'low')),
                        'close': float(row.get(self.field_map.get('close', 'close') or 'close')),
                        'volume': int(row.get(self.field_map.get('volume', 'volume') or 'volume') or 0),
                    }
                    if start and item['timestamp'] < start:
                        continue
                    if end and item['timestamp'] > end:
                        continue
                    yield item

        else:  # jsonl
            with self._open(p) as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                    except Exception:
                        continue
                    ts_raw = obj.get(self.field_map.get('timestamp', 'time')) or obj.get('time') or obj.get('t')
                    if not ts_raw:
                        continue
                    try:
                        ts = _dt.fromisoformat(ts_raw)
                    except Exception:
                        try:
                            ts = _dt.fromtimestamp(float(ts_raw))
                        except Exception:
                            continue
                    item = {
                        'timestamp': ts,
                        'open': float(obj.get(self.field_map.get('open', 'o')) or obj.get('o') or obj.get('open')),
                        'high': float(obj.get(self.field_map.get('high', 'h')) or obj.get('h') or obj.get('high')),
                        'low': float(obj.get(self.field_map.get('low', 'l')) or obj.get('l') or obj.get('low')),
                        'close': float(obj.get(self.field_map.get('close', 'c')) or obj.get('c') or obj.get('close')),
                        'volume': int(obj.get(self.field_map.get('volume', 'v')) or obj.get('v') or obj.get('volume') or 0),
                    }
                    if start and item['timestamp'] < start:
                        continue
                    if end and item['timestamp'] > end:
                        continue
                    yield item


# register with factory
def _qc_ctor(cfg: Dict[str, Any]) -> QuantConnectAdapter:
    return QuantConnectAdapter(
        path=cfg.get('path'),
        fmt=cfg.get('format'),
        field_map=cfg.get('field_map'),
        periods=set(cfg.get('periods') or []),
    )


register_adapter('quantconnect', _qc_ctor)
