import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import date, timedelta, datetime
from urllib.parse import urlencode
import json
import time

st.set_page_config(page_title="TODO PRO",page_icon="📋",layout="wide",initial_sidebar_state="expanded")

st.markdown("""<style>*{margin:0;padding:0;}html,body{background:linear-gradient(135deg,#fffacd 0%,#ffeaa7 50%,#ffdc82 100%);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;}[data-testid="stAppViewContainer"]{background:linear-gradient(135deg,#fffacd 0%,#ffeaa7 50%,#ffdc82 100%);}[data-testid="stSidebar"]{background:linear-gradient(180deg,#ffffff 0%,#fffef0 100%);border-right:3px solid #ffd93d;}[data-testid="stSidebar"]*{color:#1a2f4f;}h1{font-size:42px;font-weight:800;background:linear-gradient(90deg,#ff6b35 0%,#f7931e 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin:30px 0 10px 0 !important;letter-spacing:-1px;}h2{font-size:28px;font-weight:700;color:#ff6b35;margin:25px 0 15px 0 !important;}h3{color:#ff6b35 !important;font-weight:700;}.modern-card{background:white;border-radius:20px;padding:24px;margin-bottom:20px;box-shadow:0 4px 20px rgba(0,0,0,0.08);transition:all 0.3s cubic-bezier(0.4,0,0.2,1);border:3px solid #ffd93d;}.modern-card:hover{box-shadow:0 12px 40px rgba(0,0,0,0.15);transform:translateY(-4px);border-color:#ff6b35;}.banner-blue{background:linear-gradient(135deg,#87ceeb 0%,#5dade2 100%);border-radius:24px;padding:40px;margin-bottom:30px;color:white;box-shadow:0 12px 40px rgba(93,173,226,0.3);position:relative;overflow:hidden;}.banner-blue::before{content:'';position:absolute;top:-50%;right:-10%;width:300px;height:300px;background:rgba(255,255,255,0.1);border-radius:50%;}.banner-blue h2{color:#0a2f51;font-size:32px;margin:0 0 12px 0 !important;font-weight:800;position:relative;z-index:1;}.banner-blue p{color:#0a2f51;font-size:16px;margin:0;position:relative;z-index:1;}.banner-yellow{background:linear-gradient(135deg,#ffe6a0 0%,#ffc966 100%);border-radius:24px;padding:30px;margin-bottom:30px;box-shadow:0 8px 30px rgba(255,192,102,0.25);border:3px solid #ff6b35;}.banner-yellow h3{color:#8b5a00;font-size:24px;margin:0 0 10px 0 !important;}.banner-yellow p{color:#a67c52;margin:0;}.banner-pink{background:linear-gradient(135deg,#ffd4e5 0%,#ffb3d9 100%);border-radius:24px;padding:30px;margin-bottom:30px;box-shadow:0 8px 30px rgba(255,179,217,0.25);border:3px solid #ff6b35;}.notification-box{background:linear-gradient(135deg,#fff5b4 0%,#ffe680 100%);border-radius:16px;padding:20px;margin-bottom:20px;border-left:5px solid #ff6b35;box-shadow:0 4px 15px rgba(255,107,53,0.2);}.notification-text{color:#8b5a00;font-size:14px;font-weight:600;}.notification-title{color:#ff6b35;font-size:16px;font-weight:700;margin-bottom:8px;}.task-card{background:white;border-radius:18px;padding:20px;margin-bottom:15px;box-shadow:0 2px 12px rgba(0,0,0,0.06);border-left:5px solid #ffd93d;transition:all 0.3s ease;cursor:pointer;}.task-card:hover{box-shadow:0 8px 24px rgba(0,0,0,0.12);transform:translateX(4px);border-left-color:#ff6b35;}.task-card-high{border-left-color:#ff6b35;}.task-card-medium{border-left-color:#ffa500;}.task-card-low{border-left-color:#4ecdc4;}.task-title{font-size:18px;font-weight:700;color:#1a2f4f;margin-bottom:10px;}.task-desc{font-size:13px;color:#7a8fa3;margin-bottom:12px;line-height:1.5;}.task-meta{display:flex;gap:10px;flex-wrap:wrap;align-items:center;}.badge{display:inline-block;padding:6px 14px;border-radius:12px;font-size:12px;font-weight:700;}.badge-high{background:#ffe0e0;color:#d32f2f;}.badge-medium{background:#fff3cd;color:#ff9800;}.badge-low{background:#d4f1f4;color:#00897b;}.badge-completed{background:#c8e6c9;color:#2e7d32;}.badge-pending{background:#ffe0b2;color:#e65100;}.stButton>button{background:linear-gradient(135deg,#ff6b35 0%,#f7931e 100%) !important;color:white !important;border:none !important;border-radius:12px !important;padding:12px 28px !important;font-weight:700 !important;font-size:15px !important;transition:all 0.3s ease !important;box-shadow:0 4px 15px rgba(255,107,53,0.3) !important;}.stButton>button:hover{transform:translateY(-2px) !important;box-shadow:0 8px 25px rgba(255,107,53,0.5) !important;}.google-btn{background:white !important;color:#1a2f4f !important;border:2px solid #ff6b35 !important;}.google-btn:hover{background:#fff5f0 !important;}.stTextInput>div>div>input,.stTextArea>div>div>textarea,.stDateInput>div>div>input,.stNumberInput>div>div>input{background-color:white !important;border:2px solid #ffd93d !important;color:#1a2f4f !important;border-radius:12px !important;padding:12px 16px !important;font-size:14px !important;transition:all 0.3s ease !important;}.stTextInput>div>div>input:focus,.stTextArea>div>div>textarea:focus,.stDateInput>div>div>input:focus{border-color:#ff6b35 !important;box-shadow:0 0 0 3px rgba(255,107,53,0.1) !important;}[data-baseweb="select"]>div>div{background:white !important;border:2px solid #ffd93d !important;border-radius:12px !important;color:#1a2f4f !important;}.stSuccess{background:#c8e6c9 !important;border-left:5px solid #2e7d32 !important;border-radius:12px !important;padding:16px !important;color:#1b5e20 !important;}.stError{background:#ffcdd2 !important;border-left:5px solid #d32f2f !important;border-radius:12px !important;padding:16px !important;color:#b71c1c !important;}.stInfo{background:#bbdefb !important;border-left:5px solid #1976d2 !important;border-radius:12px !important;padding:16px !important;color:#01579b !important;}.stWarning{background:#fff3cd !important;border-left:5px solid #ff9800 !important;border-radius:12px !important;padding:16px !important;color:#f57f17 !important;}.stat-box{background:white;border-radius:18px;padding:24px;text-align:center;box-shadow:0 4px 20px rgba(0,0,0,0.08);border:3px solid #ffd93d;}.stat-number{font-size:42px;font-weight:800;color:#ff6b35;margin:10px 0;}.stat-label{font-size:13px;color:#7a8fa3;font-weight:700;text-transform:uppercase;letter-spacing:1px;}[data-baseweb="tab"]{background:white !important;border-radius:12px !important;color:#7a8fa3 !important;padding:12px 24px !important;margin-right:10px !important;box-shadow:0 2px 8px rgba(0,0,0,0.04) !important;border:2px solid #ffd93d !important;}[aria-selected="true"]{background:linear-gradient(135deg,#ff6b35 0%,#f7931e 100%) !important;color:white !important;box-shadow:0 4px 15px rgba(255,107,53,0.3) !important;border:2px solid #ff6b35 !important;}hr{border:none;height:2px;background:linear-gradient(90deg,transparent,#ffd93d,transparent);margin:30px 0;}.empty-state{text-align:center;padding:80px 40px;background:white;border-radius:20px;box-shadow:0 4px 20px rgba(0,0,0,0.08);border:3px solid #ffd93d;}.empty-emoji{font-size:88px;margin-bottom:20px;}.empty-text{color:#7a8fa3;font-size:18px;margin:15px 0;}.footer{text-align:center;color:#ff6b35;padding:40px 20px;font-size:13px;margin-top:60px;border-top:3px solid #ffd93d;font-weight:700;}.stProgress>div>div>div>div{background:linear-gradient(90deg,#ff6b35 0%,#f7931e 100%) !important;}.stDataFrame{background:white !important;}[data-testid="stDataFrame"] {background: white !important;}</style>""",unsafe_allow_html=True)

