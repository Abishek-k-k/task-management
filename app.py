import sqlite3
import pandas as pd
import streamlit as st
from datetime import date
from datetime import timedelta
from datetime import datetime
st.title("TODO")
pg=st.sidebar.selectbox("pages",["insert","view","edit","delete","weekly","monthly"])
if pg=="insert":
    i=st.number_input("Enter id")
    n=st.text_input("Enter name of the task")
    d=st.text_input("enter Description")
    p=st.selectbox("Priority",["Low","Medium","High"])
    s=st.selectbox("Status",["done","pending"])
    due=st.date_input("Due Date")
    created=date.today()
    submit=st.button("submit")
    if submit:
        con=sqlite3.connect("database.db")
        cur=con.cursor()
        cur.execute("insert into list(id,name,desc,priority,status,created,due) values(?,?,?,?,?,?,?)",(i,n,d,p,s,str(created),str(due)))
        st.success("inserted")
        con.commit()
if pg=="view":
    con=sqlite3.connect("database.db")
    cur=con.cursor()
    re=cur.execute("select * from list")
    data=re.fetchall()
    col=[desc[0] for desc in cur.description]
    frame=pd.DataFrame(data,columns=col)
    st.dataframe(frame)
if pg=="edit":
    con=sqlite3.connect("database.db")
    cur=con.cursor()
    i = st.text_input("Enter name")
    cur.execute("SELECT * FROM list WHERE name=?", (i,))
    old = cur.fetchone()
    if old:
        old_name = old[1]
        old_desc = old[2]
        old_priority = old[3]
        old_status = old[4]
        old_due = old[6]
        n = st.text_input("New Name")
        d = st.text_input("New Description")
        p = st.text_input("New Priority")
        s = st.text_input("New Status")
        due = st.date_input("New Due Date")
        if st.button("Update"):
            if n == "":
                n = old_name
            if d == "":
                d = old_desc
            if p == "":
                p = old_priority        
            if s =="":
                s = old_status
            if due == "":
                 due = old_due
            cur.execute("""UPDATE list SET name=?,desc=?,priority=?,status=?,due=? WHERE name=?""",(n, d, p, s, due, i))
            st.success("edited")
        con.commit()
if pg=="delete":
    con=sqlite3.connect("database.db")
    cur=con.cursor()
    i=st.text_input("enter task to delete")
    delete=st.button("delete")
    if delete:      
        re=cur.execute("select * from list where name=?",(i,))
        data=re.fetchone()
        if data:
             cur.execute("DELETE FROM list WHERE name=?",(i,))
             con.commit()
             st.success("deleted")
        else:
             st.error("no")
if pg=="weekly":
    con=sqlite3.connect("database.db")
    cur=con.cursor()
    selected_date=st.date_input("Select Date")
    monday=selected_date-timedelta(days=selected_date.weekday())
    sunday=monday+timedelta(days=6)
    st.write(f"Week Range : {monday} to {sunday}")
    cur.execute("SELECT * FROM list WHERE due BETWEEN ? AND ? ORDER BY due",(str(monday),str(sunday)))
    tasks=cur.fetchall()
    for i in range(7):
        current_day=monday+timedelta(days=i)
        day_name=current_day.strftime("%A")
        st.subheader(f"{day_name} - {current_day}")
        count=0
        for task in tasks:
            if task[6]==str(current_day):
                count+=1
                if task[3]=="High":
                    st.error(f"{task[1]} : {task[2]}")
                elif task[3]=="Medium":
                    st.warning(f"{task[1]} : {task[2]}")
                else:
                    st.success(f"{task[1]} : {task[2]}")
        if count==0:
            st.write("No tasks scheduled")
        else:
            st.write(f"Tasks Count : {count}")
if pg=="monthly":
    con=sqlite3.connect("database.db")
    month_names={1:"January",2:"February",3:"March",4:"April",5:"May",6:"June",7:"July",8:"August",9:"September",10:"October",11:"November",12:"December"}
    st.title("📆 Monthly View")
    col1,col2=st.columns(2)
    with col1:
        month=st.selectbox("Select Month",list(range(1,13)),format_func=lambda x:month_names[x])
    with col2:
        year=st.number_input("Select Year",min_value=2020,max_value=2100,value=datetime.now().year)
        st.subheader(f"Showing : {month_names[month]} {year}")
    month_string=f"{year}-{month:02d}"
    query="""SELECT * FROM list WHERE strftime('%Y-%m',due)=? ORDER BY due"""
    df=pd.read_sql_query(query,con,params=(month_string,))
    if len(df)==0:
        st.info("No tasks available for this month")
    else:
        total_tasks=len(df)
        completed_tasks=len(df[df["status"]=="done"])
        pending_tasks=total_tasks-completed_tasks
        completion_rate=(completed_tasks/total_tasks)*100
        c1,c2,c3,c4=st.columns(4)
        with c1:
            st.metric("Total Tasks",total_tasks)
        with c2:
            st.metric("Completed",completed_tasks)
        with c3:
            st.metric("Pending",pending_tasks)
        with c4:
            st.metric("Completion %",f"{completion_rate:.1f}%")
        st.subheader("Task List")
        st.dataframe(df)
