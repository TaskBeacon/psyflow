from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Optional


_NONE_STRS = {"", "none", "null", "nan", "na"}


def _parse_optional_float(v: Any) -> Optional[float]:
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        s = v.strip().lower()
        if s in _NONE_STRS:
            return None
        try:
            return float(s)
        except ValueError:
            return None
    return None


def _parse_optional_bool(v: Any) -> Optional[bool]:
    if v is None:
        return None
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return bool(int(v))
    if isinstance(v, str):
        s = v.strip().lower()
        if s in _NONE_STRS:
            return None
        if s in ("1", "true", "yes", "on"):
            return True
        if s in ("0", "false", "no", "off"):
            return False
    return None


def validate_trace_csv(
    trace_path: str | Path,
    *,
    required_columns: list[str] | None = None,
    expected_trial_count: int | None = None,
    expected_condition_counts: dict[str, int] | None = None,
    allowed_keys: list[str] | None = None,
    strict: bool = False,
) -> dict[str, Any]:
    """Validate a QA trace CSV using minimal, generic invariants."""
    trace_path = Path(trace_path)
    if not trace_path.exists():
        raise FileNotFoundError(f"Trace not found: {trace_path}")

    required_columns = required_columns or []
    allowed_keys = allowed_keys or []

    errors: list[str] = []
    warnings: list[str] = []

    with trace_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames or []

        missing_cols = [c for c in required_columns if c not in header]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Condition/balance expectations (optional).
        row_count = 0
        cond_counts: dict[str, int] = {}

        # Generic invariants per row.
        for row_i, row in enumerate(reader, start=1):
            row_count += 1
            cond = row.get("condition")
            if cond is not None and str(cond).strip().lower() not in _NONE_STRS:
                cond_s = str(cond)
                cond_counts[cond_s] = cond_counts.get(cond_s, 0) + 1

            # RT sanity + optional rt<=duration checks.
            for k, v in row.items():
                if not k.endswith("_rt"):
                    continue
                rt = _parse_optional_float(v)
                if rt is None:
                    continue
                if rt < 0:
                    errors.append(f"row {row_i}: {k} < 0 ({rt})")
                    continue

                dur_key = k[: -len("_rt")] + "_duration"
                if dur_key in row:
                    dur = _parse_optional_float(row.get(dur_key))
                    if dur is not None and rt > dur + 1e-6:
                        errors.append(f"row {row_i}: {k} ({rt}) > {dur_key} ({dur})")

            # key_press consistency checks when present.
            for k, v in row.items():
                if not k.endswith("_key_press"):
                    continue
                pressed = _parse_optional_bool(v)
                if pressed is None:
                    continue
                prefix = k[: -len("_key_press")]
                resp_k = prefix + "_response"
                rt_k = prefix + "_rt"

                resp_val = row.get(resp_k)
                rt_val = _parse_optional_float(row.get(rt_k))

                if not pressed:
                    if resp_val and str(resp_val).strip().lower() not in _NONE_STRS:
                        errors.append(f"row {row_i}: {k}=False but {resp_k} is set ({resp_val})")
                    if rt_val is not None:
                        errors.append(f"row {row_i}: {k}=False but {rt_k} is set ({rt_val})")

            # Response key sanity (optional).
            if allowed_keys:
                for k, v in row.items():
                    if not k.endswith("_response") and k != "response":
                        continue
                    if v is None:
                        continue
                    s = str(v).strip()
                    if not s or s.lower() in _NONE_STRS:
                        continue
                    if s not in allowed_keys:
                        errors.append(f"row {row_i}: {k} has unexpected key {s!r}")

            # If response_window_open is logged and closed, responses should be empty.
            rwo = row.get("response_window_open")
            open_flag = _parse_optional_bool(rwo)
            if open_flag is False:
                for k, v in row.items():
                    if not k.endswith("_response") and k != "response":
                        continue
                    if v is None:
                        continue
                    s = str(v).strip()
                    if s and s.lower() not in _NONE_STRS:
                        errors.append(f"row {row_i}: response recorded while response_window_open=0 ({k}={s!r})")

        if expected_trial_count is not None and row_count != int(expected_trial_count):
            errors.append(f"trial count mismatch: expected {expected_trial_count}, got {row_count}")

        if expected_condition_counts:
            for cond, exp_n in expected_condition_counts.items():
                got = cond_counts.get(cond, 0)
                if got != exp_n:
                    errors.append(f"condition count mismatch for {cond!r}: expected {exp_n}, got {got}")

    if errors and strict:
        raise ValueError("Trace invariants violated: " + "; ".join(errors[:5]))

    return {"errors": errors, "warnings": warnings}


def validate_events(events_path: str | Path) -> dict[str, Any]:
    """Validate trigger planned vs executed counts when events exist."""
    events_path = Path(events_path)
    if not events_path.exists():
        return {"warnings": ["qa_events.jsonl not found; trigger checks skipped."], "errors": []}

    planned: dict[int, int] = {}
    executed: dict[int, int] = {}

    with events_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except Exception:
                continue
            typ = ev.get("type")
            code = ev.get("code")
            if not isinstance(code, int):
                continue
            if typ == "trigger_planned":
                planned[code] = planned.get(code, 0) + 1
            elif typ == "trigger_executed":
                executed[code] = executed.get(code, 0) + 1

    missing: list[str] = []
    for code, n in planned.items():
        if executed.get(code, 0) < n:
            missing.append(f"code {code}: planned {n}, executed {executed.get(code, 0)}")

    errors = [f"Missing executed triggers: {missing}"] if missing else []
    return {"warnings": [], "errors": errors}
