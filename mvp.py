import os
import imagehash
from PIL import Image
from collections import defaultdict

# Set your image directory
image_dir = "path/to/your/images"

# Dictionary to store hashes
hash_dict = defaultdict(list)

# Scan images and store their hashes
for root, _, files in os.walk(image_dir):
    for file in files:
        if file.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'bmp')):
            img_path = os.path.join(root, file)
            try:
                img = Image.open(img_path)
                img_hash = imagehash.phash(img)  # Generate perceptual hash
                hash_dict[img_hash].append(img_path)
            except Exception as e:
                print(f"Error processing {img_path}: {e}")

# Find and handle duplicates
for img_hash, paths in hash_dict.items():
    if len(paths) > 1:
        print(f"Duplicate images found: {paths}")
        # Uncomment below to delete duplicates (except the first one)
        # for dup in paths[1:]:
        #     os.remove(dup)
