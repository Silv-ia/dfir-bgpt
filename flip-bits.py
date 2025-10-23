### To run inside Kali with the bitflip tool 

### Commands: 
# python3 corrupt_dataset.py \
# --input /mnt/data/clean_chunks \
# --output /mnt/data/corrupted_chunks \
# --bits 0.1


import os
import subprocess
from pathlib import Path
import json

BITFLIP_CMD = "bitflip"  # command name only, since it's in PATH
CORRUPTION_PERCENT = 0.1  # percent of bits to flip (e.g., 0.1 = 0.1%)

def corrupt_chunk(chunk_path: Path, output_path: Path, bits=CORRUPTION_PERCENT):
    """Run bitflip spray on a single binary chunk."""
    cmd = [
        BITFLIP_CMD,
        "spray",
        f"--bits={bits}",
        f"--input={chunk_path}",
        f"--output={output_path}"
    ]
    subprocess.run(cmd, check=True)

def process_dataset(input_root: Path, output_root: Path, bits=CORRUPTION_PERCENT):
    """Iterate through dataset and corrupt all body chunks."""
    output_root.mkdir(parents=True, exist_ok=True)
    image_dirs = sorted([p for p in input_root.iterdir() if p.is_dir()])

    for img_idx, image_dir in enumerate(image_dirs, 1):
        print(f"[{img_idx}/{len(image_dirs)}] Processing {image_dir.name}")

        input_chunks_dir = image_dir / "body_chunks"
        output_chunks_dir = output_root / image_dir.name / "body_chunks"
        output_chunks_dir.mkdir(parents=True, exist_ok=True)

        meta_src = input_chunks_dir / "meta.json"
        if meta_src.exists():
            (output_chunks_dir / "meta.json").write_text(meta_src.read_text())

        # Corrupt all chunks
        for chunk_file in sorted(input_chunks_dir.glob("chunk_*.bin")):
            output_file = output_chunks_dir / chunk_file.name
            corrupt_chunk(chunk_file, output_file, bits=bits)

        # Copy header/trailer unchanged
        for name in ["header.bin", "trailer.bin"]:
            src = image_dir / name
            dst = output_root / image_dir.name / name
            if src.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(src.read_bytes())

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Automate bitflip corruption across dataset.")
    parser.add_argument("--input", type=Path, required=True, help="Path to clean dataset directory.")
    parser.add_argument("--output", type=Path, required=True, help="Path to save corrupted dataset.")
    parser.add_argument("--bits", type=float, default=0.1, help="Percentage of bits to flip (e.g. 0.1 = 0.1%).")

    args = parser.parse_args()

    process_dataset(args.input, args.output, bits=args.bits)
