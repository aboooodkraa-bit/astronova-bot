from telegram import InlineKeyboardMarkup, InlineKeyboardButton
def admin_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 لوحة الإحصائيات", callback_data="stats:home")],
        [InlineKeyboardButton("📢 إدارة الإعلانات", callback_data="admin:ann")],
        [InlineKeyboardButton("🏆 إدارة النقاط", callback_data="admin:points")],
        [InlineKeyboardButton("💡 مراجعة الأفكار", callback_data="admin:ideas_pending")],
        [InlineKeyboardButton("👥 إدارة الأعضاء", callback_data="admin:members")],
        [InlineKeyboardButton("🔐 إدارة الصلاحيات", callback_data="admin:perms")],
        [InlineKeyboardButton("📥 الرسائل الواردة", callback_data="admin:inbox")],
        [InlineKeyboardButton("💾 نسخة احتياطية (البيانات)", callback_data="admin:backup")],
        [InlineKeyboardButton("🔙 العودة", callback_data="menu:main")]])
def ann_admin_kb(): return InlineKeyboardMarkup([[InlineKeyboardButton("✍️ إنشاء إعلان", callback_data="annadmin:create")],[InlineKeyboardButton("🔙 العودة", callback_data="admin:home")]])
def points_admin_kb(): return InlineKeyboardMarkup([[InlineKeyboardButton("➕ إضافة نقاط لعضو", callback_data="padmin:add")],[InlineKeyboardButton("📊 جميع الأعضاء", callback_data="padmin:all")],[InlineKeyboardButton("📜 سجل العمليات", callback_data="padmin:log")],[InlineKeyboardButton("🔙 العودة", callback_data="admin:home")]])
