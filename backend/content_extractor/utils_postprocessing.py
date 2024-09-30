import re
from collections import defaultdict
from pathlib import Path

def parse_ocr_results(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    # Regular expression to match each entry
    pattern = r'File: (.*?) - OCR: (.*?) - Time needed: (.*?) - \[(.*?)\]'
    
    # Find all matches
    matches = re.findall(pattern, content, re.DOTALL)

    idx = 0
    results = defaultdict(dict)

    for file_path, ocr, time, text in matches:
        clean_text = ' '.join(text.split())
        results[idx] = {'filepath': str(file_path), 'ocr': str(ocr), 'text': str(clean_text)}
        idx += 1
    
    return results

def get_txt_files(directory):
    SUPPORTED_FORMATS = ['.txt']
    txt_files = []
    for file in Path(directory).iterdir():
        if file.is_file() and file.suffix.lower() in SUPPORTED_FORMATS:
            txt_files.append(file)

    output = sorted(txt_files)
    return output
