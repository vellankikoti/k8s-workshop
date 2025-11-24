# Scenario 1: CrashLoopBackOff

**Difficulty:** Beginner
**Estimated Time:** 15 minutes
**Image:** `vellankikoti/k8s-masterclass-crashloop:v1.0`

## Learning Objectives

- Understand the CrashLoopBackOff pod state
- Learn how to read container logs for debugging
- Identify missing environment variable errors
- Use `kubectl describe` to investigate pod failures
- Fix configuration issues in deployments

## The Challenge

Your team just deployed a new application to the Kubernetes cluster. Minutes later, the monitoring system alerts that the pods are not running. When you check the cluster, you see the pods are in a `CrashLoopBackOff` state with increasing restart counts.

**Your mission:** Find out why the application keeps crashing and fix it!

## Step 1: Deploy the Broken Application

```bash
cd scenarios/01-crashloop-backoff
kubectl apply -f broken/
```

**Expected output:**
```
deployment.apps/crashloop-app created
```

## Step 2: Observe the Failure

Wait about 30 seconds, then check the pod status:

```bash
kubectl get pods
```

**What you should see:**
```
NAME                             READY   STATUS             RESTARTS   AGE
crashloop-app-xxxxxxxxxx-xxxxx   0/1     CrashLoopBackOff   3          1m
```

Notice:
- `STATUS` shows `CrashLoopBackOff` or `Error`
- `RESTARTS` count keeps increasing
- Pod is never `READY` (0/1)

## Step 3: Investigate

Let's gather information about what's happening:

### View Pod Details
```bash
kubectl describe pod -l app=crashloop-app
```

Look for:
- **State** section showing `Waiting` or `Terminated`
- **Last State** showing exit code (usually 1)
- **Events** showing repeated container restarts

### Check Application Logs
```bash
kubectl logs -l app=crashloop-app
```

**Key Questions:**
- What error message does the application print?
- What is the application looking for?
- Why is the container exiting?

## Step 4: Troubleshoot

<details>
<summary>💡 Hint 1 - Where to look</summary>

The error message in the logs is your biggest clue. Read what the application is complaining about.

</details>

<details>
<summary>💡 Hint 2 - What's missing</summary>

The application is checking for an environment variable called `REQUIRED_CONFIG`. Is it set in the deployment?

</details>

<details>
<summary>💡 Hint 3 - How to fix</summary>

You need to add an `env` section to the container spec in the deployment YAML.

</details>

<details>
<summary>✅ Solution</summary>

### The Problem

The application requires an environment variable `REQUIRED_CONFIG` to start, but it's not defined in the deployment. When the application doesn't find this variable, it exits with code 1, causing Kubernetes to restart it repeatedly.

### The Fix

```bash
kubectl apply -f solution/
```

**What changed:**

```yaml
spec:
  containers:
  - name: app
    image: vellankikoti/k8s-masterclass-crashloop:v1.0
    # Added environment variable
    env:
    - name: REQUIRED_CONFIG
      value: "production"
```

### Why This Works

1. The application code checks for `REQUIRED_CONFIG` environment variable
2. If missing, it prints an error and exits with code 1
3. Kubernetes sees the exit code and restarts the container
4. After several failures, Kubernetes backs off (CrashLoopBackOff)
5. By providing the environment variable, the app starts successfully

**Key Kubernetes Concept:** Pods restart when containers exit with non-zero codes. The `CrashLoopBackOff` state indicates Kubernetes is backing off on restart attempts after repeated failures.

</details>

## Step 5: Verify the Fix

Check that the pod is now running:

```bash
kubectl get pods
```

**Expected output:**
```
NAME                             READY   STATUS    RESTARTS   AGE
crashloop-app-xxxxxxxxxx-xxxxx   1/1     Running   0          30s
```

View the application logs to confirm it's working:

```bash
kubectl logs -l app=crashloop-app
```

**Expected output:**
```
[2025-11-24 ...] Starting application...
[2025-11-24 ...] Configuration loaded: production
[2025-11-24 ...] Application started successfully!
[2025-11-24 ...] Application is running... (heartbeat #1)
```

## Step 6: Cleanup

```bash
kubectl delete -f solution/
```

## What You Learned

✅ How to identify CrashLoopBackOff pod state
✅ Using `kubectl logs` to read application error messages
✅ Using `kubectl describe pod` to see restart history and exit codes
✅ Understanding that pods restart when containers exit with errors
✅ How to add environment variables to Kubernetes deployments
✅ Best practices: Applications should fail fast with clear error messages

## Common Pitfalls

- **Ignoring logs**: Always check logs first - they usually contain the exact error
- **Not checking all pods**: Use `-l app=name` to see logs from any pod with that label
- **Assuming the image is bad**: Often it's configuration, not the container image itself

## Going Deeper

**Kubernetes Documentation:**
- [Pod Lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)
- [Container Restart Policy](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#restart-policy)

**Related Concepts:**
- Environment variables can also come from ConfigMaps and Secrets
- `restartPolicy` can be set to `Always` (default), `OnFailure`, or `Never`
- Exit codes: 0 = success, non-zero = failure

**Try This:**
- Change the environment variable value and see the pod update
- Set `restartPolicy: Never` and see what happens
- Use a ConfigMap instead of inline environment variables

## Next Challenge

Ready for more? Try **[Scenario 2: ImagePullBackOff](../02-image-pull-backoff/)** to learn about container registry issues!

---

**Questions or Issues?** Open an issue on [GitHub](https://github.com/vellankikoti/k8s-masterclass/issues)
