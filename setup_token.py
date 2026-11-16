"""
setup_token.py — إدخال التوكن بشكل آمن.

عند الكتابة لن تظهر الحروف على الشاشة (مثل كلمة السر)،
ويُحفظ التوكن في ملف .env على جهازك فقط.
"""
import getpass
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parent / ".env"


def main() -> None:
    print("=== إعداد بوت أسترونوفا ===\n")
    token = getpass.getpass("الصق التوكن هنا (لن يظهر أثناء الكتابة) ثم اضغط Enter: ").strip()
    if ":" not in token or len(token) < 30:
        print("❌ هذا لا يبدو توكن صحيحاً. انسخه من @BotFather كاملاً وحاول مجدداً.")
        return

    owner = input("أدخل رقم Telegram ID الخاص بك (رئيس النادي) ثم Enter: ").strip()
    if not owner.isdigit():
        print("❌ المعرّف يجب أن يكون أرقاماً فقط (يمكنك معرفته من بوت @userinfobot).")
        return

    ENV_PATH.write_text(f"BOT_TOKEN={token}\nOWNER_ID={owner}\n", encoding="utf-8")
    try:
        ENV_PATH.chmod(0o600)
    except OSError:
        pass
    print("\n✅ تم حفظ الإعدادات في ملف .env")
    print("   الآن شغّل البوت بالأمر:  python main.py")


if __name__ == "__main__":
    main()
