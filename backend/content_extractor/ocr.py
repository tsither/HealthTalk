import pytesseract
#from easyocr import Reader 
#import keras_ocr
#from paddleocr import PaddleOCR
#import mmocr

class TesseractOCR:
    @staticmethod
    def process(image):
        return pytesseract.image_to_string(image)

'''
class docTR:
    @staticmethod
    def process(image):
        model = ocr_predictor(det_arch='db_resnet50', reco_arch='crnn_vgg16_bn', pretrained=True)
        DocumentFile.from_images(image)
        result = model(doc)
        return result
'''

'''
class EasyOCR:
    @staticmethod
    def process(image):
        reader = Reader(['en'])  # Initialize with English language
        result = reader.readtext(image)
        return '\n'.join([text for text, _, _ in result])

class KerasOCR:
    @staticmethod
    def process(image):
        pipeline = keras_ocr.pipeline.Pipeline()
        prediction_groups = pipeline.recognize([image])
        return '\n'.join([text for text, _ in prediction_groups[0]])



class PaddleOCR:
    @staticmethod
    def process(image):
        ocr = PaddleOCR()
        result = ocr.ocr(image)
        return '\n'.join([text for text, _, _ in result])

class MMOCR:
    @staticmethod
    def process(image):
        result = mmocr.ocr(image)
        return result
'''

