from math import isclose

import pytest

from psyflow.pointer_reach import (
    angular_difference_deg,
    build_simulated_reach,
    evaluate_reach,
    polar_point,
    rotate_point,
    transform_reach_point,
)


def test_rotation_and_angles_are_consistent():
    assert rotate_point((0, 6), -45) == pytest.approx((4.242640687, 4.242640687))
    assert transform_reach_point((0, 6), "veridical", 45) == (0.0, 6.0)
    assert angular_difference_deg(-179, 179) == 2
    with pytest.raises(ValueError):
        transform_reach_point((0, 0), "invalid", 0)


def test_simulated_rotated_reach_hits_target_after_compensation():
    samples = build_simulated_reach(
        target_distance=6,
        hand_angle_deg=135,
        reaction_time_s=0.25,
        movement_time_s=0.15,
        feedback_mode="rotated",
        rotation_deg=-45,
    )
    result = evaluate_reach(
        samples,
        target_position=polar_point(6, 90),
        target_distance=6,
        target_radius=0.25,
        reaction_threshold=1,
        movement_deadline=0.5,
    )
    assert result["completed"] is True
    assert result["cursor_hit"] is True
    assert isclose(result["hand_angle_deg"], 135.0)
    assert isclose(result["cursor_angle_deg"], 90.0)


def test_slow_and_empty_reaches_timeout():
    samples = build_simulated_reach(
        target_distance=6,
        hand_angle_deg=90,
        reaction_time_s=0.25,
        movement_time_s=0.75,
        feedback_mode="none",
        rotation_deg=0,
    )
    slow = evaluate_reach(
        samples,
        target_position=(0, 6),
        target_distance=6,
        target_radius=0.25,
        reaction_threshold=1,
        movement_deadline=0.5,
    )
    empty = evaluate_reach(
        [],
        target_position=(0, 6),
        target_distance=6,
        target_radius=0.25,
        reaction_threshold=1,
        movement_deadline=0.5,
    )
    assert slow["timed_out"] is True
    assert empty["sample_count"] == 0
