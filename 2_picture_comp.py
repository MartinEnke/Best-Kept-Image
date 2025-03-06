'''
Best Kept Image
Deletes duplicates or similar picture versions.
Features: GUI, Side by Side Preview of 2 pictures, Similarity Threshold-Sider, Backup...
'''

import os
import shutil
import imagehash
import cv2
from PIL import Image, ImageTk
from collections import defaultdict
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk  # Import ttk for themed widgets


class DuplicateImageFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("Duplicate Image Finder")

        self.image_dir = None
        self.backup_dir = "../backup"  # Default backup directory
        os.makedirs(self.backup_dir, exist_ok=True)

        self.hash_dict = defaultdict(list)
        self.duplicates = []
        self.current_index = 0
        self.similarity_threshold = 5  # Allow slight differences in hashes
        self.hist_threshold = 0.9  # Threshold for histogram comparison

        # UI Elements
        self.label = tk.Label(root, text="Select a folder to scan for duplicates")
        self.label.pack(pady=10)

        self.select_button = tk.Button(root, text="Select Folder", command=self.select_folder)
        self.select_button.pack()

        self.slider_label = tk.Label(root, text=f"Similarity Threshold: {self.similarity_threshold}")
        self.slider_label.pack()

        self.threshold_slider = tk.Scale(root, from_=0, to=10, orient=tk.HORIZONTAL, command=self.update_threshold)
        self.threshold_slider.set(self.similarity_threshold)
        self.threshold_slider.pack()

        # Create all buttons with white text and black background
        self.next_button = ttk.Button(root, text="Next Duplicate Set", command=self.show_next_duplicate)
        self.next_button.pack(pady=10)
        self.style_button(self.next_button)

        self.canvas_frame = tk.Frame(root)
        self.canvas_frame.pack()

        self.canvas_left = tk.Canvas(self.canvas_frame, width=250, height=250)
        self.canvas_left.grid(row=0, column=0, padx=10)

        self.canvas_right = tk.Canvas(self.canvas_frame, width=250, height=250)
        self.canvas_right.grid(row=0, column=1, padx=10)

        self.action_frame = tk.Frame(root)
        self.action_frame.pack(pady=10)

        self.keep_button = ttk.Button(self.action_frame, text="Keep First & Delete Rest", command=self.delete_duplicates)
        self.keep_button.grid(row=0, column=0, padx=5)
        self.style_button(self.keep_button)

        self.move_button = ttk.Button(self.action_frame, text="Move to Backup", command=self.move_duplicates)
        self.move_button.grid(row=0, column=1, padx=5)
        self.style_button(self.move_button)

        self.skip_button = ttk.Button(self.action_frame, text="Skip", command=self.skip_duplicates)
        self.skip_button.grid(row=0, column=2, padx=5)
        self.style_button(self.skip_button)

        self.delete_all_button = ttk.Button(root, text="Delete All Duplicates", command=self.delete_all_duplicates)
        self.delete_all_button.pack(pady=10)
        self.style_button(self.delete_all_button)

    def style_button(self, button):
        # This function ensures all buttons have white text and black background
        button.configure(style='TButton')
        style = ttk.Style()
        style.configure('TButton', foreground='white', background='black')

    def update_threshold(self, value):
        self.similarity_threshold = int(value)
        self.slider_label.config(text=f"Similarity Threshold: {self.similarity_threshold}")

    def select_folder(self):
        self.image_dir = filedialog.askdirectory()
        if not self.image_dir:
            return
        self.label.config(text=f"Scanning: {self.image_dir}")
        self.find_duplicates()


    def resize_image(self, img, canvas):
        canvas_width = int(canvas.cget("width"))
        canvas_height = int(canvas.cget("height"))

        img_ratio = img.width / img.height
        canvas_ratio = canvas_width / canvas_height

        if img_ratio > canvas_ratio:
            new_width = canvas_width
            new_height = int(canvas_width / img_ratio)
        else:
            new_height = canvas_height
            new_width = int(canvas_height * img_ratio)

        img_resized = img.resize((new_width, new_height), Image.LANCZOS)
        return ImageTk.PhotoImage(img_resized)


    def find_duplicates(self):
        self.hash_dict.clear()
        self.duplicates.clear()

        for root, _, files in os.walk(self.image_dir):
            for file in files:
                if file.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'bmp')):
                    img_path = os.path.join(root, file)
                    try:
                        img = Image.open(img_path)
                        img_hash = imagehash.phash(img)

                        found_similar = False
                        for existing_hash in self.hash_dict.keys():
                            if abs(existing_hash - img_hash) <= self.similarity_threshold:
                                # Further compare using histogram similarity
                                if self.compare_histogram(img_path,
                                                          self.hash_dict[existing_hash][0]) >= self.hist_threshold:
                                    self.hash_dict[existing_hash].append(img_path)
                                    found_similar = True
                                    break

                        if not found_similar:
                            self.hash_dict[img_hash].append(img_path)
                    except Exception as e:
                        print(f"Error processing {img_path}: {e}")

        self.duplicates = [paths for paths in self.hash_dict.values() if len(paths) > 1]

        if self.duplicates:
            self.label.config(text=f"Found {len(self.duplicates)} duplicate sets.")
            self.enable_buttons()
            self.show_next_duplicate()
        else:
            messagebox.showinfo("No Duplicates", "No duplicate images found.")


    def delete_duplicates(self):
        if self.current_index < len(self.duplicates):
            paths = self.duplicates[self.current_index]
            for dup in paths[1:]:
                os.remove(dup)
            self.current_index += 1
            self.show_next_duplicate()

    def move_duplicates(self):
        if self.current_index < len(self.duplicates):
            paths = self.duplicates[self.current_index]
            for dup in paths[1:]:
                shutil.move(dup, os.path.join(self.backup_dir, os.path.basename(dup)))
            self.current_index += 1
            self.show_next_duplicate()

    def skip_duplicates(self):
        self.current_index += 1
        self.show_next_duplicate()

    def delete_all_duplicates(self):
        for paths in self.duplicates:
            for dup in paths[1:]:
                os.remove(dup)
        messagebox.showinfo("Success", "All duplicates deleted.")
        self.reset_buttons()

    def reset_buttons(self):
        self.next_button.config(state=tk.DISABLED)
        self.keep_button.config(state=tk.DISABLED)
        self.move_button.config(state=tk.DISABLED)
        self.skip_button.config(state=tk.DISABLED)
        self.delete_all_button.config(state=tk.DISABLED)
        self.label.config(text="Scanning complete. No more duplicates.")


    def show_next_duplicate(self):
        if not self.duplicates:
            return

        self.current_index = (self.current_index + 1) % len(self.duplicates)
        current_set = self.duplicates[self.current_index]

        self.canvas_left.delete("all")
        self.canvas_right.delete("all")

        img1 = Image.open(current_set[0])
        img2 = Image.open(current_set[1])

        img1_tk = self.resize_image(img1, self.canvas_left)
        img2_tk = self.resize_image(img2, self.canvas_right)

        self.canvas_left.create_image(125, 125, anchor=tk.CENTER, image=img1_tk)
        self.canvas_right.create_image(125, 125, anchor=tk.CENTER, image=img2_tk)

        self.canvas_left.image = img1_tk
        self.canvas_right.image = img2_tk

    def compare_histogram(self, img1_path, img2_path):
        img1 = cv2.imread(img1_path)
        img2 = cv2.imread(img2_path)

        img1_hsv = cv2.cvtColor(img1, cv2.COLOR_BGR2HSV)
        img2_hsv = cv2.cvtColor(img2, cv2.COLOR_BGR2HSV)

        hist1 = cv2.calcHist([img1_hsv], [0, 1], None, [50, 60], [0, 180, 0, 256])
        hist2 = cv2.calcHist([img2_hsv], [0, 1], None, [50, 60], [0, 180, 0, 256])

        cv2.normalize(hist1, hist1, 0, 1, cv2.NORM_MINMAX)
        cv2.normalize(hist2, hist2, 0, 1, cv2.NORM_MINMAX)

        similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
        return similarity

    def enable_buttons(self):
        self.next_button.config(state=tk.NORMAL)
        self.keep_button.config(state=tk.NORMAL)
        self.move_button.config(state=tk.NORMAL)
        self.skip_button.config(state=tk.NORMAL)
        self.delete_all_button.config(state=tk.NORMAL)


if __name__ == "__main__":
    root = tk.Tk()
    app = DuplicateImageFinder(root)
    root.mainloop()
