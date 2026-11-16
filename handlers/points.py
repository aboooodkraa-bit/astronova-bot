from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, ConversationHandler, filters
from database import get_member, add_member, list_members, member_history, ranking, monthly_ranking, add_points, all_points_log, is_admin
from config import POINTS_TASKS, level_for
from keyboards.admin_menu import points_admin_kb

# دالة لإنشاء شريط تقدم احترافي
def progress_bar(points, max_points, length=10):
    if max_points == 0: return "░" * length
    filled = int((points / max_points) * length)
    return "█" * filled + "░" * (length - filled)

POINTS_MENU_KB = InlineKeyboardMarkup([
    [InlineKeyboardButton("⭐ نقاطي الحالية", callback_data="points:mine")],
    [InlineKeyboardButton("🥇 ترتيب الأعضاء (Top 10)", callback_data="points:rank")],
    [InlineKeyboardButton("📈 سجل إنجازاتي", callback_data="points:history")],
    [InlineKeyboardButton("🎖️ مستواي في النادي", callback_data="points:level")],
    [InlineKeyboardButton("📅 ترتيب هذا الشهر", callback_data="points:monthly")],
    [InlineKeyboardButton("🔙 العودة", callback_data="menu:main")],
])

async def points_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    await q.edit_message_text("🏆 *نظام النقاط والترتيب المتقدم*\n\nاختر ما تريد استكشافه:", reply_markup=POINTS_MENU_KB, parse_mode="Markdown")

def _ensure_member(u):
    m = get_member(u.id)
    if not m: 
        add_member(u.id, u.full_name, u.username or "", "—", "—")
        m = get_member(u.id)
    return m

async def my_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    m = _ensure_member(update.effective_user)
    await q.edit_message_text(f"⭐ *نقاطك الحالية:* {m['points']}\n🎖️ *مستواك:* {level_for(m['points'])}", reply_markup=POINTS_MENU_KB, parse_mode="Markdown")

async def ranking_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    members = ranking()[:10]
    if not members:
        return await q.edit_message_text("📭 لا يوجد أعضاء بعد.", reply_markup=POINTS_MENU_KB)
    
    top_points = members[0]['points'] if members else 1
    text = "🏆 *لوحة شرف أسترونوفا (أفضل 10)*\n\n"
    
    for i, r in enumerate(members):
        if i == 0: medal = "🥇"
        elif i == 1: medal = "🥈"
        elif i == 2: medal = "🥉"
        else: medal = f"🔹 {i+1}."
        
        bar = progress_bar(r['points'], top_points)
        text += f"{medal} *{r['full_name']}*\n{bar} {r['points']} نقطة\n\n"
        
    await q.edit_message_text(text, reply_markup=POINTS_MENU_KB, parse_mode="Markdown")

async def history_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    rows = member_history(update.effective_user.id)
    if not rows: return await q.edit_message_text("📭 لا توجد عمليات.", reply_markup=POINTS_MENU_KB)
    lines = ["📈 *سجل إنجازاتك:*\n\n"] + [f"✅ +{r['points']} — {r['reason']} `({r['created_at'][:10]})`" for r in rows]
    await q.edit_message_text("\n".join(lines), reply_markup=POINTS_MENU_KB, parse_mode="Markdown")

async def level_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    m = _ensure_member(update.effective_user)
    await q.edit_message_text(f"🎖️ *مستواك:* {level_for(m['points'])}\n⭐ *نقاطك:* {m['points']}", reply_markup=POINTS_MENU_KB, parse_mode="Markdown")

async def monthly_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    lines = ["📅 *أبطال هذا الشهر*\n\n"] + [f"🏅 {r['full_name']} — {r['month_points']} نقطة" for r in monthly_ranking()[:10]]
    await q.edit_message_text("\n".join(lines), reply_markup=POINTS_MENU_KB, parse_mode="Markdown")

P_MEM, P_AMT, P_REA = range(20, 23)

