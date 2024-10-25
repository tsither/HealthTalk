import pytesseract
import cv2
import argparse
from pdf2image import convert_from_path
# Using 57/TesseractOCR/Gemma2

EXTRACTION_PROMPT = """
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

@staticmethod
def read_image(path):
    return cv2.imread(path)

@staticmethod
def basic(image):
    def is_grayscale(image):
        return len(image.shape) == 2

    def to_grayscale(image):
        if not is_grayscale(image):
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return image

    gray = to_grayscale(image)
    _, output = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    return output

@staticmethod
def median_filter(image, kernel_size=3):
    return cv2.medianBlur(image, kernel_size)

@staticmethod
def tesseract(image):
    result = pytesseract.image_to_string(image)
    result = result.replace("\n", " ")
    return result

def main():
    # Create the parser
    parser = argparse.ArgumentParser(description="Process a file")
    parser.add_argument('-f', '--file', type=str, required=True, help='Path to the input file')
    args = parser.parse_args()
    file_path = args.file
    
    if ".pdf" in file_path:
        pages = convert_from_path(file_path, poppler_path="")
        file_path = file_path.replace(".pdf", ".tiff")
     #print("Creating:",file_path)
        pages[0].save(file_path, "tiff")

    image = read_image(str(file_path))
    image = basic(image)
    image = median_filter(image)    
    text = tesseract(image)
    print(text)

    # answer = extract_test_results(text)

    # while True:
    #     try:
    #         json_object = json.loads(answer)
    #     except ValueError as e:
    #         answer = extract_test_results(text)
    #         # print(f'ERROR: {e}')
    #         continue
    #     break

    # print(json.dumps(json_object, indent=4))

if __name__ == "__main__":    
    main()