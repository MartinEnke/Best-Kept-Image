# Best-Kept-Image
image-duplicate eraser


Best Kept Image 1.0


1. Requirements

Libraries:
 - hashlib (for hashing images)
 - Pillow (PIL) (for loading images)
 - imagehash (for perceptual hashing)
 - numpy (for faster array operations)
 - os (for file handling)

If not installed, install them via:
pip install pillow imagehash numpy
pip install opencv-python
pip install numpy
pip install pillow


Principles
Read all images in the target directory (including subfolders if needed).
Generate a unique hash for each image.
Perceptual hashing (imagehash.phash) is better than cryptographic hashes (md5, sha256)
since it accounts for small differences like compression.
Compare hashes and detect duplicates.
If two hashes are identical or very similar (Hamming distance ≤ a threshold),
the images are considered duplicates.
Delete or move duplicates while keeping one original.


What to Consider
a) Hash Sensitivity
Exact hash matching → Only detects identical files.
Perceptual hashing (pHash, aHash, dHash) → Detects similar images even with slight edits.
b) Image Differences
Cropped, rotated, or slightly modified images may have different hashes.
Watermarked or resized images might not be detected as duplicates.
c) File System
Be careful when deleting images—consider moving them to a "Duplicates" folder first.



Best Kept Image 1.0
Includes:


Features:

1. Delete Confirmation
- Interactive confirmation before deletion
- Option to skip, delete, or move duplicates
- Better error handling
- Progress tracking

How It Works
Scans images, generates perceptual hashes, and finds duplicates.
Displays all duplicate images found.
Asks what to do with them:
(K) Keep the first one & delete the rest.
(M) Move duplicates to a backup folder.
(S) Skip this set.
Processes the choice and moves to the next duplicate set.
Additional Improvements
- Backup folder ensures safety before deletion.
- Better file selection by skipping unreadable images.
- Flexible options so you don’t delete everything at once.


2. Preview
- Opens duplicate images before making a decision
- Keeps the interactive confirmation step
- More user-friendly messages

How It Works:
Scans and detects duplicate images based on perceptual hashing (phash).
Lists the duplicates found for review.
Automatically opens each duplicate image in the default image viewer.
Prompts the user for action:
(K) Keep the first image and delete the rest.
(M) Move duplicates to a backup folder.
(S) Skip this set.
Processes the choice and moves to the next duplicate set.


3. GUI using Tkinter and defined Button Styles using ttk.Button (the themed widget from Tkinter)

Features of the GUI
- Folder Selection – Pick a directory to scan
- Similarity Threshold for near-duplicates (adjustable)
- Side-by-Side Image Comparison
- User Actions – Choose to delete, move to backup, or skip
- Next Duplicate Set – Automatically loads the next set
- Backup Folder – Prevents accidental deletion
- Delete All Duplicates button for bulk deletion


4. Advanced comparison
Use of cv2 (OpenCV) for structural similarity (cv2.compareHist())
Integration of OpenCV's histogram comparison (cv2.compareHist())
for more advanced image similarity detection.


5. Two versions: for 2-picture and 4-picture comparison
