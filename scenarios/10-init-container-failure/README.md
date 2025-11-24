# Scenario 10: Init Container Failure

**Difficulty:** Advanced
**Estimated Time:** 25 minutes
**Image:** `vellankikoti/k8s-masterclass-init-app:v1.0`

## Learning Objectives

- Understand init containers and their purpose
- Learn about pod initialization phases
- Identify init container failure states
- Debug init container issues using `kubectl logs` and `kubectl describe`
- Understand the relationship between init containers and main containers

## The Challenge

Your team deployed a todo application that requires a Redis database. The deployment includes an init container that waits for Redis to be ready before starting the main application. However, the pod is stuck and won't start - it's either in `Init:Error` or `Init:CrashLoopBackOff` state.

**Your mission:** Find out why the init container is failing and fix the initialization logic!

## Step 1: Deploy the Broken Application

```bash
cd scenarios/10-init-container-failure
kubectl apply -f broken/
```

**Expected output:**
```
deployment.apps/todo-app created
service/todo-service created
```

## Step 2: Observe the Failure

Wait about 20-30 seconds, then check the pod status:

```bash
kubectl get pods -l app=todo
```

**What you should see:**
```
NAME                        READY   STATUS                 RESTARTS   AGE
todo-app-xxxxxxxxxx-xxxxx   0/1     Init:Error              0          1m
```

Or it might show:
```
NAME                        READY   STATUS                     RESTARTS   AGE
todo-app-xxxxxxxxxx-xxxxx   0/1     Init:CrashLoopBackOff       3          2m
```

Notice:
- `STATUS` shows `Init:Error` or `Init:CrashLoopBackOff` ❌
- `READY` is 0/1 (pod is not ready)
- Main container never started (stuck in init phase)

## Step 3: Investigate

### View Pod Details
```bash
kubectl describe pod -l app=todo
```

Look for the **Init Containers** section:

```
Init Containers:
  wait-for-redis:
    Container ID:  docker://abc123...
    Image:         busybox:1.36
    State:         Waiting
      Reason:      CrashLoopBackOff
    Last State:    Terminated
      Reason:      Error
      Exit Code:    1
```

Also check **Events**:

```
Events:
  Type     Reason     Age                From               Message
  ----     ------     ----               ----               -------
  Normal   Scheduled  1m                 default-scheduler  Successfully assigned default/todo-app-xxx to node
  Normal   Pulled     1m                 kubelet            Container image "busybox:1.36" already present
  Normal   Created    1m                 kubelet            Created container wait-for-redis
  Normal   Started    1m                 kubelet            Started container wait-for-redis
  Warning  Failed     30s (x3 over 1m)   kubelet            Error: failed to start container "wait-for-redis": Error response from daemon
```

### Check Init Container Logs
```bash
kubectl logs -l app=todo -c wait-for-redis
```

**What you should see:**
```
Waiting for Redis to be ready...
Redis not available yet...
nc: can't resolve 'redis-nonexistent'
```

❌ The init container is trying to connect to `redis-nonexistent`, which doesn't exist!

### Check the Deployment Configuration
```bash
kubectl get deployment todo-app -o yaml | grep -A 20 initContainers
```

**What you should see:**
```yaml
initContainers:
- name: wait-for-redis
  image: busybox:1.36
  command:
  - sh
  - -c
  - |
    until nc -z redis-nonexistent 6379; do  # ❌ Wrong hostname!
      echo "Redis not available yet..."
      sleep 2
    done
```

### Check if Redis Exists
```bash
kubectl get pods -l app=redis
kubectl get svc redis-service
```

**Expected output:**
```
No resources found in default namespace.
```

❌ Redis doesn't exist! The init container is trying to connect to a non-existent service.

**Key Questions:**
- What is the init container trying to connect to?
- Does that service/host exist?
- What error appears in the init container logs?
- Why can't the init container complete successfully?

## Step 4: Troubleshoot

<details>
<summary>💡 Hint 1 - Read the init container logs</summary>

The init container logs show it's trying to connect to `redis-nonexistent`. Does this service exist in the cluster?

</details>

<details>
<summary>💡 Hint 2 - Check the hostname</summary>

The init container command uses `redis-nonexistent` as the hostname. What should the correct Redis service name be? Check the main container's environment variables for a hint.

</details>

<details>
<summary>💡 Hint 3 - Fix the connection target</summary>

The init container should connect to the actual Redis service. The main container uses `REDIS_HOST=redis-service`, so the init container should also use `redis-service` instead of `redis-nonexistent`. Also, make sure Redis is deployed first!

</details>

<details>
<summary>✅ Solution</summary>

### The Problem

The init container is trying to connect to `redis-nonexistent`, which doesn't exist in the cluster. Additionally, Redis itself is not deployed. The init container keeps failing because:
1. The hostname `redis-nonexistent` cannot be resolved
2. Even if the hostname was correct, Redis service doesn't exist