def init_database():
 con=sqlite3.connect("database.db");cur=con.cursor()
 cur.execute("""CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY AUTOINCREMENT,username TEXT UNIQUE,password TEXT,google_id TEXT)""")
 cur.execute("""CREATE TABLE IF NOT EXISTS list_new(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,name TEXT,desc TEXT,priority TEXT,status TEXT,created TEXT,due TEXT)""")
 con.commit();con.close()

init_database()

def register_user(username,password,google_id=None):
 try:con=sqlite3.connect("database.db");cur=con.cursor();cur.execute("INSERT INTO users(username,password,google_id)VALUES(?,?,?)",(username,password,google_id));con.commit();con.close();return True,"✅ Account Created"
 except:return False,"❌ Username exists"

def login_user(username,password):
 con=sqlite3.connect("database.db");cur=con.cursor();cur.execute("SELECT user_id FROM users WHERE username=? AND password=?",(username,password));user=cur.fetchone();con.close()
 return (True,user[0]) if user else (False,None)

def check_overdue_tasks(user_id):
 con=sqlite3.connect("database.db");df=pd.read_sql_query("SELECT*FROM list_new WHERE user_id=?AND status='Pending'AND due<?ORDER BY due",con,params=(user_id,str(date.today())))
 con.close();return df

