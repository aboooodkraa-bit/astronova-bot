"""
permissions.py — الأدوار والصلاحيات.

كل صلاحية مرتبطة بمعرّف Telegram ID المخزن في جدول admins.
"""

PRESIDENT = "president"
VICE_PRESIDENT = "vice_president"
SECTION_HEAD = "section_head"
ACTIVITY_HEAD = "activity_head"

ROLE_NAMES_AR = {
    PRESIDENT: "رئيس النادي",
    VICE_PRESIDENT: "نائب الرئيس",
    SECTION_HEAD: "مسؤول قسم",
    ACTIVITY_HEAD: "مسؤول أنشطة",
}

# أسماء الصلاحيات
MANAGE_ADMINS = "manage_admins"
MANAGE_MEMBERS = "manage_members"
MANAGE_ACTIVITIES = "manage_activities"
MANAGE_ATTENDANCE = "manage_attendance"
MANAGE_POINTS = "manage_points"
MANAGE_ANNOUNCEMENTS = "manage_announcements"
VIEW_STATS = "view_stats"
REPLY_MESSAGES = "reply_messages"

ROLE_PERMISSIONS = {
    PRESIDENT: {
        MANAGE_ADMINS, MANAGE_MEMBERS, MANAGE_ACTIVITIES, MANAGE_ATTENDANCE,
        MANAGE_POINTS, MANAGE_ANNOUNCEMENTS, VIEW_STATS, REPLY_MESSAGES,
    },
    VICE_PRESIDENT: {
        MANAGE_MEMBERS, MANAGE_ACTIVITIES, MANAGE_ATTENDANCE,
        MANAGE_POINTS, MANAGE_ANNOUNCEMENTS, VIEW_STATS, REPLY_MESSAGES,
    },
    SECTION_HEAD: {
        MANAGE_MEMBERS, VIEW_STATS, REPLY_MESSAGES,
    },
    ACTIVITY_HEAD: {
        MANAGE_ACTIVITIES, MANAGE_ATTENDANCE, VIEW_STATS,
    },
}


def has_permission(role: str | None, permission: str) -> bool:
    if not role:
        return False
    return permission in ROLE_PERMISSIONS.get(role, set())
