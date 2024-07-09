import re
from collections import defaultdict

def parse_ocr_results(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    # Regular expression to match each entry
    pattern = r'File: (.*?) - Time needed: (.*?) - Config: (.*?) - \[(.*?)\]'
    
    # Find all matches
    matches = re.findall(pattern, content, re.DOTALL)
    print(len(matches))

    idx = 0
    results = defaultdict(dict)

    for file_path, time, config, text in matches:
        clean_text = ' '.join(text.split())
        results[idx] = {'filepath': str(file_path), 'config': str(config), 'text': str(clean_text)}
        idx += 1
    
    return results