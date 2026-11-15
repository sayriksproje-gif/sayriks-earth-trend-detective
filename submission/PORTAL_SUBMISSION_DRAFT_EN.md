# NASA Space Apps 2026 — Project Submission Draft (English)

> Team: Sayriks Space Technological Research  
> Team Member (Owner): ÜNAL YÜREKLİ (@sayriks, Turkey)  
> Challenge: **Be An Earth System Trend Detective!** (NASA Space Apps 2026)  
> Local working project: Earth Trend Detective (Streamlit + MySQL)

> **Note:** Fill in the final public links (Demo, Final Project) after uploading to YouTube/Drive/GitHub. Keep all linked materials publicly accessible (no login/password/permission). Project page and linked materials must be in English (demo video may be in another language but **must include English subtitles**).

---

## Project Name
**Earth Trend Detective — Sayriks Space Technological Research**

## High-Level Project Summary (draft)
Earth Trend Detective is an interactive Earth-system analytics platform that helps users answer: *What changed, where, by how much, and is the change statistically meaningful?* Using NASA POWER open data (1981–present), the project processes multi-parameter time series for 201 locations (81 provinces of Türkiye plus selected countries/capitals worldwide) and presents trend magnitude, anomalies, and significance through maps/globes, charts, and downloadable evidence reports. By combining a processed MySQL data layer with statistical validation (linear trend, p-value, 95% confidence interval, Mann–Kendall), the tool turns large NASA datasets into clear, comparable, and decision-relevant insights for climate and environmental awareness.

## Link to Project Demo (public, no login)
- **[PASTE PUBLIC DEMO LINK HERE]**  
  - Format: **≤30-second video** OR **≤7-slide deck** (including title and intro slides).  
  - Hosting suggestions: YouTube (Unlisted/Public) or Google Drive/OneDrive/Google Slides with “Anyone with the link” access.  
  - Demo flow suggestion (single main flow): (1) Control panel (source/parameter/location/date) → (2) Map & overview (metrics, globe/map) → (3) Trends & statistics (series, trend, anomaly, p-value/95% CI/MK) → (4) Comparison & evidence (location scan, country/province averages, seasonal/non-seasonal anomalies, radiation findings) → (5) Presentation/report output.  
  - Correct labeling in demo: **Working prototype / live demo** (real NASA POWER or MySQL data), **Simulation (offline/fallback) mode** (UI/flow test only, not scientific observation), **Test/evidence output** (pre-generated reports/records).

## Link to Final Project (public, no login)
- **[PASTE PUBLIC FINAL PROJECT LINK HERE]** (recommended: public GitHub repository)  
  - Include: source code, README, setup/run instructions, sample outputs/reports, screenshots, and data/method documentation. Do **not** include `.env` or secrets.

## Detailed Project Description (draft)
**What it does**  
Earth Trend Detective ingests and analyzes NASA Earth-system time-series indicators to detect trends and anomalies for selected locations and periods. Users can explore parameters such as temperature, precipitation, humidity, wind, radiation/energy, cloud, and aerosol-related variables; compare locations; and review statistical evidence.

**How it works**  
- **Data ingestion & storage:** NASA POWER daily/aggregated observations are fetched and stored in a MySQL analytical database (`nasa_power_raw`, `locations`, `analysis_results`, and World Bank context in `worldbank_indicator_raw`) for fast querying and reuse.  
- **Analysis:** The app computes trend magnitude (including per-decade trend), statistical significance (**p-value**), **95% confidence interval**, and **Mann–Kendall** trend test; it also supports anomaly views (including seasonal/non-seasonal patterns) and comparative summaries (country/province averages and changes).  
- **Visualization & evidence:** Interactive Streamlit UI with side-by-side globe/map views, time-series and anomaly charts, comparison tables, and downloadable/printable HTML presentation-report outputs (jury-oriented flow, timeline, SWOT, evidence pages).

**Benefits**  
- Makes large Earth observation datasets understandable and comparable.  
- Provides evidence-based interpretation (not only visualization) to support awareness and planning discussions (e.g., heat, precipitation variability, radiation/UV context).  
- Supports multilingual exploration (TR/EN/DE/FR/IT in the app interface).

