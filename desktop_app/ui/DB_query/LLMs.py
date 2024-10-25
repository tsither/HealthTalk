import logging
from openai import OpenAI
from premai import Prem


# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

    
class langdock_LLM_Chatbot():
    def __init__(self, model_name, api_key, base_url, context):
        self.api_key = api_key
        self.model_name = model_name
        self.conversation_history = []
        self.base_url = base_url
        self.context = context

    def chat_completion(self, context, question):
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)


        messages = [
            {"role": "system", "content": context},
            {"role": "user", "content": question}
        ]

        self.conversation_history.append({"role": "user", "content": question})

        try:
            completion = client.chat.completions.create(
                model=self.model_name,
                messages=messages,
            )

            response = completion.choices[0].message.content
            logger.debug(f"API Response: {response}")

            self.conversation_history.append({"role": "assistant", "content": response})

            return response
        except Exception as e:
            logger.error(f"Error during chat completion: {e}")
            return f"An error occurred while processing your request: {e}"

    def clear_history(self):
        """Clear the conversation history."""
        self.conversation_history = []


    
class PREM_LLM_Chatbot():
    def __init__(self, model_name, api_key, project_id):
        self.model_name = model_name
        self.api_key = api_key
        self.project_id = project_id
        self.conversation_history = []

    def chat_completion(self, prompt, question):
        client = Prem(api_key=self.api_key)

        self.project_id = 5834

        self.conversation_history.append({"role": "user", "content": question})

        # Construct messages correctly
        messages = [
            {"role": "user", "content": question}
        ]

        try:
            response = client.chat.completions.create(
                project_id=self.project_id,
                system_prompt=prompt,
                messages=messages,
                model=self.model_name
            )

            content = response.choices[0].message.content

            logger.debug(f"API Response: {content}")

            self.conversation_history.append({"role": "assistant", "content": content})

            return content
        except Exception as e:
            logger.error(f"Error during chat completion: {e}")
            return f"An error occurred while processing your request: {e}"

    def clear_history(self):
        """Clear the conversation history."""
        self.conversation_history = []
