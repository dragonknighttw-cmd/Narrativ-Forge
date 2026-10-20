"""
Burmese Two-Person AI Podcast & Audio Drama Engine.
Generates natural conversational scripts between two hosts (ကိုသူရ & မမေ)
and formats them with Edge Neural Burmese TTS parameters.
"""

from typing import List, Dict, Any
import datetime

HOST_A = {
    "name": "ကိုသူရ (Ko Thura)",
    "role": "Host & Curious Questioner",
    "voice_id": "my-MM-ThihaNeural",
    "tone": "Engaging, inquisitive, modern Burmese"
}

HOST_B = {
    "name": "မမေ (Ma May)",
    "role": "Co-host & Insightful Storyteller",
    "voice_id": "my-MM-NilarNeural",
    "tone": "Warm, analytical, descriptive"
}

PODCAST_TEMPLATES = {
    "cinema_deep_dive": {
        "title": "ရုပ်ရှင်အတွေးစကား (Cinema Deep Dive)",
        "intro_hook": "မင်္ဂလာပါ ခင်ဗျာ။ ရုပ်ရှင်ချစ်ပရိသတ်တွေအတွက် ဒီနေ့မှာတော့ မထင်မှတ်ထားတဲ့ အလှည့်အပြောင်းတွေနဲ့ ဇာတ်ကားတစ်ကားအကြောင်း မမေနဲ့အတူ ဆွေးနွေးသွားမှာပါခင်ဗျာ။",
        "bgm_preset": "Cinematic Ambient Lo-Fi",
    },
    "tech_frontier": {
        "title": "နည်းပညာနဲ့ အနာဂတ် (Tech Frontier)",
        "intro_hook": "မင်္ဂလာပါ ပရိသတ်ကြီးရေ။ ဒီတစ်ပတ်မှာ လူပြောများနေတဲ့ AI နည်းပညာတွေအကြောင်း ကိုသူရတို့ ဘယ်လိုမြင်လဲဆိုတာ စကားဝိုင်းလေး စတင်လိုက်ရအောင်နော်။",
        "bgm_preset": "Cyberpunk Synthwave",
    },
    "true_mystery": {
        "title": "လျှို့ဝှက်ဆန်းကြယ် ဇာတ်လမ်းစုံ (Mystery Files)",
        "intro_hook": "နားဆင်နေကြတဲ့ မိတ်ဆွေတို့ရေ... မဖြေရှင်းနိုင်သေးတဲ့ ပဟေဠိဆန်ဆန် ဖြစ်ရပ်တစ်ခုရဲ့ နောက်ကွယ်က လျှို့ဝှက်ချက်တွေကို အတူတူ လိုက်လံစုံစမ်းကြည့်ကြရအောင်။",
        "bgm_preset": "Suspense Dark Strings",
    }
}

def generate_burmese_duo_podcast(topic: str, synopsis: str, template_key: str = "cinema_deep_dive") -> Dict[str, Any]:
    template = PODCAST_TEMPLATES.get(template_key, PODCAST_TEMPLATES["cinema_deep_dive"])
    
    dialogues: List[Dict[str, Any]] = [
        {
            "turn": 1,
            "speaker": HOST_A["name"],
            "voice_id": HOST_A["voice_id"],
            "timestamp": "00:00 - 00:15",
            "burmese_text": template["intro_hook"],
            "cue": "Warm opening, background music fades from 100% to 20%",
        },
        {
            "turn": 2,
            "speaker": HOST_B["name"],
            "voice_id": HOST_B["voice_id"],
            "timestamp": "00:16 - 00:35",
            "burmese_text": f"ဟုတ်ကဲ့ပါ ကိုသူရရေ။ အခု ဆွေးနွေးမယ့် '{topic}' ဆိုတဲ့ အကြောင်းအရာက အပြင်မှာ တကယ်ပဲ စိတ်ဝင်စားစရာ ကောင်းတာနော်။ အထူးသဖြင့် {synopsis[:60]}... ဆိုတဲ့ အချက်က ပရိသတ်တွေကို အတော်လေး ဆွဲဆောင်သွားစေတာပါ။",
            "cue": "Enthusiastic tone, smiling voice",
        },
        {
            "turn": 3,
            "speaker": HOST_A["name"],
            "voice_id": HOST_A["voice_id"],
            "timestamp": "00:36 - 00:55",
            "burmese_text": "အဲဒီနေရာမှာ ကျွန်တော် သတိထားမိတာတစ်ခုရှိတယ် မမေ။ ဇာတ်ကောင်ရဲ့ ရွေးချယ်မှုက သာမန်လူတွေ တွေးထားသလို မဟုတ်ဘဲ လုံးဝ အလှည့်အပြောင်း ဖြစ်သွားတာလေ။ မမေကော အဲဒီအခန်းကို ဘယ်လို ခံစားရလဲ?",
            "cue": "Reflective question with dramatic pause",
        },
        {
            "turn": 4,
            "speaker": HOST_B["name"],
            "voice_id": HOST_B["voice_id"],
            "timestamp": "00:56 - 01:25",
            "burmese_text": "အင်း... အဲဒါက ဒီဇာတ်လမ်းရဲ့ အသက်ပဲ ကိုသူရ။ လူတိုင်းက မထင်ထားတဲ့ လှည့်ကွက်တစ်ခုကို ဒါရိုက်တာက သိမ်သိမ်မွေ့မွေ့လေး ထည့်ပေးလိုက်တာ။ အဆုံးသတ်ရောက်သွားတဲ့အခါ အားလုံးရဲ့ ရင်ထဲမှာ မေးခွန်းတွေ အများကြီး ကျန်ခဲ့စေတယ်လေ။",
            "cue": "Deep emotional tone, subtle chime effect",
        },
        {
            "turn": 5,
            "speaker": HOST_A["name"],
            "voice_id": HOST_A["voice_id"],
            "timestamp": "01:26 - 01:45",
            "burmese_text": "တကယ်ပဲ အချိန်ပေးပြီး နားဆင်ထိုက်တဲ့ အကြောင်းအရာပါပဲ။ နားဆင်ပေးခဲ့ကြတဲ့ မိတ်ဆွေအားလုံးကို ကျေးဇူးတင်ပါတယ်။ နောက်အပိုင်းတွေမှာလည်း စိတ်ဝင်စားစရာ ကောင်းတာတွေကို ဆက်လက် တင်ဆက်ပေးသွားမှာမို့ Subscribe လုပ်ထားကြပါဦးခင်ဗျာ။",
            "cue": "Closing beat, BGM swells to 100%",
        }
    ]

    total_est_seconds = 105
    return {
        "status": "success",
        "topic": topic,
        "template": template["title"],
        "bgm_preset": template["bgm_preset"],
        "hosts": [HOST_A, HOST_B],
        "total_dialogue_turns": len(dialogues),
        "estimated_duration": f"{total_est_seconds // 60}m {total_est_seconds % 60}s",
        "dialogues": dialogues,
        "created_at": datetime.datetime.utcnow().isoformat(),
    }
