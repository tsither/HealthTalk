from openai import OpenAI
import pytesseract
import cv2
import os
import json
import argparse
from octoai.client import OctoAI
from octoai.text_gen import ChatMessage
from pdf2image import convert_from_path

def main():
    @staticmethod
    def read_image(path):
        return cv2.imread(path)

    @staticmethod
    def median_filter(image, kernel_size=3):
        return cv2.medianBlur(image, kernel_size)

    @staticmethod
    def process(image):
        result = pytesseract.image_to_string(image)
        result = result.replace("\n", " ")
        return result

    @staticmethod
    def chat_completion(prompt, question):

        client = OctoAI()
        completion = client.text_gen.create_chat_completion(
        model="gemma2-7b",
        messages=[
            ChatMessage(
                role="system",
                content=prompt,
            ),
            ChatMessage(role="user", content=question),
        ],
        temperature=0.1,
        max_tokens=8192-len(prompt),
        )

        response = completion.choices[0].message.content

        return response

    @staticmethod
    def extract_test_results(ocr_text):
        prompt = """
        CONTEXT: You are an expert in analyzing blood test results in a laboratory. Your work is extremely important and will be used in a life or death situation.  

        TASK: Given the following text extracted using an OCR from a blood test report, please extract and structure the following information:
        - Date of the test
        - Patient information (if available)
        - Test results, including:
            - Test name
            - Result value
            - Unit of measurement (if available)
            - Reference range (if available)

        Format the output as a JSON object. If a piece of information is not available, use null for its value.

        EXAMPLE OF YOUR EXPECTED OUTPUT:
        {
        "Date": "21.05.1995",
        "patient_information": {
            "patient_id": "12",
            "patient_name": "Max Mustermann",
            "patient_sex": "Female",
            "patient_age": "21"
            },
        "test_results": [
            {
                "test_name": "Hemoglobin (Hb)",
                "result_value": "12.5",
                "unit_of_measurement": "g/dl",
                "reference_range": "13.0-17.0 g/dL"
            },
            {
                "test_name": "Mean Corpuscular Volume (MCV)",
                "result_value": "87.75",
                "unit_of_measurement": "fL",
                "reference_range": "83-101 fL"
            }
            ]
        }
        
        IMPORTANT: Just return the JSON object. Do not make any further comment. Otherwise, the patient will die. Make sure that the JSON is efficiently formatted.
        """

        response = chat_completion(prompt, ocr_text)

        return response
    
    # Create the parser
    parser = argparse.ArgumentParser(description="Process a file")
    parser.add_argument('-f', '--file', type=str, required=True, help='Path to the input file')
    args = parser.parse_args()
    file_path = args.file
    
    if ".pdf" in file_path:
    	pages = convert_from_path(file_path)
    	file_path = file_path.replace(".pdf", ".tiff")
    	#print("Creating:",file_path)
    	pages[0].save(file_path, "tiff")

    image = read_image(str(file_path))
    image = median_filter(image)    
    text = process(image)
    answer = extract_test_results(text)

    while True:
        try:
            json_object = json.loads(answer)
        except ValueError as e:
            answer = extract_test_results(text)
            # print(f'ERROR: {e}')
            continue
        break

    print(json.dumps(json_object, indent=4))

if __name__ == "__main__":    
    main()
