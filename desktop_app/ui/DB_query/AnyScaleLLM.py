from langchain_core.runnables.base import Runnable
import openai
import logging

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class AnyScaleLLM():
    def __init__(self, model_name, api_key, base_url="https://api.endpoints.anyscale.com/v1"):
        self.base_url = base_url
        self.api_key = api_key
        self.model_name = model_name
        self.conversation_history = []


    def chat_completion(self, prompt, question):
        client = openai.OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )

        self.conversation_history.append({"role": "user", "content": question})

        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": question}
        ] + self.conversation_history

        try:
            chat_completion = client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.1
            )

            response = chat_completion.choices[0].message.content
            logger.debug(f"API Response: {response}")
            
            self.conversation_history.append({"role": "assistant", "content": response})

            return response
        except Exception as e:
            logger.error(f"Error during chat completion: {e}")
            return "An error occurred while processing your request."
        
        
    def clear_history(self):
        """Clear the conversation history."""
        self.conversation_history = []

        
class Chatbot:
    def __init__(self, model_name, api_key, system_prompt):
        self.llm = AnyScaleLLM(model_name, api_key)
        self.system_prompt = system_prompt

    def chat(self, user_input):
        return self.llm.chat_completion(self.system_prompt, user_input)

    def clear_chat_history(self):
        self.llm.clear_history()