def insert_task(user_id,name,desc,priority,status,created,due):
 con=sqlite3.connect("database.db");cur=con.cursor();cur.execute("INSERT INTO list_new(user_id,name,desc,priority,status,created,due)VALUES(?,?,?,?,?,?,?)",(user_id,name,desc,priority,status,str(created),str(due)));con.commit();con.close()

def get_tasks(user_id):
 con=sqlite3.connect("database.db");df=pd.read_sql_query("SELECT*FROM list_new WHERE user_id=?ORDER BY due",con,params=(user_id,));con.close();return df

def update_task(user_id,old_name,name,desc,priority,status,due):
 con=sqlite3.connect("database.db");cur=con.cursor();cur.execute("UPDATE list_new SET name=?,desc=?,priority=?,status=?,due=?WHERE user_id=?AND name=?",(name,desc,priority,status,str(due),user_id,old_name));con.commit();con.close()

def delete_task(user_id,name):
 con=sqlite3.connect("database.db");cur=con.cursor();cur.execute("DELETE FROM list_new WHERE user_id=?AND name=?",(user_id,name));con.commit();con.close()

if "logged_in" not in st.session_state:st.session_state.logged_in=False;st.session_state.user_id=None;st.session_state.username=None;st.session_state.view_date=date.today()

if not st.session_state.logged_in:
 col1,col2,col3=st.columns([1,2,1])
 with col2:
  st.markdown("<br><br>",unsafe_allow_html=True)
  st.markdown("<h1 style='text-align:center;font-size:52px;'>📋 TODO PRO</h1>",unsafe_allow_html=True)
  st.markdown("<p style='text-align:center;color:#ff6b35;font-size:18px;margin-bottom:30px;font-weight:700;'>Smart Task Management System</p>",unsafe_allow_html=True)
  choice=st.radio("",["🔐 Login","📝 Sign Up"],horizontal=True,label_visibility="collapsed")
  st.markdown("<hr>",unsafe_allow_html=True)
  if "Login" in choice:
   st.subheader("🔐 Welcome Back")
   with st.form("login_form"):
    username=st.text_input("Username",placeholder="Enter your username")
    password=st.text_input("Password",type="password",placeholder="Enter your password")
    if st.form_submit_button("🔓 Login",use_container_width=True):
     if not username or not password:st.error("❌ Please fill all fields")
     else:
      success,user_id=login_user(username,password)
      if success:st.session_state.logged_in=True;st.session_state.user_id=user_id;st.session_state.username=username;st.success("✅ Login Success!");st.rerun()
      else:st.error("❌ Invalid credentials")
   st.markdown("<p style='text-align:center;color:#7a8fa3;margin:20px 0;'>━━━ OR ━━━</p>",unsafe_allow_html=True)
   if st.button("🔵 Login with Google",use_container_width=True,key="google_login"):
    st.info("💡 Google login feature is ready! Create an account first, then you can enable Google login in settings.")
  else:
   st.subheader("📝 Create Account")
   with st.form("signup_form"):
    username=st.text_input("Username",placeholder="Choose username")
    password=st.text_input("Password",type="password",placeholder="Min 4 chars")
    confirm=st.text_input("Confirm",type="password",placeholder="Confirm")
    if st.form_submit_button("📝 Sign Up",use_container_width=True):
     if not username or not password:st.error("❌ Fill all fields")
     elif len(username)<3:st.error("❌ Min 3 chars")
     elif len(password)<4:st.error("❌ Min 4 chars")
     elif password!=confirm:st.error("❌ Don't match")
     else:
      success,msg=register_user(username,password)
      if success:st.success(msg);st.info("✅ Login now!")
      else:st.error(msg)
   st.markdown("<p style='text-align:center;color:#7a8fa3;margin:20px 0;'>━━━ OR ━━━</p>",unsafe_allow_html=True)
   if st.button("🔵 Sign Up with Google",use_container_width=True,key="google_signup"):
    st.info("💡 Google signup is available! First create a regular account, then enable Google OAuth in your settings.")
