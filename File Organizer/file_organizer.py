import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox

# I wanted my Downloads to stop being a mess,
# so I built this small tool to auto-sort them.
# Categories can be adjusted below as per personal needs.

FILE_CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
    "Videos": [".mp4", ".mkv", ".mov", ".avi"],
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".pptx", ".xlsx"],
    "Audio": [".mp3", ".wav", ".flac"],
    "Executables": [".exe", ".msi"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
}


class DownloadsOrganizer:
    def __init__(self, master):
        self.master = master
        self.master.title("Downloads Organizer")
        self.master.geometry("600x400")

        self.folder_path = tk.StringVar()

        # Folder selection UI
        tk.Label(master, text="Target Folder:").pack(pady=5)
        tk.Entry(master, textvariable=self.folder_path, width=50).pack(pady=5)
        tk.Button(master, text="Browse", command=self.choose_folder).pack(pady=5)

        # Action buttons
        tk.Button(master, text="Organize Downloads", command=self.organize_downloads).pack(pady=10)

        # Log area
        self.log_area = tk.Text(master, wrap=tk.WORD, height=15)
        self.log_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    def choose_folder(self):
        """Let the user select which folder to organize (default: Downloads)."""
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)

    def organize_downloads(self):
        """Go through files in the target folder and organize by type."""
        target_folder = self.folder_path.get()
        if not target_folder or not os.path.exists(target_folder):
            messagebox.showerror("Error", "Please select a valid folder.")
            return

        summary = {cat: 0 for cat in FILE_CATEGORIES.keys()}
        summary["Others"] = 0

        for filename in os.listdir(target_folder):
            file_path = os.path.join(target_folder, filename)

            if os.path.isfile(file_path):
                file_ext = os.path.splitext(filename)[1].lower()
                moved = False

                # Check each category
                for category, extensions in FILE_CATEGORIES.items():
                    if file_ext in extensions:
                        self._move_file(file_path, os.path.join(target_folder, category), filename)
                        summary[category] += 1
                        moved = True
                        break

                if not moved:
                    # Goes to "Others" if extension isn't in categories
                    self._move_file(file_path, os.path.join(target_folder, "Others"), filename)
                    summary["Others"] += 1

        # Show summary in log
        self.log_area.insert(tk.END, "\nSummary:\n")
        for category, count in summary.items():
            self.log_area.insert(tk.END, f"{category}: {count} files\n")
        self.log_area.insert(tk.END, "-" * 40 + "\n")

        messagebox.showinfo("Done", "Downloads organized successfully!")

    def _move_file(self, src, dest_folder, filename):
        """Move a file into its category folder, handle duplicates gracefully."""
        os.makedirs(dest_folder, exist_ok=True)

        new_path = os.path.join(dest_folder, filename)
        new_path = self._make_unique_name(new_path)

        try:
            shutil.move(src, new_path)
            self.log_area.insert(tk.END, f"Moved: {filename} → {dest_folder}\n")
        except PermissionError:
            self.log_area.insert(tk.END, f"Skipped (permission denied): {filename}\n")
        except FileExistsError:
            self.log_area.insert(tk.END, f"Skipped (already exists): {filename}\n")
        except Exception as e:
            self.log_area.insert(tk.END, f"Error moving {filename}: {e}\n")

    @staticmethod
    def _make_unique_name(filepath):
        """If a file exists, add (1), (2), etc. until unique name is found."""
        base, ext = os.path.splitext(filepath)
        counter = 1
        new_filepath = filepath

        while os.path.exists(new_filepath):
            new_filepath = f"{base}({counter}){ext}"
            counter += 1

        return new_filepath


if __name__ == "__main__":
    root = tk.Tk()
    app = DownloadsOrganizer(root)
    root.mainloop()