**Key Issue:**
- Init container connects to: `redis-nonexistent` ❌ (doesn't exist)
- Should connect to: `redis-service` ✅
- Redis deployment: Not created ❌
- Result: Init container fails → Pod stuck in Init phase → Main container never starts

**Init Container Behavior:**
- Init containers must complete successfully before main containers start
- If init container fails → Pod stays in Init phase
- Init containers can restart (like main containers) → Can show CrashLoopBackOff

### The Fix

```bash
kubectl apply -f solution/
```

**What changed:**

The solution includes:
1. **Redis deployment** (was missing)
2. **Redis service** (was missing)
3. **Fixed init container** (correct hostname)

```yaml
# Redis deployment (NEW)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
---
# Redis service (NEW)
apiVersion: v1
kind: Service
metadata:
  name: redis-service
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
---
# Todo app with fixed init container
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-app
spec:
  ...
  template:
    spec:
      initContainers:
      - name: wait-for-redis
        image: busybox:1.36
        command:
        - sh
        - -c
        - |
          echo "Waiting for Redis to be ready..."
          # FIXED: Using correct Redis service name
          until nc -z redis-service 6379; do
            echo "Redis not available yet..."
            sleep 2
          done
          echo "✅ Redis is ready!"
```

### Why This Works

1. **Init Containers**:
   - Run before main containers start
   - Must all complete successfully (exit code 0)
   - Run sequentially (one after another)
   - If any fails → Pod stays in Init phase

2. **Use Cases**:
   - Wait for dependencies (databases, services)
   - Download/configure files
   - Set up permissions
   - Run database migrations

3. **Service Discovery**:
   - Init containers can use Kubernetes DNS
   - `redis-service` resolves to the Redis service IP
   - Must wait for service to be ready

4. **Execution Order**:
   - Init containers run → All succeed → Main containers start
   - If init fails → Main containers never start

**Key Kubernetes Concept:** Init containers are perfect for dependency checks and setup tasks. They must complete successfully before main containers start. Use them to ensure dependencies are ready.

</details>

## Step 5: Verify the Fix

Check that Redis is running:

```bash
kubectl get pods -l app=redis
```

**Expected output:**
```
NAME                     READY   STATUS    RESTARTS   AGE
redis-xxxxxxxxxx-xxxxx   1/1     Running   0          1m
```

✅ Redis is running!

Check the todo app pod:

```bash
kubectl get pods -l app=todo
```

**Expected output:**
```
NAME                        READY   STATUS    RESTARTS   AGE
todo-app-xxxxxxxxxx-xxxxx   1/1     Running   0          1m
```

✅ Pod is now running! The init container completed successfully!

Check init container logs:

```bash
kubectl logs -l app=todo -c wait-for-redis
```

**Expected output:**
```
Waiting for Redis to be ready...
Redis not available yet...
Redis not available yet...
✅ Redis is ready!
```

✅ Init container completed successfully!

Test the todo application:

```bash
kubectl port-forward -l app=todo 8080:5000
```

Access http://localhost:8080 - you should see the todo application working with Redis!

## Step 6: Cleanup

```bash
kubectl delete -f solution/
```

## What You Learned

✅ Understanding init containers and their execution model
✅ Identifying init container failure states (Init:Error, Init:CrashLoopBackOff)
✅ Using `kubectl logs -c <container-name>` to view init container logs
✅ Understanding that init containers must succeed before main containers start
✅ Using init containers to wait for dependencies
✅ Best practice: Use init containers for dependency checks and setup tasks

## Common Pitfalls

- **Wrong hostname/service name**: Init container connects to non-existent service
- **Dependency not deployed**: Waiting for service that doesn't exist
- **Infinite loop**: Init container never succeeds (wrong condition)
- **Timeout issues**: Dependency takes too long to be ready
- **Wrong port**: Connecting to wrong port number
- **DNS not ready**: Service exists but DNS not propagated yet

## Going Deeper

**Kubernetes Documentation:**
- [Init Containers](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/)
- [Pod Lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)

**Related Concepts:**
- **Init Container Order**: Run sequentially, all must succeed
- **Resource Limits**: Init containers can have their own resource limits
- **Image Pulling**: Init containers are pulled before main containers
- **Restart Policy**: Init containers can restart (like main containers)
- **Debugging**: Use `kubectl logs -c <init-container-name>` to debug

**Try This:**
```bash
# View init container status
kubectl describe pod -l app=todo | grep -A 10 "Init Containers"

# View init container logs
kubectl logs <pod-name> -c wait-for-redis

# View all container logs
kubectl logs <pod-name> --all-containers=true

# Check init container exit codes
kubectl get pod <pod-name> -o jsonpath='{.status.initContainerStatuses[*].state}'

# Create an init container that downloads files
# Create an init container that runs database migrations
# Create multiple init containers (they run sequentially)
```

**Init Container Patterns:**
```yaml
# Wait for service
initContainers:
- name: wait-for-db
  image: busybox
  command: ['sh', '-c', 'until nc -z db-service 5432; do sleep 2; done']

# Download configuration
initContainers:
- name: download-config
  image: curlimages/curl
  command: ['sh', '-c', 'curl -o /config/app.conf https://config-server/config']

# Run migrations
initContainers:
- name: migrate-db
  image: myapp:migrate
  command: ['python', 'manage.py', 'migrate']
```

## Next Steps

🎉 **Congratulations!** You've completed all 10 Kubernetes troubleshooting scenarios!

**What's Next?**
- Review scenarios you found challenging
- Try combining scenarios (deploy multiple broken apps)
- Experiment with different failure modes
- Share your learnings with your team
- Contribute new scenarios to the workshop!

**Keep Learning:**
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- Practice on real clusters
- Join Kubernetes community forums

---

**Questions or Issues?** Open an issue on [GitHub](https://github.com/vellankikoti/k8s-masterclass/issues)

**Thank you for completing the Kubernetes Masterclass!** 🚀

