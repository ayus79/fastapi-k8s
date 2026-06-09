# Kubernetes Knowledge Base

## What is Kubernetes?

Kubernetes (K8s) is a container orchestration platform. It runs, scales, heals, and updates your containerized apps automatically.

```
Without K8s                     With K8s
-----------                     --------
Manual restarts                 Auto self-healing
Manual scaling                  Auto scaling
Downtime on deploy              Zero-downtime rolling updates
One server = one point of fail  Multiple pods across nodes
```

---

## Core Concepts

### Pod

- Smallest unit in K8s
- One or more containers running together
- Ephemeral - dies and gets replaced, never "fixed"
- Has its own IP inside the cluster (not accessible from outside)

### Deployment

- Manages pods - how many, which image, update strategy
- Ensures desired state is always maintained (e.g. always 3 pods)
- Handles rolling updates and rollbacks

### Service

- Stable network endpoint to reach your pods
- Pods come and go, Service IP stays the same
- Types:
  - `ClusterIP` - internal only (default)
  - `NodePort` - exposes on a port on each node
  - `LoadBalancer` - cloud load balancer (AWS ELB, GCP LB)

### Ingress

- HTTP/HTTPS routing into the cluster
- One entry point → routes to multiple services by path or host
- Needs an Ingress Controller (nginx, traefik) to work

### ConfigMap

- Non-sensitive config as env vars (APP_ENV, LOG_LEVEL)
- Never store passwords or secrets here

### Secret

- Sensitive config as env vars (DB passwords, API keys)
- Base64 encoded by K8s (not encrypted by default - see production checklist)

### Namespace

- Virtual cluster inside a cluster
- Isolates resources (dev, staging, prod can share one cluster)

### Node

- A server (VM or physical) that runs pods
- One node locally (minikube), many nodes in production

---

## Kubernetes Architecture

```
┌─────────────────────────────────────────┐
│              Control Plane              │
│  ┌──────────┐  ┌───────┐  ┌─────────┐  │
│  │  API     │  │ etcd  │  │Scheduler│  │
│  │  Server  │  │(state)│  │         │  │
│  └──────────┘  └───────┘  └─────────┘  │
└─────────────────────────────────────────┘
            │
    ┌───────┴────────┐
    ▼                ▼
┌────────┐      ┌────────┐
│ Node 1 │      │ Node 2 │    ← Worker Nodes
│ Pod    │      │ Pod    │
│ Pod    │      │ Pod    │
└────────┘      └────────┘
```

- **API Server** - everything talks to this (kubectl, pods, controllers)
- **etcd** - database that stores entire cluster state
- **Scheduler** - decides which node a new pod runs on
- **kubelet** - agent on each node, runs pods
- **kube-proxy** - handles networking between pods

---

## Local vs Production

### Local (Minikube)


| Thing      | Local Setup                                 |
| ---------- | ------------------------------------------- |
| Cluster    | Minikube (single node)                      |
| Driver     | Docker                                      |
| Image      | Push to Docker Hub, pull from there         |
| Access     | `minikube service` or `minikube tunnel`     |
| Secrets    | Plain text in secret.yaml (ok for learning) |
| Replicas   | 1-3 (your laptop has limited resources)     |
| Ingress    | nginx ingress via minikube addons           |
| TLS        | Not needed                                  |
| Monitoring | Optional                                    |


```bash
# enable ingress on minikube (easier than manual install)
minikube addons enable ingress

# expose LoadBalancer services
minikube tunnel
```

### Production (Cloud - GKE, EKS, AKS)


| Thing      | Production Setup                                     |
| ---------- | ---------------------------------------------------- |
| Cluster    | Managed K8s (GKE/EKS/AKS)                            |
| Image      | Private registry (ECR, GCR, Docker Hub private)      |
| Access     | Ingress + real domain + TLS (cert-manager)           |
| Secrets    | External secret manager (AWS Secrets Manager, Vault) |
| Replicas   | 3+ with HPA (auto-scaling)                           |
| Ingress    | Cloud load balancer + nginx/traefik                  |
| TLS        | cert-manager with Let's Encrypt                      |
| Monitoring | Prometheus + Grafana                                 |
| Logging    | ELK stack or cloud logging                           |


