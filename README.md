# FastAPI on Kubernetes

A learning project to understand Kubernetes concepts using a simple FastAPI app.

## Stack

- **FastAPI** - Python web framework
- **Docker** - containerize the app
- **Kubernetes** - orchestrate containers
- **Minikube / Docker Desktop** - local K8s cluster

## Project Structure

```
fastapi-k8s/
├── app/
│   ├── main.py          # FastAPI app, health probes
│   └── routers.py       # API routes
├── k8s/
│   ├── namespace.yaml   # isolated namespace
│   ├── deployment.yaml  # 3 replicas, rolling update, probes, resource limits
│   ├── service.yaml     # NodePort service
│   ├── configmap.yaml   # non-sensitive env vars
│   ├── secret.yaml      # sensitive env vars
│   └── ingress.yaml     # HTTP routing
├── Dockerfile
├── requirements.txt
├── quick_commands.md    # kubectl & minikube cheat sheet
└── kubernetes_knowledge.md  # full K8s knowledge base
```

## K8s Concepts Covered

- Pods, Deployments, Services, Namespaces
- ConfigMap & Secrets
- Liveness & Readiness probes
- Rolling updates with zero downtime
- Resource requests & limits
- Ingress with nginx
- Horizontal scaling

## Run Locally

### Prerequisites
- Docker Desktop
- Minikube (`brew install minikube`)

### Steps

```bash
# 1. Start minikube
minikube start --driver=docker

# 2. Build and push image
docker build -t fastapi-k8s:v1 .
docker tag fastapi-k8s:v1 <your-dockerhub-username>/fastapi-k8s:v1
docker push <your-dockerhub-username>/fastapi-k8s:v1

# 3. Apply manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/

# 4. Open in browser
minikube service fastapi-service -n fastapi-k8s
```

## API Endpoints

| Endpoint | Description |
|---|---|
| `GET /` | Root |
| `GET /items` | List items |
| `GET /items/{id}` | Get item by ID |
| `GET /health/live` | Liveness probe |
| `GET /health/ready` | Readiness probe |
| `GET /docs` | Swagger UI |
