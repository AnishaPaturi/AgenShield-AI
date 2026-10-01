from pathlib import Path
from PIL import Image

img_dir = Path("docs/college/extracted_images")
images = sorted(img_dir.glob("*.*"))

for img_path in images:
    with Image.open(img_path) as im:
        print(f"{img_path.name}: {im.size} (aspect {im.size[0]/im.size[1]:.2f})")
