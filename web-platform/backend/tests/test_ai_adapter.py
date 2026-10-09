import pytest

from app.services.ai_adapter import ContentPlan, MockAIAdapter, OpenAICompatibleAdapter, RoutedAIAdapter, ChatProvider, _configured_chat_providers


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


def test_openrouter_free_only_policy_blocks_paid_model_before_network(monkeypatch):
    called = False

    def fake_post(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("network must not be called for a paid model")

    monkeypatch.setattr("app.services.ai_adapter.httpx.post", fake_post)
    provider = ChatProvider("openrouter-1", "key", "https://openrouter.ai/api/v1", "openai/gpt-4o", 1)
    with pytest.raises(ValueError, match="free-only policy"):
        OpenAICompatibleAdapter(provider).create_content_plan(idea="test")
    assert called is False


def test_openrouter_configuration_filters_nonfree_models(monkeypatch):
    from app.services import ai_adapter

    monkeypatch.setattr(ai_adapter.settings, "openrouter_api_key", "test-key")
    monkeypatch.setattr(ai_adapter.settings, "openrouter_base_url", "https://openrouter.ai/api/v1")
    monkeypatch.setattr(
        ai_adapter.settings,
        "openrouter_models",
        "cohere/north-mini-code:free,openai/gpt-4o,openrouter/free",
    )
    providers = _configured_chat_providers()
    assert [provider.model for provider in providers] == [
        "cohere/north-mini-code:free",
        "openrouter/free",
    ]
    assert all(provider.name.startswith("openrouter-") for provider in providers)


def test_no_openrouter_key_means_mock_fallback_only(monkeypatch):
    from app.services import ai_adapter

    monkeypatch.setattr(ai_adapter.settings, "openrouter_api_key", "")
    assert _configured_chat_providers() == []


def test_router_tries_next_free_model_when_endpoint_is_unavailable(monkeypatch):
    calls = []

    class ModelUnavailableError(RuntimeError):
        status_code = 404

    class FakeAdapter:
        def __init__(self, provider):
            self.provider = provider

        def create_content_plan(self, **kwargs):
            calls.append(self.provider.name)
            if self.provider.name == "openrouter-1":
                raise ModelUnavailableError("model not found")
            return ContentPlan("hook", "script", [])

    monkeypatch.setattr("app.services.ai_adapter.OpenAICompatibleAdapter", FakeAdapter)
    providers = [
        ChatProvider("openrouter-1", "key", "https://example.test/v1", "retired:free", 1),
        ChatProvider("openrouter-2", "key", "https://example.test/v1", "active:free", 2),
    ]
    plan = RoutedAIAdapter(providers).create_content_plan(idea="test")
    assert plan.script == "script"
    assert calls == ["openrouter-1", "openrouter-2"]


def test_openrouter_free_suffix_alone_is_not_enough(monkeypatch):
    called = False

    def fake_post(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("network must not be called for an unapproved model ID")

    monkeypatch.setattr("app.services.ai_adapter.httpx.post", fake_post)
    provider = ChatProvider("openrouter-1", "key", "https://openrouter.ai/api/v1", "unknown/unapproved:free", 1)
    with pytest.raises(ValueError, match="free-only policy"):
        OpenAICompatibleAdapter(provider).create_content_plan(idea="test")
    assert called is False


def test_openrouter_agentic_harness_only_models_are_not_allowed_for_chat_completions(monkeypatch):
    from app.services import ai_adapter

    monkeypatch.setattr(ai_adapter.settings, "openrouter_api_key", "test-key")
    monkeypatch.setattr(ai_adapter.settings, "openrouter_base_url", "https://openrouter.ai/api/v1")
    monkeypatch.setattr(
        ai_adapter.settings,
        "openrouter_models",
        "thinkingmachines/inkling-small:free,thinkingmachines/inkling:free,cohere/north-mini-code:free",
    )
    providers = _configured_chat_providers()
    assert [provider.model for provider in providers] == ["cohere/north-mini-code:free"]
