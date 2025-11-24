# Kubernetes Masterclass - Troubleshooting Workshop

> **Master Kubernetes troubleshooting through hands-on scenarios with real failures**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker Hub](https://img.shields.io/badge/Docker%20Hub-vellankikoti-blue)](https://hub.docker.com/u/vellankikoti)

## 🎯 About This Workshop

Learn Kubernetes troubleshooting by encountering and fixing **real cluster failures** using `kubectl`. No simulated errors - every scenario uses actual Kubernetes behavior that you'll see in production environments.

**Key Features:**
- ✅ **10 Progressive Scenarios** - From beginner to advanced
- ✅ **Pre-built Images** - All container images available on Docker Hub
- ✅ **Real Applications** - Not just "hello world" - meaningful code
- ✅ **Self-Contained** - Each scenario includes broken and working solutions
- ✅ **No Build Required** - Pull images directly from Docker Hub

All container images are pre-built and publicly available on Docker Hub - no local builds required!

## 📚 What You'll Learn

### Beginner Level
- Pod lifecycle states and restart policies
- Reading container logs for debugging
- Container image registry concepts
- Service networking and port mapping

### Intermediate Level
- ConfigMaps and Secrets integration
- RBAC (Role-Based Access Control)
- Resource limits and OOMKilled pods
- Health probes (liveness, readiness, startup)

### Advanced Level
- Network policies and pod-to-pod communication
- Persistent Volume Claims (PVCs) and storage
- Init containers and pod initialization

## 🚀 Prerequisites

Before starting, ensure you have the following installed and configured:

### Required Tools

- **kubectl** (v1.28 or higher)
  ```bash
  kubectl version --client
  ```

- **Docker** (for local cluster options)
  ```bash
  docker --version
  ```

- **A Kubernetes Cluster** - Choose one:
  - **Docker Desktop** (recommended for beginners)
  - **kind** (Kubernetes in Docker)
  - **minikube** (local Kubernetes)
  - **k3d** (lightweight alternative)

- **Basic kubectl knowledge**: `get`, `describe`, `logs`, `apply`, `delete`

### Verify Your Setup

Run these commands to verify everything is ready:

```bash
# Check kubectl is installed
kubectl version --client

# Check cluster connectivity
kubectl cluster-info

# Verify you can list nodes
kubectl get nodes

# Check default namespace
kubectl get pods
```

If any command fails, see the [Setup Instructions](#-setup-your-kubernetes-cluster) below.

## ⚙️ Setup Your Kubernetes Cluster

### Option 1: Docker Desktop (Easiest)

1. **Install Docker Desktop** from [docker.com](https://www.docker.com/products/docker-desktop)
2. **Enable Kubernetes**:
   - Open Docker Desktop
   - Go to Settings → Kubernetes
   - Check "Enable Kubernetes"
   - Click "Apply & Restart"
3. **Verify**:
   ```bash
   kubectl cluster-info
   kubectl get nodes
   ```

### Option 2: kind (Kubernetes in Docker)

```bash
# Install kind (macOS/Linux)
brew install kind
# OR download from: https://kind.sigs.k8s.io/docs/user/quick-start/

# Create cluster
kind create cluster --name k8s-workshop

# Verify
kubectl cluster-info
```

### Option 3: minikube

```bash
# Install minikube
brew install minikube  # macOS
# OR see: https://minikube.sigs.k8s.io/docs/start/

# Start cluster
minikube start --driver=docker

# Verify
kubectl cluster-info
minikube status
```

### Option 4: k3d (Lightweight)

```bash
# Install k3d
brew install k3d  # macOS
# OR see: https://k3d.io/

# Create cluster
k3d cluster create k8s-workshop

# Verify
kubectl cluster-info
```

## 🎓 Quick Start Guide

### Step 1: Clone or Download This Repository

```bash
# If using git
git clone <repository-url>
cd k8s-workshop

# Or download and extract the ZIP file
```

### Step 2: Verify Cluster Access

```bash
# Check cluster is accessible
kubectl cluster-info

# Verify you can create resources
kubectl get namespaces
```

### Step 3: Start Your First Scenario

Navigate to any scenario directory and follow its README:

```bash
cd scenarios/01-crashloop-backoff
cat README.md
```

Then follow the scenario instructions!

## 📖 Workshop Structure

**Total Time:** 4-6 hours (can be done in parts)

### Beginner Scenarios (1-1.5 hours)

| # | Scenario | Failure Type | Time | Concepts | Link |
|---|----------|--------------|------|----------|------|
| 1 | **CrashLoopBackOff** | Pod crashes repeatedly | 15 min | Pod lifecycle, env vars, logs | [Start →](scenarios/01-crashloop-backoff/) |
| 2 | **ImagePullBackOff** | Can't pull container image | 15 min | Image registries, tags | [Start →](scenarios/02-image-pull-backoff/) |
| 3 | **Port Mismatch** | Service can't reach pods | 20 min | Services, networking, ports | [Start →](scenarios/03-port-mismatch/) |

### Intermediate Scenarios (2-2.5 hours)

| # | Scenario | Failure Type | Time | Concepts | Link |
|---|----------|--------------|------|----------|------|
| 4 | **Missing ConfigMap** | Pod can't start due to config | 20 min | ConfigMaps, dependencies | [Start →](scenarios/04-missing-configmap/) |
| 5 | **RBAC Forbidden** | Permission denied errors | 25 min | RBAC, ServiceAccounts, Roles | [Start →](scenarios/05-rbac-forbidden/) |
| 6 | **OOMKilled** | Pod killed by memory limits | 20 min | Resource limits, memory mgmt | [Start →](scenarios/06-oom-killed/) |
| 7 | **Probe Failure** | Health checks failing | 20 min | Liveness/readiness probes | [Start →](scenarios/07-probe-failure/) |

### Advanced Scenarios (1.5-2 hours)

| # | Scenario | Failure Type | Time | Concepts | Link |
|---|----------|--------------|------|----------|------|
| 8 | **Network Policy** | Pods can't communicate | 25 min | NetworkPolicies, pod networking | [Start →](scenarios/08-network-policy/) |
| 9 | **PVC Pending** | Storage not provisioning | 25 min | PVCs, StorageClasses | [Start →](scenarios/09-pvc-pending/) |
| 10 | **Init Container Failure** | Pod stuck in init phase | 25 min | Init containers, debugging | [Start →](scenarios/10-init-container-failure/) |

## 🛠️ How Each Scenario Works

Every scenario follows this consistent pattern:

1. **📥 Deploy** - Apply broken Kubernetes manifests from the `broken/` directory
2. **👀 Observe** - See the failure using `kubectl get pods`, `kubectl describe`, etc.
3. **🔍 Investigate** - Use troubleshooting commands to gather information
4. **💡 Troubleshoot** - Follow hints (or jump to solution) to understand the issue
5. **✅ Fix** - Apply the working solution from the `solution/` directory
6. **🧪 Verify** - Confirm everything works correctly
7. **🧹 Cleanup** - Remove resources to prepare for the next scenario

### Example Workflow

```bash
# Navigate to a scenario
cd scenarios/01-crashloop-backoff

# Deploy the broken version
kubectl apply -f broken/

# Observe the failure
kubectl get pods
kubectl describe pod -l app=crashloop-app
kubectl logs -l app=crashloop-app

# Apply the fix
kubectl apply -f solution/

# Verify it works
kubectl get pods
kubectl logs -l app=crashloop-app

# Cleanup
kubectl delete -f solution/
```

## 📦 Container Images

All images are hosted on **Docker Hub** under the `vellankikoti/k8s-masterclass-*` namespace.

### Available Images

| Image Name | Tag | Scenario | Description |
|------------|-----|----------|-------------|
| `vellankikoti/k8s-masterclass-crashloop` | `v1.0`, `latest` | 1, 2 | Python app requiring env var |
| `vellankikoti/k8s-masterclass-webapp` | `v1.0`, `latest` | 3 | Flask web application |
| `vellankikoti/k8s-masterclass-config-app` | `v1.0`, `latest` | 4 | Blog app requiring ConfigMap |
| `vellankikoti/k8s-masterclass-rbac-app` | `v1.0`, `latest` | 5 | Pod monitor dashboard |
| `vellankikoti/k8s-masterclass-memory-hog` | `v1.0`, `latest` | 6 | Image processor service |
| `vellankikoti/k8s-masterclass-health-app` | `v1.0`, `latest` | 7 | API health check service |
| `vellankikoti/k8s-masterclass-netpol-client` | `v1.0`, `latest` | 8 | Network policy client app |
| `vellankikoti/k8s-masterclass-netpol-server` | `v1.0`, `latest` | 8 | Network policy server app |
| `vellankikoti/k8s-masterclass-storage-app` | `v1.0`, `latest` | 9 | PVC testing application |
| `vellankikoti/k8s-masterclass-init-app` | `v1.0`, `latest` | 10 | Init container demo app |

**All images are public** - no authentication required to pull!

### Pulling Images Manually (Optional)

You can test image pulls manually:

```bash
docker pull vellankikoti/k8s-masterclass-crashloop:v1.0
docker pull vellankikoti/k8s-masterclass-webapp:v1.0
# ... etc
```

## 🏗️ Building Images (For Contributors)

If you want to build images locally or contribute new scenarios:

### Prerequisites for Building

- Docker installed and running
- Docker Hub account (or your own registry)
- Logged in to Docker: `docker login -u vellankikoti`

### Build Scripts

Two build scripts are available in the `scripts/` directory:

**Option 1: Bash Script** (macOS, Linux, WSL)
```bash
cd scripts
chmod +x build-and-push-all.sh
./build-and-push-all.sh
```

**Option 2: Python Script** (Cross-platform)
```bash
cd scripts
python3 build-and-push-all.py
```

Both scripts will:
1. Check Docker is running
2. Verify Docker Hub login
3. Build all scenario images
4. Tag with both `v1.0` and `latest`
5. Push to Docker Hub

### Building Individual Images

```bash
# Example: Build scenario 1
docker build -t vellankikoti/k8s-masterclass-crashloop:v1.0 \
  -t vellankikoti/k8s-masterclass-crashloop:latest \
  scenarios/01-crashloop-backoff/app/

# Push to Docker Hub
docker push vellankikoti/k8s-masterclass-crashloop:v1.0
docker push vellankikoti/k8s-masterclass-crashloop:latest
```

See [BUILD_AND_TEST.md](BUILD_AND_TEST.md) for detailed build and test instructions.

## 🎓 Recommended Learning Path

We recommend following scenarios in order to build knowledge progressively:

```
Beginner Track:
  1 → 2 → 3
    ↓
Intermediate Track:
  4 → 5 → 6 → 7
    ↓
Advanced Track:
  8 → 9 → 10
```

**However**, each scenario is self-contained and can be completed independently if you prefer to focus on specific topics.

## 💡 Tips for Success

1. **Read the Error Messages** - Kubernetes provides detailed error information in `kubectl describe` and logs
2. **Use `kubectl describe`** - This is your best friend for debugging
3. **Check Logs Early** - Application logs often contain the exact error
4. **Compare Broken vs Solution** - Use `diff` to see what changed:
   ```bash
   diff -u broken/deployment.yaml solution/deployment.yaml
   ```
5. **Don't Skip Cleanup** - Always clean up after each scenario to avoid conflicts
6. **Take Notes** - Document what you learned from each scenario

## 🐛 Troubleshooting Common Issues

### Issue: `kubectl: command not found`

**Solution**: Install kubectl
- macOS: `brew install kubectl`
- Linux: See [kubectl installation guide](https://kubernetes.io/docs/tasks/tools/)
- Windows: Use WSL or see [kubectl installation guide](https://kubernetes.io/docs/tasks/tools/install-kubectl-windows/)

### Issue: `The connection to the server <hostname> was refused`

**Solution**: Your cluster is not running
- Docker Desktop: Enable Kubernetes in settings
- kind: Run `kind create cluster`
- minikube: Run `minikube start`

### Issue: `ImagePullBackOff` when pulling workshop images

**Solution**: 
- Check internet connection
- Verify image name is correct
- Try pulling manually: `docker pull vellankikoti/k8s-masterclass-crashloop:v1.0`

### Issue: Pods stuck in `Pending` state

**Solution**: 
- Check node resources: `kubectl describe node`
- Check for taints: `kubectl describe node | grep Taint`
- Verify cluster has enough resources

### Issue: Permission denied errors

**Solution**: 
- Check RBAC permissions: `kubectl auth can-i <verb> <resource>`
- Verify you're using the correct context: `kubectl config current-context`

## 📚 Additional Resources

### Official Kubernetes Documentation

- [Kubernetes Concepts](https://kubernetes.io/docs/concepts/)
- [kubectl Reference](https://kubernetes.io/docs/reference/kubectl/)
- [Troubleshooting Applications](https://kubernetes.io/docs/tasks/debug/)
- [Pod Lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)

### Useful kubectl Commands

```bash
# Get resources
kubectl get pods,svc,deploy,cm,secret

# Describe resources
kubectl describe pod <pod-name>

# View logs
kubectl logs <pod-name>
kubectl logs -f <pod-name>  # Follow logs

# Execute commands in pods
kubectl exec -it <pod-name> -- /bin/sh

# Port forward
kubectl port-forward <pod-name> <local-port>:<pod-port>

# Get resource YAML
kubectl get <resource> <name> -o yaml

# Watch resources
kubectl get pods -w
```

## 🤝 Contributing

Found an issue or want to add a scenario? Contributions are welcome!

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/new-scenario`
3. **Make your changes**
4. **Test thoroughly** - Ensure the broken version fails and solution works
5. **Submit a pull request** with a clear description

### Contributing Guidelines

- Follow the existing scenario structure (`broken/` and `solution/` directories)
- Include a comprehensive README.md for each scenario
- Ensure Docker images are built and pushed to Docker Hub
- Test on at least one Kubernetes distribution (kind, minikube, or Docker Desktop)
- Update this main README.md if adding new scenarios

## 📝 License

MIT License - see [LICENSE](LICENSE) for details (if available)

## 🙏 Acknowledgments

Created for DevOps engineers, SREs, and developers learning Kubernetes troubleshooting.

**Special Thanks:**
- Kubernetes community for excellent documentation
- Docker Hub for hosting container images
- All contributors and testers

## 📞 Support

- **Issues**: Open an [issue on GitHub](https://github.com/vellankikoti/k8s-masterclass/issues)
- **Questions**: Check scenario-specific README files first
- **Docker Hub**: [vellankikoti/k8s-masterclass-*](https://hub.docker.com/u/vellankikoti)

---

## 🚀 Ready to Start?

**Beginner?** Start with [Scenario 1: CrashLoopBackOff](scenarios/01-crashloop-backoff/) 🎯

**Experienced?** Jump to any scenario that interests you!

**Want to build images?** Check out [BUILD_AND_TEST.md](BUILD_AND_TEST.md) 📦

---

**Happy Troubleshooting!** 🎉
