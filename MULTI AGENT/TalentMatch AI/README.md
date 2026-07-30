# TalentMatch AI — Multi-Agent Recruiting Intelligence System

TalentMatch AI is a multi-agent artificial intelligence system that sources candidates across multiple recruiting channels simultaneously (LinkedIn, Indeed, Wuzzuf, Internal Referrals, and Company Careers), aggregates and cleans the results, analyzes candidate reference & verification trust signals, compares all candidates against real hiring-manager priorities, and produces explainable hiring recommendations through a modern Streamlit web interface.

---

## ✨ Features

- **Multi-Agent Architecture (CrewAI)**: 6 specialized AI agents handling Job Requisition Analysis, Channel Sourcing, Candidate Aggregation, Reference Verification, Fit Scoring, and Report Synthesis.
- **Parallel Channel Sourcing**: Queries multiple recruiting channels concurrently using HTTP requests and BeautifulSoup fallback generators.
- **Fit-for-Role Scoring**: Dynamic 0-100 score calculating salary fit, skills match, interview rating, and hiring-manager priority focus (Lowest Salary, Experience, Balanced).
- **Fuzzy Candidate Deduplication**: Merges duplicate profiles of the same candidate across channels using `rapidfuzz`.
- **Reference & Verification Intelligence**: Identifies verified pros/cons and candidate trust flags (`Verified`, `Caution`, `Insufficient Data`).
- **Modern Streamlit UI**: Custom CSS design system with cards, Plotly charts, interactive comparison tables, search history, and salary tracking over time.
- **Export Capabilities**: One-click export to executive PDF reports and Excel spreadsheets.
- **Persistent Caching**: SQLite database with SQLAlchemy caching requisition searches and recording salary history points.

---

## 🚀 Quick Start

### 1. Installation

Clone the repository and install dependencies:

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Configuration

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

### 3. Launch Application

Run the application using Python:

```bash
python run.py
```

or directly with Streamlit:

```bash
streamlit run frontend/app.py
```

Open your browser at `http://localhost:8501`.

---

## 🐳 Docker Setup

Run using Docker Compose:

```bash
docker-compose up --build
```

---

## 🧪 Testing

Run pytest suite:

```bash
pytest
```
