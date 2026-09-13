import streamlit as st
import pandas as pd
import sqlite3
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# ============================================================
# PAGE CONFIGURATION & STYLING
# ============================================================
st.set_page_config(
    page_title="AI Conversation Analytics | Data Engineering Pipeline",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .status-box {
        border-radius: 8px;
        padding: 12px 18px;
        margin-top: 10px;
        margin-bottom: 15px;
    }
    .stButton>button {
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
# SIDEBAR NAVIGATION
# ============================================================
st.sidebar.image("https://img.icons8.com/color/96/artificial-intelligence.png", width=70)
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    [
        "🚀 Run ETL Pipeline",
        "📊 Analytics Dashboard",
        "🗄️ Database Explorer",
        "💻 SQL Query Console",
        "ℹ️ Architecture & Viva Prep"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 💾 Database Status")
if DB_PATH.exists():
    db_size_mb = DB_PATH.stat().st_size / (1024 * 1024)
    st.sidebar.success(f"Connected: `oasst.db` ({db_size_mb:.2f} MB)")
else:
    st.sidebar.warning("⚠️ `oasst.db` not found. Please run the ETL Pipeline.")

st.sidebar.markdown("---")
st.sidebar.caption("AI Assistant Conversation Analytics • End-to-End Pipeline")


# ============================================================
# PAGE 1: RUN ETL PIPELINE
# ============================================================
if page == "🚀 Run ETL Pipeline":
    st.markdown('<div class="main-header">🚀 End-to-End Data Pipeline Runner</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Feed raw conversation datasets into the pipeline and watch the data flow through extraction, transformation, validation, and database loading.</div>', unsafe_allow_html=True)

    tab_upload, tab_default = st.tabs(["📤 Upload New Dataset", "📁 Use Default OASST1 Dataset"])

    with tab_upload:
        st.markdown("#### Upload Custom CSV Dataset")
        st.write("Upload your raw training and validation CSV files to process them through the pipeline:")
        
        col1, col2 = st.columns(2)
        with col1:
            uploaded_train = st.file_uploader("Upload Training CSV (`oasst1_train.csv`)", type=["csv"], key="train_uploader")
        with col2:
            uploaded_val = st.file_uploader("Upload Validation CSV (`oasst1_validation.csv`)", type=["csv"], key="val_uploader")

        if uploaded_train is not None:
            train_save_path = RAW_DATA_DIR / "oasst1_train.csv"
            with open(train_save_path, "wb") as f:
                f.write(uploaded_train.getbuffer())
            st.success(f"✅ Training data saved ({uploaded_train.name})")

        if uploaded_val is not None:
            val_save_path = RAW_DATA_DIR / "oasst1_validation.csv"
            with open(val_save_path, "wb") as f:
                f.write(uploaded_val.getbuffer())
            st.success(f"✅ Validation data saved ({uploaded_val.name})")

    with tab_default:
        st.markdown("#### Default OASST1 Dataset")
        train_file = RAW_DATA_DIR / "oasst1_train.csv"
        val_file = RAW_DATA_DIR / "oasst1_validation.csv"

        col1, col2 = st.columns(2)
        with col1:
            if train_file.exists():
                size_mb = train_file.stat().st_size / (1024 * 1024)
                st.info(f"📄 `01_DATA/raw/oasst1_train.csv` ({size_mb:.2f} MB ready)")
            else:
                st.warning("⚠️ Training file missing in `01_DATA/raw/`")
        with col2:
            if val_file.exists():
                size_mb = val_file.stat().st_size / (1024 * 1024)
                st.info(f"📄 `01_DATA/raw/oasst1_validation.csv` ({size_mb:.2f} MB ready)")
            else:
                st.warning("⚠️ Validation file missing in `01_DATA/raw/`")

    st.markdown("---")
    st.markdown("### ⚡ Pipeline Execution Controls")

    col_btn, col_info = st.columns([1, 2])
    with col_btn:
        run_button = st.button("▶️ Run Full ETL Pipeline", type="primary", use_container_width=True)

    if run_button:
        st.markdown("#### 🔄 Pipeline Progress")
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.info("🚀 Initiating master pipeline execution...")
            progress_bar.progress(0.2)
            
            # Execute pipeline
            result = subprocess.run(
                [sys.executable, str(PIPELINE_SCRIPT)],
                cwd=str(PROJECT_ROOT),
                capture_output=True,
                text=True,
                check=True
            )
            
            progress_bar.progress(1.0)
            status_text.success("🎉 ETL Pipeline Completed Successfully! Database is updated.")
            st.balloons()
            
            with st.expander("📋 View Detailed Pipeline Execution Logs", expanded=True):
                st.code(result.stdout, language="text")

        except subprocess.CalledProcessError as e:
            progress_bar.progress(0.4)
            status_text.error("❌ Pipeline execution encountered an error.")
            with st.expander("⚠️ View Error Logs", expanded=True):
                st.code(e.stdout + "\n" + e.stderr, language="text")


# ============================================================
# PAGE 2: ANALYTICS DASHBOARD (KPI SCORECARD & INSIGHTS)
# ============================================================
elif page == "📊 Analytics Dashboard":
    st.markdown('<div class="main-header">📊 Executive KPI & Analytics Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Live business intelligence, operational metrics, and conversation analytics computed directly from SQLite.</div>', unsafe_allow_html=True)

    if not DB_PATH.exists():
        st.error("⚠️ Database `oasst.db` not found. Please run the ETL Pipeline first from the **Run ETL Pipeline** tab.")
    else:
        # Dashboard Filters
        st.markdown("#### 🔍 Filter Dashboard")
        col_f1, col_f2 = st.columns([1, 2])
        with col_f1:
            lang_options_df = query_db("SELECT DISTINCT lang FROM messages ORDER BY lang;")
            all_langs = ["All Languages"] + (lang_options_df["lang"].dropna().tolist() if lang_options_df is not None else [])
            selected_lang = st.selectbox("Filter by Language:", all_langs)
        
        lang_where = ""
        params = ()
        if selected_lang != "All Languages":
            lang_where = " WHERE lang = ?"
            params = (selected_lang,)

        # ------------------------------------------------------------
        # 1. CORE EXECUTIVE KPIS
        # ------------------------------------------------------------
        st.markdown("### 📌 Executive KPI Summary")
        
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

            # Row 1: High Level Metrics
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Messages", f"{tot_msgs:,}", f"{tot_langs} Languages")
            c2.metric("Conversation Trees", f"{tot_trees:,}", f"Avg {avg_per_tree} msgs/tree")
            c3.metric("Unique Contributors", f"{tot_users:,}", "Global Community")
            c4.metric("Avg Message Length", f"{avg_chars:,} chars", "Across all messages")

            # Row 2: Quality & Engagement KPIs
            st.markdown(" ")
            c5, c6, c7, c8 = st.columns(4)
            c5.metric("Assistant Share", f"{asst_pct}%", f"{asst_msgs:,} replies")
            c6.metric("User Prompter Share", f"{prmt_pct}%", f"{prmt_msgs:,} prompts")
            c7.metric("Review Quality Rate", f"{approval_rate}%", f"{approved:,} approved")
            c8.metric("Interaction Ratio", f"{round(asst_msgs / max(prmt_msgs, 1), 2)} : 1", "Assistant / Prompter")

        st.markdown("---")

        # ------------------------------------------------------------
        # 2. CHARTS & VISUAL ANALYTICS
        # ------------------------------------------------------------
        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("👥 Role Distribution (Assistant vs Prompter)")
            role_df = query_db(f"""
                SELECT role, 
                       COUNT(*) AS message_count,
                       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM messages {lang_where}), 2) AS percentage
                FROM messages
                {lang_where}
                GROUP BY role
                ORDER BY message_count DESC;
            """, params)
            if role_df is not None:
                st.bar_chart(role_df.set_index("role")["message_count"], color="#2563EB")
                st.dataframe(role_df, hide_index=True, use_container_width=True)

        with col_right:
            st.subheader("🌐 Top Active Languages")
            lang_chart_df = query_db("""
                SELECT lang AS Language, 
                       COUNT(*) AS Messages,
                       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM messages), 2) AS Pct_Share
                FROM messages 
                GROUP BY lang 
                ORDER BY Messages DESC 
                LIMIT 10;
            """)
            if lang_chart_df is not None:
                st.bar_chart(lang_chart_df.set_index("Language")["Messages"], color="#059669")
                st.dataframe(lang_chart_df, hide_index=True, use_container_width=True)

        st.markdown("---")

        # ------------------------------------------------------------
        # 3. CONVERSATION DEPTH & POWER USERS
        # ------------------------------------------------------------
        col_bottom1, col_bottom2 = st.columns(2)
        
        with col_bottom1:
            st.subheader("🏆 Top 5 Deepest Conversation Threads")
            depth_df = query_db(f"""
                SELECT message_tree_id AS Tree_ID, 
                       COUNT(*) AS Messages_Count, 
                       COUNT(DISTINCT user_id) AS Participants
                FROM messages
                {lang_where}
                GROUP BY message_tree_id 
                ORDER BY Messages_Count DESC 
                LIMIT 5;
            """, params)
            if depth_df is not None:
                st.dataframe(depth_df, hide_index=True, use_container_width=True)

        with col_bottom2:
            st.subheader("🌟 Top 5 Most Active Users")
            users_df = query_db(f"""
                SELECT user_id AS User_ID, 
                       COUNT(*) AS Total_Contributions,
                       SUM(CASE WHEN role = 'prompter' THEN 1 ELSE 0 END) AS Prompts,
                       SUM(CASE WHEN role = 'assistant' THEN 1 ELSE 0 END) AS Replies
                FROM messages
                {lang_where}
                GROUP BY user_id 
                ORDER BY Total_Contributions DESC 
                LIMIT 5;
            """, params)
            if users_df is not None:
                st.dataframe(users_df, hide_index=True, use_container_width=True)


# ============================================================
# PAGE 3: DATABASE EXPLORER
# ============================================================
elif page == "🗄️ Database Explorer":
    st.markdown('<div class="main-header">🗄️ SQLite Database Table Explorer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Browse, search, and filter the indexed relational SQLite tables.</div>', unsafe_allow_html=True)

    if not DB_PATH.exists():
        st.error("⚠️ Database not found. Please run the ETL Pipeline first.")
    else:
        table_choice = st.selectbox("Select Table to Inspect:", ["messages", "conversations"])
        
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            limit = st.slider("Rows to display:", min_value=10, max_value=500, value=50, step=10)
        with col_f2:
            filter_lang = st.text_input("Filter by Language Code (e.g. 'en', 'es', 'de'):", "")
        with col_f3:
            filter_role = st.selectbox("Filter by Role:", ["All", "prompter", "assistant"])

        # Construct filter query
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
                st.success(f"Displaying **{len(df_display)}** rows from `{table_choice}`")
                st.dataframe(df_display, use_container_width=True)
                
                # CSV Export button
                csv_data = df_display.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Displayed Data as CSV",
                    data=csv_data,
                    file_name=f"{table_choice}_filtered.csv",
                    mime="text/csv"
                )
        except Exception as e:
            st.error(f"Error reading database: {e}")


# ============================================================
# PAGE 4: SQL QUERY CONSOLE
# ============================================================
elif page == "💻 SQL Query Console":
    st.markdown('<div class="main-header">💻 Live SQL Query Console</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Execute real-time SQL queries directly against the indexed SQLite database.</div>', unsafe_allow_html=True)

    if not DB_PATH.exists():
        st.error("⚠️ Database not found. Please run the ETL Pipeline first.")
    else:
        preset_queries = {
            "Select Pre-Saved Query...": "",
            "1. Dataset Overall Statistics": """SELECT 
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
            "3. Top 10 Most Active Languages": """SELECT 
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
            "5. Most Active Contributors": """SELECT 
    user_id,
    COUNT(*) AS total_contributions,
    SUM(CASE WHEN role = 'prompter' THEN 1 ELSE 0 END) AS user_prompts,
    SUM(CASE WHEN role = 'assistant' THEN 1 ELSE 0 END) AS assistant_replies
FROM messages
GROUP BY user_id
ORDER BY total_contributions DESC
LIMIT 10;"""
        }

        selected_preset = st.selectbox("📌 Choose a Pre-configured Query (or write your own below):", list(preset_queries.keys()))

        initial_query = preset_queries[selected_preset] if selected_preset != "Select Pre-Saved Query..." else "SELECT * FROM messages LIMIT 10;"

        user_query = st.text_area("SQL Editor:", value=initial_query, height=160)

        col_exec, col_clear = st.columns([1, 4])
        with col_exec:
            execute_btn = st.button("▶️ Execute SQL", type="primary", use_container_width=True)

        if execute_btn or selected_preset != "Select Pre-Saved Query...":
            if user_query.strip():
                try:
                    start_time = datetime.now()
                    result_df = query_db(user_query)
                    elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000

                    if result_df is not None:
                        st.success(f"⚡ Query executed in **{elapsed_ms:.1f} ms** • **{len(result_df)}** rows returned")
                        st.dataframe(result_df, use_container_width=True)
                        
                        # Download button
                        csv = result_df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 Export Query Results to CSV",
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
    st.markdown('<div class="main-header">ℹ️ System Architecture & Teacher Viva Guide</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Key technical details, architecture walkthrough, and answers to common evaluation questions.</div>', unsafe_allow_html=True)

    st.markdown("""
    ### 🏗️ Complete Pipeline Architecture
    ```
    +-----------------------------------------------------------------------------------+
    |                                 OASST1 RAW DATASET                                |
    |                        01_DATA/raw/oasst1_train & validation                      |
    +-----------------------------------------------------------------------------------+
                                              |
                                              v
    +-----------------------------------------------------------------------------------+
    |                               1. EXTRACTION & INGESTION                           |
    |  • Ingests 84,437 train + 4,401 validation records                                |
    |  • Validates schema columns and file integrity                                    |
    +-----------------------------------------------------------------------------------+
                                              |
                                              v
    +-----------------------------------------------------------------------------------+
    |                              2. TRANSFORMATION & CLEANING                         |
    |  • Unifies splits into 88,838 unified records                                     |
    |  • Drops unusable fields (model_name 100% null)                                   |
    |  • Cleans string whitespace, standardizes ISO 8601 timestamps                     |
    |  • Validates parent-child conversation relationships (0 orphan nodes)             |
    |  • Exports: 01_DATA/processed/oasst1_processed.csv                                |
    +-----------------------------------------------------------------------------------+
                                              |
                                              v
    +-----------------------------------------------------------------------------------+
    |                            3. DATABASE LOADING & INDEXING                         |
    |  • Relational Schema: 'conversations' and 'messages' tables                       |
    |  • Builds 6 performance B-tree indexes: lang, role, user, parent, date, tree      |
    |  • Database Storage: 03_DATABASE/oasst.db (SQLite)                                |
    +-----------------------------------------------------------------------------------+
                                              |
                    +-------------------------+-------------------------+
                    |                                                   |
                    v                                                   v
    +-------------------------------+                   +-------------------------------+
    |       4. SQL ANALYTICS        |                   |      5. INTERACTIVE GUI       |
    | • DB Browser for SQLite       |                   | • Streamlit GUI (app.py)      |
    | • Saved .sql query suite      |                   | • Jupyter Notebook EDA        |
    | • Sub-millisecond queries     |                   | • Live KPI metrics & charts   |
    +-------------------------------+                   +-------------------------------+
    ```

    ---

    ### 🎯 Top Viva & Evaluation Questions
    
    **Q1: Why did you use SQLite instead of keeping data in CSV files?**
    > *Answer*: CSVs are flat text files that require full memory scanning for every query. SQLite provides relational integrity, foreign key validation, and B-Tree indexing on fields like `lang` and `role`, enabling sub-millisecond query performance over 88,000+ records.
    
    **Q2: What is a conversation tree in this dataset?**
    > *Answer*: In AI conversations, a prompt can have multiple assistant responses and follow-up user questions, forming a hierarchical tree structure. We track this using `message_tree_id` for the root and `parent_id` for individual branches.
    
    **Q3: What data quality checks did your pipeline enforce?**
    > *Answer*: We verified:
    > 1. Duplicate message ID check (0 duplicates found).
    > 2. Orphan parent check (verified all parent IDs exist in the dataset).
    > 3. Removed 100% missing columns (`model_name`).
    > 4. Validated non-negative review counts and valid roles (`prompter`, `assistant`).
    """)
