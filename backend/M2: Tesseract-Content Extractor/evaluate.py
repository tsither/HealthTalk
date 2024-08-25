from utils_evaluate import *
import csv

def main():
    final_results = []

    gold_standard_dir = "./data/json/"
    results_dir = "./results/txt/extracted/"

    # Process all gold standards
    gold_standards = process_gold_standards(gold_standard_dir)

    results_path = Path(results_dir)
    for eval_file in results_path.glob('*.json'):
        stem = eval_file.stem.split('_')[0]
        
        config = eval_file.stem.split('_')[1]
        ocr_module = eval_file.stem.split('_')[2]
        llm_model = eval_file.stem.split('_')[3]

        if stem in gold_standards:
            print(f"\nProcessing: {eval_file.name}")

            gold_data = gold_standards[stem]
            try:
                eval_data = load_json_file(str(eval_file))
            except Exception as e:
                print(e)
                continue

            comparison_results = preprocess_data(gold_data, eval_data)
            
            if comparison_results == None:
                y_true, y_pred = [1, 1, 1], [0, 0, 0]
            else:
                y_true, y_pred = prepare_for_sklearn_metrics(comparison_results)
            
            # Calculate metrics            
            print("Metrics:")
            (accuracy, precision, recall, f1) = calculate_metrics(y_true, y_pred)
            print(f"Accuracy: {accuracy}")
            print(f"Precision: {precision}")
            print(f"Recall: {recall}")
            print(f"F1-Score: {f1}")

            if np.isnan(accuracy):
                accuracy = 0.0

            list_to_add = [stem, config[6:], ocr_module, llm_model, float(accuracy), float(precision), float(recall), float(f1)]
            final_results.append(list_to_add)

        else:
            print(f"Warning: No matching gold standard found for {eval_file.name}")

    print(final_results)

    with open('./results/csv/evaluation.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        head = ['Filename', 'Config', 'OCR_module', 'LLM_model', "Accuracy", "Precision", "Recall", "F1_Score"]
        csvwriter.writerow(head)

        # Write each row from the list
        for row in final_results:
            csvwriter.writerow(row)
    


if __name__ == "__main__":
    main()