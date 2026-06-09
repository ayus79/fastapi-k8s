# Kubernetes Quick Commands

## Minikube

```bash
minikube start --driver=docker        # start cluster using Docker
minikube stop                         # stop cluster
minikube delete                       # delete cluster completely
minikube status                       # check cluster status
minikube dashboard                    # open K8s dashboard in browser
minikube tunnel                       # expose LoadBalancer services to localhost
minikube service fastapi-service -n fastapi-k8s  # open service URL in browser
```

## Apply Manifests

```bash
kubectl apply -f k8s/namespace.yaml   # always apply namespace first
kubectl apply -f k8s/                 # apply all manifests in k8s/ folder
kubectl delete -f k8s/               # delete all resources in k8s/ folder
```

## Pods

```bash
kubectl get pods -n fastapi-k8s              # list all pods
kubectl get pods -n fastapi-k8s -w           # watch pods in real time
kubectl describe pod <pod-name> -n fastapi-k8s  # full pod details + events
kubectl delete pod <pod-name> -n fastapi-k8s    # delete a pod (K8s auto-restarts it)
kubectl exec -it <pod-name> -n fastapi-k8s -- /bin/bash  # shell into a pod
```

## Logs

```bash
kubectl logs -n fastapi-k8s deployment/fastapi-deployment           # latest logs
kubectl logs -n fastapi-k8s deployment/fastapi-deployment -f        # stream logs live
kubectl logs -n fastapi-k8s deployment/fastapi-deployment --prefix=true  # show which pod served each request
kubectl logs -n fastapi-k8s <pod-name> --previous                   # logs from crashed pod
```

## Deployment

```bash
kubectl get deployments -n fastapi-k8s                              # list deployments
kubectl describe deployment fastapi-deployment -n fastapi-k8s       # full deployment details
kubectl rollout status deployment/fastapi-deployment -n fastapi-k8s # check rollout progress
kubectl rollout history deployment/fastapi-deployment -n fastapi-k8s # rollout history
kubectl rollout undo deployment/fastapi-deployment -n fastapi-k8s   # rollback to previous version
kubectl rollout restart deployment/fastapi-deployment -n fastapi-k8s # restart all pods
```

## Scaling

```bash
kubectl scale deployment fastapi-deployment -n fastapi-k8s --replicas=5  # scale to 5 pods
kubectl scale deployment fastapi-deployment -n fastapi-k8s --replicas=3  # scale back to 3
```

## Services

```bash
kubectl get svc -n fastapi-k8s                  # list services
kubectl describe svc fastapi-service -n fastapi-k8s  # full service details
```

## Ingress

```bash
kubectl get ingress -n fastapi-k8s              # list ingress rules
kubectl describe ingress -n fastapi-k8s         # full ingress details
```

## Namespace

```bash
kubectl get namespaces                          # list all namespaces
kubectl delete namespace fastapi-k8s            # delete namespace + everything inside it
```

## ConfigMap & Secret

```bash
kubectl get configmap -n fastapi-k8s            # list configmaps
kubectl get secret -n fastapi-k8s               # list secrets
kubectl describe configmap fastapi-config -n fastapi-k8s  # view configmap values
```

## Cluster Info

```bash
kubectl get all -n fastapi-k8s                  # list everything in namespace
kubectl get nodes                               # list cluster nodes
kubectl top pods -n fastapi-k8s                 # CPU/memory usage per pod (needs metrics-server)
kubectl top nodes                               # CPU/memory usage per node
kubectl config get-contexts                     # list all clusters kubectl knows about
kubectl config use-context minikube             # switch to minikube cluster
kubectl config use-context docker-desktop       # switch to Docker Desktop cluster
kubectl config current-context                  # show current active cluster
```

## Port Forward (temporary local access)

```bash
kubectl port-forward svc/fastapi-service 8010:80 -n fastapi-k8s  # forward service to localhost:8080
```

## Docker (build & push image)

```bash
docker build -t fastapi-k8s:v1 .                                        # build image
docker tag fastapi-k8s:v1 <your-dockerhub-username>/fastapi-k8s:v1             # tag for Docker Hub
docker push <your-dockerhub-username>/fastapi-k8s:v1                           # push to Docker Hub
```

