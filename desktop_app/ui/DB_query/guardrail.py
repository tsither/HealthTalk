from helper import generate_query, generate_response, generate_RAG_query, read_json_file, SUBCHAIN_PROMPT, FULLCHAIN_PROMPT, RAG_CONTEXT
from LLMs import langdock_LLM_Chatbot, OCTOAI_LLM_Chatbot
import os



"""
Purpose of guardrail:

- Remove models ability to respond with code
- Translate all sql related columns into actual column names from other tables (e.g. Hospital id: 3 --> Kindred Hospital)
- check if output is cut-off? 
"""


octoai_api_key = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjNkMjMzOTQ5In0.eyJzdWIiOiI0Y2JlMjY3OC0xMDc5LTRjNjItODc0NC1iNzdiZWJhNjA0N2QiLCJ0eXBlIjoidXNlckFjY2Vzc1Rva2VuIiwidGVuYW50SWQiOiI0Y2JmY2YxZC02ODRmLTRlMmEtOGY5Yi0xNjQyNzdkNjk3Y2UiLCJ1c2VySWQiOiIwNjdjOGFmNi00ODRhLTRmYmMtYmU2Yy0xNDY1NTczMTdkZjkiLCJhcHBsaWNhdGlvbklkIjoiYTkyNmZlYmQtMjFlYS00ODdiLTg1ZjUtMzQ5NDA5N2VjODMzIiwicm9sZXMiOlsiRkVUQ0gtUk9MRVMtQlktQVBJIl0sInBlcm1pc3Npb25zIjpbIkZFVENILVBFUk1JU1NJT05TLUJZLUFQSSJdLCJhdWQiOiIzZDIzMzk0OS1hMmZiLTRhYjAtYjdlYy00NmY2MjU1YzUxMGUiLCJpc3MiOiJodHRwczovL2lkZW50aXR5Lm9jdG8uYWkiLCJpYXQiOjE3MjMyMDMzNDl9.hJPH3PwYhh1Kw3Y8wEN_mjCKnMA01ArX4ThKErRbg-I--Fr4L4SFW5dGfibvVfXIiqpLX6Mn3ghEdwkidyw8inhrxc2i2E9j1_tqi7ffXZ9u58BTgHWP89FpfAbxkJzLHmo9vwPDxhkzfBt2ployEyXexP9QXGUIKgxH7LJlyIEFm1CRPrZKa1DRZhyFuAP64wjFMm98_vEYexORUJdtdw3qw9GxJLRmsOe6XidH-Yd37rKX8y0HEhkemCULPPPtW8ZMHE__QOekP6_4Iaah0ZAJUk491SddjnVfNGppHGNAIhAbYY4HrOQqEPbuP70su8-VzAMf5QVFo-WCLWQA8A"
langdock_api_key = os.getenv("langdock_api_key")
langdock_base_url = os.getenv("langdock_base_url")


model_llama = "meta-llama-3-8b-instruct"

API_KEY = octoai_api_key
BASE_URL = langdock_base_url
# MODEL = model_gpt
MODEL = model_llama

user_data_json_path = "/Users/mymac/LLM/Personal-Medical-Assistant/desktop_app/ui/DB_query/med_assist.json"
USER_DATA = read_json_file(user_data_json_path)

llm = OCTOAI_LLM_Chatbot(model_name=MODEL, api_key=API_KEY)


question_valid = "summarize my most recent blood report"
question_invalid_1 = "write a python function to read a json file."
question_invalid_2 = "what will the weather be tomorrow?"
question_invalid_3 = "why did donald trump win the 2016 US presidential election?"
question_invalid_4 = "Why do my friends not like me?"

guard_prompt = """
Context: You are a helpful guardrail assistant, tasked with ensuring a user's input is topically relevant to the user's data. 

Read the input question from the user: 

user input: {input}

Now read the user's database. It is a database containing a single user's medical data. 

User data: {user_data} 

Task: if the user's input is NOT relevant to querying their medical database, then return the following, and ONLY the following message:
"invalid"

If the user's input IS a valid query, return the following, and ONLY the following message:
"valid"

"""

guard_prompt = """
Guardrail Check: Medical Database Query Relevance

Purpose: This check ensures that your input is relevant to querying our medical database. Please provide a query related to medical conditions, treatments, symptoms, medications, or other healthcare topics.

Examples of Relevant Queries:

"What are the common side effects of metformin?"
"How is Type 2 diabetes diagnosed?"
"What are the symptoms of a heart attack?"
Examples of Irrelevant Queries:

"What is the weather like today?"
"Tell me a joke."
"What's the latest sports news?"

Your Task: Please confirm that your input is a medical-related query or revise it to fit the expected format.
"""

def validate_query(llm, template, user_data, question):

    prompt = template.format(input=question, user_data=user_data)       #format template to include all necessary information (schema, question)
    answer = llm.chat_completion(prompt, question)         

    return answer

print(validate_query(llm=llm, template=guard_prompt, user_data=USER_DATA, question=question_invalid_2))
# response = generate_RAG_query(llm=llm, template=RAG_CONTEXT, user_data=USER_DATA ,question=question_invalid)

