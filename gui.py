#!/usr/bin/env python3
"""Graphical user interface for the wallpaper scraper."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
from pathlib import Path
from typing import List
import asyncio

import config
from scraper import WallpaperScraper, ImageFilter, Categorizer, extract_image_urls, is_direct_image_url
import requests


class WallpaperScraperGUI:
    """Main GUI application."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Wallpaper Scraper")
        self.root.geometry("900x700")
        
        # Progress queue for thread-safe updates
        self.progress_queue = queue.Queue()
        
        # Download state
        self.is_downloading = False
        self.download_thread = None
        
        self._create_widgets()
        self._check_progress_queue()
    
    def _create_widgets(self):
        """Create and layout GUI widgets."""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Wallpaper Scraper",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # URL Input Section
        url_frame = ttk.LabelFrame(main_frame, text="Input", padding="10")
        url_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        url_frame.columnconfigure(1, weight=1)
        
        # URL or file input
        ttk.Label(url_frame, text="URLs/File:").grid(row=0, column=0, sticky=tk.W, pady=2)
        
        url_input_frame = ttk.Frame(url_frame)
        url_input_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)
        url_input_frame.columnconfigure(0, weight=1)
        
        self.url_text = scrolledtext.ScrolledText(url_input_frame, height=4, width=50)
        self.url_text.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        url_buttons = ttk.Frame(url_input_frame)
        url_buttons.grid(row=0, column=1, sticky=tk.N)
        
        ttk.Button(url_buttons, text="Load File", command=self._load_file).pack(pady=2)
        ttk.Button(url_buttons, text="Clear", command=lambda: self.url_text.delete(1.0, tk.END)).pack(pady=2)
        
        ttk.Label(url_frame, text="(Enter URLs or webpage, one per line)").grid(
            row=1, column=1, sticky=tk.W, pady=(0, 5)
        )
        
        # Output directory
        ttk.Label(url_frame, text="Output Dir:").grid(row=2, column=0, sticky=tk.W, pady=2)
        
        output_frame = ttk.Frame(url_frame)
        output_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2)
        output_frame.columnconfigure(0, weight=1)
        
        self.output_var = tk.StringVar(value=config.DEFAULT_OUTPUT_DIR)
        ttk.Entry(output_frame, textvariable=self.output_var).grid(
            row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5)
        )
        ttk.Button(output_frame, text="Browse", command=self._browse_output).grid(row=0, column=1)
        
        # Filter Settings
        filter_frame = ttk.LabelFrame(main_frame, text="Filter Settings", padding="10")
        filter_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N), padx=(0, 5), pady=(0, 10))
        filter_frame.columnconfigure(1, weight=1)
        
        # Resolution
        ttk.Label(filter_frame, text="Min Width:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.min_width_var = tk.IntVar(value=config.DEFAULT_MIN_WIDTH)
        ttk.Spinbox(filter_frame, from_=0, to=7680, textvariable=self.min_width_var, width=10).grid(
            row=0, column=1, sticky=tk.W, pady=2
        )
        
        ttk.Label(filter_frame, text="Min Height:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.min_height_var = tk.IntVar(value=config.DEFAULT_MIN_HEIGHT)
        ttk.Spinbox(filter_frame, from_=0, to=4320, textvariable=self.min_height_var, width=10).grid(
            row=1, column=1, sticky=tk.W, pady=2
        )
        
        # Aspect ratio
        ttk.Label(filter_frame, text="Min Aspect:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.min_aspect_var = tk.DoubleVar(value=config.DEFAULT_MIN_ASPECT_RATIO)
        ttk.Spinbox(filter_frame, from_=0.1, to=10.0, increment=0.1,
                    textvariable=self.min_aspect_var, width=10).grid(row=2, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(filter_frame, text="Max Aspect:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.max_aspect_var = tk.DoubleVar(value=config.DEFAULT_MAX_ASPECT_RATIO)
        ttk.Spinbox(filter_frame, from_=0.1, to=10.0, increment=0.1,
                    textvariable=self.max_aspect_var, width=10).grid(row=3, column=1, sticky=tk.W, pady=2)
        
        # File size
        ttk.Label(filter_frame, text="Min Size (KB):").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.min_size_var = tk.IntVar(value=config.DEFAULT_MIN_FILE_SIZE // 1024)
        ttk.Spinbox(filter_frame, from_=0, to=10000, textvariable=self.min_size_var, width=10).grid(
            row=4, column=1, sticky=tk.W, pady=2
        )
        
        # Download Settings
        download_frame = ttk.LabelFrame(main_frame, text="Download Settings", padding="10")
        download_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N), pady=(0, 10))
        download_frame.columnconfigure(1, weight=1)
        
        ttk.Label(download_frame, text="Concurrent:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.concurrent_var = tk.IntVar(value=config.DEFAULT_CONCURRENT_DOWNLOADS)
        ttk.Spinbox(download_frame, from_=1, to=20, textvariable=self.concurrent_var, width=10).grid(
            row=0, column=1, sticky=tk.W, pady=2
        )
        
        ttk.Label(download_frame, text="Timeout (s):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.timeout_var = tk.IntVar(value=config.DEFAULT_TIMEOUT)
        ttk.Spinbox(download_frame, from_=5, to=300, textvariable=self.timeout_var, width=10).grid(
            row=1, column=1, sticky=tk.W, pady=2
        )
        
        self.categorize_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(download_frame, text="Auto-categorize", variable=self.categorize_var).grid(
            row=2, column=0, columnspan=2, sticky=tk.W, pady=2
        )
        
        # Action Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(0, 10))
        
        self.download_btn = ttk.Button(
            button_frame,
            text="Start Download",
            command=self._start_download,
            style="Accent.TButton"
        )
        self.download_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(
            button_frame,
            text="Stop",
            command=self._stop_download,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Progress Section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.status_label = ttk.Label(progress_frame, text="Ready")
        self.status_label.grid(row=1, column=0, sticky=tk.W)
        
        # Statistics
        stats_frame = ttk.Frame(progress_frame)
        stats_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        self.stats_label = ttk.Label(
            stats_frame,
            text="Downloaded: 0 | Filtered: 0 | Failed: 0"
        )
        self.stats_label.pack(side=tk.LEFT)
        
        # Log Section
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="10")
        log_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, state=tk.DISABLED)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def _log(self, message: str):
        """Add message to log."""
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)
    
    def _load_file(self):
        """Load URLs from file."""
        filepath = filedialog.askopenfilename(
            title="Select URL file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filepath:
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                self.url_text.delete(1.0, tk.END)
                self.url_text.insert(1.0, content)
                self._log(f"Loaded URLs from {filepath}")
            except FileNotFoundError:
                messagebox.showerror("Error", f"File not found: {filepath}")
            except PermissionError:
                messagebox.showerror("Error", f"Permission denied: {filepath}")
            except UnicodeDecodeError:
                messagebox.showerror("Error", f"Invalid file encoding. Please use UTF-8.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {e}")
    
    def _browse_output(self):
        """Browse for output directory."""
        directory = filedialog.askdirectory(title="Select output directory")
        if directory:
            self.output_var.set(directory)
    
    def _get_urls(self) -> List[dict]:
        """Get URLs from input."""
        text = self.url_text.get(1.0, tk.END).strip()
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        image_data = []
        for line in lines:
            if line.startswith('#'):
                continue
            
            # Check if it's a direct image URL or a webpage
            if is_direct_image_url(line):
                image_data.append({'url': line, 'metadata': {}})
            else:
                # Try to extract images from webpage
                self._log(f"Extracting images from {line}...")
                try:
                    response = requests.get(line, headers={'User-Agent': config.USER_AGENT}, timeout=30)
                    response.raise_for_status()
                    extracted = extract_image_urls(response.text, line)
                    image_data.extend(extracted)
                    self._log(f"Found {len(extracted)} images")
                except requests.Timeout:
                    self._log(f"Timeout extracting from {line}")
                except requests.ConnectionError:
                    self._log(f"Connection error extracting from {line}")
                except requests.HTTPError as e:
                    self._log(f"HTTP error extracting from {line}: {e}")
                except Exception as e:
                    self._log(f"Error extracting from {line}: {e}")
        
        return image_data
    
    def _progress_callback(self, status: str, url: str, extra: str = None):
        """Callback for download progress."""
        self.progress_queue.put((status, url, extra))
    
    def _check_progress_queue(self):
        """Check progress queue and update UI."""
        try:
            while True:
                status, url, extra = self.progress_queue.get_nowait()
                
                if status == 'start':
                    total = int(url)
                    self.total_images = total
                    self.processed_images = 0
                    self.downloaded_count = 0
                    self.filtered_count = 0
                    self.failed_count = 0
                    self.status_label.config(text=f"Downloading 0/{total}...")
                    self.progress_var.set(0)
                
                elif status == 'downloaded':
                    self.downloaded_count += 1
                    self.processed_images += 1
                    self._update_progress()
                    self._log(f"✓ Downloaded: {Path(extra).name}")
                
                elif status == 'filtered':
                    self.filtered_count += 1
                    self.processed_images += 1
                    self._update_progress()
                
                elif status == 'failed':
                    self.failed_count += 1
                    self.processed_images += 1
                    self._update_progress()
                    self._log(f"✗ Failed: {url[:50]}... - {extra}")
                
                elif status == 'complete':
                    self.status_label.config(text="Download complete!")
                    self.progress_var.set(100)
                    self._log("\n" + "="*50)
                    self._log("Download Summary")
                    self._log("="*50)
                    stats = extra  # stats dict
                    self._log(f"Total: {stats['total']}")
                    self._log(f"Downloaded: {stats['downloaded']}")
                    self._log(f"Filtered: {stats['filtered']}")
                    self._log(f"Failed: {stats['failed']}")
                    if stats['categories']:
                        self._log("\nCategories:")
                        for cat, count in sorted(stats['categories'].items()):
                            self._log(f"  {cat}: {count}")
                    
                    self.is_downloading = False
                    self.download_btn.config(state=tk.NORMAL)
                    self.stop_btn.config(state=tk.DISABLED)
                    
                    messagebox.showinfo("Complete", f"Download complete!\n\nDownloaded: {stats['downloaded']}\nFiltered: {stats['filtered']}\nFailed: {stats['failed']}")
        
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self._check_progress_queue)
    
    def _update_progress(self):
        """Update progress bar and labels."""
        if self.total_images > 0:
            progress = (self.processed_images / self.total_images) * 100
            self.progress_var.set(progress)
            self.status_label.config(
                text=f"Processing {self.processed_images}/{self.total_images}..."
            )
            self.stats_label.config(
                text=f"Downloaded: {self.downloaded_count} | Filtered: {self.filtered_count} | Failed: {self.failed_count}"
            )
    
    def _download_worker(self, image_data: List[dict], scraper: WallpaperScraper):
        """Worker function for download thread."""
        try:
            # Signal start
            self.progress_queue.put(('start', str(len(image_data)), None))
            
            # Download
            urls = [item['url'] for item in image_data]
            metadata_list = [item['metadata'] for item in image_data]
            scraper.download_images_sync(urls, metadata_list)
            
            # Signal complete
            stats = scraper.get_stats()
            self.progress_queue.put(('complete', '', stats))
        
        except KeyboardInterrupt:
            # User cancelled
            self.progress_queue.put(('complete', '', {'total': 0, 'downloaded': 0, 'filtered': 0, 'failed': 0, 'categories': {}}))
        except Exception as e:
            # Log error and signal completion
            import traceback
            error_msg = f"Download error: {str(e)}\n{traceback.format_exc()}"
            self.progress_queue.put(('failed', 'Critical Error', error_msg))
            self.progress_queue.put(('complete', '', {'total': 0, 'downloaded': 0, 'filtered': 0, 'failed': 0, 'categories': {}}))
    
    def _start_download(self):
        """Start download process."""
        if self.is_downloading:
            return
        
        # Get URLs
        image_data = self._get_urls()
        if not image_data:
            messagebox.showwarning("No URLs", "Please enter at least one URL or load a file")
            return
        
        self._log(f"\nPreparing to download {len(image_data)} images...")
        
        # Create filter
        image_filter = ImageFilter(
            min_width=self.min_width_var.get(),
            min_height=self.min_height_var.get(),
            min_aspect_ratio=self.min_aspect_var.get(),
            max_aspect_ratio=self.max_aspect_var.get(),
            min_file_size=self.min_size_var.get() * 1024
        )
        
        # Create categorizer
        categorizer = Categorizer() if self.categorize_var.get() else None
        
        # Create scraper
        scraper = WallpaperScraper(
            output_dir=self.output_var.get(),
            image_filter=image_filter,
            categorizer=categorizer,
            concurrent_downloads=self.concurrent_var.get(),
            timeout=self.timeout_var.get(),
            progress_callback=self._progress_callback
        )
        
        # Start download in thread
        self.is_downloading = True
        self.download_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        self.download_thread = threading.Thread(
            target=self._download_worker,
            args=(image_data, scraper),
            daemon=True
        )
        self.download_thread.start()
    
    def _stop_download(self):
        """Stop download process."""
        # Note: This is a graceful signal - downloads in progress will complete
        self.is_downloading = False
        self._log("\nStopping downloads (in-progress downloads will complete)...")
        self.stop_btn.config(state=tk.DISABLED)


def main():
    """Main entry point for GUI."""
    root = tk.Tk()
    
    # Set theme
    style = ttk.Style()
    if 'clam' in style.theme_names():
        style.theme_use('clam')
    
    app = WallpaperScraperGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
