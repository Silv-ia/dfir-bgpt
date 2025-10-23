### Also checks which correct bits were incorrectly flipped

def detailed_recovery_stats(original: Path, corrupted: Path, repaired: Path):
    o = original.read_bytes()
    c = corrupted.read_bytes()
    r = repaired.read_bytes()

    min_len = min(len(o), len(c), len(r))
    o, c, r = o[:min_len], c[:min_len], r[:min_len]

    flipped = recovered = false_changes = unchanged = 0

    for bo, bc, br in zip(o, c, r):
        diff_corrupt = bo ^ bc
        diff_repair = bo ^ br

        flipped += diff_corrupt.bit_count()
        recovered += (diff_corrupt & ~diff_repair).bit_count()  # flipped -> fixed
        false_changes += (~diff_corrupt & diff_repair).bit_count()  # clean -> altered

    total_bits = len(o) * 8
    print(f"Total bits: {total_bits:,}")
    print(f"Flipped by corruption: {flipped:,}")
    print(f"Recovered correctly: {recovered:,} ({100*recovered/flipped:.3f}%)")
    print(f"False changes (clean bits altered): {false_changes:,}")
