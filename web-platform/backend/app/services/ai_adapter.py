from dataclasses import dataclass
from typing import Protocol


@dataclass
class ContentPlan:
    hook: str
    script: str
    scenes: list[dict]


class AIAdapter(Protocol):
    def create_content_plan(self, *, idea: str, category: str | None = None) -> ContentPlan:
        ...


class MockAIAdapter:
    """Deterministic adapter for local development and E2E tests."""

    def create_content_plan(self, *, idea: str, category: str | None = None) -> ContentPlan:
        hook = idea.strip()[:120]
        script = f"{idea.strip()}\n\nအဓိကအချက်တွေကို အတိုချုံးရှင်းပြပြီး လူကြည့်သူအတွက် အသုံးဝင်တဲ့အဆုံးသတ်တစ်ခု ပေးမယ်။"
        return ContentPlan(
            hook=hook,
            script=script,
            scenes=[{
                "scene_number": 1,
                "purpose": "hook",
                "description": hook,
                "dialogue": hook,
                "duration_seconds": 5,
            }, {
                "scene_number": 2,
                "purpose": "body",
                "description": "Main explanation",
                "dialogue": script,
                "duration_seconds": 20,
            }],
        )


def get_ai_adapter() -> AIAdapter:
    return MockAIAdapter()
