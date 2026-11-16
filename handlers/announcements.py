from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
from database import list_announcements, get_announcement, create_announcement, mark_published, is_admin
from config import ANNOUNCE_CATEGORIES, CHANNEL_ID, GROUP_ID
from keyboards.admin_menu import ann_admin_kb

def ann_menu_kb():
    rows = [[InlineKeyboardButton(v, callback_data=f"ann:cat:{k}")] for k, v in ANNOUNCE_CATEGORIES.items()]
    rows.append([InlineKeyboardButton("🔙 العودة", callback_data="menu:main")])
    return InlineKeyboardMarkup(rows)

async def show_ann_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    await q.edit_message_text("📢 *إعلانات نادي أسترونوفا العلمي*", reply_markup=ann_menu_kb(), parse_mode="Markdown")

async def show_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    cat = q.data.split(":")[2]
    anns = list_announcements(category=cat, limit=20)
    if not anns: return await q.edit_message_text("📭 لا توجد إعلانات في هذا القسم بعد.", reply_markup=ann_menu_kb())
    rows = [[InlineKeyboardButton(f"📌 {a['title']}", callback_data=f"ann:view:{a['id']}")] for a in anns]
    rows.append([InlineKeyboardButton("🔙 العودة", callback_data="menu:announcements")])
    await q.edit_message_text(f"*{ANNOUNCE_CATEGORIES[cat]}*\n\nاختر إعلانًا:", reply_markup=InlineKeyboardMarkup(rows), parse_mode="Markdown")

async def show_announcement(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    a = get_announcement(int(q.data.split(":")[2]))
    if not a: return await q.edit_message_text("⚠️ الإعلان غير موجود.")
    text = f"*{a['title']}*\n\n{a['content']}"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 العودة", callback_data=f"ann:cat:{a['category']}")]])
    await q.edit_message_text(text, reply_markup=kb, parse_mode="Markdown")

A_TITLE, A_CONTENT, A_CAT, A_MEDIA, A_SCHED, A_CONF = range(10, 16)

def category_kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton(v, callback_data=f"annnew:cat:{k}")] for k, v in ANNOUNCE_CATEGORIES.items() if k != "archive"])

async def ann_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if not is_admin(update.effective_user.id): return await q.edit_message_text("🚫 غير مصرّح.")
    await q.edit_message_text("📢 *إدارة الإعلانات*", reply_markup=ann_admin_kb(), parse_mode="Markdown")

async def new_ann_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    context.user_data["ann"] = {}
    await q.edit_message_text("✍️ أدخل *عنوان* الإعلان:", parse_mode="Markdown")
    return A_TITLE

async def new_ann_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ann"]["title"] = update.message.text.strip()
    await update.message.reply_text("📝 أدخل *محتوى* الإعلان:", parse_mode="Markdown")
    return A_CONTENT

async def new_ann_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ann"]["content"] = update.message.text.strip()
    await update.message.reply_text("📂 اختر تصنيف الإعلان:", reply_markup=category_kb())
    return A_CAT

async def new_ann_cat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    context.user_data["ann"]["category"] = q.data.split(":")[2]
    await q.edit_message_text("🖼️ أرسل صورة (أو اكتب `تخطي`):")
    return A_MEDIA

async def new_ann_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if msg.text and msg.text.strip() == "تخطي": context.user_data["ann"]["media_type"] = None
    elif msg.photo: context.user_data["ann"]["media_type"] = "photo"; context.user_data["ann"]["media_file_id"] = msg.photo[-1].file_id
    else: return await msg.reply_text("⚠️ أرسل صورة أو اكتب `تخطي`.")
    await msg.reply_text("🕒 نشر الآن أم جدولة؟", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📢 نشر الآن", callback_data="annnew:now")],[InlineKeyboardButton("🕒 جدولة", callback_data="annnew:schedule")]]))
    return A_SCHED

async def new_ann_sched(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if q.data == "annnew:now": context.user_data["ann"]["publish_at"] = None; return await _conf_view(update, context)
    await q.edit_message_text("🕒 أدخل وقت النشر بصيغة `YYYY-MM-DD HH:MM`:")
    return A_CONF

async def new_ann_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ann"]["publish_at"] = update.message.text.strip()
    return await _conf_view(update, context)

async def _conf_view(update, context):
    d = context.user_data["ann"]
    text = f"🔎 *مراجعة:*\n📌 {d['title']}\n📂 {ANNOUNCE_CATEGORIES[d['category']]}\n🕒 {d.get('publish_at') or 'فورًا'}\n\n{d['content']}"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("✅ حفظ", callback_data="annnew:save")],[InlineKeyboardButton("❌ إلغاء", callback_data="annnew:cancel")]])
    if update.callback_query: await update.callback_query.edit_message_text(text, reply_markup=kb, parse_mode="Markdown")
    else: await update.message.reply_text(text, reply_markup=kb, parse_mode="Markdown")
    return A_CONF

async def new_ann_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    d = context.user_data["ann"]
    status = "scheduled" if d.get("publish_at") else "draft"
    aid = create_announcement(d["title"], d["content"], d["category"], d.get("media_type"), d.get("media_file_id"), None, d.get("publish_at"), update.effective_user.id, status)
    if not d.get("publish_at"): await _publish_ann(context, aid)
    await q.edit_message_text(f"✅ تم الحفظ #{aid}.", reply_markup=ann_admin_kb())
    context.user_data.pop("ann", None)
    return ConversationHandler.END

async def new_ann_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    context.user_data.pop("ann", None)
    await q.edit_message_text("❌ تم الإلغاء.", reply_markup=ann_admin_kb())
    return ConversationHandler.END

async def _publish_ann(context, aid):
    a = get_announcement(aid)
    if not a: return
    text = f"📢 *{a['title']}*\n\n{a['content']}"
    for t in [x for x in (CHANNEL_ID, GROUP_ID) if x]:
        try:
            if a["media_type"] == "photo" and a["media_file_id"]: await context.bot.send_photo(t, a["media_file_id"], caption=text, parse_mode="Markdown")
            else: await context.bot.send_message(t, text, parse_mode="Markdown")
        except Exception: pass
    mark_published(aid)

def get_conv_handler():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(new_ann_start, pattern="^annadmin:create$")],
        states={A_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, new_ann_title)],A_CONTENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, new_ann_content)],A_CAT: [CallbackQueryHandler(new_ann_cat, pattern="^annnew:cat:")],A_MEDIA: [MessageHandler(filters.PHOTO | filters.TEXT, new_ann_media)],A_SCHED: [CallbackQueryHandler(new_ann_sched, pattern="^annnew:(now|schedule)$")],A_CONF: [MessageHandler(filters.TEXT & ~filters.COMMAND, new_ann_time), CallbackQueryHandler(new_ann_save, pattern="^annnew:save$"), CallbackQueryHandler(new_ann_cancel, pattern="^annnew:cancel$")],},
        fallbacks=[CallbackQueryHandler(new_ann_cancel, pattern="^admin:ann$")],
    )
