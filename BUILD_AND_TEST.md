# Build and Test Guide

## 🎯 Current Status

**✅ 7 Complete Scenarios Ready to Build & Test!**

All applications use real, meaningful code (not just hello world):
1. CrashLoopBackOff - Python app
2. ImagePullBackOff - (reuses #1)
3. Port Mismatch - Flask web app
4. Missing ConfigMap - Blog configuration app
5. RBAC Forbidden - Pod monitor dashboard
6. OOMKilled - Image processor service
7. Probe Failure - API health check service

## 📦 Prerequisites

```bash
# 1. Start Docker Desktop
open -a Docker

# 2. Wait for Docker to start, then verify
docker ps

# 3. Login to Docker Hub
docker login -u vellankikoti

# 4. Verify Kubernetes cluster
kubectl cluster-info

# If no cluster, create one:
kind create cluster --name k8s-workshop
# OR
minikube start
```

## 🏗️ Build All Images

```bash
cd /Users/koti/workshop/workshops/k8s-workshop

# Build Scenario 1 - CrashLoop
echo "Building scenario 1..."
docker build -t vellankikoti/k8s-masterclass-crashloop:v1.0 \
  -t vellankikoti/k8s-masterclass-crashloop:latest \
  scenarios/01-crashloop-backoff/app/

# Build Scenario 3 - WebApp
echo "Building scenario 3..."
docker build -t vellankikoti/k8s-masterclass-webapp:v1.0 \
  -t vellankikoti/k8s-masterclass-webapp:latest \
  scenarios/03-port-mismatch/app/

# Build Scenario 4 - ConfigMap
echo "Building scenario 4..."
docker build -t vellankikoti/k8s-masterclass-config-app:v1.0 \
  -t vellankikoti/k8s-masterclass-config-app:latest \
  scenarios/04-missing-configmap/app/

# Build Scenario 5 - RBAC
echo "Building scenario 5..."
docker build -t vellankikoti/k8s-masterclass-rbac-app:v1.0 \
  -t vellankikoti/k8s-masterclass-rbac-app:latest \
  scenarios/05-rbac-forbidden/app/

# Build Scenario 6 - Memory
echo "Building scenario 6..."
docker build -t vellankikoti/k8s-masterclass-memory-hog:v1.0 \
  -t vellankikoti/k8s-masterclass-memory-hog:latest \
  scenarios/06-oom-killed/app/

# Build Scenario 7 - Probes
echo "Building scenario 7..."
docker build -t vellankikoti/k8s-masterclass-health-app:v1.0 \
  -t vellankikoti/k8s-masterclass-health-app:latest \
  scenarios/07-probe-failure/app/

echo "✅ All images built!"
```

## 📤 Push to Docker Hub

```bash
# Push all images
docker push vellankikoti/k8s-masterclass-crashloop:v1.0
docker push vellankikoti/k8s-masterclass-crashloop:latest

docker push vellankikoti/k8s-masterclass-webapp:v1.0
docker push vellankikoti/k8s-masterclass-webapp:latest

docker push vellankikoti/k8s-masterclass-config-app:v1.0
docker push vellankikoti/k8s-masterclass-config-app:latest

docker push vellankikoti/k8s-masterclass-rbac-app:v1.0
docker push vellankikoti/k8s-masterclass-rbac-app:latest

docker push vellankikoti/k8s-masterclass-memory-hog:v1.0
docker push vellankikoti/k8s-masterclass-memory-hog:latest

docker push vellankikoti/k8s-masterclass-health-app:v1.0
docker push vellankikoti/k8s-masterclass-health-app:latest

echo "✅ All images pushed to Docker Hub!"
```

## 🧪 Test Each Scenario

### Test Scenario 1: CrashLoopBackOff

```bash
cd scenarios/01-crashloop-backoff

# Deploy broken version
kubectl apply -f broken/

# Wait 30 seconds, then check
kubectl get pods
# Should see: CrashLoopBackOff

# Check logs
kubectl logs -l app=crashloop-app
# Should see: ERROR: REQUIRED_CONFIG environment variable is not set!

# Apply fix
kubectl apply -f solution/

# Verify
kubectl get pods
# Should see: Running

# Cleanup
kubectl delete -f solution/
```

### Test Scenario 2: ImagePullBackOff

```bash
cd ../02-image-pull-backoff

kubectl apply -f broken/
sleep 20
kubectl get pods
# Should see: ImagePullBackOff

kubectl describe pod -l app=imagepull-app | grep -A 5 Events
# Should see: Failed to pull image...tag "broken": not found

kubectl apply -f solution/
kubectl get pods
# Should see: Running

kubectl delete -f solution/
```

### Test Scenario 3: Port Mismatch

```bash
cd ../03-port-mismatch

kubectl apply -f broken/
kubectl get pods,svc

# Test connectivity (should fail)
kubectl run curl-test --image=curlimages/curl:latest --rm -it --restart=Never -- \
  curl -v http://webapp-service

# Apply fix
kubectl apply -f solution/

# Test connectivity (should work)
kubectl run curl-test --image=curlimages/curl:latest --rm -it --restart=Never -- \
  curl http://webapp-service

# Cleanup
kubectl delete -f solution/
```

### Test Scenario 4: Missing ConfigMap

```bash
cd ../04-missing-configmap

kubectl apply -f broken/
kubectl get pods
# Should see: CreateContainerConfigError

kubectl describe pod -l app=blog-app | grep -A 5 Events
# Should see: ConfigMap "blog-config" not found

kubectl apply -f solution/
kubectl get pods
# Should see: Running

# Access the blog
kubectl port-forward -l app=blog-app 8080:5000
# Open http://localhost:8080 in browser

kubectl delete -f solution/
```

### Test Scenario 5: RBAC Forbidden

```bash
cd ../05-rbac-forbidden

kubectl apply -f broken/
kubectl get pods
# Should see: Running

# Check logs for permission error
kubectl logs -l app=pod-monitor
# Should see: ERROR: 403 - Forbidden: ServiceAccount lacks permission

kubectl apply -f solution/
kubectl logs -l app=pod-monitor
# Should see: Found X pods (no error)

# Access dashboard
kubectl port-forward -l app=pod-monitor 8080:5000
# Open http://localhost:8080 - should see pod list

kubectl delete -f solution/
```

### Test Scenario 6: OOMKilled

```bash
cd ../06-oom-killed

kubectl apply -f broken/
kubectl get pods
# Pod starts normally

# Port-forward to access
kubectl port-forward -l app=image-processor 8080:5000 &

# Trigger memory usage
curl -X POST http://localhost:8080/process -H "Content-Type: application/json" -d '{"count":15}'

# Check pod status
kubectl get pods
# Should eventually see: OOMKilled or CrashLoopBackOff

kubectl describe pod -l app=image-processor | grep -A 3 "Last State"
# Should see: Reason: OOMKilled

# Apply fix
kubectl delete -f broken/
kubectl apply -f solution/

# Verify with larger memory limit
kubectl port-forward -l app=image-processor 8080:5000
# Can now process more images without OOMKilled

kubectl delete -f solution/
```

### Test Scenario 7: Probe Failure

```bash
cd ../07-probe-failure

kubectl apply -f broken/
kubectl get pods
# Might see: 1/1 Running but watch for issues

kubectl describe pod -l app=api-service | grep -A 5 Readiness
# Check probe configuration

# Apply fix
kubectl apply -f solution/

kubectl get pods
# Should see: 1/1 Running with correct ready count

kubectl delete -f solution/
```

## ✅ Verification Checklist

After testing:

- [ ] All 7 scenarios build without errors
- [ ] All images push to Docker Hub successfully
- [ ] Scenario 1: Pod crashes and logs show env var error
- [ ] Scenario 2: ImagePullBackOff visible
- [ ] Scenario 3: Service connectivity fails then works
- [ ] Scenario 4: CreateContainerConfigError then runs
- [ ] Scenario 5: 403 Forbidden in logs then pod list works
- [ ] Scenario 6: OOMKilled visible in pod status
- [ ] Scenario 7: Probes configured correctly

## 🚀 Push to GitHub

```bash
cd /Users/koti/workshop/workshops/k8s-workshop

# Check status
git status

# Add all files
git add .

# Commit
git commit -m "Initial release: 7 K8s troubleshooting scenarios

Complete scenarios:
- Scenario 1: CrashLoopBackOff
- Scenario 2: ImagePullBackOff
- Scenario 3: Service Port Mismatch
- Scenario 4: Missing ConfigMap
- Scenario 5: RBAC Forbidden
- Scenario 6: OOMKilled
- Scenario 7: Probe Failure

All with real applications, Docker images on Docker Hub (vellankikoti/k8s-masterclass-*),
comprehensive manifests, and ready for hands-on learning."

# Push to GitHub
git push -u origin main
```

## 📊 Success Metrics

**You've created:**
- ✅ 6 unique Docker images
- ✅ 7 complete troubleshooting scenarios
- ✅ 28+ files (apps, Dockerfiles, manifests, docs)
- ✅ Real applications (not hello world)
- ✅ Production-ready workshop material

**Impact:**
- Learners get hands-on with real K8s failures
- All scenarios use actual meaningful applications
- Progressive difficulty from beginner to intermediate
- Ready to share with the community!

---

## 🎉 You're Ready!

1. Build the images ⬆️
2. Push to Docker Hub ⬆️
3. Test scenarios ⬆️
4. Push to GitHub ⬆️
5. Share your workshop! 🚀

**Estimated time:** 1-2 hours for build, push, and test
