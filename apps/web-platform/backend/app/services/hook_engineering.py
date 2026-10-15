from __future__ import annotations

from dataclasses import dataclass


HOOK_TEMPLATES = {
    "question": "ဒီအကြောင်းကို တကယ်သိထားသင့်တာ ဘာလဲ?",
    "curiosity_gap": "လူအများ မသိသေးတဲ့ အချက်တစ်ခုရှိတယ်…",
    "bold_claim": "ဒီအချက်တစ်ခုက အမြင်ကို ပြောင်းသွားစေနိုင်တယ်။",
    "story": "ဒီအကြောင်းကို စဖြစ်ခဲ့တာက ဒီလိုပါ။",
    "problem_solution": "ဒီပြဿနာကို ဖြေရှင်းဖို့ အရင်ဆုံး ဒီအချက်ကို သိရမယ်။",
    "number": "ဒီအကြောင်းမှာ မှတ်ထားသင့်တဲ့ အချက် ၃ ချက်ရှိတယ်။",
    "contrast": "လူအများထင်တာနဲ့ တကယ်ဖြစ်နေတာက မတူဘူး။",
    "challenge": "ဒီအချက်ကို နားလည်ရင် ကိုယ်တိုင်တောင် စမ်းကြည့်ချင်လာမယ်။",
}

CANONICAL_HOOK_TYPES = (
    "question",
    "shock",
    "mystery",
    "warning",
    "personal_story",
    "contrarian",
    "cliffhanger",
    "number",
)

CANONICAL_HOOK_TEMPLATES = {
    "question": "ဒီအကြောင်းကို သင် တကယ် သိထားပြီးပြီလား?",
    "shock": "ဒီအချက်ကို သိသွားရင် လူတိုင်း အံ့သြသွားစေမယ့် အမှန်တရားတစ်ခု!",
    "mystery": "လူအများ မသိသေးတဲ့ လျှို့ဝှက်ချက်တစ်ခု ရှိနေတယ်…",
    "warning": "ဒီအမှားကို မလုပ်မိဖို့ အခုပဲ သတိထားပါ!",
    "personal_story": "ကျွန်တော်ကိုယ်တိုင် ကြုံတွေ့ခဲ့ရတဲ့ မယုံနိုင်စရာ အဖြစ်အပျက်ကတော့…",
    "contrarian": "လူတိုင်း ထင်နေကြတာက မှားနေတယ်။ တကယ့်အရှိတရားက…",
    "cliffhanger": "နောက်ဆုံးမှာ ဘာဖြစ်သွားမလဲဆိုတာ မထင်မှတ်ထားလောက်အောင်…",
    "number": "မဖြစ်မနေ သိထားသင့်တဲ့ အရေးကြီးဆုံး အချက် ၃ ချက်!",
}

HOOK_TYPE_CANONICAL_MAP = {
    "curiosity_gap": "mystery",
    "bold_claim": "shock",
    "story": "personal_story",
    "problem_solution": "warning",
    "contrast": "contrarian",
    "challenge": "cliffhanger",
}


@dataclass(frozen=True)
class HookCandidate:
    hook_type: str
    text: str
    score: float


def canonicalize_hook_type(hook_type: str) -> str:
    cleaned = hook_type.strip().lower()
    return HOOK_TYPE_CANONICAL_MAP.get(cleaned, cleaned)


def generate_hook_candidates(topic: str, *, category: str | None = None) -> list[HookCandidate]:
    topic = " ".join(topic.split()).strip()
    if not topic:
        raise ValueError("topic is required")
    candidates = []
    for index, (hook_type, template) in enumerate(HOOK_TEMPLATES.items()):
        text = f"{template} {topic[:120]}".strip()
        score = max(0.0, 1.0 - index * 0.05)
        candidates.append(HookCandidate(hook_type=hook_type, text=text, score=score))
    return candidates


def generate_canonical_hook_candidates(topic: str, *, category: str | None = None) -> list[HookCandidate]:
    topic = " ".join(topic.split()).strip()
    if not topic:
        raise ValueError("topic is required")
    candidates = []
    for index, (hook_type, template) in enumerate(CANONICAL_HOOK_TEMPLATES.items()):
        text = f"{template} {topic[:120]}".strip()
        score = max(0.0, 1.0 - index * 0.05)
        candidates.append(HookCandidate(hook_type=hook_type, text=text, score=score))
    return candidates


def recommend_hooks(topic: str, evidence: dict[str, float] | None = None) -> list[HookCandidate]:
    candidates = generate_hook_candidates(topic)
    evidence = evidence or {}
    return sorted(
        candidates,
        key=lambda item: item.score + float(evidence.get(item.hook_type, 0.0)),
        reverse=True,
    )

