import os
from dotenv import load_dotenv
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
SUPER_ADMIN_IDS = [int(x.strip()) for x in os.getenv("SUPER_ADMIN_IDS", "").split(",") if x.strip().isdigit()]
CHANNEL_ID = os.getenv("CHANNEL_ID") or None
GROUP_ID = os.getenv("GROUP_ID") or None
DB_PATH = os.getenv("DB_PATH", "astronova.db")
CLUB_NAME_AR = "نادي أسترونوفا العلمي"
MESSAGE_TYPES = {"suggest": "💡 اقتراح", "inquiry": "❓ استفسار", "concern": "📌 انشغال", "general": "📨 رسالة عامة"}
ANNOUNCE_CATEGORIES = {"latest": "📌 آخر الإعلانات", "upcoming": "📅 الأنشطة القادمة", "opportunities": "📝 التسجيلات والفرص", "urgent": "⚠️ الإعلانات العاجلة", "archive": "📚 أرشيف الإعلانات"}
POINTS_TASKS = {"meeting": ("حضور اجتماع النادي", 5), "activity": ("المشاركة في نشاط", 10), "organizing": ("المساهمة في تنظيم نشاط", 15), "idea": ("تقديم فكرة مميزة معتمدة", 15), "initiative": ("تنفيذ مبادرة ناجحة", 25), "media": ("التصوير والتغطية الإعلامية", 10), "design": ("تصميم منشور أو إعلان", 10), "represent": ("تمثيل النادي في فعالية جامعية", 20), "venue": ("المشاركة في تهيئة المقر", 15), "lead": ("قيادة مشروع أو نشاط", 25)}
LEVELS = [(0, "🌱 مستكشف"), (50, "🔭 باحث"), (120, "💡 مبدع"), (200, "🚀 رائد"), (300, "🌌 أسطورة أسترونوفا")]
def level_for(points: int) -> str:
    lvl = LEVELS[0][1]
    for threshold, name in LEVELS:
        if points >= threshold: lvl = name
    return lvl

# 🌟 الآي دي الخاص بالمجموعة (الذي أرسلته)
GROUP_CHAT_ID = -1004411507445
