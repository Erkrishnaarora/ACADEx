# Project: ACADEx
# Developed by: Krishna Arora
# Year: 2026
# Description: Academic Centralized Analytics and Data System for Student Performance and Expense Management
# GitHub: https://github.com/ErKrishnaarora
import streamlit as st    
import pandas as pd    
import sqlite3    
import hashlib    
import plotly.express as px    
from datetime import datetime    
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle    
from reportlab.lib import colors    
from reportlab.lib.styles import getSampleStyleSheet    
import io   

# ---------------- DATABASE ----------------    
conn = sqlite3.connect("acadex.db", check_same_thread=False)    
c = conn.cursor()    
    
c.execute('''CREATE TABLE IF NOT EXISTS users    
(username TEXT PRIMARY KEY, password TEXT)''')    
    
c.execute('''CREATE TABLE IF NOT EXISTS students    
(id INTEGER PRIMARY KEY AUTOINCREMENT,    
name TEXT, class_roll TEXT, uni_roll TEXT,    
attended REAL, total REAL,    
mst1 REAL, mst2 REAL,    
expenses REAL,    
timestamp TEXT)''')    
    
# ---------------- FUNCTIONS ----------------    
def hash_password(pw):    
    return hashlib.sha256(pw.encode()).hexdigest()    
    
def login_user(user, pw):    
    c.execute("SELECT * FROM users WHERE username=? AND password=?",    
              (user, hash_password(pw)))    
    return c.fetchone()    
    
def signup_user(user, pw):    
    try:    
        c.execute("INSERT INTO users VALUES (?,?)",    
                  (user, hash_password(pw)))    
        conn.commit()    
        return True    
    except:    
        return False    
    
# ---------------- UI CONFIG ----------------    
st.set_page_config(page_title="ACADEx", layout="wide")    
    
st.markdown("""    
<style>    
body {background: linear-gradient(135deg,#020617,#0f172a,#4c1d95); color:white;}    
.title {text-align:center;font-size:60px;font-weight:bold;    
background: linear-gradient(90deg,#06b6d4,#9333ea);    
-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-top:50px;}    
.section {font-size:32px;font-weight:700;    
background: linear-gradient(90deg,#22d3ee,#a855f7);    
-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-top:25px;margin-bottom:10px;}    
.card {padding:18px;border-radius:15px;margin-top:10px;color:white;font-weight:500;}    
.green {background: rgba(34,197,94,0.2); border:1px solid #22c55e;}    
.yellow {background: rgba(234,179,8,0.2); border:1px solid #eab308;}    
.red {background: rgba(239,68,68,0.2); border:1px solid #ef4444;}    
.divider {height:2px;background: linear-gradient(to right,#06b6d4,#9333ea);margin:15px 0;}    

.blue {background: rgba(59,130,246,0.2); border:1px solid #3b82f6;}
</style>    
""", unsafe_allow_html=True)    
    
# ---------------- SESSION ----------------    
if "login" not in st.session_state:    
    st.session_state.login = False    
    
# ---------------- LOGIN ----------------    
if not st.session_state.login:    
    st.markdown('<div class="title">WELCOME TO ACADEx</div>', unsafe_allow_html=True)    
    
    menu = st.radio("Access", ["Login", "Signup"])    
    
    user = st.text_input("Username")    
    pw = st.text_input("Password", type="password")    
    
    if menu == "Login":    
        if st.button("Login"):    
            if login_user(user, pw):    
                st.session_state.login = True    
                st.rerun()    
            else:    
                st.error("Invalid credentials")    
    
    else:    
        if st.button("Create Account"):    
            if signup_user(user, pw):    
                st.success("Account created successfully")    
            else:    
                st.error("User already exists")    
    
