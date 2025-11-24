# Scenario 5: RBAC Forbidden

**Difficulty:** Intermediate
**Estimated Time:** 25 minutes
**Image:** `vellankikoti/k8s-masterclass-rbac-app:v1.0`

## Learning Objectives

- Understand Kubernetes RBAC (Role-Based Access Control)
- Learn about ServiceAccounts, Roles, and RoleBindings
- Identify 403 Forbidden errors in application logs
- Debug RBAC permission issues
- Understand how pods use ServiceAccounts to access the API

## The Challenge

Your team deployed a pod monitoring dashboard that needs to list pods in the cluster. The pod starts successfully and appears healthy, but the dashboard shows an error: "403 Forbidden - ServiceAccount lacks permission". The application logs confirm permission denied errors.

**Your mission:** Find out why the application can't access the Kubernetes API and fix the RBAC configuration!

## Step 1: Deploy the Broken Application

```bash
cd scenarios/05-rbac-forbidden
kubectl apply -f broken/
```

**Expected output:**
```
serviceaccount/pod-monitor created
deployment.apps/pod-monitor created
service/pod-monitor-service created
```

## Step 2: Observe the Failure

Wait about 10-15 seconds, then check the pod status:

```bash
kubectl get pods -l app=pod-monitor
```

**What you should see:**
```
NAME                           READY   STATUS    RESTARTS   AGE
pod-monitor-xxxxxxxxxx-xxxxx   1/1     Running   0          30s
```

✅ The pod is running! But let's check the application logs:

```bash
kubectl logs -l app=pod-monitor
```

**What you should see:**
```
[2025-11-24 ...] Starting Pod Monitor Dashboard...
[2025-11-24 ...] Pod: pod-monitor-xxxxxxxxxx-xxxxx
[2025-11-24 ...] ERROR: 403 - Forbidden: ServiceAccount lacks permission to list pods
[2025-11-24 ...] Cannot fetch pod list: <Response [403]>
```

❌ The pod is running, but the application can't access the Kubernetes API!

## Step 3: Investigate

### Check Application Logs
```bash
kubectl logs -l app=pod-monitor --tail=20
```

Look for 403 Forbidden errors.

### Check the ServiceAccount
```bash
kubectl get serviceaccount pod-monitor
kubectl describe serviceaccount pod-monitor
```

### Check What Permissions the ServiceAccount Has
```bash
# Check if there are any Roles or RoleBindings
kubectl get roles
kubectl get rolebindings

# Check what the pod's ServiceAccount can do
kubectl auth can-i list pods --as=system:serviceaccount:default:pod-monitor
```

**Expected output:**
```
no
```

### Check the Deployment Configuration
```bash
kubectl get deployment pod-monitor -o yaml | grep -A 3 serviceAccount
```

**Key Questions:**
- What ServiceAccount is the pod using?
- Does that ServiceAccount have any Roles or RoleBindings?
- What permissions does the application need?
- What error appears in the logs?

### Access the Dashboard (Optional)
```bash
kubectl port-forward -l app=pod-monitor 8080:5000
```

Open http://localhost:8080 in your browser - you'll see the error message displayed.

## Step 4: Troubleshoot

<details>
<summary>💡 Hint 1 - Read the error message</summary>

The logs say "403 - Forbidden: ServiceAccount lacks permission". What does this tell you about RBAC?

</details>

<details>
<summary>💡 Hint 2 - Check RBAC resources</summary>

The deployment uses a ServiceAccount, but does that ServiceAccount have any Roles or RoleBindings? Check with `kubectl get roles` and `kubectl get rolebindings`.

</details>

<details>
<summary>💡 Hint 3 - What's missing?</summary>

You need to create:
1. A **Role** that defines what permissions are needed (e.g., list pods)
2. A **RoleBinding** that binds the Role to the ServiceAccount

</details>

<details>
<summary>✅ Solution</summary>

### The Problem

The deployment uses a ServiceAccount (`pod-monitor`), but this ServiceAccount has no permissions granted to it. When the application tries to call the Kubernetes API to list pods, it receives a 403 Forbidden error because the ServiceAccount lacks the necessary RBAC permissions.

**Key Issue:**
- ServiceAccount exists: `pod-monitor` ✅
- ServiceAccount has no Roles or RoleBindings ❌
- Application needs to `list` pods ❌
- Result: 403 Forbidden error

### The Fix

```bash
kubectl apply -f solution/
```

**What changed:**

The solution adds a Role and RoleBinding:

