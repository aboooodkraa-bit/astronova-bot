from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from database import list_admins, get_message, get_idea, get_member
from config import MESSAGE_TYPES

async def notify_admins_join(bot, rid, user_id, data):
    text = f"📥 *طلب انضمام جديد #{rid}*\n\n👤 الاسم: {data['j_name']}\n🎓 التخصص: {data['j_specialty']}\n📚 المستوى: {data['j_level']}\n📱 Username: @{data['j_username'] or '—'}\n🆔 Telegram ID: `{user_id}`\n💡 السبب: {data['j_reason']}\n⭐ المهارات: {data['j_skills']}"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("✅ قبول", callback_data=f"jr:approve:{rid}"), InlineKeyboardButton("❌ رفض", callback_data=f"jr:reject:{rid}")]])
    for a in list_admins():
        try: await bot.send_message(a["telegram_id"], text, reply_markup=kb, parse_mode="Markdown")
        except Exception: pass

async def notify_admins_message(bot, mid):
    m = get_message(mid)
    if not m: return
    text = f"📬 *رسالة جديدة #{mid}*\n\n👤 {m['full_name']}\n🆔 `{m['from_id']}`\n📱 @{m['username'] or '—'}\n📂 النوع: {MESSAGE_TYPES.get(m['type'], m['type'])}\n🕒 {m['created_at']}\n\n💬 {m['content']}"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("✅ الرد على العضو", callback_data=f"msg:reply:{mid}")],[InlineKeyboardButton("🗑️ حذف", callback_data=f"msg:del:{mid}")]])
    for a in list_admins():
        try: await bot.send_message(a["telegram_id"], text, reply_markup=kb, parse_mode="Markdown")
        except Exception: pass

async def notify_admins_new_idea(bot, iid, author_id):
    idea = get_idea(iid)
    author = get_member(author_id)
    if not idea: return
    text = f"💡 *فكرة جديدة #{iid}*\n\n👤 {author['full_name'] if author else '—'}\n📂 {idea['category']}\n\n📌 *{idea['title']}*\n\n{idea['description']}"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("✅ اعتماد", callback_data=f"idea:approve:{iid}"), InlineKeyboardButton("❌ رفض", callback_data=f"idea:reject:{iid}")]])
    for a in list_admins():
        try: await bot.send_message(a["telegram_id"], text, reply_markup=kb, parse_mode="Markdown")
        except Exception: pass
