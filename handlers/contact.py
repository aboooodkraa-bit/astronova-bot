from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, ConversationHandler, filters
from database import create_message, get_message, save_reply, set_message_status, delete_message, is_admin
from config import MESSAGE_TYPES
from keyboards.main_menu import back_kb
from services.notifications import notify_admins_message

def contact_kb():
    rows = [[InlineKeyboardButton(v, callback_data=f"contact:type:{k}")] for k, v in MESSAGE_TYPES.items()]
    rows.append([InlineKeyboardButton("🔙 العودة", callback_data="menu:main")])
    return InlineKeyboardMarkup(rows)

C_TYPE, C_TEXT = range(30, 32)

async def show_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    await q.edit_message_text("📩 *التواصل مع إدارة نادي أسترونوفا العلمي*\n\n_«لكل عضو صوتًا يستحق أن يُسمع.»_\n\nاختر نوع رسالتك:", reply_markup=contact_kb(), parse_mode="Markdown")

async def pick_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    context.user_data["msg_type"] = q.data.split(":")[2]
    await q.edit_message_text("✍️ اكتب رسالتك الآن:")
    return C_TEXT

async def save_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    mid = create_message(u.id, u.username or "", u.full_name, context.user_data.get("msg_type", "general"), update.message.text.strip())
    await update.message.reply_text(f"✅ تم الاستلام.\nرقم: `#{mid}`\nسيتم الرد قريبًا.", reply_markup=back_kb(), parse_mode="Markdown")
    try: await notify_admins_message(context.bot, mid)
    except Exception: pass
    context.user_data.clear()
    return ConversationHandler.END

async def cancel_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    context.user_data.clear()
    await q.edit_message_text("❌ إلغاء.", reply_markup=back_kb())
    return ConversationHandler.END

R_REPLY = 40

async def reply_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if not is_admin(update.effective_user.id): return ConversationHandler.END
    context.user_data["reply_to"] = int(q.data.split(":")[2])
    await q.edit_message_text(f"✍️ اكتب الرد:")
    return R_REPLY

async def reply_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mid = context.user_data.get("reply_to"); m = get_message(mid)
    if m:
        save_reply(mid, update.effective_user.id, update.message.text.strip())
        set_message_status(mid, "answered")
        try: await context.bot.send_message(m["from_id"], f"📬 *رد الإدارة #{mid}:*\n\n{update.message.text.strip()}", parse_mode="Markdown")
        except Exception: pass
        await update.message.reply_text("✅ تم الإرسال.")
    context.user_data.clear()
    return ConversationHandler.END

def get_conv_handler():
    return ConversationHandler(entry_points=[CallbackQueryHandler(pick_type, pattern="^contact:type:")],states={C_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_msg)]},fallbacks=[CallbackQueryHandler(cancel_contact, pattern="^menu:main$")])

def get_reply_conv():
    return ConversationHandler(entry_points=[CallbackQueryHandler(reply_start, pattern="^msg:reply:")],states={R_REPLY: [MessageHandler(filters.TEXT & ~filters.COMMAND, reply_save)]},fallbacks=[])
