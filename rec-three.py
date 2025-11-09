from pathlib import Path

def reconstruct_jpeg(header_path: Path, body_path: Path, trailer_path: Path, output_path: Path):
    """Reconstruct a JPEG from header, body, and trailer binary files."""
    header = header_path.read_bytes()
    body = body_path.read_bytes()
    trailer = trailer_path.read_bytes()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(header)
        f.write(body)
        f.write(trailer)

    print(f"JPEG reconstructed and saved to {output_path}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Reconstruct a JPEG from header/body/trailer binaries.")
    parser.add_argument("--header", type=Path, required=True, help="Path to header.bin")
    parser.add_argument("--body", type=Path, required=True, help="Path to body.bin")
    parser.add_argument("--trailer", type=Path, required=True, help="Path to trailer.bin")
    parser.add_argument("--output", type=Path, required=True, help="Output JPEG file path")
    args = parser.parse_args()

    reconstruct_jpeg(args.header, args.body, args.trailer, args.output)
