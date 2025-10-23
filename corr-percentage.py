### Compare original with corrupted or repaired 
# to see if corruption is correct, or 
# to see how many percent are correct after repair! 

from pathlib import Path

def bit_diff_stats(original: Path, test: Path):
    """Compare two binary files bit by bit."""
    orig_bytes = original.read_bytes()
    test_bytes = test.read_bytes()

    # Ensure equal length for fair comparison
    if len(orig_bytes) != len(test_bytes):
        min_len = min(len(orig_bytes), len(test_bytes))
        print(f"⚠️ File lengths differ: truncating to {min_len} bytes for comparison.")
        orig_bytes = orig_bytes[:min_len]
        test_bytes = test_bytes[:min_len]

    total_bits = len(orig_bytes) * 8
    diff_bits = 0

    # Bitwise comparison using XOR
    for b1, b2 in zip(orig_bytes, test_bytes):
        diff_bits += (b1 ^ b2).bit_count()

    same_bits = total_bits - diff_bits
    match_percent = 100 * same_bits / total_bits

    print(f"✅ Compared {total_bits:,} bits")
    print(f"   • Matching bits: {same_bits:,} ({match_percent:.6f}%)")
    print(f"   • Different bits: {diff_bits:,} ({100 - match_percent:.6f}%)")
    return match_percent, diff_bits, total_bits


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Compare bit-level differences between two binary files.")
    parser.add_argument("--original", type=Path, required=True, help="Path to original file.")
    parser.add_argument("--test", type=Path, required=True, help="Path to corrupted or repaired file.")
    args = parser.parse_args()

    bit_diff_stats(args.original, args.test)