**Tools, languages, software**  
- Python, Streamlit, Pandas/NumPy/SciPy (statistics), Plotly (visualization), MySQL/PyMySQL (processed data layer), Requests (data access), HTML/CSS report generation.  
- Data sources accessed via NASA POWER API and World Bank indicators API.

**Goals and future work**  
- Complete and continuously refresh global/location coverage, improve performance and deployment options, integrate additional validated datasets/ground observations, and extend scenario/risk communication features.

## Use of Artificial Intelligence (AI) / Super Intelligence (SI) tools
**[REVIEW AND EDIT THIS SECTION TO MATCH ACTUAL USE]**

- **If AI/SI tools were used (example text):** We used AI-assisted coding/chat tools to help draft/refactor parts of the application code, documentation text, and UI/report wording. All generated suggestions were reviewed, edited, and validated by the team. AI tools were **not** used to invent the core challenge solution concept or scientific conclusions; analyses are based on NASA/World Bank data processed by implemented statistical methods in the project.
  - **Code/text:** AI assistance (if any) is acknowledged in project documentation/metadata where applicable.
  - **Images/videos/audio:** Any AI-generated images/videos/audio included in submitted materials (if any) will include visible watermarks and/or clear descriptive/metadata acknowledgment as required.
  - No NASA branding/design elements were generated or modified using AI.
- **If no AI/SI tools were used:** No Super Intelligence/AI generative tools were used to create the submitted project code, data analyses, images, videos, or text beyond standard non-generative software features.

## NASA Data
*(At least one NASA data/resource is required for Global Award eligibility.)*

- **NASA POWER (Prediction Of Worldwide Energy Resources) Project** — primary data source used for Earth-system time-series analysis.
  - Accessed via NASA POWER API for selected locations and parameters (daily values aggregated/analyzed in the project).
  - Example parameter groups used: near-surface air temperature (e.g., T2M, T2M_MAX, T2M_MIN, T2MDEW, T2MWET), precipitation (e.g., PRECTOTCORR), humidity (e.g., RH2M, QV2M), wind/pressure (e.g., WS10M, WS2M, PS), solar/radiation and energy-related variables (e.g., ALLSKY_SFC_SW_DWN, CLRSKY_SFC_SW_DWN, ALLSKY_SFC_LW_DWN, related components), cloud/aerosol and other available POWER parameters (project configured for 36 parameters across 201 locations, 1981–present coverage in processed dataset).
- **NASA Space Apps Challenge context/resources:** Challenge brief and guidance for *“Be An Earth System Trend Detective!”* informed problem framing and expected outputs (trend detection, location/magnitude, statistical significance, visualization).

## Space Agency Partner & Other Data / References
- **World Bank Open Data (World Development Indicators API):** contextual country-level indicators ingested into `worldbank_indicator_raw` for complementary socio-environmental context (e.g., emissions, energy use, renewables, PM2.5, electricity access, forest area) where available.
- **Open-source libraries/tools:** Python, Streamlit, Pandas, NumPy, SciPy, Plotly, PyMySQL, Requests (and other dependencies listed in `requirements.txt`).
- **Project-generated materials:** analysis outputs, charts/maps, and HTML/PDF-printable presentation-report exports produced by the application from the above data sources.
- **[ADD ANY OTHER datasets, code snippets, fonts, images, or references used — include licenses/permissions where required]**

## Submission Checklist (before clicking “Submit for Judging”)
- [ ] All team members confirmed in the same Local Event (or Universal Event rules satisfied)
- [ ] All required Project page fields completed in English
- [ ] Demo link public (no login) and within limits (≤30s video or ≤7 slides); English subtitles if video not in English
- [ ] Final project link public (no login)
- [ ] NASA data/resources clearly listed (≥1 NASA source)
- [ ] SI/AI use accurately disclosed; any AI-generated media properly watermarked/acknowledged
- [ ] No under-18 likeness in demo/final materials; no unauthorized NASA branding modifications
- [ ] Links tested in private/incognito window
- [ ] Submit before **Nov 15, 2026 11:59 p.m. (Local Event / Team Owner local time)**

## Backup plan for demo (connectivity/errors)
- Record **screen capture video** and take **screenshots** of the full demo flow in advance.
- Keep offline copies of **downloadable HTML/PDF report** and sample **CSV outputs**.
- If live data/API/DB fails during judging, show: pre-generated report/recording + clearly label mode (**live prototype** vs **simulation/fallback** vs **test/evidence output**).
