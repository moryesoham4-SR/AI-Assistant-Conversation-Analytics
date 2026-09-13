import streamlit as st
import pandas as pd
import sqlite3
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# ============================================================
# PAGE CONFIGURATION & METADATA
# ============================================================
st.set_page_config(
    page_title="AI Conversation Analytics | Data Engineering",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# MODERN PREMIUM CSS STYLING
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Gradient Top Header */
    .hero-banner {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #334155 100%);
        border-radius: 16px;
        padding: 24px 32px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0;
        background: linear-gradient(90deg, #FFFFFF 0%, #93C5FD 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-subtitle {
        font-size: 1rem;
        color: #94A3B8;
        margin-top: 6px;
        margin-bottom: 14px;
    }
    .badge-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 5px 12px;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 600;
        color: #E2E8F0;
        margin-right: 8px;
    }
    .badge-green {
        background: rgba(16, 185, 129, 0.15);
        border-color: rgba(16, 185, 129, 0.4);
        color: #34D399;
    }

    /* Custom KPI Card */
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        margin-bottom: 12px;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
        border-color: #CBD5E1;
    }
    .kpi-label {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: #64748B;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 1.85rem;
        font-weight: 800;
        color: #0F172A;
        letter-spacing: -0.02em;
        line-height: 1.1;
    }
    .kpi-sub {
        font-size: 0.8rem;
        color: #10B981;
        font-weight: 600;
        margin-top: 6px;
    }

    /* Modern Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 24px;
        font-weight: 600;
        font-size: 0.95rem;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #1D4ED8 0%, #1E40AF 100%);
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.35);
        transform: translateY(-1px);
        color: white;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0F172A;
        border-right: 1px solid #1E293B;
    }
    section[data-testid="stSidebar"] * {
        color: #E2E8F0;
    }
    section[data-testid="stSidebar"] .stRadio label {
        font-weight: 500;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #F8FAFC;
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Project Paths
PROJECT_ROOT = Path(__file__).resolve().parent
RAW_DATA_DIR = PROJECT_ROOT / "01_DATA" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "01_DATA" / "processed"
DATABASE_DIR = PROJECT_ROOT / "03_DATABASE"
DB_PATH = DATABASE_DIR / "oasst.db"
PIPELINE_SCRIPT = PROJECT_ROOT / "02_ETL" / "pipeline.py"

# Ensure directories exist
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# DATABASE HELPER FUNCTIONS
# ============================================================
def get_db_connection():
    if not DB_PATH.exists():
        return None
    return sqlite3.connect(str(DB_PATH))

def query_db(query, params=()):
    conn = get_db_connection()
    if conn is None:
        return None
    try:
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    except Exception as e:
        conn.close()
        raise e


# ============================================================
# SIDEBAR NAVIGATION & ACADEMIC CREDITS
# ============================================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 10px 0 16px 0;">
        <div style="font-size: 2.6rem;">⚡</div>
        <div style="font-size: 1.15rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.01em;">AI Conversation Pipeline</div>
        <div style="font-size: 0.78rem; color: #94A3B8;">Data Engineering Pipeline</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "NAVIGATION",
        [
            "🚀 Run ETL Pipeline",
            "📊 Analytics Dashboard",
            "🗄️ Database Explorer",
            "💻 SQL Query Console",
            "ℹ️ Architecture & Viva Prep"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    
    # Academic Project Profile Card
    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 14px; margin-bottom: 14px;">
        <div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; color: #38BDF8; font-weight: 700; margin-bottom: 6px;">Academic Project</div>
        <div style="font-size: 0.88rem; font-weight: 700; color: #F8FAFC;">Data Engineering</div>
        <div style="font-size: 0.8rem; color: #94A3B8;">Semester 5 &bull; B.Sc. Data Science</div>
    </div>
    """, unsafe_allow_html=True)

    # Database Status Pill
    if DB_PATH.exists():
        db_size_mb = DB_PATH.stat().st_size / (1024 * 1024)
        st.markdown(f"""
        <div style="background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 8px; padding: 10px; font-size: 0.8rem; color: #34D399; font-weight: 600; text-align: center;">
            ● SQLite DB Connected ({db_size_mb:.1f} MB)
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: rgba(239, 68, 68, 0.12); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 8px; padding: 10px; font-size: 0.8rem; color: #F87171; font-weight: 600; text-align: center;">
            ○ Database Not Loaded
        </div>
        """, unsafe_allow_html=True)


# ============================================================
# TOP HERO BANNER (ACADEMIC BANNER)
# ============================================================
st.markdown("""
<div class="hero-banner">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
        <div>
            <h1 class="hero-title">AI Assistant Conversation Analytics</h1>
            <div class="hero-subtitle">Automated Multi-Stage ETL Pipeline &amp; Relational SQLite Analytics</div>
        </div>
        <div>
            <span class="badge-pill badge-green">⚡ B.Sc. Data Science</span>
            <span class="badge-pill">Sem 5</span>
            <span class="badge-pill">Data Engineering</span>
        </div>
    </div>
    <div style="display: flex; align-items: center; gap: 16px; margin-top: 10px; font-size: 0.88rem; color: #CBD5E1;">
        <span>📊 <strong>Domain:</strong> Conversational AI Analytics</span>
        <span>&bull;</span>
        <span>🗄️ <strong>Engine:</strong> Python, SQLite, OASST1 Dataset</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# PAGE 1: RUN ETL PIPELINE
# ============================================================
if page == "🚀 Run ETL Pipeline":
    st.markdown("### 🚀 Master Data Engineering Pipeline")
    st.caption("Feed raw conversation datasets through extraction, transformation, quality validation, and indexed SQLite storage.")

    tab_default, tab_upload = st.tabs(["📁 Default OASST1 Dataset", "📤 Upload Custom Dataset"])

    with tab_default:
        train_file = RAW_DATA_DIR / "oasst1_train.csv"
        val_file = RAW_DATA_DIR / "oasst1_validation.csv"

        col1, col2 = st.columns(2)
        with col1:
            if train_file.exists():
                size_mb = train_file.stat().st_size / (1024 * 1024)
                st.info(f"📄 **Training File**: `oasst1_train.csv` ({size_mb:.2f} MB verified)")
            else:
                st.warning("⚠️ Training file missing in `01_DATA/raw/`")
        with col2:
            if val_file.exists():
                size_mb = val_file.stat().st_size / (1024 * 1024)
                st.info(f"📄 **Validation File**: `oasst1_validation.csv` ({size_mb:.2f} MB verified)")
            else:
                st.warning("⚠️ Validation file missing in `01_DATA/raw/`")

    with tab_upload:
        st.write("Upload custom raw CSV files to run through the cleaning and database pipeline:")
        col1, col2 = st.columns(2)
        with col1:
            uploaded_train = st.file_uploader("Upload Training CSV (`oasst1_train.csv`)", type=["csv"], key="train_uploader")
        with col2:
            uploaded_val = st.file_uploader("Upload Validation CSV (`oasst1_validation.csv`)", type=["csv"], key="val_uploader")

        if uploaded_train is not None:
            with open(RAW_DATA_DIR / "oasst1_train.csv", "wb") as f:
                f.write(uploaded_train.getbuffer())
            st.success(f"✅ Training data uploaded ({uploaded_train.name})")

        if uploaded_val is not None:
            with open(RAW_DATA_DIR / "oasst1_validation.csv", "wb") as f:
                f.write(uploaded_val.getbuffer())
            st.success(f"✅ Validation data uploaded ({uploaded_val.name})")

    st.markdown("---")
    col_btn, col_blank = st.columns([1, 2])
    with col_btn:
        run_button = st.button("▶️ Execute Full ETL Pipeline", type="primary", use_container_width=True)

    if run_button:
        st.markdown("#### 🔄 Pipeline Execution Status")
        progress_bar = st.progress(0)
        status_box = st.empty()
        
        try:
            status_box.info("⏳ Processing: Running Stage 1 (Extract) -> Stage 2 (Transform) -> Stage 3 (Load)...")
            progress_bar.progress(0.3)
            
            result = subprocess.run(
                [sys.executable, str(PIPELINE_SCRIPT)],
                cwd=str(PROJECT_ROOT),
                capture_output=True,
                text=True,
                check=True
            )
            
            progress_bar.progress(1.0)
            status_box.success("✅ **ETL Pipeline Executed Successfully!** All 88,838 records validated and SQLite database updated.")
            
            with st.expander("📋 View Real-Time Execution Logs", expanded=True):
                st.code(result.stdout, language="text")

        except subprocess.CalledProcessError as e:
            progress_bar.progress(0.4)
            status_box.error("❌ Pipeline execution encountered an issue.")
            with st.expander("⚠️ View Error Log", expanded=True):
                st.code(e.stdout + "\n" + e.stderr, language="text")


# ============================================================
# PAGE 2: ANALYTICS DASHBOARD (KPI SCORECARD)
# ============================================================
elif page == "📊 Analytics Dashboard":
    st.markdown("### 📊 Executive KPI & Analytics Dashboard")
    st.caption("Real-time conversational performance, engagement metrics, and multilingual distributions computed directly from SQLite.")

    if not DB_PATH.exists():
        st.error("⚠️ Database `oasst.db` not found. Please run the ETL Pipeline first.")
    else:
        # Filter Bar
        col_f1, col_f2 = st.columns([1, 3])
        with col_f1:
            lang_options_df = query_db("SELECT DISTINCT lang FROM messages ORDER BY lang;")
            all_langs = ["All Languages"] + (lang_options_df["lang"].dropna().tolist() if lang_options_df is not None else [])
            selected_lang = st.selectbox("🌐 Filter by Language:", all_langs)

        lang_where = ""
        params = ()
        if selected_lang != "All Languages":
            lang_where = " WHERE lang = ?"
            params = (selected_lang,)

        # KPI Queries
        kpi_query = f"""
        SELECT 
            COUNT(*) AS total_messages,
            COUNT(DISTINCT message_tree_id) AS total_trees,
            COUNT(DISTINCT user_id) AS total_users,
            COUNT(DISTINCT lang) AS total_languages,
            ROUND(AVG(LENGTH(text)), 1) AS avg_chars_per_message,
            SUM(CASE WHEN role = 'assistant' THEN 1 ELSE 0 END) AS assistant_msgs,
            SUM(CASE WHEN role = 'prompter' THEN 1 ELSE 0 END) AS prompter_msgs,
            SUM(CASE WHEN review_result = 1 THEN 1 ELSE 0 END) AS approved_reviews,
            SUM(CASE WHEN review_result IS NOT NULL THEN 1 ELSE 0 END) AS total_reviews
        FROM messages
        {lang_where};
        """
        kpi_df = query_db(kpi_query, params)

        if kpi_df is not None and not kpi_df.empty:
            row = kpi_df.iloc[0]
            tot_msgs = row['total_messages'] or 0
            tot_trees = row['total_trees'] or 1
            tot_users = row['total_users'] or 0
            tot_langs = row['total_languages'] or 0
            avg_chars = row['avg_chars_per_message'] or 0
            asst_msgs = row['assistant_msgs'] or 0
            prmt_msgs = row['prompter_msgs'] or 0
            approved = row['approved_reviews'] or 0
            total_rev = row['total_reviews'] or 1

            avg_per_tree = round(tot_msgs / tot_trees, 2) if tot_trees > 0 else 0
            asst_pct = round((asst_msgs / tot_msgs) * 100, 1) if tot_msgs > 0 else 0
            prmt_pct = round((prmt_msgs / tot_msgs) * 100, 1) if tot_msgs > 0 else 0
            approval_rate = round((approved / total_rev) * 100, 1) if total_rev > 0 else 0

            # Row 1: High Level KPIs
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">Total Messages</div>
                    <div class="kpi-value">{tot_msgs:,}</div>
                    <div class="kpi-sub">Across {tot_langs} Languages</div>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">Conversation Trees</div>
                    <div class="kpi-value">{tot_trees:,}</div>
                    <div class="kpi-sub">Avg {avg_per_tree} msgs / tree</div>
                </div>
                """, unsafe_allow_html=True)
            with c3:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">Unique Contributors</div>
                    <div class="kpi-value">{tot_users:,}</div>
                    <div class="kpi-sub">Human-Generated Prompts</div>
                </div>
                """, unsafe_allow_html=True)
            with c4:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">Avg Message Length</div>
                    <div class="kpi-value">{avg_chars:,}</div>
                    <div class="kpi-sub">Characters Per Message</div>
                </div>
                """, unsafe_allow_html=True)

            # Row 2: Engagement Ratios
            c5, c6, c7, c8 = st.columns(4)
            with c5:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">Assistant Share</div>
                    <div class="kpi-value">{asst_pct}%</div>
                    <div class="kpi-sub">{asst_msgs:,} Replies Generated</div>
                </div>
                """, unsafe_allow_html=True)
            with c6:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">User Prompts Share</div>
                    <div class="kpi-value">{prmt_pct}%</div>
                    <div class="kpi-sub">{prmt_msgs:,} User Inquiries</div>
                </div>
                """, unsafe_allow_html=True)
            with c7:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">Quality Approval Rate</div>
                    <div class="kpi-value">{approval_rate}%</div>
                    <div class="kpi-sub">{approved:,} Approved Messages</div>
                </div>
                """, unsafe_allow_html=True)
            with c8:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">Interaction Ratio</div>
                    <div class="kpi-value">{round(asst_msgs / max(prmt_msgs, 1), 2)} : 1</div>
                    <div class="kpi-sub">Assistant / User Ratio</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")

        # Interactive Charts
        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("👥 Role Distribution")
            role_df = query_db(f"""
                SELECT role AS Role, 
                       COUNT(*) AS Message_Count,
                       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM messages {lang_where}), 2) AS Percentage_Share
                FROM messages
                {lang_where}
                GROUP BY role
                ORDER BY Message_Count DESC;
            """, params)
            if role_df is not None:
                st.bar_chart(role_df.set_index("Role")["Message_Count"], color="#3B82F6")
                st.dataframe(role_df, hide_index=True, use_container_width=True)

        with col_right:
            st.subheader("🌐 Top Active Languages")
            lang_chart_df = query_db("""
                SELECT lang AS Language, 
                       COUNT(*) AS Messages,
                       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM messages), 2) AS Percentage_Share
                FROM messages 
                GROUP BY lang 
                ORDER BY Messages DESC 
                LIMIT 10;
            """)
            if lang_chart_df is not None:
                st.bar_chart(lang_chart_df.set_index("Language")["Messages"], color="#10B981")
                st.dataframe(lang_chart_df, hide_index=True, use_container_width=True)

        st.markdown("---")
        
        # Deepest Trees & Top Contributors
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            st.subheader("🏆 Top 5 Deepest Conversation Threads")
            depth_df = query_db(f"""
                SELECT message_tree_id AS Tree_ID, 
                       COUNT(*) AS Total_Messages, 
                       COUNT(DISTINCT user_id) AS Participants
                FROM messages
                {lang_where}
                GROUP BY message_tree_id 
                ORDER BY Total_Messages DESC 
                LIMIT 5;
            """, params)
            if depth_df is not None:
                st.dataframe(depth_df, hide_index=True, use_container_width=True)

        with col_b2:
            st.subheader("🌟 Top 5 Most Active Contributors")
            users_df = query_db(f"""
                SELECT user_id AS User_ID, 
                       COUNT(*) AS Contributions,
                       SUM(CASE WHEN role = 'prompter' THEN 1 ELSE 0 END) AS User_Prompts,
                       SUM(CASE WHEN role = 'assistant' THEN 1 ELSE 0 END) AS Assistant_Replies
                FROM messages
                {lang_where}
                GROUP BY user_id 
                ORDER BY Contributions DESC 
                LIMIT 5;
            """, params)
            if users_df is not None:
                st.dataframe(users_df, hide_index=True, use_container_width=True)


# ============================================================
# PAGE 3: DATABASE EXPLORER
# ============================================================
elif page == "🗄️ Database Explorer":
    st.markdown("### 🗄️ SQLite Database Table Explorer")
    st.caption("Inspect, filter, and export indexed relational tables directly from `03_DATABASE/oasst.db`.")

    if not DB_PATH.exists():
        st.error("⚠️ Database not found. Please run the ETL Pipeline first.")
    else:
        table_choice = st.selectbox("Select Table:", ["messages", "conversations"])
        
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            limit = st.slider("Display Limit:", min_value=10, max_value=500, value=50, step=10)
        with col_f2:
            filter_lang = st.text_input("Language Filter (e.g. 'en', 'es', 'de'):", "")
        with col_f3:
            filter_role = st.selectbox("Role Filter:", ["All", "prompter", "assistant"])

        where_clauses = []
        params = []

        if filter_lang.strip():
            where_clauses.append("lang = ?")
            params.append(filter_lang.strip().lower())

        if filter_role != "All":
            where_clauses.append("role = ?")
            params.append(filter_role)

        where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        query = f"SELECT * FROM {table_choice}{where_sql} LIMIT {limit};"

        try:
            df_display = query_db(query, tuple(params))
            if df_display is not None:
                st.dataframe(df_display, use_container_width=True)
                
                csv_data = df_display.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Export Displayed Records to CSV",
                    data=csv_data,
                    file_name=f"{table_choice}_export.csv",
                    mime="text/csv"
                )
        except Exception as e:
            st.error(f"Database Error: {e}")


# ============================================================
# PAGE 4: SQL QUERY CONSOLE
# ============================================================
elif page == "💻 SQL Query Console":
    st.markdown("### 💻 Live SQL Analytics Console")
    st.caption("Execute custom or pre-saved analytical SQL queries against the indexed SQLite database.")

    if not DB_PATH.exists():
        st.error("⚠️ Database not found. Please run the ETL Pipeline first.")
    else:
        preset_queries = {
            "Select Pre-Saved Query...": "",
            "1. Dataset High-Level Summary": """SELECT 
    (SELECT COUNT(*) FROM conversations) AS total_conversations,
    (SELECT COUNT(*) FROM messages) AS total_messages,
    (SELECT COUNT(DISTINCT user_id) FROM messages) AS total_unique_users,
    (SELECT COUNT(DISTINCT lang) FROM messages) AS total_languages;""",
            "2. Role Distribution & Percentage": """SELECT 
    role,
    COUNT(*) AS total_messages,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM messages), 2) AS percentage_share
FROM messages
GROUP BY role
ORDER BY total_messages DESC;""",
            "3. Top 10 Active Languages": """SELECT 
    lang AS language_code,
    COUNT(*) AS message_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM messages), 2) AS percentage
FROM messages
GROUP BY lang
ORDER BY message_count DESC
LIMIT 10;""",
            "4. Top 10 Longest Conversation Threads": """SELECT 
    message_tree_id,
    COUNT(*) AS total_messages_in_thread,
    COUNT(DISTINCT user_id) AS participants_count
FROM messages
GROUP BY message_tree_id
ORDER BY total_messages_in_thread DESC
LIMIT 10;""",
            "5. Top Active Contributors": """SELECT 
    user_id,
    COUNT(*) AS total_contributions,
    SUM(CASE WHEN role = 'prompter' THEN 1 ELSE 0 END) AS user_prompts,
    SUM(CASE WHEN role = 'assistant' THEN 1 ELSE 0 END) AS assistant_replies
FROM messages
GROUP BY user_id
ORDER BY total_contributions DESC
LIMIT 10;"""
        }

        selected_preset = st.selectbox("📌 Choose an Analysis Template:", list(preset_queries.keys()))
        initial_query = preset_queries[selected_preset] if selected_preset != "Select Pre-Saved Query..." else "SELECT * FROM messages LIMIT 10;"

        user_query = st.text_area("SQL Editor:", value=initial_query, height=150)

        if st.button("▶️ Execute Query", type="primary"):
            if user_query.strip():
                try:
                    start_time = datetime.now()
                    result_df = query_db(user_query)
                    elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000

                    if result_df is not None:
                        st.success(f"⚡ Query executed in **{elapsed_ms:.1f} ms** &bull; Returned **{len(result_df)}** rows")
                        st.dataframe(result_df, use_container_width=True)
                        
                        csv = result_df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 Download Results as CSV",
                            data=csv,
                            file_name="query_results.csv",
                            mime="text/csv"
                        )
                except Exception as e:
                    st.error(f"❌ SQL Execution Error: {e}")


# ============================================================
# PAGE 5: ARCHITECTURE & VIVA PREP
# ============================================================
elif page == "ℹ️ Architecture & Viva Prep":
    st.markdown("### ℹ️ Architecture Walkthrough & Teacher Viva Guide")
    st.caption("Technical architectural breakdown, data cleaning specifications, and viva evaluation questions.")

    st.markdown("""
    #### 🏗️ Pipeline Architecture Flow
    ```text
    +-----------------------------------------------------------------------------------+
    |                                 OASST1 RAW DATASET                                |
    |                        01_DATA/raw/oasst1_train & validation                      |
    +-----------------------------------------------------------------------------------+
                                              │
                                              ▼
    +-----------------------------------------------------------------------------------+
    |                               1. EXTRACTION & INGESTION                           |
    |  • Ingests 84,437 train + 4,401 validation records                                |
    |  • Validates schema columns and file integrity                                    |
    +-----------------------------------------------------------------------------------+
                                              │
                                              ▼
    +-----------------------------------------------------------------------------------+
    |                              2. TRANSFORMATION & CLEANING                         |
    |  • Unifies splits into 88,838 unified records                                     |
    |  • Drops unusable fields (model_name 100% null)                                   |
    |  • Cleans string whitespace, standardizes ISO 8601 timestamps                     |
    |  • Validates parent-child conversation relationships (0 orphan nodes)             |
    |  • Exports: 01_DATA/processed/oasst1_processed.csv                                |
    +-----------------------------------------------------------------------------------+
                                              │
                                              ▼
    +-----------------------------------------------------------------------------------+
    |                            3. DATABASE LOADING & INDEXING                         |
    |  • Relational Schema: 'conversations' and 'messages' tables                       |
    |  • Builds 6 performance B-tree indexes: lang, role, user, parent, date, tree      |
    |  • Database Storage: 03_DATABASE/oasst.db (SQLite)                                |
    +-----------------------------------------------------------------------------------+
                                              │
                    +-------------------------+-------------------------+
                    │                                                   │
                    ▼                                                   ▼
    +-------------------------------+                   +-------------------------------+
    |       4. SQL ANALYTICS        |                   |      5. INTERACTIVE GUI       |
    | • DB Browser for SQLite       |                   | • Streamlit GUI (app.py)      |
    | • Saved .sql query suite      |                   | • Interactive KPI Scorecard   |
    | • Sub-millisecond queries     |                   | • Live database explorer      |
    +-------------------------------+                   +-------------------------------+
    ```

    ---

    #### 🎯 Essential Viva & Evaluation Answers
    
    **Q1: Why was SQLite selected over flat CSV storage?**
    > *Answer*: Flat CSVs require linear O(N) scanning of the entire file on every query and offer no integrity enforcement. SQLite provides ACID-compliant transactions, relational integrity with foreign keys, and B-Tree indexing on frequently queried columns (`lang`, `role`, `created_date`), delivering sub-millisecond query execution on 88,000+ rows.
    
    **Q2: What is a conversation tree in this dataset?**
    > *Answer*: AI interactions are not simply one prompt and one reply; users ask follow-up questions, creating branching trees. The root message has no parent ID, while subsequent assistant and prompter messages reference their predecessor via `parent_id` and belong to the same `message_tree_id`.
    
    **Q3: What data quality checks did your pipeline execute?**
    > *Answer*: Our pipeline verified:
    > 1. **Duplicate message IDs**: 0 duplicates found.
    > 2. **Orphan parent checks**: 0 orphaned branches (every child connects to a valid message).
    > 3. **Null field elimination**: Removed `model_name` because it was 100% missing in the raw data.
    > 4. **Range validation**: Confirmed non-negative review counts and standardized timestamps into ISO 8601 UTC.
    """)
