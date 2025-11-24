# Scenario 9: PVC Pending

**Difficulty:** Advanced
**Estimated Time:** 25 minutes
**Image:** `vellankikoti/k8s-masterclass-storage-app:v1.0`

## Learning Objectives

- Understand PersistentVolumeClaims (PVCs) and StorageClasses
- Learn about dynamic volume provisioning
- Identify PVC pending issues
- Debug storage provisioning problems
- Understand the relationship between PVCs, PVs, and StorageClasses

## The Challenge

Your team deployed a file service that requires persistent storage. The deployment was applied, but the pod is stuck in `ContainerCreating` state and won't start. The PersistentVolumeClaim shows `Pending` status.

**Your mission:** Find out why the PVC is pending and fix the storage configuration!

## Step 1: Deploy the Broken Application

```bash
cd scenarios/09-pvc-pending
kubectl apply -f broken/
```

**Expected output:**
```
persistentvolumeclaim/file-storage created
deployment.apps/file-service created
service/file-service created
```

## Step 2: Observe the Failure

Wait about 15-20 seconds, then check the PVC status:

```bash
kubectl get pvc
```

**What you should see:**
```
NAME           STATUS    VOLUME   CAPACITY   ACCESS MODES   STORAGECLASS   AGE
file-storage   Pending                                      <none>         1m
```

Notice:
- `STATUS` shows `Pending` ❌
- `VOLUME` is empty (no volume bound)
- `STORAGECLASS` shows `<none>` (no storage class specified)

Check the pod status:

```bash
kubectl get pods -l app=file-service
```

**What you should see:**
```
NAME                           READY   STATUS              RESTARTS   AGE
file-service-xxxxxxxxxx-xxxxx   0/1     ContainerCreating   0          1m
```

❌ Pod is stuck in `ContainerCreating` because it's waiting for the PVC to be bound!

## Step 3: Investigate

### View PVC Details
```bash
kubectl describe pvc file-storage
```

Look for the **Events** section:

```
Events:
  Type     Reason              Age                From                         Message
  ----     ------              ----               ----                         -------
  Warning  ProvisioningFailed  30s                persistentvolume-controller  storageclass.storage.k8s.io "<none>" not found
```

Also check **Conditions**:

```
Status:
  Phase:  Pending
Conditions:
  Type       Status  LastProbeTime                     LastTransitionTime                Reason  Message
  ----       ------  -----------------                 --------------------                ------  -------
  ProvisioningFailed  True   2025-11-24T12:00:00Z      2025-11-24T12:00:00Z              NoStorageClass
```

### Check Available StorageClasses
```bash
kubectl get storageclass
```

**What you should see (varies by cluster):**
```
NAME                 PROVISIONER       RECLAIMPOLICY   VOLUMEBINDINGMODE   AGE
standard (default)   k8s.io/minikube  Delete          Immediate           5d
```

Or for kind:
```
NAME            PROVISIONER             RECLAIMPOLICY   VOLUMEBINDINGMODE   AGE
standard        rancher.io/local-path   Delete          WaitForFirstConsumer 5d
```

### Check the PVC Configuration
```bash
kubectl get pvc file-storage -o yaml | grep -A 10 spec
```

**What you should see:**
```yaml
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
  # No storageClassName specified!
```

### Check Pod Events
```bash
kubectl describe pod -l app=file-service
```

Look for events related to volume mounting:

```
Events:
  Type     Reason            Age                From               Message
  ----     ------            ----               ----               -------
  Warning  FailedMount      1m (x5 over 2m)    kubelet            Unable to attach or mount volumes: unmounted volumes=[storage], unattached volumes=[storage]
```

**Key Questions:**
- What StorageClass is the PVC using?
- Are there any StorageClasses available in the cluster?
- What error appears in the PVC events?
- Why can't the volume be provisioned?

## Step 4: Troubleshoot

<details>
<summary>💡 Hint 1 - Check StorageClass</summary>

The PVC doesn't have a `storageClassName` specified. Does your cluster have a default StorageClass? If not, you need to specify one explicitly.

</details>

<details>
<summary>💡 Hint 2 - Find available StorageClasses</summary>

Run `kubectl get storageclass` to see what StorageClasses are available. You need to specify one in the PVC.

</details>

<details>
<summary>💡 Hint 3 - Specify storageClassName</summary>

You need to add `storageClassName` to the PVC spec. Use the StorageClass name from your cluster (commonly "standard" or "hostpath" for local clusters).

</details>

<details>
<summary>✅ Solution</summary>

### The Problem

The PersistentVolumeClaim doesn't specify a `storageClassName`. While some clusters have a default StorageClass that would be used automatically, many clusters (especially kind, k3d, or custom setups) don't have a default StorageClass set. Without a StorageClass, Kubernetes cannot provision the volume dynamically.

**Key Issue:**
- PVC has no `storageClassName` specified ❌
- Cluster may not have a default StorageClass ❌
- Result: PVC remains `Pending`, no volume provisioned, pod cannot start

**Storage Provisioning Flow:**
1. PVC created → Kubernetes looks for StorageClass
2. If no StorageClass → Cannot provision volume
3. PVC stays `Pending` → Pod waits for volume
4. Pod stuck in `ContainerCreating`

