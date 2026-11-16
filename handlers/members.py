from telegram import Update
from telegram.ext import ContextTypes
from keyboards.main_menu import back_kb

MEMBERS_TEXT = "👥 *أعضاء نادي أسترونوفا العلمي*\n\n👑 *رئيسة النادي:* مرام شين\n🤝 *نائبة الرئيس:* نسرين دردروبة\n\n🌟 *الأعضاء المؤسسون:*\n1. عبد الغفور كراع\n2. بلال زيبوشي\n3. ضياء ذبيحي\n4. صوفيا زرفة يحي\n5. آمنة غمري\n6. مرام بديرينة\n7. هبة خباش\n8. ميساء شمار\n\n_«وراء كل فكرة عظيمة فريق يؤمن بها، ووراء كل بداية أشخاص قرروا أن يصنعوا الاختلاف._\n\n_هؤلاء هم أصحاب الخطوة الأولى، ومن وضعوا اللبنة الأولى لهذا الحلم._\n\n_وما زالت الحكاية في بدايتها، فكل عضو جديد هو إضافة، وكل فكرة جديدة هي احتمال لبداية عظيمة._\n\n_أسترونوفا ليست أسماءً في قائمة، بل عقول اجتمعت لتصنع أثرًا.»_"

async def show_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    await q.edit_message_text(MEMBERS_TEXT, reply_markup=back_kb(), parse_mode="Markdown")
