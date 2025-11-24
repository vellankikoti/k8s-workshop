# Build and Test Guide

## 🎯 Current Status

**✅ 10 Complete Scenarios Ready to Build & Test!**

All applications use real, meaningful code (not just hello world):
1. CrashLoopBackOff - Python app requiring env var
2. ImagePullBackOff - (reuses #1 image with wrong tag)
3. Port Mismatch - Flask web app
4. Missing ConfigMap - Blog configuration app
5. RBAC Forbidden - Pod monitor dashboard
6. OOMKilled - Image processor service
7. Probe Failure - API health check service
8. Network Policy - Order service (client) + Inventory service (server)
9. PVC Pending - File storage service
10. Init Container Failure - Todo app with Redis dependency

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

### Option 1: Use Build Scripts (Recommended)

**Bash Script (macOS, Linux, WSL):**
```bash
cd /Users/koti/workshop/workshops/k8s-workshop
chmod +x scripts/build-and-push-all.sh
./scripts/build-and-push-all.sh
```

**Python Script (Cross-platform):**
```bash
cd /Users/koti/workshop/workshops/k8s-workshop
python3 scripts/build-and-push-all.py
```

### Option 2: Manual Build Commands

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

# Build Scenario 8 - Network Policy (Client)
echo "Building scenario 8 - client..."
docker build -t vellankikoti/k8s-masterclass-netpol-client:v1.0 \
  -t vellankikoti/k8s-masterclass-netpol-client:latest \
  scenarios/08-network-policy/app-client/

# Build Scenario 8 - Network Policy (Server)
echo "Building scenario 8 - server..."
docker build -t vellankikoti/k8s-masterclass-netpol-server:v1.0 \
  -t vellankikoti/k8s-masterclass-netpol-server:latest \
  scenarios/08-network-policy/app-server/

# Build Scenario 9 - Storage
echo "Building scenario 9..."
docker build -t vellankikoti/k8s-masterclass-storage-app:v1.0 \
  -t vellankikoti/k8s-masterclass-storage-app:latest \
  scenarios/09-pvc-pending/app/

# Build Scenario 10 - Init Container App
echo "Building scenario 10 - init app..."
docker build -t vellankikoti/k8s-masterclass-init-app:v1.0 \
  -t vellankikoti/k8s-masterclass-init-app:latest \
  scenarios/10-init-container-failure/app/

# Build Scenario 10 - Init Wait (busybox-based)
echo "Building scenario 10 - init wait..."
docker build -t vellankikoti/k8s-masterclass-init-wait:v1.0 \
  -t vellankikoti/k8s-masterclass-init-wait:latest \
  scenarios/10-init-container-failure/init-wait/

# Build Scenario 10 - Redis
echo "Building scenario 10 - redis..."
docker build -t vellankikoti/k8s-masterclass-redis:v1.0 \
  -t vellankikoti/k8s-masterclass-redis:latest \
  scenarios/10-init-container-failure/redis/

echo "✅ All images built!"
```

## 📤 Push to Docker Hub

### Option 1: Use Build Scripts (Recommended)

The build scripts automatically push images after building them.

### Option 2: Manual Push Commands

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

docker push vellankikoti/k8s-masterclass-netpol-client:v1.0
docker push vellankikoti/k8s-masterclass-netpol-client:latest

docker push vellankikoti/k8s-masterclass-netpol-server:v1.0
docker push vellankikoti/k8s-masterclass-netpol-server:latest

docker push vellankikoti/k8s-masterclass-storage-app:v1.0
docker push vellankikoti/k8s-masterclass-storage-app:latest

docker push vellankikoti/k8s-masterclass-init-app:v1.0
docker push vellankikoti/k8s-masterclass-init-app:latest

docker push vellankikoti/k8s-masterclass-init-wait:v1.0
docker push vellankikoti/k8s-masterclass-init-wait:latest

docker push vellankikoti/k8s-masterclass-redis:v1.0
docker push vellankikoti/k8s-masterclass-redis:latest

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
# Both pods and service should be running

# Test connectivity from inside cluster (should fail)
kubectl run curl-test --image=curlimages/curl:latest --rm -it --restart=Never -- \
  curl -v http://webapp-service
# Should see: Connection refused or timeout

# Test via port-forward (broken state - should fail)
# In one terminal:
kubectl port-forward svc/webapp-service 8080:80
# In another terminal or browser:
curl http://localhost:8080
# Should fail: Connection established but no response, or timeout
# This is because service targets port 8080, but container listens on 5000

# Verify direct pod access works (bypasses service)
POD_NAME=$(kubectl get pod -l app=webapp -o jsonpath='{.items[0].metadata.name}')
kubectl port-forward $POD_NAME 8081:5000 &
# In another terminal:
curl http://localhost:8081
# Should work! This proves the app is running correctly

# Apply fix
kubectl apply -f solution/

# Test connectivity from inside cluster (should work now)
kubectl run curl-test --image=curlimages/curl:latest --rm -it --restart=Never -- \
  curl http://webapp-service
# Should see JSON response with success message

# Test via port-forward (fixed state - should work)
# Stop previous port-forward (Ctrl+C), then:
kubectl port-forward svc/webapp-service 8080:80
# In another terminal or browser:
curl http://localhost:8080
# OR open http://localhost:8080 in browser
# Should see JSON response with success message

# Cleanup
kubectl delete -f solution/
```

**Key Points:**
- Port-forward to service: Use `kubectl port-forward svc/webapp-service 8080:80` (service port is 80)
- Port-forward to pod: Use `kubectl port-forward <pod> 8080:5000` (container port is 5000)
- Broken state: Service can't reach pods (port mismatch)
- Fixed state: Service successfully routes traffic to pods

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
POD_NAME=$(kubectl get pod -l app=blog-app -o jsonpath='{.items[0].metadata.name}')
kubectl port-forward $POD_NAME 8080:5000
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

# Access dashboard (broken state - shows error)
POD_NAME=$(kubectl get pod -l app=pod-monitor -o jsonpath='{.items[0].metadata.name}')
kubectl port-forward $POD_NAME 8080:5000 &
# Open http://localhost:8080 - should see error message
# Stop port-forward (Ctrl+C or kill process)

kubectl apply -f solution/
kubectl logs -l app=pod-monitor
# Should see: Found X pods (no error)

# Access dashboard (fixed state - shows pod list)
POD_NAME=$(kubectl get pod -l app=pod-monitor -o jsonpath='{.items[0].metadata.name}')
kubectl port-forward $POD_NAME 8080:5000
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
POD_NAME=$(kubectl get pod -l app=image-processor -o jsonpath='{.items[0].metadata.name}')
kubectl port-forward $POD_NAME 8080:5000 &

# Trigger memory usage
curl -X POST http://localhost:8080/process -H "Content-Type: application/json" -d '{"count":15}'
# You might see: "Empty reply from server" - this is expected! Pod was killed during processing.

# Check pod status immediately
kubectl get pods -l app=image-processor
# May show: OOMKilled, CrashLoopBackOff, or Running (with RESTARTS: 1)

# Verify OOMKilled occurred (even if pod shows as Running)
kubectl describe pod -l app=image-processor | grep -A 5 "Last State"
# Should see: Reason: OOMKilled, Exit Code: 137

# Check events for OOMKilled
kubectl describe pod -l app=image-processor | grep -i "oom"
# Should see: Warning OOMKilled - Memory limit exceeded

# Note: If pod shows as Running with RESTARTS: 1, Kubernetes restarted it after OOMKilled
# This is normal - check Last State to confirm OOMKilled occurred

# Apply fix
kubectl delete -f broken/
kubectl apply -f solution/

# Wait for pod to restart
kubectl get pods -l app=image-processor

# Verify with larger memory limit
POD_NAME=$(kubectl get pod -l app=image-processor -o jsonpath='{.items[0].metadata.name}')
kubectl port-forward $POD_NAME 8080:5000 &

# Try processing again
curl -X POST http://localhost:8080/process -H "Content-Type: application/json" -d '{"count":15}'
# Should succeed now (no "Empty reply from server")

# Verify pod stays running
kubectl get pods -l app=image-processor
# Should see: Running with RESTARTS: 0 (or same as before, no new restart)

kubectl delete -f solution/
```

**Key Points:**
- "Empty reply from server" = pod was OOMKilled during processing (expected)
- Pod may show as `Running` after restart - check `Last State` to confirm OOMKilled
- `RESTARTS: 1` indicates pod was killed and restarted
- Exit code 137 = OOMKilled (128 + SIGKILL)

### Test Scenario 7: Probe Failure

```bash
cd ../07-probe-failure

kubectl apply -f broken/
sleep 30

# Check pod status (should be 0/1 Ready)
kubectl get pods -l app=api-service
# Should see: 0/1 Ready

# Run demo script
./demo-probe-issue.sh
# Shows: probe checks wrong endpoint, no endpoints

# Check probe configuration
kubectl get deployment api-service -o yaml | grep -A 5 readinessProbe
# Should see: path: /readiness (wrong!)

# Check probe failures
kubectl describe pod -l app=api-service | grep -A 2 "Readiness probe failed"
# Should see: HTTP probe failed with statuscode: 404

# Test endpoints
pkill -f "kubectl port-forward.*8080" || true
POD_NAME=$(kubectl get pod -l app=api-service -o jsonpath='{.items[0].metadata.name}')
kubectl port-forward $POD_NAME 8080:5000 &
sleep 2

curl -v http://localhost:8080/readiness
# Should see: 404 NOT FOUND

curl -v http://localhost:8080/ready
# Should see: 200 OK (if pod > 10s) or 503 (if < 10s)

# Apply fix
kubectl apply -f solution/
sleep 15

# Verify fix
kubectl get pods -l app=api-service
# Should see: 1/1 Ready

kubectl get endpoints api-service
# Should see: Endpoints populated

# Test service
kubectl run curl-test --image=curlimages/curl:latest --rm -it --restart=Never -- \
  curl http://api-service/api/data
# Should work!

# Cleanup
pkill -f "kubectl port-forward" || true
kubectl delete -f solution/
```

**Key Points:**
- Broken: Probe checks `/readiness` (doesn't exist) → 404 → pods never ready
- Fixed: Probe checks `/ready` (exists) → pods ready → service works

### Test Scenario 8: Network Policy

```bash
cd ../08-network-policy

kubectl apply -f broken/
sleep 20

# Check pods are running
kubectl get pods -l 'app in (order,inventory)'
# Both should be running

# Test connectivity (should fail)
ORDER_POD=$(kubectl get pod -l app=order -o jsonpath='{.items[0].metadata.name}')
kubectl exec $ORDER_POD -- wget -O- --timeout=3 http://inventory-service:80
# Should fail: timeout or connection refused

# Check NetworkPolicy
kubectl get networkpolicies
kubectl describe networkpolicy deny-all-ingress
# Should see: Allowing ingress traffic: <none> (deny all)

# Apply fix
kubectl apply -f solution/
sleep 5

# Test connectivity again (should work now)
kubectl exec $ORDER_POD -- wget -O- --timeout=3 http://inventory-service:80
# Should succeed with JSON response

# Access order service dashboard
kubectl port-forward $ORDER_POD 8080:5000 &
sleep 2
# Open http://localhost:8080 in browser - should see inventory items

# Cleanup
pkill -f "kubectl port-forward.*8080" || true
kubectl delete -f solution/
```

**Key Points:**
- Broken: NetworkPolicy has no ingress rules → deny all → connection fails
- Fixed: NetworkPolicy allows frontend → backend → connection succeeds
- Port-forward: Use `localhost:8080` (not 5000) after port-forwarding

### Test Scenario 9: PVC Pending

```bash
cd ../09-pvc-pending

kubectl apply -f broken/
kubectl get pvc
# Should see: STATUS Pending

kubectl describe pvc file-storage
# Should see: Warning ProvisioningFailed, storageclass.storage.k8s.io "<none>" not found

kubectl get pods
# Should see: ContainerCreating (stuck waiting for PVC)

# Check available StorageClasses
kubectl get storageclass
# Note the StorageClass name (usually "standard" or "hostpath")

# Apply fix (may need to update storageClassName in solution/deployment.yaml)
kubectl apply -f solution/

kubectl get pvc
# Should see: STATUS Bound

kubectl get pods
# Should see: Running

# Access file service
POD_NAME=$(kubectl get pod -l app=file-service -o jsonpath='{.items[0].metadata.name}')
kubectl port-forward $POD_NAME 8080:5000
# Open http://localhost:8080 in browser

kubectl delete -f solution/
```

### Test Scenario 10: Init Container Failure

```bash
cd ../10-init-container-failure

kubectl apply -f broken/
kubectl get pods
# Should see: Init:Error or Init:CrashLoopBackOff

kubectl describe pod -l app=todo
# Should see: Init Containers: wait-for-redis - State: Waiting, Reason: CrashLoopBackOff

kubectl logs -l app=todo -c wait-for-redis
# Should see: nc: can't resolve 'redis-nonexistent'

# Apply fix
kubectl apply -f solution/

# Wait for Redis to start
kubectl get pods -l app=redis
# Should see: Running

# Check todo app
kubectl get pods -l app=todo
# Should see: Running (init container completed)

kubectl logs -l app=todo -c wait-for-redis
# Should see: ✅ Redis is ready!

# Access todo app
POD_NAME=$(kubectl get pod -l app=todo -o jsonpath='{.items[0].metadata.name}')
kubectl port-forward $POD_NAME 8080:5000
# Open http://localhost:8080 - should see todo app working

kubectl delete -f solution/
```

## ✅ Verification Checklist

After testing all scenarios:

- [ ] All 10 scenarios build without errors
- [ ] All images push to Docker Hub successfully
- [ ] Scenario 1: Pod crashes and logs show env var error
- [ ] Scenario 2: ImagePullBackOff visible
- [ ] Scenario 3: Service connectivity fails then works
- [ ] Scenario 4: CreateContainerConfigError then runs
- [ ] Scenario 5: 403 Forbidden in logs then pod list works
- [ ] Scenario 6: OOMKilled visible in pod status
- [ ] Scenario 7: Probes configured correctly, endpoints populated
- [ ] Scenario 8: NetworkPolicy blocks then allows traffic
- [ ] Scenario 9: PVC pending then bound, pod starts
- [ ] Scenario 10: Init container fails then succeeds, app starts

## 🚀 Push to GitHub

```bash
cd /Users/koti/workshop/workshops/k8s-workshop

# Check status
git status

# Add all files
git add .

# Commit
git commit -m "Complete release: 10 K8s troubleshooting scenarios

Complete scenarios:
- Scenario 1: CrashLoopBackOff
- Scenario 2: ImagePullBackOff
- Scenario 3: Service Port Mismatch
- Scenario 4: Missing ConfigMap
- Scenario 5: RBAC Forbidden
- Scenario 6: OOMKilled
- Scenario 7: Probe Failure
- Scenario 8: Network Policy
- Scenario 9: PVC Pending
- Scenario 10: Init Container Failure

All with real applications, Docker images on Docker Hub (vellankikoti/k8s-masterclass-*),
comprehensive manifests, detailed README files, and ready for hands-on learning."

# Push to GitHub
git push -u origin main
```

## 📊 Success Metrics

**You've created:**
- ✅ 10 unique Docker images (including 2 for scenario 8)
- ✅ 10 complete troubleshooting scenarios
- ✅ 40+ files (apps, Dockerfiles, manifests, READMEs, docs)
- ✅ Real applications (not hello world)
- ✅ Production-ready workshop material
- ✅ Comprehensive documentation for each scenario

**Impact:**
- Learners get hands-on with real K8s failures
- All scenarios use actual meaningful applications
- Progressive difficulty from beginner to advanced
- Complete documentation and testing guides
- Ready to share with the community!

---

## 🎉 You're Ready!

1. Build the images ⬆️
2. Push to Docker Hub ⬆️
3. Test scenarios ⬆️
4. Push to GitHub ⬆️
5. Share your workshop! 🚀

**Estimated time:** 1-2 hours for build, push, and test

**Quick Test Command:**
```bash
# Test one scenario quickly
cd scenarios/01-crashloop-backoff
kubectl apply -f broken/ && sleep 10 && kubectl get pods && kubectl logs -l app=crashloop-app
```
