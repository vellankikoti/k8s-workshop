# Scenario 4: Missing ConfigMap

**Difficulty:** Intermediate
**Estimated Time:** 20 minutes
**Image:** `vellankikoti/k8s-masterclass-config-app:v1.0`

## Learning Objectives

- Understand ConfigMap resources and their lifecycle
- Learn how pods depend on ConfigMaps
- Identify `CreateContainerConfigError` pod state
- Use `kubectl describe` to debug ConfigMap issues
- Understand resource dependencies in Kubernetes

## The Challenge

Your team deployed a blog application that requires configuration from a ConfigMap. The deployment was applied successfully, but the pods are stuck and won't start. When you check the pod status, you see `CreateContainerConfigError`.

**Your mission:** Find out why the pod can't start and fix the configuration dependency!

## Step 1: Deploy the Broken Application

```bash
cd scenarios/04-missing-configmap
kubectl apply -f broken/
```

**Expected output:**
```
deployment.apps/blog-app created
```

## Step 2: Observe the Failure

Wait about 10-15 seconds, then check the pod status:

```bash
kubectl get pods
```

**What you should see:**
```
NAME                        READY   STATUS                       RESTARTS   AGE
blog-app-xxxxxxxxxx-xxxxx   0/1     CreateContainerConfigError    0          30s
```

Notice:
- `STATUS` shows `CreateContainerConfigError`
- `READY` is 0/1 (pod is not ready)
- `RESTARTS` is 0 (container never started)

## Step 3: Investigate

### View Pod Details
```bash
kubectl describe pod -l app=blog-app
```

Look for the **Events** section at the bottom:

```
Events:
  Type     Reason                   Age                From               Message
  ----     ------                   ----               ----               -------
  Warning  FailedCreatePodSandbox  30s (x3 over 1m)  kubelet            Error: configmap "blog-config" not found
```

Also check the **Conditions** section:
```
Conditions:
  Type              Status
  PodScheduled      True
  Initialized       True
  ContainersReady   False
  Ready             False
```

### Check What ConfigMap the Pod Needs
```bash
kubectl get deployment blog-app -o yaml | grep -A 5 configMap
```

**Key Questions:**
- What ConfigMap name is the pod looking for?
- Does that ConfigMap exist in the cluster?
- What error message appears in the pod events?

### Verify ConfigMap Existence
```bash
kubectl get configmap blog-config
```

**Expected output:**
```
Error from server (NotFound): configmaps "blog-config" not found
```

## Step 4: Troubleshoot

<details>
<summary>💡 Hint 1 - Read the error message</summary>

The error message says "configmap 'blog-config' not found". What does this tell you about what's missing?

</details>

<details>
<summary>💡 Hint 2 - Check the deployment spec</summary>

Look at the deployment YAML. The pod references a ConfigMap in the `volumes` section. Does that ConfigMap exist?

</details>

<details>
<summary>💡 Hint 3 - Create the missing resource</summary>

You need to create the ConfigMap that the deployment is expecting. Check the `solution/` directory for the ConfigMap definition.

</details>

<details>
<summary>✅ Solution</summary>

### The Problem

The deployment references a ConfigMap named `blog-config` in its volume configuration, but this ConfigMap was never created. Kubernetes cannot start the pod because it cannot mount the volume that depends on the non-existent ConfigMap.

**Key Issue:**
- Deployment references: `configMap.name: blog-config`
- ConfigMap `blog-config` does not exist in the cluster
- Pod cannot start without the required ConfigMap

### The Fix

```bash
kubectl apply -f solution/
```

**What changed:**

The solution includes both the ConfigMap and the deployment:

```yaml
# ConfigMap created first
apiVersion: v1
kind: ConfigMap
metadata:
  name: blog-config
data:
  blog.json: |
    {
      "blog_name": "Kubernetes Learning Blog",
      "tagline": "Master K8s troubleshooting, one scenario at a time",
      "author": "K8s Workshop Team",
      "theme": "tech-purple",
      "max_posts_per_page": 15,
      "comments_enabled": true
    }
---
# Deployment (same as before, but now ConfigMap exists)
apiVersion: apps/v1
kind: Deployment
...
  volumes:
  - name: config
    configMap:
      name: blog-config  # Now this exists!
```