---

## Deployment Strategies

### Rolling Update (default - what we use)

```
Old: [v1] [v1] [v1]
         ↓
Step 1: [v2] [v1] [v1]   ← spin up new, kill old one by one
Step 2: [v2] [v2] [v1]
Step 3: [v2] [v2] [v2]
```

- Zero downtime
- Slow rollback if something goes wrong

### Blue-Green

```
Blue (v1) → live traffic
Green (v2) → deploy and test
Switch traffic to Green instantly
```

- Instant rollback (switch back to Blue)
- Needs double the resources

### Canary

```
v1 → 90% of traffic
v2 → 10% of traffic (testing on real users)
Gradually shift to 100% v2
```

- Best for risky changes
- Complex to set up

---

## Resource Management

Always set requests and limits on every container:

```yaml
resources:
  requests:
    cpu: "100m"      # guaranteed minimum
    memory: "128Mi"
  limits:
    cpu: "500m"      # hard cap
    memory: "256Mi"
```

- **Requests** - what K8s guarantees your pod gets
- **Limits** - hard ceiling, pod gets killed if it exceeds memory limit
- `100m` CPU = 0.1 core, `1000m` = 1 full core

---

## Health Probes

```yaml
livenessProbe:   # is the app alive? if fails → restart pod
readinessProbe:  # is the app ready? if fails → remove from load balancer
startupProbe:    # is the app done starting? protects slow-starting apps
```

Rule of thumb:

- Liveness → check if process is alive (`/health/live`)
- Readiness → check if DB is connected, cache is warm (`/health/ready`)
- Startup → for apps that take >30s to start

---

## Horizontal Pod Autoscaler (HPA)

Automatically scales pods based on CPU/memory:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: fastapi-hpa
  namespace: fastapi-k8s
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: fastapi-deployment
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70   # scale up when CPU > 70%
```

Requires metrics-server:

```bash
minikube addons enable metrics-server   # local
```

---

## Networking

```
Internet
   ↓
Ingress (nginx)          ← handles HTTP routing, TLS termination
   ↓
Service (ClusterIP)      ← stable internal IP, load balances across pods
   ↓
Pod 1 / Pod 2 / Pod 3   ← actual app containers
```

- Pods talk to each other via Service name (DNS): `http://fastapi-service/`
- Never hardcode pod IPs - they change every restart

---

## Storage

Pods are stateless - files written inside a pod are lost when it dies.


| Type                    | Use for                                           |
| ----------------------- | ------------------------------------------------- |
| `emptyDir`              | Temp files, shared between containers in same pod |
| `hostPath`              | Mount a folder from the node (local dev only)     |
| `PersistentVolume`      | Real persistent storage (databases)               |
| `PersistentVolumeClaim` | Pod's request for storage                         |


For databases in K8s - use **StatefulSets** (not Deployments). Or better: run DB outside K8s (managed DB like MongoDB Atlas, RDS).

---

## Local Development Checklist

- Docker Desktop installed and running
- Minikube installed (`brew install minikube`)
- Minikube started (`minikube start --driver=docker`)
- Image built (`docker build -t name:tag .`)
- Image pushed to Docker Hub
- Namespace applied first (`kubectl apply -f k8s/namespace.yaml`)
- All manifests applied (`kubectl apply -f k8s/`)
- Pods are Running (`kubectl get pods -n <namespace>`)
- Service is created (`kubectl get svc -n <namespace>`)
- App is accessible (`minikube service <service-name> -n <namespace>`)
- Liveness probe returns 200
- Readiness probe returns 200
- Logs look clean (`kubectl logs -n <namespace> deployment/<name>`)

---

## Production Readiness Checklist

### Docker Image

