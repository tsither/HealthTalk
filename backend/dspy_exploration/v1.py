import os
import dspy
from dspy import HFModel
ANYSCALE_API_KEY = os.getenv("ANYSCALE_API_KEY")
ANYSCALE_API_BASE = os.getenv("ANYSCALE_BASE_URL")


import requests

class Anyscale(dspy.HFModel):
    def __init__(self, model, **kwargs):
        self.model = model
        self.api_base = os.getenv("ANYSCALE_API_BASE")
        self.token = os.getenv("ANYSCALE_API_KEY")
        self.provider = "default"
        self.base_url = f"{self.api_base}/v1/models/{model}/completions"

    def basic_request(self, prompt: str, **kwargs):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        data = {
            **kwargs,
            "model": self.model,
            "prompt": prompt
        }
        response = requests.post(self.base_url, headers=headers, json=data)
        
        # Print response content for debugging
        print("Response Content:", response.content)
        
        try:
            response_json = response.json()
        except ValueError:
            raise Exception("Received invalid JSON response from server")
        
        return response_json


anyscale = Anyscale(model='mistralai/Mistral-7B-Instruct-v0.1')

print("\nLoaded model\n")
dspy.configure(lm=anyscale)


print("\nConfigured model\n")

#Example DSPy CoT QA program
qa = dspy.ChainOfThought('question -> answer')

print("\nChain of thought\n")


response = qa(question="What is the capital of Paris?") #Prompted to anyscale
print(response.answer)