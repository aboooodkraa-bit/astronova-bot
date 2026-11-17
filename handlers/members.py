from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from database import list_members, get_new_members
from keyboards.main_menu import back_kb

def members_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌟 الأعضاء المؤسسون", callback_data="members:founders")],
        [InlineKeyboardButton("📋 جميع الأعضاء المسجلين", callback_data="members:all")],
        [InlineKeyboardButton("🆕 أحدث المنضمين", callback_data="members:new")],
        [InlineKeyboardButton("🔙 العودة", callback_data="menu:main")],
    ])

async def show_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    await q.edit_message_text("👥 *قسم الأعضاء*\n\nاختر القائمة التي تريد استعراضها:", reply_markup=members_menu_kb(), parse_mode="Markdown")

async def show_founders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    text = (
        "👑 *رئيسة النادي:* مرام شين\n"
        "🤝 *نائبة الرئيس:* نسرين دردروبة\n\n"
        "🌟 *الأعضاء المؤسسون:*\n"
        "1. عبد الغفور كراع\n2. بلال زيبوشي\n3. ضياء ذبيحي\n4. صوفيا زرفة يحي\n"
        "5. آمنة غمري\n6. مرام بديرينة\n7. هبة خباش\n8. ميساء شمار\n\n"
        "_«وراء كل فكرة عظيمة فريق يؤمن بها.»_"
    )
    await q.edit_message_text(text, reply_markup=members_menu_kb(), parse_mode="Markdown")

async def show_all_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    members = list_members()
    if not members:
        return await q.edit_message_text("📭 لا يوجد أعضاء مسجلون حالياً.", reply_markup=members_menu_kb())
    
    text = f"📋 *جميع الأعضاء المسجلين ({len(members)}):*\n\n"
    for i, m in enumerate(members, 1):
        text += f"{i}. {m['full_name']}\n"
        if i >= 40:
            text += "\n_(وغيرهم...)_"
            break
    await q.edit_message_text(text, reply_markup=members_menu_kb(), parse_mode="Markdown")

async def show_new_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    members = get_new_members(15)
    if not members:
        return await q.edit_message_text("📭 لا يوجد أعضاء جدد.", reply_markup=members_menu_kb())
    
    text = "🆕 *أحدث 15 عضواً انضموا للبوت:*\n\n"
    for i, m in enumerate(members, 1):
        date = m['joined_at'][:10] if m['joined_at'] else "—"
        text += f"{i}. {m['full_name']} `({date})`\n"
    await q.edit_message_text(text, reply_markup=members_menu_kb(), parse_mode="Markdown")
