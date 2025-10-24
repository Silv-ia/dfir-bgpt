### To run inside Kali with the bitflip tool 

### Commands: 
# python3 flip-bits.py \
# --input /mnt/data/clean_chunks \
# --output /mnt/data/corrupted_chunks \
# --bits 0.1


import os
import shutil
import subprocess
from pathlib import Path

CORRUPTION_PERCENT = 0.3  # e.g. 0.3 = 0.3%
BITFLIP_CMD = "bitflip"

def corrupt_chunk(chunk_path: Path, bits=CORRUPTION_PERCENT):
    """Run bitflip spray on a single binary chunk (modifies in place)."""
    cmd = [BITFLIP_CMD, "spray", f"percent:{bits}", str(chunk_path)]
    print("Running:", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Bitflip failed on {chunk_path}")
        print("stderr:", result.stderr.strip())
        raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)


def process_dataset(input_root: Path, output_root: Path, bits=CORRUPTION_PERCENT):
    """Duplicate dataset and corrupt all body chunks."""
    output_root.mkdir(parents=True, exist_ok=True)
    image_dirs = sorted([p for p in input_root.iterdir() if p.is_dir()])

    for img_idx, image_dir in enumerate(image_dirs, 1):
        print(f"[{img_idx}/{len(image_dirs)}] Processing {image_dir.name}")

        # Duplicate directory structure
        output_image_dir = output_root / image_dir.name
        shutil.copytree(image_dir, output_image_dir, dirs_exist_ok=True)

        # Corrupt only body chunks
        body_dir = output_image_dir / "body"
        for chunk_file in sorted(body_dir.glob("chunk_*.bin")):
            corrupt_chunk(chunk_file, bits=bits)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Automate bitflip corruption across dataset.")
    parser.add_argument("--input", type=Path, required=True, help="Path to clean dataset directory.")
    parser.add_argument("--output", type=Path, required=True, help="Path to save corrupted dataset.")
    parser.add_argument("--bits", type=float, default=0.3, help="Percentage of bits to flip (e.g. 0.3 = 0.3%).")
    args = parser.parse_args()

    process_dataset(args.input, args.output, bits=args.bits)

