from django.shortcuts import render
from django.http import JsonResponse
import os
import json
from .models import User
from langchain_community.utilities.sql_database import SQLDatabase
import sqlalchemy
from .DB_query.helper import generate_query, generate_response, SUBCHAIN_PROMPT, FULLCHAIN_PROMPT
#from .DB_query.AnyScaleLLM import AnyScaleLLM
import logging
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.db import connection
from django.contrib.sessions.models import Session
from django.utils import timezone
from pathlib import Path
from django.http import HttpResponseRedirect
from django.urls import reverse
from json2html import *
import tempfile
import subprocess

from octoai.client import OctoAI
from octoai.text_gen import ChatMessage


# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


# current_dir = Path(__file__).resolve().parent
# db_path = current_dir / "DB_query" / "med_assist.db"

# TODO: Do this dinamically
# DB = SQLDatabase.from_uri(f"sqlite:///////home/leonnico/Documents/UP/Personal-Medical-Assistant/med_assist.db") 
DB = SQLDatabase.from_uri("sqlite:////Users/hanamcmahon-cole/Documents/Sqlite/med_assist.db")

ANYSCALE_API_KEY = os.getenv("ANYSCALE_API_KEY").strip()

# print(f"ANYSCALE_API_KEY:{ANYSCALE_API_KEY}")
MODEL = "mistralai/Mistral-7B-Instruct-v0.1"
#MODEL = "mistralai/Mistral-7B-Instruct-v0.1:Ted:iGZ9Hwf"
# DB = SQLDatabase.from_uri("sqlite:///Users/mymac/Downloads/desktop_app/ui/DB_query/med_assist.db")


# guard_NSFW = Guard().use(
#     NSFWText, threshold=0.8, validation_method="sentence", on_fail="exception"
# )


#Test database connection
def test_db_connection(db_uri):
    try:
        engine = sqlalchemy.create_engine(db_uri)
        with engine.connect() as connection:
            result = connection.execute(sqlalchemy.text("SELECT 1"))
            if result.scalar() == 1:
                logger.info("Database connection is successful.")
                return True
            else:
                logger.error("Failed to execute test query.")
                return False
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

def home(request):
    return render(request, 'ui/home.html')

def page1_view(request):
    try:
        logger.debug("Attempting to fetch user information.")

        # Check if the 'User' table exists and get its columns
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='USER'")
            table_exists = cursor.fetchone()

            if table_exists:
                cursor.execute("PRAGMA table_info('User')")
                columns = cursor.fetchall()
                column_names = [col[1] for col in columns]
                logger.info(f"Table 'User' found with columns: {column_names}")
            else:
                logger.error("Table 'User' does not exist in the database.")
                return render(request, 'ui/page1_1.html', {'error': "Table 'User' does not exist in the database."})

        # Fetch user info from the database using Django ORM
        user = User.objects.filter(first_name='Belen').first()

        if user:
            user_info = {
                "user_id": user.user_id,
                "full_name": f"{user.first_name} {user.last_name}",
                "gender": user.gender,
                "birth_date": user.birth_date,
                # "email": user.email,
                "phone_number": user.phone_number,
            }
            logger.info(f"Fetched user information: {user_info}")
        else:
            user_info = None
            logger.warning("No user found with first name 'Belen'.")

        return render(request, 'ui/page1_1.html', {'user_info': user_info})

    except Exception as e:
        logger.error(f"Error fetching user information: {e}")
        return render(request, 'ui/page1_1.html', {'error': 'Error fetching user information'})

def process_reports(request):
    '''
    This part takes the file and runs it through the script. It also get the result as string (but its a json)
    '''
    if request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as temp_file:
            for chunk in uploaded_file.chunks():
                temp_file.write(chunk)

        # Run the external Python script
        result = subprocess.run(
            # TODO: Make this dynamic
            # ['python', '/home/leonnico/Documents/UP/Personal-Medical-Assistant/backend/content_extractor/extraction.py', 
            #  '-f', temp_file.name],
            ['python', '/Users/hanamcmahon-cole/Documents/Medical_assistant/Personal-Medical-Assistant/backend/content_extractor/extraction.py', 
             '-f', temp_file.name],
            capture_output=True,
            text=True,
            check=True
        )
            
        # Get the output of the script
        output = result.stdout

        print(output)

        try:
            json_output = json.loads(result.stdout)
            html_output = json2html.convert(json = json_output)
            os.unlink(temp_file.name)  # Delete the temporary file
            #todo: also transfer json output for sql update 
            return render(request, 'ui/page2_2.html', {'output': html_output})
            #return render(request, 'ui/page2_1.html', {'output': json.dumps(json_output, indent=4)})
        except json.JSONDecodeError:
            print("Script did not return valid JSON. Please try again.")
            return render(request, 'ui/page2_1.html', {'error': "Invalid JSON output"})

    return HttpResponseRedirect(reverse('upload_success'))

