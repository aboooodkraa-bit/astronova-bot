# بوت نادي أسترونوفا العلمي 🚀

## وظيفة كل ملف

| الملف | وظيفته |
|---|---|
| `main.py` | تشغيل البوت وربط الأوامر والأزرار والسجلات |
| `config.py` | قراءة الإعدادات والأسرار من ملف `.env` |
| `database.py` | قاعدة بيانات SQLite (كل الجداول جاهزة) |
| `permissions.py` | أدوار الإدارة وصلاحياتها |
| `keyboards.py` | الأزرار التفاعلية |
| `texts.py` | كل النصوص العربية (سهلة التعديل) |
| `handlers/start.py` | /start والقائمة الرئيسية |
| `setup_token.py` | إدخال التوكن بشكل آمن (لا يظهر على الشاشة) |
| `requirements.txt` | المكتبات المطلوبة |
| `.env.example` | مثال فقط للإعدادات |

## التشغيل على أندرويد (Termux)

1. ثبّت **Termux** من متجر **F-Droid** (نسخة Google Play قديمة ولا تعمل جيداً).
2. افتح Termux ونفّذ:
   ```
   pkg update -y && pkg install -y python unzip
   ```
3. انسخ ملف المشروع `astronova_bot.zip` إلى الهاتف، ثم في Termux:
   ```
   termux-setup-storage
   cp ~/storage/downloads/astronova_bot.zip ~/
   unzip astronova_bot.zip
   cd astronova_bot
   ```
4. ثبّت المكتبة:
   ```
   pip install -r requirements.txt
   ```
5. أدخل التوكن بشكل آمن (لن تظهر الحروف أثناء اللصق):
   ```
   python setup_token.py
   ```
   - التوكن: تحصل عليه من @BotFather (أو من `/token` لبوتك).
   - رقم Telegram ID الخاص بك: أرسل أي رسالة إلى @userinfobot.
6. شغّل البوت:
   ```
   python main.py
   ```
7. افتح البوت في تلغرام وأرسل `/start`.

لإيقاف البوت اضغط `Ctrl + C`.
