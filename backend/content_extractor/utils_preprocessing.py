import cv2
import matplotlib.pyplot as plt
from pathlib import Path


def read_image(path):
    return cv2.imread(path)

def save_image(image, path):
    cv2.imwrite(path, image)

def show_image(image):
    if image is None or image.size == 0:
        print("Image cannot be shown.")
        return None
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.axis('off')
    plt.show()

def get_image_files(directory):
    SUPPORTED_FORMATS = ['.png', '.jpg', '.jpeg', '.webp', '.tiff', '.bmp', '.pdf']
    image_files = []
    for file in Path(directory).iterdir():
        if file.is_file() and file.suffix.lower() in SUPPORTED_FORMATS:
            image_files.append(file)

    output = sorted(image_files)
    return output

@staticmethod
def is_grayscale(image):
    return len(image.shape) == 2

@staticmethod
def to_grayscale(image):
    if not is_grayscale(image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    return image