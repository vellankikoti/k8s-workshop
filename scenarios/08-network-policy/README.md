# Scenario 8: Network Policy

**Difficulty:** Advanced
**Estimated Time:** 25 minutes
**Images:** 
- `vellankikoti/k8s-masterclass-netpol-client:v1.0` (Order Service)
- `vellankikoti/k8s-masterclass-netpol-server:v1.0` (Inventory Service)

## Learning Objectives

- Understand Kubernetes NetworkPolicies
- Learn how NetworkPolicies control pod-to-pod communication
- Identify network policy blocking issues
- Debug connectivity problems between pods
- Understand pod selectors and label-based policies

## The Challenge

Your team deployed a microservices application with an order service (frontend) and an inventory service (backend). The pods are running, but the order service cannot connect to the inventory service. A NetworkPolicy was recently applied for security, and now legitimate traffic is being blocked.

**Your mission:** Find out why the NetworkPolicy is blocking traffic and fix it to allow the frontend to communicate with the backend!

## Step 1: Deploy the Broken Application

```bash
cd scenarios/08-network-policy
kubectl apply -f broken/
```

**Expected output:**
```
deployment.apps/inventory-service created
service/inventory-service created
deployment.apps/order-service created
service/order-service created
networkpolicy.networking.k8s.io/deny-all-ingress created
```

## Step 2: Observe the Failure

Wait about 15-20 seconds, then check pod status:

```bash
kubectl get pods
```

**What you should see:**
```
NAME                                 READY   STATUS    RESTARTS   AGE
inventory-service-xxxxxxxxxx-xxxxx   1/1     Running   0          30s
order-service-xxxxxxxxxx-xxxxx       1/1     Running   0          30s
```

✅ Both pods are running! But let's check if they can communicate:

```bash
# Port-forward to order service
kubectl port-forward -l app=order 8080:5000 &
```

Open http://localhost:8080 in your browser, or check logs:

```bash
kubectl logs -l app=order --tail=20
```

**What you should see:**
```
[2025-11-24 ...] Starting Order Service...
[2025-11-24 ...] ERROR: Connection refused - NetworkPolicy may be blocking traffic
[2025-11-24 ...] Cannot connect to inventory-service
```

❌ The order service cannot connect to the inventory service!

## Step 3: Investigate

### Check Pod Status
```bash
kubectl get pods -l app=order
kubectl get pods -l app=inventory
```

Both should be running.

### Check Services
```bash
kubectl get svc
```

**Expected output:**
```
NAME                TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE
inventory-service   ClusterIP   10.96.xxx.xxx   <none>        80/TCP    1m
order-service       ClusterIP   10.96.xxx.xxx   <none>        80/TCP    1m
```

✅ Services exist!

### Check NetworkPolicy
```bash
kubectl get networkpolicy
```

**Expected output:**
```
NAME              POD-SELECTOR      AGE
deny-all-ingress  role=backend      1m
```

```bash
kubectl describe networkpolicy deny-all-ingress
```

**What you should see:**
```
Name:         deny-all-ingress
Namespace:    default
Created:      1m ago
Labels:       <none>
Annotations:  <none>
Spec:
  Pod Selector:     role=backend
  Allowing ingress traffic:
    <none>  ❌ No ingress rules = deny all!
  Allowing egress traffic:
    <none>
  Policy Types: Ingress
```

### Test Connectivity from Order Pod
```bash
# Get order pod name
ORDER_POD=$(kubectl get pod -l app=order -o jsonpath='{.items[0].metadata.name}')

# Try to connect to inventory service from order pod
kubectl exec $ORDER_POD -- wget -O- --timeout=3 http://inventory-service:80
```

**Expected output:**
```
wget: download timed out
OR
wget: can't connect to remote host
```

❌ Connection fails!

### Check Pod Labels
```bash
kubectl get pods --show-labels
```

**What you should see:**
```
NAME                                 ...   LABELS
inventory-service-xxx               ...   app=inventory,role=backend
order-service-xxx                    ...   app=order,role=frontend
```

**Key Questions:**
- What pods does the NetworkPolicy apply to? (check podSelector)
- What ingress rules does the NetworkPolicy have?
- What labels do the pods have?
- Can the frontend pods connect to backend pods?

## Step 4: Troubleshoot

<details>
<summary>💡 Hint 1 - Understand the NetworkPolicy</summary>

The NetworkPolicy is named "deny-all-ingress" and applies to pods with `role=backend`. What does "deny-all" suggest about the ingress rules?

</details>

<details>
<summary>💡 Hint 2 - Check ingress rules</summary>

The NetworkPolicy has `policyTypes: [Ingress]` but no `ingress` rules. In Kubernetes, if you specify Ingress policy type but don't define any ingress rules, what happens?

</details>

<details>
<summary>💡 Hint 3 - Allow frontend to backend</summary>

You need to add an ingress rule that allows pods with `role=frontend` to connect to pods with `role=backend` on port 5000.

</details>

<details>
<summary>✅ Solution</summary>

### The Problem

The NetworkPolicy `deny-all-ingress` applies to pods with `role=backend` (the inventory service). It specifies `policyTypes: [Ingress]` but has **no ingress rules defined**. In Kubernetes, when a NetworkPolicy specifies Ingress but has no rules, it defaults to **deny all ingress traffic**.

