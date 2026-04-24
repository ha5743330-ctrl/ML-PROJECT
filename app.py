import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

# .env file se variables load karne ke liye (Local VS Code setup)
load_dotenv()

# --- PAGE CONFIG ---
st.set_page_config(page_title="LeadGenie AI", page_icon="🚀", layout="wide")

# --- DATABASE SETUP (SQL Requirement) ---
def init_db():
    conn = sqlite3.connect('outreach_logs.db')
    c = conn.cursor()
    # history table for logging every generation
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

# --- LLM INTEGRATION (Core Intelligence) ---
def generate_ai_email(input_text):
    # Pehle secrets check karega (Cloud), phir env (Local)
    api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
    
    if not api_key:
        return "❌ Error: API Key missing! Please check .env or Streamlit Secrets."

    try:
        client = Groq(api_key=api_key)
        prompt = f"Write a short, professional cold email for this prospect: {input_text}. Be concise and include a call to action."
        
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ API Error: {str(e)}"

# --- UI INTERFACE ---
init_db()

st.title("🚀 LeadGenie: AI Sales Outreach")
st.markdown("---")

tab1, tab2 = st.tabs(["✉️ Email Generator", "📊 Data Logs (SQL)"])

with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Prospect Details")
        raw_input = st.text_area("Enter Lead Bio / Info:", 
                                 placeholder="e.g. CEO of a tech startup looking for cloud solutions...", 
                                 height=200)
        
        if st.button("Generate Email ✨"):
            if raw_input:
                with st.spinner("LLM is processing..."):
                    result = generate_ai_email(raw_input)
                    st.session_state['output'] = result
                    save_log(raw_input, result) # SQL Logging
            else:
                st.warning("Please enter some text first.")

    with col2:
        st.subheader("AI Draft")
        if 'output' in st.session_state:
            st.write(st.session_state['output'])
            st.button("Done ✅")

with tab2:
    st.subheader("Database Records")
    conn = sqlite3.connect('outreach_logs.db')
    # Fetch data to show SQL is working
    df = pd.read_sql_query("SELECT * FROM history ORDER BY id DESC", conn)
    st.dataframe(df, use_container_width=True)
    conn.close()
    
    st.caption("Note: These records are stored in a local SQLite database.")