### Why This Works

1. **Resource Dependencies**: Kubernetes pods can depend on other resources (ConfigMaps, Secrets, PVCs)
2. **CreateContainerConfigError**: This error occurs when a pod references a ConfigMap or Secret that doesn't exist
3. **Order Matters**: While `kubectl apply` can create resources in any order, the pod won't start until all dependencies exist
4. **ConfigMap Mount**: Once the ConfigMap exists, Kubernetes can mount it as a volume, and the pod can start

**Key Kubernetes Concept:** Pods wait for all required resources (ConfigMaps, Secrets, PVCs) to exist before starting containers. Always create dependencies before or alongside deployments.

</details>

## Step 5: Verify the Fix

Check that the pod is now running:

```bash
kubectl get pods
```

**Expected output:**
```
NAME                        READY   STATUS    RESTARTS   AGE
blog-app-xxxxxxxxxx-xxxxx   1/1     Running   0          30s
```

Verify the ConfigMap is mounted:

```bash
kubectl exec -it deployment/blog-app -- ls -la /config
```

You should see:
```
total 8
drwxr-xr-x    3 root     root          4096 Nov 24 12:00 .
drwxr-xr-x    1 root     root          4096 Nov 24 12:00 ..
drwxr-xr-x    2 root     root          4096 Nov 24 12:00 ..2023_11_24_12_00_00.1234567890
lrwxrwxrwx    1 root     root          31 Nov 24 12:00 blog.json -> ..data/blog.json
```

Access the blog application:

```bash
kubectl port-forward -l app=blog-app 8080:5000
```

In another terminal or browser:
```bash
curl http://localhost:8080
# OR open http://localhost:8080 in your browser
```

You should see the blog application running with the configuration loaded!

## Step 6: Cleanup

```bash
kubectl delete -f solution/
```

## What You Learned

✅ Understanding `CreateContainerConfigError` pod state
✅ How ConfigMaps are used as volumes in pods
✅ Identifying missing resource dependencies
✅ Using `kubectl describe` to find ConfigMap errors
✅ Understanding that pods wait for dependencies before starting
✅ Best practice: Create ConfigMaps before or with deployments

## Common Pitfalls

- **Missing ConfigMap**: Most common - always create ConfigMaps before referencing them
- **Wrong ConfigMap name**: Typo in the name causes the same error
- **Wrong namespace**: ConfigMap must be in the same namespace as the pod
- **ConfigMap not ready**: Even if created, wait a moment for it to be available

## Going Deeper

**Kubernetes Documentation:**
- [ConfigMaps](https://kubernetes.io/docs/concepts/configuration/configmap/)
- [Configure a Pod to Use a ConfigMap](https://kubernetes.io/docs/tasks/configure-pod-container/configure-pod-configmap/)
- [Pod Lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)

**Related Concepts:**
- ConfigMaps can be mounted as volumes or used as environment variables
- Secrets work similarly but for sensitive data
- ConfigMaps can be updated, and pods can watch for changes
- Use `kubectl create configmap` to create from files or literals

**Try This:**
```bash
# Create ConfigMap from a file
kubectl create configmap my-config --from-file=config.json

# Create ConfigMap from literal values
kubectl create configmap my-config --from-literal=key1=value1 --from-literal=key2=value2

# View ConfigMap data
kubectl get configmap blog-config -o yaml

# Update ConfigMap and see if pod picks up changes (depends on how it's mounted)
kubectl edit configmap blog-config
```

## Next Challenge

Ready for more? Try **[Scenario 5: RBAC Forbidden](../05-rbac-forbidden/)** to learn about Kubernetes permissions!

---

**Questions or Issues?** Open an issue on [GitHub](https://github.com/vellankikoti/k8s-masterclass/issues)

