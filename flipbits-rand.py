### Different levels of corruption all in one dataset. 

import os
import shutil
import subprocess
import random
import json
from pathlib import Path

BITFLIP_CMD = "bitflip"

# Define corruption levels (in percent)
CORRUPTION_LEVELS = [0.05, 0.1, 0.2, 0.3, 0.5]
LEVEL_WEIGHTS = [10, 20, 30, 25, 15]  # probability distribution

def choose_corruption_level():
    """Randomly pick a corruption severity."""
    return random.choices(CORRUPTION_LEVELS, weights=LEVEL_WEIGHTS, k=1)[0]

def corrupt_chunk(chunk_path: Path, percent: float):
    """Run bitflip spray on a single binary chunk (modifies in place)."""
    cmd = [BITFLIP_CMD, "spray", f"percent:{percent}", str(chunk_path)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Bitflip failed on {chunk_path}")
        print("stderr:", result.stderr.strip())
        raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)

def corrupt_dataset(input_root: Path, output_root: Path, log_path: Path):
    """Duplicate dataset once and corrupt each image at a random severity."""
    input_root = input_root.resolve()
    output_root = output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    image_dirs = sorted([p for p in input_root.iterdir() if p.is_dir()])
    log = {}

    print(f"Found {len(image_dirs)} images to process...\n")

    for idx, image_dir in enumerate(image_dirs, 1):
        level = choose_corruption_level()
        log[image_dir.name] = level
        print(f"[{idx}/{len(image_dirs)}] {image_dir.name} → {level:.2f}% corruption")

        output_image_dir = output_root / image_dir.name
        shutil.copytree(image_dir, output_image_dir, dirs_exist_ok=True)

        body_dir = output_image_dir / "body"
        if not body_dir.exists():
            print(f"Skipping {image_dir.name}, no 'body' directory found.")
            continue

        for chunk_file in sorted(body_dir.glob("chunk_*.bin")):
            corrupt_chunk(chunk_file, percent=level)

    # Save mapping of image → corruption level
    with open(log_path, "w") as f:
        json.dump(log, f, indent=2)
    print(f"\nDone. Log saved to {log_path}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Randomly corrupt dataset once with different severity levels.")
    parser.add_argument("--input", type=Path, required=True, help="Path to clean dataset.")
    parser.add_argument("--output", type=Path, required=True, help="Path to save corrupted dataset.")
    parser.add_argument("--log", type=Path, default="corruption_log.json", help="Path to save corruption mapping.")
    args = parser.parse_args()

    corrupt_dataset(args.input, args.output, log_path=args.log)
