import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler
from database import is_admin, list_admins, add_admin, remove_admin, log_admin, get_conn, set_message_status, delete_message, approve_join, get_join_request, set_join_status
from keyboards.admin_menu import admin_menu_kb
from config import DB_PATH

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return await update.message.reply_text("🚫 غير مصرّح.")
    await update.message.reply_text("🛡️ *لوحة التحكم الإدارية*\n\nمرحباً بك. اختر القسم:", reply_markup=admin_menu_kb(), parse_mode="Markdown")

async def admin_home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if not is_admin(update.effective_user.id): return await q.edit_message_text("🚫 غير مصرّح.")
    await q.edit_message_text("🛡️ *لوحة التحكم الإدارية*", reply_markup=admin_menu_kb(), parse_mode="Markdown")

async def backup_db(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if not is_admin(update.effective_user.id): return
    await q.edit_message_text("⏳ جاري تجهيز النسخة الاحتياطية...")
    try:
        await context.bot.send_document(update.effective_user.id, document=open(DB_PATH, 'rb'), filename="astronova_backup.db")
        await q.edit_message_text("✅ تم إرسال نسخة احتياطية من قاعدة البيانات إلى محادثتك. احتفظ بها في مكان آمن!")
    except Exception as e:
        await q.edit_message_text(f"⚠️ حدث خطأ: {e}")

async def jr_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if not is_admin(update.effective_user.id): return
    tid = approve_join(int(q.data.split(":")[2]))
    if tid:
        try: await context.bot.send_message(tid, "🎉 تم قبول انضمامك لنادي أسترونوفا!")
        except: pass
    await q.edit_message_text("✅ تم القبول.")

async def jr_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if not is_admin(update.effective_user.id): return
    rid = int(q.data.split(":")[2]); req = get_join_request(rid)
    set_join_status(rid, "rejected")
    if req:
        try: await context.bot.send_message(req["telegram_id"], "نأسف، لم يتم القبول.")
        except: pass
    await q.edit_message_text("❌ تم الرفض.")

async def inbox(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    with get_conn() as c: rows = c.execute("SELECT * FROM messages ORDER BY created_at DESC LIMIT 15").fetchall()
    text = "📥 *الرسائل:*\n\n" + "\n".join([f"#{r['id']} | {r['full_name']} | {r['type']}" for r in rows])
    await q.edit_message_text(text if rows else "📭 لا رسائل.", reply_markup=admin_menu_kb(), parse_mode="Markdown")

async def msg_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    delete_message(int(q.data.split(":")[2]))
    await q.edit_message_text("🗑️ تم الحذف.")

async def perms_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    admins = list_admins()
    text = "🔐 *المسؤولون:*\n\n" + "\n".join([f"• {a['name']} (`{a['telegram_id']}`)" for a in admins])
    await q.edit_message_text(text, reply_markup=admin_menu_kb(), parse_mode="Markdown")

async def add_admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id) or len(context.args) < 2: return
    add_admin(int(context.args[0]), " ".join(context.args[1:]), update.effective_user.id)
    await update.message.reply_text("✅ تمت الإضافة.")

async def remove_admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id) or len(context.args) < 1: return
    remove_admin(int(context.args[0]))
    await update.message.reply_text("✅ تمت الإزالة.")

def register(app):
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CommandHandler("add_admin", add_admin_cmd))
    app.add_handler(CommandHandler("remove_admin", remove_admin_cmd))
    app.add_handler(CallbackQueryHandler(admin_home, pattern="^admin:home$"))
    app.add_handler(CallbackQueryHandler(backup_db, pattern="^admin:backup$"))
    app.add_handler(CallbackQueryHandler(perms_menu, pattern="^admin:perms$"))
    app.add_handler(CallbackQueryHandler(inbox, pattern="^admin:inbox$"))
    app.add_handler(CallbackQueryHandler(jr_approve, pattern="^jr:approve:"))
    app.add_handler(CallbackQueryHandler(jr_reject, pattern="^jr:reject:"))
    app.add_handler(CallbackQueryHandler(msg_delete, pattern="^msg:del:"))
