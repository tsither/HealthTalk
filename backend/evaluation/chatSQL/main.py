from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.llms import Ollama

from helper import construct_prompt, get_schema, generate_query, run_query, generate_response


LLM = Ollama(model="phi3")

DB = SQLDatabase.from_uri("sqlite:///Chinook.db")



def main():


    agent_executor = create_sql_agent(LLM, db=DB, verbose=False)






if __name__ == "__main__":
    main()