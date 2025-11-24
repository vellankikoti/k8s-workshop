# K8s Workshop Build & Pull Scripts

This directory contains scripts to build, push, and pull Docker images for the K8s Workshop scenarios.

## 🚀 Features

- **Multi-platform support**: All images are built for `linux/amd64` and `linux/arm64`
- **No more platform issues**: Works seamlessly on Intel/AMD and ARM (Apple Silicon, AWS Graviton, etc.)
- **Cross-platform scripts**: Available in both Python and Bash versions
- **Automated**: Build, tag, and push all images with a single command

## 📋 Prerequisites

- Docker Desktop (or Docker Engine with buildx support)
- Docker Hub account (for pushing images)
- Python 3.6+ (for `.py` scripts) OR Bash (for `.sh` scripts)

## 🛠️ Build and Push Scripts

### Python Version (Recommended - works everywhere)

```bash
# Make executable (first time only)
chmod +x scripts/build-and-push-all.py

# Build and push all images (multi-platform)
./scripts/build-and-push-all.py
```

### Bash Version (macOS, Linux, WSL)

```bash
# Make executable (first time only)
chmod +x scripts/build-and-push-all.sh

# Build and push all images (multi-platform)
./scripts/build-and-push-all.sh
```

### What it does:

1. ✅ Checks Docker and Docker buildx availability
2. ✅ Sets up multi-platform builder (creates if needed)
3. ✅ Verifies Docker Hub login
4. ✅ Builds images for **both** `linux/amd64` and `linux/arm64`
5. ✅ Tags with `v1.0` and `latest`
6. ✅ Pushes to Docker Hub

## 📥 Pull Scripts

Use these scripts to pull all pre-built images from Docker Hub (useful if images are already built).

### Python Version

```bash
# Make executable (first time only)
chmod +x scripts/pull-all-images.py

# Pull all images
./scripts/pull-all-images.py
```

### Bash Version

```bash
# Make executable (first time only)
chmod +x scripts/pull-all-images.sh

# Pull all images
./scripts/pull-all-images.sh
```

### What it does:

1. ✅ Checks Docker availability
2. ✅ Detects your platform (Docker will pull the right architecture)
3. ✅ Pulls both `v1.0` and `latest` tags for all scenarios
4. ✅ Provides detailed progress and summary

## 🎯 Scenarios Included

All scripts process these scenarios:

1. `crashloop` - CrashLoopBackOff demo
2. `webapp` - Port mismatch demo
3. `config-app` - Missing ConfigMap demo
4. `rbac-app` - RBAC forbidden demo
5. `memory-hog` - OOMKilled demo
6. `health-app` - Probe failure demo
7. `netpol-client` - Network policy client
8. `netpol-server` - Network policy server
9. `storage-app` - PVC pending demo
10. `init-app` - Init container failure demo
11. `init-wait` - Init wait container
12. `redis` - Redis for init demo

## 🔧 Configuration

Edit the configuration at the top of any script:

```python
# Python
DOCKER_USER = "vellankikoti"
VERSION = "v1.0"
REPO_PREFIX = "k8s-masterclass"
```

```bash
# Bash
DOCKER_USER="vellankikoti"
VERSION="v1.0"
REPO_PREFIX="k8s-masterclass"
```

## 🐛 Troubleshooting

### "no matching manifest for linux/amd64"

This error means images were built without multi-platform support. **Solution**: Use the updated scripts in this directory - they now use `docker buildx` with `--platform linux/amd64,linux/arm64`.

### Docker buildx not found

Update Docker Desktop to the latest version. Buildx is included by default in Docker Desktop 19.03+.

### Builder initialization failed

```bash
# Remove and recreate builder
docker buildx rm multiplatform
docker buildx create --name multiplatform --use
docker buildx inspect --bootstrap
```

### Pull fails with authentication error

```bash
# Login to Docker Hub
docker login -u vellankikoti
```

## 🎓 How It Works

### Traditional Build (OLD - single platform)
```bash
docker build -t image:tag .
docker push image:tag
```
❌ Only builds for your current platform (Intel or ARM)

### Multi-platform Build (NEW - works everywhere)
```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t image:tag \
  --push \
  .
```
✅ Builds for both Intel/AMD and ARM platforms
✅ Creates a manifest list that works on any platform
✅ Automatically selects the correct image when pulling

## 📚 Additional Resources

- [Docker Buildx Documentation](https://docs.docker.com/buildx/working-with-buildx/)
- [Multi-platform Images](https://docs.docker.com/build/building/multi-platform/)
- [Docker Hub](https://hub.docker.com/)

## 🤝 Contributing

To add a new scenario:

1. Add the scenario to the `SCENARIOS` list in all scripts
2. Ensure the Dockerfile exists in the correct path
3. Run the build script to test

## 📝 License

Part of the K8s Workshop materials.
