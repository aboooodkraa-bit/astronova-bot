from datetime import datetime
from database import list_pending_scheduled, mark_published, get_announcement
from config import CHANNEL_ID, GROUP_ID
async def publish_scheduled(context):
    a = get_announcement(context.job.data)
    if not a or a["status"] != "scheduled": return
    text = f"📢 *{a['title']}*\n\n{a['content']}"
    for t in [x for x in (CHANNEL_ID, GROUP_ID) if x]:
        try:
            if a["media_type"] == "photo" and a["media_file_id"]: await context.bot.send_photo(t, a["media_file_id"], caption=text, parse_mode="Markdown")
            else: await context.bot.send_message(t, text, parse_mode="Markdown")
        except Exception: pass
    mark_published(a["id"])
def schedule_jobs(application):
    for a in list_pending_scheduled():
        if not a["publish_at"]: continue
        try: dt = datetime.fromisoformat(a["publish_at"])
        except ValueError: continue
        when = (dt - datetime.utcnow()).total_seconds()
        if when < 0: when = 5
        application.job_queue.run_once(publish_scheduled, when=when, data=a["id"])
