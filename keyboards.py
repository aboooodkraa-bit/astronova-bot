"""keyboards.py — الأزرار التفاعلية."""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# أسماء الأزرار (callback_data)
MENU_MAIN = "menu:main"
MENU_ABOUT = "menu:about"
MENU_JOIN = "menu:join"
MENU_ACTIVITIES = "menu:activities"
MENU_ANNOUNCEMENTS = "menu:announcements"
MENU_POINTS = "menu:points"
MENU_CONTACT = "menu:contact"


def main_menu_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("🌌 التعريف بالنادي", callback_data=MENU_ABOUT)],
        [InlineKeyboardButton("👥 الانضمام إلى النادي", callback_data=MENU_JOIN)],
        [InlineKeyboardButton("📅 الأنشطة والفعاليات", callback_data=MENU_ACTIVITIES)],
        [InlineKeyboardButton("📢 إعلانات النادي", callback_data=MENU_ANNOUNCEMENTS)],
        [InlineKeyboardButton("🏆 نظام النقاط وترتيب الأعضاء", callback_data=MENU_POINTS)],
        [InlineKeyboardButton("📩 التواصل مع الإدارة", callback_data=MENU_CONTACT)],
    ]
    return InlineKeyboardMarkup(rows)


def back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔙 العودة إلى القائمة الرئيسية", callback_data=MENU_MAIN)]]
    )
