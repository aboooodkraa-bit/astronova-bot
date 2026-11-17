import random
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from database import add_points
from keyboards.main_menu import back_kb

QUESTIONS = [
    {"q": "ما هو الكوكب الأقرب إلى الشمس؟", "a": "عطارد", "hint": "يبدأ بحرف العين"},
    {"q": "ما هي أكبر دولة عربية من حيث المساحة؟", "a": "الجزائر", "hint": "بلد المليون ونصف المليون شهيد"},
    {"q": "كم عدد كواكب المجموعة الشمسية؟", "a": "8", "hint": "رقم بين 7 و 9"},
    {"q": "ما هو أطول نهر في العالم؟", "a": "النيل", "hint": "يمر بمصر والسودان"},
    {"q": "ما هو الغاز الذي تحتاجه النباتات للقيام بعملية البناء الضوئي؟", "a": "ثاني أكسيد الكربون", "hint": "يحتوي على كلمة كربون"},
]

def games_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 لعبة الفضاء (اربح 5 نقاط)", callback_data="game:start")],
        [InlineKeyboardButton("🔙 العودة", callback_data="menu:main")],
    ])

async def show_games(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    await q.edit_message_text(
        "🎮 *ألعاب أسترونوفا التفاعلية*\n\n"
        "أجب على السؤال بشكل صحيح لتحصل على 5 نقاط تلقائياً في رصيدك!",
        reply_markup=games_menu_kb(), parse_mode="Markdown"
    )

async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    question = random.choice(QUESTIONS)
    context.user_data["current_q"] = question
    
    await q.edit_message_text(
        f"❓ *سؤال:*\n\n{question['q']}\n\n"
        f"💡 *تلميح:* {question['hint']}\n\n"
        "✍️ اكتب إجابتك الآن في المحادثة:",
        parse_mode="Markdown"
    )

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "current_q" not in context.user_data:
        return
    
    question = context.user_data["current_q"]
    user_answer = update.message.text.strip()
    
    if user_answer == question["a"]:
        add_points(update.effective_user.id, 5, "فوز في لعبة تفاعلية", "activity", 0)
        await update.message.reply_text(
            f"🎉 *إجابة صحيحة!*\nلقد حصلت على 5 نقاط في رصيدك.",
            reply_markup=games_menu_kb(), parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            f"❌ *إجابة خاطئة!*\nالإجابة الصحيحة هي: *{question['a']}*\n\nحظ أوفر في المرة القادمة!",
            reply_markup=games_menu_kb(), parse_mode="Markdown"
        )
    
    context.user_data.pop("current_q", None)
