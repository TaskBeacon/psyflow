from __future__ import annotations

import json
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


class FailureCode:
    CONFIG_INVALID = "CONFIG_INVALID"
    ASSET_MISSING = "ASSET_MISSING"
    CONTRACT_INVALID = "CONTRACT_INVALID"
    TRIGGER_INVALID = "TRIGGER_INVALID"
    KEYS_INVALID = "KEYS_INVALID"
    RUNTIME_EXCEPTION = "RUNTIME_EXCEPTION"
    LOG_SCHEMA_MISMATCH = "LOG_SCHEMA_MISMATCH"
    INVARIANT_VIOLATION = "INVARIANT_VIOLATION"
    BALANCE_OFF = "BALANCE_OFF"
    TRIGGER_MISSING = "TRIGGER_MISSING"


@dataclass
class QAReport:
    status: str  # pass | fail
    failure_code: Optional[str] = None
    message: Optional[str] = None
    task_dir: Optional[str] = None
    mode: str = "qa"
    seed: Optional[int] = None
    artifacts: dict[str, str] = field(default_factory=dict)
    details: dict[str, Any] = field(default_factory=dict)
    t_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=True, indent=2)

    def write(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_json(), encoding="utf-8")
