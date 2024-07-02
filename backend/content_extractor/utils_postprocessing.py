import re
from collections import defaultdict

def parse_ocr_results(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    # Regular expression to match each entry
    pattern = r'File: (.*?) - Config: (.*?) - \[(.*?)\]'
    
    # Find all matches
    matches = re.findall(pattern, content, re.DOTALL)

    # Organize the results
    results = defaultdict(dict)
    for file_path, config, text in matches:
        # Clean up the text (remove extra whitespace and newlines)
        clean_text = ' '.join(text.split())
        results[file_path]["Config"] = config
        results[file_path]["Input"] = clean_text

    return dict(results)