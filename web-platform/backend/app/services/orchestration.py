from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AgentTask:
    """A dependency-aware unit of work; execution remains delegated to workers."""
    name: str
    capability: str
    depends_on: tuple[str, ...] = ()
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ExecutionPlan:
    stages: tuple[tuple[AgentTask, ...], ...]

    @property
    task_names(self) -> tuple[str, ...]:
        return tuple(task.name for stage in self.stages for task in stage)


def build_parallel_plan(tasks: list[AgentTask]) -> ExecutionPlan:
    """Build deterministic parallel stages using a dependency DAG."""
    by_name = {task.name: task for task in tasks}
    if len(by_name) != len(tasks):
        raise ValueError("Task names must be unique")
    for task in tasks:
        missing = [name for name in task.depends_on if name not in by_name]
        if missing:
            raise ValueError(f"{task.name} depends on unknown task(s): {missing}")

    remaining = set(by_name)
    completed: set[str] = set()
    stages: list[tuple[AgentTask, ...]] = []
    while remaining:
        ready = sorted(
            (by_name[name] for name in remaining if set(by_name[name].depends_on).issubset(completed)),
            key=lambda task: task.name,
        )
        if not ready:
            cycle = ", ".join(sorted(remaining))
            raise ValueError(f"Task dependency cycle detected: {cycle}")
        stage = tuple(ready)
        stages.append(stage)
        completed.update(task.name for task in stage)
        remaining.difference_update(task.name for task in stage)
    return ExecutionPlan(stages=tuple(stages))


def default_episode_plan() -> ExecutionPlan:
    """Reference DAG for an episode; independent preparation runs in parallel."""
    return build_parallel_plan([
        AgentTask("episode_plan", "planning"),
        AgentTask("script", "script", ("episode_plan",)),
        AgentTask("assets", "asset", ("episode_plan",)),
        AgentTask("metadata", "metadata", ("episode_plan",)),
        AgentTask("transcript", "transcription", ("assets",)),
        AgentTask("subtitle", "subtitle", ("script", "transcript")),
        AgentTask("render", "render", ("assets", "subtitle")),
        AgentTask("qa", "quality", ("render", "subtitle", "script")),
        AgentTask("approval", "human_review", ("qa",)),
        AgentTask("export", "export", ("approval",)),
    ])
