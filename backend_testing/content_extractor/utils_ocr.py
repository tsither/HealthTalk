from pathlib import Path

def get_image_files(directory):
    SUPPORTED_FORMATS = ['.png', '.jpg', '.jpeg', '.webp', '.tiff', '.bmp']
    image_files = []
    for file in Path(directory).iterdir():
        if file.is_file() and file.suffix.lower() in SUPPORTED_FORMATS:
            image_files.append(file)
    return image_files