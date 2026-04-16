import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from PIL import Image, ImageFile
import threading

class ImageCompressorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Compressor Pro")
        self.root.geometry("520x450")
        self.root.resizable(False, False)
        
        # Variables
        self.entry_path = tk.StringVar()
        self.quality_var = tk.IntVar(value=85)
        self.format_var = tk.StringVar(value="Keep Original")
        self.max_size_var = tk.IntVar(value=8000)
        
        self.setup_ui()

    def setup_ui(self):
        # Header
        header = tk.Label(self.root, text="🖼️ Image Compressor Pro", font=("Segoe UI", 16, "bold"))
        header.pack(pady=20)

        # Folder Selection Frame
        folder_frame = tk.LabelFrame(self.root, text=" Source Folder ", padx=10, pady=10)
        folder_frame.pack(fill="x", padx=30, pady=5)

        tk.Entry(folder_frame, textvariable=self.entry_path, state="readonly").pack(side="left", fill="x", expand=True, padx=(0, 5))
        tk.Button(folder_frame, text="Browse", command=self.select_folder, width=10).pack(side="right")

        # Options Frame
        options_frame = tk.LabelFrame(self.root, text=" Compression Settings ", padx=10, pady=10)
        options_frame.pack(fill="x", padx=30, pady=10)

        # Quality Slider
        tk.Label(options_frame, text="Quality (%):").grid(row=0, column=0, sticky="w", pady=5)
        quality_scale = ttk.Scale(options_frame, from_=10, to=95, variable=self.quality_var, orient="horizontal")
        quality_scale.grid(row=0, column=1, sticky="ew", padx=10)
        tk.Label(options_frame, textvariable=self.quality_var, width=3).grid(row=0, column=2)

        # Resolution Slider (Max Side)
        tk.Label(options_frame, text="Max Size (px):").grid(row=1, column=0, sticky="w", pady=5)
        size_scale = ttk.Scale(options_frame, from_=500, to=12000, variable=self.max_size_var, orient="horizontal")
        size_scale.grid(row=1, column=1, sticky="ew", padx=10)
        tk.Label(options_frame, textvariable=self.max_size_var, width=5).grid(row=1, column=2)

        # Format Dropdown
        tk.Label(options_frame, text="Output Format:").grid(row=2, column=0, sticky="w", pady=5)
        format_combo = ttk.Combobox(options_frame, textvariable=self.format_var, 
                                    values=["Keep Original", "JPEG", "PNG", "WEBP"], state="readonly")
        format_combo.grid(row=2, column=1, sticky="w", padx=10)

        options_frame.grid_columnconfigure(1, weight=1)

        # Progress Section
        self.progress = ttk.Progressbar(self.root, mode="determinate", maximum=100)
        self.progress.pack(fill="x", padx=30, pady=(15, 0))

        self.status_label = tk.Label(self.root, text="Ready", fg="gray")
        self.status_label.pack(pady=5)

        # Action Buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        
        self.start_btn = tk.Button(btn_frame, text="🚀 Start Compression", command=self.start_thread, 
                                   bg="#2e7d32", fg="white", font=("Segoe UI", 10, "bold"), padx=20)
        self.start_btn.pack(side="left", padx=10)

    def select_folder(self):
        folder = filedialog.askdirectory(title="Select Folder Containing Images")
        if folder:
            self.entry_path.set(folder)

    def start_thread(self):
        if not self.entry_path.get():
            messagebox.showwarning("Warning", "Please select a source folder first!")
            return
        
        # Disable button during process
        self.start_btn.config(state="disabled")
        thread = threading.Thread(target=self.process_images, daemon=True)
        thread.start()

    def process_images(self):
        try:
            source_dir = Path(self.entry_path.get())
            quality = self.quality_var.get()
            max_size_val = self.max_size_var.get()
            out_fmt_raw = self.format_var.get().lower()
            
            # Setup output directory
            output_dir = source_dir / "Optimized_Images"
            output_dir.mkdir(exist_ok=True)

            # Global Pillow Config
            Image.MAX_IMAGE_PIXELS = None 
            ImageFile.LOAD_TRUNCATED_IMAGES = True

            # Get supported files
            extensions = {'.jpg', '.jpeg', '.png', '.webp'}
            image_files = [f for f in source_dir.iterdir() if f.is_file() and f.suffix.lower() in extensions]

            if not image_files:
                self.root.after(0, lambda: messagebox.showinfo("Info", "No valid images found in folder."))
                return

            total_files = len(image_files)

            for index, file_path in enumerate(image_files):
                # Update UI Status
                self.status_label.config(text=f"Processing: {file_path.name}", fg="blue")
                
                # Determine target extension
                target_ext = file_path.suffix if out_fmt_raw == "keep original" else f".{out_fmt_raw.replace('jpeg', 'jpg')}"
                save_path = output_dir / f"{file_path.stem}{target_ext}"

                with Image.open(file_path) as img:
                    # Handle transparency for JPEG conversion
                    if img.mode in ("RGBA", "P") and target_ext.lower() in (".jpg", ".jpeg"):
                        img = img.convert("RGB")
                    
                    # Resize while maintaining aspect ratio
                    img.thumbnail((max_size_val, max_size_val), Image.Resampling.LANCZOS)
                    
                    # Save
                    img.save(save_path, optimize=True, quality=quality, progressive=True)

                # Update Progress Bar
                progress_val = ((index + 1) / total_files) * 100
                self.progress['value'] = progress_val
                self.root.update_idletasks()

            self.status_label.config(text=f"✅ Finished! Saved in /Optimized_Images", fg="green")
            messagebox.showinfo("Success", f"Processed {total_files} images successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_label.config(text="❌ Error", fg="red")
        
        finally:
            self.start_btn.config(state="normal")
            self.progress['value'] = 0

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageCompressorApp(root)
    root.mainloop()
