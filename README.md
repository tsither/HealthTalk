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

Spider Dataset: https://github.com/taoyds/spider


##### Example Eval Metrics

Mistralai and llama3 70B are the best performers on 200 queries out of the box (no fine-tuning or training)

Count: (number of queries organized by difficultly - true for all runs except phi3 model)
- easy --> 52
- medium --> 102
- hard --> 30
- extra --> 16
- all --> 200

Meta-Llama-3-70B-Instruct: (200_queries)

Execution Accuracy:
- easy --> 0.558
- medium --> 0.353 
- hard --> 0.367
- extra --> 0.250
- all --> .400 

*****************************************************

Mistral-7B-Instruct: (200 queries) 

Execution Accuracy:
- easy --> 0.538
- medium --> 0.235  
- hard --> 0.167
- extra --> 0.000
- all --> 0.285


*****************************************************

Meta-Llama-3-8B-Instruct: (200 queries) 

Execution Accuracy:
- easy --> 0.481 
- medium --> 0.196  
- hard --> 0.133
- extra --> 0.000
- all --> 0.245  

*****************************************************

Phi3: (100 queries)

Execution Accuracy:
- easy --> 0.417
- medium --> 0.135 
- hard --> 0.071 
- extra --> 0.000
- all --> 0.180 

*****************************************************
