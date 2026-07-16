"""Natural-order image file sorter.

Sorts filenames so that numeric parts are compared as numbers:
  1.png, 2.png, 10.png  (not  1.png, 10.png, 2.png)
"""

import os
import re

SUPPORTED_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif', '.gif',
}


def natural_sort_key(filename: str):
    """Generate a sort key that orders numbers naturally.

    'img2.png' comes before 'img10.png'.
    """
    parts = re.split(r'(\d+)', filename.lower())
    result = []
    for part in parts:
        if part.isdigit():
            result.append((0, int(part)))   # numbers sort first, by value
        else:
            result.append((1, part))        # strings sort second, lexicographic
    return result


def get_sorted_images(directory: str) -> list[str]:
    """Get all image files from a directory, sorted in natural order.

    Args:
        directory: Path to the image directory.

    Returns:
        List of absolute paths to image files, sorted naturally.

    Raises:
        ValueError: If directory doesn't exist or contains no images.
    """
    if not os.path.isdir(directory):
        raise ValueError(f"Image directory not found: {directory}")

    images = []
    for filename in os.listdir(directory):
        ext = os.path.splitext(filename)[1].lower()
        if ext in SUPPORTED_EXTENSIONS:
            images.append(filename)

    if not images:
        raise ValueError(f"No supported images found in: {directory}")

    images.sort(key=natural_sort_key)

    return [os.path.join(directory, img) for img in images]
