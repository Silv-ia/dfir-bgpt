import os
import random
import shutil
from pathlib import Path

# --- USER CONFIG ---
SOURCE_DIR = Path("images-5k")  # directory with all images
DEST_TRAIN = Path("training-images")
DEST_TEST = Path("train-test")
DEST_FINAL = Path("final-validation")

N_TRAIN = 4050
N_TEST = 450
N_FINAL = 500
EXTENSIONS = {".jpg", ".jpeg"}  # add others if needed

# --- MAIN LOGIC ---
def split_and_copy_images(src: Path):
    # Collect all image files
    all_images = [p for p in src.iterdir() if p.suffix.lower() in EXTENSIONS]
    total = len(all_images)
    print(f"Found {total} image files in {src}")

    required = N_TRAIN + N_TEST + N_FINAL
    if total < required:
        raise ValueError(f"Not enough images ({total}) for requested split ({required}).")

    # Shuffle images once
    random.shuffle(all_images)

    # Split
    train_imgs = all_images[:N_TRAIN]
    test_imgs = all_images[N_TRAIN:N_TRAIN + N_TEST]
    final_imgs = all_images[N_TRAIN + N_TEST:N_TRAIN + N_TEST + N_FINAL]

    # Copy helper
    def copy_files(file_list, dst_dir: Path, label: str):
        dst_dir.mkdir(parents=True, exist_ok=True)
        print(f"Copying {len(file_list)} files to {dst_dir} ...")
        for img in file_list:
            shutil.copy2(img, dst_dir / img.name)
        print(f"✅ {label} split done.\n")

    # Perform copies
    copy_files(train_imgs, DEST_TRAIN, "Training")
    copy_files(test_imgs, DEST_TEST, "Train-test")
    copy_files(final_imgs, DEST_FINAL, "Final-validation")

    print("🎯 All splits completed successfully!")


if __name__ == "__main__":
    split_and_copy_images(SOURCE_DIR)

