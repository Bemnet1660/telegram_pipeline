# Telegram Medical Data Pipeline

End‑to‑end ELT pipeline that scrapes public Telegram channels (medical/pharma businesses in Ethiopia), loads data into a PostgreSQL data warehouse, transforms it using dbt into a star schema, enriches images with YOLO object detection, and exposes insights via a FastAPI API. All steps are orchestrated with Dagster.

---

##  Quick Start

### 1. Clone & Setup
`bash
git clone <your-repo-url>
cd telegram_pipeline
python -m venv venv
source venv/bin/activate   # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
