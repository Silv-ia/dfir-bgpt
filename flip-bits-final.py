## different level of corruption
# some clean bits
# training and test split (not necessary...)
## Use on train-test + training-images

import os
import shutil
import subprocess
import random
import json
from pathlib import Path

BITFLIP_CMD = "bitflip"

# Corruption configuration
CORRUPTION_LEVELS = [0.05, 0.1, 0.2, 0.3, 0.5]
LEVEL_WEIGHTS = [10, 20, 30, 25, 15]  # probability distribution
CLEAN_RATIO = 0.1  # 10% of chunks remain clean → clean->clean examples

def choose_corruption_level():
    """Randomly pick a corruption severity."""
    return random.choices(CORRUPTION_LEVELS, weights=LEVEL_WEIGHTS, k=1)[0]

def corrupt_file(src: Path, dst: Path, percent: float):
    """Run bitflip spray on a file and save output to dst."""
    shutil.copy(src, dst)
    cmd = [BITFLIP_CMD, "spray", f"percent:{percent}", str(dst)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Bitflip failed on {src.name}")
        print("stderr:", result.stderr.strip())
        raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)

def build_bgpt_dataset(input_root: Path, output_root: Path, log_path: Path):
    """
    Build a dataset compatible with bGPT:
    - .input = corrupted bytes
    - .output = clean bytes
    """
    output_root.mkdir(parents=True, exist_ok=True)
    all_chunks = []
    log = {}

    image_dirs = sorted([p for p in input_root.iterdir() if p.is_dir()])
    print(f"Found {len(image_dirs)} image folders to process...\n")

    for idx, image_dir in enumerate(image_dirs, 1):
        body_dir = image_dir / "body"
        if not body_dir.exists():
            print(f"Skipping {image_dir.name}, no 'body' directory found.")
            continue

        for chunk_file in sorted(body_dir.glob("chunk_*.bin")):
            base = f"{image_dir.name}_{chunk_file.stem}"
            out_input = output_root / f"{base}.input"
            out_output = output_root / f"{base}.output"

            # Always copy clean version for output
            shutil.copy(chunk_file, out_output)

            # Decide if this chunk should be corrupted or kept clean
            if random.random() < CLEAN_RATIO:
                # clean->clean pair
                shutil.copy(chunk_file, out_input)
                log[base] = 0.0
            else:
                level = choose_corruption_level()
                corrupt_file(chunk_file, out_input, percent=level)
                log[base] = level

        print(f"[{idx}/{len(image_dirs)}] Processed {image_dir.name}")

    with open(log_path, "w") as f:
        json.dump(log, f, indent=2)
    print(f"\n✅ Dataset ready at {output_root}")
    print(f"   Log saved to {log_path}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create bGPT-compatible corruption dataset (.input/.output).")
    parser.add_argument("--input", type=Path, required=True, help="Path to clean dataset.")
    parser.add_argument("--output", type=Path, required=True, help="Path to save bGPT dataset.")
    parser.add_argument("--log", type=Path, default="corruption_log.json", help="Path to save corruption mapping.")
    args = parser.parse_args()

    build_bgpt_dataset(args.input, args.output, args.log)