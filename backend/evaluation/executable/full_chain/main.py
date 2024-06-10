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



#1 Write your Question
QUESTION = "How many albums are there?"

#2 Choose model
MODEL = "mistralai/Mistral-7B-Instruct-v0.1"                #### MODELS FROM ANYSCALE
                                                            #  "meta-llama/Meta-Llama-3-8B-Instruct"
                                                            #  "mistralai/Mistral-7B-Instruct-v0.1"
                                                            #  "meta-llama/Meta-Llama-3-70B-Instruct"
                                                            #  "codellama/CodeLlama-70b-Instruct-hf"



llm = AnyScaleLLM(model_name=MODEL, api_key=ANYSCALE_API_KEY) #instantiate anyscale llm object
 

#   Example database (Chinook.db) Fake database about music/artists/songs etc.
DB = SQLDatabase.from_uri("sqlite:////Users/mymac/LLM/Personal-Medical-Assistant/backend/evaluation/executable/full_chain/example_db/Chinook.db")


def main():


    query = generate_query(llm=llm, template=SUBCHAIN_PROMPT, question=QUESTION, db=DB)

    print(f"Question: {QUESTION}\n\n")
    print(f"Query: {query}\n\n")


    response = generate_response(llm=llm, query=query, template=FULLCHAIN_PROMPT, question=QUESTION, db=DB)

    print(f"Response: {response}")



if __name__ == "__main__":
    main()



