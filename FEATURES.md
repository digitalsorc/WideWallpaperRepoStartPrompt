# Features Overview

## Complete Wallpaper Scraping Solution

This project provides a production-ready wallpaper scraper with both GUI and CLI interfaces.

## Core Capabilities

### 1. Download Management
- **Concurrent Downloads**: Download up to 20 images simultaneously
- **Smart Timeout Handling**: Configurable timeout with automatic retry logic
- **Progress Tracking**: Real-time progress updates with statistics
- **Batch Processing**: Handle hundreds or thousands of URLs efficiently

### 2. Advanced Filtering

#### Resolution Filters
- Minimum width (default: 1920px)
- Minimum height (default: 1080px)
- Perfect for filtering 4K, ultrawide, or specific display sizes

#### Aspect Ratio Filters
- Minimum aspect ratio (default: 1.5 for wide wallpapers)
- Maximum aspect ratio (default: 3.0 for ultrawide)
- Great for matching specific monitor configurations

#### Quality Filters
- Minimum file size (default: 100KB)
- Helps exclude low-quality or compressed images
- Ensures high-quality wallpapers

### 3. Automatic Categorization

Images are automatically organized into folders based on content:

- **nature**: Landscapes, mountains, forests, beaches, sunsets
- **space**: Galaxies, nebulas, planets, stars, cosmos
- **abstract**: Patterns, geometric designs, minimalist art
- **city**: Urban scenes, skylines, architecture
- **animals**: Wildlife, pets
- **tech**: Technology, computers, cyberpunk, futuristic
- **fantasy**: Fantasy art, dragons, magic
- **uncategorized**: Everything else

Categories are determined by analyzing:
- Image title
- Alt text
- Description
- URL path

### 4. Flexible Input Methods

#### Direct Image URLs
```bash
python cli.py -u https://example.com/img1.jpg https://example.com/img2.jpg
```

#### URL File
```bash
# urls.txt
https://example.com/wallpaper1.jpg
https://example.com/wallpaper2.png
# Comments supported

python cli.py -f urls.txt
```

#### Webpage Extraction
```bash
python cli.py -p https://example.com/wallpaper-gallery
```

### 5. User Interfaces

#### Graphical Interface (GUI)
- Visual controls for all settings
- Drag-and-drop URL input
- Real-time progress visualization
- Detailed activity logs
- Category statistics

#### Command-Line Interface (CLI)
- Full feature parity with GUI
- Scriptable and automatable
- Perfect for servers or automation
- Detailed help documentation

#### Quick Start Script
- Interactive setup wizard
- Dependency checking
- Example usage
- Easy for beginners

## File Organization

Downloaded wallpapers are organized as:

```
wallpapers/
├── nature/
│   ├── mountain_sunset_a1b2c3d4.jpg
│   └── forest_mist_e5f6g7h8.jpg
├── space/
│   ├── galaxy_spiral_i9j0k1l2.png
│   └── nebula_colors_m3n4o5p6.jpg
├── city/
│   └── tokyo_night_q7r8s9t0.jpg
└── uncategorized/
    └── wallpaper_u1v2w3x4.jpg
```

## Performance Features

- **Async I/O**: Non-blocking concurrent downloads
- **Connection Pooling**: Efficient network resource usage
- **Memory Efficient**: Streams large files without loading entire content
- **Rate Limiting**: Respects server resources with configurable concurrency

## Safety Features

- **Image Validation**: Verifies images before saving
- **Format Detection**: Supports JPG, PNG, WebP, BMP
- **Error Recovery**: Continues on failures, reports at end
- **Duplicate Detection**: Hash-based filename generation prevents duplicates

## Customization

All defaults can be customized via:
- Command-line arguments
- GUI controls
- `config.py` for global defaults
- Category keywords are fully customizable

## Use Cases

1. **Ultrawide Monitor Owners**: Filter for 21:9 or 32:9 aspect ratios
2. **4K Display Users**: Set minimum resolution to 3840x2160
3. **Bulk Downloads**: Download entire galleries with one command
4. **Automated Collections**: Script regular wallpaper updates
5. **Curated Collections**: Filter by quality and organize automatically

## Technical Stack

- **Python 3.7+**: Modern Python features
- **aiohttp**: High-performance async HTTP
- **Pillow**: Image processing and validation
- **BeautifulSoup4**: HTML parsing for webpage extraction
- **tkinter**: Native GUI (no external dependencies)
- **tqdm**: Beautiful CLI progress bars

## Security

- Uses latest patched versions of all dependencies
- No known CVE vulnerabilities
- Safe HTML parsing
- URL validation
- No arbitrary code execution
