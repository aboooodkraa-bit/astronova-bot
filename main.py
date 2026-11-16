import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from config import BOT_TOKEN
import database as db
from handlers import start as start_h, members as members_h, joining as joining_h
from handlers import announcements as ann_h, points as points_h, contact as contact_h
from handlers import admin as admin_h, ideas as ideas_h, stats as stats_h
from services.scheduler import schedule_jobs

logging.basicConfig(level=logging.INFO)

def main():
    db.init_db(); db.bootstrap_admins()
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(joining_h.get_conv_handler())
    app.add_handler(contact_h.get_conv_handler())
    app.add_handler(contact_h.get_reply_conv())
    app.add_handler(ann_h.get_conv_handler())
    app.add_handler(points_h.get_conv_handler())
    app.add_handler(ideas_h.get_conv_handler())

    app.add_handler(CommandHandler("start", start_h.start))
    admin_h.register(app)

    # أزرار الموافقة والرفض للأفكار
    app.add_handler(CallbackQueryHandler(ideas_h.approve_idea, pattern="^idea:approve:"))
    app.add_handler(CallbackQueryHandler(ideas_h.reject_idea, pattern="^idea:reject:"))

    app.add_handler(CallbackQueryHandler(start_h.main_menu_callback, pattern="^menu:main$"))
    app.add_handler(CallbackQueryHandler(start_h.about_callback, pattern="^menu:about$"))
    app.add_handler(CallbackQueryHandler(members_h.show_members, pattern="^menu:members$"))
    app.add_handler(CallbackQueryHandler(joining_h.show_join_menu, pattern="^menu:join$"))
    app.add_handler(CallbackQueryHandler(joining_h.show_terms, pattern="^join:terms$"))
    app.add_handler(CallbackQueryHandler(ann_h.show_ann_menu, pattern="^menu:announcements$"))
    app.add_handler(CallbackQueryHandler(ann_h.show_category, pattern="^ann:cat:"))
    app.add_handler(CallbackQueryHandler(ann_h.show_announcement, pattern="^ann:view:"))
    app.add_handler(CallbackQueryHandler(ann_h.ann_admin_menu, pattern="^admin:ann$"))
    app.add_handler(CallbackQueryHandler(points_h.points_menu, pattern="^menu:points$"))
    app.add_handler(CallbackQueryHandler(points_h.my_points, pattern="^points:mine$"))
    app.add_handler(CallbackQueryHandler(points_h.ranking_view, pattern="^points:rank$"))
    app.add_handler(CallbackQueryHandler(points_h.history_view, pattern="^points:history$"))
    app.add_handler(CallbackQueryHandler(points_h.level_view, pattern="^points:level$"))
    app.add_handler(CallbackQueryHandler(points_h.monthly_view, pattern="^points:monthly$"))
    app.add_handler(CallbackQueryHandler(points_h.padmin_menu, pattern="^admin:points$"))
    app.add_handler(CallbackQueryHandler(points_h.padmin_all, pattern="^padmin:all$"))
    app.add_handler(CallbackQueryHandler(points_h.padmin_log, pattern="^padmin:log$"))
    app.add_handler(CallbackQueryHandler(contact_h.show_contact, pattern="^menu:contact$"))
    
    app.add_handler(CallbackQueryHandler(ideas_h.ideas_home, pattern="^menu:ideas$"))
    app.add_handler(CallbackQueryHandler(ideas_h.ideas_top, pattern="^idea:top$"))
    app.add_handler(CallbackQueryHandler(ideas_h.idea_view, pattern="^idea:view:"))
    app.add_handler(CallbackQueryHandler(ideas_h.idea_vote, pattern="^idea:(up|down):"))
    
    app.add_handler(CallbackQueryHandler(stats_h.stats_home, pattern="^stats:home$"))
    app.add_handler(CallbackQueryHandler(stats_h.stats_overview_view, pattern="^stats:overview$"))
    app.add_handler(CallbackQueryHandler(stats_h.stats_levels_view, pattern="^stats:levels$"))
    app.add_handler(CallbackQueryHandler(stats_h.stats_top_view, pattern="^stats:top$"))
    app.add_handler(CallbackQueryHandler(stats_h.stats_activity_view, pattern="^stats:activity$"))

    schedule_jobs(app)
    print("🚀 ASTRONOVA BOT is starting...")
    app.run_polling(allowed_updates=["message", "callback_query"])

if __name__ == "__main__":
    main()