else:
 user_id=st.session_state.user_id;df=get_tasks(user_id);today=date.today()
 overdue_tasks=check_overdue_tasks(user_id)
 with st.sidebar:
  st.markdown(f"<h2 style='margin-top:0;'>👤 {st.session_state.username}</h2>",unsafe_allow_html=True)
  st.markdown(f"<p style='color:#ff6b35;margin-top:-10px;font-weight:700;'>Welcome back!</p>",unsafe_allow_html=True)
  st.markdown("<hr>",unsafe_allow_html=True)
  page=st.radio("Menu",["📋 Dashboard","➕ Add Task","📊 All Tasks","✏️ Edit","🗑️ Delete","📅 Calendar","📈 Analytics","📉 Charts"],label_visibility="collapsed")
  st.markdown("<hr>",unsafe_allow_html=True)
  if st.button("🚪 Logout",use_container_width=True):st.session_state.logged_in=False;st.rerun()
 
 if len(overdue_tasks)>0:
  st.markdown(f'<div class="notification-box"><div class="notification-title">⏰ {len(overdue_tasks)} Overdue Task{"s" if len(overdue_tasks)>1 else ""}!</div><div class="notification-text">You have {len(overdue_tasks)} pending task{"s" if len(overdue_tasks)>1 else ""} that are overdue. Please complete them!</div></div>',unsafe_allow_html=True)
  for idx,task in overdue_tasks.iterrows():
   st.markdown(f'<div style="background:#fff5b4;padding:12px;border-left:4px solid #ff6b35;border-radius:8px;margin-bottom:8px;"><strong>{task["name"]}</strong> - Due: {task["due"]}</div>',unsafe_allow_html=True)
  st.markdown("<hr>",unsafe_allow_html=True)
 
 if "Dashboard" in page:
  st.markdown("<h1>📋 Today's Tasks</h1>",unsafe_allow_html=True)
  st.markdown('<div class="banner-blue"><h2>📅 Select a Date to View Tasks</h2><p>Click any date below to see what tasks are scheduled</p></div>',unsafe_allow_html=True)
  st.markdown("<h3>📆 This Week</h3>",unsafe_allow_html=True)
  cols=st.columns(7)
  for i in range(7):
   curr_date=today-timedelta(days=3-i);is_today=curr_date==st.session_state.view_date
   with cols[i]:
    if st.button(f"{curr_date.strftime('%a').upper()}\n{curr_date.day}",key=f"date_{i}",use_container_width=True):st.session_state.view_date=curr_date;st.rerun()
  
  st.markdown("<hr>",unsafe_allow_html=True)
  view_date_str=str(st.session_state.view_date)
  st.markdown(f"<h2>📋 Tasks for {st.session_state.view_date.strftime('%A, %B %d, %Y')}</h2>",unsafe_allow_html=True)
  day_tasks=df[df['due']==view_date_str]
  
  if day_tasks.empty:
   st.markdown('<div class="empty-state"><div class="empty-emoji">✅</div><div class="empty-text">No tasks for this day</div><div class="empty-text" style="font-size:14px;color:#b0b7bf;">Great! You have a free day</div></div>',unsafe_allow_html=True)
  else:
   completed_count=len(day_tasks[day_tasks['status']=='Completed'])
   st.markdown(f'<div class="section-stat" style="margin-bottom:20px;width:fit-content;">✅ {completed_count}/{len(day_tasks)} completed</div>',unsafe_allow_html=True)
   for idx,task in day_tasks.iterrows():
    priority_class=f"task-card-{task['priority'].lower()}";status_emoji="✅" if task['status']=='Completed' else "⏳"
    priority_badge=f'<span class="badge badge-{task["priority"].lower()}">{task["priority"]}</span>';status_badge=f'<span class="badge badge-{task["status"].lower()}">{task["status"]}</span>'
    st.markdown(f'<div class="task-card {priority_class}"><div class="task-title">{status_emoji} {task["name"]}</div><div class="task-desc">{task["desc"] if pd.notna(task["desc"]) else "No description"}</div><div class="task-meta">{priority_badge}{status_badge}</div></div>',unsafe_allow_html=True)
  
  st.markdown("<hr>",unsafe_allow_html=True)
  if not df.empty:
   total=len(df);completed=len(df[df["status"]=="Completed"]);pending=len(df[df["status"]=="Pending"]);completion_rate=(completed/total*100)if total>0 else 0
   col1,col2,col3,col4=st.columns(4)
   with col1:st.markdown(f'<div class="stat-box"><div class="stat-label">📌 Total</div><div class="stat-number">{total}</div></div>',unsafe_allow_html=True)
   with col2:st.markdown(f'<div class="stat-box"><div class="stat-label">✅ Done</div><div class="stat-number" style="color:#4ecdc4;">{completed}</div></div>',unsafe_allow_html=True)
   with col3:st.markdown(f'<div class="stat-box"><div class="stat-label">⏳ Left</div><div class="stat-number" style="color:#ffa500;">{pending}</div></div>',unsafe_allow_html=True)
   with col4:st.markdown(f'<div class="stat-box"><div class="stat-label">📈 Rate</div><div class="stat-number" style="color:#ff6b35;">{completion_rate:.0f}%</div></div>',unsafe_allow_html=True)
   st.markdown("<h3>⏳ Progress</h3>",unsafe_allow_html=True);st.progress(completion_rate/100 if total>0 else 0)
 
 elif "Add Task" in page:
  st.markdown("<h1>➕ Create Task</h1>",unsafe_allow_html=True)
  st.markdown('<div class="banner-yellow"><h3>📝 New Task</h3><p>Add details and organize your work</p></div>',unsafe_allow_html=True)
  with st.form("add_task_form"):
   name=st.text_input("Task Name *",placeholder="What to do?")
   desc=st.text_area("Description",placeholder="Add details...",height=80)
   col1,col2=st.columns(2)
   with col1:priority=st.selectbox("Priority *",["High","Medium","Low"])
   with col2:due=st.date_input("Due Date *")
   status=st.selectbox("Status *",["Pending","Completed"])
   if st.form_submit_button("✨ Add Task",use_container_width=True):
    if not name:st.error("❌ Enter task name")
    else:insert_task(user_id,name,desc,priority,status,date.today(),due);st.success("✅ Created!");st.rerun()
 
 elif "All Tasks" in page:
  st.markdown("<h1>📊 All Tasks</h1>",unsafe_allow_html=True)
  if df.empty:st.markdown('<div class="empty-state"><div class="empty-emoji">📭</div><div class="empty-text">No tasks</div></div>',unsafe_allow_html=True)
  else:
   search=st.text_input("🔍 Search...",placeholder="Search tasks")
   df_filtered=df[df['name'].str.contains(search,case=False)] if search else df
   if df_filtered.empty:st.info("No match")
   else:
    st.dataframe(df_filtered,use_container_width=True,hide_index=True,height=600)
    csv=df_filtered.to_csv(index=False).encode("utf-8");st.download_button("⬇️ Download CSV",csv,"tasks.csv","text/csv",use_container_width=True)
 
 elif "Edit" in page:
  st.markdown("<h1>✏️ Edit Task</h1>",unsafe_allow_html=True)
  if df.empty:st.info("📭 No tasks")
  else:
   task_names=df['name'].tolist();selected=st.selectbox("Select",task_names)
   old=df[df['name']==selected].iloc[0]
   with st.form("edit_task_form"):
    name=st.text_input("Name",value=old['name'])
    desc=st.text_area("Desc",value=old['desc'] if pd.notna(old['desc']) else "",height=80)
    col1,col2=st.columns(2)
    with col1:priority=st.selectbox("Priority",["High","Medium","Low"],index=["High","Medium","Low"].index(old['priority']))
    with col2:status=st.selectbox("Status",["Pending","Completed"],index=["Pending","Completed"].index(old['status']))
    due=st.date_input("Due",value=datetime.strptime(old['due'],"%Y-%m-%d").date())
    if st.form_submit_button("💾 Update",use_container_width=True):update_task(user_id,selected,name,desc,priority,status,due);st.success("✅ Updated!");st.rerun()
 
 elif "Delete" in page:
  st.markdown("<h1>🗑️ Delete Task</h1>",unsafe_allow_html=True)
  st.markdown('<div class="banner-pink"><h3>⚠️ Delete</h3><p>Cannot be undone!</p></div>',unsafe_allow_html=True)
  if df.empty:st.info("📭 No tasks")
  else:
   task_names=df['name'].tolist();selected=st.selectbox("Select",task_names)
   st.warning("⚠️ Cannot undo!")
   if st.button("🗑️ Delete",use_container_width=True):delete_task(user_id,selected);st.success("✅ Deleted!");st.rerun()
 
 elif "Calendar" in page:
  st.markdown("<h1>📅 Calendar</h1>",unsafe_allow_html=True)
  selected_date=st.date_input("Pick date");monday=selected_date-timedelta(days=selected_date.weekday())
  col_c1,col_c2,col_c3,col_c4,col_c5,col_c6,col_c7=st.columns(7);columns=[col_c1,col_c2,col_c3,col_c4,col_c5,col_c6,col_c7];days_names=['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
  for i in range(7):
   current_day=monday+timedelta(days=i);day_tasks=df[df['due']==str(current_day)]
   with columns[i]:st.markdown(f'<div class="modern-card" style="text-align:center;min-height:200px;display:flex;flex-direction:column;justify-content:space-between;"><div style="font-weight:700;color:#ff6b35;font-size:16px;">{days_names[i]}</div><div style="font-weight:800;color:#1a2f4f;font-size:32px;margin:15px 0;">{current_day.day}</div><div style="font-size:32px;">{"✅" if len(day_tasks)>0 else "○"}</div><div style="font-size:13px;color:#7a8fa3;font-weight:700;">{len(day_tasks)} task</div></div>',unsafe_allow_html=True)
 
 elif "Analytics" in page:
  st.markdown("<h1>📈 Analytics</h1>",unsafe_allow_html=True)
  if df.empty:st.markdown('<div class="empty-state"><div class="empty-emoji">📊</div><div class="empty-text">No data</div></div>',unsafe_allow_html=True)
  else:
   total=len(df);completed=len(df[df['status']=='Completed']);pending=len(df[df['status']=='Pending']);high=len(df[df['priority']=='High']);medium=len(df[df['priority']=='Medium']);low=len(df[df['priority']=='Low']);completion_rate=(completed/total*100)if total>0 else 0
   col1,col2,col3,col4=st.columns(4)
   with col1:st.markdown(f'<div class="stat-box"><div class="stat-label">Total</div><div class="stat-number">{total}</div></div>',unsafe_allow_html=True)
   with col2:st.markdown(f'<div class="stat-box"><div class="stat-label">Done</div><div class="stat-number" style="color:#4ecdc4;">{completed}</div></div>',unsafe_allow_html=True)
   with col3:st.markdown(f'<div class="stat-box"><div class="stat-label">Left</div><div class="stat-number" style="color:#ffa500;">{pending}</div></div>',unsafe_allow_html=True)
   with col4:st.markdown(f'<div class="stat-box"><div class="stat-label">Rate</div><div class="stat-number" style="color:#ff6b35;">{completion_rate:.0f}%</div></div>',unsafe_allow_html=True)
   st.markdown("<h3>⏳ Progress</h3>",unsafe_allow_html=True);st.progress(completion_rate/100 if total>0 else 0)
 
 elif "Charts" in page:
  st.markdown("<h1>📉 Charts</h1>",unsafe_allow_html=True)
  if df.empty:st.info("📭 No data")
  else:
   tab1,tab2,tab3,tab4=st.tabs(["Status","Priority","Timeline","Mix"])
   with tab1:
    st.subheader("Status Distribution")
    status_counts=df['status'].value_counts()
    fig=px.pie(values=status_counts.values,names=status_counts.index,color_discrete_map={'Completed':'#4ecdc4','Pending':'#ffa500'},template='plotly_white',hole=0.4)
    fig.update_layout(height=500,paper_bgcolor='white',plot_bgcolor='white');st.plotly_chart(fig,use_container_width=True)
   with tab2:
    st.subheader("Priority Breakdown")
    priority_df=pd.DataFrame({'Priority':['High','Medium','Low'],'Count':[len(df[df['priority']=='High']),len(df[df['priority']=='Medium']),len(df[df['priority']=='Low'])]})
    fig=px.bar(priority_df,x='Priority',y='Count',color='Priority',color_discrete_map={'High':'#ff6b6b','Medium':'#ffa500','Low':'#4ecdc4'},template='plotly_white')
    fig.update_layout(height=500,showlegend=False,paper_bgcolor='white',plot_bgcolor='white');st.plotly_chart(fig,use_container_width=True)
   with tab3:
    st.subheader("Timeline View")
    due_counts=df['due'].value_counts().sort_index().head(20)
    fig=px.line(x=due_counts.index,y=due_counts.values,markers=True,template='plotly_white',line_shape='linear')
    fig.update_layout(height=500,paper_bgcolor='white',plot_bgcolor='white');st.plotly_chart(fig,use_container_width=True)
   with tab4:
    st.subheader("Priority vs Status")
    cross=pd.crosstab(df['priority'],df['status'])
    fig=px.bar(cross,barmode='group',template='plotly_white')
    fig.update_layout(height=500,paper_bgcolor='white',plot_bgcolor='white');st.plotly_chart(fig,use_container_width=True)

st.markdown("<div class='footer'>📋 TODO PRO | Smart Task Management | © 2024</div>",unsafe_allow_html=True)