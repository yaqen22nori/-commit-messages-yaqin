import time
import difflib
import requests

# إعدادات التليجرام
bot_token = "8655043920:AAHs1uenSdo5P0c-OSY_FNLxA4g9euSZ8J8"
chat_id = "784582542"  # رقم محادثتك مع البوت

# إعدادات GitHub
username = "username"  # غيره باسم حسابك
repo = "MyPythonProject"  # اسم المستودع

# ملف محلي للمراقبة
file_path = "/storage/emulated/0/Download/MyPythonProject/test.py"

# دالة لإرسال رسالة على التليجرام
def send_telegram(message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("خطأ بإرسال رسالة التلغرام:", e)

# دالة قراءة الملف المحلي
def read_file():
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.readlines()
    except FileNotFoundError:
        print(f"⚠️ الملف {file_path} مو موجود!")
        return []

# قراءة الملف المحلي لأول مرة
old_lines = read_file()
send_telegram("بدأت مراقبة الملف 🔍")
print("بدأت مراقبة الملف...")

# تذكر آخر commit من GitHub
last_commit = None

while True:
    time.sleep(5)  # كل 5 ثواني

    # ===== مراقبة الملف المحلي =====
    new_lines = read_file()
    diff = difflib.ndiff(old_lines, new_lines)
    line_number = 0

    for line in diff:
        if line.startswith("  "):
            line_number += 1
        elif line.startswith("- "):
            msg = f"❌ حذف في السطر {line_number + 1}: {line[2:].strip()}"
            print(msg)
            send_telegram(msg)
            line_number += 1
        elif line.startswith("+ "):
            msg = f"➕ إضافة في السطر {line_number + 1}: {line[2:].strip()}"
            print(msg)
            send_telegram(msg)
            line_number += 1

    old_lines = new_lines

    # ===== مراقبة GitHub =====
    try:
        url = f"https://api.github.com/repos/{username}/{repo}/commits"
        r = requests.get(url).json()
        commit = r[0]["sha"]

        if last_commit is None:
            last_commit = commit
        elif commit != last_commit:
            msg = f"🚨 هناك تعديل جديد على GitHub: {r[0]['commit']['message']}"
            send_telegram(msg)
            last_commit = commit
    except Exception as e:
        print("خطأ بمراقبة GitHub:", e)
