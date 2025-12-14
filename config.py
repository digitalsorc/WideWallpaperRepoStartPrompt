"""Configuration settings for the wallpaper scraper."""

# Default download settings
DEFAULT_OUTPUT_DIR = "wallpapers"
DEFAULT_CONCURRENT_DOWNLOADS = 5
DEFAULT_TIMEOUT = 30

# Default filter settings
DEFAULT_MIN_WIDTH = 1920
DEFAULT_MIN_HEIGHT = 1080
DEFAULT_MIN_ASPECT_RATIO = 1.5  # For wide wallpapers
DEFAULT_MAX_ASPECT_RATIO = 3.0
DEFAULT_MIN_FILE_SIZE = 100 * 1024  # 100 KB

# Supported image formats
SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.webp', '.bmp']

# User agent for requests
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# Category keywords for automatic categorization
CATEGORY_KEYWORDS = {
    'nature': ['nature', 'landscape', 'mountain', 'forest', 'ocean', 'beach', 'sunset', 'sunrise'],
    'space': ['space', 'galaxy', 'nebula', 'planet', 'star', 'cosmos', 'astronomy'],
    'abstract': ['abstract', 'pattern', 'geometric', 'minimalist', 'artistic'],
    'city': ['city', 'urban', 'skyline', 'architecture', 'building', 'street'],
    'animals': ['animal', 'wildlife', 'cat', 'dog', 'bird', 'lion', 'tiger'],
    'tech': ['technology', 'computer', 'digital', 'cyberpunk', 'futuristic'],
    'fantasy': ['fantasy', 'dragon', 'magic', 'medieval', 'artwork'],
}
