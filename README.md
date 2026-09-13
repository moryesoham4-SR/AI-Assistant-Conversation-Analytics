# AI Assistant Conversation Analytics — End-to-End Data Engineering Pipeline

---

### 🎓 Academic Project Information
| Attribute | Details |
| :--- | :--- |
| **Course / Degree** | **B.Sc. Data Science** |
| **Semester** | **Semester 5** |
| **Subject** | **Data Engineering** |
| **Team Members** | **Soham Morye** & **Grishma Patil** |

---

## 📌 Project Overview

This project implements an end-to-end **Data Engineering and Business Intelligence pipeline** to extract, transform, clean, validate, and analyze large-scale AI conversational data using the **OpenAssistant Conversations Dataset (OASST1)**.

The pipeline processes multi-level conversation trees into an indexed, relational **SQLite database**, provides an interactive **Streamlit Web GUI application**, powers exploratory SQL analytics, and supports visual reporting.

> **One-Line Pipeline Flow:**  
> `Raw OASST1 Dataset` ➔ `ETL Ingestion & Validation` ➔ `Structured SQLite Database` ➔ `SQL & Python Analytics` ➔ `Interactive Streamlit GUI` ➔ `Actionable Insights`

---

## 🎯 1. Problem Statement

Raw conversational datasets from modern AI assistants present several data engineering challenges:
- **Missing & Sparse Metadata**: Critical attributes requiring strict validation or removal.
- **Complex Tree Structures**: Messages are structured as conversation trees (prompts, replies, child branches) rather than flat tables.
- **Data Quality Issues**: Risk of duplicate IDs, negative review scores, and orphaned parent references.
- **Analytical Storage**: Flat CSVs do not support efficient sub-millisecond multi-attribute queries across tens of thousands of rows.

This project resolves these challenges by building an automated, repeatable data engineering pipeline that produces analysis-ready structured data.

---

## 📊 2. Dataset Information

The project uses the **OpenAssistant OASST1 Dataset**, consisting of human-generated, multi-lingual conversation trees.

### Dataset Overview
| Metric | Value |
| :--- | :--- |
| **Total Messages** | 88,838 |
| **Total Conversation Trees** | 10,364 |
| **Unique Contributors** | 13,249 |
| **Supported Languages** | 25+ |
| **Final Processed Fields** | 18 |
| **Duplicate Message IDs** | 0 |
| **Orphan Parent References** | 0 |
| **Data Collection Period** | January – April 2023 |

### Role Distribution
| Role | Total Messages | Percentage Share |
| :--- | :--- | :--- |
| **Assistant** | 55,668 | 62.66% |
| **Prompter (User)** | 33,170 | 37.34% |

---

## 🏗️ 3. Pipeline Architecture

```text
                     OASST1 DATASET (01_DATA/raw)
                               │
                               ▼
                    ┌─────────────────────┐
                    │    1. EXTRACTION    │  ingest.py
                    │  Schema & Count Ver.│
                    └─────────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  2. TRANSFORMATION  │  transform.py
                    │ Cleaning/Validation │
                    └─────────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ 3. PROCESSED DATA   │  oasst1_processed.csv
                    │  Cleaned & Verified │
                    └─────────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  4. DATABASE LOAD   │  load.py
                    │ Relational & Indexes│
                    └─────────────────────┘
                               │
                               ▼
                    SQLite Database (oasst.db)
                               │
            ┌──────────────────┴──────────────────┐
            ▼                                     ▼
   Streamlit Web GUI                       SQL Analytics & EDA
   (Pipeline & KPIs)                       (DB Browser & Jupyter)
```

---

## 🚀 4. Interactive Streamlit Web GUI (`app.py`)

A full graphical user interface is built directly into the project to run and demonstrate the entire pipeline visually:

1. **🚀 Pipeline Runner**: Upload custom CSVs or use the default dataset. Execute the entire 4-stage pipeline with live progress bars and real-time terminal logs.
2. **📊 Executive KPI Dashboard**: Real-time metrics scorecard, role distributions, multilingual charts, and deepest conversation trees with language filtering.
3. **🗄️ Database Explorer**: Browse, search, filter, and export SQLite tables (`messages` and `conversations`) to CSV.
4. **💻 SQL Query Console**: Run pre-saved analytical queries or write custom SQL with sub-millisecond execution speeds.
5. **ℹ️ Architecture & Viva Prep**: Visual architecture breakdown and answers to evaluation questions.