```yaml
# Role defines what permissions are needed
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
---
# RoleBinding connects the Role to the ServiceAccount
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: pod-monitor-binding
subjects:
- kind: ServiceAccount
  name: pod-monitor
  namespace: default
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

### Why This Works

1. **RBAC Model**: Kubernetes uses Role-Based Access Control
   - **ServiceAccount**: Identity for pods
   - **Role**: Defines permissions (what can be done)
   - **RoleBinding**: Connects Role to ServiceAccount (who can do it)

2. **API Access**: Pods use their ServiceAccount's token to authenticate to the Kubernetes API

3. **Permission Check**: When the application calls the API, Kubernetes checks:
   - Does the ServiceAccount have a RoleBinding? ✅
   - Does the Role allow the requested action? ✅
   - If yes, allow; if no, return 403 Forbidden

4. **Namespace Scoped**: Roles and RoleBindings are namespace-scoped (use ClusterRole/ClusterRoleBinding for cluster-wide permissions)

**Key Kubernetes Concept:** By default, ServiceAccounts have no permissions. You must explicitly grant permissions using Roles/ClusterRoles and RoleBindings/ClusterRoleBindings.

</details>

## Step 5: Verify the Fix

Check that the application can now access the API:

```bash
kubectl logs -l app=pod-monitor --tail=20
```

**Expected output:**
```
[2025-11-24 ...] Starting Pod Monitor Dashboard...
[2025-11-24 ...] Pod: pod-monitor-xxxxxxxxxx-xxxxx
[2025-11-24 ...] ✅ Successfully fetched pod list
[2025-11-24 ...] Found 5 pods in namespace 'default'
[2025-11-24 ...] Dashboard ready at http://0.0.0.0:5000
```

Verify RBAC is working:

```bash
kubectl auth can-i list pods --as=system:serviceaccount:default:pod-monitor
```

**Expected output:**
```
yes
```

Access the dashboard:

```bash
kubectl port-forward -l app=pod-monitor 8080:5000
```

Open http://localhost:8080 - you should now see a list of pods in the dashboard!

## Step 6: Cleanup

```bash
kubectl delete -f solution/
```

## What You Learned

✅ Understanding Kubernetes RBAC model (ServiceAccount, Role, RoleBinding)
✅ Identifying 403 Forbidden errors in application logs
✅ Using `kubectl auth can-i` to check permissions
✅ How pods authenticate to the Kubernetes API using ServiceAccounts
✅ Creating Roles to define permissions
✅ Creating RoleBindings to grant permissions
✅ Best practice: Grant minimum required permissions (principle of least privilege)

## Common Pitfalls

- **Missing RoleBinding**: Created Role but forgot RoleBinding
- **Wrong ServiceAccount**: RoleBinding references wrong ServiceAccount name
- **Wrong namespace**: RoleBinding must be in same namespace as ServiceAccount
- **Insufficient verbs**: Role doesn't include all needed verbs (get, list, watch)
- **Wrong resources**: Role references wrong API group or resource name

## Going Deeper

**Kubernetes Documentation:**
- [RBAC Authorization](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
- [Using RBAC Authorization](https://kubernetes.io/docs/reference/access-authn-authz/rbac/#using-rbac-authorization)
- [ServiceAccounts](https://kubernetes.io/docs/concepts/security/service-accounts/)

**Related Concepts:**
- **ClusterRole/ClusterRoleBinding**: For cluster-wide permissions
- **Role/RoleBinding**: For namespace-scoped permissions
- **verbs**: get, list, watch, create, update, patch, delete
- **apiGroups**: "" for core resources, "apps" for Deployments, etc.
- **resources**: pods, services, configmaps, etc.

**Try This:**
```bash
# Check what a ServiceAccount can do
kubectl auth can-i --list --as=system:serviceaccount:default:pod-monitor

# Create a Role that allows reading ConfigMaps
kubectl create role configmap-reader --verb=get,list --resource=configmaps

# Bind it to a ServiceAccount
kubectl create rolebinding configmap-reader-binding \
  --role=configmap-reader \
  --serviceaccount=default:pod-monitor

# Test the permission
kubectl auth can-i get configmaps --as=system:serviceaccount:default:pod-monitor
```

**Debugging RBAC:**
```bash
# View all Roles in namespace
kubectl get roles

# View Role details
kubectl describe role pod-reader

# View all RoleBindings
kubectl get rolebindings

# View RoleBinding details
kubectl describe rolebinding pod-monitor-binding

# Check what permissions a user/SA has
kubectl auth can-i --list --as=system:serviceaccount:default:pod-monitor
```

## Next Challenge

Ready for more? Try **[Scenario 6: OOMKilled](../06-oom-killed/)** to learn about resource limits and memory management!

---

**Questions or Issues?** Open an issue on [GitHub](https://github.com/vellankikoti/k8s-masterclass/issues)

