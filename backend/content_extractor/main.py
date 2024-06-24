from utils import read_image, save_image, show_image, get_image_files
from preprocessing import Binarization, SkewCorrection, NoiseRemoval
from ocr import TesseractOCR
from postprocessing import GrammarCorrection, ResultExtraction, LLMProcessor

def test_configuration(image_path, preprocess_methods, ocr_method, postprocess_methods):
    image = read_image(image_path)
    
    for preprocess_class, method in preprocess_methods:
        image = getattr(preprocess_class, method)(image)
    
    text = ocr_method.process(image)
    
    for postprocess_class, method in postprocess_methods:
        if postprocess_class == LLMProcessor:
            text = getattr(postprocess_class, method)(text)
        else:
            text = getattr(postprocess_class, method)(text)
    
    return text

def main():
    image_files = get_image_files("./data/images/skew")

    for image_file in image_files:
        print(f"Processing: {image_file.name}")
        
        image_file = read_image(image_file)
        
        binarization = Binarization()
        correct = binarization.basic(image_file)

        skew_correction = SkewCorrection()
        correct = skew_correction.boxes(correct)

        noise_removal = NoiseRemoval()
        #show_image(noise_removal.unsharp_filter(correct))

        tesseract = TesseractOCR()
        text_tesseract = tesseract.process(correct)
        print("Tesseract OCR:")
        print(text_tesseract)
        
        print("-" * 50)


    
    '''
    configurations = [
        {
            "preprocess": [(Binarization, "otsu"), (SkewCorrection, "hough_transform")],
            "ocr": TesseractOCR,
            "postprocess": [(GrammarCorrection, "basic_rules"), (LLMProcessor, "extract_and_structure")]
        },
        {
            "preprocess": [(Binarization, "adaptive")],
            "ocr": EasyOCR,
            "postprocess": [(LLMProcessor, "extract_and_structure")]
        },
        # Add more configurations to test
    ]
    
    for config in configurations:
        result = test_configuration(
            image_path,
            config["preprocess"],
            config["ocr"],
            config["postprocess"]
        )
        print(f"Configuration: {config}")
        print(f"Result: {result}\n")
    '''
    

if __name__ == "__main__":
    main()