# ---------------- MAIN APP ----------------    
if st.session_state.login:    
    
    st.sidebar.title("ACADEX Navigation")    
    page = st.sidebar.radio("Select Page", [    
        "Student Entry",    
        "Analytics",    
        "Search",    
        "Smart Dashboard",    
        "Manage Data",    
        "Export and Logout"    
    ])    
    
    df = pd.read_sql("SELECT * FROM students", conn)    
    
    # ---------------- STUDENT ENTRY ----------------    
    if page == "Student Entry":    
        st.markdown('<div class="section">Student Entry</div>', unsafe_allow_html=True)    
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)    
    
        col1, col2 = st.columns(2)    
    
        with col1:    
            name = st.text_input("Student Name")    
            class_roll = st.text_input("Class Roll Number")    
            uni_roll = st.text_input("University Roll Number")    
            attended = st.number_input("Classes Attended", 0)    
            total = st.number_input("Total Classes", 1)    
    
        with col2:    
            mst1 = st.number_input("MST 1 Marks", 0.0)    
            mst2 = st.number_input("MST 2 Marks", 0.0)    
            expenses = st.number_input("Monthly Expenses (Optional)", 0.0)    
    
        if st.button("Save Record"):    
            if name == "" or attended > total:    
                st.error("Invalid input")    
            else:    
                c.execute("""INSERT INTO students     
                (name,class_roll,uni_roll,attended,total,mst1,mst2,expenses,timestamp)    
                VALUES (?,?,?,?,?,?,?,?,?)""",    
                (name,class_roll,uni_roll,attended,total,mst1,mst2,expenses,str(datetime.now())))    
                conn.commit()    
                st.success("Record saved")    
    
        best = max(mst1, mst2)    
        avg = (mst1 + mst2)/2    
        attendance = (attended/total)*100 if total else 0    
    
        st.markdown(f"<div class='card'>Best MST: {best}</div>", unsafe_allow_html=True)    
        st.markdown(f"<div class='card'>Average MST: {avg}</div>", unsafe_allow_html=True)    
        st.markdown(f"<div class='card'>Attendance: {round(attendance,2)}%</div>", unsafe_allow_html=True)    
    
    # ---------------- SMART DASHBOARD ----------------    
    elif page == "Smart Dashboard":    
        st.markdown('<div class="section">Performance Classification</div>', unsafe_allow_html=True)    
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)    
    
        if not df.empty:    
            df["avg"] = (df["mst1"] + df["mst2"]) / 2    
    
            bright = df[df["avg"] > 19]    
            average = df[(df["avg"] > 10) & (df["avg"] <= 19)]    
            poor = df[df["avg"] <= 10]    
    
            col1, col2, col3 = st.columns(3)    
    
            col1.markdown(f"<div class='card green'><b>Bright Students ({len(bright)})</b><br>{bright['name'].tolist()}</div>", unsafe_allow_html=True)    
            col2.markdown(f"<div class='card yellow'><b>Average Students ({len(average)})</b><br>{average['name'].tolist()}</div>", unsafe_allow_html=True)    
            col3.markdown(f"<div class='card red'><b>Poor Students ({len(poor)})</b><br>{poor['name'].tolist()}</div>", unsafe_allow_html=True)    
    
    # ---------------- ANALYTICS ----------------    
    elif page == "Analytics":    
        st.title("Analytics")    
        if not df.empty:    
            df["avg"] = (df["mst1"] + df["mst2"]) / 2    
            df["best"] = df[["mst1","mst2"]].max(axis=1)    
    
            st.plotly_chart(px.bar(df, x="name", y=["mst1","mst2"]))    
            st.plotly_chart(px.pie(df, values="expenses", names="name"))    
            st.plotly_chart(px.line(df, x="name", y=["avg","best"]))    
    
            st.markdown("### Expense Records (High spenders highlighted)")
            exp_df = df[df["expenses"] > 0]

            def highlight(row):
                if row["expenses"] >= 10000:
                    return ['background-color: rgba(59,130,246,0.3)']*len(row)
                return ['']*len(row)

            st.dataframe(exp_df.style.apply(highlight, axis=1))
    
    # ---------------- SEARCH ----------------    
    elif page == "Search":    
        st.title("Search")    
        search = st.text_input("Enter Name")    
        if search:    
            results = df[df["name"].str.contains(search, case=False)]    
            if not results.empty:    
                st.dataframe(results)    
    
    # ---------------- MANAGE DATA ----------------    
    elif page == "Manage Data":    
        st.title("Manage Data")    
    
        if not df.empty:    
            selected_id = st.selectbox("Select Record ID", df["id"])    
            student = df[df["id"] == selected_id].iloc[0]    
    
            name = st.text_input("Name", student["name"])    
            mst1 = st.number_input("MST1", value=float(student["mst1"]))    
            mst2 = st.number_input("MST2", value=float(student["mst2"]))    
            expenses = st.number_input("Expenses", value=float(student["expenses"]))    
    
            if st.button("Update"):    
                c.execute("""    
                UPDATE students SET name=?, mst1=?, mst2=?, expenses=?    
                WHERE id=?""",    
                (name, mst1, mst2, expenses, selected_id))    
                conn.commit()    
                st.success("Record Updated")    
    
            if st.button("Delete"):    
                c.execute("DELETE FROM students WHERE id=?", (selected_id,))    
                conn.commit()    
                st.warning("Record Deleted")    
    
    # ---------------- EXPORT ----------------    
    elif page == "Export and Logout":    
    
        if st.button("Download CSV"):    
            df.to_csv("acadex.csv", index=False)    
            st.success("CSV saved")    
    
        #  FIXED PDF DOWNLOAD
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer)
        styles = getSampleStyleSheet()

        data = [df.columns.tolist()] + df.values.tolist()

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.grey),
            ('TEXTCOLOR',(0,0),(-1,0),colors.white),
            ('GRID',(0,0),(-1,-1),1,colors.black)
        ]))

        elements = []
        elements.append(Paragraph("ACADEX REPORT", styles["Title"]))
        elements.append(table)

        doc.build(elements)

        st.download_button(
            label=" Download PDF",
            data=buffer.getvalue(),
            file_name="acadex_report.pdf",
            mime="application/pdf"
        )

        if st.button("Logout"):    
            st.session_state.login = False    
            st.rerun()
        st.markdown("""
<hr style="margin-top:30px;">
<div style='text-align:center; font-size:16px;
background: linear-gradient(90deg,#06b6d4,#9333ea);
-webkit-background-clip:text;
-webkit-text-fill-color:transparent;'>
Developed with ❤️ by Krishna Arora and Team
</div>
""", unsafe_allow_html=True)