'''
Best Kept Image
Deletes duplicates or similar picture versions.
Features: GUI, Side by Side Preview of up to 4 pictures,
Delete Selection, Similarity Threshold-Sider, Backup...
'''

import os
import shutil
import imagehash
import cv2
from PIL import Image, ImageTk
from collections import defaultdict
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

class DuplicateImageFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("Duplicate Image Finder")

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        self.window_width = int(screen_width * 0.75)
        self.window_height = int(screen_height * 0.75)
        root.geometry(f"{self.window_width}x{self.window_height}")

        self.image_dir = None
        self.backup_dir = "../backup"
        os.makedirs(self.backup_dir, exist_ok=True)

        self.hash_dict = defaultdict(list)
        self.duplicates = []
        self.current_index = 0
        self.similarity_threshold = 5
        self.hist_threshold = 0.9

        # UI Elemente
        self.label = tk.Label(root, text="Select a folder to scan for duplicates")
        self.label.pack(pady=10)

        self.select_button = tk.Button(root, text="Select Folder", command=self.select_folder)
        self.select_button.pack()

        self.slider_label = tk.Label(root, text=f"Similarity Threshold: {self.similarity_threshold}")
        self.slider_label.pack()

        self.threshold_slider = tk.Scale(root, from_=0, to=10, orient=tk.HORIZONTAL, command=self.update_threshold)
        self.threshold_slider.set(self.similarity_threshold)
        self.threshold_slider.pack()

        self.canvas_frame = tk.Frame(root)
        self.canvas_frame.pack()

        # Erstellen von 4 Canvas-Elementen für die Bildanzeige
        self.canvases = []
        for row in range(2):
            for col in range(2):
                canvas = tk.Canvas(self.canvas_frame, width=250, height=250)
                canvas.grid(row=row, column=col, padx=10, pady=10)
                self.canvases.append(canvas)

        # Auswahlbuttons für jedes Bild
        self.selection_vars = [tk.BooleanVar() for _ in range(4)]
        self.selection_checkbuttons = [
            tk.Checkbutton(root, text=f"Delete Image {i+1}", variable=self.selection_vars[i]) for i in range(4)
        ]
        for btn in self.selection_checkbuttons:
            btn.pack()

        # Funktions-Buttons
        self.action_frame = tk.Frame(root)
        self.action_frame.pack(pady=10)

        self.keep_button = ttk.Button(self.action_frame, text="Keep First & Delete Rest", command=self.delete_duplicates)
        self.keep_button.grid(row=0, column=0, padx=5)

        self.delete_selected_button = ttk.Button(self.action_frame, text="Delete Selected", command=self.delete_selected)
        self.delete_selected_button.grid(row=0, column=1, padx=5)

        self.move_button = ttk.Button(self.action_frame, text="Move to Backup", command=self.move_duplicates)
        self.move_button.grid(row=0, column=2, padx=5)

        self.skip_button = ttk.Button(self.action_frame, text="Skip", command=self.skip_duplicates)
        self.skip_button.grid(row=0, column=3, padx=5)

        self.next_button = ttk.Button(root, text="Next Duplicate Set", command=self.show_next_duplicate)
        self.next_button.pack(pady=10)

    def update_threshold(self, value):
        self.similarity_threshold = int(value)
        self.slider_label.config(text=f"Similarity Threshold: {self.similarity_threshold}")

    def select_folder(self):
        self.image_dir = filedialog.askdirectory()
        if not self.image_dir:
            return
        self.label.config(text=f"Scanning: {self.image_dir}")
        self.find_duplicates()

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
                                if self.compare_histogram(img_path, self.hash_dict[existing_hash][0]) >= self.hist_threshold:
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
            self.show_next_duplicate()
        else:
            messagebox.showinfo("No Duplicates", "No duplicate images found.")

    def delete_duplicates(self):
        """Löscht alle Bilder außer das erste in der aktuellen Duplikatengruppe."""
        if self.current_index < len(self.duplicates):
            paths = self.duplicates[self.current_index]
            for i, path in enumerate(paths):
                if i > 0:  # Erstes Bild bleibt erhalten
                    os.remove(path)
            self.current_index += 1
            self.show_next_duplicate()

    def delete_selected(self):
        """Löscht nur die explizit ausgewählten Bilder."""
        if self.current_index < len(self.duplicates):
            paths = self.duplicates[self.current_index]
            for i, path in enumerate(paths):
                if self.selection_vars[i].get():
                    os.remove(path)
            self.current_index += 1
            self.show_next_duplicate()

    def move_duplicates(self):
        """Verschiebt ausgewählte Bilder in den Backup-Ordner."""
        if self.current_index < len(self.duplicates):
            paths = self.duplicates[self.current_index]
            for i, path in enumerate(paths):
                if self.selection_vars[i].get():
                    shutil.move(path, os.path.join(self.backup_dir, os.path.basename(path)))
            self.current_index += 1
            self.show_next_duplicate()

    def skip_duplicates(self):
        """Überspringt die aktuelle Duplikatengruppe."""
        self.current_index += 1
        self.show_next_duplicate()

    def show_next_duplicate(self):
        """Zeigt das nächste Duplikatenset an."""
        if not self.duplicates:
            return
        self.current_index = (self.current_index + 1) % len(self.duplicates)
        current_set = self.duplicates[self.current_index]
        for i, canvas in enumerate(self.canvases):
            canvas.delete("all")
            if i < len(current_set):
                img = Image.open(current_set[i])
                img.thumbnail((250, 250))
                img_tk = ImageTk.PhotoImage(img)
                canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
                canvas.image = img_tk
        for i in range(4):
            self.selection_vars[i].set(False)

    def compare_histogram(self, img1_path, img2_path):
        """Vergleicht die Histogramme zweier Bilder und gibt die Ähnlichkeit zurück."""
        img1 = cv2.imread(img1_path)
        img2 = cv2.imread(img2_path)
        img1_hsv = cv2.cvtColor(img1, cv2.COLOR_BGR2HSV)
        img2_hsv = cv2.cvtColor(img2, cv2.COLOR_BGR2HSV)
        hist1 = cv2.calcHist([img1_hsv], [0, 1], None, [50, 60], [0, 180, 0, 256])
        hist2 = cv2.calcHist([img2_hsv], [0, 1], None, [50, 60], [0, 180, 0, 256])
        return cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)

if __name__ == "__main__":
    root = tk.Tk()
    app = DuplicateImageFinder(root)
    root.mainloop()
