# Earth Trend Detective — Be An Earth System Trend Detective!

**NASA Space Apps Challenge 2026** | Team/Project: **Sayriks Space Technological Research**  
**Team Member (Owner):** ÜNAL YÜREKLİ (@sayriks, Turkey)

## Overview
Earth Trend Detective is an interactive Streamlit application that answers: **What changed, where, by how much, and is the change statistically meaningful?**  
It analyzes NASA POWER Earth-system time-series data (1981–present) across multiple parameters and locations (Türkiye’s 81 provinces + selected countries/capitals), providing trends, anomalies, comparisons, and evidence-oriented visualizations.

## Challenge
- **Challenge:** Be An Earth System Trend Detective! (NASA Space Apps 2026)
- **Goal:** Detect trends in Earth system data and communicate what changed, where, magnitude, and statistical significance with clear visual and statistical evidence.

## Key Features
- NASA POWER data ingestion and MySQL-backed processed storage for fast analysis
- Trend and significance analysis: linear trend (per decade), **p-value**, **95% confidence interval**, **Mann–Kendall** test
- Daily/monthly series, year/month range selection, seasonal and non-seasonal anomaly views
- Interactive map/globe visualizations and location comparisons (country/province averages and changes)
- World Bank indicators as complementary context (`worldbank_indicator_raw`)
- Multilingual UI (TR/EN/DE/FR/IT)
- Downloadable/printable HTML presentation-report output (jury-oriented flow, timeline, SWOT, evidence pages)

## Data Sources
- **NASA POWER (Prediction Of Worldwide Energy Resources)** via NASA POWER API — primary Earth observation/model-derived parameters (temperature, precipitation, humidity, wind/pressure, radiation/energy, cloud/aerosol, etc.; project configured for 36 parameters).  
  *NASA data/resources are used in this project for analysis and visualization.*
- **World Bank Open Data (World Development Indicators API)** — contextual indicators (where available).
- See `submission/PORTAL_SUBMISSION_DRAFT_EN.md` for the detailed data/resources list to paste into the Space Apps Project page.

## Repository Structure
- `app.py` — Streamlit application (UI, analysis, visualizations, report/presentation export)
- `utils/` — data fetching and analysis utilities
- `database/` — schemas and ingestion scripts (`ingest_nasa_to_db.py`, `ingest_worldbank_to_db.py`, `schema_mysql.sql`)
- `RAPOR_Earth_Trend_Detective.html` — sample generated report output
- `SUNUM.md`, `PROJECT_STRUCTURE.md` — project notes
- `submission/` — submission drafts and upload guide

## Setup & Run (local)
### Prerequisites
- Python 3.10+
- MySQL (optional but recommended for processed dataset) or run with available data/simulation fallback
- NASA POWER API access (internet) for live fetching/ingestion

### Install
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS (WSL)
pip install -r requirements.txt
```

### Configure database (optional, recommended)
Create a `.env` file (do **not** commit it):
```env
DB_MODE=mysql
MYSQL_HOST=<host>
MYSQL_PORT=3306
MYSQL_USER=<user>
MYSQL_PASSWORD=<password>
MYSQL_DATABASE=sayriks_earth_trend_detective
```
Initialize schema (MySQL): run `database/schema_mysql.sql`.

### Run the app
```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```
Open http://localhost:8501

### Data ingestion (optional, long-running)
```bash
# NASA POWER -> MySQL
python database/ingest_nasa_to_db.py --db mysql --env .env

# World Bank indicators -> MySQL
python database/ingest_worldbank_to_db.py --env .env
```

## Demo & Evidence
- **Project Demo (video/slides):** [PASTE PUBLIC DEMO LINK]
- **Final Project:** [PASTE PUBLIC REPO/PROJECT LINK]
- **Backup evidence:** screen recording, screenshots, and generated HTML/CSV outputs (see `submission/UPLOAD_AND_LINKS_TR.md`)

> Labeling: *Working prototype / Live demo* (real data), *Simulation (offline/fallback) mode* (flow test only), *Test/evidence output* (pre-generated artifacts).

## AI / Super Intelligence (SI) Disclosure
[REVIEW AND UPDATE] Document any AI/SI tool usage transparently in the Space Apps submission and in linked materials (including watermarks/metadata for AI-generated media where applicable). Do not use AI to modify NASA branding/design elements.

## License & Acknowledgments
- License: see `LICENSE` (update if needed).
- Data: NASA POWER, World Bank Open Data, and other referenced sources as listed in the submission. Respect original data/source terms and cite all third-party materials used.