---

## 🔄 5. Multi-Stage ETL Pipeline Details

### Stage 1: Extraction (`02_ETL/ingest.py`)
- Reads raw training (`84,437` records) and validation (`4,401` records) files.
- Verifies column structure and initial counts.

### Stage 2: Transformation & Cleaning (`02_ETL/transform.py`)
- Standardizes column names and trims leading/trailing whitespace.
- Formats timestamps to ISO 8601 UTC.
- Validates parent-child relationships to guarantee **0 orphan nodes**.
- Drops `model_name` (100% missing in source data).
- Validates duplicate message IDs and negative review counts.
- Exports cleaned data to `01_DATA/processed/oasst1_processed.csv`.

### Stage 3: Database Loading & Indexing (`02_ETL/load.py`)
- Creates relational tables: `conversations` and `messages`.
- Enforces foreign key constraints.
- Builds **6 B-Tree indexes** for fast query execution:
  - `idx_messages_tree`
  - `idx_messages_parent`
  - `idx_messages_role`
  - `idx_messages_lang`
  - `idx_messages_created_date`
  - `idx_messages_user`
- Stores database at `03_DATABASE/oasst.db`.

### Master Orchestration (`02_ETL/pipeline.py`)
A single master script executing the full pipeline sequentially with verification checks and duration logs.

---

## 📁 6. Repository File Structure

```text
AI-Assistant-Conversation-Analytics/
├── 01_DATA/
│   ├── raw/                 # Raw train & validation CSVs (Git LFS)
│   └── processed/           # Cleaned & standardized processed CSV
├── 02_ETL/
│   ├── ingest.py            # Extraction script
│   ├── transform.py         # Data cleaning & validation
│   ├── load.py              # SQLite loading & indexing
│   └── pipeline.py          # Master ETL orchestrator
├── 03_DATABASE/
│   ├── schema.sql           # DDL schema definition
│   └── oasst.db             # Generated relational SQLite database
├── 04_ANALYSIS/
│   ├── eda/                 # Jupyter Notebook for exploratory analysis
│   └── sql/                 # Analytical SQL queries
├── 05_POWER_BI/             # Power BI dashboard files (.pbix)
├── 06_TESTING/              # Test reports & validation logs
├── 07_DOCUMENTATION/        # Project architecture and guides
├── .gitignore               # Excludes virtual environments and caches
├── app.py                   # Interactive Streamlit Web GUI Application
└── README.md                # Comprehensive project documentation
```

---

## 🛠️ 7. How to Setup and Run Locally

### 1. Clone the Repository
```bash
git clone https://github.com/moryesoham4-SR/AI-Assistant-Conversation-Analytics.git
cd AI-Assistant-Conversation-Analytics
```

### 2. Pull Git LFS Dataset Files
```bash
git lfs pull
```

### 3. Create & Activate Virtual Environment
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate
```

### 4. Install Dependencies
```bash
pip install pandas matplotlib seaborn jupyter notebook streamlit
```

### 5. Run the Interactive Web GUI
```bash
streamlit run app.py
```

### 6. (Alternative) Run ETL via Command Line
```bash
python 02_ETL/pipeline.py
```

---

## 💻 8. Core SQL Analytical Queries

The database can be queried directly in SQLite or via the GUI SQL Console:

#### Role Share Analysis
```sql
SELECT 
    role,
    COUNT(*) AS total_messages,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM messages), 2) AS percentage_share
FROM messages
GROUP BY role
ORDER BY total_messages DESC;
```

#### Top Active Languages
```sql
SELECT 
    lang AS language_code,
    COUNT(*) AS message_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM messages), 2) AS pct_of_total
FROM messages
GROUP BY lang
ORDER BY message_count DESC
LIMIT 10;
```

#### Deepest Conversation Threads
```sql
SELECT 
    message_tree_id,
    COUNT(*) AS total_messages,
    COUNT(DISTINCT user_id) AS participants
FROM messages
GROUP BY message_tree_id
ORDER BY total_messages DESC
LIMIT 5;
```

---

## 👥 Authors & Credits
- **Soham Morye**
- **Grishma Patil**  
*Department of Data Science — Semester 5 (Data Engineering)*