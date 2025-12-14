"""Core wallpaper scraper module for downloading and filtering images."""

import os
import re
import hashlib
import asyncio
import aiohttp
from urllib.parse import urlparse, urljoin
from pathlib import Path
from typing import List, Dict, Optional, Callable
from PIL import Image
from io import BytesIO
import validators

import config


class ImageFilter:
    """Filter images based on resolution, aspect ratio, and file size."""
    
    def __init__(
        self,
        min_width: int = config.DEFAULT_MIN_WIDTH,
        min_height: int = config.DEFAULT_MIN_HEIGHT,
        min_aspect_ratio: float = config.DEFAULT_MIN_ASPECT_RATIO,
        max_aspect_ratio: float = config.DEFAULT_MAX_ASPECT_RATIO,
        min_file_size: int = config.DEFAULT_MIN_FILE_SIZE
    ):
        self.min_width = min_width
        self.min_height = min_height
        self.min_aspect_ratio = min_aspect_ratio
        self.max_aspect_ratio = max_aspect_ratio
        self.min_file_size = min_file_size
    
    def check_image(self, image_data: bytes, metadata: dict = None) -> bool:
        """Check if image meets filter criteria."""
        try:
            # Check file size
            if len(image_data) < self.min_file_size:
                return False
            
            # Open image and check dimensions
            img = Image.open(BytesIO(image_data))
            width, height = img.size
            
            # Check minimum resolution
            if width < self.min_width or height < self.min_height:
                return False
            
            # Check aspect ratio
            aspect_ratio = width / height if height > 0 else 0
            if aspect_ratio < self.min_aspect_ratio or aspect_ratio > self.max_aspect_ratio:
                return False
            
            return True
        except (OSError, Image.UnidentifiedImageError, ValueError) as e:
            # Invalid or corrupted image data
            return False


class Categorizer:
    """Categorize images based on metadata and descriptions."""
    
    def __init__(self, keywords: Dict[str, List[str]] = None):
        self.keywords = keywords or config.CATEGORY_KEYWORDS
    
    def categorize(self, metadata: dict) -> str:
        """Determine category based on metadata."""
        # Extract text from metadata
        text_fields = []
        if 'title' in metadata:
            text_fields.append(metadata['title'].lower())
        if 'description' in metadata:
            text_fields.append(metadata['description'].lower())
        if 'alt' in metadata:
            text_fields.append(metadata['alt'].lower())
        if 'url' in metadata:
            text_fields.append(metadata['url'].lower())
        
        combined_text = ' '.join(text_fields)
        
        # Count keyword matches for each category
        category_scores = {}
        for category, keywords in self.keywords.items():
            score = sum(1 for keyword in keywords if keyword in combined_text)
            if score > 0:
                category_scores[category] = score
        
        # Return category with highest score, or 'uncategorized'
        if category_scores:
            return max(category_scores, key=category_scores.get)
        return 'uncategorized'


