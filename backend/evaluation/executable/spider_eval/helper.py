"""
Module Name: helper.py
Description: Module storing prompt for an LLM and necessary helper functions for module 'main.py'
Author: Ted Sither
Date: 2024-06-09

Notes: Current implementation only works with models from Anyscale AI api
"""


from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser               #Getting SQL squery, then running query in db, so string is required
from langchain_core.runnables import RunnablePassthrough                #allows us to pass through a function so our chain can use it
import pandas as pd
import json
import re



########################################################################################################
########################################################################################################
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
########################################################################################################
########################################################################################################


def data_processor(dataset, valid_txt):
    """
    Process spider dataset

    Parameters:
    dataset (dataset object from huggingface): complete spider dataset (sql queries and their corresponding natural language questions)
    valid_txt (.txt): txt file containing the names of the databases in spider dataset that were able to be loaded properly (some databases had formatting issues)
                        --> only evaluating on the databases that are in 'valid_txt' file

    Returns:
    train_data (list):  list of tuples containing 1) db_id 2) NL question 3) gold_query associated with that question
    test_data (list): list of tuples containing 1) db_id 2) NL question 3) gold_query associated with that question
    """

    dataset_train = dataset['train'].to_pandas()    
    dataset_validation = dataset['validation'].to_pandas()

    with open(valid_txt, 'r') as file:
        lines = file.readlines()

    lines = [line.strip() for line in lines]

    new_train = pd.DataFrame()
    new_test = pd.DataFrame()

    for line in lines:

        result_train = dataset_train.loc[dataset_train['db_id'].str.contains(line, na=False)]

        result_test = dataset_validation.loc[dataset_validation['db_id'].str.contains(line, na=False)]

        new_train = pd.concat([new_train, result_train], ignore_index=True)

        new_test = pd.concat([new_test, result_test], ignore_index=True)


    train_data = []            #list of tuples containing ('db_id', 'question', 'gold query')

    test_data = []


    for idx, row in new_train.iterrows():
        entry = (row['db_id'],row['question'], row['query'])
        train_data.append(entry)

    for idx, row in new_test.iterrows():
        entry = (row['db_id'],row['question'], row['query'])
        test_data.append(entry)

        
    return train_data, test_data



def generate_query(schema, template, llm, question, ollama):
    """
    Generates an SQL query.

    Parameters:
    llm (Class): Class instance of large language model 
    template (str): Prompt for llm to follow
    question (str): User's question for the database
    ollama (Bool): choice of using ollama (if True) or anyscale API (if False) for LLM

    Returns:
    out (str): SQL query
    """

    if ollama:      #use locally hosted LLM

        prompt = ChatPromptTemplate.from_template(template)             #format prompt to include variables (schema, question)

        prompt.format(schema=schema, question=question)

        sql_chain = RunnablePassthrough.assign(schema= lambda _: schema) | prompt | llm | StrOutputParser()          

        sql_query = sql_chain.invoke({"question": {question}})


    else:           #use LLM via Anyscale AI api

        prompt = template.format(schema=schema,question=question)       #format template to include all necessary information (schema, question)
        sql_query = llm.chat_completion(prompt, question)               #generates sql sql_query

        return sql_query


def clean_pred_txt(prediction_txt_file):
    """
    Re-writes previously made pred.txt with proper formatting for evaluation 
    --> (i.e. each query is on its own line)

    Parameters:
    prediction_txt_file (.txt): txt file containing sql query predictions

    """

    with open(prediction_txt_file, 'r') as file:        #read file and write lines to list
        lines = file.readlines()

    single_string = ' '.join(lines)                             #turn all lines into single string
    removed_newlines_string = single_string.replace('\n', '')    #remove all newline characters

    pattern = r'\t(?=\d)'                                       #regex pattern to split by a tab character and digit
    split_result = re.split(pattern, removed_newlines_string)   #split

    formatted_list = []           

    for x in split_result:                                  
        no_digits = re.sub(r'\d', '', x)            #remove all digits and add new entries to 'formatted_list'
        formatted_list.append(no_digits)

    with open(prediction_txt_file, 'w') as file:     #write each entry in 'formatted_list' to original txt filename
        for line in formatted_list:
            file.write(line + '\n')



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


def write_to_txt(elements, filename):

    
        with open(filename, 'w') as file:
            count = 0
            for element in elements:
                
                file.write(element + '\t' + str(count) + '\n')
                count += 1


def read_json_file(file_path):
    """
    Read a JSON file and return its content as a dictionary.
    
    Parameters:
        file_path (str): The path to the JSON file.
    
    Returns:
        dict: The content of the JSON file as a dictionary.
    """
    with open(file_path, 'r') as file:
        data = json.load(file)
        
    return data
