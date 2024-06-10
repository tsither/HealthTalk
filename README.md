# Personal-Medical-Assistant
Using LLMs to create accessible database of health info



### Runnable files:

#### Full chain execution
Personal-Medical-Assistant/backend/evaluation/executable/full_chain/main.py
LLM generates SQL query given a question, executes query, and returns information. 

Edit file to modify specific details like:
- Which LLM to use
- Question
- Database? *Currently only functional with toy database (Chinook.db)

#### Evaluate performance on Spider Dataset:
Personal-Medical-Assistant/backend/evaluation/executable/spider_eval/main.py

Edit file to modify specific details like:
- Which LLM to use
- The number of queries you want to generate and evaluate

Important: 
    This file only creates queries formatted to be evaluated. Formal evaluation is done using the Spider dataset functionality in their 'evaluation.py' module. Therefore, it is necessary to download Spider dataset repository from github to run the evaluation.  
