# Scenario 2: ImagePullBackOff

**Difficulty:** Beginner
**Estimated Time:** 15 minutes
**Image:** `vellankikoti/k8s-masterclass-crashloop:v1.0` (correct), `broken` (incorrect tag)

## Learning Objectives

- Understand the ImagePullBackOff pod state
- Learn how image pull errors occur
- Use `kubectl describe` to identify image pull failures
- Understand container image naming and tagging
- Fix image reference errors

## The Challenge

A developer just pushed a deployment manifest to the cluster, but the pods won't start. The status shows `ImagePullBackOff`, and no containers are running. The team needs to deploy this application urgently!

**Your mission:** Figure out why Kubernetes can't pull the container image and get the app running!

## Step 1: Deploy the Broken Application

```bash
cd scenarios/02-image-pull-backoff
kubectl apply -f broken/
```

**Expected output:**
```
deployment.apps/imagepull-app created
```

## Step 2: Observe the Failure

Wait about 15-30 seconds, then check the pod status:

```bash
kubectl get pods
```

**What you should see:**
```
NAME                             READY   STATUS             RESTARTS   AGE
imagepull-app-xxxxxxxxxx-xxxxx   0/1     ImagePullBackOff   0          45s
```

Or you might see:
```
NAME                             READY   STATUS         RESTARTS   AGE
imagepull-app-xxxxxxxxxx-xxxxx   0/1     ErrImagePull   0          15s
```

Notice:
- `STATUS` shows `ImagePullBackOff` or `ErrImagePull`
- `RESTARTS` stays at 0 (the container never started)
- Pod is never `READY` (0/1)

## Step 3: Investigate

### View Pod Details
```bash
kubectl describe pod -l app=imagepull-app
```

Look for the **Events** section at the bottom:

```
Events:
  Type     Reason     Age                From               Message
  ----     ------     ----               ----               -------
  Normal   Scheduled  45s                default-scheduler  Successfully assigned default/imagepull-app-xxx to node
  Normal   Pulling    15s (x3 over 45s)  kubelet            Pulling image "vellankikoti/k8s-masterclass-crashloop:broken"
  Warning  Failed     15s (x3 over 45s)  kubelet            Failed to pull image "vellankikoti/k8s-masterclass-crashloop:broken": rpc error: code = NotFound desc = failed to pull and unpack image "docker.io/vellankikoti/k8s-masterclass-crashloop:broken": failed to resolve reference "docker.io/vellankikoti/k8s-masterclass-crashloop:broken": docker.io/vellankikoti/k8s-masterclass-crashloop:broken: not found
  Warning  Failed     15s (x3 over 45s)  kubelet            Error: ErrImagePull
  Normal   BackOff    5s (x2 over 45s)   kubelet            Back-off pulling image "vellankikoti/k8s-masterclass-crashloop:broken"
  Warning  Failed     5s (x2 over 45s)   kubelet            Error: ImagePullBackOff
```

**Key Questions:**
- What image is Kubernetes trying to pull?
- What error message does the kubelet report?
- Does the image tag exist in the registry?

### Check the Deployment Spec
```bash
kubectl get deployment imagepull-app -o yaml | grep image:
```

## Step 4: Troubleshoot

<details>
<summary>💡 Hint 1 - Read the error message</summary>

Look at the "Failed to pull image" message in the events. What does "not found" mean?

</details>

<details>
<summary>💡 Hint 2 - Check the image tag</summary>

The image reference is: `vellankikoti/k8s-masterclass-crashloop:broken`

Does the tag `:broken` exist? What tags are available for this image?

</details>

<details>
<summary>💡 Hint 3 - What's the correct tag?</summary>

Try using `:v1.0` instead of `:broken`

</details>

<details>
<summary>✅ Solution</summary>

### The Problem

The deployment references a non-existent image tag: `vellankikoti/k8s-masterclass-crashloop:broken`

While the repository `vellankikoti/k8s-masterclass-crashloop` exists on Docker Hub, there is no tag called `broken`. Kubernetes attempts to pull the image several times, then backs off when it repeatedly fails.

