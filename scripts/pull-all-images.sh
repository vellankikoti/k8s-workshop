#!/bin/bash

###########################################
# K8s Workshop - Pull All Images
# Works on macOS, Linux, WSL
# Pulls all workshop images from Docker Hub
###########################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOCKER_USER="vellankikoti"
VERSION="v1.0"
REPO_PREFIX="k8s-masterclass"

# Scenarios to pull
declare -a SCENARIOS=(
    "crashloop"
    "webapp"
    "config-app"
    "rbac-app"
    "memory-hog"
    "health-app"
    "netpol-client"
    "netpol-server"
    "storage-app"
    "init-app"
    "init-wait"
    "redis"
)

print_header() {
    echo -e "\n${BLUE}============================================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}============================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}▶ $1${NC}"
}

check_prerequisites() {
    print_header "Checking Prerequisites"

    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi

    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running"
        echo "Please start Docker and try again"
        exit 1
    fi
    print_success "Docker is running"

    # Check platform
    local platform=$(docker version --format '{{.Server.Os}}/{{.Server.Arch}}' 2>/dev/null || echo "unknown")
    print_success "Docker platform: $platform"
    echo "   (Multi-platform images support linux/amd64 and linux/arm64)"
}

pull_image() {
    local scenario_name="$1"
    local tag="$2"
    local image_name="$DOCKER_USER/$REPO_PREFIX-$scenario_name:$tag"

    print_info "Pulling $scenario_name:$tag"

    if docker pull "$image_name"; then
        print_success "Pulled $scenario_name:$tag"
        return 0
    else
        print_error "Failed to pull $scenario_name:$tag"
        return 1
    fi
}

main() {
    print_header "K8s Workshop - Pull All Images"
    echo "Docker User: $DOCKER_USER"
    echo "Version: $VERSION"
    echo "Total Images: ${#SCENARIOS[@]}"
    echo ""
    echo "ℹ️  All images are multi-platform (linux/amd64, linux/arm64)"
    echo "   Docker will automatically pull the correct version for your system"
    echo ""

    # Check prerequisites
    check_prerequisites

    # Pull all images
    print_header "Pulling Images from Docker Hub"

    local success_count=0
    local failed_images=()
    local total=${#SCENARIOS[@]}

    for idx in "${!SCENARIOS[@]}"; do
        local scenario_name="${SCENARIOS[$idx]}"
        local current=$((idx + 1))

        echo ""
        echo -e "${BLUE}[$current/$total] Processing: $scenario_name${NC}"
        echo "------------------------------------------------------------"

        local scenario_success=true

        # Pull v1.0 tag
        if ! pull_image "$scenario_name" "$VERSION"; then
            failed_images+=("$scenario_name:$VERSION")
            scenario_success=false
        fi

        # Pull latest tag
        if ! pull_image "$scenario_name" "latest"; then
            failed_images+=("$scenario_name:latest")
            scenario_success=false
        fi

        if [ "$scenario_success" = true ]; then
            success_count=$((success_count + 1))
            print_success "Successfully pulled $scenario_name"
        fi

        echo ""
    done

    # Summary
    print_header "Pull Summary"
    echo "Total scenarios: $total"
    echo -e "${GREEN}✅ Successful: $success_count${NC}"
    echo -e "${RED}❌ Failed: ${#failed_images[@]}${NC}"

    if [ ${#failed_images[@]} -gt 0 ]; then
        echo ""
        echo "Failed images:"
        for image in "${failed_images[@]}"; do
            echo "  - $image"
        done
        echo ""
        print_warning "Some images failed to pull. Common reasons:"
        echo "  1. Images don't exist on Docker Hub"
        echo "  2. Network connectivity issues"
        echo "  3. Images not built with multi-platform support"
        echo ""
        echo "ℹ️  Run build-and-push-all.sh to build and push images"
        exit 1
    else
        echo ""
        echo -e "${GREEN}🎉 All images pulled successfully!${NC}"
        echo ""
        echo "Images are now available locally:"
        for scenario_name in "${SCENARIOS[@]}"; do
            echo "  docker.io/$DOCKER_USER/$REPO_PREFIX-$scenario_name:$VERSION"
        done
        echo ""
        print_success "Ready to use with Kubernetes!"
        echo ""
        echo "To verify, run: docker images | grep k8s-masterclass"
    fi
}

# Handle Ctrl+C
trap 'echo -e "\n${YELLOW}⚠️  Pull cancelled by user${NC}"; exit 1' INT

# Run main
main
