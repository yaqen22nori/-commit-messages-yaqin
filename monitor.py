import time
import requests
import re

# ===== إعدادات التليجرام =====
bot_token = "8655043920:AAHs1uenSdo5P0c-OSY_FNLxA4g9euSZ8J8"
chat_id = "784582542"

# ===== إعدادات GitHub =====
username = "r8oth"
repo = "-commit-messages-yaqin"

last_commit = None

def send_telegram(message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("✅ الرسالة أرسلت بنجاح للتليجرام")
        else:
            print("❌ فشل إرسال الرسالة:", response.text)
    except Exception as e:
        print("خطأ بإرسال رسالة التليجرام:", e)

send_telegram("🔍 بدأت مراقبة المستودع على GitHub")
print("بدأت مراقبة المستودع...")

while True:
    time.sleep(10)

    try:
        commits_url = f"https://api.github.com/repos/{username}/{repo}/commits"
        r = requests.get(commits_url).json()

        if isinstance(r, list) and len(r) > 0:
            commit = r[0]["sha"]
            message = r[0]["commit"]["message"]

            if last_commit is None:
                last_commit = commit
            elif commit != last_commit:
                diff_url = f"https://api.github.com/repos/{username}/{repo}/commits/{commit}"
                commit_detail = requests.get(diff_url).json()
                files_changed = commit_detail.get("files", [])

                msg_lines = [f"🚨 هناك تعديل جديد على GitHub:\n{message}\n"]

                hunk_pattern = re.compile(r'^@@ -(\d+),\d+ \+(\d+),\d+ @@')
                
                for f in files_changed:
                    filename = f.get("filename")
                    patch = f.get("patch")
                    if patch:
                        msg_lines.append(f"📄 {filename}:")
                        lines = patch.splitlines()
                        old_line_num = 0
                        new_line_num = 0
                        for line in lines:
                            hunk = hunk_pattern.match(line)
                            if hunk:
                                old_line_num = int(hunk.group(1))
                                new_line_num = int(hunk.group(2))
                                continue
                            if line.startswith("-"):
                                msg_lines.append(f"❌ سطر {old_line_num}: {line[1:].strip()}")
                                old_line_num += 1
                            elif line.startswith("+"):
                                msg_lines.append(f"➕ سطر {new_line_num}: {line[1:].strip()}")
                                new_line_num += 1
                            else:
                                old_line_num += 1
                                new_line_num += 1

                send_telegram("\n".join(msg_lines))
                print("\n".join(msg_lines))
                last_commit = commit
        else:
            print("❌ لم أستطع الحصول على commits من GitHub")
    except Exception as e:
        print("خطأ بمراقبة GitHub:", e)
