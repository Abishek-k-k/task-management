import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
import hashlib
import resend
from datetime import date, timedelta, datetime
from apscheduler.schedulers.background import BackgroundScheduler

# ─────────────────────────────────────────────
# ✅ SETTINGS — only change these
# ─────────────────────────────────────────────
RESEND_API_KEY  = "re_aaKU8hcz_A5ppcrUe4qzdV68afCyVC7xJ"  # ← your Resend API key
SEND_HOUR       = 10    # ← hour to send daily reminder (24hr format, e.g. 8 = 8:00 AM)
SEND_MINUTE     = 5    # ← minute  (e.g. 30 → 8:30 AM)

# ─────────────────────────────────────────────
# DB SETUP
# ─────────────────────────────────────────────
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
    try:
        cur.execute("ALTER TABLE users ADD COLUMN email TEXT NOT NULL DEFAULT ''")
        con.commit()
    except Exception:
        pass
    con.commit()
    con.close()

def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

# ─────────────────────────────────────────────
# EMAIL HELPERS
# ─────────────────────────────────────────────
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

def send_reminder(to_email: str, username: str, tasks: list) -> tuple:
    if not tasks:
        return False, "No pending tasks due today."
    if RESEND_API_KEY.startswith("re_xxx"):
        return False, "API key not set. Paste your Resend key in sec.py."
    try:
        resend.api_key = RESEND_API_KEY
        resend.Emails.send({
            "from":    "TODO App <onboarding@resend.dev>",
            "to":      [to_email],
            "subject": f"⏰ You have {len(tasks)} task(s) due today!",
            "html":    build_email_html(username, tasks),
        })
        return True, f"Reminder sent to {to_email}"
    except Exception as e:
        return False, f"Failed: {e}"

# ─────────────────────────────────────────────
# AUTOMATIC DAILY JOB
# Runs every day at SEND_HOUR:SEND_MINUTE
# Sends reminders to ALL users with pending tasks due today
# ─────────────────────────────────────────────
def send_daily_reminders():
    today = str(date.today())
    try:
        con  = sqlite3.connect("database.db")
        cur  = con.cursor()
        # Get all users
        cur.execute("SELECT user_id, username, email FROM users")
        users = cur.fetchall()
        for user_id, username, email in users:
            # Get their pending tasks due today
            rows = pd.read_sql_query(
                "SELECT name, desc, priority, due FROM list_new_new "
                "WHERE user_id=? AND due=? AND status='Pending'",
                con, params=(user_id, today)
            ).to_dict("records")
            if rows:
                send_reminder(email, username, rows)
        con.close()
    except Exception as e:
        print(f"[Scheduler] Error: {e}")

# Start scheduler only once using session state flag
if "scheduler_started" not in st.session_state:
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        send_daily_reminders,
        trigger="cron",
        hour=SEND_HOUR,
        minute=SEND_MINUTE,
        id="daily_reminder"
    )
    scheduler.start()
    st.session_state.scheduler_started = True

# ─────────────────────────────────────────────
# AUTH HELPERS
# ─────────────────────────────────────────────
def login_user(username, password):
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute(
        "SELECT user_id, username, email FROM users WHERE username=? AND password=?",
        (username, hash_password(password))
    )
    row = cur.fetchone()
    con.close()
    return row

def register_user(username, email, password):
    try:
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        cur.execute(
            "INSERT INTO users(username, email, password) VALUES(?,?,?)",
            (username, email.lower(), hash_password(password))
        )
        con.commit()
        con.close()
        return True, "Account created!"
    except sqlite3.IntegrityError as e:
        if "username" in str(e):
            return False, "Username already taken."
        if "email" in str(e):
            return False, "Email already registered."
        return False, "Registration failed."

# ─────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────
init_db()

for key, val in [("logged_in", False), ("user_id", None),
                 ("username",  None),   ("user_email", None)]:
    if key not in st.session_state:
        st.session_state[key] = val

