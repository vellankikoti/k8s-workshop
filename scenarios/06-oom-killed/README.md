# Scenario 6: OOMKilled

**Difficulty:** Intermediate
**Estimated Time:** 20 minutes
**Image:** `vellankikoti/k8s-masterclass-memory-hog:v1.0`

## Learning Objectives

- Understand Kubernetes resource limits and requests
- Learn about OOMKilled pod termination
- Identify memory limit issues
- Use `kubectl describe` to see OOMKilled events
- Understand container memory management

## The Challenge

Your team deployed an image processing service that handles batch image processing requests. The pod starts successfully, but when processing more than a few images, the pod gets killed and restarts. The pod status shows `OOMKilled` or the pod keeps restarting.

**Your mission:** Find out why the pod is being killed and fix the resource limits!

## Step 1: Deploy the Broken Application

```bash
cd scenarios/06-oom-killed
kubectl apply -f broken/
```

**Expected output:**
```
deployment.apps/image-processor created
service/image-processor-service created
```

## Step 2: Observe the Failure

Wait about 10-15 seconds, then check the pod status:

```bash
kubectl get pods -l app=image-processor
```

**What you should see:**
```
NAME                              READY   STATUS    RESTARTS   AGE
image-processor-xxxxxxxxxx-xxxxx   1/1     Running   0          30s
```

✅ The pod starts fine! But let's trigger the memory issue:

```bash
# Port-forward to access the service
kubectl port-forward -l app=image-processor 8080:5000 &
```

In another terminal, trigger image processing:

```bash
curl -X POST http://localhost:8080/process \
  -H "Content-Type: application/json" \
  -d '{"count": 15}'
```

Now check the pod status again:

```bash
kubectl get pods -l app=image-processor
```

**What you should see:**
```
NAME                              READY   STATUS      RESTARTS   AGE
image-processor-xxxxxxxxxx-xxxxx   0/1     OOMKilled   1          2m
```

Or it might show:
```
NAME                              READY   STATUS             RESTARTS   AGE
image-processor-xxxxxxxxxx-xxxxx   0/1     CrashLoopBackOff   3          3m
```

❌ The pod was killed due to out-of-memory!

## Step 3: Investigate

### View Pod Details
```bash
kubectl describe pod -l app=image-processor
```

Look for the **Last State** section:

```
Last State:     Terminated
  Reason:       OOMKilled
  Exit Code:    137
  Started:      ...
  Finished:     ...
```

Also check the **Events** section:

```
Events:
  Type     Reason     Age                From               Message
  ----     ------     ----               ----               -------
  Warning  OOMKilled  30s                kubelet            Memory limit exceeded
```

### Check Resource Limits
```bash
kubectl get deployment image-processor -o yaml | grep -A 10 resources
```

**What you should see:**
```yaml
resources:
  requests:
    memory: "64Mi"
    cpu: "100m"
  limits:
    memory: "128Mi"  # This is too low!
    cpu: "500m"
```

### Check Container Memory Usage (if pod is running)
```bash
kubectl top pod -l app=image-processor
```

**Key Questions:**
- What is the memory limit set to?
- What is the actual memory usage?
- What does the OOMKilled reason mean?
- How much memory does the application need?

## Step 4: Troubleshoot

<details>
<summary>💡 Hint 1 - Understand OOMKilled</summary>

OOMKilled means "Out Of Memory Killed". The container exceeded its memory limit and was terminated by the kernel.

</details>

<details>
<summary>💡 Hint 2 - Check the memory limit</summary>

The deployment sets a memory limit. Is it high enough for the application's workload? Processing 15 images might need more than 128Mi.

</details>

<details>
<summary>💡 Hint 3 - Increase the limit</summary>

You need to increase the memory limit in the deployment to allow the application to process more images without being killed.

</details>

<details>
<summary>✅ Solution</summary>

### The Problem

The deployment has a memory limit of `128Mi`, which is too low for the image processing workload. When processing multiple images (each image processing operation uses ~10-15MB), the container's memory usage exceeds the limit, causing the Linux kernel's OOM (Out Of Memory) killer to terminate the container.

**Key Issue:**
- Memory limit: `128Mi` ❌ (too low)
- Application needs: ~200-300Mi for processing 15 images
- Result: Container killed when memory limit exceeded

**Exit Code 137:**
- Exit code 137 = 128 + 9 (SIGKILL)
- Indicates the process was killed by the system (OOM killer)