def convert_to_sql(request):
    json_data = request.POST.get('json_data')
    if json_data:
        try:
            data = json.loads(json_data)
            sql_query = json_to_sql(data)
            return render(request, 'ui/page2_1.html', {'output': data, 'sql_query': sql_query})
        except json.JSONDecodeError:
            return render(request, 'ui/page2_1.html', {'error': "Invalid JSON data"})
    return render(request, 'ui/page2_1.html', {'error': "No JSON data provided"})

def json_to_sql(data):
    json_output = json.dumps(data, indent=4)

    # Prepare the prompt for the LLM
    prompt = f"""
    CONTEXT: You are an expert interpreter of json files to sql queries that will update a database. Your work is extremely important and will be used in a life or death situation.
    TASK: Given the information of a json file, generate a SQL query to update the database based on the information given in the json file.
    EXAMPLE OF THE JSON YOU WILL RECEIVE:
    {{
    "Date": "21.05.1995",
    "patient_information": {{
    "patient_id": "12",
    "patient_name": "Max Mustermann",
    "patient_sex": "Female",
    "patient_age": "21"
    }},
    "test_results": [
    {{
    "test_name": "Hemoglobin (Hb)",
    "result_value": "12.5",
    "unit_of_measurement": "g/dl",
    "reference_range": "13.0-17.0 g/dL"
    }},
    {{
    "test_name": "Mean Corpuscular Volume (MCV)",
    "result_value": "87.75",
    "unit_of_measurement": "fL",
    "reference_range": "83-101 fL"
    }}
    ]
    }}
    EXAMPLE OF THE SQL QUERY THAT SHOULD BE YOUR OUTPUT:
    INSERT INTO reports (
    report_date,
    test_name,
    test_result,
    test_units,
    test_reference_range,
    report_type_id,
    user_id,
    hospital_id
    ) VALUES (
    '02.12.202X',
    'Hemoglobin',
    12.5,
    'g/dL',
    '13.0 - 17.0',
    1,
    1,
    1
    );
    INSERT INTO reports (
    report_date,
    test_name,
    test_result,
    test_units,
    test_reference_range,
    report_type_id,
    user_id,
    hospital_id
    ) VALUES (
    '02.12.202X',
    'Mean Corpuscular Volume (MCV)',
    '87.75',
    'fL',
    '83 - 101',
    1,
    1,
    1
    );
    IMPORTANT: Just return the SQL query. Do not make any further comment. Otherwise, the patient will die.
    """

    # llm = AnyScaleLLM(model_name=MODEL, api_key=ANYSCALE_API_KEY)
    # logger.debug("AnyScaleLLM instantiated successfully.")

    # answer = llm.chat_completion(prompt, str(json_output))
    # print(answer)

    # TODO: Create new OctoAI class as line 231
    client = OctoAI()
    completion = client.text_gen.create_chat_completion(
        model="meta-llama-3-8b-instruct",
        messages=[
            ChatMessage(
                role="system",
                content=prompt,
            ),
            ChatMessage(role="user", content=str(json_output)),
        ],
        temperature=0.1,
        max_tokens=8192-len(prompt),
    )

    response = completion.choices[0].message.content
    print(response)

    return str(response)

def upload_success(request):
    '''
    Here, if the upload is sucessfull, we should do the prompting to the LLM
    '''
    return render(request, 'ui/page2_1.html')