# ─────────────────────────────────────────────
# AUTH PAGES
# ─────────────────────────────────────────────
if not st.session_state.logged_in:
    st.title("📝 TODO App")
    auth_tab = st.selectbox("", ["Login", "Register"])

    if auth_tab == "Login":
        st.subheader("Login")
        uname = st.text_input("Username", key="login_user")
        pwd   = st.text_input("Password", type="password", key="login_pwd")
        if st.button("Login"):
            if not uname or not pwd:
                st.warning("Please enter both fields.")
            else:
                result = login_user(uname, pwd)
                if result:
                    st.session_state.logged_in  = True
                    st.session_state.user_id    = result[0]
                    st.session_state.username   = result[1]
                    st.session_state.user_email = result[2]
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

    else:
        st.subheader("Create an Account")
        new_uname = st.text_input("Username",         key="reg_user")
        new_email = st.text_input("Email Address",    key="reg_email", placeholder="you@example.com")
        new_pwd   = st.text_input("Password",         type="password", key="reg_pwd")
        confirm   = st.text_input("Confirm Password", type="password", key="reg_confirm")
        if st.button("Register"):
            if not new_uname or not new_email or not new_pwd or not confirm:
                st.warning("Please fill in all fields.")
            elif "@" not in new_email or "." not in new_email:
                st.error("Enter a valid email address.")
            elif new_pwd != confirm:
                st.error("Passwords do not match.")
            elif len(new_pwd) < 4:
                st.error("Password must be at least 4 characters.")
            else:
                ok, msg = register_user(new_uname, new_email, new_pwd)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)
    st.stop()

# ─────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────
uid        = st.session_state.user_id
username   = st.session_state.username
user_email = st.session_state.user_email

st.title("📝 TODO")
st.sidebar.write(f"👤 **{username}**")
st.sidebar.write(f"📧 {user_email}")
st.sidebar.caption(f"⏰ Auto-reminder runs daily at {SEND_HOUR:02d}:{SEND_MINUTE:02d}")

# Manual trigger button (optional, kept for convenience)
if st.sidebar.button("🔔 Send Reminder Now"):
    today = str(date.today())
    con   = sqlite3.connect("database.db")
    rows  = pd.read_sql_query(
        "SELECT name, desc, priority, due FROM list_new_new "
        "WHERE user_id=? AND due=? AND status='Pending'",
        con, params=(uid, today)
    ).to_dict("records")
    con.close()
    if not rows:
        st.sidebar.info("No pending tasks due today.")
    else:
        ok, msg = send_reminder(user_email, username, rows)
        if ok:
            st.sidebar.success(msg)
        else:
            st.sidebar.error(msg)

if st.sidebar.button("Logout"):
    for k in ["logged_in","user_id","username","user_email"]:
        st.session_state[k] = False if k == "logged_in" else None
    st.rerun()

pg = st.sidebar.selectbox(
    "Pages",
    ["insert","view","edit","delete","weekly","monthly","analysis","visualization","filters"]
)

# ─── INSERT ───────────────────────────────────
if pg == "insert":
    n       = st.text_input("Enter name of the task")
    d       = st.text_input("Enter Description")
    p       = st.selectbox("Priority", ["Low","Medium","High"])
    s       = st.selectbox("Status",   ["Completed","Pending"])
    due     = st.date_input("Due Date")
    created = date.today()
    if st.button("Submit"):
        if not n:
            st.warning("Task name is required.")
        else:
            con = sqlite3.connect("database.db")
            cur = con.cursor()
            cur.execute(
                "INSERT INTO list_new_new(user_id,name,desc,priority,status,created,due) VALUES(?,?,?,?,?,?,?)",
                (uid, n, d, p, s, str(created), str(due))
            )
            con.commit()
            con.close()
            st.success("Task inserted successfully!")

# ─── VIEW ────────────────────────────────────
elif pg == "view":
    con = sqlite3.connect("database.db")
    df  = pd.read_sql_query("SELECT * FROM list_new_new WHERE user_id=?", con, params=(uid,))
    con.close()
    if df.empty:
        st.info("No tasks found.")
    else:
        today     = str(date.today())
        due_today = df[(df["due"] == today) & (df["status"] == "Pending")]
        if not due_today.empty:
            st.warning(f"⏰ You have {len(due_today)} task(s) due today!")
        st.dataframe(df, use_container_width=True)

