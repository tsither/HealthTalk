
from langchain_core.runnables.base import Runnable
import openai


class AnyScaleLLM():
    def __init__(self, model_name, api_key, base_url="https://api.endpoints.anyscale.com/v1"):
        self.base_url = base_url
        self.api_key = api_key
        self.model_name = model_name

    def chat_completion(self, prompt, question):

        client = openai.OpenAI(
            base_url = self.base_url,
            api_key = self.api_key
        )
        
        chat_completion = client.chat.completions.create(
        model=self.model_name,
        messages=[{"role": "system", "content": prompt}, 
                {"role": "user", "content": question}],
        temperature=0.1

        )

        response = chat_completion.choices[0].message.content

        return response
    


