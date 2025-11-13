# ISA GetKeywords Service

A microservice for generating relevant Hebrew keywords in the stocks and finance industry using Google's Gemini AI, part of the ISA microservices architecture.

## Overview

This service:
- Generates Hebrew keywords related to stocks and finance using Gemini AI (gemini-2.0-flash-exp)
- Stores keywords in the existing BigQuery table `pwcnext-sandbox01.telegram.keys` (column: `keys_group`)
- Prevents duplicate entries by checking existing keywords
- Runs on a scheduled basis via Cloud Scheduler
- Follows the same design patterns as [isa-getgroups-service](https://github.com/roy2392/isa-getgroups-service)

## Architecture

```
Cloud Scheduler (Daily at 2 AM UTC)
    ↓ POST request
FastAPI Endpoint (/)
    ↓ calls
batch_generate_keywords.main()
    ↓ uses
Gemini AI (keyword generation)
    ↓ checks duplicates
BigQuery (keywords table)
    ↓ inserts
New Keywords
```

## Technology Stack

- **Language**: Python 3.11
- **Web Framework**: FastAPI
- **AI Provider**: Google Gemini AI
- **Data Storage**: Google BigQuery
- **Secret Management**: GCP Secret Manager
- **Infrastructure**: Terraform
- **CI/CD**: GitHub Actions
- **Deployment**: Google Cloud Run

## Project Structure

```
isa-getkeywords-service/
├── .github/
│   └── workflows/
│       └── main.yml              # CI/CD pipeline
├── src/
│   ├── __init__.py
│   ├── config.py                 # Configuration constants
│   ├── generate_keywords.py     # Gemini keyword generation logic
│   └── batch_generate_keywords.py  # Main orchestration
├── terraform/
│   ├── main.tf                   # Terraform provider config
│   ├── variables.tf              # Input variables
│   ├── outputs.tf                # Output values
│   ├── bigquery.tf               # BigQuery dataset and table
│   ├── cloud_run.tf              # Cloud Run service
│   ├── cloud_scheduler.tf        # Scheduled job trigger
│   ├── secrets.tf                # Secret Manager resources
│   └── terraform.tfvars.example  # Example variables file
├── .env.example                  # Environment variables template
├── .gitignore
├── Dockerfile
├── main.py                       # FastAPI entry point
├── README.md
└── requirements.txt
```

## Prerequisites

- GCP Project with the following APIs enabled:
  - Cloud Run API
  - Cloud Scheduler API
  - BigQuery API
  - Secret Manager API
  - Artifact Registry API
- Gemini API Key
- Terraform >= 1.0
- Docker (for local testing)
- Python 3.11 (for local development)

## Local Development

### 1. Clone the Repository

```bash
git clone https://github.com/roy2392/isa-getkeywords-service.git
cd isa-getkeywords-service
```

### 2. Set Up Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
cp .env.example .env
```

### 3. Configure Environment Variables

Edit `.env`:

```bash
GCP_PROJECT_ID=your-project-id
GEMINI_API_KEY=your-gemini-api-key
```

### 4. Run Locally

```bash
# Run the service
python main.py

# Or use uvicorn directly
uvicorn main:app --reload --port 8080
```

### 5. Test the Endpoint

```bash
# Health check
curl http://localhost:8080/

# Trigger job manually
curl -X POST http://localhost:8080/
```

## Configuration

### Environment Variables

- `GCP_PROJECT_ID`: Your GCP project ID (required)
- `GEMINI_API_KEY`: Gemini API key (local development only)

### Configuration Settings (`src/config.py`)

```python
BIGQUERY_KEYWORDS_TABLE = "pwcnext-sandbox01.telegram.keys"
BIGQUERY_KEYWORD_COLUMN = "keys_group"
GEMINI_MODEL = "gemini-2.0-flash-exp"
KEYWORDS_PER_GENERATION = 20
INDUSTRY_FOCUS = "stocks and finance"
LANGUAGE = "Hebrew"
CHECK_DUPLICATES = True
```

Adjust these values based on your requirements.

## BigQuery Table

This service uses an **existing shared BigQuery table**:
- **Table**: `pwcnext-sandbox01.telegram.keys`
- **Column**: `keys_group` (stores the Hebrew keywords)

The table is shared across ISA microservices and is not created by this service. Keywords are inserted directly into the `keys_group` column.

## Deployment

### 1. Set Up GCP Secrets

```bash
# Create Gemini API key secret
echo -n "your-gemini-api-key" | gcloud secrets create gemini-api-key --data-file=-
```

### 2. Configure Terraform Variables

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`:

```hcl
project_id = "your-gcp-project-id"
region     = "us-central1"
service_name = "isa-getkeywords-service"
image_url  = "us-central1-docker.pkg.dev/your-project/your-repo/isa-getkeywords-service:latest"
schedule   = "0 2 * * *"  # Daily at 2 AM UTC

# Note: This service uses existing BigQuery table: pwcnext-sandbox01.telegram.keys
```

### 3. Deploy Infrastructure

```bash
terraform init
terraform plan
terraform apply
```

### 4. Set Up CI/CD (Automated)

The CI/CD pipeline automatically builds, tests, and deploys on every push to `main` branch.

Configure GitHub Secrets:
- `GCP_PROJECT_ID`: Your GCP project ID
- `GCP_SA_KEY`: Service account JSON key with deployment permissions

The pipeline will:
1. Build Docker image for linux/amd64
2. Push to Artifact Registry
3. Deploy with Terraform
4. Run health checks and integration tests

Push to `main` branch to trigger automatic deployment.

## Manual Deployment

### Build and Push Docker Image

```bash
# Build image
docker build -t isa-getkeywords-service .

# Tag for GCP Artifact Registry
docker tag isa-getkeywords-service \
  us-central1-docker.pkg.dev/YOUR_PROJECT/YOUR_REPO/isa-getkeywords-service:latest

# Push to registry
docker push us-central1-docker.pkg.dev/YOUR_PROJECT/YOUR_REPO/isa-getkeywords-service:latest
```

### Deploy to Cloud Run

```bash
gcloud run deploy isa-getkeywords-service \
  --image us-central1-docker.pkg.dev/YOUR_PROJECT/YOUR_REPO/isa-getkeywords-service:latest \
  --region us-central1 \
  --platform managed \
  --no-allow-unauthenticated \
  --service-account isa-getkeywords-service-sa@YOUR_PROJECT.iam.gserviceaccount.com \
  --set-env-vars GCP_PROJECT_ID=YOUR_PROJECT \
  --timeout 3600 \
  --memory 4Gi \
  --cpu 2
```

## Monitoring & Logs

### View Logs

```bash
# Cloud Run logs
gcloud run services logs read isa-getkeywords-service --region us-central1

# Cloud Scheduler logs
gcloud scheduler jobs describe isa-getkeywords-service-trigger --location us-central1
```

### Check Job Status

```bash
# View recent executions
gcloud scheduler jobs describe isa-getkeywords-service-trigger --location us-central1 --format="value(status.lastAttemptTime,status.lastAttemptStatus)"
```

## Troubleshooting

### Issue: "GCP_PROJECT_ID environment variable not set"

**Solution**: Ensure the environment variable is set in Cloud Run or locally in `.env`

### Issue: "Failed to retrieve Gemini API key"

**Solution**:
1. Check if secret exists: `gcloud secrets list`
2. Verify service account has `secretmanager.secretAccessor` role
3. Ensure secret name is `gemini-api-key`

### Issue: "Could not connect to BigQuery"

**Solution**:
1. Verify BigQuery API is enabled
2. Check service account has `bigquery.dataEditor` and `bigquery.jobUser` roles
3. Verify dataset and table exist

### Issue: Duplicate keywords being inserted

**Solution**:
- Check `CHECK_DUPLICATES` is set to `True` in `src/config.py`
- Verify `keys_group` column has data in BigQuery table
- Ensure table name and column name in config match the actual BigQuery table

## Development Workflow

1. **Make Changes**: Edit code in `src/` directory
2. **Test Locally**: Run `python main.py` and test with curl
3. **Commit & Push**: Push to `main` branch
4. **Automatic Deployment**: GitHub Actions builds, tests, and deploys
5. **Verify**: Check Cloud Run logs and BigQuery table

## API Endpoints

### GET `/`
Health check endpoint

**Response**:
```json
{
  "status": "healthy",
  "service": "isa-getkeywords-service",
  "version": "1.0.0"
}
```

### POST `/`
Trigger keyword generation job (called by Cloud Scheduler)

**Response**:
```json
{
  "status": "OK"
}
```

## Cost Optimization

- Cloud Run: Only charged when job runs (scheduled once daily)
- BigQuery: Minimal storage costs for keywords table
- Gemini API: Pay per API call (20 keywords per run)
- Secret Manager: Minimal cost for single secret

**Estimated Monthly Cost**: < $5 USD for daily runs

## Security

- Secrets stored in GCP Secret Manager
- Service account with least-privilege IAM roles
- Cloud Run requires authentication (not publicly accessible)
- GitHub Actions uses service account with limited deployment permissions

## Related Services

- [isa-getgroups-service](https://github.com/roy2392/isa-getgroups-service) - Telegram groups classifier service

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

[Add your license here]

## Contact

[Add your contact information here]
