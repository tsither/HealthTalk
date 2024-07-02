from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.llms import Ollama
from langchain_community.agent_toolkits import create_sql_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser               #Getting SQL squery, then running query in db, so string is required
from langchain_core.runnables import RunnablePassthrough                #allows us to pass through a function so our chain can use it


TEMPLATE = """
Based on the schema below, write an SQL query that would answer the user's question:
{schema}

*Make sure to output only a runnable SQL Query, do not output any other information. The last character in the output must be a ;

Question: {question}
SQL Query:
"""


def construct_prompt(template):

    prompt = ChatPromptTemplate.from_template(TEMPLATE)

    prompt.format(schema="my schema", question="How many users are there?")

    return prompt




agent_executor = create_sql_agent(llm, db=db, verbose=False)

agent_executor.

agent_executor.invoke(
    "How many artists are there?"
)

def get_schema(_):
    return db.get_table_info()

get_schema(None)


def generate_query(schema, prompt, llm):

    # sql_chain = RunnablePassthrough.assign(schema=get_schema) | prompt | llm | StrOutputParser()                 #chain
    sql_chain = RunnablePassthrough.assign(schema=schema) | prompt | llm | StrOutputParser()                 #chain

    query = sql_chain.invoke({"question": "How many artists are there?"})

    return query



def run_query(query):
    """
    Takes query and runs query in database
    """
    return db.run(query)


def generate_response(query, schema, execution, prompt, llm):
    full_chain = RunnablePassthrough.assign(query=query).assign(schema=schema, response= lambda variables: run_query(variables["query"])) | prompt | llm 

    response = full_chain.invoke({"question": "How many artists are there?"})
    return response

# full_chain = RunnablePassthrough.assign(query=sql_chain).assign(schema=get_schema, response= lambda variables: run_query(variables["query"])) | prompt | llm 

# full_chain.invoke({"question": "How many artists are there?"})