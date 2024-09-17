import os
import time
from dotenv import load_dotenv
from utils_postprocessing import parse_ocr_results
import json
from together import Together
import ollama

class TogetherAI():
    def __init__(self, model_name, api_key, log_filepath):
        self.log_filepath = log_filepath
        self.api_key = api_key
        self.model_name = model_name

    def chat_completion(self, prompt, question):

        # client = Together(
        #     api_key=self.api_key
        # )

        # chat_completion = client.chat.completions.create(
        #     model=self.model_name,
        #     messages=[{"role": "system", "content": prompt},
        #               {"role": "user", "content": question}],
        #     temperature=0.1,
        #     top_p=0.2,
        #     top_k=20
        # )

        # response = chat_completion.choices[0].message.content
        # print(response)

        response = ollama.chat( 
            model=str(self.model_name), 
            messages=[{"role": "system", "content": prompt},
                      {"role": "user", "content": question}])
        response = response['message']['content']
        return response

    def extract_test_results(self, ocr_text):
        prompt = """
        CONTEXT: You are an expert in analyzing blood test results in a laboratory. Your work is extremely important and will be used in a life or death situation.  

        TASK: Given the following text extracted from a blood test report, please extract and structure the following information:
        - Date of the test (if available)
        - Patient information (if available)
        - Test results, including:
            - Test name
            - Result value
            - Unit of measurement
            - Reference range (if available)

        Format the output as a JSON object. If a piece of information is not available, use null for its value.

        EXAMPLE:
        {
        "Date": "XX.XX.XXX",
        "patient_information": {
            "patient_id": [FILL],
            "patient_name": "[FILL]",
            "patient_sex": "[FILL]",
            "patient_age": [FILL]
            },
        "test_results": [
            {
                "test_name": "[FILL]",
                "result_value": [FILL],
                "unit_of_measurement": "[FILL]",
                "reference_range": "[FILL]"
            }
            ]
        }
        
        IMPORTANT: Just return the code of the JSON object. Do not make any further comment and do not add "json" before the object. Otherwise, the patient will die.
        """
        exit = False
        while exit == False:
            try:
                response = self.chat_completion(prompt, ocr_text)
                time.sleep(2)
                exit = True
            except Exception as e:
                print(e)
                time.sleep(5)
                continue

        return response

    def read_txt_file(self, file_path, model):
        ocr_results = parse_ocr_results(os.path.join(os.getcwd(), file_path))

        for key, value in ocr_results.items():
            print('Progress', key, len(ocr_results.items()))
            file_path_str = str(value['filepath'])
            file_path_str = "/" + file_path_str
            print(f"Prompting extracted text from {value['filepath']} using module {value['ocr']}")
            start = time.time()
            structured_results = self.extract_test_results(value['text'])
            ocr_results[key]["Output"] = structured_results
            end = time.time()
            time_elapsed = end - start

            with open(self.log_filepath, 'a+') as log_file_path:
                log_file_path.write(f"File: {file_path_str} - OCR: {value['ocr']} - LLM: {model} - Time needed: {time_elapsed} \n")
                log_file_path.flush()

        return ocr_results


def main():
    load_dotenv('./postprocessing_venv/key.env')  # Load the .env file
    TOGETHER_API_KEY = os.environ.get('API_KEY')  # Access the API key
    models = {
        #   "llama3.1": "Llama3-8B",
        #  "qwen2:7b": "Qwen2-7B",
        # "phi3:14b": "Phi3-14B",
        #  "gemma2" : "Gemma2-9B",
         "mistral-nemo" : "Mistral-12B",
    }

    for key, model in models.items():
        log_file_path = os.path.join("./results/txt/extracted/", f"postprocessing_log_{model}.txt")
        print(f"Testing model: {model}")
        llm = TogetherAI(model_name=key, api_key=TOGETHER_API_KEY, log_filepath=log_file_path)
        
        output = llm.read_txt_file(
            "./results/txt/extracted/ocr_results_log.txt", model)        

        for key, value in output.items():
            print(f"Processing result from {value['filepath']} to json object")
            filename = os.path.splitext(os.path.basename(value['filepath']))[0]
            config_name = value["ocr"]
            pathfile = f"{filename}_{config_name}_{model}"
            file_name_json = f"./results/txt/extracted/{pathfile}.json"

            if "Output" not in value:
                continue

            with open(file_name_json, 'w', encoding='utf-8') as f:
                try:
                    json_object = json.loads(output[key]["Output"])
                except ValueError as e:
                    print(f"COMMON ERROR (JSON object): {e}")
                    answer = str(output[key]["Output"])
                    print(f"Original answer: {answer}")
                    continue
                except Exception as e:
                    print(f"NEW ERROR (JSON object): {e}")
                    answer = str(output[key]["Output"])
                    print(f"Original answer: {answer}")
                    continue

                try:
                    json.dump(json_object, f, ensure_ascii=False, indent=4)
                except Exception as e:
                    print(f"NEW ERROR (JSON dumping): {e}")
                    continue

                print(f"Results saved in: {file_name_json}\n")
                print("-" * 50)


if __name__ == "__main__":
    main()
