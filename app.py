import sqlite3
import pandas as pd
import streamlit as st
from datetime import date
st.title("TODO")
pg=st.sidebar.selectbox("pages",["insert","view","edit","delete"])
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
        due = st.text_input("New Due Date")
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
             st.success("delete")
        else:
             st.error("no")