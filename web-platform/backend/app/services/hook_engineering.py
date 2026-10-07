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


@dataclass(frozen=True)
class HookCandidate:
    hook_type: str
    text: str
    score: float


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


def recommend_hooks(topic: str, evidence: dict[str, float] | None = None) -> list[HookCandidate]:
    candidates = generate_hook_candidates(topic)
    evidence = evidence or {}
    return sorted(
        candidates,
        key=lambda item: item.score + float(evidence.get(item.hook_type, 0.0)),
        reverse=True,
    )
