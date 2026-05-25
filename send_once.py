import sqlite3, smtplib, os, logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date

GMAIL_SENDER  = os.environ.get("GMAIL_SENDER",  "a20114466@gmail.com")
GMAIL_APP_PWD = os.environ.get("GMAIL_APP_PWD", "jfir zpvm elbe wntp")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

def get_users():
    today = str(date.today())
    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT user_id, username, email FROM users")
    result = []
    for u in cur.fetchall():
        cur.execute("SELECT name, desc, priority, due FROM list_new_new WHERE user_id=? AND due=? AND status='Pending'", (u["user_id"], today))
        tasks = [dict(r) for r in cur.fetchall()]
        if tasks:
            result.append({"username": u["username"], "email": u["email"], "tasks": tasks})
    con.close()
    return result

def send(to, username, tasks):
    rows = "".join(
        f'<tr><td style="padding:8px;color:#eee">{t["name"]}</td>'
        f'<td style="padding:8px;color:#aaa">{t["priority"]}</td>'
        f'<td style="padding:8px;color:#aaa">{t["due"]}</td></tr>'
        for t in tasks
    )
    html = (f'<html><body style="background:#0d0d0f;font-family:sans-serif;padding:32px">'
            f'<div style="max-width:500px;margin:auto;background:#111116;border-radius:16px;padding:32px">'
            f'<h2 style="color:#fff">Hi {username}, you have {len(tasks)} task(s) due today</h2>'
            f'<table style="width:100%;border-collapse:collapse">'
            f'<thead><tr><th style="text-align:left;color:#555;padding:8px">Task</th>'
            f'<th style="text-align:left;color:#555;padding:8px">Priority</th>'
            f'<th style="text-align:left;color:#555;padding:8px">Due</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div></body></html>')
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"⏰ {len(tasks)} task(s) due today — Taskflow"
        msg["From"]    = f"Taskflow <{GMAIL_SENDER}>"
        msg["To"]      = to
        msg.attach(MIMEText(html, "html"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(GMAIL_SENDER, GMAIL_APP_PWD)
            s.sendmail(GMAIL_SENDER, to, msg.as_string())
        return True
    except Exception as e:
        log.error(e)
        return False

if __name__ == "__main__":
    for u in get_users():
        ok = send(u["email"], u["username"], u["tasks"])
        log.info(f"{'✅' if ok else '❌'} {u['username']}")
