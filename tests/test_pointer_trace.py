from math import isclose

import pytest

from psyflow.pointer_trace import (
    advance_ordered_progress,
    build_simulated_trace,
    evaluate_trace,
    nearest_path_position,
    normalize_path,
    transform_point,
)


PATH = [(0, 1), (1, 0), (0, -1), (-1, 0)]


def test_normalize_and_transform():
    assert normalize_path(PATH)[-1] == (0.0, 1.0)
    assert transform_point((2, -3), "mirror_x") == (-2.0, -3.0)
    assert transform_point((2, -3), "identity") == (2.0, -3.0)
    with pytest.raises(ValueError):
        transform_point((0, 0), "rotate")


def test_nearest_path_position_returns_distance_and_progress():
    distance, progress = nearest_path_position((0.5, 0.5), normalize_path(PATH))
    assert isclose(distance, 0.0, abs_tol=1e-9)
    assert 0.0 < progress < 0.5


def test_simulated_accurate_trace_completes_without_errors():
    samples = build_simulated_trace(PATH, profile="accurate", duration_s=2.0, corridor_width=0.2)
    result = evaluate_trace(
        samples,
        PATH,
        corridor_width=0.2,
        completion_progress=0.90,
        finish_radius=0.15,
    )
    assert result["completed"] is True
    assert result["error_excursions"] == 0
    assert isclose(result["movement_time"], 2.0)


def test_simulated_error_trace_records_excursion():
    samples = build_simulated_trace(PATH, profile="error", duration_s=2.0, corridor_width=0.2)
    result = evaluate_trace(
        samples,
        PATH,
        corridor_width=0.2,
        completion_progress=0.90,
        finish_radius=0.15,
    )
    assert result["completed"] is True
    assert result["error_excursions"] >= 1
    assert result["off_path_duration"] > 0.0


def test_timeout_trace_has_null_metrics():
    result = evaluate_trace(
        [],
        PATH,
        corridor_width=0.2,
        completion_progress=0.90,
        finish_radius=0.15,
    )
    assert result["completed"] is False
    assert result["movement_time"] is None


def test_reverse_departure_cannot_shortcut_closed_path_completion():
    path = normalize_path(PATH)
    reverse_samples = [
        {"t": 0.0, "display": [0.0, 1.0]},
        {"t": 0.1, "display": [-0.05, 0.95]},
        {"t": 0.2, "display": [-0.10, 0.90]},
        {"t": 0.3, "display": [0.0, 1.0]},
    ]
    result = evaluate_trace(
        reverse_samples,
        path,
        corridor_width=0.2,
        completion_progress=0.90,
        finish_radius=0.15,
    )
    assert result["completed"] is False
    assert result["max_progress"] == 0.0
    assert advance_ordered_progress(0.10, 0.15) == 0.15
    assert advance_ordered_progress(0.0, 0.95) == 0.0