class WallpaperScraper:
    """Main wallpaper scraper class."""
    
    def __init__(
        self,
        output_dir: str = config.DEFAULT_OUTPUT_DIR,
        image_filter: ImageFilter = None,
        categorizer: Categorizer = None,
        concurrent_downloads: int = config.DEFAULT_CONCURRENT_DOWNLOADS,
        timeout: int = config.DEFAULT_TIMEOUT,
        progress_callback: Callable = None
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.image_filter = image_filter or ImageFilter()
        self.categorizer = categorizer or Categorizer()
        self.concurrent_downloads = concurrent_downloads
        self.timeout = timeout
        self.progress_callback = progress_callback
        self.session = None
        
        # Statistics
        self.stats = {
            'total': 0,
            'downloaded': 0,
            'filtered': 0,
            'failed': 0,
            'categories': {}
        }
    
    def _get_image_extension(self, url: str, content_type: str = None) -> str:
        """Determine image file extension."""
        if content_type:
            ext_map = {
                'image/jpeg': '.jpg',
                'image/png': '.png',
                'image/webp': '.webp',
                'image/bmp': '.bmp'
            }
            if content_type in ext_map:
                return ext_map[content_type]
        
        # Try to get from URL
        parsed = urlparse(url)
        path = parsed.path.lower()
        for ext in config.SUPPORTED_FORMATS:
            if path.endswith(ext):
                return ext
        
        return '.jpg'  # Default
    
    def _generate_filename(self, url: str, metadata: dict, extension: str) -> str:
        """Generate unique filename for image."""
        # Create hash from URL
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        
        # Try to use title if available
        if 'title' in metadata and metadata['title']:
            # Clean title for filename
            title = re.sub(r'[^\w\s-]', '', metadata['title'])
            title = re.sub(r'[-\s]+', '_', title)[:50]
            return f"{title}_{url_hash}{extension}"
        
        return f"wallpaper_{url_hash}{extension}"
    
    async def download_image(self, url: str, metadata: dict = None) -> Optional[dict]:
        """Download a single image."""
        if metadata is None:
            metadata = {}
        
        metadata['url'] = url
        
        try:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            async with self.session.get(url, timeout=timeout) as response:
                if response.status != 200:
                    return None
                
                content_type = response.headers.get('content-type', '')
                image_data = await response.read()
                
                # Apply filters
                if not self.image_filter.check_image(image_data, metadata):
                    self.stats['filtered'] += 1
                    if self.progress_callback:
                        self.progress_callback('filtered', url)
                    return None
                
                # Determine category
                category = self.categorizer.categorize(metadata)
                
                # Create category directory
                category_dir = self.output_dir / category
                category_dir.mkdir(exist_ok=True)
                
                # Generate filename and save
                extension = self._get_image_extension(url, content_type)
                filename = self._generate_filename(url, metadata, extension)
                filepath = category_dir / filename
                
                # Save image
                with open(filepath, 'wb') as f:
                    f.write(image_data)
                
                # Update statistics
                self.stats['downloaded'] += 1
                self.stats['categories'][category] = self.stats['categories'].get(category, 0) + 1
                
                if self.progress_callback:
                    self.progress_callback('downloaded', url, str(filepath))
                
                return {
                    'url': url,
                    'filepath': str(filepath),
                    'category': category,
                    'size': len(image_data)
                }
        
        except aiohttp.ClientError as e:
            # Network-related errors
            self.stats['failed'] += 1
            if self.progress_callback:
                self.progress_callback('failed', url, f"Network error: {str(e)}")
            return None
        except OSError as e:
            # File system errors
            self.stats['failed'] += 1
            if self.progress_callback:
                self.progress_callback('failed', url, f"File error: {str(e)}")
            return None
        except Exception as e:
            # Other unexpected errors
            self.stats['failed'] += 1
            if self.progress_callback:
                self.progress_callback('failed', url, f"Error: {str(e)}")
            return None
    
    async def download_images(self, image_urls: List[str], metadata_list: List[dict] = None):
        """Download multiple images concurrently."""
        if metadata_list is None:
            metadata_list = [{}] * len(image_urls)
        
        self.stats['total'] = len(image_urls)
        
        # Create session with custom headers and timeout
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        connector = aiohttp.TCPConnector(limit=self.concurrent_downloads)
        self.session = aiohttp.ClientSession(
            connector=connector,
            headers={'User-Agent': config.USER_AGENT},
            timeout=timeout
        )
        
        try:
            # Create tasks for concurrent downloads
            semaphore = asyncio.Semaphore(self.concurrent_downloads)
            
            async def bounded_download(url, metadata):
                async with semaphore:
                    return await self.download_image(url, metadata)
            
            tasks = [
                bounded_download(url, metadata)
                for url, metadata in zip(image_urls, metadata_list)
            ]
            
            await asyncio.gather(*tasks)
        
        finally:
            await self.session.close()
    
    def download_images_sync(self, image_urls: List[str], metadata_list: List[dict] = None):
        """Synchronous wrapper for download_images."""
        asyncio.run(self.download_images(image_urls, metadata_list))
    
    def get_stats(self) -> dict:
        """Get download statistics."""
        return self.stats.copy()


def extract_image_urls(html_content: str, base_url: str = None) -> List[Dict]:
    """Extract image URLs from HTML content."""
    from bs4 import BeautifulSoup
    
    soup = BeautifulSoup(html_content, 'html.parser')
    images = []
    
    for img in soup.find_all('img'):
        src = img.get('src') or img.get('data-src')
        if not src:
            continue
        
        # Convert relative URLs to absolute
        if base_url and not src.startswith('http'):
            src = urljoin(base_url, src)
        
        # Validate URL
        if not validators.url(src):
            continue
        
        metadata = {
            'title': img.get('title', ''),
            'alt': img.get('alt', ''),
            'description': ''
        }
        
        images.append({'url': src, 'metadata': metadata})
    
    return images


def is_direct_image_url(url: str) -> bool:
    """Check if URL is a direct image link."""
    parsed = urlparse(url)
    path = parsed.path.lower()
    return any(path.endswith(ext) for ext in config.SUPPORTED_FORMATS)
