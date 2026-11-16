from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from database import is_admin, stats_overview, stats_level_distribution, stats_top_members, stats_activity_last_months

def bar(v, m, w=10):
    if m <= 0: return "░" * w
    return "▓" * round((v/m)*w) + "░" * (w - round((v/m)*w))

def stats_kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("📊 نظرة شاملة", callback_data="stats:overview")],[InlineKeyboardButton("🎖️ توزيع المستويات", callback_data="stats:levels")],[InlineKeyboardButton("🏆 أفضل الأعضاء", callback_data="stats:top")],[InlineKeyboardButton("📈 نشاط آخر 6 أشهر", callback_data="stats:activity")],[InlineKeyboardButton("🔙 العودة", callback_data="admin:home")]])

async def stats_home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if not is_admin(update.effective_user.id): return await q.edit_message_text("🚫 غير مصرّح.")
    await q.edit_message_text("📊 *لوحة الإحصائيات*", reply_markup=stats_kb(), parse_mode="Markdown")

async def stats_overview_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    s = stats_overview()
    text = f"📊 *نظرة شاملة*\n\n👥 أعضاء: *{s['members']}*\n⭐ إجمالي النقاط: *{s['total_points']}*\n🔥 نشطاء الشهر: *{s['active_this_month']}*\n💡 أفكار: *{s['ideas_total']}*"
    await q.edit_message_text(text, reply_markup=stats_kb(), parse_mode="Markdown")

async def stats_levels_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    dist = stats_level_distribution()
    mx = max(dist.values()) if dist else 1
    text = "🎖️ *توزيع المستويات:*\n\n" + "\n".join([f"{k}\n{bar(v,mx)} {v}" for k,v in dist.items()])
    await q.edit_message_text(text, reply_markup=stats_kb(), parse_mode="Markdown")

async def stats_top_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    tops = stats_top_members(5)
    text = "🏆 *أفضل الأعضاء:*\n\n" + "\n".join([f"▪️ {r['full_name']}: {r['points']}" for r in tops])
    await q.edit_message_text(text, reply_markup=stats_kb(), parse_mode="Markdown")

async def stats_activity_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    rows = stats_activity_last_months(6)
    mx = max([r["total"] or 0 for r in rows]) if rows else 1
    text = "📈 *نشاط الأشهر:*\n\n" + "\n".join([f"📅 {r['ym']}\n{bar(r['total'] or 0, mx)}" for r in rows])
    await q.edit_message_text(text, reply_markup=stats_kb(), parse_mode="Markdown")
