#!/usr/bin/env python3
"""
Universal Build and Push Script for K8s Workshop
Works on Windows, macOS, Linux - anywhere Python is installed
"""

import subprocess
import sys
import os
from pathlib import Path

# Configuration
DOCKER_USER = "vellankikoti"
VERSION = "v1.0"
REPO_PREFIX = "k8s-masterclass"

# Scenarios to build
SCENARIOS = [
    ("crashloop", "01-crashloop-backoff/app"),
    ("webapp", "03-port-mismatch/app"),
    ("config-app", "04-missing-configmap/app"),
    ("rbac-app", "05-rbac-forbidden/app"),
    ("memory-hog", "06-oom-killed/app"),
    ("health-app", "07-probe-failure/app"),
    ("netpol-client", "08-network-policy/app-client"),
    ("netpol-server", "08-network-policy/app-server"),
    ("storage-app", "09-pvc-pending/app"),
    ("init-app", "10-init-container-failure/app"),
    ("init-wait", "10-init-container-failure/init-wait"),
    ("redis", "10-init-container-failure/redis"),
]

def print_header(message):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {message}")
    print("=" * 60 + "\n")

def run_command(cmd, description):
    """Run a shell command and handle errors"""
    print(f"▶ {description}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ {description} - SUCCESS\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"Error: {e.stderr}\n")
        return False

def check_docker():
    """Check if Docker is running"""
    print_header("Checking Prerequisites")

    # Check Docker
    try:
        subprocess.run(["docker", "version"], capture_output=True, check=True)
        print("✅ Docker is running")
    except:
        print("❌ Docker is not running or not installed")
        print("Please start Docker Desktop and try again")
        sys.exit(1)

    # Check Docker login
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            check=True
        )
        if DOCKER_USER not in result.stdout:
            print(f"\n⚠️  Not logged in to Docker Hub as {DOCKER_USER}")
            print("Attempting to log in...")
            subprocess.run(["docker", "login", "-u", DOCKER_USER], check=True)
        else:
            print(f"✅ Logged in to Docker Hub as {DOCKER_USER}")
    except:
        print("⚠️  Could not verify Docker Hub login")
        print("You may need to run: docker login -u", DOCKER_USER)

def build_image(scenario_name, scenario_path):
    """Build a Docker image"""
    image_name = f"{DOCKER_USER}/{REPO_PREFIX}-{scenario_name}"
    tag_v1 = f"{image_name}:{VERSION}"
    tag_latest = f"{image_name}:latest"

    # Get absolute path
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    build_context = repo_root / "scenarios" / scenario_path

    if not build_context.exists():
        print(f"❌ Directory not found: {build_context}")
        return False

    # Build command
    build_cmd = f'docker build -t "{tag_v1}" -t "{tag_latest}" "{build_context}"'

    return run_command(build_cmd, f"Building {scenario_name}")

def push_image(scenario_name):
    """Push a Docker image to Docker Hub"""
    image_name = f"{DOCKER_USER}/{REPO_PREFIX}-{scenario_name}"

    # Push v1.0 tag
    push_cmd_v1 = f'docker push "{image_name}:{VERSION}"'
    if not run_command(push_cmd_v1, f"Pushing {scenario_name}:{VERSION}"):
        return False

    # Push latest tag
    push_cmd_latest = f'docker push "{image_name}:latest"'
    return run_command(push_cmd_latest, f"Pushing {scenario_name}:latest")

def main():
    """Main build and push workflow"""
    print_header("K8s Workshop - Build and Push All Images")
    print(f"Docker User: {DOCKER_USER}")
    print(f"Version: {VERSION}")
    print(f"Total Images: {len(SCENARIOS)}")

    # Check prerequisites
    check_docker()

    # Build and push all images
    print_header("Building and Pushing Images")

    success_count = 0
    failed_scenarios = []

    for idx, (scenario_name, scenario_path) in enumerate(SCENARIOS, 1):
        print(f"\n[{idx}/{len(SCENARIOS)}] Processing: {scenario_name}")
        print("-" * 60)

        # Build
        if not build_image(scenario_name, scenario_path):
            failed_scenarios.append(scenario_name)
            print(f"⚠️  Skipping push for {scenario_name} due to build failure\n")
            continue

        # Push
        if not push_image(scenario_name):
            failed_scenarios.append(scenario_name)
            print(f"⚠️  Push failed for {scenario_name}\n")
            continue

        success_count += 1
        print(f"✅ Successfully built and pushed {scenario_name}\n")

    # Summary
    print_header("Build Summary")
    print(f"Total scenarios: {len(SCENARIOS)}")
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {len(failed_scenarios)}")

    if failed_scenarios:
        print("\nFailed scenarios:")
        for scenario in failed_scenarios:
            print(f"  - {scenario}")
        sys.exit(1)
    else:
        print("\n🎉 All images built and pushed successfully!")
        print("\nImages are now available at:")
        for scenario_name, _ in SCENARIOS:
            print(f"  docker.io/{DOCKER_USER}/{REPO_PREFIX}-{scenario_name}:{VERSION}")
        print("\n✅ Ready to test on Kubernetes!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Build cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
