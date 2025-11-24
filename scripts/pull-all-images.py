#!/usr/bin/env python3
"""
Universal Pull Script for K8s Workshop Images
Works on Windows, macOS, Linux - anywhere Python is installed
Pulls all workshop images from Docker Hub for offline use
"""

import subprocess
import sys
import os
from pathlib import Path

# Configuration
DOCKER_USER = "vellankikoti"
VERSION = "v1.0"
REPO_PREFIX = "k8s-masterclass"

# Scenarios to pull
SCENARIOS = [
    "crashloop",
    "webapp",
    "config-app",
    "rbac-app",
    "memory-hog",
    "health-app",
    "netpol-client",
    "netpol-server",
    "storage-app",
    "init-app",
    "init-wait",
    "redis",
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
        print("Please start Docker and try again")
        sys.exit(1)

    # Check platform
    try:
        result = subprocess.run(
            ["docker", "version", "--format", "{{.Server.Os}}/{{.Server.Arch}}"],
            capture_output=True,
            text=True,
            check=True
        )
        platform = result.stdout.strip()
        print(f"✅ Docker platform: {platform}")
        print("   (Multi-platform images support linux/amd64 and linux/arm64)")
    except:
        print("⚠️  Could not detect platform, but will continue")

def pull_image(scenario_name, tag):
    """Pull a Docker image from Docker Hub"""
    image_name = f"{DOCKER_USER}/{REPO_PREFIX}-{scenario_name}:{tag}"
    pull_cmd = f'docker pull "{image_name}"'

    return run_command(pull_cmd, f"Pulling {scenario_name}:{tag}")

def main():
    """Main pull workflow"""
    print_header("K8s Workshop - Pull All Images")
    print(f"Docker User: {DOCKER_USER}")
    print(f"Version: {VERSION}")
    print(f"Total Images: {len(SCENARIOS)}")
    print("\nℹ️  All images are multi-platform (linux/amd64, linux/arm64)")
    print("   Docker will automatically pull the correct version for your system\n")

    # Check prerequisites
    check_docker()

    # Pull all images
    print_header("Pulling Images from Docker Hub")

    success_count = 0
    failed_scenarios = []

    for idx, scenario_name in enumerate(SCENARIOS, 1):
        print(f"\n[{idx}/{len(SCENARIOS)}] Processing: {scenario_name}")
        print("-" * 60)

        # Pull v1.0 tag
        if not pull_image(scenario_name, VERSION):
            failed_scenarios.append(f"{scenario_name}:{VERSION}")
            print(f"⚠️  Failed to pull {scenario_name}:{VERSION}\n")
            # Continue to try latest tag

        # Pull latest tag
        if not pull_image(scenario_name, "latest"):
            failed_scenarios.append(f"{scenario_name}:latest")
            print(f"⚠️  Failed to pull {scenario_name}:latest\n")
            continue

        success_count += 1
        print(f"✅ Successfully pulled {scenario_name}\n")

    # Summary
    print_header("Pull Summary")
    print(f"Total scenarios: {len(SCENARIOS)}")
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {len(failed_scenarios)}")

    if failed_scenarios:
        print("\nFailed images:")
        for image in failed_scenarios:
            print(f"  - {image}")

        print("\n⚠️  Some images failed to pull. Common reasons:")
        print("  1. Images don't exist on Docker Hub")
        print("  2. Network connectivity issues")
        print("  3. Images not built with multi-platform support")
        print("\nℹ️  Run build-and-push-all.py to build and push images")
        sys.exit(1)
    else:
        print("\n🎉 All images pulled successfully!")
        print("\nImages are now available locally:")
        for scenario_name in SCENARIOS:
            print(f"  docker.io/{DOCKER_USER}/{REPO_PREFIX}-{scenario_name}:{VERSION}")
        print("\n✅ Ready to use with Kubernetes!")
        print("\nTo verify, run: docker images | grep k8s-masterclass")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Pull cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
