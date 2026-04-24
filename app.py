import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

# --- INITIAL SETUP ---
load_dotenv()

# Page Config (Browser tab name aur icon)
st.set_page_config(page_title="LeadGenie AI", page_icon="🚀", layout="wide")

# --- CUSTOM CSS (Visual Appeal) ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #f8f9fa;
    }
    /* Buttons Styling */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #007bff;
        color: white;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #0056b3;
        border: none;
    }
    /* Cards for Output */
    .output-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 5px solid #007bff;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATABASE LOGIC ---
def init_db():
    conn = sqlite3.connect('outreach_logs.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS history 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                 timestamp TEXT, 
                 prospect_data TEXT, 
                 generated_content TEXT)''')
    conn.commit()
    conn.close()

def save_log(prospect, content):
    conn = sqlite3.connect('outreach_logs.db')
    c = conn.cursor()
    c.execute("INSERT INTO history (timestamp, prospect_data, generated_content) VALUES (?, ?, ?)",
              (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), prospect, content))
    conn.commit()
    conn.close()

# --- LLM INTEGRATION ---
def generate_ai_email(input_text):
    api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
    if not api_key:
        return "❌ Error: API Key missing!"

    try:
        client = Groq(api_key=api_key)
        prompt = f"Write a professional and highly personalized cold email for: {input_text}. Use a friendly yet corporate tone."
        
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ API Error: {str(e)}"

# --- SIDEBAR (Security & Info) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1055/1055646.png", width=100)
    st.title("Admin Access")
    password = st.text_input("Enter Access Key", type="password")
    
    st.markdown("---")
    st.subheader("App Info 💡")
    st.info("LeadGenie uses Llama 3.1 & SQLite to automate sales outreach.")
    
    if password != "admin123":
        st.error("Invalid Key")
        st.stop()
    else:
        st.success("Authorized")

# --- MAIN UI ---
init_db()

# Header Section
col_h1, col_h2 = st.columns([4, 1])
with col_h1:
    st.title("🚀 LeadGenie: AI Sales Outreach")
    st.write("Transform lead data into high-converting emails instantly.")

# Tabs System
tab1, tab2, tab3 = st.tabs(["✉️ Email Generator", "📊 Data Logs (SQL)", "📝 About Project"])

with tab1:
    col_input, col_output = st.columns([1, 1], gap="large")
    
    with col_input:
        st.subheader("Step 1: Prospect Info")
        raw_input = st.text_area("Paste Lead Bio or LinkedIn Details:", 
                                 placeholder="e.g. Haider is a Python developer looking for cloud automation tools...", 
                                 height=250)
        
        btn_generate = st.button("Generate Magic Email ✨")

    with col_output:
        st.subheader("Step 2: AI Generated Draft")
        if btn_generate:
            if raw_input:
                with st.spinner("Llama 3.1 is thinking..."):
                    result = generate_ai_email(raw_input)
                    st.session_state['output'] = result
                    save_log(raw_input, result)
                    st.markdown(f'<div class="output-card">{result}</div>', unsafe_allow_html=True)
            else:
                st.warning("Please enter some prospect data.")
        elif 'output' in st.session_state:
            st.markdown(f'<div class="output-card">{st.session_state["output"]}</div>', unsafe_allow_html=True)

with tab2:
    st.subheader("💾 Persistent SQL Database")
    conn = sqlite3.connect('outreach_logs.db')
    df = pd.read_sql_query("SELECT * FROM history ORDER BY id DESC", conn)
    st.dataframe(df, use_container_width=True)
    
    if st.button("Refresh Logs 🔄"):
        st.rerun()
    conn.close()

with tab3:
    st.subheader("Project Technical Specs")
    st.write("""
    - **Frontend:** Streamlit 1.56.0
    - **Model:** Llama 3.1 (Groq Cloud API)
    - **Database:** SQLite3 (Server-side persistence)
    - **Architecture:** Python-based Micro-service
    """)
    st.success("This project is ready for professional sales deployment.")