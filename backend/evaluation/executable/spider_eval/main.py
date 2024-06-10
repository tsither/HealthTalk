"""
Module Name: main.py
Description: This file takes an LLM and generates a chain to predict SQL queries from the Spider NL-to-SQL dataset
Author: Ted Sither
Date: 2024-06-08
"""


from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.llms import Ollama
from datasets import load_dataset
import time
import os

from helper import generate_query, data_processor, write_to_txt, read_json_file, clean_pred_txt, SUBCHAIN_PROMPT
from AnyScaleLLM import AnyScaleLLM


ANYSCALE_API_KEY= os.getenv("ANYSCALE_API_KEY").strip()

#TO DO BEFORE RUNNING FILE:
#1 Choose whether or not to use LLM from ollama
#2 Choose number of queries you want to evaluate
#3 Choose llm 

#1 Choose whether or not to use LLM from ollama
OLLAMA = False          

#2 Choose number of queries you want to evaluate
NUMBER_OF_QUERIES = 3

if OLLAMA:

    MODEL = "phi3"          #3 choose LLM
    LLM = Ollama(model=MODEL)      

else:
    MODEL = "meta-llama/Meta-Llama-3-8B-Instruct"              #3 choose LLM
    LLM = AnyScaleLLM(model_name=MODEL, api_key=ANYSCALE_API_KEY)
                                                                        #### MODELS FROM ANYSCALE
                                                                        #  "meta-llama/Meta-Llama-3-8B-Instruct"
                                                                        #  "mistralai/Mistral-7B-Instruct-v0.1"
                                                                        #  "meta-llama/Meta-Llama-3-70B-Instruct"
                                                                        #  "codellama/CodeLlama-70b-Instruct-hf"        #doesn't seem to work very well



SCHEMAS_DICT = read_json_file('Personal-Medical-Assistant/backend/evaluation/executable/spider_eval/helper_txt_files/schemas.json')      #dictionary containing all db_ids (as keys) and their schemas (as values)
# print("REACHED")

spider_dataset = load_dataset("xlangai/spider") #load spider dataset from huggingface
print(type(spider_dataset))




# Note: Not all databases are compatible, txt file contains all compatible databases, variable is read in 'data_processor' function
valid_datasets = 'Personal-Medical-Assistant/backend/evaluation/executable/spider_eval/helper_txt_files/valid_datasets.txt'

def main():

    #process Spider datasets          
    train_data, test_data = data_processor(dataset=spider_dataset, valid_txt=valid_datasets)          
    print(type(test_data))

    pred_queries = []
    gold_queries = []

    count = 0
        
    for tuple in test_data:
        
            db_id = tuple[0] + '.db'
            question = tuple[1]
            gold_query = tuple[2] + '\t' + tuple[0]

            schema = SCHEMAS_DICT[db_id]            #get schema for current database

            query = generate_query(schema=schema, template=SUBCHAIN_PROMPT, llm=LLM, question=question, ollama = OLLAMA)


            pred_queries.append(query)
            gold_queries.append(gold_query)

            print(f"DB_ID: {db_id}\n")
            print(f"Question: {question}\n\n")
            print(f"Query: \n{query}\n\n")
            

            print(f"Gold Query: \n{gold_query}")
            print(f'Processed: {count + 1}/{NUMBER_OF_QUERIES}')
            
            count += 1

            if count >= NUMBER_OF_QUERIES:
                    break


    # write queries to txt files for evaluation (Models go in their own folders)
    write_to_txt(pred_queries, 'Personal-Medical-Assistant/backend/evaluation/executable/spider_eval/eval_txts/' + MODEL + '_pred_' + str(NUMBER_OF_QUERIES) + '.txt')
    write_to_txt(gold_queries, 'Personal-Medical-Assistant/backend/evaluation/executable/spider_eval/eval_txts/' + MODEL + '_gold_' + str(NUMBER_OF_QUERIES) + '.txt')

    #  clean predicted txt file and re-write to same filename for evaluation, (admittedly a clunky implementation) but still necessary --> LLM doesn't produce perfectly structured query on its own line every time, often includes newline characters '\n' which is prohibited in evaluation.py
    clean_pred_txt('Personal-Medical-Assistant/backend/evaluation/executable/spider_eval/eval_txts/' + MODEL + '_pred_' + str(NUMBER_OF_QUERIES) + '.txt')





if __name__ == "__main__":
    main()




# arguments:
#   [gold file]        gold.sql file where each line is `a gold SQL \t db_id`
#   [predicted file]   predicted sql file where each line is a predicted SQL
#   [evaluation type]  "match" for exact set matching score, "exec" for execution score, and "all" for both
#   [database dir]     directory which contains sub-directories where each SQLite3 database is stored
#   [table file]       table.json file which includes foreign key info of each database
  

# python evaluation.py --gold gold.txt --pred pred.txt --etype "exec"  --db [database dir] --table tables.json 


