"""
Experimental script for testing contrast enhancement on receipt images.

This script is for development/testing purposes only.
"""
import os
from PIL import Image, ImageEnhance


def enhance_contrast(image, factor):
    """Return a new image with enhanced contrast."""
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(factor)


def main():
    cropped_dir = os.path.join('data', 'cropped2')
    enhanced_dir = os.path.join('data', 'enhanced')
    os.makedirs(enhanced_dir, exist_ok=True)
    images = sorted(os.listdir(cropped_dir))
    for img_name in images:
        img_path = os.path.join(cropped_dir, img_name)
        try:
            im = Image.open(img_path)
            contrast_im = enhance_contrast(im, factor=2)
            enhanced_img_path = os.path.join(enhanced_dir, img_name)
            contrast_im.save(enhanced_img_path)
            print(f"Enhanced and saved: {enhanced_img_path}")
        except Exception as e:
            print(f"Failed to process {img_name}: {e}")


if __name__ == "__main__":
    main()

