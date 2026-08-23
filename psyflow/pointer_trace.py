"""Pure geometry and metric helpers for continuous pointer tracing."""

from __future__ import annotations

from math import hypot, sqrt
from typing import Iterable, Sequence

Point = tuple[float, float]


def advance_ordered_progress(current: float, candidate: float, *, max_step: float = 0.20) -> float:
    """Advance path progress only through a plausible forward-continuous sample.

    Closed paths map positions just counter-clockwise from the start to values
    near 1.0. Rejecting a large initial jump prevents that location from being
    mistaken for an almost-complete clockwise trace.
    """
    current_value = max(0.0, min(1.0, float(current)))
    candidate_value = max(0.0, min(1.0, float(candidate)))
    delta = candidate_value - current_value
    if 0.0 <= delta <= float(max_step):
        return candidate_value
    return current_value


def normalize_path(points: Iterable[Sequence[float]], *, closed: bool = True) -> list[Point]:
    path = [(float(point[0]), float(point[1])) for point in points]
    if len(path) < 2:
        raise ValueError("pointer trace path requires at least two points")
    if closed and path[0] != path[-1]:
        path.append(path[0])
    if all(hypot(b[0] - a[0], b[1] - a[1]) == 0.0 for a, b in zip(path, path[1:])):
        raise ValueError("pointer trace path must contain a non-zero segment")
    return path


def transform_point(point: Sequence[float], transform: str) -> Point:
    x, y = float(point[0]), float(point[1])
    if transform == "identity":
        return x, y
    if transform == "mirror_x":
        return -x, y
    raise ValueError(f"unsupported pointer transform: {transform!r}")


def nearest_path_position(point: Sequence[float], path_points: Iterable[Sequence[float]]) -> tuple[float, float]:
    """Return minimum distance and normalized arclength position on a path."""
    path = normalize_path(path_points, closed=False)
    lengths = [hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(path, path[1:])]
    total = sum(lengths)
    if total <= 0.0:
        raise ValueError("pointer trace path has zero total length")

    px, py = float(point[0]), float(point[1])
    best_distance = float("inf")
    best_progress = 0.0
    elapsed = 0.0
    for (ax, ay), (bx, by), length in zip(path, path[1:], lengths):
        if length <= 0.0:
            continue
        dx, dy = bx - ax, by - ay
        fraction = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (length * length)))
        qx, qy = ax + fraction * dx, ay + fraction * dy
        distance = hypot(px - qx, py - qy)
        if distance < best_distance:
            best_distance = distance
            best_progress = (elapsed + fraction * length) / total
        elapsed += length
    return best_distance, best_progress


def interpolate_path(path_points: Iterable[Sequence[float]], sample_count: int) -> list[Point]:
    path = normalize_path(path_points)
    count = max(2, int(sample_count))
    lengths = [hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(path, path[1:])]
    total = sum(lengths)
    targets = [total * index / (count - 1) for index in range(count)]
    samples: list[Point] = []
    segment_index = 0
    elapsed = 0.0
    for target in targets:
        while segment_index < len(lengths) - 1 and target > elapsed + lengths[segment_index]:
            elapsed += lengths[segment_index]
            segment_index += 1
        length = lengths[segment_index]
        fraction = 0.0 if length <= 0.0 else (target - elapsed) / length
        ax, ay = path[segment_index]
        bx, by = path[segment_index + 1]
        samples.append((ax + fraction * (bx - ax), ay + fraction * (by - ay)))
    return samples


def build_simulated_trace(
    path_points: Iterable[Sequence[float]],
    *,
    profile: str,
    duration_s: float,
    corridor_width: float,
    sample_count: int = 49,
) -> list[dict[str, object]]:
    """Create a deterministic trace for QA/simulation responders."""
    if profile == "timeout":
        return []
    points = interpolate_path(path_points, sample_count)
    if profile == "error" and len(points) >= 5:
        middle = len(points) // 2
        x, y = points[middle]
        points[middle] = (x + float(corridor_width) * 1.25, y)
    total = max(0.01, float(duration_s))
    return [
        {"t": total * index / (len(points) - 1), "display": [point[0], point[1]]}
        for index, point in enumerate(points)
    ]


def evaluate_trace(
    samples: Sequence[dict[str, object]],
    path_points: Iterable[Sequence[float]],
    *,
    corridor_width: float,
    completion_progress: float,
    finish_radius: float,
) -> dict[str, object]:
    path = normalize_path(path_points)
    half_width = float(corridor_width) / 2.0
    distances: list[float] = []
    max_progress = 0.0
    error_excursions = 0
    off_path_duration = 0.0
    previous_inside = True
    previous_t: float | None = None

    for sample in samples:
        display = sample.get("display")
        if not isinstance(display, (list, tuple)) or len(display) < 2:
            continue
        t = float(sample.get("t", 0.0))
        distance, progress = nearest_path_position(display, path)
        inside = distance <= half_width
        if not inside and previous_inside:
            error_excursions += 1
        if previous_t is not None and not inside:
            off_path_duration += max(0.0, t - previous_t)
        previous_inside = inside
        previous_t = t
        distances.append(distance)
        max_progress = advance_ordered_progress(max_progress, progress)

    if not distances:
        return {
            "completed": False,
            "movement_time": None,
            "error_excursions": 0,
            "off_path_duration": 0.0,
            "off_path_proportion": None,
            "rms_path_error": None,
            "max_progress": 0.0,
            "sample_count": 0,
        }

    first_t = float(samples[0].get("t", 0.0))
    last_t = float(samples[-1].get("t", first_t))
    movement_time = max(0.0, last_t - first_t)
    last_display = samples[-1].get("display")
    finish_distance = hypot(float(last_display[0]) - path[0][0], float(last_display[1]) - path[0][1])
    completed = max_progress >= float(completion_progress) and finish_distance <= float(finish_radius)
    return {
        "completed": completed,
        "movement_time": movement_time,
        "error_excursions": error_excursions,
        "off_path_duration": off_path_duration,
        "off_path_proportion": (off_path_duration / movement_time) if movement_time > 0.0 else 0.0,
        "rms_path_error": sqrt(sum(value * value for value in distances) / len(distances)),
        "max_progress": max_progress,
        "sample_count": len(distances),
    }
