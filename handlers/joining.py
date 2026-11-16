from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
from database import create_join_request
from services.notifications import notify_admins_join
from keyboards.main_menu import back_kb

J_NAME, J_SPECIALTY, J_LEVEL, J_USERNAME, J_REASON, J_SKILLS, J_CONFIRM = range(7)
JOIN_INTRO = "🌌 *باب الانضمام إلى عائلة أسترونوفا مفتوح!*\n\nنؤمن أن الإبداع لا يرتبط بتخصص معين، وأن الأفكار العظيمة قد تأتي من أبسط العقول وأكثرها فضولًا.\n\nيسر نادي أسترونوفا العلمي أن يفتح أبوابه لكل طالب وطالبة يرغبون في خوض تجربة جامعية مختلفة، والمساهمة بأفكارهم ومواهبهم وطاقاتهم.\n\n*لا يشترط أن تكون خبيرًا*، ولا أن تمتلك تجربة سابقة؛ يكفي أن تمتلك الرغبة في التعلم، والاستعداد للعمل الجماعي، والشغف بصناعة شيء مميز.\n\n«لا تنتظر أن تجد المكان الذي يشبه طموحك، بل كن جزءًا من صناعته.»"
JOIN_KB = InlineKeyboardMarkup([[InlineKeyboardButton("📝 طلب الانضمام", callback_data="join:start")],[InlineKeyboardButton("ℹ️ شروط الانضمام", callback_data="join:terms")],[InlineKeyboardButton("🔙 العودة", callback_data="menu:main")]])
TERMS_TEXT = "ℹ️ *شروط الانضمام:*\n• طالب/طالبة منتظم(ة) بالملحقة.\n• الالتزام بالحضور والمساهمة الفعلية.\n• احترام أعضاء الفريق وروح العمل الجماعي.\n• الشغف بالتعلم والاستعداد للتجربة."

async def show_join_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    await q.edit_message_text(JOIN_INTRO, reply_markup=JOIN_KB, parse_mode="Markdown")

async def show_terms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    await q.edit_message_text(TERMS_TEXT, reply_markup=JOIN_KB, parse_mode="Markdown")

async def start_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    context.user_data.clear()
    await q.edit_message_text("📝 *الخطوة 1/6:* ما هو اسمك الكامل (الاسم واللقب)؟", parse_mode="Markdown")
    return J_NAME

async def got_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["j_name"] = update.message.text.strip()
    await update.message.reply_text("🎓 *الخطوة 2/6:* ما هو تخصصك؟", parse_mode="Markdown")
    return J_SPECIALTY

async def got_specialty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["j_specialty"] = update.message.text.strip()
    await update.message.reply_text("📚 *الخطوة 3/6:* ما هو مستواك الدراسي؟", parse_mode="Markdown")
    return J_LEVEL

async def got_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["j_level"] = update.message.text.strip()
    await update.message.reply_text("📱 *الخطوة 4/6:* اسم المستخدم على Telegram (أو اكتب `تخطي`).", parse_mode="Markdown")
    return J_USERNAME

async def got_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.message.text.strip()
    context.user_data["j_username"] = "" if u == "تخطي" else u.lstrip("@")
    await update.message.reply_text("💡 *الخطوة 5/6:* لماذا ترغب في الانضمام؟", parse_mode="Markdown")
    return J_REASON

async def got_reason(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["j_reason"] = update.message.text.strip()
    await update.message.reply_text("⭐ *الخطوة 6/6:* ما هي مهاراتك واهتماماتك؟", parse_mode="Markdown")
    return J_SKILLS

async def got_skills(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["j_skills"] = update.message.text.strip()
    d = context.user_data
    summary = f"📋 *مراجعة طلبك:*\n\n👤 الاسم: {d['j_name']}\n🎓 التخصص: {d['j_specialty']}\n📚 المستوى: {d['j_level']}\n📱 Username: @{d['j_username'] or '—'}\n💡 السبب: {d['j_reason']}\n⭐ المهارات: {d['j_skills']}\n"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("✅ تأكيد وإرسال", callback_data="join:confirm")],[InlineKeyboardButton("❌ إلغاء", callback_data="join:cancel")]])
    await update.message.reply_text(summary, reply_markup=kb, parse_mode="Markdown")
    return J_CONFIRM

async def confirm_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    u = update.effective_user; d = context.user_data
    rid = create_join_request(u.id, d["j_name"], d["j_specialty"], d["j_level"], d["j_username"], d["j_reason"], d["j_skills"])
    await q.edit_message_text(f"✅ *تم استلام طلبك بنجاح!*\nرقم الطلب: `#{rid}`\n\nسيتم مراجعته من طرف الإدارة.", parse_mode="Markdown")
    try: await notify_admins_join(context.bot, rid, u.id, d)
    except Exception: pass
    context.user_data.clear()
    return ConversationHandler.END

async def cancel_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    await q.edit_message_text("❌ تم إلغاء الطلب.", reply_markup=back_kb())
    context.user_data.clear()
    return ConversationHandler.END

def get_conv_handler():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(start_join, pattern="^join:start$")],
        states={J_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, got_name)],J_SPECIALTY: [MessageHandler(filters.TEXT & ~filters.COMMAND, got_specialty)],J_LEVEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, got_level)],J_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, got_username)],J_REASON: [MessageHandler(filters.TEXT & ~filters.COMMAND, got_reason)],J_SKILLS: [MessageHandler(filters.TEXT & ~filters.COMMAND, got_skills)],J_CONFIRM: [CallbackQueryHandler(confirm_join, pattern="^join:confirm$"), CallbackQueryHandler(cancel_join, pattern="^join:cancel$")],},
        fallbacks=[CallbackQueryHandler(cancel_join, pattern="^menu:main$")],
    )
