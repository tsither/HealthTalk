

CHECK_USER_PROMPT = """
CONTEXT: You are an LLM guardrail, designed to prevent unsupported querying from the users. 

Based on the database schema, you must decide whether a user's question is a relevant inquiry to the database. 

If a user's input is NOT relevant to the database, then print 'False'. 

IF a user's input is relevant to the database, print 'True'. 

IMPORTANT: Only print either True or False, and no other characters/words etc. 

To assist you, here are a list of relevant topics to the database: 

["health", "fitness", "medicine", "data", "drugs","medical reports","doctors","appoinments","doctors","personal information"]

Question: {question}
Schema: {schema}

Return (True or False): 
"""


def get_schema(db):
    """
    Gets schema from SQL database (db)
    """
    return db.get_table_info()

def check_user_input(question, template, db, llm):
    """
    Intended to check whether user input in relevant to database --> prevent use of LLM for unsupported queries.
    """

    prompt = template.format(schema=get_schema(db),question=question)       #format template to include all necessary information (schema, question)

    sql_query = llm.chat_completion(prompt, question)         #generates sql query
