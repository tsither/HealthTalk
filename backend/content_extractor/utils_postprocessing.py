import re
from collections import defaultdict

def parse_ocr_results(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    # Regular expression to match each entry
    pattern = r'File: (.*?) - Time needed: (.*?) - Config: (.*?) - \[(.*?)\]'
    
    # Find all matches
    matches = re.findall(pattern, content, re.DOTALL)

    # Organize the results
    results = defaultdict(dict)
    for file_path, time, config, text in matches:
        
        if "docTR" in str(config):
            continue

        clean_text = ' '.join(text.split())
        results[file_path]["Config"] = config
        results[file_path]["Input"] = clean_text
    
    return results