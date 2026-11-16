from telegram import Update
from telegram.ext import ContextTypes
from config import CLUB_NAME_AR
from keyboards.main_menu import main_menu_kb, back_kb

ABOUT_TEXT = f"🚀 *{CLUB_NAME_AR}*\n\n*ASTRONOVA SCIENTIFIC CLUB*\nملحقة المدرسة العليا للأساتذة\n\n«نحن هنا، رغم اختلاف تخصصاتنا وتعدد اهتماماتنا، تجمعنا فكرة واحدة: أن لكل إنسان فكرة تستحق أن تُسمع، ولكل موهبة مساحة تستحق أن تُكتشف، ولكل شغف فرصة يستحق أن يُمنح.\n\nأسترونوفا ليس مجرد نادٍ جامعي، بل هو مساحة نلتقي فيها لنحوّل الأفكار إلى مشاريع، والأحلام إلى خطوات، والفضول إلى معرفة، والإبداع إلى أثر.\n\nفتحنا أبوابنا لكل التخصصات، لأننا نؤمن أن أجمل الأفكار تولد حين تلتقي العقول المختلفة.\n\nهنا لا نبحث عن أشخاص يعرفون كل شيء، بل عن أشخاص لديهم الشغف ليتعلموا، والجرأة ليجربوا، والرغبة في أن يتركوا أثرًا.\n\nأهلًا بك في عائلة أسترونوفا!\n\nأسترونوفا... حيث تلتقي العقول، وتولد الأفكار، وتبدأ الحكايات. 🚀»"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🚀 *مرحبًا بك في {CLUB_NAME_AR}*\n\nاختر من القائمة الرئيسية:", reply_markup=main_menu_kb(), parse_mode="Markdown")

async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    await q.edit_message_text(f"🚀 *{CLUB_NAME_AR}*\n\nاختر من القائمة:", reply_markup=main_menu_kb(), parse_mode="Markdown")

async def about_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    await q.edit_message_text(ABOUT_TEXT, reply_markup=back_kb(), parse_mode="Markdown")
