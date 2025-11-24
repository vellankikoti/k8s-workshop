# Scenario 3: Service Port Mismatch

**Difficulty:** Beginner
**Estimated Time:** 20 minutes
**Image:** `vellankikoti/k8s-masterclass-webapp:v1.0`

## Learning Objectives

- Understand Kubernetes Service port mapping
- Learn the difference between `port`, `targetPort`, and `containerPort`
- Debug service connectivity issues
- Use `kubectl port-forward` and `kubectl exec` for testing
- Identify port misconfiguration in service definitions

## The Challenge

The development team deployed a web application with a Service to expose it within the cluster. The pods are running perfectly, but when other applications try to connect to the service, they get connection refused errors or timeouts.

**Your mission:** Find out why the Service can't route traffic to the pods and fix the configuration!

## Step 1: Deploy the Broken Application

```bash
cd scenarios/03-port-mismatch
kubectl apply -f broken/
```

**Expected output:**
```
deployment.apps/webapp created
service/webapp-service created
```

## Step 2: Observe the Failure

Check that pods are running:

```bash
kubectl get pods -l app=webapp
```

**Expected output:**
```
NAME                      READY   STATUS    RESTARTS   AGE
webapp-xxxxxxxxxx-xxxxx   1/1     Running   0          30s
webapp-xxxxxxxxxx-xxxxx   1/1     Running   0          30s
```

✅ Pods are running fine!

Check the service:

```bash
kubectl get svc webapp-service
```

**Expected output:**
```
NAME             TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE
webapp-service   ClusterIP   10.96.xxx.xxx   <none>        80/TCP    30s
```

✅ Service exists!

But let's try to access it:

**Option 1: Test from inside cluster (recommended for this step):**
```bash
kubectl run curl-test --image=curlimages/curl:latest --rm -it --restart=Never -- \
  curl -v http://webapp-service
```

**Option 2: Test via port-forward (for localhost access):**
```bash
# Port-forward through service: localhost:8080 → service:80 → pod:8080 (broken!)
kubectl port-forward svc/webapp-service 8080:80
```

In another terminal or browser, try:
```bash
curl http://localhost:8080
# OR open http://localhost:8080 in browser
```

**What you should see:**
- **From cluster test**: Connection refused, timeout, or "Could not connect"
- **From port-forward**: Connection established but no response, or timeout
- **Browser**: Page doesn't load or connection error

**Why it fails:**
The service is trying to forward traffic to port 8080 on the pods, but the container is listening on port 5000. The port-forward connects, but nothing responds because nothing is listening on port 8080.

❌ Service exists but connectivity fails!

## Step 3: Investigate

### Check Service Endpoints
```bash
kubectl get endpoints webapp-service
```

You should see endpoints (pod IPs) listed - this means the service found the pods:
```
NAME             ENDPOINTS                         AGE
webapp-service   10.244.0.5:8080,10.244.0.6:8080   2m
```

### Test Direct Pod Access
Let's verify the pods are actually working by accessing them directly:

```bash
# Get a pod name
POD_NAME=$(kubectl get pods -l app=webapp -o jsonpath='{.items[0].metadata.name}')

# Port-forward directly to the pod
kubectl port-forward $POD_NAME 8080:5000
```

In another terminal:
```bash
curl http://localhost:8080
```

You should see:
```json
{
  "status": "success",
  "message": "Welcome to the Kubernetes Masterclass!",
  ...
}
```

✅ The application works when accessed directly!

### Check the Configuration
```bash
# View the service details
kubectl describe svc webapp-service

# Check what port the container is listening on
kubectl get deployment webapp -o jsonpath='{.spec.template.spec.containers[0].ports[0].containerPort}'
```

**Key Questions:**
- What port is the container listening on?
- What `targetPort` is the service using?
- Do these ports match?

## Step 4: Troubleshoot

<details>
<summary>💡 Hint 1 - Understanding ports</summary>

Three port types in Kubernetes:
- **containerPort**: Port the application listens on inside the container
- **targetPort**: Port the Service forwards traffic to on the pod
- **port**: Port the Service exposes (what clients connect to)

These must be correctly aligned!

</details>

<details>
<summary>💡 Hint 2 - Compare the ports</summary>

Run these commands:
```bash
# What port is the container using?
kubectl get deployment webapp -o yaml | grep containerPort

# What port is the service targeting?
kubectl get svc webapp-service -o yaml | grep targetPort
```

Do they match?

</details>

<details>
<summary>💡 Hint 3 - The mismatch</summary>

- Container is listening on port **5000**
- Service is sending traffic to port **8080**
- This mismatch causes connection failures!

</details>

<details>
<summary>✅ Solution</summary>

### The Problem

**Port Mapping Mismatch:**

| Component | Port | Actual Value |
|-----------|------|--------------|
| Container listens on | `containerPort` | 5000 ✅ |
| Service forwards to | `targetPort` | 8080 ❌ |

The service is trying to send traffic to port 8080 on the pods, but the Flask application is listening on port 5000. This causes all connection attempts to fail.

### The Fix

```bash
kubectl apply -f solution/
```

**What changed:**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: webapp-service
spec:
  selector:
    app: webapp
  ports:
  - name: http
    protocol: TCP
    port: 80            # Service exposes on port 80
    targetPort: 5000    # Changed from 8080 to 5000
