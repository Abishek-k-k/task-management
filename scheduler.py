import sqlite3
import smtplib
import schedule
import time
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date

GMAIL_SENDER  = "a20114466@gmail.com"
GMAIL_APP_PWD = "jfir zpvm elbe wntp"
SEND_TIME = "14:15"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
log = logging.getLogger(__name__)

def get_all_users_with_due_tasks() -> list[dict]:
    today = str(date.today())
    try:
        con = sqlite3.connect("database.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT user_id, username, email FROM users")
        users = cur.fetchall()
        result = []
        for user in users:
            cur.execute("""
                SELECT name, desc, priority, due
                FROM list_new_new
                WHERE user_id = ? AND due = ? AND status = 'Pending'
            """, (user["user_id"], today))
            tasks = [dict(row) for row in cur.fetchall()]
            if tasks:
                result.append({
                    "user_id":  user["user_id"],
                    "username": user["username"],
                    "email":    user["email"],
                    "tasks":    tasks
                })
        con.close()
        return result
    except Exception as e:
        log.error(f"DB error: {e}")
        return []

def build_email_html(username: str, tasks: list) -> str:
    rows = ""
    for t in tasks:
        color = {"High": "#e74c3c", "Medium": "#f39c12", "Low": "#27ae60"}.get(t["priority"], "#555")
        rows += f"""
        <tr>
          <td style="padding:8px;border:1px solid #ddd;">{t['name']}</td>
          <td style="padding:8px;border:1px solid #ddd;">{t['desc'] or '—'}</td>
          <td style="padding:8px;border:1px solid #ddd;color:{color};font-weight:bold;">{t['priority']}</td>
          <td style="padding:8px;border:1px solid #ddd;">{t['due']}</td>
        </tr>"""
    return f"""
    <html><body style="font-family:Arial,sans-serif;background:#f4f4f4;padding:20px;">
      <div style="max-width:600px;margin:auto;background:#fff;border-radius:8px;
                  box-shadow:0 2px 8px rgba(0,0,0,0.1);overflow:hidden;">
        <div style="background:#4A90D9;padding:24px 32px;">
          <h1 style="color:#fff;margin:0;font-size:22px;">📋 Task Due Reminder</h1>
        </div>
        <div style="padding:24px 32px;">
          <p style="font-size:16px;">Hi <strong>{username}</strong>,</p>
          <p style="color:#555;">These task(s) are <strong>due today</strong>
             ({date.today().strftime('%B %d, %Y')}). Please take action!</p>
          <table style="width:100%;border-collapse:collapse;margin-top:12px;">
            <thead>
              <tr style="background:#4A90D9;color:#fff;">
                <th style="padding:10px;text-align:left;">Task</th>
                <th style="padding:10px;text-align:left;">Description</th>
                <th style="padding:10px;text-align:left;">Priority</th>
                <th style="padding:10px;text-align:left;">Due Date</th>
              </tr>
            </thead>
            <tbody>{rows}</tbody>
          </table>
          <p style="margin-top:20px;color:#888;font-size:13px;">
            Login to your TODO app to mark them complete.
          </p>
        </div>
        <div style="background:#f0f0f0;padding:12px 32px;text-align:center;
                    color:#aaa;font-size:12px;">
          TODO App — Automated Daily Reminder
        </div>
      </div>
    </body></html>"""

def send_email(to_email: str, username: str, tasks: list) -> bool:
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"⏰ You have {len(tasks)} task(s) due today!"
        msg["From"]    = f"TODO App <{GMAIL_SENDER}>"
        msg["To"]      = to_email
        msg.attach(MIMEText(build_email_html(username, tasks), "html"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_SENDER, GMAIL_APP_PWD)
            server.sendmail(GMAIL_SENDER, to_email, msg.as_string())
        return True
    except Exception as e:
        log.error(f"Failed to send to {to_email}: {e}")
        return False

def send_daily_reminders():
    log.info("=== Daily reminder job started ===")
    users = get_all_users_with_due_tasks()
    if not users:
        log.info("No users have tasks due today. Nothing to send.")
        return
    sent = 0
    failed = 0
    for user in users:
        log.info(f"Sending to {user['username']} ({user['email']}) — {len(user['tasks'])} task(s)")
        ok = send_email(user["email"], user["username"], user["tasks"])
        if ok:
            log.info(f"  ✅ Sent successfully")
            sent += 1
        else:
            log.warning(f"  ❌ Failed")
            failed += 1
    log.info(f"=== Done: {sent} sent, {failed} failed ===")

if __name__ == "__main__":
    log.info(f"Scheduler started. Will send reminders daily at {SEND_TIME}.")
    log.info(f"Watching database: database.db")
    schedule.every().day.at(SEND_TIME).do(send_daily_reminders)
    while True:
        schedule.run_pending()
        time.sleep(30)
