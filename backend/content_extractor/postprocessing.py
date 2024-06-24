import re
from ollama import Client

class GrammarCorrection:
    @staticmethod
    def basic_rules(text):
        # Implement basic grammar correction rules
        pass

class ResultExtraction:
    @staticmethod
    def regex(text):
        # Implement regex-based result extraction
        pass

class LLMProcessor:
    client = Client()
    
    @staticmethod
    def extract_and_structure(text, model="llama2"):
        prompt = f"""
        Extract the following information from the given text of a blood test result:
        - Date
        - Glucose level
        - Magnesium level
        - Vitamin D level
        - Any other test results present

        Format the output as a CSV string with headers.

        Text:
        {text}
        """
        
        response = LLMProcessor.client.generate(model=model, prompt=prompt)
        return response['response']

# Add more postprocessing classes as needed