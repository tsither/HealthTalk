"""
Module Name: main.py
Description: Uses a LLM to answer a user question relating to an SQLite database
Author: Ted Sither
Date: 2024-06-09
"""


from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.llms import Ollama
import os
from helper import generate_query, generate_response, SUBCHAIN_PROMPT, FULLCHAIN_PROMPT
from AnyScaleLLM import AnyScaleLLM


ANYSCALE_API_KEY= os.getenv("ANYSCALE_API_KEY").strip()


MODEL = "mistralai/Mistral-7B-Instruct-v0.1"                #### MODELS FROM ANYSCALE
                                                            #  "meta-llama/Meta-Llama-3-8B-Instruct"
                                                            #  "mistralai/Mistral-7B-Instruct-v0.1"
                                                            #  "meta-llama/Meta-Llama-3-70B-Instruct"
                                                            #  "codellama/CodeLlama-70b-Instruct-hf"



llm = AnyScaleLLM(model_name=MODEL, api_key=ANYSCALE_API_KEY) #instantiate anyscale llm object
 

#   Example database (Chinook.db) Fake database about music/artists/songs etc.
DB = SQLDatabase.from_uri("sqlite://///Users/mymac/LLM/Personal-Medical-Assistant/database/med_assist.db")


def main():

    print("\n ----------------- Personal Medical Assistant ----------------- \n")
    while True:
        try:
            user_input = input("\n (Type 'exit' to quit) \n > ")
            if user_input.lower() == 'exit':
                break

            query = generate_query(llm=llm, template=SUBCHAIN_PROMPT, question=user_input, db=DB)

            print(f"Predicted DB Query: {query}\n\n")

            response = generate_response(llm=llm, query=query, template=FULLCHAIN_PROMPT, question=user_input, db=DB)

            print(f"Response: {response}")

        except Exception as e:
            print(f"Error: The previous inquiry led to an error on our end. Try again.")
            print(f"Error details: {str(e)}")



if __name__ == "__main__":
    main()



