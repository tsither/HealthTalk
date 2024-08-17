
"""
Module Name: helper.py
Description: Module storing prompts for an LLM and necessary helper functions for module 'main.py'
Author: Ted Sither
Date: 2024-06-09

Notes: Current implementation only works with models from Anyscale AI api
"""

import json
from datetime import datetime, timezone


################################################################################################
################################################################################################

SUBCHAIN_PROMPT = """

You are a senior data engineer at Microsoft, responsible for constructing valid, intelligent SQL queries. 

Based on the schema below, write an SQL query that would answer the user's question:
{schema}

Question: {question}

Below are three conditions you MUST satisfy before returning the query:

Condition 1: Make sure to ONLY output an executable SQL Query, do not output any other information or irrelevant information or characters. 

Condition 2: The first character MUST be an SQL keyword, and the last character in the output must be a ;

Condition 3: The query MUST be on a single line only (newline character \\n is prohibited in query!)


IMPORTANT: Make sure to get the table names exactly correct (e.g. artist and NOT artists)

SQL Query:
"""
################################################################################################
################################################################################################


FULLCHAIN_PROMPT = """
Based on the question, SQL Query, and the SQL Execution, respond to the user's question:

Important: Only give the relevant information from the executed sql query as a response.


Question: {question}
SQL Query: {query}
SQL Execution: {executed_query}

Response:
"""

################################################################################################
################################################################################################

RAG_CONTEXT = """
You are a helpful medical assistant. 

Given the user question and the user medical data, answer the user's question to the best of your ability. The data is an sql database in JSON format. The data is the users personal medical data, so the user may use personal pronouns like 'my' when querying. It is okay to say you do not have the information the user is looking for.

Answer the users question to the best of your ability, ensuring to ONLY respond with information you find in the provided dataset. 

User question: {question}
User medical data: {user_data}

Current date: {current_date}

"""

################################################################################################
################################################################################################

def get_current_time():
    # Get current time in UTC
    utc_time = datetime.now(timezone.utc)
    
    # Format the date and time in European style
    # %d/%m/%Y for day/month/year
    # %H:%M:%S for 24-hour time
    formatted_time = utc_time.strftime("%d/%m/%Y %H:%M:%S")
    
    return formatted_time
 
def get_schema(db):
    """
    Gets schema from SQL database (db)
    """
    return db.get_table_info()


def run_query(query, db):
    """
    Takes query and runs query in database (db)
    """
    return db.run(query)


def generate_query(llm, template, question, db):
    """
    Generates an SQL query.

    Parameters:
    llm (Class): Class instance of large language model
    template (str): Prompt for llm to follow
    question (str): User's question for the database
    db (Class): LangChain SQL database instance

    Returns:
    out (str): SQL query
    """

    prompt = template.format(schema=get_schema(db),question=question)       #format template to include all necessary information (schema, question)
    sql_query = llm.chat_completion(prompt, question)         #generates sql query

    return sql_query


def generate_response(llm, query, template, question, db):
    """
    Generates an SQL query.

    Parameters:
    llm (Class): Class instance of large language model
    query (str): SQL query
    template (str): Prompt for llm to follow
    question (str): User's question for the database
    db (Class): LangChain SQL database instance

    Returns:
    response (str): Natural language response to user's question
    """

    executed_query = run_query(query, db=db)    #execute query on database

    print(f"\nExecuted query: {executed_query}\n")

    formatted_template = template.format(question=question, query=query, executed_query=executed_query)     #format template to include new information

    response = llm.chat_completion(formatted_template, question)    #generate llm response

    return response



def generate_RAG_query(llm, template, user_data, question):
    """
    Generates an SQL query.

    Parameters:
    llm (Class): Class instance of large language model
    template (str): Prompt for llm to follow
    question (str): User's question for the database

    Returns:
    out (str): LLM response
    """
    current_date = get_current_time()
    prompt = template.format(question=question, user_data=user_data, current_date=current_date)       #format template to include all necessary information (schema, question)
    answer = llm.chat_completion(prompt, question)         #generates sql query

    return answer


def read_json_file(file_path):
    """
    Reads a JSON file and returns its contents as a dictionary.

    Parameters:
    file_path (str): The path to the JSON file.

    Returns:
    dict: The contents of the JSON file as a dictionary.
    """

    with open(file_path, 'r') as file:
        data = json.load(file)
    return data