import math
import os
import random
import re
import sys

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