- Use slim/alpine base image (smaller attack surface)
- Pin exact versions (`python:3.12.3-slim` not `python:latest`)
- Run as non-root user inside container
- `.dockerignore` excludes `env/`, `.env`, `__pycache__`, `*.pyc`
- No secrets baked into the image
- Image stored in private registry (ECR, GCR)
- Image tagged with git commit SHA (not just `latest`)

### Kubernetes Manifests

- All resources have a `namespace`
- All containers have `resources.requests` and `resources.limits`
- `livenessProbe` configured
- `readinessProbe` configured
- `replicas` is at least 2 (never run single pod in prod)
- `RollingUpdate` strategy with `maxUnavailable: 0`
- `imagePullPolicy: Always` (so latest pushed image is always pulled)
- Pod `antiAffinity` set (spread pods across nodes, not all on one)

### Secrets & Config

- No secrets committed to git
- Secrets stored in external manager (AWS Secrets Manager, Vault, Sealed Secrets)
- `.env` file in `.gitignore`
- `secret.yaml` in `.gitignore`
- Secrets rotated regularly

### Networking

- Ingress configured with real domain
- TLS enabled (cert-manager + Let's Encrypt)
- HTTP redirects to HTTPS
- `NetworkPolicy` restricts pod-to-pod traffic
- Rate limiting on Ingress

### Scaling & Availability

- HPA configured (auto-scale on CPU/memory)
- `PodDisruptionBudget` set (prevents all pods being killed during node drain)
- Pods spread across multiple nodes (antiAffinity)
- Multiple nodes in the cluster (not single node)

### Monitoring & Logging

- Prometheus + Grafana installed
- Alerts set up (pod crash, high CPU, high memory)
- Centralized logging (ELK, Loki, or cloud logging)
- `/health/live` and `/health/ready` endpoints work correctly
- Request latency and error rate dashboards set up

### CI/CD

- CI pipeline builds and pushes image on every merge
- Image tagged with git SHA
- CD pipeline applies manifests automatically
- Rollback procedure documented and tested
- Staging environment mirrors production

### Security

- Container runs as non-root user
- `readOnlyRootFilesystem: true` where possible
- `allowPrivilegeEscalation: false`
- K8s RBAC configured (least privilege)
- Cluster API server not publicly exposed
- etcd encrypted at rest
- Regular K8s version upgrades

---

## Common kubectl Patterns

```bash
# get all resources in a namespace
kubectl get all -n fastapi-k8s

# describe a resource (best for debugging)
kubectl describe pod <pod-name> -n fastapi-k8s

# shell into a running pod
kubectl exec -it <pod-name> -n fastapi-k8s -- /bin/bash

# copy file from pod to local
kubectl cp fastapi-k8s/<pod-name>:/app/file.txt ./file.txt

# watch resource changes in real time
kubectl get pods -n fastapi-k8s -w

# check events (great for debugging why pod won't start)
kubectl get events -n fastapi-k8s --sort-by='.lastTimestamp'

# force delete a stuck pod
kubectl delete pod <pod-name> -n fastapi-k8s --grace-period=0 --force
```

---

## Debugging Pods

```
Pod not starting?
  ↓
kubectl describe pod <name> -n <namespace>
  → look at Events section at the bottom

Common errors:
  ErrImagePull        → wrong image name or not pushed to registry
  ErrImageNeverPull   → image not found locally (imagePullPolicy: Never)
  CrashLoopBackOff    → app is crashing on startup, check logs
  OOMKilled           → pod exceeded memory limit, increase limits
  Pending             → no node has enough resources to schedule pod
  CreateContainerConfigError → ConfigMap or Secret not found
```

```bash
# step 1 - describe the pod
kubectl describe pod <pod-name> -n fastapi-k8s

# step 2 - check logs
kubectl logs <pod-name> -n fastapi-k8s

# step 3 - check logs of crashed pod
kubectl logs <pod-name> -n fastapi-k8s --previous

# step 4 - check cluster events
kubectl get events -n fastapi-k8s --sort-by='.lastTimestamp'
```

