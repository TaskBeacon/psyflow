"""Pure geometry and simulation helpers for centre-out pointer reaches."""

from __future__ import annotations

from math import atan2, cos, degrees, hypot, radians, sin
from typing import Sequence

Point = tuple[float, float]


def normalize_angle_deg(value: float) -> float:
    """Normalize an angle to the half-open interval [-180, 180)."""
    return (float(value) + 180.0) % 360.0 - 180.0


def point_angle_deg(point: Sequence[float]) -> float:
    return degrees(atan2(float(point[1]), float(point[0])))


def angular_difference_deg(value: float, reference: float) -> float:
    return normalize_angle_deg(float(value) - float(reference))


def rotate_point(point: Sequence[float], angle_deg: float) -> Point:
    x, y = float(point[0]), float(point[1])
    theta = radians(float(angle_deg))
    return x * cos(theta) - y * sin(theta), x * sin(theta) + y * cos(theta)


def polar_point(radius: float, angle_deg: float) -> Point:
    theta = radians(float(angle_deg))
    return float(radius) * cos(theta), float(radius) * sin(theta)


def transform_reach_point(point: Sequence[float], feedback_mode: str, rotation_deg: float) -> Point:
    mode = str(feedback_mode)
    if mode in {"veridical", "none"}:
        return float(point[0]), float(point[1])
    if mode == "rotated":
        return rotate_point(point, rotation_deg)
    raise ValueError(f"unsupported reach feedback mode: {mode!r}")


def build_simulated_reach(
    *,
    target_distance: float,
    hand_angle_deg: float,
    reaction_time_s: float,
    movement_time_s: float,
    feedback_mode: str,
    rotation_deg: float,
    sample_count: int = 13,
) -> list[dict[str, object]]:
    """Build a deterministic radial reach for QA and simulation."""
    count = max(3, int(sample_count))
    endpoint = polar_point(target_distance, hand_angle_deg)
    samples: list[dict[str, object]] = []
    for index in range(count):
        fraction = index / (count - 1)
        physical = (endpoint[0] * fraction, endpoint[1] * fraction)
        shown = transform_reach_point(physical, feedback_mode, rotation_deg)
        samples.append(
            {
                "t": float(reaction_time_s) + float(movement_time_s) * fraction,
                "physical": [physical[0], physical[1]],
                "display": [shown[0], shown[1]],
                "visible": feedback_mode != "none" or index == 0,
            }
        )
    return samples


def evaluate_reach(
    samples: Sequence[dict[str, object]],
    *,
    target_position: Sequence[float],
    target_distance: float,
    target_radius: float,
    reaction_threshold: float,
    movement_deadline: float,
) -> dict[str, object]:
    """Evaluate completion, endpoint geometry, and timing for a reach."""
    valid = [sample for sample in samples if isinstance(sample.get("physical"), (list, tuple))]
    if not valid:
        return {
            "completed": False,
            "timed_out": True,
            "reaction_time": None,
            "movement_time": None,
            "physical_endpoint": None,
            "display_endpoint": None,
            "hand_angle_deg": None,
            "cursor_angle_deg": None,
            "cursor_error_deg": None,
            "cursor_hit": False,
            "sample_count": 0,
        }

    first_move_t: float | None = None
    reaction_time: float | None = None
    terminal: dict[str, object] | None = None
    for sample in valid:
        physical = sample["physical"]
        radius = hypot(float(physical[0]), float(physical[1]))
        sample_t = float(sample.get("t", 0.0))
        if first_move_t is None and radius > 0.0:
            first_move_t = sample_t
        if reaction_time is None and radius >= float(reaction_threshold):
            reaction_time = sample_t
        if radius >= float(target_distance):
            terminal = sample
            break

    if terminal is None:
        terminal = valid[-1]
    physical = terminal["physical"]
    shown = terminal.get("display", physical)
    terminal_t = float(terminal.get("t", 0.0))
    move_start = 0.0 if first_move_t is None else first_move_t
    movement_time = max(0.0, terminal_t - move_start)
    radial_complete = hypot(float(physical[0]), float(physical[1])) >= float(target_distance)
    completed = radial_complete and movement_time <= float(movement_deadline)
    target_angle = point_angle_deg(target_position)
    hand_angle = point_angle_deg(physical)
    cursor_angle = point_angle_deg(shown)
    cursor_error = angular_difference_deg(cursor_angle, target_angle)
    cursor_hit = hypot(float(shown[0]) - float(target_position[0]), float(shown[1]) - float(target_position[1])) <= float(target_radius)
    return {
        "completed": completed,
        "timed_out": not completed,
        "reaction_time": reaction_time,
        "movement_time": movement_time,
        "physical_endpoint": [float(physical[0]), float(physical[1])],
        "display_endpoint": [float(shown[0]), float(shown[1])],
        "hand_angle_deg": hand_angle,
        "cursor_angle_deg": cursor_angle,
        "cursor_error_deg": cursor_error,
        "cursor_hit": bool(completed and cursor_hit),
        "sample_count": len(valid),
    }