```

### Why This Works

**Port Flow:**
```
Client → Service (port 80) → Service routes to targetPort 5000 → Container (listening on 5000) ✅
```

**Understanding Service Ports:**

1. **port**: The port the Service listens on (what clients use)
   - Example: `curl http://webapp-service:80`

2. **targetPort**: The port on the Pod where traffic is sent
   - Must match the container's `containerPort`
   - Can be a number (5000) or name reference ("http")

3. **containerPort**: The port the application binds to
   - Defined in Deployment spec
   - Must match what the application actually listens on

**Alternative Fix (using port names):**
```yaml
# In Deployment
ports:
- containerPort: 5000
  name: http

# In Service
ports:
- port: 80
  targetPort: http  # Reference by name
```

</details>

## Step 5: Verify the Fix

Test the service now works. You can test in multiple ways:

### Method 1: Test from inside cluster (recommended)

```bash
kubectl run curl-test --image=curlimages/curl:latest --rm -it --restart=Never -- \
  curl http://webapp-service
```

**Expected output:**
```json
{
  "status": "success",
  "message": "Welcome to the Kubernetes Masterclass!",
  "scenario": "03 - Port Mismatch",
  "pod_name": "webapp-xxxxxxxxxx-xxxxx"
}
```

✅ Service is working!

### Method 2: Test via port-forward (for localhost access)

**Important:** When port-forwarding to a service, use the **service port (80)**, not the container port (5000):

```bash
# Correct: localhost:8080 → service:80 → pod:5000
kubectl port-forward svc/webapp-service 8080:80
```

**Note:** The format is `kubectl port-forward svc/<service-name> <local-port>:<service-port>`
- `8080` = your local port (you can choose any port)
- `80` = the service port (NOT the container port 5000)

In another terminal or browser:
```bash
curl http://localhost:8080
# OR open http://localhost:8080 in browser
```

**Expected output:**
```json
{
  "status": "success",
  "message": "Welcome to the Kubernetes Masterclass!",
  "scenario": "03 - Port Mismatch",
  "pod_name": "webapp-xxxxxxxxxx-xxxxx"
}
```

✅ Service is working through port-forward!

**Alternative: Port-forward directly to pod (bypasses service)**
```bash
# Direct pod access: localhost:8080 → pod:5000
kubectl port-forward -l app=webapp 8080:5000
```
This works in both broken and fixed states since it bypasses the service.

### Method 3: Test load balancing

Test multiple times to see load balancing across pods:
```bash
for i in {1..5}; do
  kubectl run curl-test-$i --image=curlimages/curl:latest --rm -it --restart=Never -- \
    curl -s http://webapp-service | grep pod_name
done
```

You should see different pod names, showing the service load balances!

## Step 6: Cleanup

```bash
kubectl delete -f solution/
```

## What You Learned

✅ Understanding Kubernetes port types: `port`, `targetPort`, `containerPort`
✅ How Services route traffic to Pods using selectors and targetPort
✅ Debugging service connectivity with `kubectl port-forward`
✅ Using `kubectl describe endpoints` to verify service-pod connection
✅ Testing services from within the cluster using curl pods
✅ Best practice: Use named ports for clarity and flexibility

## Common Pitfalls

- **Port mismatch**: Most common issue - targetPort must match containerPort
- **Selector mismatch**: Service selector must match pod labels
- **Wrong port when port-forwarding to service**: Use service port (80), not container port (5000)
  - ✅ Correct: `kubectl port-forward svc/webapp-service 8080:80`
  - ❌ Wrong: `kubectl port-forward svc/webapp-service 8080:5000`
- **Port-forward to pod vs service**: 
  - Pod: `kubectl port-forward <pod> 8080:5000` (uses container port)
  - Service: `kubectl port-forward svc/<service> 8080:80` (uses service port)
- **Network policies**: Can block traffic even when ports are correct
- **DNS not ready**: Give DNS a few seconds to propagate service names

## Going Deeper

**Kubernetes Documentation:**
- [Services](https://kubernetes.io/docs/concepts/services-networking/service/)
- [Connecting Applications with Services](https://kubernetes.io/docs/tutorials/services/connect-applications-service/)

**Related Concepts:**
- Service types: ClusterIP, NodePort, LoadBalancer, ExternalName
- Headless services (ClusterIP: None)
- Service discovery via DNS
- EndpointSlices

**Try This:**
```bash
# See the actual iptables rules created by the service
kubectl run -it --rm debug --image=nicolaka/netshoot --restart=Never -- iptables -t nat -L | grep webapp

# View service DNS records
kubectl run -it --rm debug --image=nicolaka/netshoot --restart=Never -- nslookup webapp-service

# Check endpoints in detail
kubectl get endpointslices -l kubernetes.io/service-name=webapp-service -o yaml
```

**Advanced Debugging:**
```bash
# Exec into a pod and test
kubectl exec -it deployment/webapp -- sh
# Inside container:
# netstat -tlnp  # See what ports are listening
# wget -O- localhost:5000  # Test the app

# Test from a debug pod in the same namespace
kubectl run -it debug --image=nicolaka/netshoot --rm --restart=Never -- bash
# Inside debug pod:
# curl webapp-service
# dig webapp-service
# nc -zv webapp-service 80
```

## Next Challenge

Ready for intermediate scenarios? Try **[Scenario 4: Missing ConfigMap](../04-missing-configmap/)** to learn about configuration dependencies!

---

**Questions or Issues?** Open an issue on [GitHub](https://github.com/vellankikoti/k8s-masterclass/issues)