### The Fix

```bash
kubectl apply -f solution/
```

**What changed:**

```yaml
spec:
  containers:
  - name: app
    # Changed from :broken to :v1.0
    image: vellankikoti/k8s-masterclass-crashloop:v1.0
    env:
    - name: REQUIRED_CONFIG
      value: "production"
```

### Why This Works

1. **Image naming format**: `registry/username/repository:tag`
   - Registry: `docker.io` (default, can be omitted)
   - Username: `vellankikoti`
   - Repository: `k8s-masterclass-crashloop`
   - Tag: `v1.0` (corrected from `broken`)

2. **Kubernetes behavior**: When kubelet can't pull an image, it:
   - First shows `ErrImagePull`
   - Retries with exponential backoff
   - Shows `ImagePullBackOff` when backing off

3. **The tag `v1.0` exists** in the registry and can be pulled successfully

**Note:** We also added the `REQUIRED_CONFIG` environment variable from Scenario 1, otherwise the pod would crash after pulling the image!

</details>

## Step 5: Verify the Fix

Check that the image pulls successfully and the pod runs:

```bash
kubectl get pods
```

**Expected output:**
```
NAME                             READY   STATUS    RESTARTS   AGE
imagepull-app-xxxxxxxxxx-xxxxx   1/1     Running   0          30s
```

View the events to see successful image pull:

```bash
kubectl describe pod -l app=imagepull-app | grep -A 5 Events
```

You should see:
```
Events:
  Type    Reason     Age   From               Message
  ----    ------     ----  ----               -------
  Normal  Scheduled  45s   default-scheduler  Successfully assigned default/imagepull-app-xxx to node
  Normal  Pulling    44s   kubelet            Pulling image "vellankikoti/k8s-masterclass-crashloop:v1.0"
  Normal  Pulled     40s   kubelet            Successfully pulled image "vellankikoti/k8s-masterclass-crashloop:v1.0"
  Normal  Created    40s   kubelet            Created container app
  Normal  Started    40s   kubelet            Started container app
```

## Step 6: Cleanup

```bash
kubectl delete -f solution/
```

## What You Learned

✅ Understanding ImagePullBackOff vs ErrImagePull states
✅ How to read image pull errors in `kubectl describe`
✅ Container image naming: `registry/username/repository:tag`
✅ Kubernetes retries image pulls with exponential backoff
✅ Common causes: typos in image name/tag, wrong registry, missing credentials
✅ How to verify image existence before deploying

## Common Pitfalls

- **Typos in image names**: Double-check spelling of registry, username, repository, and tag
- **Missing tag**: If you don't specify a tag, Kubernetes uses `:latest` by default
- **Private registries**: If images require authentication, you need `imagePullSecrets`
- **Wrong registry**: Forgetting to specify `gcr.io`, `ghcr.io`, or other registries

## Going Deeper

**Kubernetes Documentation:**
- [Images](https://kubernetes.io/docs/concepts/containers/images/)
- [Pulling Images from Private Registries](https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/)

**Related Concepts:**
- Image pull policies: `Always`, `IfNotPresent`, `Never`
- `imagePullSecrets` for private registries
- Image digests for immutable deployments (`image@sha256:...`)

**Try This:**
- Pull the image manually: `docker pull vellankikoti/k8s-masterclass-crashloop:v1.0`
- Check available tags on Docker Hub
- Try using `imagePullPolicy: Never` with a local image

**Debugging Commands:**
```bash
# Check what images nodes have cached
kubectl get nodes -o json | jq '.items[].status.images'

# View image pull policy
kubectl get deployment imagepull-app -o jsonpath='{.spec.template.spec.containers[0].imagePullPolicy}'
```

## Next Challenge

Ready for more? Try **[Scenario 3: Port Mismatch](../03-port-mismatch/)** to learn about service networking issues!

---

**Questions or Issues?** Open an issue on [GitHub](https://github.com/vellankikoti/k8s-masterclass/issues)
