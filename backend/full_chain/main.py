"""
Module Name: main.py
Description: Uses a LLM to answer a user question relating to an SQLite database
Author: Ted Sither
Date: 2024-06-09
"""


from langchain_community.utilities.sql_database import SQLDatabase
import os
from helper import generate_query, generate_response, SUBCHAIN_PROMPT, FULLCHAIN_PROMPT
from AnyScaleLLM import AnyScaleLLM
from guardrails import Guard
from guardrails.hub import NSFWText

from topic_guardrail import check_user_input, CHECK_USER_PROMPT

# Use the Guard with the validator
guard_NSFW = Guard().use(
    NSFWText, threshold=0.8, validation_method="sentence", on_fail="exception"
)



ANYSCALE_API_KEY= os.getenv("ANYSCALE_API_KEY").strip()
ANYSCALE_BASE_URL = os.getenv("ANYSCALE_BASE_URL")

MODEL = "mistralai/Mistral-7B-Instruct-v0.1:Ted:iGZ9Hwf"                #### MODELS FROM ANYSCALE
                                                            #  "meta-llama/Meta-Llama-3-8B-Instruct"
                                                            #  "mistralai/Mistral-7B-Instruct-v0.1"
                                                            #  "meta-llama/Meta-Llama-3-70B-Instruct"
                                                            #  "codellama/CodeLlama-70b-Instruct-hf"


llm = AnyScaleLLM(model_name=MODEL, api_key=ANYSCALE_API_KEY, base_url=ANYSCALE_BASE_URL) #instantiate anyscale llm object
 

DB = SQLDatabase.from_uri("sqlite://///Users/mymac/LLM/Personal-Medical-Assistant/database/med_assist.db")


def main():

    print("\n ----------------- Personal Medical Assistant ----------------- \n")
    while True:
        
        try:
            user_input = input("\n (Type 'exit' to quit) \n > ")
            if user_input.lower() == 'exit':
                break
            
            # Test failing response
            guard_NSFW.validate(user_input)


            query = generate_query(llm=llm, template=SUBCHAIN_PROMPT, question=user_input, db=DB)

            print(f"Predicted DB Query: {query}\n\n")

            response = generate_response(llm=llm, query=query, template=FULLCHAIN_PROMPT, question=user_input, db=DB)

            print(f"Response: {response}")

        except Exception as e:
            # print(f"Error: The previous inquiry led to an error on our end. Try again.")
            print(f"Error details: {str(e)}")



if __name__ == "__main__":
    main()