**Key Issue:**
- NetworkPolicy applies to: `role=backend` pods (inventory service) ✅
- NetworkPolicy has: `policyTypes: [Ingress]` ✅
- NetworkPolicy has: **No ingress rules** ❌
- Result: All ingress traffic to backend pods is denied
- Order service (frontend) cannot connect to inventory service (backend)

**Default Behavior:**
- If no NetworkPolicy applies → allow all traffic
- If NetworkPolicy applies with no rules → deny all traffic (default deny)

### The Fix

```bash
kubectl apply -f solution/
```

**What changed:**

```yaml
# FIXED: NetworkPolicy that allows ingress from order-service (frontend) to inventory-service (backend)
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-backend
spec:
  podSelector:
    matchLabels:
      role: backend  # Applies to inventory service pods
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          role: frontend  # Allow traffic from frontend pods
    ports:
    - protocol: TCP
      port: 5000  # Allow on port 5000
```

### Why This Works

1. **NetworkPolicy Basics**:
   - Controls pod-to-pod communication
   - Uses pod selectors (labels) to identify pods
   - Default deny if policy applies but no rules match

2. **Policy Structure**:
   - **podSelector**: Which pods this policy applies to
   - **policyTypes**: Ingress (incoming) and/or Egress (outgoing)
   - **ingress/egress rules**: What traffic is allowed

3. **Label-Based Selection**:
   - Frontend pods have: `role=frontend`
   - Backend pods have: `role=backend`
   - Policy allows: `role=frontend` → `role=backend` on port 5000

4. **Traffic Flow**:
   - Order service (frontend) → Inventory service (backend) ✅
   - Other pods → Inventory service ❌ (not allowed)
   - Inventory service → Anywhere ✅ (no egress policy)

**Key Kubernetes Concept:** NetworkPolicies are additive - if a pod matches a NetworkPolicy, it must have an explicit allow rule to receive traffic. No rules = deny all.

</details>

## Step 5: Verify the Fix

Check that the order service can now connect:

```bash
kubectl logs -l app=order --tail=20
```

**Expected output:**
```
[2025-11-24 ...] Starting Order Service...
[2025-11-24 ...] ✅ Successfully connected to inventory-service
[2025-11-24 ...] Dashboard ready at http://0.0.0.0:5000
```

✅ Connection successful!

Test from the order pod:

```bash
ORDER_POD=$(kubectl get pod -l app=order -o jsonpath='{.items[0].metadata.name}')
kubectl exec $ORDER_POD -- wget -O- --timeout=3 http://inventory-service:80
```

You should see a successful response!

Access the order service dashboard:

```bash
kubectl port-forward -l app=order 8080:5000
```

Open http://localhost:8080 - you should now see the inventory items displayed!

## Step 6: Cleanup

```bash
kubectl delete -f solution/
```

## What You Learned

✅ Understanding Kubernetes NetworkPolicies and how they control traffic
✅ Using pod selectors and labels for network policy rules
✅ Understanding default deny behavior in NetworkPolicies
✅ Debugging pod-to-pod connectivity issues
✅ Using `kubectl describe networkpolicy` to inspect policies
✅ Best practice: Explicitly allow required traffic, deny by default

## Common Pitfalls

- **No ingress rules**: Specifying Ingress policy type without rules = deny all
- **Wrong pod selector**: Policy applies to wrong pods
- **Wrong label selector**: Ingress rule doesn't match source pods
- **Wrong port**: Policy allows traffic but on wrong port
- **Missing policy type**: Forgot to specify Ingress/Egress
- **CNI not supporting NetworkPolicies**: Some cluster setups don't support NetworkPolicies

## Going Deeper

**Kubernetes Documentation:**
- [Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [Declare Network Policy](https://kubernetes.io/docs/tasks/administer-cluster/declare-network-policy/)

**Related Concepts:**
- **CNI Plugins**: NetworkPolicies require CNI that supports them (Calico, Cilium, etc.)
- **Default Behavior**: No policy = allow all, policy with no rules = deny all
- **Namespace Isolation**: NetworkPolicies are namespace-scoped
- **Egress Policies**: Can also control outbound traffic
- **IP Blocks**: Can allow/deny specific IP ranges

**Try This:**
```bash
# View all NetworkPolicies
kubectl get networkpolicies

# Describe a NetworkPolicy
kubectl describe networkpolicy allow-frontend-to-backend

# Test connectivity between pods
kubectl exec <pod-name> -- wget -O- http://<service-name>

# Check if CNI supports NetworkPolicies
kubectl get networkpolicies
# If this works, your CNI supports NetworkPolicies

# Create a policy that allows all ingress
kubectl create networkpolicy allow-all \
  --pod-selector="" \
  --ingress=""
```

**NetworkPolicy Examples:**
```yaml
# Allow all ingress to a pod
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  ingress:
  - {}  # Empty rule = allow all

# Deny all ingress (default deny)
spec:
  podSelector:
    matchLabels:
      app: myapp
  policyTypes:
  - Ingress
  # No ingress rules = deny all

# Allow from specific namespace
ingress:
- from:
  - namespaceSelector:
      matchLabels:
        name: production
```

## Next Challenge

Ready for more? Try **[Scenario 9: PVC Pending](../09-pvc-pending/)** to learn about persistent storage!

---

**Questions or Issues?** Open an issue on [GitHub](https://github.com/vellankikoti/k8s-masterclass/issues)

