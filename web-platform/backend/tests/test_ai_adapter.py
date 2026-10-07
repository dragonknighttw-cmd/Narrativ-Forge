import pytest

from app.services.ai_adapter import ContentPlan, MockAIAdapter, RoutedAIAdapter, ChatProvider


def test_mock_adapter_is_deterministic():
    plan = MockAIAdapter().create_content_plan(idea="မြန်မာအကြောင်းအရာ")
    assert isinstance(plan, ContentPlan)
    assert plan.hook
    assert plan.script
    assert plan.scenes


def test_router_uses_fallback_when_no_provider_is_configured():
    plan = RoutedAIAdapter([]).create_content_plan(idea="test")
    assert plan.script


def test_router_orders_providers_by_priority(monkeypatch):
    calls = []

    class FakeAdapter:
        def __init__(self, provider):
            self.provider = provider

        def create_content_plan(self, **kwargs):
            calls.append(self.provider.name)
            if self.provider.name == "groq":
                raise RuntimeError("temporary timeout")
            return ContentPlan("hook", "script", [])

    monkeypatch.setattr("app.services.ai_adapter.OpenAICompatibleAdapter", FakeAdapter)
    providers = [
        ChatProvider("openai", "key", "https://example.test/v1", "model", 20),
        ChatProvider("groq", "key", "https://example.test/v1", "model", 10),
    ]
    plan = RoutedAIAdapter(providers).create_content_plan(idea="test")
    assert plan.script == "script"
    assert calls == ["groq", "openai"]
