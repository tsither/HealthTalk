from dotenv import load_dotenv
from openai import OpenAI
import pytesseract
import numpy as np
import cv2
import os
import json
import argparse

def main():
    @staticmethod
    def read_image(path):
        return cv2.imread(path)

    @staticmethod
    def is_grayscale(image):
        return len(image.shape) == 2

    @staticmethod
    def to_grayscale(image):
        if not is_grayscale(image):
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return image

    @staticmethod
    def adaptive_gaussian(image):
        gray = to_grayscale(image)
        medblur = cv2.medianBlur(gray, 5)
        return cv2.adaptiveThreshold(medblur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    @staticmethod
    def moments(image):
        gray = to_grayscale(image)
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
        # Calculate image moments
        moments = cv2.moments(binary)

        # Compute the skew angle
        skew_angle = 0.5 * \
            np.arctan2(2 * moments['mu11'], moments['mu20'] - moments['mu02'])
        skew_angle = np.degrees(skew_angle)

        # Rotate the image to correct skew
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, skew_angle, 1.0)
        # Adjust the bounding box size to fit the entire rotated image
        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])
        new_w = int((h * sin) + (w * cos))
        new_h = int((h * cos) + (w * sin))
        M[0, 2] += (new_w / 2) - center[0]
        M[1, 2] += (new_h / 2) - center[1]

        # Rotate the image to correct skew
        rotated = cv2.warpAffine(
            image, M, (new_w, new_h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return rotated

    @staticmethod
    def conservative_filter(image, kernel_size=3):
        pad_size = kernel_size // 2
        padded = np.pad(image, pad_size, mode='edge')
        result = np.zeros_like(image)

        # total_iterations = padded.shape[0] - 2 * pad_size
        # quarter = total_iterations // 4

        for i in range(pad_size, padded.shape[0] - pad_size):
            # if i == pad_size + quarter:
            #     print("Loading: 25%")
            # elif i == pad_size + 2 * quarter:
            #     print("Loading: 50%")
            # elif i == pad_size + 3 * quarter:
            #     print("Loading: 75%")
            for j in range(pad_size, padded.shape[1] - pad_size):
                region = padded[i - pad_size:i + pad_size +
                                1, j - pad_size:j + pad_size + 1]
                min_val = np.min(region)
                max_val = np.max(region)
                if image[i - pad_size, j - pad_size] < min_val:
                    result[i - pad_size, j - pad_size] = min_val
                elif image[i - pad_size, j - pad_size] > max_val:
                    result[i - pad_size, j - pad_size] = max_val
                else:
                    result[i - pad_size, j - pad_size] = image[i -
                                                               pad_size, j - pad_size]
        return result

    @staticmethod
    def process(image):
        result = pytesseract.image_to_string(image)
        result = result.replace("\n", " ")
        return result

    @staticmethod
    def chat_completion(prompt, question):

        ANYSCALE_API_KEY = os.getenv("ANYSCALE_API_KEY").strip()

        client = OpenAI(
            base_url="https://api.endpoints.anyscale.com/v1",
            api_key=ANYSCALE_API_KEY
        )

        chat_completion = client.chat.completions.create(
            model='meta-llama/Meta-Llama-3-8B-Instruct',
            messages=[{"role": "system", "content": prompt},
                      {"role": "user", "content": question}],
            temperature=0.1
        )

        response = chat_completion.choices[0].message.content

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

    # Add the -f/--file argument
    parser.add_argument('-f', '--file', type=str, required=True, help='Path to the input file')


    # Parse the arguments
    args = parser.parse_args()

    # Access the file path
    file_path = args.file

    image = read_image(str(file_path))

    # print('Preprocessing file')

    image = conservative_filter(moments(adaptive_gaussian(image)))

    # print('Extracting file')
    text = process(image)

    # print('Extracting results')
    answer = extract_test_results(text)

    while True:
        try:
            json_object = json.loads(answer)
        except ValueError as e:
            # print(f'ERROR: {e}')
            continue
        break

    print(json_object)

    # # Create output JSON file path
    # input_dir = os.path.dirname(file_path)
    # input_filename = os.path.splitext(os.path.basename(file_path))[0]
    # output_json_path = os.path.join(input_dir, f"{input_filename}.json")

    # # Save the data as JSON
    # with open(output_json_path, 'w') as json_file:
    #     json.dump(json_object, json_file, indent=4)

    # print(f"Input file processed: {file_path}")
    # print(f"Output JSON saved: {output_json_path}")




if __name__ == "__main__":    
    main()
