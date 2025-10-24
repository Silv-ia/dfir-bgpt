### Part I, select 5k images
import zipfile

zip_path = r"C:\Users\laira\Downloads\archive.zip"
output_dir = r"C:\Users\laira\Documents\GitHub\dfir-bgpt"
os.makedirs(output_dir, exist_ok=True)

with zipfile.ZipFile(zip_path, 'r') as z:
    all_files = z.namelist()  # All filenames in the zip
    sample_files = random.sample(all_files, 5000)  # Pick 5k files

    for i, f in enumerate(sample_files, 1):
        z.extract(f, output_dir)
        if i % 500 == 0:
            print(f"Extracted {i} / 5000")

print("5,000 images extracted to:", output_dir)

### 



import os
import shutil
import subprocess
import random
import json
from pathlib import Path
from math import floor

BITFLIP_CMD = "bitflip"

# Corruption configuration
CORRUPTION_LEVELS = [0.05, 0.1, 0.2, 0.3, 0.5]  # corruption severities (in %)
LEVEL_WEIGHTS = [10, 20, 30, 25, 15]             # relative probabilities
CLEAN_RATIO = 0.1                                # 10% clean→clean pairs
TEST_SPLIT = 0.1                                 # 10% test data

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
      - split into training/ and test/
    """
    train_dir = output_root / "training"
    test_dir = output_root / "test"
    for d in (train_dir, test_dir):
        d.mkdir(parents=True, exist_ok=True)

    all_pairs = []
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
            all_pairs.append((chunk_file, base))

        print(f"[{idx}/{len(image_dirs)}] Indexed {image_dir.name}")

    # Shuffle for random split
    random.shuffle(all_pairs)
    split_idx = floor(len(all_pairs) * (1 - TEST_SPLIT))
    train_pairs = all_pairs[:split_idx]
    test_pairs = all_pairs[split_idx:]

    print(f"\nTotal chunks: {len(all_pairs)}")
    print(f" → Training: {len(train_pairs)}")
    print(f" → Test: {len(test_pairs)}\n")

    def process_split(pairs, out_dir, split_name):
        for idx, (chunk_file, base) in enumerate(pairs, 1):
            out_input = out_dir / f"{base}.input"
            out_output = out_dir / f"{base}.output"

            # Always copy clean version for .output
            shutil.copy(chunk_file, out_output)

            if random.random() < CLEAN_RATIO:
                shutil.copy(chunk_file, out_input)
                log[f"{split_name}/{base}"] = 0.0
            else:
                level = choose_corruption_level()
                corrupt_file(chunk_file, out_input, percent=level)
                log[f"{split_name}/{base}"] = level

            if idx % 500 == 0:
                print(f"[{split_name}] Processed {idx}/{len(pairs)} chunks...")

    # Process both splits
    process_split(train_pairs, train_dir, "train")
    process_split(test_pairs, test_dir, "test")

    # Save log
    with open(log_path, "w") as f:
        json.dump(log, f, indent=2)

    print(f"\nDataset ready:")
    print(f"  Training dir: {train_dir}")
    print(f"  Test dir: {test_dir}")
    print(f"  Log file: {log_path}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create bGPT-compatible corruption dataset (.input/.output) with automatic split.")
    parser.add_argument("--input", type=Path, required=True, help="Path to clean dataset (chunked images).")
    parser.add_argument("--output", type=Path, required=True, help="Path to save final dataset with train/test split.")
    parser.add_argument("--log", type=Path, default="corruption_log.json", help="Path to save corruption mapping.")
    args = parser.parse_args()

    build_bgpt_dataset(args.input, args.output, args.log)

#########################

