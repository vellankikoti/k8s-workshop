# Scenario 7: Probe Failure

**Difficulty:** Intermediate
**Estimated Time:** 20 minutes
**Image:** `vellankikoti/k8s-masterclass-health-app:v1.0`

## Learning Objectives

- Understand Kubernetes health probes (liveness, readiness)
- Learn the difference between liveness and readiness probes
- Identify probe configuration issues
- Debug probe failures using `kubectl describe`
- Understand how probes affect pod status and traffic routing

## The Challenge

Your team deployed an API service, but the pods show `0/1 Ready` and won't receive traffic. The readiness probe is failing with 404 errors.

**Your mission:** Find out why the readiness probe is failing and fix it!

## Step 1: Deploy the Broken Application

```bash
cd scenarios/07-probe-failure
kubectl apply -f broken/
```

## Step 2: Observe the Failure

Wait 30 seconds, then check pod status:

```bash
kubectl get pods -l app=api-service
```

**Expected output:**
```
NAME                           READY   STATUS    RESTARTS   AGE
api-service-xxxxxxxxxx-xxxxx   0/1     Running   0          1m
api-service-xxxxxxxxxx-xxxxx   0/1     Running   0          1m
```

❌ Pods show `0/1 Ready` - they're not ready!

Check service endpoints:
```bash
kubectl get endpoints api-service
```

**Expected output:**
```
NAME           ENDPOINTS   AGE
api-service    <none>      1m
```

❌ No endpoints! Service can't route traffic.

## Step 3: Investigate

### Check Pod Events

```bash
kubectl describe pod -l app=api-service
```

Look for **Events** section:

```
Events:
  Type     Reason     Age                From               Message
  ----     ------     ----               ----               -------
  Warning  Unhealthy  30s (x6 over 1m)   kubelet            Readiness probe failed: HTTP probe failed with statuscode: 404
```

❌ **Readiness probe failed: 404** - The probe is checking an endpoint that doesn't exist!

### Check Probe Configuration

```bash
kubectl get deployment api-service -o yaml | grep -A 5 readinessProbe
```

**What you'll see:**
```yaml
readinessProbe:
  httpGet:
    path: /readiness  # ❌ This endpoint doesn't exist!
    port: 5000
```

**Problem:** The readiness probe is checking `/readiness`, but this endpoint doesn't exist in the application!

### Test What Endpoints Actually Exist

The application runs on port 5000 inside the container. We'll use port-forward to test it locally:

```bash
# Kill any existing port-forwards
pkill -f "kubectl port-forward.*8080" || true

# Get a pod name
POD_NAME=$(kubectl get pod -l app=api-service -o jsonpath='{.items[0].metadata.name}')

# Port-forward: local port 8080 → container port 5000
kubectl port-forward $POD_NAME 8080:5000 &
sleep 2

# Test the endpoint the probe is checking (doesn't exist!)
# Note: We use localhost:8080 (the forwarded port), not 5000
curl -v http://localhost:8080/readiness
```

**Expected output:**
```
< HTTP/1.1 404 NOT FOUND
```

❌ 404 - This endpoint doesn't exist! This is why the probe fails.

```bash
# Test the correct endpoint
# Note: Still using localhost:8080 (the forwarded port)
curl -v http://localhost:8080/ready
```

**Expected output (if pod is > 10 seconds old):**
```json
{"status": "ready", "message": "Application is ready to receive traffic"}
```
HTTP Status: `200 OK`

✅ The `/ready` endpoint exists and works!

```bash
# Clean up
pkill -f "kubectl port-forward.*8080" || true
```

## Step 4: The Solution

The readiness probe should check `/ready`, not `/readiness`.

**The Fix:**
```bash
kubectl apply -f solution/
```

**What changed:**
- Readiness probe path: `/readiness` → `/ready` ✅

Wait 15 seconds, then verify:

```bash
kubectl get pods -l app=api-service
```

**Expected output:**
```
NAME                           READY   STATUS    RESTARTS   AGE
api-service-xxxxxxxxxx-xxxxx   1/1     Running   0          1m
api-service-xxxxxxxxxx-xxxxx   1/1     Running   0          1m
```

✅ Pods are now `1/1 Ready`!

```bash
kubectl get endpoints api-service
```

**Expected output:**
```
NAME           ENDPOINTS                                    AGE
api-service    10.244.0.5:5000,10.244.0.6:5000             1m
```

✅ Endpoints are populated!

Test the service:
```bash
kubectl run curl-test --image=curlimages/curl:latest --rm -it --restart=Never -- \
  curl http://api-service/api/data
```

✅ Service works!

## Step 5: Cleanup

```bash
kubectl delete -f solution/
pkill -f "kubectl port-forward.*8080" || true
```

## What You Learned

✅ Readiness probes check if pods can receive traffic
✅ If probe fails → pod not ready → removed from service endpoints
✅ Probe must check an endpoint that actually exists
✅ `/ready` endpoint indicates service readiness
✅ `/health` endpoint indicates process liveness

## Key Concepts

**Liveness Probe:**
- Checks: Is the container alive?
- If fails: Restart the container
- Example: Check `/health` endpoint

**Readiness Probe:**
- Checks: Can the container serve traffic?
- If fails: Remove from service endpoints (don't restart)
- Example: Check `/ready` endpoint

**Why This Matters:**
- Service only routes to pods with `Ready = True`
- Readiness probe must succeed for pod to be marked Ready
- Wrong endpoint → probe fails → pod never ready → no traffic

## Common Pitfalls

- ❌ Probe checks endpoint that doesn't exist (404 errors)
- ❌ Probe checks wrong endpoint (wrong semantics)
- ❌ Using liveness endpoint for readiness probe
- ❌ Missing probe configuration

## Next Challenge

Ready for more? Try **[Scenario 8: Network Policy](../08-network-policy/)**!

---

**Questions or Issues?** Open an issue on [GitHub](https://github.com/vellankikoti/k8s-masterclass/issues)
