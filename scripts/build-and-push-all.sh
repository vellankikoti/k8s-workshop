#!/bin/bash

###########################################
# K8s Workshop - Build and Push All Images
# Works on macOS, Linux, WSL
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

# Scenarios array (name:path)
declare -a SCENARIOS=(
    "crashloop:01-crashloop-backoff/app"
    "webapp:03-port-mismatch/app"
    "config-app:04-missing-configmap/app"
    "rbac-app:05-rbac-forbidden/app"
    "memory-hog:06-oom-killed/app"
    "health-app:07-probe-failure/app"
    "netpol-client:08-network-policy/app-client"
    "netpol-server:08-network-policy/app-server"
    "storage-app:09-pvc-pending/app"
    "init-app:10-init-container-failure/app"
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
        echo "Please start Docker Desktop and try again"
        exit 1
    fi
    print_success "Docker is running"

    # Check Docker Hub login
    if ! docker info 2>/dev/null | grep -q "Username: $DOCKER_USER"; then
        print_warning "Not logged in to Docker Hub as $DOCKER_USER"
        echo "Attempting to log in..."
        docker login -u "$DOCKER_USER"
    else
        print_success "Logged in to Docker Hub as $DOCKER_USER"
    fi
}

build_image() {
    local scenario_name="$1"
    local scenario_path="$2"
    local image_name="$DOCKER_USER/$REPO_PREFIX-$scenario_name"

    # Get script directory and repo root
    local script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    local repo_root="$(dirname "$script_dir")"
    local build_context="$repo_root/scenarios/$scenario_path"

    if [ ! -d "$build_context" ]; then
        print_error "Directory not found: $build_context"
        return 1
    fi

    print_info "Building $scenario_name from $scenario_path"

    # Build with both tags
    if docker build \
        -t "$image_name:$VERSION" \
        -t "$image_name:latest" \
        "$build_context"; then
        print_success "Built $scenario_name"
        return 0
    else
        print_error "Failed to build $scenario_name"
        return 1
    fi
}

push_image() {
    local scenario_name="$1"
    local image_name="$DOCKER_USER/$REPO_PREFIX-$scenario_name"

    print_info "Pushing $scenario_name:$VERSION"
    if docker push "$image_name:$VERSION"; then
        print_success "Pushed $scenario_name:$VERSION"
    else
        print_error "Failed to push $scenario_name:$VERSION"
        return 1
    fi

    print_info "Pushing $scenario_name:latest"
    if docker push "$image_name:latest"; then
        print_success "Pushed $scenario_name:latest"
    else
        print_error "Failed to push $scenario_name:latest"
        return 1
    fi

    return 0
}

main() {
    print_header "K8s Workshop - Build and Push All Images"
    echo "Docker User: $DOCKER_USER"
    echo "Version: $VERSION"
    echo "Total Images: ${#SCENARIOS[@]}"
    echo ""

    # Check prerequisites
    check_prerequisites

    # Build and push all images
    print_header "Building and Pushing Images"

    local success_count=0
    local failed_scenarios=()
    local total=${#SCENARIOS[@]}

    for scenario_info in "${SCENARIOS[@]}"; do
        local scenario_name=$(echo "$scenario_info" | cut -d: -f1)
        local scenario_path=$(echo "$scenario_info" | cut -d: -f2)

        success_count=$((success_count + 1))
        echo ""
        echo -e "${BLUE}[$success_count/$total] Processing: $scenario_name${NC}"
        echo "------------------------------------------------------------"

        # Build
        if ! build_image "$scenario_name" "$scenario_path"; then
            failed_scenarios+=("$scenario_name")
            print_warning "Skipping push for $scenario_name due to build failure"
            continue
        fi

        # Push
        if ! push_image "$scenario_name"; then
            failed_scenarios+=("$scenario_name")
            print_warning "Push failed for $scenario_name"
            continue
        fi

        print_success "Successfully built and pushed $scenario_name"
        echo ""
    done

    # Summary
    print_header "Build Summary"
    echo "Total scenarios: $total"
    echo -e "${GREEN}✅ Successful: $((total - ${#failed_scenarios[@]}))${NC}"
    echo -e "${RED}❌ Failed: ${#failed_scenarios[@]}${NC}"

    if [ ${#failed_scenarios[@]} -gt 0 ]; then
        echo ""
        echo "Failed scenarios:"
        for scenario in "${failed_scenarios[@]}"; do
            echo "  - $scenario"
        done
        exit 1
    else
        echo ""
        echo -e "${GREEN}🎉 All images built and pushed successfully!${NC}"
        echo ""
        echo "Images are now available at:"
        for scenario_info in "${SCENARIOS[@]}"; do
            local scenario_name=$(echo "$scenario_info" | cut -d: -f1)
            echo "  docker.io/$DOCKER_USER/$REPO_PREFIX-$scenario_name:$VERSION"
        done
        echo ""
        print_success "Ready to test on Kubernetes!"
    fi
}

# Handle Ctrl+C
trap 'echo -e "\n${YELLOW}⚠️  Build cancelled by user${NC}"; exit 1' INT

# Run main
main
