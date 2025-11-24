# Scenario 7: Probe Failure

**Difficulty:** Intermediate
**Estimated Time:** 20 minutes
**Image:** `vellankikoti/k8s-masterclass-health-app:v1.0`

## Learning Objectives

- Understand Kubernetes health probes (liveness, readiness, startup)
- Learn the difference between liveness and readiness probes
- Identify probe configuration issues
- Debug probe failures using `kubectl describe`
- Understand how probes affect pod status and traffic routing

## The Challenge

Your team deployed an API service with health probes configured. The pods are running, but they show `0/1 Ready` and are not receiving traffic from the service. The application is actually healthy, but Kubernetes thinks it's not ready.

**Your mission:** Find out why the readiness probe is failing and fix the probe configuration!

## Step 1: Deploy the Broken Application

```bash
cd scenarios/07-probe-failure
kubectl apply -f broken/
```

**Expected output:**
```
deployment.apps/api-service created
service/api-service created
```

## Step 2: Observe the Failure

Wait about 30-40 seconds, then check the pod status:

```bash
kubectl get pods -l app=api-service
```

**What you should see:**
```
NAME                           READY   STATUS    RESTARTS   AGE
api-service-xxxxxxxxxx-xxxxx   0/1     Running   0          1m
api-service-xxxxxxxxxx-xxxxx   0/1     Running   0          1m
```

Notice:
- `READY` shows `0/1` (pod is not ready)
- `STATUS` shows `Running` (container is running)
- Pods are not receiving traffic from the service

### Check Service Endpoints
```bash
kubectl get endpoints api-service
```

**What you should see:**
```
NAME           ENDPOINTS   AGE
api-service    <none>      1m
```

❌ No endpoints! The service can't route traffic because pods aren't ready.

## Step 3: Investigate

### View Pod Details
```bash
kubectl describe pod -l app=api-service
```

Look for the **Readiness** section:

```
Readiness:      http-get http://:5000/health delay=5s timeout=1s period=5s #success=1 #failure=3
  Warning  Unhealthy  30s (x6 over 1m)  kubelet  Readiness probe failed: HTTP probe failed with statuscode: 404
```

Also check **Conditions**:

```
Conditions:
  Type              Status
  PodScheduled      True
  Initialized       True
  ContainersReady   False  ❌
  Ready             False  ❌
```

### Check What Endpoint the Probe is Using
```bash
kubectl get deployment api-service -o yaml | grep -A 10 readinessProbe
```

**What you should see:**
```yaml
readinessProbe:
  httpGet:
    path: /health  # This might be wrong!
    port: 5000
```

### Test the Application Directly
```bash
# Port-forward to test
kubectl port-forward -l app=api-service 8080:5000 &

# Test the /health endpoint
curl http://localhost:8080/health
```

**Expected output:**
```json
{"status": "healthy"}
```

✅ The `/health` endpoint works!

```bash
# Test the /ready endpoint
curl http://localhost:8080/ready
```

**Expected output:**
```json
{"status": "ready", "message": "Service is ready to accept traffic"}
```

✅ The `/ready` endpoint also works!

**Key Questions:**
- What endpoint is the readiness probe checking?
- Does that endpoint exist and return 200?
- What's the difference between `/health` and `/ready`?

## Step 4: Troubleshoot

<details>
<summary>💡 Hint 1 - Check the probe path</summary>

The readiness probe is checking `/health`, but should it be checking a different endpoint? What endpoint indicates the service is ready to accept traffic?

</details>

<details>
<summary>💡 Hint 2 - Understand probe types</summary>

- **Liveness probe**: Is the container alive? (restarts if fails)
- **Readiness probe**: Is the container ready to serve traffic? (removes from service if fails)

The readiness probe should check if the service is ready to accept requests.

</details>

<details>
<summary>💡 Hint 3 - Check the correct endpoint</summary>

The application has both `/health` and `/ready` endpoints. The readiness probe should check `/ready`, not `/health`. The liveness probe can check `/health`.

</details>

<details>
<summary>✅ Solution</summary>

### The Problem

The readiness probe is configured to check the `/health` endpoint, but it should be checking the `/ready` endpoint. While `/health` indicates the container is alive, `/ready` indicates the service is ready to accept traffic. This is a common pattern where:
- `/health` = basic health check (for liveness)
- `/ready` = readiness check (dependencies ready, can accept traffic)

