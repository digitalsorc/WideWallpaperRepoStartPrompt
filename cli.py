#!/usr/bin/env python3
"""Command-line interface for the wallpaper scraper."""

import argparse
import sys
from pathlib import Path
from typing import List
import requests
from tqdm import tqdm

import config
from scraper import WallpaperScraper, ImageFilter, Categorizer, extract_image_urls, is_direct_image_url


class ProgressTracker:
    """Progress tracker with tqdm."""
    
    def __init__(self, total: int):
        self.pbar = tqdm(total=total, desc="Downloading", unit="img")
        self.downloaded = 0
        self.filtered = 0
        self.failed = 0
    
    def update(self, status: str, url: str, extra: str = None):
        """Update progress based on status."""
        if status == 'downloaded':
            self.downloaded += 1
            self.pbar.set_postfix(
                downloaded=self.downloaded,
                filtered=self.filtered,
                failed=self.failed
            )
            self.pbar.update(1)
        elif status == 'filtered':
            self.filtered += 1
            self.pbar.set_postfix(
                downloaded=self.downloaded,
                filtered=self.filtered,
                failed=self.failed
            )
            self.pbar.update(1)
        elif status == 'failed':
            self.failed += 1
            self.pbar.set_postfix(
                downloaded=self.downloaded,
                filtered=self.filtered,
                failed=self.failed
            )
            self.pbar.update(1)
    
    def close(self):
        """Close progress bar."""
        self.pbar.close()


def read_urls_from_file(filepath: str) -> List[str]:
    """Read URLs from a text file (one per line)."""
    urls = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                urls.append(line)
    return urls


def fetch_and_extract_urls(page_url: str) -> List[dict]:
    """Fetch a webpage and extract image URLs."""
    try:
        response = requests.get(page_url, headers={'User-Agent': config.USER_AGENT}, timeout=30)
        response.raise_for_status()
        return extract_image_urls(response.text, page_url)
    except requests.Timeout:
        print(f"Timeout fetching {page_url}", file=sys.stderr)
        return []
    except requests.ConnectionError:
        print(f"Connection error fetching {page_url}", file=sys.stderr)
        return []
    except requests.HTTPError as e:
        print(f"HTTP error fetching {page_url}: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"Error fetching {page_url}: {e}", file=sys.stderr)
        return []


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Wallpaper Scraper - Download and organize high-resolution wallpapers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download from direct image URLs
  %(prog)s -u https://example.com/image1.jpg https://example.com/image2.jpg
  
  # Download from URLs in a file
  %(prog)s -f urls.txt
  
  # Extract and download from a webpage
  %(prog)s -p https://example.com/wallpapers
  
  # Custom filters
  %(prog)s -u https://example.com/image.jpg --min-width 2560 --min-height 1440
  
  # Concurrent downloads
  %(prog)s -f urls.txt --concurrent 10
        """
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('-u', '--urls', nargs='+', help='Direct image URLs to download')
    input_group.add_argument('-f', '--file', help='File containing URLs (one per line)')
    input_group.add_argument('-p', '--page', help='Webpage URL to extract images from')
    
    # Output options
    parser.add_argument('-o', '--output', default=config.DEFAULT_OUTPUT_DIR,
                        help=f'Output directory (default: {config.DEFAULT_OUTPUT_DIR})')
    
    # Filter options
    parser.add_argument('--min-width', type=int, default=config.DEFAULT_MIN_WIDTH,
                        help=f'Minimum width in pixels (default: {config.DEFAULT_MIN_WIDTH})')
    parser.add_argument('--min-height', type=int, default=config.DEFAULT_MIN_HEIGHT,
                        help=f'Minimum height in pixels (default: {config.DEFAULT_MIN_HEIGHT})')
    parser.add_argument('--min-aspect', type=float, default=config.DEFAULT_MIN_ASPECT_RATIO,
                        help=f'Minimum aspect ratio (default: {config.DEFAULT_MIN_ASPECT_RATIO})')
    parser.add_argument('--max-aspect', type=float, default=config.DEFAULT_MAX_ASPECT_RATIO,
                        help=f'Maximum aspect ratio (default: {config.DEFAULT_MAX_ASPECT_RATIO})')
    parser.add_argument('--min-size', type=int, default=config.DEFAULT_MIN_FILE_SIZE // 1024,
                        help=f'Minimum file size in KB (default: {config.DEFAULT_MIN_FILE_SIZE // 1024})')
    
    # Download options
    parser.add_argument('--concurrent', type=int, default=config.DEFAULT_CONCURRENT_DOWNLOADS,
                        help=f'Number of concurrent downloads (default: {config.DEFAULT_CONCURRENT_DOWNLOADS})')
    parser.add_argument('--timeout', type=int, default=config.DEFAULT_TIMEOUT,
                        help=f'Download timeout in seconds (default: {config.DEFAULT_TIMEOUT})')
    
    # Categorization options
    parser.add_argument('--no-categorize', action='store_true',
                        help='Disable automatic categorization')
    
    args = parser.parse_args()
    
    # Prepare URLs
    image_data = []
    
    if args.urls:
        # Direct URLs
        for url in args.urls:
            image_data.append({'url': url, 'metadata': {}})
    elif args.file:
        # URLs from file
        urls = read_urls_from_file(args.file)
        for url in urls:
            image_data.append({'url': url, 'metadata': {}})
    elif args.page:
        # Extract from webpage
        print(f"Extracting images from {args.page}...")
        image_data = fetch_and_extract_urls(args.page)
        print(f"Found {len(image_data)} images")
    
    if not image_data:
        print("No images to download", file=sys.stderr)
        return 1
    
    # Create filter
    image_filter = ImageFilter(
        min_width=args.min_width,
        min_height=args.min_height,
        min_aspect_ratio=args.min_aspect,
        max_aspect_ratio=args.max_aspect,
        min_file_size=args.min_size * 1024
    )
    
    # Create categorizer
    categorizer = Categorizer() if not args.no_categorize else None
    
    # Create progress tracker
    progress = ProgressTracker(len(image_data))
    
    # Create scraper
    scraper = WallpaperScraper(
        output_dir=args.output,
        image_filter=image_filter,
        categorizer=categorizer,
        concurrent_downloads=args.concurrent,
        timeout=args.timeout,
        progress_callback=progress.update
    )
    
    # Download images
    urls = [item['url'] for item in image_data]
    metadata_list = [item['metadata'] for item in image_data]
    
    try:
        scraper.download_images_sync(urls, metadata_list)
    finally:
        progress.close()
    
    # Print statistics
    stats = scraper.get_stats()
    print("\n" + "="*50)
    print("Download Summary")
    print("="*50)
    print(f"Total images processed: {stats['total']}")
    print(f"Successfully downloaded: {stats['downloaded']}")
    print(f"Filtered out: {stats['filtered']}")
    print(f"Failed: {stats['failed']}")
    
    if stats['categories']:
        print("\nCategories:")
        for category, count in sorted(stats['categories'].items()):
            print(f"  {category}: {count}")
    
    print(f"\nImages saved to: {args.output}/")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