def page2_1view(request):
    '''
    Hana, before you start, consider the following:

    0. I changed three files of yours: views.py, urls.py and ui/page2_1.html. In views I added functions
    to get the file and then process it. In urls, I just added to more urls, so the functions have a place.
    In the html I added some file suffixes.

    Now, for it to work, you'll need the following as well:

    1. Install all module requirements under:
    Personal-Medical-Assistant/backend/content_extractor/requirements/extraction_venv_requirements.txt
    
    2. Check your DB filepath and environment path to get the API (lines 36 to 40 of this script)

    3. Check process_reports() in this script. It takes the file and then process it through my script. 
    As a result, we receive a json as string.

    4. Check upload_success() in this script. That function should do the prompting and printing.

    TODOS:
    a) In upload_success() call an LLM so that it creates a SQL query
    b) In general, it'd be nice to print the json and the sql query, so that people can see it.
    Again, do not focus on updating the database. Let's just show the results of the json and the SQL.
    That's the impressive part of this part of the project.

    COMMENT: I talked with Ted and there is no real reason to focus on updating the database just now.
    Its just enough if we show the json and the possible query. The updating is gonna be messy, so do
    not try it.
    
    For the prompting, you can consider this:
    
    a) Prompt the LLM with my gold standard (json) and Teds gold standard (SQL query) as an example.
    He said it should be enough like that. I sent you his gold standard on telegram. Mine is under:
    Personal-Medical-Assistant/backend/content_extractor/data/json/example3_goldstandard.json 
    According to him, it should be able to do a correct guess.

    b) Do a properly parsing of the json to the SQL query. This seems like a lot of work.

    See ya!
    '''

    return render(request, 'ui/page2_1.html')

def page2_2view(request):
    return render(request, 'ui/page2_2.html')

def page3_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            question = data.get("question", "") 

            if not question:
                return JsonResponse({"error": "No question provided"}, status=400)

            if not test_db_connection("sqlite:////Users/mymac/Downloads/desktop_app/med_assist.db"):
                return JsonResponse({"error": "Database connection failed"}, status=500)
            
            guard_NSFW.validate(question) #NSFW guardrail

            logger.debug(f"Instantiating AnyScaleLLM with model_name={MODEL} and api_key={ANYSCALE_API_KEY}")
            llm = AnyScaleLLM(model_name=MODEL, api_key=ANYSCALE_API_KEY)
            logger.debug("AnyScaleLLM instantiated successfully.")
            query = generate_query(llm=llm, template=SUBCHAIN_PROMPT, question=question, db=DB)
            response = generate_response(llm=llm, query=query, template=FULLCHAIN_PROMPT, question=question, db=DB)

            logger.debug(f"User question: {question}")
            logger.debug(f"Generated query: {query}")
            logger.debug(f"LLM response: {response}")

            return JsonResponse({"response": response})
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            error_message = str(e)
            return JsonResponse({"error": error_message}, status=500)

    return render(request, 'ui/page3_2.html')

def page3_3(request):
    return render(request, 'ui/page3_3.html')  

# def page3_view(request):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             question = data.get("question", "")
#             if not question:
#                 return JsonResponse({"error": "No question provided"}, status=400)
#
#             if not test_db_connection("sqlite:///C:/Users/MI/Sqlite/med_assist.db"):
#                 return JsonResponse({"error": "Database connection failed"}, status=500)
#
#             logger.debug(f"Instantiating AnyScaleLLM with model_name={MODEL} and api_key={ANYSCALE_API_KEY}")
#             llm = AnyScaleLLM(model_name=MODEL, api_key=ANYSCALE_API_KEY)
#             logger.debug("AnyScaleLLM instantiated successfully.")
#
#             chat_history = []
#             while True:
#                 query = generate_query(llm=llm, template=SUBCHAIN_PROMPT, question=question, db=DB)
#                 response = generate_response(llm=llm, query=query, template=FULLCHAIN_PROMPT, question=question, db=DB)
#
#                 logger.debug(f"User question: {question}")
#                 logger.debug(f"Generated query: {query}")
#                 logger.debug(f"LLM response: {response}")
#
#                 chat_history.append({"user_question": question, "bot_response": response})
#
#                 # Check termination condition (e.g., specific keyword or number of interactions)
#                 if "exit" in response.lower():
#                     break
#
#                 # Prepare for next iteration based on user input or continue loop
#                 question = response
#
#             return JsonResponse({"chat_history": chat_history})
#
#         except Exception as e:
#             logger.error(f"Error processing request: {e}")
#             return JsonResponse({"error": "Internal server error"}, status=500)
#
#     return render(request, 'ui/page3_2.html')
