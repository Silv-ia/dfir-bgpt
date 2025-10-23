# Edit

import os
import json
from pathlib import Path

def reconstruct_image(image_dir: Path, output_path: Path, repaired_dir: Path = None):
    """
    Reassemble a JPEG file from header, (repaired) body chunks, and trailer.

    Args:
        image_dir (Path): Folder containing header.bin, trailer.bin, and body_chunks/.
        output_path (Path): Path to write the reconstructed JPEG.
        repaired_dir (Path, optional): 
            Directory with repaired chunk files. If None, uses the original body_chunks.
    """
    header_path = image_dir / "header.bin"
    trailer_path = image_dir / "trailer.bin"
    chunks_dir = repaired_dir if repaired_dir else (image_dir / "body_chunks")

    # --- Load header and trailer ---
    header = header_path.read_bytes()
    trailer = trailer_path.read_bytes()

    # --- Load metadata ---
    meta_path = chunks_dir / "meta.json"
    with open(meta_path, "r") as f:
        meta = json.load(f)
    chunk_size = meta["chunk_size"]
    last_chunk_len = meta["last_chunk_len"]
    num_chunks = meta["num_chunks"]

    # --- Concatenate body chunks ---
    body_bytes = bytearray()
    for i in range(num_chunks):
        chunk_file = chunks_dir / f"chunk_{i:04d}.bin"
        if not chunk_file.exists():
            raise FileNotFoundError(f"Missing chunk: {chunk_file}")
        chunk = chunk_file.read_bytes()
        body_bytes.extend(chunk)

    # --- Remove zero padding on last chunk ---
    total_expected_len = (num_chunks - 1) * chunk_size + last_chunk_len
    body_bytes = body_bytes[:total_expected_len]

    # --- Combine and write final JPEG ---
    full_jpeg = header + b'\xFF\xDA' + body_bytes + b'\xFF\xD9'
    output_path.write_bytes(full_jpeg)
    print(f"✅ Reconstructed image saved to: {output_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Reassemble a JPEG from header, chunks, and trailer.")
    parser.add_argument("--image_dir", type=Path, required=True, help="Path to the image_XXXX directory.")
    parser.add_argument("--output", type=Path, required=True, help="Output JPEG path.")
    parser.add_argument("--repaired_dir", type=Path, help="Path to repaired chunks (optional).")
    args = parser.parse_args()

    reconstruct_image(args.image_dir, args.output, args.repaired_dir)
