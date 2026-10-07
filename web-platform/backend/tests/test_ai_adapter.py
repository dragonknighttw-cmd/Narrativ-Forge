import pytest

from app.services.ai_adapter import ContentPlan, MockAIAdapter, OpenAICompatibleAdapter, RoutedAIAdapter, ChatProvider


pytestmark = pytest.mark.unit


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


def test_openai_compatible_adapter_normalizes_json(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"choices": [{"message": {"content": '{"hook":"Hook","script":"Script","scenes":[{"scene_number":1,"purpose":"hook","description":"D","dialogue":"D","duration_seconds":5}]}'}}]}

    def fake_post(url, **kwargs):
        assert url == "https://example.test/v1/chat/completions"
        assert kwargs["json"]["model"] == "model"
        assert "response_format" not in kwargs["json"]
        return FakeResponse()

    monkeypatch.setattr("app.services.ai_adapter.httpx.post", fake_post)
    provider = ChatProvider("test", "key", "https://example.test/v1", "model", 1)
    plan = OpenAICompatibleAdapter(provider).create_content_plan(idea="test")
    assert plan.hook == "Hook"
    assert plan.script == "Script"
    assert plan.scenes[0]["duration_seconds"] == 5
