from dagster import job, op, AssetSelection, Definitions
import subprocess
import os

@op
def scrape_telegram(context):
    """Run the scraper script."""
    result = subprocess.run(["python", "src/scraper.py"], capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Scraper failed: {result.stderr}")
    context.log.info("Scraping completed successfully.")

@op
def load_raw_to_postgres(context):
    """Load raw JSON to PostgreSQL."""
    result = subprocess.run(["python", "src/load_to_postgres.py"], capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Load failed: {result.stderr}")
    context.log.info("Data loaded to PostgreSQL.")

@op
def run_dbt_transformations(context):
    """Run dbt models."""
    result = subprocess.run(["dbt", "run"], cwd="dbt_project", capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"dbt run failed: {result.stderr}")
    context.log.info("dbt transformations completed.")

@op
def run_yolo_enrichment(context):
    """Run YOLO detection."""
    result = subprocess.run(["python", "src/yolo_detect.py"], capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"YOLO failed: {result.stderr}")
    context.log.info("YOLO enrichment completed.")

@job
def telegram_pipeline():
    scrape = scrape_telegram()
    load = load_raw_to_postgres()
    dbt = run_dbt_transformations()
    yolo = run_yolo_enrichment()
    
    # Dependencies
    load.depends_on(scrape)
    dbt.depends_on(load)
    yolo.depends_on(dbt)  # YOLO needs the fct_messages table with image_paths

# Define a schedule to run daily at 2 AM
from dagster import ScheduleDefinition

daily_schedule = ScheduleDefinition(
    job=telegram_pipeline,
    cron_schedule="0 2 * * *",  # daily at 2 AM UTC
)

defs = Definitions(jobs=[telegram_pipeline], schedules=[daily_schedule])
