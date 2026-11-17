from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 التعريف بالنادي", callback_data="menu:about")],
        [InlineKeyboardButton("👥 أعضاء النادي", callback_data="menu:members")],
        [InlineKeyboardButton("🤝 الانضمام إلى النادي", callback_data="menu:join")],
        [InlineKeyboardButton("📢 إعلانات النادي", callback_data="menu:announcements")],
        [InlineKeyboardButton("🏆 نظام النقاط والترتيب", callback_data="menu:points")],
        [InlineKeyboardButton("🎮 ألعاب تفاعلية", callback_data="menu:games")],
        [InlineKeyboardButton("💡 صندوق الأفكار", callback_data="menu:ideas")],
        [InlineKeyboardButton("📩 التواصل مع الإدارة", callback_data="menu:contact")],
    ])

def back_kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 العودة", callback_data="menu:main")]])
