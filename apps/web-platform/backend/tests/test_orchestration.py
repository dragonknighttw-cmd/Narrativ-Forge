import pytest

from app.services.orchestration import AgentTask, build_parallel_plan, default_episode_plan


pytestmark = pytest.mark.unit


def test_parallel_plan_groups_independent_tasks():
    plan = default_episode_plan()
    assert [tuple(task.name for task in stage) for stage in plan.stages] == [
        ("episode_plan",),
        ("assets", "metadata", "script"),
        ("transcript",),
        ("subtitle",),
        ("render",),
        ("qa",),
        ("approval",),
        ("export",),
    ]


def test_parallel_plan_rejects_unknown_dependency():
    try:
        build_parallel_plan([AgentTask("a", "x", ("missing",))])
    except ValueError as exc:
        assert "unknown task" in str(exc)
    else:
        raise AssertionError("expected dependency validation failure")


def test_parallel_plan_rejects_cycle():
    try:
        build_parallel_plan([AgentTask("a", "x", ("b",)), AgentTask("b", "x", ("a",))])
    except ValueError as exc:
        assert "cycle" in str(exc)
    else:
        raise AssertionError("expected cycle validation failure")


def test_execution_plan_exposes_parallel_stage_widths():
    plan = default_episode_plan()
    assert plan.stage_widths == (1, 3, 1, 1, 1, 1, 1, 1)
