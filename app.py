import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import hashlib
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date, timedelta, datetime

GMAIL_SENDER  = "a20114466@gmail.com"
GMAIL_APP_PWD = "jfir zpvm elbe wntp"
APP_NAME = "Taskflow"

def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif !important; }
    .stApp { background: #0d0d0f !important; color: #e8e8f0 !important; }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding: 0 !important; max-width: 100% !important; }
    [data-testid="stSidebar"] { background: #111116 !important; border-right: 1px solid #1e1e28 !important; width: 260px !important; }
    [data-testid="stSidebar"] > div { padding: 0 !important; }
    .sidebar-brand { padding: 28px 24px 20px; border-bottom: 1px solid #1e1e28; margin-bottom: 8px; }
    .sidebar-brand h1 { font-size: 20px !important; font-weight: 700 !important; color: #fff !important; margin: 0 !important; letter-spacing: -0.5px; }
    .sidebar-brand p { font-size: 12px !important; color: #555566 !important; margin: 2px 0 0 !important; }
    .nav-section { padding: 4px 12px; font-size: 10px; font-weight: 600; color: #444455; text-transform: uppercase; letter-spacing: 1px; margin: 12px 0 4px; }
    .nav-item { display: flex; align-items: center; gap: 10px; padding: 8px 16px; border-radius: 8px; margin: 1px 8px; font-size: 13px; color: #8888aa; cursor: pointer; transition: all 0.15s; }
    .nav-item:hover { background: #1a1a24; color: #e8e8f0; }
    .nav-item.active { background: #1e1e2e; color: #a78bfa; font-weight: 600; }
    .nav-dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; }
    .user-card { position: absolute; bottom: 0; left: 0; right: 0; padding: 16px; border-top: 1px solid #1e1e28; display: flex; align-items: center; gap: 12px; background: #111116; }
    .user-avatar { width: 32px; height: 32px; border-radius: 10px; background: linear-gradient(135deg, #a78bfa, #60a5fa); display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 700; color: white; flex-shrink: 0; }
    .user-name { font-size: 13px; font-weight: 600; color: #e8e8f0; }
    .user-email { font-size: 11px; color: #555566; }
    .main-content { padding: 40px 48px; max-width: 900px; }
    .page-header { margin-bottom: 32px; }
    .page-header h2 { font-size: 28px !important; font-weight: 700 !important; color: #fff !important; margin: 0 0 4px !important; letter-spacing: -0.5px; }
    .page-header p { font-size: 14px; color: #555566; margin: 0; }
    .stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 32px; }
    .stat-card { background: #111116; border: 1px solid #1e1e28; border-radius: 12px; padding: 20px; transition: border-color 0.2s; }
    .stat-card:hover { border-color: #2e2e44; }
    .stat-label { font-size: 11px; font-weight: 600; color: #444455; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 8px; }
    .stat-value { font-size: 32px; font-weight: 700; color: #fff; font-family: 'JetBrains Mono', monospace; line-height: 1; }
    .stat-sub { font-size: 11px; color: #555566; margin-top: 4px; }
    .stat-card.purple .stat-value { color: #a78bfa; }
    .stat-card.blue   .stat-value { color: #60a5fa; }
    .stat-card.green  .stat-value { color: #34d399; }
    .stat-card.amber  .stat-value { color: #fbbf24; }
    .task-list { display: flex; flex-direction: column; gap: 1px; }
    .task-card { background: #111116; border: 1px solid #1e1e28; border-radius: 10px; padding: 14px 18px; display: flex; align-items: center; gap: 14px; transition: all 0.15s; margin-bottom: 4px; }
    .task-card:hover { border-color: #2e2e44; background: #141420; transform: translateX(2px); }
    .task-card.due-today { border-left: 3px solid #f87171 !important; }
    .task-checkbox { width: 18px; height: 18px; border: 2px solid #333344; border-radius: 5px; flex-shrink: 0; cursor: pointer; transition: all 0.15s; }
    .task-checkbox.done { background: #34d399; border-color: #34d399; }
    .task-name { font-size: 14px; font-weight: 500; color: #e8e8f0; flex: 1; }
    .task-name.done { text-decoration: line-through; color: #444455; }
    .task-desc { font-size: 12px; color: #555566; }
    .badge { display: inline-flex; align-items: center; gap: 4px; padding: 3px 8px; border-radius: 5px; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
    .badge-high   { background: #2d1515; color: #f87171; border: 1px solid #3d1818; }
    .badge-medium { background: #2d2010; color: #fbbf24; border: 1px solid #3d2c12; }
    .badge-low    { background: #0d2d1a; color: #34d399; border: 1px solid #0f3d22; }
    .badge-done   { background: #1a1a2e; color: #6666aa; border: 1px solid #2a2a3e; }
    .due-chip { font-size: 11px; color: #555566; font-family: 'JetBrains Mono', monospace; white-space: nowrap; }
    .due-chip.overdue { color: #f87171; }
    .due-chip.today   { color: #fbbf24; }
    .stTextInput > div > div > input, .stTextArea > div > div > textarea, .stSelectbox > div > div, .stDateInput > div > div > input { background: #111116 !important; border: 1px solid #1e1e28 !important; border-radius: 8px !important; color: #e8e8f0 !important; font-family: 'Plus Jakarta Sans', sans-serif !important; }
    .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus { border-color: #a78bfa !important; box-shadow: 0 0 0 3px rgba(167,139,250,0.1) !important; }
    label, .stTextInput label, .stSelectbox label { color: #8888aa !important; font-size: 12px !important; font-weight: 600 !important; text-transform: uppercase; letter-spacing: 0.6px; }
    .stButton > button { background: #a78bfa !important; color: #0d0d0f !important; border: none !important; border-radius: 8px !important; font-weight: 700 !important; font-size: 13px !important; font-family: 'Plus Jakarta Sans', sans-serif !important; padding: 8px 20px !important; transition: all 0.15s !important; letter-spacing: 0.3px; }
    .stButton > button:hover { background: #c4b5fd !important; transform: translateY(-1px); box-shadow: 0 4px 16px rgba(167,139,250,0.3) !important; }
    .stButton > button:active { transform: translateY(0) !important; }
    .danger-btn .stButton > button { background: #2d1515 !important; color: #f87171 !important; border: 1px solid #3d1818 !important; }
    .danger-btn .stButton > button:hover { background: #f87171 !important; color: #0d0d0f !important; box-shadow: 0 4px 16px rgba(248,113,113,0.3) !important; }
    .ghost-btn .stButton > button { background: transparent !important; color: #8888aa !important; border: 1px solid #1e1e28 !important; }
    .ghost-btn .stButton > button:hover { background: #1a1a24 !important; color: #e8e8f0 !important; box-shadow: none !important; }
    .stSuccess, .stInfo, .stWarning, .stError { border-radius: 8px !important; border: none !important; font-size: 13px !important; }
    .stSuccess { background: #0d2d1a !important; color: #34d399 !important; }
    .stInfo    { background: #0d1e2d !important; color: #60a5fa !important; }
    .stWarning { background: #2d2010 !important; color: #fbbf24 !important; }
    .stError   { background: #2d1515 !important; color: #f87171 !important; }
    .stDataFrame { border: 1px solid #1e1e28 !important; border-radius: 10px !important; overflow: hidden; }
    hr { border-color: #1e1e28 !important; }
    [data-testid="metric-container"] { background: #111116; border: 1px solid #1e1e28; border-radius: 12px; padding: 16px 20px; }
    [data-testid="metric-container"] label { color: #555566 !important; font-size: 11px !important; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] { color: #fff !important; font-family: 'JetBrains Mono', monospace !important; font-size: 28px !important; }
    .stSelectbox [data-baseweb="select"] > div { background: #111116 !important; border-color: #1e1e28 !important; }
    .stDateInput [data-baseweb="input"] { background: #111116 !important; border-color: #1e1e28 !important; }
    .js-plotly-plot { border-radius: 12px; overflow: hidden; }
    .auth-container { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: #0d0d0f; }
    .auth-box { width: 400px; background: #111116; border: 1px solid #1e1e28; border-radius: 16px; padding: 40px; }
    .auth-logo { font-size: 24px; font-weight: 800; color: #fff; letter-spacing: -1px; margin-bottom: 4px; }
    .auth-logo span { color: #a78bfa; }
    .auth-sub { font-size: 13px; color: #555566; margin-bottom: 32px; }
    .section-header { display: flex; align-items: center; gap: 10px; margin-bottom: 16px; }
    .section-header h3 { font-size: 16px !important; font-weight: 600 !important; color: #e8e8f0 !important; margin: 0 !important; }
    .section-count { background: #1e1e28; color: #8888aa; font-size: 11px; font-weight: 700; padding: 2px 7px; border-radius: 10px; font-family: 'JetBrains Mono', monospace; }
    .empty-state { text-align: center; padding: 60px 20px; color: #333344; }
    .empty-state .icon { font-size: 40px; margin-bottom: 12px; }
    .empty-state p { font-size: 14px; }
    .day-block { background: #111116; border: 1px solid #1e1e28; border-radius: 12px; padding: 20px; margin-bottom: 12px; }
    .day-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
    .day-name { font-size: 13px; font-weight: 700; color: #e8e8f0; }
    .day-date { font-size: 11px; color: #555566; font-family: 'JetBrains Mono', monospace; }
    .day-count { font-size: 11px; font-weight: 700; color: #a78bfa; background: #1e1e2e; padding: 2px 8px; border-radius: 10px; font-family: 'JetBrains Mono', monospace; }
    .progress-bar { height: 4px; background: #1e1e28; border-radius: 2px; overflow: hidden; margin-top: 8px; }
    .progress-fill { height: 100%; border-radius: 2px; background: linear-gradient(90deg, #a78bfa, #60a5fa); transition: width 0.3s ease; }
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #1e1e28; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #2e2e44; }
    [data-testid="stSidebar"] .stSelectbox > div > div { background: #1a1a24 !important; border-color: #2e2e44 !important; color: #a78bfa !important; font-size: 13px !important; }
    .stTabs [data-baseweb="tab-list"] { background: transparent !important; border-bottom: 1px solid #1e1e28 !important; gap: 0 !important; }
    .stTabs [data-baseweb="tab"] { background: transparent !important; color: #555566 !important; font-size: 13px !important; font-weight: 600 !important; padding: 10px 18px !important; border-bottom: 2px solid transparent !important; }
    .stTabs [aria-selected="true"] { color: #a78bfa !important; border-bottom-color: #a78bfa !important; }
    .form-card { background: #111116; border: 1px solid #1e1e28; border-radius: 14px; padding: 28px; margin-bottom: 24px; }
    .week-task-row { display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid #1a1a24; }
    .week-task-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
    .week-task-name { font-size: 13px; color: #e8e8f0; flex: 1; }
    .week-task-name.done { text-decoration: line-through; opacity: 0.5; }
    .week-task-priority { font-size: 11px; font-weight: 700; text-transform: uppercase; }
    .week-no-tasks { font-size: 12px; color: #333344; padding: 8px 0; margin: 0; }
    </style>
    """, unsafe_allow_html=True)

def init_db():
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id  INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email    TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS list_new_new (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id  INTEGER NOT NULL,
            name     TEXT NOT NULL,
            desc     TEXT,
            priority TEXT NOT NULL,
            status   TEXT NOT NULL,
            created  TEXT,
            due      TEXT,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    """)
    con.commit()
    con.close()

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def get_user_email(uid):
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("SELECT email FROM users WHERE user_id=?", (uid,))
    row = cur.fetchone()
    con.close()
    return row[0] if row else None

def build_email_html(username, tasks):
    rows = ""
    for t in tasks:
        color = {"High":"#f87171","Medium":"#fbbf24","Low":"#34d399"}.get(t["priority"],"#aaa")
        rows += f"""
        <tr>
          <td style="padding:10px 12px;border-bottom:1px solid #1e1e28;color:#e8e8f0">{t['name']}</td>
          <td style="padding:10px 12px;border-bottom:1px solid #1e1e28;color:#8888aa">{t['desc'] or '—'}</td>
          <td style="padding:10px 12px;border-bottom:1px solid #1e1e28;color:{color};font-weight:700;font-size:11px;text-transform:uppercase">{t['priority']}</td>
          <td style="padding:10px 12px;border-bottom:1px solid #1e1e28;color:#8888aa;font-family:monospace">{t['due']}</td>
        </tr>"""
    return f"""
    <html><body style="background:#0d0d0f;margin:0;padding:32px;font-family:'Segoe UI',sans-serif;">
      <div style="max-width:560px;margin:auto">
        <div style="margin-bottom:32px">
          <span style="font-size:22px;font-weight:800;color:#fff;letter-spacing:-0.5px">Task<span style="color:#a78bfa">flow</span></span>
        </div>
        <div style="background:#111116;border:1px solid #1e1e28;border-radius:16px;overflow:hidden">
          <div style="padding:28px 32px;border-bottom:1px solid #1e1e28">
            <p style="margin:0 0 6px;font-size:13px;color:#a78bfa;font-weight:600;text-transform:uppercase;letter-spacing:1px">Daily Reminder</p>
            <h2 style="margin:0;font-size:22px;color:#fff;font-weight:700">You have {len(tasks)} task(s) due today</h2>
            <p style="margin:8px 0 0;font-size:13px;color:#555566">Hi {username} — {date.today().strftime('%A, %B %d %Y')}</p>
          </div>
          <table style="width:100%;border-collapse:collapse">
            <thead>
              <tr style="background:#0d0d0f">
                <th style="padding:10px 12px;text-align:left;font-size:10px;color:#444455;text-transform:uppercase;letter-spacing:1px;font-weight:700">Task</th>
                <th style="padding:10px 12px;text-align:left;font-size:10px;color:#444455;text-transform:uppercase;letter-spacing:1px;font-weight:700">Description</th>
                <th style="padding:10px 12px;text-align:left;font-size:10px;color:#444455;text-transform:uppercase;letter-spacing:1px;font-weight:700">Priority</th>
                <th style="padding:10px 12px;text-align:left;font-size:10px;color:#444455;text-transform:uppercase;letter-spacing:1px;font-weight:700">Due</th>
              </tr>
            </thead>
            <tbody>{rows}</tbody>
          </table>
          <div style="padding:24px 32px">
            <p style="margin:0;font-size:12px;color:#444455">Login to Taskflow to mark tasks complete.</p>
          </div>
        </div>
        <p style="text-align:center;margin-top:24px;font-size:11px;color:#333344">Taskflow — Automated Daily Reminder</p>
      </div>
    </body></html>"""

def send_reminder(uid, username, tasks):
    if not tasks:
        return False, "No pending tasks due today."
    to_email = get_user_email(uid)
    if not to_email:
        return False, "No email found."
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"⏰ {len(tasks)} task(s) due today — Taskflow"
        msg["From"]    = f"Taskflow <{GMAIL_SENDER}>"
        msg["To"]      = to_email
        msg.attach(MIMEText(build_email_html(username, tasks), "html"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_SENDER, GMAIL_APP_PWD)
            server.sendmail(GMAIL_SENDER, to_email, msg.as_string())
        return True, f"Sent to {to_email}"
    except smtplib.SMTPAuthenticationError:
        return False, "Gmail auth failed — check App Password."
    except Exception as e:
        return False, f"Send failed: {e}"

def get_due_tasks(uid):
    today = str(date.today())
    con   = sqlite3.connect("database.db")
    rows  = pd.read_sql_query(
        "SELECT name, desc, priority, due FROM list_new_new WHERE user_id=? AND due=? AND status='Pending'",
        con, params=(uid, today)
    ).to_dict("records")
    con.close()
    return rows

def check_and_notify(uid, username):
    if st.session_state.get("email_sent"):
        return
    st.session_state.email_sent = True
    tasks = get_due_tasks(uid)
    if tasks:
        ok, msg = send_reminder(uid, username, tasks)
        if ok:
            st.toast(f"📧 Reminder sent — {len(tasks)} task(s) due today", icon="✅")
        else:
            st.session_state.email_error = msg

def login_user(username, password):
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("SELECT user_id, username FROM users WHERE username=? AND password=?",
                (username, hash_password(password)))
    row = cur.fetchone()
    con.close()
    return row

def register_user(username, email, password):
    try:
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        cur.execute("INSERT INTO users(username,email,password) VALUES(?,?,?)",
                    (username, email.lower(), hash_password(password)))
        con.commit()
        con.close()
        return True, "Account created!"
    except sqlite3.IntegrityError as e:
        if "username" in str(e): return False, "Username already taken."
        if "email"    in str(e): return False, "Email already registered."
        return False, "Registration failed."

def priority_badge(p):
    cls = {"High":"badge-high","Medium":"badge-medium","Low":"badge-low"}.get(p,"badge-low")
    dot = {"High":"🔴","Medium":"🟡","Low":"🟢"}.get(p,"⚪")
    return f'<span class="badge {cls}">{dot} {p}</span>'

def due_chip(due_str, status):
    if not due_str: return ""
    try:
        d = datetime.strptime(due_str, "%Y-%m-%d").date()
        today = date.today()
        if status == "Completed":
            return f'<span class="due-chip">{due_str}</span>'
        elif d < today:
            diff = (today - d).days
            return f'<span class="due-chip overdue">⚠ {diff}d overdue</span>'
        elif d == today:
            return f'<span class="due-chip today">⏰ Due today</span>'
        else:
            diff = (d - today).days
            return f'<span class="due-chip">📅 {diff}d left</span>'
    except:
        return f'<span class="due-chip">{due_str}</span>'

def task_card_html(name, desc, priority, due_str, status, extra_class="", extra_style=""):
    badge = priority_badge(priority)
    chip  = due_chip(due_str, status)
    desc_html = f'<div class="task-desc">{desc}</div>' if desc else ''
    name_cls  = "task-name done" if status == "Completed" else "task-name"
    return (
        f'<div class="task-card {extra_class}" style="{extra_style}">'
        f'<div style="flex:1">'
        f'<div class="{name_cls}">{name}</div>'
        f'{desc_html}'
        f'</div>'
        f'{badge}{chip}'
        f'</div>'
    )

def render_weekly_day(day_name, current_day, day_tasks, is_today):
    """Render a single day block in the weekly view using st.markdown properly."""
    border_style = "border-color:#a78bfa;" if is_today else ""
    today_badge = (
        '<span style="background:#1e1e2e;color:#a78bfa;font-size:10px;font-weight:700;'
        'padding:2px 8px;border-radius:10px;margin-left:8px">TODAY</span>'
        if is_today else ""
    )
    count_badge = (
        f'<span style="background:#1e1e28;color:#8888aa;font-size:11px;padding:2px 8px;'
        f'border-radius:10px;font-family:monospace">{len(day_tasks)}</span>'
        if not day_tasks.empty else ""
    )

    # Build task rows HTML
    if not day_tasks.empty:
        task_rows_html = ""
        for _, row in day_tasks.iterrows():
            color = {"High": "#f87171", "Medium": "#fbbf24", "Low": "#34d399"}.get(row["priority"], "#aaa")
            name_style = "text-decoration:line-through;opacity:0.5;" if row["status"] == "Completed" else ""
            task_rows_html += (
                f'<div style="display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid #1a1a24;">'
                f'<span style="width:6px;height:6px;border-radius:50%;background:{color};flex-shrink:0;display:inline-block;"></span>'
                f'<span style="font-size:13px;color:#e8e8f0;flex:1;{name_style}">{row["name"]}</span>'
                f'<span style="font-size:11px;color:{color};font-weight:700;text-transform:uppercase;">{row["priority"]}</span>'
                f'</div>'
            )
    else:
        task_rows_html = '<p style="font-size:12px;color:#444455;padding:8px 0;margin:0;">No tasks scheduled</p>'

    html = (
        f'<div class="day-block" style="{border_style}">'
        f'  <div class="day-header">'
        f'    <div>'
        f'      <span class="day-name">{day_name}{today_badge}</span>'
        f'      <span class="day-date" style="margin-left:8px;">{current_day.strftime("%b %d")}</span>'
        f'    </div>'
        f'    {count_badge}'
        f'  </div>'
        f'  {task_rows_html}'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def get_all_tasks(uid):
    con = sqlite3.connect("database.db")
    df  = pd.read_sql_query("SELECT * FROM list_new_new WHERE user_id=? ORDER BY due", con, params=(uid,))
    con.close()
    return df

# ── Bootstrap ──────────────────────────────────────────────────────────────────
init_db()
inject_css()

for key, val in [("logged_in", False), ("user_id", None), ("username", None),
                 ("email_sent", False), ("email_error", None), ("page", "inbox")]:
    if key not in st.session_state:
        st.session_state[key] = val

# ── Auth ───────────────────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    tab = st.selectbox("", ["Login", "Register"], label_visibility="collapsed")

    if tab == "Login":
        st.markdown("""
        <div style='text-align:center;padding:40px 0 8px'>
            <div style='font-size:32px;font-weight:800;color:#fff;letter-spacing:-1px'>
                Task<span style='color:#a78bfa'>flow</span>
            </div>
            <p style='color:#555566;font-size:14px;margin:6px 0 32px'>Your tasks. Your flow.</p>
        </div>
        """, unsafe_allow_html=True)
        uname = st.text_input("Username", placeholder="Enter username", key="lu")
        pwd   = st.text_input("Password", type="password", placeholder="••••••••", key="lp")
        if st.button("Sign in →", use_container_width=True):
            if not uname or not pwd:
                st.error("Please fill in all fields.")
            else:
                result = login_user(uname, pwd)
                if result:
                    st.session_state.logged_in   = True
                    st.session_state.user_id     = result[0]
                    st.session_state.username    = result[1]
                    st.session_state.email_sent  = False
                    st.session_state.email_error = None
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
    else:
        st.markdown("""
        <div style='text-align:center;padding:40px 0 8px'>
            <div style='font-size:32px;font-weight:800;color:#fff;letter-spacing:-1px'>
                Task<span style='color:#a78bfa'>flow</span>
            </div>
            <p style='color:#555566;font-size:14px;margin:6px 0 32px'>Create your account</p>
        </div>
        """, unsafe_allow_html=True)
        nu = st.text_input("Username", placeholder="Choose a username", key="ru")
        ne = st.text_input("Email",    placeholder="you@example.com",   key="re")
        np = st.text_input("Password", type="password", placeholder="Min 4 characters", key="rp")
        nc = st.text_input("Confirm Password", type="password", placeholder="Repeat password", key="rc")
        if st.button("Create account →", use_container_width=True):
            if not nu or not ne or not np or not nc:
                st.warning("Please fill in all fields.")
            elif "@" not in ne or "." not in ne:
                st.error("Enter a valid email address.")
            elif np != nc:
                st.error("Passwords do not match.")
            elif len(np) < 4:
                st.error("Password must be at least 4 characters.")
            else:
                ok, msg = register_user(nu, ne, np)
                if ok: st.success(msg + " Switch to Login.")
                else:  st.error(msg)
    st.stop()

# ── Logged-in state ────────────────────────────────────────────────────────────
uid      = st.session_state.user_id
username = st.session_state.username
check_and_notify(uid, username)

if st.session_state.email_error:
    st.sidebar.error(f"📧 {st.session_state.email_error}")

df_all = get_all_tasks(uid)
total_tasks   = len(df_all)
pending_tasks = len(df_all[df_all["status"] == "Pending"]) if not df_all.empty else 0
today_tasks   = len(df_all[(df_all["due"] == str(date.today())) & (df_all["status"] == "Pending")]) if not df_all.empty else 0

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <h1>Task<span style='color:#a78bfa'>flow</span></h1>
        <p>Personal task manager</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="nav-section">Menu</div>', unsafe_allow_html=True)
    page = st.selectbox("Navigate",
        ["inbox", "tasks", "add", "edit", "delete", "weekly", "monthly", "analytics", "charts"],
        format_func=lambda x: {
            "inbox":     "📥 Inbox",
            "tasks":     "✅ All Tasks",
            "add":       "➕ Add Task",
            "edit":      "✏️ Edit Task",
            "delete":    "🗑 Delete Task",
            "weekly":    "📅 Weekly",
            "monthly":   "🗓 Monthly",
            "analytics": "📊 Analytics",
            "charts":    "📈 Charts",
        }[x],
        label_visibility="collapsed"
    )
    st.markdown("---")
    if st.button("🔔 Send Reminder Now", use_container_width=True):
        tasks = get_due_tasks(uid)
        if not tasks:
            st.info("No pending tasks due today.")
        else:
            ok, msg = send_reminder(uid, username, tasks)
            if ok: st.success(f"✅ {msg}")
            else:  st.error(msg)
    st.markdown("---")
    initials      = username[:2].upper()
    email_display = get_user_email(uid) or ""
    st.markdown(f"""
    <div style='padding:8px 0'>
        <div style='display:flex;align-items:center;gap:10px'>
            <div style='width:32px;height:32px;border-radius:10px;background:linear-gradient(135deg,#a78bfa,#60a5fa);
                        display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:white;flex-shrink:0'>
                {initials}
            </div>
            <div>
                <div style='font-size:13px;font-weight:600;color:#e8e8f0'>{username}</div>
                <div style='font-size:11px;color:#444455'>{email_display}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
        if st.button("Sign out", use_container_width=True):
            for k in ["logged_in", "user_id", "username", "email_sent", "email_error"]:
                st.session_state[k] = False if k == "logged_in" else None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ── Main content ───────────────────────────────────────────────────────────────
st.markdown('<div style="padding: 32px 40px; max-width: 960px;">', unsafe_allow_html=True)

# ── INBOX ──────────────────────────────────────────────────────────────────────
if page == "inbox":
    today = date.today()
    hour  = datetime.now().hour
    greeting = "morning" if hour < 12 else "afternoon" if hour < 17 else "evening"
    st.markdown(f"""
    <div class="page-header">
        <h2>Good {greeting}, {username} 👋</h2>
        <p>{today.strftime('%A, %B %d %Y')} · {pending_tasks} pending · {today_tasks} due today</p>
    </div>
    """, unsafe_allow_html=True)
    completed = len(df_all[df_all["status"] == "Completed"]) if not df_all.empty else 0
    rate = int(completed / total_tasks * 100) if total_tasks else 0
    high = len(df_all[df_all["priority"] == "High"]) if not df_all.empty else 0
    st.markdown(f"""
    <div class="stat-grid">
        <div class="stat-card purple">
            <div class="stat-label">Total Tasks</div>
            <div class="stat-value">{total_tasks}</div>
            <div class="stat-sub">All time</div>
        </div>
        <div class="stat-card green">
            <div class="stat-label">Completed</div>
            <div class="stat-value">{completed}</div>
            <div class="stat-sub">{rate}% completion rate</div>
        </div>
        <div class="stat-card amber">
            <div class="stat-label">Due Today</div>
            <div class="stat-value">{today_tasks}</div>
            <div class="stat-sub">Pending tasks</div>
        </div>
        <div class="stat-card blue">
            <div class="stat-label">High Priority</div>
            <div class="stat-value">{high}</div>
            <div class="stat-sub">Needs attention</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <div style='margin-bottom:32px'>
        <div style='display:flex;justify-content:space-between;margin-bottom:6px'>
            <span style='font-size:12px;font-weight:600;color:#8888aa'>Overall Progress</span>
            <span style='font-size:12px;font-weight:700;color:#a78bfa;font-family:monospace'>{rate}%</span>
        </div>
        <div class="progress-bar"><div class="progress-fill" style="width:{rate}%"></div></div>
    </div>
    """, unsafe_allow_html=True)
    if not df_all.empty:
        due_today_df = df_all[(df_all["due"] == str(today)) & (df_all["status"] == "Pending")]
        if not due_today_df.empty:
            st.markdown(f"""
            <div class="section-header">
                <h3>⏰ Due Today</h3>
                <span class="section-count">{len(due_today_df)}</span>
            </div>
            """, unsafe_allow_html=True)
            for _, row in due_today_df.iterrows():
                st.markdown(task_card_html(row['name'], row['desc'] or '', row['priority'], row['due'], row['status'], extra_class="due-today"), unsafe_allow_html=True)
        upcoming_df = df_all[
            (df_all["due"] > str(today)) &
            (df_all["due"] <= str(today + timedelta(days=7))) &
            (df_all["status"] == "Pending")
        ]
        if not upcoming_df.empty:
            st.markdown(f"""
            <div class="section-header" style='margin-top:28px'>
                <h3>📅 Upcoming (next 7 days)</h3>
                <span class="section-count">{len(upcoming_df)}</span>
            </div>
            """, unsafe_allow_html=True)
            for _, row in upcoming_df.iterrows():
                st.markdown(task_card_html(row['name'], '', row['priority'], row['due'], row['status']), unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="icon">✨</div>
            <p>No tasks yet. Add your first task to get started.</p>
        </div>
        """, unsafe_allow_html=True)

# ── ALL TASKS ──────────────────────────────────────────────────────────────────
elif page == "tasks":
    st.markdown("""
    <div class="page-header">
        <h2>All Tasks</h2>
        <p>Every task across all projects</p>
    </div>
    """, unsafe_allow_html=True)
    if df_all.empty:
        st.markdown('<div class="empty-state"><div class="icon">📭</div><p>No tasks yet.</p></div>', unsafe_allow_html=True)
    else:
        col1, col2, col3 = st.columns([2, 2, 3])
        with col1: pri_filter = st.selectbox("🎯 Priority", ["All", "High", "Medium", "Low"])
        with col2: sta_filter = st.selectbox("📌 Status",   ["All", "Pending", "Completed"])
        filtered = df_all.copy()
        if pri_filter != "All": filtered = filtered[filtered["priority"] == pri_filter]
        if sta_filter != "All": filtered = filtered[filtered["status"]   == sta_filter]
        st.markdown(f"""
        <div class="section-header" style='margin-top:16px'>
            <h3>Results</h3>
            <span class="section-count">{len(filtered)}</span>
        </div>
        """, unsafe_allow_html=True)
        if filtered.empty:
            st.markdown('<div class="empty-state"><div class="icon">🔍</div><p>No matching tasks.</p></div>', unsafe_allow_html=True)
        else:
            for _, row in filtered.iterrows():
                extra = "due-today" if row["due"] == str(date.today()) and row["status"] == "Pending" else ""
                st.markdown(task_card_html(row['name'], row['desc'] or '', row['priority'], row['due'], row['status'], extra_class=extra), unsafe_allow_html=True)

# ── ADD TASK ───────────────────────────────────────────────────────────────────
elif page == "add":
    st.markdown("""
    <div class="page-header">
        <h2>Add Task</h2>
        <p>Create a new task</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="form-card">', unsafe_allow_html=True)
    n = st.text_input("Task Name *", placeholder="e.g. Submit project report")
    d = st.text_input("Description", placeholder="Optional details...")
    col1, col2, col3 = st.columns(3)
    with col1: p   = st.selectbox("Priority", ["Low", "Medium", "High"])
    with col2: s   = st.selectbox("Status",   ["Pending", "Completed"])
    with col3: due = st.date_input("Due Date", value=date.today())
    st.markdown('</div>', unsafe_allow_html=True)
    if st.button("＋ Add Task", use_container_width=False):
        if not n.strip():
            st.error("Task name is required.")
        else:
            con = sqlite3.connect("database.db")
            cur = con.cursor()
            cur.execute(
                "INSERT INTO list_new_new(user_id,name,desc,priority,status,created,due) VALUES(?,?,?,?,?,?,?)",
                (uid, n.strip(), d.strip(), p, s, str(date.today()), str(due))
            )
            con.commit()
            con.close()
            st.success(f"✅ Task **{n}** added successfully!")
            st.balloons()

# ── EDIT TASK ──────────────────────────────────────────────────────────────────
elif page == "edit":
    st.markdown("""
    <div class="page-header">
        <h2>Edit Task</h2>
        <p>Update an existing task</p>
    </div>
    """, unsafe_allow_html=True)
    if not df_all.empty:
        task_names = df_all["name"].tolist()
        selected   = st.selectbox("Select task to edit", task_names)
        row        = df_all[df_all["name"] == selected].iloc[0]
        st.markdown('<div class="form-card">', unsafe_allow_html=True)
        n = st.text_input("Task Name", value=row["name"])
        d = st.text_input("Description", value=row["desc"] or "")
        col1, col2, col3 = st.columns(3)
        pri_opts = ["Low", "Medium", "High"]
        sta_opts = ["Pending", "Completed"]
        with col1: p = st.selectbox("Priority", pri_opts, index=pri_opts.index(row["priority"]))
        with col2: s = st.selectbox("Status",   sta_opts, index=sta_opts.index(row["status"]))
        with col3:
            try:    due_val = datetime.strptime(row["due"], "%Y-%m-%d").date()
            except: due_val = date.today()
            due = st.date_input("Due Date", value=due_val)
        st.markdown('</div>', unsafe_allow_html=True)
        if st.button("💾 Save Changes", use_container_width=False):
            if not n.strip():
                st.error("Task name cannot be empty.")
            else:
                con = sqlite3.connect("database.db")
                cur = con.cursor()
                cur.execute(
                    "UPDATE list_new_new SET name=?,desc=?,priority=?,status=?,due=? WHERE name=? AND user_id=?",
                    (n.strip(), d.strip(), p, s, str(due), selected, uid)
                )
                con.commit()
                con.close()
                st.success("✅ Task updated!")
                st.rerun()
    else:
        st.markdown('<div class="empty-state"><div class="icon">📭</div><p>No tasks to edit.</p></div>', unsafe_allow_html=True)

# ── DELETE TASK ────────────────────────────────────────────────────────────────
elif page == "delete":
    st.markdown("""
    <div class="page-header">
        <h2>Delete Task</h2>
        <p>Permanently remove a task</p>
    </div>
    """, unsafe_allow_html=True)
    if not df_all.empty:
        task_names = df_all["name"].tolist()
        selected   = st.selectbox("Select task to delete", task_names)
        row        = df_all[df_all["name"] == selected].iloc[0]
        st.markdown(task_card_html(row['name'], row['desc'] or '', row['priority'], row['due'], row['status'],
                                   extra_style="margin:16px 0;border-color:#3d1818"), unsafe_allow_html=True)
        st.markdown('<div class="danger-btn">', unsafe_allow_html=True)
        if st.button("🗑 Delete this task", use_container_width=False):
            con = sqlite3.connect("database.db")
            cur = con.cursor()
            cur.execute("DELETE FROM list_new_new WHERE name=? AND user_id=?", (selected, uid))
            con.commit()
            con.close()
            st.success(f"🗑 Task **{selected}** deleted.")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="empty-state"><div class="icon">📭</div><p>No tasks to delete.</p></div>', unsafe_allow_html=True)

# ── WEEKLY VIEW ────────────────────────────────────────────────────────────────
elif page == "weekly":
    st.markdown("""
    <div class="page-header">
        <h2>Weekly View</h2>
        <p>Tasks organized by day</p>
    </div>
    """, unsafe_allow_html=True)

    selected_date = st.date_input("Select week", value=date.today(), label_visibility="collapsed")
    monday = selected_date - timedelta(days=selected_date.weekday())
    sunday = monday + timedelta(days=6)

    st.markdown(
        f'<p style="color:#555566;font-size:13px;margin-bottom:24px">'
        f'Week of {monday.strftime("%b %d")} — {sunday.strftime("%b %d, %Y")}</p>',
        unsafe_allow_html=True
    )

    con = sqlite3.connect("database.db")
    week_df = pd.read_sql_query(
        "SELECT * FROM list_new_new WHERE user_id=? AND due BETWEEN ? AND ? ORDER BY priority DESC",
        con, params=(uid, str(monday), str(sunday))
    )
    con.close()

    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for i in range(7):
        current_day = monday + timedelta(days=i)
        day_tasks   = week_df[week_df["due"] == str(current_day)] if not week_df.empty else pd.DataFrame()
        is_today    = current_day == date.today()
        render_weekly_day(day_names[i], current_day, day_tasks, is_today)

# ── MONTHLY VIEW ───────────────────────────────────────────────────────────────
elif page == "monthly":
    st.markdown("""
    <div class="page-header">
        <h2>Monthly View</h2>
        <p>Tasks for the selected month</p>
    </div>
    """, unsafe_allow_html=True)
    month_names = {1:"January",2:"February",3:"March",4:"April",5:"May",6:"June",
                   7:"July",8:"August",9:"September",10:"October",11:"November",12:"December"}
    col1, col2 = st.columns([2, 1])
    with col1: month = st.selectbox("Month", list(range(1, 13)), index=date.today().month - 1, format_func=lambda x: month_names[x])
    with col2: year  = st.number_input("Year", min_value=2020, max_value=2100, value=date.today().year)
    con = sqlite3.connect("database.db")
    mdf = pd.read_sql_query(
        "SELECT * FROM list_new_new WHERE user_id=? AND strftime('%Y-%m',due)=? ORDER BY due",
        con, params=(uid, f"{year}-{month:02d}")
    )
    con.close()
    if mdf.empty:
        st.markdown('<div class="empty-state"><div class="icon">📅</div><p>No tasks this month.</p></div>', unsafe_allow_html=True)
    else:
        total = len(mdf)
        comp  = len(mdf[mdf["status"] == "Completed"])
        pend  = total - comp
        rate  = int(comp / total * 100)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total",     total)
        c2.metric("Completed", comp)
        c3.metric("Pending",   pend)
        c4.metric("Rate",      f"{rate}%")
        st.markdown(f"""
        <div class="progress-bar" style="margin:16px 0 28px">
            <div class="progress-fill" style="width:{rate}%"></div>
        </div>
        """, unsafe_allow_html=True)
        for _, row in mdf.iterrows():
            extra = "due-today" if row["due"] == str(date.today()) else ""
            st.markdown(task_card_html(row['name'], row['desc'] or '', row['priority'], row['due'], row['status'], extra_class=extra), unsafe_allow_html=True)

# ── ANALYTICS ──────────────────────────────────────────────────────────────────
elif page == "analytics":
    st.markdown("""
    <div class="page-header">
        <h2>Analytics</h2>
        <p>Insights into your productivity</p>
    </div>
    """, unsafe_allow_html=True)
    if df_all.empty:
        st.markdown('<div class="empty-state"><div class="icon">📊</div><p>Add tasks to see analytics.</p></div>', unsafe_allow_html=True)
    else:
        total = len(df_all)
        comp  = len(df_all[df_all["status"] == "Completed"])
        pend  = total - comp
        rate  = int(comp / total * 100) if total else 0
        high  = len(df_all[df_all["priority"] == "High"])
        med   = len(df_all[df_all["priority"] == "Medium"])
        low   = len(df_all[df_all["priority"] == "Low"])
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Tasks",  total)
        c2.metric("Completed",    comp)
        c3.metric("Pending",      pend)
        c4.metric("Completion %", f"{rate}%")
        st.markdown("<br>", unsafe_allow_html=True)
        c5, c6, c7 = st.columns(3)
        c5.metric("🔴 High Priority",   high)
        c6.metric("🟡 Medium Priority", med)
        c7.metric("🟢 Low Priority",    low)
        today    = str(date.today())
        upcoming = df_all[(df_all["status"] == "Pending") & (df_all["due"] >= today)].head(10)
        if not upcoming.empty:
            st.markdown("""
            <div class="section-header" style='margin-top:32px'>
                <h3>📅 Upcoming Tasks</h3>
            </div>
            """, unsafe_allow_html=True)
            for _, row in upcoming.iterrows():
                st.markdown(task_card_html(row['name'], '', row['priority'], row['due'], row['status']), unsafe_allow_html=True)

# ── CHARTS ─────────────────────────────────────────────────────────────────────
elif page == "charts":
    st.markdown("""
    <div class="page-header">
        <h2>Charts</h2>
        <p>Visual breakdown of your tasks</p>
    </div>
    """, unsafe_allow_html=True)
    if df_all.empty:
        st.markdown('<div class="empty-state"><div class="icon">📈</div><p>Add tasks to see charts.</p></div>', unsafe_allow_html=True)
    else:
        CHART_THEME = dict(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Plus Jakarta Sans", color="#8888aa", size=12),
            margin=dict(l=20, r=20, t=40, b=20),
        )
        col1, col2 = st.columns(2)
        with col1:
            pc  = df_all["priority"].value_counts()
            fig = go.Figure(go.Bar(
                x=pc.index, y=pc.values,
                marker_color=["#f87171", "#fbbf24", "#34d399"],
                text=pc.values, textposition="auto",
                textfont=dict(color="#fff", size=14, family="JetBrains Mono"),
            ))
            fig.update_layout(title="Priority Breakdown", **CHART_THEME,
                              xaxis=dict(gridcolor="#1e1e28"),
                              yaxis=dict(gridcolor="#1e1e28"))
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            sc  = df_all["status"].value_counts()
            fig = go.Figure(go.Pie(
                labels=sc.index, values=sc.values,
                hole=0.6,
                marker=dict(colors=["#34d399", "#a78bfa"],
                            line=dict(color="#0d0d0f", width=2)),
                textfont=dict(color="#fff"),
            ))
            fig.update_layout(title="Status Distribution", **CHART_THEME,
                              showlegend=True,
                              legend=dict(font=dict(color="#8888aa")))
            st.plotly_chart(fig, use_container_width=True)
        dc  = df_all["due"].value_counts().sort_index()
        fig = go.Figure(go.Scatter(
            x=dc.index, y=dc.values,
            mode="lines+markers",
            line=dict(color="#a78bfa", width=2),
            marker=dict(color="#a78bfa", size=8,
                        line=dict(color="#0d0d0f", width=2)),
            fill="tozeroy",
            fillcolor="rgba(167,139,250,0.08)",
        ))
        fig.update_layout(title="Task Timeline", **CHART_THEME,
                          xaxis=dict(gridcolor="#1e1e28"),
                          yaxis=dict(gridcolor="#1e1e28"))
        st.plotly_chart(fig, use_container_width=True)
        cross = pd.crosstab(df_all["priority"], df_all["status"])
        fig   = go.Figure(go.Bar(
            name="Completed", x=cross.index,
            y=cross.get("Completed", pd.Series([0] * len(cross), index=cross.index)),
            marker_color="#34d399",
        ))
        fig.add_trace(go.Bar(
            name="Pending", x=cross.index,
            y=cross.get("Pending", pd.Series([0] * len(cross), index=cross.index)),
            marker_color="#a78bfa",
        ))
        fig.update_layout(title="Priority × Status", barmode="group", **CHART_THEME,
                          xaxis=dict(gridcolor="#1e1e28"),
                          yaxis=dict(gridcolor="#1e1e28"),
                          legend=dict(font=dict(color="#8888aa")))
        st.plotly_chart(fig, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)