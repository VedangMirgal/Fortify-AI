# run_utils.py

import os


def get_next_run_id() -> str:
    """
    Returns the next sequential run id as a zero-padded string, e.g. '001', '002', ...
    Looks at the existing 'runs/run_XXX' folders and picks max+1.
    """
    base_dir = "runs"
    os.makedirs(base_dir, exist_ok=True)

    existing = [
        d for d in os.listdir(base_dir)
        if d.startswith("run_") and os.path.isdir(os.path.join(base_dir, d))
    ]

    max_n = 0
    for d in existing:
        try:
            suffix = d.split("_", 1)[1]
            n = int(suffix)
            if n > max_n:
                max_n = n
        except Exception:
            continue

    next_n = max_n + 1
    return f"{next_n:03d}"
