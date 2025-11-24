#!/usr/bin/env python3
"""
Kubernetes Masterclass - Scenario 1: CrashLoopBackOff
A simple Python app that requires an environment variable to run.
"""

import os
import sys
import time
from datetime import datetime

def main():
    print(f"[{datetime.now()}] Starting application...")

    # Check for required environment variable
    required_config = os.getenv('REQUIRED_CONFIG')

    if not required_config:
        print("ERROR: REQUIRED_CONFIG environment variable is not set!", file=sys.stderr)
        print("Application cannot start without proper configuration.", file=sys.stderr)
        sys.exit(1)

    print(f"[{datetime.now()}] Configuration loaded: {required_config}")
    print(f"[{datetime.now()}] Application started successfully!")

    # Keep the application running
    counter = 0
    while True:
        counter += 1
        print(f"[{datetime.now()}] Application is running... (heartbeat #{counter})")
        time.sleep(10)

if __name__ == "__main__":
    main()
