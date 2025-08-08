# Health Score Flask Application

A Flask application for ingesting health assessment data, calculating health scores, generating charts/PDFs, and optionally emailing reports.

## Architecture

```
lngvty-flask/
├── app.py                        # Application factory, blueprint registration, static index
├── routes/                       # Feature-based blueprints
│   ├── webhook_routes.py         # /api/webhook*, ingest and process
│   ├── file_routes.py            # /api/files*, list/read/process/email
│   └── report_routes.py          # /api/download-pdf, /api/view-chart
├── controllers/                  # Route controllers (single-responsibility)
│   ├── webhook_controller.py
│   ├── file_controller.py
│   └── report_controller.py
├── services/                     # Core business services
│   ├── health_score_service.py   # Health score calculation
│   ├── health_score_orchestration_service.py  # Coordinates chart/PDF
│   ├── chart_generation_service.py            # Chart generation (PNG)
│   ├── pdf_report_service.py     # PDF report generation
│   └── email_service.py          # SendGrid-based email sender
├── JsonData/                     # Stored inbound JSON payloads
├── PdfData/                      # Generated outputs
│   ├── charts/
│   └── reports/
├── static/index.html             # Simple UI served at '/'
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

The app uses a factory (`create_app()`) and registers blueprints from `routes/`. JSON payloads are saved to `JsonData/`. Generated assets (charts/PDFs) are saved to `PdfData/`.

## Endpoints

- GET `/` — Serve `static/index.html`.
- GET `/health` — Simple health check.

Webhook ingestion

- POST `/api/webhook` — Ingest JSON, compute scores, persist, return JSON result metadata.
- POST `/api/webhook-to-pdf` — Ingest JSON, compute, generate PDF, return the PDF as a file response.
- POST `/api/webhook-to-email?email=<optional>` — Ingest JSON, compute, generate PDF, email the report (uses email from payload if present, or `email` query param).

File management and processing

- GET `/api/files` — List JSON files stored in `JsonData/`.
- GET `/api/files/<filename>` — Return JSON content of a stored file.
- POST `/api/files/<filename>/process` — Process stored JSON, generate outputs. Body: `{ "outputFormat": "pdf" }` (default `pdf`).
- POST `/api/files/<filename>/email?email=<optional>` — Generate PDF from stored JSON and email it. Tries to infer email from stored payload if not provided.

Report/asset retrieval

- GET `/api/download-pdf?path=<absolute-or-known-path>` — Download a generated PDF by file path.
- GET `/api/view-chart?path=<absolute-or-known-path>` — Return a generated chart PNG by file path.

## Requirements

- Python 3.11+ (Docker image uses 3.13-slim)
- macOS/Linux/Windows

## Setup (local)

1. Create and activate a virtual environment

```
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. Install dependencies

```
pip install -r requirements.txt
```

3. (Optional, for email) Configure environment variables

- `SENDGRID_API_KEY` — Required to send emails
- `SENDGRID_FROM_EMAIL` — Optional sender (default: no-reply@frontlab.io)

Example (mac/Linux):

```
export SENDGRID_API_KEY=your_sendgrid_key
export SENDGRID_FROM_EMAIL=reports@example.com
```

4. Run the app

```
python app.py
```

App runs at http://localhost:5000

## Run with Docker

Build and run via Docker directly:

```
docker build -t lngvty-flask .
docker run -p 5000:5000 \
  -e SENDGRID_API_KEY=$SENDGRID_API_KEY \
  -e SENDGRID_FROM_EMAIL=$SENDGRID_FROM_EMAIL \
  -v $(pwd)/JsonData:/app/JsonData \
  -v $(pwd)/PdfData:/app/PdfData \
  --name lngvty-flask \
  lngvty-flask
```

Or with Compose:

```
docker-compose up --build -d
```

Compose already mounts `JsonData/` and `PdfData/`. Export your SendGrid env vars before `up` or add them to your environment securely.

## Usage Examples

- Ingest a JSON payload:

```
curl -X POST -H "Content-Type: application/json" \
  -d @sample_data.json \
  http://localhost:5000/api/webhook
```

- Ingest and receive the PDF as a download:

```
curl -X POST -H "Content-Type: application/json" \
  -d @sample_data.json \
  -o report.pdf -J -O \
  http://localhost:5000/api/webhook-to-pdf
```

- Ingest and email the PDF (email can be inferred from payload or provided):

```
curl -X POST -H "Content-Type: application/json" \
  -d @sample_data.json \
  "http://localhost:5000/api/webhook-to-email?email=user@example.com"
```

- List stored files:

```
curl http://localhost:5000/api/files
```

- Process a stored file into PDF:

```
curl -X POST -H "Content-Type: application/json" \
  -d '{"outputFormat":"pdf"}' \
  http://localhost:5000/api/files/<filename>/process
```

- Email a stored file's report:

```
curl -X POST "http://localhost:5000/api/files/<filename>/email?email=user@example.com"
```

- Download a generated PDF by path:

```
curl -L -o report.pdf "http://localhost:5000/api/download-pdf?path=/app/PdfData/reports/<file>.pdf"
```

- View a generated chart by path:

```
curl -L "http://localhost:5000/api/view-chart?path=/app/PdfData/charts/<file>.png" --output chart.png
```

## Notes

- Data locations:
  - Incoming JSON: `JsonData/`
  - Generated charts/PDFs: `PdfData/` (subfolders may be created automatically)
- Emailing requires valid `SENDGRID_API_KEY`. Without it, email endpoints will return an error.
- The static landing page is served from `static/index.html` at `/`.

## Future Improvements

- Harden input validation and error handling
- Authentication/authorization for protected endpoints
- Cloud storage backends (e.g., S3/Azure Blob) for artifacts
- CI/CD and automated tests