# ─── EDIT ────────────────────────────────────
elif pg == "edit":
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    i   = st.text_input("Enter task name to edit")
    cur.execute("SELECT * FROM list_new_new WHERE name=? AND user_id=?", (i, uid))
    old = cur.fetchone()
    if i and not old:
        st.error("Task not found.")
    if old:
        cols     = [desc[0] for desc in cur.description]
        old_dict = dict(zip(cols, old))
        n   = st.text_input("New Name",        value=old_dict["name"])
        d   = st.text_input("New Description", value=old_dict["desc"] or "")
        pri_opts = ["Low","Medium","High"]
        p   = st.selectbox("New Priority", pri_opts, index=pri_opts.index(old_dict["priority"]))
        sta_opts = ["Completed","Pending"]
        s   = st.selectbox("New Status",   sta_opts, index=sta_opts.index(old_dict["status"]))
        due = st.date_input("New Due Date",
                            value=datetime.strptime(old_dict["due"], "%Y-%m-%d").date())
        if st.button("Update"):
            cur.execute(
                "UPDATE list_new_new SET name=?,desc=?,priority=?,status=?,due=? WHERE name=? AND user_id=?",
                (n, d, p, s, str(due), i, uid)
            )
            con.commit()
            st.success("Task updated successfully!")
    con.close()

# ─── DELETE ──────────────────────────────────
elif pg == "delete":
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    i   = st.text_input("Enter task name to delete")
    if st.button("Delete"):
        cur.execute("SELECT * FROM list_new_new WHERE name=? AND user_id=?", (i, uid))
        if cur.fetchone():
            cur.execute("DELETE FROM list_new_new WHERE name=? AND user_id=?", (i, uid))
            con.commit()
            st.success("Task deleted successfully!")
        else:
            st.error("Task not found.")
    con.close()

# ─── WEEKLY ──────────────────────────────────
elif pg == "weekly":
    con           = sqlite3.connect("database.db")
    cur           = con.cursor()
    selected_date = st.date_input("Select Date")
    monday        = selected_date - timedelta(days=selected_date.weekday())
    sunday        = monday + timedelta(days=6)
    st.write(f"**Week Range:** {monday} to {sunday}")
    cur.execute(
        "SELECT * FROM list_new_new WHERE user_id=? AND due BETWEEN ? AND ? ORDER BY due",
        (uid, str(monday), str(sunday))
    )
    tasks   = cur.fetchall()
    cur.execute("PRAGMA table_info(list_new_new)")
    col_map = {info[1]: info[0] for info in cur.fetchall()}
    for i in range(7):
        current_day = monday + timedelta(days=i)
        st.subheader(f"{current_day.strftime('%A')} - {current_day}")
        count = 0
        for task in tasks:
            if task[col_map["due"]] == str(current_day):
                count += 1
                label = f"{task[col_map['name']]} : {task[col_map['desc']]}"
                if task[col_map["priority"]] == "High":
                    st.error(label)
                elif task[col_map["priority"]] == "Medium":
                    st.warning(label)
                else:
                    st.success(label)
        if count == 0:
            st.write("No tasks scheduled")
        else:
            st.write(f"Tasks Count: {count}")
    con.close()

# ─── MONTHLY ─────────────────────────────────
elif pg == "monthly":
    con = sqlite3.connect("database.db")
    month_names = {
        1:"January",  2:"February", 3:"March",    4:"April",
        5:"May",       6:"June",     7:"July",      8:"August",
        9:"September",10:"October",11:"November", 12:"December"
    }
    col1, col2 = st.columns(2)
    with col1:
        month = st.selectbox("Select Month", list(range(1, 13)),
                             format_func=lambda x: month_names[x])
    with col2:
        year = st.number_input("Select Year", min_value=2020,
                               max_value=2100, value=datetime.now().year)
    st.subheader(f"Showing: {month_names[month]} {year}")
    df = pd.read_sql_query(
        "SELECT * FROM list_new_new WHERE user_id=? AND strftime('%Y-%m',due)=? ORDER BY due",
        con, params=(uid, f"{year}-{month:02d}")
    )
    if df.empty:
        st.info("No tasks available for this month.")
    else:
        total     = len(df)
        completed = len(df[df["status"] == "Completed"])
        pending   = total - completed
        rate      = (completed / total) * 100
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Tasks",  total)
        c2.metric("Completed",    completed)
        c3.metric("Pending",      pending)
        c4.metric("Completion %", f"{rate:.1f}%")
        st.dataframe(df, use_container_width=True)
    con.close()

