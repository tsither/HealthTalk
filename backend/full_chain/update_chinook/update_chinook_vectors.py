from langchain_community.utilities.sql_database import SQLDatabase
import os
3
# from llama_index.core import SQLDatabase
from AnyScaleLLM import AnyScaleLLM
from sqlalchemy import MetaData, create_engine

from update_helper import generate_query, generate_response, SUBCHAIN_PROMPT, FULLCHAIN_PROMPT


ANYSCALE_API_KEY= os.getenv("ANYSCALE_API_KEY").strip()


QUESTION = "Under the artist 'Ted', create a new album called 'My Feelings'."



DB = SQLDatabase.from_uri("sqlite:////Users/mymac/LLM/Personal-Medical-Assistant/database/Chinook.db")

# engine = create_engine("sqlite:////Users/mymac/LLM/Personal-Medical-Assistant/database/Chinook.db")

# print(DB.get)
# print("\n\n")

# metadata_obj = MetaData()
# metadata_obj.reflect(bind=engine)

# print(metadata_obj.tables)
# metadata_obj.create_all(bind=engine)

# print("\n\n", metadata_obj.schema)

# print("\n\n\n" , metadata_obj.tables)


MODEL = "mistralai/Mistral-7B-Instruct-v0.1" 



llm = AnyScaleLLM(model_name=MODEL, api_key=ANYSCALE_API_KEY) #instantiate anyscale llm object
# print(llm)


query = generate_query(llm=llm, template=SUBCHAIN_PROMPT, question=QUESTION, db=DB)

print(f"\nTask: {QUESTION}\n\n")
print(f"Query: {query}\n\n")


response = generate_response(llm=llm, query=query, template=FULLCHAIN_PROMPT, question=QUESTION, db=DB)

print(f"Response: {response}")