### The Fix

```bash
kubectl apply -f solution/
```

**What changed:**

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: file-storage
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
  # FIXED: Specify storageClassName
  storageClassName: standard  # Change to match your cluster's StorageClass
```

**Note:** The StorageClass name varies by cluster:
- **Docker Desktop**: `hostpath` or `standard`
- **minikube**: `standard`
- **kind**: `standard` (local-path provisioner)
- **k3d**: `local-path`
- **GKE/EKS/AKS**: Usually `standard` or cluster-specific names

### Why This Works

1. **StorageClass**: Defines how volumes are provisioned
   - **Provisioner**: The storage driver (local-path, hostpath, cloud provider, etc.)
   - **Parameters**: Configuration for the provisioner
   - **Reclaim Policy**: What happens when PVC is deleted (Delete, Retain)

2. **Dynamic Provisioning**:
   - PVC requests storage → StorageClass provisioner creates PV → PV bound to PVC → Pod can mount

3. **Default StorageClass**:
   - Some clusters set a default StorageClass (marked with annotation)
   - If default exists, PVC without `storageClassName` uses it
   - If no default, must specify `storageClassName` explicitly

4. **Volume Binding**:
   - **Immediate**: PV created immediately when PVC created
   - **WaitForFirstConsumer**: PV created when pod using it is scheduled

**Key Kubernetes Concept:** PVCs require a StorageClass (or default) to provision volumes dynamically. Always check available StorageClasses and specify one explicitly if no default exists.

</details>

## Step 5: Verify the Fix

Check that the PVC is now bound:

```bash
kubectl get pvc
```

**Expected output:**
```
NAME           STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   AGE
file-storage   Bound    pvc-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx   1Gi        RWO            standard       1m
```

✅ PVC is now `Bound`!

Check the pod status:

```bash
kubectl get pods -l app=file-service
```

**Expected output:**
```
NAME                           READY   STATUS    RESTARTS   AGE
file-service-xxxxxxxxxx-xxxxx   1/1     Running   0          1m
```

✅ Pod is now running!

Check the PersistentVolume:

```bash
kubectl get pv
```

You should see a PV that was automatically created and bound to the PVC.

Test the file service:

```bash
kubectl port-forward -l app=file-service 8080:5000
```

Access http://localhost:8080 - you should see the file service interface!

## Step 6: Cleanup

```bash
kubectl delete -f solution/
```

**Note:** Deleting the PVC will also delete the dynamically provisioned PV (if reclaim policy is Delete).

## What You Learned

✅ Understanding PersistentVolumeClaims and StorageClasses
✅ How dynamic volume provisioning works
✅ Identifying PVC pending issues
✅ Using `kubectl describe pvc` to debug storage problems
✅ Understanding the relationship between PVCs, PVs, and StorageClasses
✅ Best practice: Always specify storageClassName explicitly

## Common Pitfalls

- **No StorageClass**: PVC doesn't specify storageClassName and cluster has no default
- **Wrong StorageClass name**: Typo in storageClassName
- **StorageClass doesn't exist**: Referenced StorageClass not found in cluster
- **Insufficient storage**: Cluster doesn't have enough storage capacity
- **Access mode mismatch**: Requested access mode not supported by StorageClass
- **Reclaim policy**: Understanding Delete vs Retain

## Going Deeper

**Kubernetes Documentation:**
- [Persistent Volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)
- [Storage Classes](https://kubernetes.io/docs/concepts/storage/storage-classes/)
- [Dynamic Volume Provisioning](https://kubernetes.io/docs/concepts/storage/dynamic-provisioning/)

**Related Concepts:**
- **Static Provisioning**: Manually create PV, then create PVC that binds to it
- **Dynamic Provisioning**: StorageClass automatically creates PV when PVC is created
- **Access Modes**: ReadWriteOnce, ReadOnlyMany, ReadWriteMany
- **Volume Modes**: Filesystem vs Block
- **Reclaim Policies**: Delete (remove PV when PVC deleted) vs Retain (keep PV)

**Try This:**
```bash
# List all StorageClasses
kubectl get storageclass

# Check which StorageClass is default
kubectl get storageclass -o jsonpath='{.items[?(@.metadata.annotations.storageclass\.kubernetes\.io/is-default-class=="true")].metadata.name}'

# View StorageClass details
kubectl describe storageclass standard

# Check PVC details
kubectl describe pvc file-storage

# View the bound PersistentVolume
kubectl get pv
kubectl describe pv <pv-name>

# Check volume mount in pod
kubectl describe pod -l app=file-service | grep -A 10 "Mounts"
```

**Finding Your Cluster's StorageClass:**
```bash
# Docker Desktop
kubectl get storageclass
# Usually: hostpath or standard

# minikube
kubectl get storageclass
# Usually: standard

# kind
kubectl get storageclass
# Usually: standard (local-path)

# Check default
kubectl get storageclass -o yaml | grep -A 5 "is-default-class"
```

## Next Challenge

Ready for the final challenge? Try **[Scenario 10: Init Container Failure](../10-init-container-failure/)** to learn about pod initialization!

---

**Questions or Issues?** Open an issue on [GitHub](https://github.com/vellankikoti/k8s-masterclass/issues)