# ─── ANALYSIS ────────────────────────────────
elif pg == "analysis":
    con = sqlite3.connect("database.db")
    df  = pd.read_sql_query("SELECT * FROM list_new_new WHERE user_id=?", con, params=(uid,))
    if df.empty:
        st.info("No tasks available.")
    else:
        total     = len(df)
        completed = len(df[df["status"] == "Completed"])
        pending   = len(df[df["status"] == "Pending"])
        rate      = (completed / total * 100) if total else 0
        high      = len(df[df["priority"] == "High"])
        medium    = len(df[df["priority"] == "Medium"])
        low       = len(df[df["priority"] == "Low"])
        st.subheader("Overall Metrics")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Tasks",  total)
        c2.metric("Completed",    completed)
        c3.metric("Pending",      pending)
        c4.metric("Completion %", f"{rate:.1f}%")
        st.subheader("Priority Breakdown")
        c5, c6, c7 = st.columns(3)
        c5.metric("High",   high)
        c6.metric("Medium", medium)
        c7.metric("Low",    low)
        st.subheader("Upcoming Tasks")
        today = str(date.today())
        upcoming = pd.read_sql_query(
            "SELECT * FROM list_new_new WHERE user_id=? AND status='Pending' AND due>=? ORDER BY due LIMIT 7",
            con, params=(uid, today)
        )
        if upcoming.empty:
            st.info("No upcoming tasks.")
        else:
            st.dataframe(upcoming, use_container_width=True)
    con.close()

# ─── VISUALIZATION ───────────────────────────
elif pg == "visualization":
    con = sqlite3.connect("database.db")
    df  = pd.read_sql_query("SELECT * FROM list_new_new WHERE user_id=?", con, params=(uid,))
    con.close()
    if df.empty:
        st.info("No tasks available.")
    else:
        total     = len(df)
        completed = len(df[df["status"] == "Completed"])
        pending   = len(df[df["status"] == "Pending"])
        high      = len(df[df["priority"] == "High"])
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total",         total)
        c2.metric("Completed",     completed)
        c3.metric("Pending",       pending)
        c4.metric("High Priority", high)
        st.divider()
        pc = df["priority"].value_counts()
        st.plotly_chart(px.bar(x=pc.index, y=pc.values, color=pc.index,
            labels={"x":"Priority","y":"Tasks"}, title="Priority Distribution"),
            use_container_width=True)
        sc = df["status"].value_counts()
        st.plotly_chart(px.pie(names=sc.index, values=sc.values,
            title="Completed vs Pending"), use_container_width=True)
        dc = df["due"].value_counts().sort_index()
        st.plotly_chart(px.line(x=dc.index, y=dc.values, markers=True,
            labels={"x":"Due Date","y":"Tasks"}, title="Tasks Timeline"),
            use_container_width=True)
        cross = pd.crosstab(df["priority"], df["status"])
        st.plotly_chart(px.bar(cross, barmode="group",
            title="Priority and Status Analysis"), use_container_width=True)
        df["month"] = pd.to_datetime(df["due"]).dt.strftime("%Y-%m")
        mc = df["month"].value_counts().sort_index()
        st.plotly_chart(px.area(x=mc.index, y=mc.values,
            labels={"x":"Month","y":"Tasks"}, title="Monthly Growth"),
            use_container_width=True)
        today    = str(date.today())
        upcoming = df[(df["status"] == "Pending") & (df["due"] >= today)].sort_values("due")
        st.subheader("Upcoming Pending Tasks")
        st.dataframe(upcoming, use_container_width=True)
        st.subheader("Full Task Database")
        st.dataframe(df, use_container_width=True)

# ─── FILTERS ─────────────────────────────────
elif pg == "filters":
    con = sqlite3.connect("database.db")
    df  = pd.read_sql_query("SELECT * FROM list_new_new WHERE user_id=?", con, params=(uid,))
    con.close()
    if df.empty:
        st.info("No tasks available.")
    else:
        pri_filter = st.selectbox("Select Priority", ["All","High","Medium","Low"])
        sta_filter = st.selectbox("Select Status",   ["All","Pending","Completed"])
        filtered   = df.copy()
        if pri_filter != "All":
            filtered = filtered[filtered["priority"] == pri_filter]
        if sta_filter != "All":
            filtered = filtered[filtered["status"]   == sta_filter]
        st.subheader("Filtered Tasks")
        if filtered.empty:
            st.warning("No matching tasks found.")
        else:
            st.dataframe(filtered, use_container_width=True)
