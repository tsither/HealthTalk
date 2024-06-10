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


Meta-Llama-3-70B-Instruct: (200_queries)
                     easy                 medium               hard                 extra                all                 
count                52                   102                  30                   16                   200                 
=====================   EXECUTION ACCURACY     =====================
execution            0.558                0.353                0.367                0.250                0.400               

====================== EXACT MATCHING ACCURACY =====================
exact match          0.558                0.176                0.133                0.125                0.265  

***************************************************************************************************************
***************************************************************************************************************

Mistral-7B-Instruct: (200 queries) 

                     easy                 medium               hard                 extra                all                 
count                52                   102                  30                   16                   200                 
=====================   EXECUTION ACCURACY     =====================
execution            0.538                0.235                0.167                0.000                0.285               

====================== EXACT MATCHING ACCURACY =====================
exact match          0.538                0.216                0.100                0.000                0.265               

***************************************************************************************************************
***************************************************************************************************************

Meta-Llama-3-8B-Instruct: (200 queries) 

                     easy                 medium               hard                 extra                all                 
count                52                   102                  30                   16                   200                 
=====================   EXECUTION ACCURACY     =====================
execution            0.481                0.196                0.133                0.000                0.245               

====================== EXACT MATCHING ACCURACY =====================
exact match          0.481                0.127                0.067                0.000                0.200               

***************************************************************************************************************
***************************************************************************************************************

Phi3: (100 queries)

                    easy                 medium               hard                 extra                all                 
count                24                   52                   14                   10                   100                 
=====================   EXECUTION ACCURACY     =====================
execution            0.417                0.135                0.071                0.000                0.180               

====================== EXACT MATCHING ACCURACY =====================
exact match          0.417                0.038                0.143                0.000                0.140               


***************************************************************************************************************
***************************************************************************************************************
