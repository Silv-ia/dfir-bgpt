import math
import os
import random
import re
import sys

### Create the dict structure under /dataset
# /image0001
# - header.bin
# - tail.bin 
# /body
# - chunk1
# - chunk2
# ...
# - meta.json

# meta.json: len of body, #chunks, ch size, last chunk len

### Use 
# python create-dataset.py --input ./test-chunk --output ./chunked

import json
from pathlib import Path

CHUNK_SIZE = 4096

# Find the indx for SOS and EOI. 
def find_markers(data: bytes):
    """Find Start of Scan (SOS) and End of Image (EOI) markers."""
    sos_marker = b'\xFF\xDA'
    eoi_marker = b'\xFF\xD9'
    sos_idx = data.find(sos_marker)
    eoi_idx = data.rfind(eoi_marker)

    if sos_idx == -1 or eoi_idx == -1:
        raise ValueError("Invalid JPEG: missing SOS or EOI marker")

    # Include markers themselves
    sos_end = sos_idx + len(sos_marker)
    eoi_start = eoi_idx
    return sos_idx, sos_end, eoi_start, eoi_start + len(eoi_marker)


def extract_parts(file_path: Path):
    """Split JPEG into header, body, and trailer sections."""
    data = file_path.read_bytes()
    sos_idx, sos_end, eoi_start, eoi_end = find_markers(data)

    header = data[:sos_idx]
    body = data[sos_end:eoi_start]
    trailer = data[eoi_start:eoi_end]

    return header, body, trailer


def chunk_and_pad(body: bytes, chunk_size=CHUNK_SIZE):
    """Split body into fixed-size chunks with zero padding."""
    body_len = len(body)
    num_chunks = math.ceil(body_len / chunk_size)
    last_chunk_len = body_len % chunk_size or chunk_size

    chunks = []
    for i in range(num_chunks):
        start = i * chunk_size
        end = start + chunk_size
        chunk = body[start:end]
        if len(chunk) < chunk_size:
            chunk += b'\x00' * (chunk_size - len(chunk))
        chunks.append(chunk)

    meta = {
        "bod_len": body_len,
        "size": chunk_size,
        "nr_chunks": num_chunks,
        "chunk_len": last_chunk_len
    }

    return chunks, meta


def save_chunks(base_dir: Path, header: bytes, trailer: bytes, chunks, meta):
    """Save header, trailer, chunks, and metadata."""
    base_dir.mkdir(parents=True, exist_ok=True)
    (base_dir / "body").mkdir(exist_ok=True)

    # Write header and trailer
    (base_dir / "header.bin").write_bytes(header)
    (base_dir / "trailer.bin").write_bytes(trailer)

    # Write chunks
    for i, chunk in enumerate(chunks):
        chunk_name = f"chunk_{i:04d}.bin"
        (base_dir / "body" / chunk_name).write_bytes(chunk)

    # Write metadata
    with open(base_dir / "body" / "meta.json", "w") as f:
        json.dump(meta, f, indent=2)


def process_dataset(input_dir: Path, output_dir: Path):
    """Process all JPEGs in a folder into structured chunks."""
    output_dir.mkdir(parents=True, exist_ok=True)
    jpeg_files = sorted(list(input_dir.glob("*.jpg")) + list(input_dir.glob("*.jpeg")))

    for idx, file_path in enumerate(jpeg_files, 1):
        print(f"[{idx}/{len(jpeg_files)}] Processing {file_path.name}")
        header, body, trailer = extract_parts(file_path)
        chunks, meta = chunk_and_pad(body)
        image_dir = output_dir / f"image_{idx:04d}"
        save_chunks(image_dir, header, trailer, chunks, meta)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Prepare JPEG dataset into header/body chunks.")
    parser.add_argument("--input", type=Path, required=True, help="Folder with original JPEGs")
    parser.add_argument("--output", type=Path, required=True, help="Output dataset folder")

    args = parser.parse_args()
    process_dataset(args.input, args.output)