### The Fix

```bash
kubectl apply -f solution/
```

**What changed:**

```yaml
resources:
  requests:
    memory: "128Mi"  # Increased from 64Mi
    cpu: "100m"
  limits:
    memory: "384Mi"  # Increased from 128Mi to 384Mi
    cpu: "500m"
```

### Why This Works

1. **Resource Limits**: Kubernetes enforces memory limits using cgroups
2. **OOM Killer**: When a container exceeds its memory limit, the Linux kernel's OOM killer terminates it
3. **Memory Requests**: Used for scheduling (ensures node has enough memory)
4. **Memory Limits**: Hard limit - container cannot exceed this
5. **Proper Sizing**: Setting appropriate limits prevents OOMKilled while avoiding resource waste

**Key Kubernetes Concept:** Always set resource requests and limits based on actual application needs. Too low = OOMKilled, too high = resource waste. Monitor and adjust based on real usage.

</details>

## Step 5: Verify the Fix

Check that the pod can now handle the workload:

```bash
kubectl get pods -l app=image-processor
```

**Expected output:**
```
NAME                              READY   STATUS    RESTARTS   AGE
image-processor-xxxxxxxxxx-xxxxx   1/1     Running   0          30s
```

Test processing more images:

```bash
# Port-forward if not already running
kubectl port-forward -l app=image-processor 8080:5000 &

# Process 15 images
curl -X POST http://localhost:8080/process \
  -H "Content-Type: application/json" \
  -d '{"count": 15}'
```

Check the pod status - it should remain running:

```bash
kubectl get pods -l app=image-processor
```

**Expected output:**
```
NAME                              READY   STATUS    RESTARTS   AGE
image-processor-xxxxxxxxxx-xxxxx   1/1     Running   0          2m
```

✅ No more OOMKilled!

Monitor memory usage:

```bash
kubectl top pod -l app=image-processor
```

You should see memory usage below the limit.

## Step 6: Cleanup

```bash
kubectl delete -f solution/
```

## What You Learned

✅ Understanding OOMKilled pod termination
✅ How Kubernetes enforces memory limits using cgroups
✅ Using `kubectl describe` to see OOMKilled events
✅ Understanding resource requests vs limits
✅ Setting appropriate memory limits for applications
✅ Exit code 137 meaning (128 + SIGKILL)
✅ Best practice: Set limits based on actual workload requirements

## Common Pitfalls

- **Too low limits**: Causes OOMKilled under normal load
- **Too high limits**: Wastes resources and can prevent scheduling
- **No limits**: Container can consume all node memory
- **Only setting limits**: Should also set requests for proper scheduling
- **Not monitoring**: Don't know actual usage to set proper limits

## Going Deeper

**Kubernetes Documentation:**
- [Resource Management for Pods and Containers](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [Assign Memory Resources to Containers and Pods](https://kubernetes.io/docs/tasks/configure-pod-container/assign-memory-resource/)
- [Configure Quality of Service for Pods](https://kubernetes.io/docs/tasks/configure-pod-container/quality-service-pod/)

**Related Concepts:**
- **Requests**: Minimum resources guaranteed (used for scheduling)
- **Limits**: Maximum resources allowed (enforced by kernel)
- **QoS Classes**: Guaranteed, Burstable, BestEffort (based on requests/limits)
- **cgroups**: Linux kernel feature that enforces limits
- **OOM Score**: How likely a process is to be killed when memory is low

**Try This:**
```bash
# Check current resource usage
kubectl top pod -l app=image-processor

# View resource requests and limits
kubectl describe pod -l app=image-processor | grep -A 5 "Limits\|Requests"

# Check QoS class
kubectl get pod -l app=image-processor -o jsonpath='{.items[0].status.qosClass}'

# Set CPU limits and see how it affects performance
# (CPU throttling vs OOMKilled for memory)
```

**Monitoring Memory:**
```bash
# Watch pod memory usage
watch kubectl top pod -l app=image-processor

# Get detailed resource metrics
kubectl get --raw /apis/metrics.k8s.io/v1beta1/namespaces/default/pods/<pod-name>
```

## Next Challenge

Ready for more? Try **[Scenario 7: Probe Failure](../07-probe-failure/)** to learn about health checks and probes!

---

**Questions or Issues?** Open an issue on [GitHub](https://github.com/vellankikoti/k8s-masterclass/issues)

