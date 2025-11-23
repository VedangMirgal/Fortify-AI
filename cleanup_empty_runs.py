# cleanup_empty_runs.py

import os

base = "runs"

for name in os.listdir(base):
    path = os.path.join(base, name)
    if os.path.isdir(path) and name.startswith("run_"):
        if not os.listdir(path):  # directory is empty
            print(f"Removing empty run directory: {path}")
            os.rmdir(path)
