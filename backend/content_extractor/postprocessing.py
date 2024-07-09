import re
import os
import time
from dotenv import load_dotenv
from openai import OpenAI
from utils_postprocessing import parse_ocr_results
import json


class AnyScaleLLM():
    def __init__(self, model_name, api_key, base_url="https://api.endpoints.anyscale.com/v1"):
        self.base_url = base_url
        self.api_key = api_key
        self.model_name = model_name

    def chat_completion(self, prompt, question):

        client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )

        chat_completion = client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "system", "content": prompt},
                      {"role": "user", "content": question}],
            temperature=0.1
        )

        response = chat_completion.choices[0].message.content

        return response

    def extract_test_results(self, ocr_text):
        prompt = """
        CONTEXT: You are an expert in analyzing blood test results in a laboratory. Your work is extremely important and will be used in a life or death situation.  

        TASK: Given the following text extracted from a blood test report, please extract and structure the following information:
        - Date of the test
        - Patient information (if available)
        - Test results, including:
            - Test name
            - Result value
            - Unit of measurement
            - Reference range (if available)

        Format the output as a JSON object. If a piece of information is not available, use null for its value.

        EXAMPLE:
        {
        "Date": "14.15.2019",
        "patient_information": {
            "patient_id": 12d,
            "patient_name": "Max Mustermann",
            "patient_sex": "Male",
            "patient_age": 18
            },
        "test_results": [
            {
                "test_name": "Hemoglobin",
                "result_value": 5.8,
                "unit_of_measurement": "g/dL",
                "reference_range": "1.0 - 10.0"
            },{
            "test_name": "RBC count",
            "result_value": 2.5,
            "unit_of_measurement": "mill/cumm",
            "reference_range": "2.0 - 7.5"
            }
            ]
        }
        
        IMPORTANT: Just return the JSON object. Do not make any further comment. Otherwise, the patient will die.
        """
        response = self.chat_completion(prompt, ocr_text)

        return response

    def read_txt_file(self, file_path):
        ocr_results = parse_ocr_results(os.path.join(os.getcwd(), file_path))

        for key, value in ocr_results.items():
            config = ocr_results[key]["Config"]
            print(f"Prompting {key} with module {config}:")
            start = time.time()
            structured_results = self.extract_test_results(ocr_results[key]["Input"])
            ocr_results[key]["Output"] = structured_results
            end = time.time()
            time_elapsed = end - start
            print(f"Time nedded: {round(time_elapsed, 5)}")

        return ocr_results


def main():
    load_dotenv('./postprocessing_venv/key.env')  # Load the .env file

    ANYSCALE_API_KEY = os.getenv('API_KEY')  # Access the API key
    models = {
        # "meta-llama/Meta-Llama-3-8B-Instruct": "Llama37B",
        # "mistralai/Mistral-7B-Instruct-v0.1": "Mistral7B",
        "google/gemma-7b-it": "Gemma7B"
    }

    for key, model in models.items():
        print(f"Testing model: {model}")
        llm = AnyScaleLLM(model_name=key, api_key=ANYSCALE_API_KEY)
        output = llm.read_txt_file(
            "./results/txt/extracted/ocr_results_log.txt")        

        for key, value in output.items():
            print(f"Processing result from {key}")
            filename = os.path.splitext(os.path.basename(key))[0]
            config_name = output[key]["Config"]

            pathfile = f"{filename}_{config_name}_{model}"
            file_name_json = f"./results/txt/extracted/{pathfile}.json"
            with open(file_name_json, 'w', encoding='utf-8') as f:
                try:
                    json_object = json.loads(output[key]["Output"])
                except ValueError as e:
                    print(f"ERROR: {e}")
                    answer = str(output[key]["Output"])
                    print(f"Original answer: {answer}")
                    continue
                except Exception as e:
                    print(f"ERROR: {e}")
                    answer = str(output[key]["Output"])
                    print(f"Original answer: {answer}")
                    continue

                json.dump(json_object, f, ensure_ascii=False, indent=4)
                print(f"Results saved in: {file_name_json}\n")


if __name__ == "__main__":
    main()
