from __future__ import annotations

import json
import time
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterator


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _to_jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, dict):
        return {str(k): _to_jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_jsonable(v) for v in value]
    return value


def make_sim_jsonl_logger(path: str | Path) -> Callable[[dict[str, Any]], None]:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    def _log(ev: dict[str, Any]) -> None:
        rec = _to_jsonable(dict(ev))
        rec.setdefault("t", time.time())
        rec.setdefault("t_utc", _utc_now_iso())
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=True) + "\n")

    return _log


def iter_sim_events(path: str | Path) -> Iterator[dict[str, Any]]:
    path = Path(path)
    if not path.exists():
        return
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except Exception:
                continue
            if isinstance(ev, dict):
                yield ev
