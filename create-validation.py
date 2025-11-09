import os
from pathlib import Path

# Find SOS and EOI markers
def find_markers(data: bytes):
    sos_marker = b'\xFF\xDA'
    eoi_marker = b'\xFF\xD9'
    sos_idx = data.find(sos_marker)
    eoi_idx = data.rfind(eoi_marker)

    if sos_idx == -1 or eoi_idx == -1:
        raise ValueError("Invalid JPEG: missing SOS or EOI marker")

    sos_end = sos_idx + len(sos_marker)
    eoi_start = eoi_idx
    eoi_end = eoi_start + len(eoi_marker)
    return sos_idx, sos_end, eoi_start, eoi_end

# Extract header, body, trailer
def extract_parts(file_path: Path):
    data = file_path.read_bytes()
    sos_idx, sos_end, eoi_start, eoi_end = find_markers(data)

    # SOS segment length (2 bytes after FFDA gives length of scan header)
    sos_length = int.from_bytes(data[sos_idx+2:sos_idx+4], byteorder='big')
    sos_end = sos_idx + 2 + sos_length  # include full SOS header

    header = data[:sos_end]
    body = data[sos_end:eoi_start]
    trailer = data[eoi_start:eoi_end]
    return header, body, trailer

# Save the parts as separate .bin files
def save_parts(output_dir: Path, header: bytes, body: bytes, trailer: bytes):
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "header.bin").write_bytes(header)
    (output_dir / "body.bin").write_bytes(body)
    (output_dir / "trailer.bin").write_bytes(trailer)

# Process all JPEGs in a folder
def process_dataset(input_dir: Path, output_dir: Path):
    jpeg_files = sorted(list(input_dir.glob("*.jpg")) + list(input_dir.glob("*.jpeg")))
    for idx, file_path in enumerate(jpeg_files, 1):
        print(f"[{idx}/{len(jpeg_files)}] Processing {file_path.name}")
        header, body, trailer = extract_parts(file_path)
        image_dir = output_dir / f"{file_path.stem}"  # keep original filename
        save_parts(image_dir, header, body, trailer)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Split JPEGs into header, body, and trailer.")
    parser.add_argument("--input", type=Path, required=True, help="Folder with original JPEGs")
    parser.add_argument("--output", type=Path, required=True, help="Output folder for split binaries")
    args = parser.parse_args()
    process_dataset(args.input, args.output)
