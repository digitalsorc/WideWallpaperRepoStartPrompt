# Wallpaper Scraper

A powerful Python tool for bulk downloading high-resolution wallpapers with advanced filtering and automatic categorization. Features both CLI and GUI interfaces for easy use.

## Features

- 🖼️ **Bulk Download**: Download multiple images concurrently from direct URLs or webpages
- 🔍 **Advanced Filtering**: Filter by resolution, aspect ratio, and file size
- 📁 **Auto-Categorization**: Automatically organize images into subfolders based on metadata
- 🎨 **Dual Interface**: Choose between command-line or graphical interface
- ⚡ **Concurrent Downloads**: Speed up downloads with configurable parallel processing
- 📊 **Progress Tracking**: Real-time progress updates and statistics
- 🎯 **Quality Control**: Ensure only high-quality wallpapers are downloaded

## Installation

1. Clone the repository:
```bash
git clone https://github.com/digitalsorc/WideWallpaperRepoStartPrompt.git
cd WideWallpaperRepoStartPrompt
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Graphical Interface (GUI)

Launch the GUI application:
```bash
python gui.py
```

The GUI provides:
- Easy URL input (paste URLs or load from file)
- Visual filter configuration
- Real-time progress tracking
- Download statistics and logs

### Command-Line Interface (CLI)

#### Basic Usage

Download from direct image URLs:
```bash
python cli.py -u https://example.com/image1.jpg https://example.com/image2.jpg
```

Download from URLs in a file:
```bash
python cli.py -f urls.txt
```

Extract and download images from a webpage:
```bash
python cli.py -p https://example.com/wallpapers-page
```

#### Advanced Options

Custom resolution filters:
```bash
python cli.py -u https://example.com/image.jpg --min-width 2560 --min-height 1440
```

Custom aspect ratio (for ultrawide monitors):
```bash
python cli.py -f urls.txt --min-aspect 2.0 --max-aspect 3.5
```

Concurrent downloads with custom output directory:
```bash
python cli.py -f urls.txt --concurrent 10 -o ./my-wallpapers
```

Disable automatic categorization:
```bash
python cli.py -f urls.txt --no-categorize
```

#### CLI Options

**Input Options** (one required):
- `-u, --urls`: Direct image URLs (space-separated)
- `-f, --file`: Text file with URLs (one per line)
- `-p, --page`: Webpage URL to extract images from

**Output Options**:
- `-o, --output`: Output directory (default: `wallpapers`)

**Filter Options**:
- `--min-width`: Minimum width in pixels (default: 1920)
- `--min-height`: Minimum height in pixels (default: 1080)
- `--min-aspect`: Minimum aspect ratio (default: 1.5)
- `--max-aspect`: Maximum aspect ratio (default: 3.0)
- `--min-size`: Minimum file size in KB (default: 100)

**Download Options**:
- `--concurrent`: Number of concurrent downloads (default: 5)
- `--timeout`: Download timeout in seconds (default: 30)
- `--no-categorize`: Disable automatic categorization

## File Formats

### URL File Format

Create a text file with one URL per line:
```
https://example.com/image1.jpg
https://example.com/image2.jpg
# Comments start with #
https://example.com/wallpapers-page  # Can extract from pages too
```

## Categorization

Images are automatically categorized into subfolders based on metadata and descriptions:

- **nature**: Landscapes, mountains, forests, oceans, beaches
- **space**: Galaxies, nebulas, planets, stars
- **abstract**: Patterns, geometric designs, minimalist art
- **city**: Urban scenes, skylines, architecture
- **animals**: Wildlife, pets
- **tech**: Technology, computers, cyberpunk
- **fantasy**: Fantasy art, dragons, magical themes
- **uncategorized**: Images that don't match any category

## Examples

### Example 1: Download Ultrawide Wallpapers
```bash
python cli.py -f ultrawide-urls.txt \
  --min-width 3440 \
  --min-height 1440 \
  --min-aspect 2.3 \
  --max-aspect 2.5 \
  -o ultrawide-wallpapers
```

### Example 2: Download from Webpage with Quality Filters
```bash
python cli.py -p https://wallpaper-site.com/gallery \
  --min-width 2560 \
  --min-height 1440 \
  --min-size 500 \
  --concurrent 8
```

### Example 3: Quick Download Without Categorization
```bash
python cli.py -u https://example.com/image.jpg --no-categorize
```

## Output Structure

Downloaded wallpapers are organized in the following structure:

```
wallpapers/
├── nature/
│   ├── mountain_sunset_a1b2c3d4.jpg
│   └── ocean_waves_e5f6g7h8.jpg
├── space/
│   ├── nebula_colors_i9j0k1l2.jpg
│   └── galaxy_spiral_m3n4o5p6.jpg
├── abstract/
│   └── geometric_pattern_q7r8s9t0.jpg
└── uncategorized/
    └── wallpaper_u1v2w3x4.jpg
```

## Configuration

Default settings can be modified in `config.py`:

- Download directories
- Default filter values
- Category keywords
- Supported image formats
- Concurrent download limits

## Dependencies

- `requests`: HTTP requests
- `Pillow`: Image processing and validation
- `beautifulsoup4`: HTML parsing for webpage extraction
- `aiohttp`: Asynchronous HTTP downloads
- `tqdm`: Progress bars (CLI)
- `validators`: URL validation

## Tips

1. **For Ultrawide Monitors**: Use `--min-aspect 2.0` or higher
2. **For 4K Displays**: Use `--min-width 3840 --min-height 2160`
3. **Faster Downloads**: Increase `--concurrent` (but respect server limits)
4. **Quality Control**: Adjust `--min-size` to filter out low-quality images
5. **Test First**: Try with a few URLs before bulk downloading

## Troubleshooting

**Issue**: Downloads are slow
- **Solution**: Increase `--concurrent` value

**Issue**: Many images are filtered out
- **Solution**: Lower the filter thresholds (min-width, min-height, etc.)

**Issue**: Images not categorizing properly
- **Solution**: Add custom keywords to `config.py`

**Issue**: Timeout errors
- **Solution**: Increase `--timeout` value

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.
