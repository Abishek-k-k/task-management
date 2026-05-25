"""
One-shot reminder script — called by GitHub Actions every day.
No infinite loop needed; GitHub handles the scheduling.
"""
import sqlite3
import smtplib
import os
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date

# Credentials come from GitHub Actions secrets (or fall back to hardcoded)
GMAIL_SENDER  = os.environ.get("GMAIL_SENDER",  "a20114466@gmail.com")
GMAIL_APP_PWD = os.environ.get("GMAIL_APP_PWD", "jfir zpvm elbe wntp")

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s  %(levelname)s  %(message)s")
log = logging.getLogger(__name__)


def get_all_users_with_due_tasks():
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
                WHERE user_id=? AND due=? AND status='Pending'
            """, (user["user_id"], today))
            tasks = [dict(row) for row in cur.fetchall()]
            if tasks:
                result.append({"username": user["username"],
                               "email":    user["email"],
                               "tasks":    tasks})
        con.close()
        return result
    except Exception as e:
        log.error(f"DB error: {e}")
        return []


def build_email_html(username, tasks):
    rows = ""
    for t in tasks:
        color = {"High":"#f87171","Medium":"#fbbf24","Low":"#34d399"}.get(t["priority"],"#aaa")
        rows += (f'<tr>'
                 f'<td style="padding:10px 12px;border-bottom:1px solid #1e1e28;color:#e8e8f0">{t["name"]}</td>'
                 f'<td style="padding:10px 12px;border-bottom:1px solid #1e1e28;color:#8888aa">{t["desc"] or "—"}</td>'
                 f'<td style="padding:10px 12px;border-bottom:1px solid #1e1e28;color:{color};font-weight:700">{t["priority"]}</td>'
                 f'<td style="padding:10px 12px;border-bottom:1px solid #1e1e28;color:#8888aa">{t["due"]}</td>'
                 f'</tr>')
    return f"""
    <html><body style="background:#0d0d0f;margin:0;padding:32px;font-family:'Segoe UI',sans-serif;">
      <div style="max-width:560px;margin:auto">
        <div style="margin-bottom:32px">
          <span style="font-size:22px;font-weight:800;color:#fff">Task<span style="color:#a78bfa">flow</span></span>
        </div>
        <div style="background:#111116;border:1px solid #1e1e28;border-radius:16px;overflow:hidden">
          <div style="padding:28px 32px;border-bottom:1px solid #1e1e28">
            <p style="margin:0 0 6px;font-size:13px;color:#a78bfa;font-weight:600;text-transform:uppercase">Daily Reminder</p>
            <h2 style="margin:0;font-size:22px;color:#fff">You have {len(tasks)} task(s) due today</h2>
            <p style="margin:8px 0 0;font-size:13px;color:#555566">Hi {username} — {date.today().strftime('%A, %B %d %Y')}</p>
          </div>
          <table style="width:100%;border-collapse:collapse">
            <thead><tr style="background:#0d0d0f">
              <th style="padding:10px 12px;text-align:left;font-size:10px;color:#444455;text-transform:uppercase">Task</th>
              <th style="padding:10px 12px;text-align:left;font-size:10px;color:#444455;text-transform:uppercase">Desc</th>
              <th style="padding:10px 12px;text-align:left;font-size:10px;color:#444455;text-transform:uppercase">Priority</th>
              <th style="padding:10px 12px;text-align:left;font-size:10px;color:#444455;text-transform:uppercase">Due</th>
            </tr></thead>
            <tbody>{rows}</tbody>
          </table>
          <div style="padding:24px 32px">
            <p style="margin:0;font-size:12px;color:#444455">Login to Taskflow to mark tasks complete.</p>
          </div>
        </div>
      </div>
    </body></html>"""


def send_email(to_email, username, tasks):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"⏰ {len(tasks)} task(s) due today — Taskflow"
        msg["From"]    = f"Taskflow <{GMAIL_SENDER}>"
        msg["To"]      = to_email
        msg.attach(MIMEText(build_email_html(username, tasks), "html"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(GMAIL_SENDER, GMAIL_APP_PWD)
            s.sendmail(GMAIL_SENDER, to_email, msg.as_string())
        return True
    except Exception as e:
        log.error(f"Failed to send to {to_email}: {e}")
        return False


if __name__ == "__main__":
    log.info("=== One-shot daily reminder ===")
    users = get_all_users_with_due_tasks()
    if not users:
        log.info("No users have tasks due today.")
    else:
        for u in users:
            log.info(f"Sending to {u['username']} ({u['email']}) — {len(u['tasks'])} task(s)")
            ok = send_email(u["email"], u["username"], u["tasks"])
            log.info("  ✅ Sent" if ok else "  ❌ Failed")
    log.info("=== Done ===")
