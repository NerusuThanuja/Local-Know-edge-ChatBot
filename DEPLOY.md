# Deployment Guide 🚀

Production deployment instructions for cloud platforms.

## Table of Contents
1. [Local Docker Deployment](#local-docker-deployment)
2. [AWS Deployment](#aws-deployment)
3. [Google Cloud Deployment](#google-cloud-deployment)
4. [Azure Deployment](#azure-deployment)
5. [Heroku Deployment](#heroku-deployment)
6. [Performance Optimization](#performance-optimization)

---

## Local Docker Deployment

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop) installed

### Quick Start
```bash
# Navigate to project directory
cd MLops

# Build image
docker build -t rag-chatbot:latest .

# Run container
docker run -p 8501:8501 rag-chatbot:latest
```

Access at: `http://localhost:8501`

### Using Docker Compose
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Verify Container
```bash
# Check if running
docker ps

# View logs
docker logs <container_id>

# Access shell
docker exec -it <container_id> bash
```

---

## AWS Deployment

### Option 1: AWS App Runner (Easiest)

```bash
# 1. Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account_id>.dkr.ecr.us-east-1.amazonaws.com

docker build -t rag-chatbot .

docker tag rag-chatbot:latest <account_id>.dkr.ecr.us-east-1.amazonaws.com/rag-chatbot:latest

docker push <account_id>.dkr.ecr.us-east-1.amazonaws.com/rag-chatbot:latest

# 2. Create App Runner service in AWS Console
# - Source: ECR image
# - Image URI: <account_id>.dkr.ecr.us-east-1.amazonaws.com/rag-chatbot:latest
# - Port: 8501
# - Environment: PYTHONUNBUFFERED=1
```

### Option 2: AWS ECS

```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name rag-chatbot

# Register task definition
# Create ecs-task-definition.json (see below)
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json

# Create service
aws ecs create-service \
    --cluster rag-chatbot \
    --service-name rag-chatbot-service \
    --task-definition rag-chatbot:1 \
    --desired-count 1 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

**ecs-task-definition.json:**
```json
{
  "family": "rag-chatbot",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "rag-chatbot",
      "image": "<account_id>.dkr.ecr.us-east-1.amazonaws.com/rag-chatbot:latest",
      "portMappings": [
        {
          "containerPort": 8501,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "PYTHONUNBUFFERED",
          "value": "1"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/rag-chatbot",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

---

## Google Cloud Deployment

### Cloud Run (Recommended)

```bash
# 1. Set project
gcloud config set project YOUR_PROJECT_ID

# 2. Build image
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/rag-chatbot

# 3. Deploy to Cloud Run
gcloud run deploy rag-chatbot \
    --image gcr.io/YOUR_PROJECT_ID/rag-chatbot \
    --platform managed \
    --region us-central1 \
    --memory 2Gi \
    --timeout 600 \
    --allow-unauthenticated
```

Access at URL provided by Cloud Run.

### Cloud Run with Cloud Storage (Persistent Data)

```bash
# 1. Create bucket
gsutil mb gs://rag-chatbot-data

# 2. Upload initial data
gsutil -m cp -r embeddings/* gs://rag-chatbot-data/embeddings/

# 3. Update Dockerfile to mount bucket
# See "GCP_Dockerfile" below

# 4. Deploy
gcloud run deploy rag-chatbot \
    --image gcr.io/YOUR_PROJECT_ID/rag-chatbot \
    --set-env-vars GCS_BUCKET=rag-chatbot-data
```

**GCP_Dockerfile:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc g++ curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

ENV PYTHONUNBUFFERED=1
ENV PORT=8501

# Mount GCS bucket (if using Cloud Run job)
# gsutil -m cp -r gs://${GCS_BUCKET}/embeddings /app/embeddings

CMD exec streamlit run app.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.enableCORS=false
```

---

## Azure Deployment

### Azure Container Instances

```bash
# 1. Create resource group
az group create --name rag-chatbot-rg --location eastus

# 2. Create container registry
az acr create --resource-group rag-chatbot-rg \
    --name ragchatbotregistry --sku Basic

# 3. Build and push image
az acr build --registry ragchatbotregistry \
    --image rag-chatbot:latest .

# 4. Deploy to Container Instances
az container create \
    --resource-group rag-chatbot-rg \
    --name rag-chatbot \
    --image ragchatbotregistry.azurecr.io/rag-chatbot:latest \
    --registry-login-server ragchatbotregistry.azurecr.io \
    --registry-username <username> \
    --registry-password <password> \
    --cpu 1 --memory 2 \
    --ports 8501 \
    --protocol TCP
```

### Azure App Service

```bash
# 1. Create App Service Plan
az appservice plan create \
    --name rag-chatbot-plan \
    --resource-group rag-chatbot-rg \
    --sku B2 --is-linux

# 2. Create Web App
az webapp create \
    --resource-group rag-chatbot-rg \
    --plan rag-chatbot-plan \
    --name rag-chatbot-app \
    --deployment-container-image-name ragchatbotregistry.azurecr.io/rag-chatbot:latest

# 3. Configure container
az webapp config container set \
    --name rag-chatbot-app \
    --resource-group rag-chatbot-rg \
    --docker-custom-image-name ragchatbotregistry.azurecr.io/rag-chatbot:latest \
    --docker-registry-server-url https://ragchatbotregistry.azurecr.io
```

---

## Heroku Deployment

### Using Heroku CLI

```bash
# 1. Login to Heroku
heroku login

# 2. Create app
heroku create rag-chatbot

# 3. Create Procfile
echo "web: streamlit run app.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile

# 4. Create runtime.txt
echo "python-3.10.0" > runtime.txt

# 5. Deploy
git push heroku main

# 6. View app
heroku open
```

**Heroku Dockerfile:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc g++ && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

ENV PYTHONUNBUFFERED=1

CMD exec streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

---

## Performance Optimization

### 1. Reduce Image Size

```dockerfile
# Use slim base image
FROM python:3.10-slim

# Multi-stage build
FROM python:3.10-slim as builder
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

FROM python:3.10-slim
COPY --from=builder /app/wheels /wheels
COPY --from=builder requirements.txt .
RUN pip install --no-cache /wheels/*
```

### 2. Cache Embeddings and Index

```bash
# Store in persistent volume or cloud storage
# Update src/config.py to load from cloud
```

### 3. Enable Model Caching

In your Streamlit app:
```python
@st.cache_resource
def load_chatbot():
    return initialize_chatbot()
```

### 4. Load Balancing (Multi-instance)

```bash
# AWS ECS
aws ecs update-service \
    --cluster rag-chatbot \
    --service rag-chatbot-service \
    --desired-count 3

# Or with Kubernetes
kubectl scale deployment rag-chatbot --replicas=3
```

---

## Monitoring

### Docker Health Checks
```bash
docker inspect --format='{{.State.Health.Status}}' <container_id>
```

### Cloud Provider Monitoring

**AWS CloudWatch:**
```bash
aws logs tail /ecs/rag-chatbot --follow
```

**Google Cloud Logging:**
```bash
gcloud logging read "resource.type=cloud_run_revision"
```

**Azure Monitor:**
Access through Azure Portal → Container Instances → Logs

---

## Cost Optimization

| Provider | Free Tier | Recommended |
|----------|-----------|-------------|
| **AWS** | 750 hrs EC2 | t3.small (~$7/month) |
| **GCP** | $300 credit | f1-micro (~$5/month) |
| **Azure** | $200 credit | B1 (~$7/month) |
| **Heroku** | Deprecated | $7/month |

---

## Troubleshooting Deployments

### Container Won't Start
```bash
# Check logs
docker logs <container_id>

# Test locally first
docker run -it --rm rag-chatbot:latest
```

### Out of Memory
Increase memory allocation:
- AWS: Increase task memory
- GCP: Use `--memory 4Gi`
- Azure: Increase container memory

### Slow Startup
```bash
# Pre-warm embeddings in image
# Add to Dockerfile before CMD:
RUN python -m src.data_loader && \
    python -m src.embedder && \
    python -m src.retriever
```

---

## Environment Variables

Set these in your deployment platform:

```
PYTHONUNBUFFERED=1
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_LOGGER_LEVEL=info
```

---

For production setups, use CI/CD pipelines (GitHub Actions, GitLab CI, etc.) for automated builds and deployments.