**Key Issue:**
- Readiness probe checks: `/health` ❌
- Should check: `/ready` ✅
- Result: Probe fails (404 or wrong response), pod marked as not ready, no traffic routed

### The Fix

```bash
kubectl apply -f solution/
```

**What changed:**

```yaml
readinessProbe:
  httpGet:
    path: /ready  # Changed from /health to /ready
    port: 5000
  initialDelaySeconds: 5
  periodSeconds: 5
  failureThreshold: 3
livenessProbe:
  httpGet:
    path: /health  # Liveness can check /health
    port: 5000
  initialDelaySeconds: 15
  periodSeconds: 10
  failureThreshold: 3
```

### Why This Works

1. **Probe Types**:
   - **Liveness Probe**: Checks if container is alive. If fails → restart container
   - **Readiness Probe**: Checks if container is ready for traffic. If fails → remove from service endpoints

2. **Endpoint Semantics**:
   - `/health`: Basic health check (is the process running?)
   - `/ready`: Readiness check (are dependencies ready? can we accept traffic?)

3. **Traffic Routing**: 
   - Service only routes to pods with `Ready` condition = True
   - Readiness probe must succeed for pod to be marked Ready
   - If readiness probe fails → pod removed from service endpoints

4. **Best Practice**: Use separate endpoints for liveness and readiness to allow fine-grained control

**Key Kubernetes Concept:** Readiness probes determine if a pod can receive traffic. If the probe fails, the pod is removed from service endpoints but not restarted. Liveness probes determine if a pod should be restarted.

</details>

## Step 5: Verify the Fix

Check that pods are now ready:

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

Check service endpoints:

```bash
kubectl get endpoints api-service
```

**Expected output:**
```
NAME           ENDPOINTS                                    AGE
api-service    10.244.0.5:5000,10.244.0.6:5000             1m
```

✅ Endpoints are now populated!

Test service connectivity:

```bash
kubectl run curl-test --image=curlimages/curl:latest --rm -it --restart=Never -- \
  curl http://api-service
```

You should get a successful response from the API service!

## Step 6: Cleanup

```bash
kubectl delete -f solution/
```

## What You Learned

✅ Understanding liveness vs readiness probes
✅ How probes affect pod status and service endpoints
✅ Using `kubectl describe` to debug probe failures
✅ Understanding probe configuration (path, port, timing)
✅ Best practice: Use separate endpoints for liveness and readiness
✅ How readiness probes control traffic routing

## Common Pitfalls

- **Wrong endpoint**: Probe checks endpoint that doesn't exist or returns wrong status
- **Wrong probe type**: Using liveness probe for readiness or vice versa
- **Too aggressive timing**: Probe fails during startup before app is ready
- **No initial delay**: Probe starts before application is up
- **Wrong port**: Probe checks wrong port number
- **Missing probe**: No readiness probe means pod is immediately ready (might not be)

## Going Deeper

**Kubernetes Documentation:**
- [Configure Liveness, Readiness and Startup Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [Pod Lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)

**Related Concepts:**
- **Startup Probe**: For slow-starting containers (disables liveness/readiness until it succeeds)
- **Probe Types**: httpGet, tcpSocket, exec
- **Timing Parameters**: initialDelaySeconds, periodSeconds, timeoutSeconds, successThreshold, failureThreshold
- **Probe Behavior**: Liveness → restart, Readiness → remove from endpoints

**Try This:**
```bash
# View probe configuration
kubectl get deployment api-service -o yaml | grep -A 15 "livenessProbe\|readinessProbe"

# Test probe endpoints manually
kubectl port-forward -l app=api-service 8080:5000
curl http://localhost:8080/health
curl http://localhost:8080/ready

# Watch pod status change as probes succeed/fail
watch kubectl get pods -l app=api-service

# Check probe events
kubectl describe pod -l app=api-service | grep -A 10 "Readiness\|Liveness"
```

**Probe Configuration Best Practices:**
- **Liveness**: Should check if the main process is alive (not dependencies)
- **Readiness**: Should check if service can accept traffic (including dependencies)
- **Initial Delay**: Give app time to start before first probe
- **Period**: Balance between responsiveness and load
- **Failure Threshold**: Allow some failures before taking action

## Next Challenge

Ready for advanced scenarios? Try **[Scenario 8: Network Policy](../08-network-policy/)** to learn about pod-to-pod networking!

---

**Questions or Issues?** Open an issue on [GitHub](https://github.com/vellankikoti/k8s-masterclass/issues)

