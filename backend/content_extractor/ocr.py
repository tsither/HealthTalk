from utils_ocr import get_image_files
from paddleocr import PaddleOCR
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
from PIL import Image
import torch
import time
import pytesseract
import keras_ocr
import easyocr
import os


class TesseractOCR:
    @staticmethod
    def process(image):
        result = pytesseract.image_to_string(image)
        result = result.replace("\n", " ")
        return result


class KerasOCR:
    @staticmethod
    def process(image):
        torch.cuda.empty_cache()
        pipeline = keras_ocr.pipeline.Pipeline()
        read_image = keras_ocr.tools.read(image)
        prediction_groups = pipeline.recognize([read_image])
        # prediction_groups is a list of (word, box) tuples
        output = [str(y[0]) for i in prediction_groups for y in i]
        return " ".join(output)

    def finetune_detector(data_dir):
        # https://keras-ocr.readthedocs.io/en/latest/examples/fine_tuning_detector.html
        # https://www.kaggle.com/discussions/general/243859
        return None

    def finetune_recognizer(data_dir):
        # https://keras-ocr.readthedocs.io/en/latest/examples/fine_tuning_recognizer.html
        return None


class EasyOCR:
    @staticmethod
    def process(image):
        torch.cuda.empty_cache()
        reader = easyocr.Reader(['en'], gpu=True)
        result = reader.readtext(image)
        output = [j for _, j, _ in result]
        return " ".join(output)


class PaddlePaddle:
    @staticmethod
    def process(image):
        # need to run only once to download and load model into memory
        ocr = PaddleOCR(use_angle_cls=True, lang='en',
                     use_gpu=True, show_log=False)
        result = ocr.ocr(image, cls=True, det=True, rec=True)
        output = [j[1][0] for i in result for j in i]
        return " ".join(output)


class docTR:
    @staticmethod
    def extract_text_from_document(document):
        # Extract all the words and join them into a single string
        text = " ".join(
            word.value
            for page in document.pages
            for block in page.blocks
            for line in block.lines
            for word in line.words
        )
        return text

    @staticmethod
    def process(image):
        model = ocr_predictor(det_arch='db_resnet50',
                              reco_arch='crnn_vgg16_bn', pretrained=True)
        single_img_doc = DocumentFile.from_images(image)
        result = model(single_img_doc)
        output = docTR.extract_text_from_document(result)
        return output


def main():
    # Define the OCR classes and their corresponding process methods
    ocr_methods = {
        "TesseractOCR": TesseractOCR.process,
        "KerasOCR": KerasOCR.process,
        "EasyOCR": EasyOCR.process,
        "PaddleOCR": PaddlePaddle.process,
        "docTR": docTR.process
    }

    
    # Define the directory containing image files
    image_files = get_image_files("./results/images/preprocessed/")
    processed_dir = "./results/txt/extracted/"
    log_file_path = os.path.join(processed_dir, "ocr_results_log.txt")

    os.makedirs(processed_dir, exist_ok=True)
    
    with open(log_file_path, 'w') as log_file:
        for image_file in image_files:
            image_path = os.path.join(os.getcwd(), image_file)
            print(f"Processing file: {image_file}")
            
            for method_name, method in ocr_methods.items():
                start = time.time()
                try:
                    output = method(image_path)
                except ValueError as ve:
                    if "unable to read file" in str(ve):
                        print(f'COMMON ERROR: {ve}')
                except Exception as e:
                    if "CUDA out of memory" in str(e):
                        print(f'COMMON ERROR: {e}')
                    elif "can not handle images with 32-bit samples" in str(e):
                        print(f'COMMON ERROR: {e}')
                    else:
                        print(f'NEW ERROR: {e}')

                end = time.time()
                time_elapsed = end - start
                print(f"Method: {method_name}")
                print(f"Time nedded: {round(time_elapsed, 5)}")
                print(f"Output: {str(output)}")
                log_file.write(f"File: {image_file} - Time needed: {time_elapsed} - Config: {method_name} - [{output}]\n")
                log_file.flush()
                
            print(f"Logged results for: {image_file}\n")
            print("-" * 50)
    
    print(f"Processing log saved to: {log_file_path}")

    

if __name__ == "__main__":
    main()
