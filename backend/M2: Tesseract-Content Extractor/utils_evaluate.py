import json
from fuzzywuzzy import fuzz
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import numpy as np
from pathlib import Path

def load_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)
    
def find_matching_key(target_key, dictionary, threshold=80):
    for key in dictionary.keys():
        if fuzz.ratio(target_key.lower(), key.lower()) >= threshold:
            return key
    
    return None

def preprocess_data(gold_data, eval_data):
    results = []

    # Find matching keys for top-level structures
    patient_info_key = find_matching_key('patient_information', eval_data)
    test_results_key = find_matching_key('test_results', eval_data)

    if not patient_info_key or not test_results_key:
        print(f"Warning: Could not find matching keys for patient information or test results.")
        return None
    
    # Check patient information
    if eval_data[patient_info_key] is None:
        for key in gold_data['patient_information']:
            gold_value = str(gold_data['patient_information'][key]).lower()
            results.append({
                'field': key,
                'correct': False,
                'gold_value': gold_value,
                'eval_value': "null"
            })
    else:
        for key in gold_data['patient_information']:
            matching_key = find_matching_key(key, eval_data[patient_info_key])
            if matching_key:
                gold_value = str(gold_data['patient_information'][key]).lower()
                eval_value = str(eval_data['patient_information'][matching_key]).lower()
                results.append({
                    'field': key,
                    'correct': gold_value == eval_value,
                    'gold_value': gold_value,
                    'eval_value': eval_value
                })

    # Check test results
    if eval_data[test_results_key] is None:
        for key in gold_data['test_results']:
            gold_value = str(gold_data['test_results'][key]).lower()
            results.append({
                'field': key,
                'correct': False,
                'gold_value': gold_value,
                'eval_value': "null"
            })
    else:
        for gold_test in gold_data['test_results']:
            
            matching_test = None
            for eval_test in eval_data[test_results_key]:

                if not isinstance(eval_test, dict):
                        print(f"Warning: eval_test is not a dictionary. Type: {type(eval_test)}")
                        continue

                test_name_key = find_matching_key('test_name', eval_test)
                
                if eval_test[test_name_key] == None:
                    eval_test[test_name_key] = "NA"

                if fuzz.ratio(gold_test['test_name'].lower(), eval_test[test_name_key].lower()) >= 80:
                    matching_test = eval_test
                    break

            if matching_test:
                test_result = {'test_name': gold_test['test_name']}
                for key in gold_test:
                    matching_key = find_matching_key(key, matching_test)
                    if matching_key:
                        gold_value = str(gold_test[key]).lower()
                        eval_value = str(matching_test[matching_key]).lower()
                        test_result[key] = {
                            'field': key,
                            'correct': gold_value == eval_value,
                            'gold_value': gold_value,
                            'eval_value': eval_value
                        }
                results.append(test_result)

    return results

def prepare_for_sklearn_metrics(comparison_results):
    y_true = []
    y_pred = []

    for item in comparison_results:
        if 'test_name' in item:  # It's a test result
            for key, value in item.items():
                if key != 'test_name':
                    y_true.append(1)  # The gold standard is always considered correct
                    y_pred.append(1 if value['correct'] else 0)
        else:  # It's a patient information field
            y_true.append(1)  # The gold standard is always considered correct
            y_pred.append(1 if item['correct'] else 0)

    return y_true, y_pred

def calculate_metrics(y_true, y_pred):
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)

    return accuracy, precision, recall, f1

def process_gold_standards(gold_standard_dir):
    gold_standards = {}
    gold_standard_path = Path(gold_standard_dir)
    
    for file_path in gold_standard_path.glob('*_goldstandard.json'):
        stem = file_path.stem.split('_')[0]  # Get the part before '_goldstandard'
        gold_data = load_json_file(str(file_path))
        gold_standards[stem] = gold_data
    
    return gold_standards