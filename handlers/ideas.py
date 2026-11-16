from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
from database import create_idea, get_idea, list_ideas, vote_idea, get_user_vote, add_points, is_admin, get_member, set_idea_status
from services.notifications import notify_admins_new_idea

def ideas_home_kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("➕ اقترح فكرة", callback_data="idea:new")],[InlineKeyboardButton("🔥 الأعلى تصويتًا", callback_data="idea:top")],[InlineKeyboardButton("🔙 العودة", callback_data="menu:main")]])

async def ideas_home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    await q.edit_message_text("💡 *صندوق أفكار أسترونوفا*\n\n_«لكل إنسان فكرة تستحق أن تُسمع»_", reply_markup=ideas_home_kb(), parse_mode="Markdown")

def _idea_list(ideas):
    rows = [[InlineKeyboardButton(f"💡 {i['title']} ({i['votes_up']}👍)", callback_data=f"idea:view:{i['id']}")] for i in ideas]
    rows.append([InlineKeyboardButton("🔙 العودة", callback_data="menu:ideas")])
    return InlineKeyboardMarkup(rows)

async def ideas_top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    ideas = list_ideas(status="approved", sort="votes", limit=15)
    await q.edit_message_text("🔥 *الأفكار الأعلى تصويتًا:*", reply_markup=_idea_list(ideas), parse_mode="Markdown")

async def idea_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    iid = int(q.data.split(":")[2]); idea = get_idea(iid)
    if not idea: return await q.edit_message_text("⚠️ غير موجودة.")
    author = get_member(idea["author_id"])
    text = f"💡 *{idea['title']}*\n\n{idea['description']}\n\n👤 {author['full_name'] if author else '—'}\n👍 {idea['votes_up']} | 👎 {idea['votes_down']}"
    my_vote = get_user_vote(iid, update.effective_user.id)
    up_btn = "👍✔️" if my_vote == "up" else "👍"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton(f"{up_btn} {idea['votes_up']}", callback_data=f"idea:up:{iid}"), InlineKeyboardButton(f"👎 {idea['votes_down']}", callback_data=f"idea:down:{iid}")],[InlineKeyboardButton("🔙 العودة", callback_data="menu:ideas")]])
    await q.edit_message_text(text, reply_markup=kb, parse_mode="Markdown")

async def idea_vote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    parts = q.data.split(":"); iid = int(parts[2]); vtype = "up" if parts[1] == "up" else "down"
    if not vote_idea(iid, update.effective_user.id, vtype): return await q.answer("⚠️ صوّتت مسبقًا!", show_alert=True)
    await q.answer("✅ تم التصويت!")
    await idea_view(update, context)

I_TITLE, I_DESC, I_CAT = range(50, 53)

async def new_idea_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    context.user_data["idea"] = {}
    await q.edit_message_text("💡 *عنوان الفكرة:*", parse_mode="Markdown")
    return I_TITLE

async def new_idea_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["idea"]["title"] = update.message.text.strip()
    await update.message.reply_text("📝 *وصف الفكرة:*")
    return I_DESC

async def new_idea_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["idea"]["description"] = update.message.text.strip()
    await update.message.reply_text("📂 اختر التصنيف:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎨 إبداع", callback_data="ideacat:art")],[InlineKeyboardButton("🔬 علم", callback_data="ideacat:science")],[InlineKeyboardButton("💻 تقنية", callback_data="ideacat:tech")]]))
    return I_CAT

async def new_idea_cat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    context.user_data["idea"]["category"] = q.data.split(":")[1]
    d = context.user_data["idea"]
    iid = create_idea(update.effective_user.id, d["title"], d["description"], d["category"])
    try: await notify_admins_new_idea(context.bot, iid, update.effective_user.id)
    except Exception: pass
    await q.edit_message_text(f"✅ تم استلام فكرتك #{iid} للمراجعة.", reply_markup=ideas_home_kb())
    context.user_data.pop("idea", None)
    return ConversationHandler.END

async def approve_idea(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if not is_admin(update.effective_user.id): return await q.answer("غير مصرح", show_alert=True)
    iid = int(q.data.split(":")[2])
    set_idea_status(iid, "approved", update.effective_user.id)
    idea = get_idea(iid)
    if idea:
        add_points(idea["author_id"], 15, f"اعتماد فكرة #{iid}", "idea", update.effective_user.id)
        try: await context.bot.send_message(idea["author_id"], f"🎉 تم اعتماد فكرتك #{iid} وتمت إضافة 15 نقطة لرصيدك!", parse_mode="Markdown")
        except: pass
    await q.edit_message_text(f"✅ تم قبول الفكرة #{iid}.")

async def reject_idea(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if not is_admin(update.effective_user.id): return await q.answer("غير مصرح", show_alert=True)
    iid = int(q.data.split(":")[2])
    set_idea_status(iid, "rejected", update.effective_user.id)
    await q.edit_message_text(f"❌ تم رفض الفكرة #{iid}.")

def get_conv_handler():
    return ConversationHandler(entry_points=[CallbackQueryHandler(new_idea_start, pattern="^idea:new$")],states={I_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, new_idea_title)],I_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, new_idea_desc)],I_CAT: [CallbackQueryHandler(new_idea_cat, pattern="^ideacat:")]},fallbacks=[])
