# DuckFleet nightly fleet — Cloud Run Job image.
# Packaging only: fleet logic lives in agents/, runtime wiring in runtimes/gcp_adk/.
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

ENV PYTHONUNBUFFERED=1
CMD ["python", "-m", "runtimes.gcp_adk.job"]