async def padmin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if not is_admin(update.effective_user.id): return await q.edit_message_text("🚫 غير مصرّح.")
    await q.edit_message_text("🏆 *إدارة النقاط*", reply_markup=points_admin_kb(), parse_mode="Markdown")

async def padmin_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    lines = ["📊 *جميع الأعضاء:*\n"] + [f"• {r['full_name']} — {r['points']}" for r in list_members()[:30]]
    await q.edit_message_text("\n".join(lines), reply_markup=points_admin_kb(), parse_mode="Markdown")

async def padmin_log(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    lines = ["📜 *آخر العمليات:*\n"] + [f"• [{r['created_at'][:16]}] {r['member_id']}: {r['points']:+d} — {r['reason']}" for r in all_points_log(25)]
    await q.edit_message_text("\n".join(lines), reply_markup=points_admin_kb(), parse_mode="Markdown")

async def padmin_add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    buttons = [[InlineKeyboardButton(r["full_name"], callback_data=f"padd:m:{r['telegram_id']}")] for r in list_members()]
    buttons.append([InlineKeyboardButton("❌ إلغاء", callback_data="padd:cancel")])
    await q.edit_message_text("👤 اختر العضو:", reply_markup=InlineKeyboardMarkup(buttons))
    return P_MEM

async def padd_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    context.user_data["padd_member"] = int(q.data.split(":")[2])
    rows = [[InlineKeyboardButton(f"{label} (+{pts})", callback_data=f"padd:t:{key}")] for key, (label, pts) in POINTS_TASKS.items()]
    rows.append([InlineKeyboardButton("✏️ مبلغ مخصص", callback_data="padd:t:custom")])
    rows.append([InlineKeyboardButton("❌ إلغاء", callback_data="padd:cancel")])
    await q.edit_message_text("📌 نوع المهمة:", reply_markup=InlineKeyboardMarkup(rows))
    return P_AMT

async def padd_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    task = q.data.split(":")[2]
    if task == "custom": context.user_data["padd_task"] = ("مهمة مخصصة", None); await q.edit_message_text("✏️ أدخل عدد النقاط:"); return P_AMT
    label, pts = POINTS_TASKS[task]
    context.user_data["padd_task"] = (label, pts); context.user_data["padd_amount"] = pts
    await q.edit_message_text("📝 أدخل سبب الإضافة (أو `تخطي`):")
    return P_REA

async def padd_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: amount = int(update.message.text.strip())
    except ValueError: return await update.message.reply_text("⚠️ أدخل رقمًا.")
    context.user_data["padd_amount"] = amount
    await update.message.reply_text("📝 أدخل السبب:")
    return P_REA

async def padd_reason(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reason = update.message.text.strip()
    if reason == "تخطي": reason = context.user_data["padd_task"][0]
    amount = context.user_data["padd_amount"]; mid = context.user_data["padd_member"]
    add_points(mid, amount, reason, context.user_data["padd_task"][0], update.effective_user.id)
    m = get_member(mid)
    await update.message.reply_text(f"✅ تمت الإضافة لـ {m['full_name']}.\nرصيده الآن: {m['points']}")
    try: await context.bot.send_message(mid, f"🎉 تمت إضافة *{amount}* نقطة!\nالسبب: {reason}", parse_mode="Markdown")
    except Exception: pass
    context.user_data.clear()
    return ConversationHandler.END

async def padd_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    await q.edit_message_text("❌ إلغاء.", reply_markup=points_admin_kb())
    return ConversationHandler.END

def get_conv_handler():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(padmin_add_start, pattern="^padmin:add$")],
        states={P_MEM: [CallbackQueryHandler(padd_member, pattern="^padd:m:")],P_AMT: [CallbackQueryHandler(padd_task, pattern="^padd:t:"), MessageHandler(filters.TEXT & ~filters.COMMAND, padd_amount)],P_REA: [MessageHandler(filters.TEXT & ~filters.COMMAND, padd_reason)],},
        fallbacks=[CallbackQueryHandler(padd_cancel, pattern="^padd:cancel$")],
    )
