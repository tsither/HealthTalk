import os
import dspy

ANYSCALE_API_KEY = os.getenv("ANYSCALE_API_KEY")
ANYSCALE_API_BASE = os.getenv("ANYSCALE_BASE_URL")


anyscale = dspy.Anyscale(model='mistralai/Mistral-7B-Instruct-v0.1')
self.api_base = os.getenv("ANYSCALE_API_BASE")
self.token = os.getenv("ANYSCALE_API_KEY")
dspy.configure(lm=anyscale)
response = anyscale(prompt='What is the capital of France?')
print(response)