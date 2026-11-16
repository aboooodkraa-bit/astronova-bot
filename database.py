import sqlite3
from datetime import datetime
from contextlib import contextmanager
from config import DB_PATH, SUPER_ADMIN_IDS, level_for
def now(): return datetime.utcnow().isoformat(timespec="seconds")
@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row
    try:
        yield conn; conn.commit()
    finally: conn.close()
def init_db():
    with get_conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS admins (telegram_id INTEGER PRIMARY KEY, name TEXT, role TEXT DEFAULT 'admin', added_by INTEGER, added_at TEXT);
        CREATE TABLE IF NOT EXISTS members (telegram_id INTEGER PRIMARY KEY, full_name TEXT, username TEXT, specialty TEXT, level TEXT, joined_at TEXT, points INTEGER DEFAULT 0);
        CREATE TABLE IF NOT EXISTS join_requests (id INTEGER PRIMARY KEY AUTOINCREMENT, telegram_id INTEGER, full_name TEXT, specialty TEXT, level TEXT, username TEXT, reason TEXT, skills TEXT, status TEXT DEFAULT 'pending', created_at TEXT);
        CREATE TABLE IF NOT EXISTS announcements (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, category TEXT, media_type TEXT, media_file_id TEXT, link TEXT, status TEXT DEFAULT 'draft', publish_at TEXT, published_at TEXT, created_by INTEGER, created_at TEXT);
        CREATE TABLE IF NOT EXISTS points_log (id INTEGER PRIMARY KEY AUTOINCREMENT, member_id INTEGER, points INTEGER, reason TEXT, task_type TEXT, admin_id INTEGER, created_at TEXT);
        CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, from_id INTEGER, username TEXT, full_name TEXT, type TEXT, content TEXT, status TEXT DEFAULT 'new', created_at TEXT);
        CREATE TABLE IF NOT EXISTS message_replies (id INTEGER PRIMARY KEY AUTOINCREMENT, message_id INTEGER, admin_id INTEGER, content TEXT, created_at TEXT);
        CREATE TABLE IF NOT EXISTS admin_log (id INTEGER PRIMARY KEY AUTOINCREMENT, admin_id INTEGER, action TEXT, details TEXT, created_at TEXT);
        CREATE TABLE IF NOT EXISTS ideas (id INTEGER PRIMARY KEY AUTOINCREMENT, author_id INTEGER, title TEXT, description TEXT, category TEXT, status TEXT DEFAULT 'pending', votes_up INTEGER DEFAULT 0, votes_down INTEGER DEFAULT 0, created_at TEXT, approved_at TEXT, approved_by INTEGER);
        CREATE TABLE IF NOT EXISTS idea_votes (id INTEGER PRIMARY KEY AUTOINCREMENT, idea_id INTEGER, user_id INTEGER, vote_type TEXT, created_at TEXT, UNIQUE(idea_id, user_id));
        CREATE TABLE IF NOT EXISTS idea_comments (id INTEGER PRIMARY KEY AUTOINCREMENT, idea_id INTEGER, user_id INTEGER, content TEXT, created_at TEXT);
        """)
def bootstrap_admins():
    with get_conn() as c:
        for tid in SUPER_ADMIN_IDS: c.execute("INSERT OR IGNORE INTO admins(telegram_id, name, role, added_at) VALUES (?,?,?,?)", (tid, "Super Admin", "super_admin", now()))
def is_admin(tid):
    with get_conn() as c: return bool(c.execute("SELECT 1 FROM admins WHERE telegram_id=?", (tid,)).fetchone()) or tid in SUPER_ADMIN_IDS
def add_admin(tid, name, by, role="admin"):
    with get_conn() as c: c.execute("INSERT OR REPLACE INTO admins(telegram_id,name,role,added_by,added_at) VALUES (?,?,?,?,?)", (tid, name, role, by, now()))
def remove_admin(tid):
    with get_conn() as c: c.execute("DELETE FROM admins WHERE telegram_id=?", (tid,))
def list_admins():
    with get_conn() as c: return c.execute("SELECT * FROM admins ORDER BY role DESC, added_at").fetchall()
def log_admin(admin_id, action, details=""):
    with get_conn() as c: c.execute("INSERT INTO admin_log(admin_id,action,details,created_at) VALUES (?,?,?,?)", (admin_id, action, details, now()))
def get_member(tid):
    with get_conn() as c: return c.execute("SELECT * FROM members WHERE telegram_id=?", (tid,)).fetchone()
def add_member(tid, full_name, username, specialty, level):
    with get_conn() as c: c.execute("INSERT OR IGNORE INTO members(telegram_id,full_name,username,specialty,level,joined_at,points) VALUES (?,?,?,?,?,?,0)", (tid, full_name, username, specialty, level, now()))
def list_members():
    with get_conn() as c: return c.execute("SELECT * FROM members ORDER BY points DESC, full_name").fetchall()
def create_join_request(tid, full_name, specialty, level, username, reason, skills):
    with get_conn() as c: return c.execute("INSERT INTO join_requests(telegram_id,full_name,specialty,level,username,reason,skills,created_at) VALUES (?,?,?,?,?,?,?,?)", (tid, full_name, specialty, level, username, reason, skills, now())).lastrowid
def get_join_request(rid):
    with get_conn() as c: return c.execute("SELECT * FROM join_requests WHERE id=?", (rid,)).fetchone()
def set_join_status(rid, status):
    with get_conn() as c: c.execute("UPDATE join_requests SET status=? WHERE id=?", (status, rid))
def approve_join(rid):
    req = get_join_request(rid)
    if not req: return None
    add_member(req["telegram_id"], req["full_name"], req["username"], req["specialty"], req["level"]); set_join_status(rid, "approved"); return req["telegram_id"]
def add_points(member_id, points, reason, task_type, admin_id):
    with get_conn() as c:
        c.execute("UPDATE members SET points = points + ? WHERE telegram_id=?", (points, member_id))
        c.execute("INSERT INTO points_log(member_id,points,reason,task_type,admin_id,created_at) VALUES (?,?,?,?,?,?)", (member_id, points, reason, task_type, admin_id, now()))
def member_history(member_id, limit=20):
    with get_conn() as c: return c.execute("SELECT * FROM points_log WHERE member_id=? ORDER BY created_at DESC LIMIT ?", (member_id, limit)).fetchall()
def ranking():
    with get_conn() as c: return c.execute("SELECT * FROM members ORDER BY points DESC, full_name").fetchall()
def monthly_ranking():
    with get_conn() as c:
        start = datetime.utcnow().strftime("%Y-%m-01T00:00:00")
        return c.execute("SELECT m.telegram_id, m.full_name, COALESCE(SUM(p.points),0) AS month_points FROM members m LEFT JOIN points_log p ON p.member_id = m.telegram_id AND p.created_at >= ? GROUP BY m.telegram_id ORDER BY month_points DESC", (start,)).fetchall()
def all_points_log(limit=100):
    with get_conn() as c: return c.execute("SELECT * FROM points_log ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
def create_message(from_id, username, full_name, type_, content):
    with get_conn() as c: return c.execute("INSERT INTO messages(from_id,username,full_name,type,content,created_at) VALUES (?,?,?,?,?,?)", (from_id, username, full_name, type_, content, now())).lastrowid
def get_message(mid):
    with get_conn() as c: return c.execute("SELECT * FROM messages WHERE id=?", (mid,)).fetchone()
def set_message_status(mid, status):
    with get_conn() as c: c.execute("UPDATE messages SET status=? WHERE id=?", (status, mid))
def delete_message(mid):
    with get_conn() as c: c.execute("DELETE FROM messages WHERE id=?", (mid,))
def save_reply(mid, admin_id, content):
    with get_conn() as c: c.execute("INSERT INTO message_replies(message_id,admin_id,content,created_at) VALUES (?,?,?,?)", (mid, admin_id, content, now()))
def create_idea(author_id, title, description, category="عام"):
    with get_conn() as c: return c.execute("INSERT INTO ideas(author_id,title,description,category,created_at) VALUES (?,?,?,?,?)", (author_id, title, description, category, now())).lastrowid
def get_idea(iid):
    with get_conn() as c: return c.execute("SELECT * FROM ideas WHERE id=?", (iid,)).fetchone()
def list_ideas(status="approved", sort="votes", limit=20):
    order = "votes_up DESC, created_at DESC" if sort == "votes" else "created_at DESC"
    with get_conn() as c:
        if status == "all": return c.execute(f"SELECT * FROM ideas ORDER BY {order} LIMIT ?", (limit,)).fetchall()
        return c.execute(f"SELECT * FROM ideas WHERE status=? ORDER BY {order} LIMIT ?", (status, limit)).fetchall()
def vote_idea(idea_id, user_id, vote_type):
    with get_conn() as c:
        existing = c.execute("SELECT * FROM idea_votes WHERE idea_id=? AND user_id=?", (idea_id, user_id)).fetchone()
        if existing:
            if existing["vote_type"] == vote_type: return False
            col_old = "votes_up" if existing["vote_type"] == "up" else "votes_down"
            col_new = "votes_up" if vote_type == "up" else "votes_down"
            c.execute(f"UPDATE ideas SET {col_old}={col_old}-1, {col_new}={col_new}+1 WHERE id=?", (idea_id,))
            c.execute("UPDATE idea_votes SET vote_type=?, created_at=? WHERE id=?", (vote_type, now(), existing["id"]))
            return True
        c.execute("INSERT INTO idea_votes(idea_id,user_id,vote_type,created_at) VALUES (?,?,?,?)", (idea_id, user_id, vote_type, now()))
        col = "votes_up" if vote_type == "up" else "votes_down"
        c.execute(f"UPDATE ideas SET {col}={col}+1 WHERE id=?", (idea_id,))
        return True
def get_user_vote(idea_id, user_id):
    with get_conn() as c:
        r = c.execute("SELECT vote_type FROM idea_votes WHERE idea_id=? AND user_id=?", (idea_id, user_id)).fetchone()
        return r["vote_type"] if r else None
def set_idea_status(idea_id, status, admin_id):
    with get_conn() as c: c.execute("UPDATE ideas SET status=?, approved_at=?, approved_by=? WHERE id=?", (status, now(), admin_id, idea_id))
def add_idea_comment(idea_id, user_id, content):
    with get_conn() as c: return c.execute("INSERT INTO idea_comments(idea_id,user_id,content,created_at) VALUES (?,?,?,?)", (idea_id, user_id, content, now())).lastrowid
def list_idea_comments(idea_id, limit=20):
    with get_conn() as c: return c.execute("SELECT c.*, m.full_name AS author_name FROM idea_comments c LEFT JOIN members m ON m.telegram_id = c.user_id WHERE c.idea_id=? ORDER BY c.created_at ASC LIMIT ?", (idea_id, limit)).fetchall()
def list_pending_ideas():
    with get_conn() as c: return c.execute("SELECT * FROM ideas WHERE status='pending' ORDER BY created_at ASC").fetchall()
def stats_overview():
    with get_conn() as c:
        members = c.execute("SELECT COUNT(*) AS c FROM members").fetchone()["c"]
        total_points = c.execute("SELECT COALESCE(SUM(points),0) AS s FROM members").fetchone()["s"]
        avg_points = round(total_points / members, 1) if members else 0
        month_start = datetime.utcnow().strftime("%Y-%m-01T00:00:00")
        active_this_month = c.execute("SELECT COUNT(DISTINCT member_id) AS c FROM points_log WHERE created_at>=?", (month_start,)).fetchone()["c"]
        join_pending = c.execute("SELECT COUNT(*) AS c FROM join_requests WHERE status='pending'").fetchone()["c"]
        msgs_open = c.execute("SELECT COUNT(*) AS c FROM messages WHERE status IN ('new','in_progress')").fetchone()["c"]
        ideas_total = c.execute("SELECT COUNT(*) AS c FROM ideas").fetchone()["c"]
        return {"members": members, "total_points": total_points, "avg_points": avg_points, "active_this_month": active_this_month, "join_pending": join_pending, "msgs_open": msgs_open, "ideas_total": ideas_total}
def stats_level_distribution():
    with get_conn() as c: rows = c.execute("SELECT points FROM members").fetchall()
    dist = {}
    for r in rows:
        lvl = level_for(r["points"]); dist[lvl] = dist.get(lvl, 0) + 1
    return dist
def stats_top_members(limit=10):
    with get_conn() as c: return c.execute("SELECT full_name, points FROM members ORDER BY points DESC LIMIT ?", (limit,)).fetchall()
def stats_activity_last_months(months=6):
    with get_conn() as c: rows = c.execute("SELECT substr(created_at,1,7) AS ym, COUNT(*) AS cnt, SUM(points) AS total FROM points_log GROUP BY ym ORDER BY ym DESC LIMIT ?", (months,)).fetchall()
    return list(reversed(rows))

def create_announcement(title, content, category, media_type=None, media_file_id=None, link=None, publish_at=None, created_by=None, status="draft"):
    with get_conn() as c:
        cur = c.execute("INSERT INTO announcements(title,content,category,media_type,media_file_id,link,status,publish_at,created_by,created_at) VALUES (?,?,?,?,?,?,?,?,?,?)", (title, content, category, media_type, media_file_id, link, status, publish_at, created_by, now()))
        return cur.lastrowid

def get_announcement(aid):
    with get_conn() as c:
        return c.execute("SELECT * FROM announcements WHERE id=?", (aid,)).fetchone()

def mark_published(aid):
    with get_conn() as c:
        c.execute("UPDATE announcements SET status='published', published_at=? WHERE id=?", (now(), aid))

def list_announcements(category=None, limit=10):
    with get_conn() as c:
        if category:
            return c.execute("SELECT * FROM announcements WHERE status='published' AND category=? ORDER BY published_at DESC LIMIT ?", (category, limit)).fetchall()
        return c.execute("SELECT * FROM announcements WHERE status='published' ORDER BY published_at DESC LIMIT ?", (limit,)).fetchall()

def list_pending_scheduled():
    with get_conn() as c:
        return c.execute("SELECT * FROM announcements WHERE status='scheduled'").fetchall()
