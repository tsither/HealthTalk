from django.shortcuts import render
from django.http import JsonResponse
import os
import json
from .models import User
from langchain_community.utilities.sql_database import SQLDatabase
import sqlalchemy
from .DB_query.helper import generate_query, generate_response, generate_RAG_query, read_json_file, SUBCHAIN_PROMPT, FULLCHAIN_PROMPT, RAG_CONTEXT, HELPFUL_PROMPT
from .DB_query.LLMs import PREM_LLM_Chatbot
import logging
import sqlite3
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.db import connection
from django.contrib.sessions.models import Session
from django.utils import timezone
from pathlib import Path
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
import tempfile
import subprocess
from guardrails import Guard
from guardrails.hub import NSFWText
from octoai.client import OctoAI
from octoai.text_gen import ChatMessage
import json2html

#######################################
########### Set up logging ############
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
#######################################


####################################################
########### Dynamic pathing to database ############    #sql generation method
current_dir = Path(__file__).resolve().parent
db_path = current_dir / "DB_query" / "med_assist.db"
db_uri = f"sqlite:////{db_path}"

DB = SQLDatabase.from_uri(db_uri)
####################################################

##########################################
########### RAG json database ############
user_data_json_path = current_dir / "DB_query" / "med_assist.json"
USER_DATA = read_json_file(user_data_json_path)
##########################################

#models, keys
PREMAI_API_KEY = "gee2EQKnNzZARpoEuuO2DOteK9fJMnblXi"


#######################################################################
########### #CHANGE HERE FOR DIFFERENT KEYS + query method ############

API_KEY = PREMAI_API_KEY 
MODEL = "claude-3.5-sonnet"
sql_query_gen_method = False            #False: converts database to json file, queries database as dictionary (JSON METHOD - NO SQL QUERY GENERATION)
                                        #True: generate SQL queries to access database info (sqlite3)
#############################################################


#guardrails
guard_NSFW = Guard().use(
    NSFWText, threshold=0.8, validation_method="sentence", on_fail="exception"
)


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

        print("TEST")
        # Fetch user info from the database using Django ORM
        user = User.objects.filter(user_id=1).first()

        if user:
            user_info = {
                "user_id": user.user_id,
                "full_name": f"{user.first_name} {user.last_name}",
                "gender": user.gender,
                "birth_date": user.birth_date,
                "phone_number": user.phone_number,
            }
            logger.info(f"Fetched user information: {user_info}")
        else:
            user_info = None
            logger.warning("No user found with user_id '1'.")

        return render(request, 'ui/page1_1.html', {'user_info': user_info})

    except Exception as e:
        logger.error(f"Error fetching user information: {e}")
        return render(request, 'ui/page1_1.html', {'error': 'Error fetching user information'})
        
def process_reports(request):
    '''
    This part takes the file and runs it through the script. It also gets the result as a string (but it's JSON).
    '''
    PMA_path = Path.cwd()
    extraction_path = PMA_path / "backend_testing" / "content_extractor" / "extraction.py"

    if request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as temp_file:
            for chunk in uploaded_file.chunks():
                temp_file.write(chunk)

        # Run the external Python script
        result = subprocess.run(
            ['python', extraction_path, '-f', temp_file.name],
            capture_output=True,
            text=True,
            check=True
        )

        output = result.stdout

        llm = PREM_LLM_Chatbot(model_name=MODEL, api_key=API_KEY, project_id=5834)

        output = llm.chat_completion(EXTRACTION_PROMPT, output)        

        print(output)

        try:
            json_output = json.loads(output)
            os.unlink(temp_file.name)  # Delete the temporary file
            # Pass JSON data to the template for rendering
            return render(request, 'ui/page2_2.html', {'json_output': json.dumps(json_output)})
        except json.JSONDecodeError:
            print("Script did not return valid JSON. Please try again.")
            return render(request, 'ui/page2_1.html', {'error': "Invalid JSON output"})

    return HttpResponseRedirect(reverse('upload_success'))

def convert_to_sql(request):
    json_data = request.POST.get('json_data')
    print(f"json_data: {json_data}")

    if not json_data:
        return render(request, 'ui/page2_3.html', {'error': "No JSON data provided"})

    try:
        # Decode unicode escape sequences if necessary
        json_data = json_data.encode('utf-8').decode('unicode_escape')
        data = json.loads(json_data)
        print(f"Try data: {data}")
        data_2 = json.dumps(data, indent=4)
        print(f"Try data_2: {data_2}")

        sql_query = json_to_sql(data)
        print(f"SQL: {sql_query}")

        # Execute the generated SQL query
        conn = sqlite3.connect(db_path)
        print(f"Connection established: {conn}")
        cursor = conn.cursor()
        print(f"Cursor established: {cursor}")

        try:
            # Test connection
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print(f"Connection test successful, result: {result}", flush=True)

            # Split the SQL query if it contains multiple statements and count them
            sql_statements = sql_query.strip().split(';')
            num_statements = len([stmt for stmt in sql_statements if stmt.strip()])  # Count non-empty statements
            print(f"Number of SQL statements to be inserted: {num_statements}")

            for statement in sql_statements:
                if statement.strip():  # Check if the statement is not empty
                    try:
                        cursor.execute(statement)
                    except sqlite3.Error as e:
                        print(f"Error executing statement: {statement}")
                        print(f"SQLite error: {e}")
                        raise  # Re-raise the exception to be caught by the outer except block

            conn.commit()

            # Fetch the latest data from the database based on the number of statements
            cursor.execute(f"SELECT * FROM reports ORDER BY report_id DESC LIMIT {num_statements}")
            inserted_rows = cursor.fetchall()
            print(f"Inserted Rows: {inserted_rows}")

            # Dynamically fetch the column names
            column_names = [description[0] for description in cursor.description]
            print(f"Column Names: {column_names}")

        except sqlite3.Error as e:
            print(f"SQLite error during connection or SQL execution: {e}")
        finally:
            cursor.close()
            conn.close()

        # return render(request, 'ui/page2_3.html', {'output': data_2, 'sql_query': sql_query, 'success': 'Database updated successfully!', 'inserted_rows': inserted_rows})

        # Render the template with dynamic column names and rows
        return render(request, 'ui/page2_3.html', {
            'output': data_2,
            'sql_query': sql_query,
            'success': 'Database updated successfully!',
            'inserted_rows': inserted_rows,
            'column_names': column_names
        })

    except json.JSONDecodeError:
        return render(request, 'ui/page2_3.html', {'error': "Invalid JSON data"})
    except sqlite3.Error as e:
        return render(request, 'ui/page2_3.html', {'error': f"Database error occurred: {str(e)}"})
    except Exception as e:
        return render(request, 'ui/page2_3.html', {'error': f"An error occurred: {str(e)}"})
# def convert_to_sql(request):
#     json_data = request.POST.get('json_data')
#     if json_data:
#         try:
#             data = json.loads(json_data)
#             sql_query = json_to_sql(data)
#             return render(request, 'ui/page2_1.html', {'output': data, 'sql_query': sql_query})
#         except json.JSONDecodeError:
#             return render(request, 'ui/page2_1.html', {'error': "Invalid JSON data"})
#     return render(request, 'ui/page2_1.html', {'error': "No JSON data provided"})

def json_to_sql(data):
    json_output = json.dumps(data, indent=4)

    # Prepare the prompt for the LLM
    prompt = f"""
    CONTEXT: You are an expert interpreter of json files to sql queries that will update a database. Your work is extremely important and will be used in a life or death situation.
    TASK: Given the information of a json file, generate a SQL query to update the database based on the information given in the json file. If no value in any json file field insert NA into string column
    and 9999 into numerical column.
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

    llm = PREM_LLM_Chatbot(model_name=MODEL, api_key=API_KEY, project_id=5834)

    response = llm.chat_completion(prompt=prompt, question=json_output)


    return str(response)

def upload_success(request):
    '''
    Here, if the upload is sucessfull, we should do the prompting to the LLM
    '''
    return render(request, 'ui/page2_1.html')

def page2_1view(request):
    return render(request, 'ui/page2_1.html')

def page2_2view(request):
    return render(request, 'ui/page2_2.html')

def page2_3view(request):
    sql_query = request.session.get('sql_query', 'No SQL query found.')
    return render(request, 'ui/page2_3.html', {'sql_query': sql_query})

def page3_view(request):
    PMA_path = Path.cwd()
    extraction_path = PMA_path / "desktop_app" / "ui" / "DB_query" / "sqlite2json.py"

    result = subprocess.run(
            ['python', extraction_path],
            capture_output=False,
            text=False,
            check=True
        )
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            question = data.get("question", "").strip()

            if not question:
                return JsonResponse({"error": "No question provided"}, status=400)

            if not test_db_connection(db_uri=db_uri):
                return JsonResponse({"error": "Database connection failed"}, status=500)

            llm = PREM_LLM_Chatbot(model_name=MODEL, api_key=API_KEY, project_id=5834)
            logger.debug(f"Instantiating LLM with model_name={MODEL}")

            # Guardrails validation
            try:
                guard_NSFW.validate(question)
            except Exception as guardrails_error:

                try:
                    question = "What questions can I ask?"
                    llm_response = llm.chat_completion(prompt=HELPFUL_PROMPT, question=question)

                    if not llm_response:
                        llm_response = "No specific guidance is available at the moment."

                    # Server-side logging
                    response_data = {
                        "error": f"Guardrails validation failed: {guardrails_error}",
                        "details": f"Medical assistant guidance: {llm_response}"
                    }

                    logger.debug(f"Response data being sent: {response_data}")

                    response_json = json.dumps(response_data)

                    return HttpResponse(response_json, content_type="application/json", status=400)

                except Exception as llm_error:
                    logger.error(f"LLM failed to generate response: {llm_error}")
                    return JsonResponse({
                        "response": "An error occurred while processing your request. Please try again later.",
                        "error": f"Guardrails validation failed: {guardrails_error}. LLM error: {llm_error}"
                    }, status=400)

            logger.debug("LLM instantiated successfully.")

            if sql_query_gen_method:
                query = generate_query(llm=llm, template=SUBCHAIN_PROMPT, question=question, db=DB)
                logger.debug(f"SQL query generated successfully: {query}")
                response = generate_response(llm=llm, query=query, template=FULLCHAIN_PROMPT, question=question, db=DB)
            else:
                response = generate_RAG_query(llm=llm, template=RAG_CONTEXT, user_data=USER_DATA, question=question)

            return JsonResponse({"response": response})

        except Exception as e:
            logger.error(f"Error processing request: {e}")
            error_message = str(e)
            return JsonResponse({"error": error_message}, status=500)

    return render(request, 'ui/page3_2.html')

def page3_3(request):
    return render(request, 'ui/page3_3.html')  


EXTRACTION_PROMPT = """
    CONTEXT: You are an expert in analyzing blood test results in a laboratory. Your work is extremely important and will be used in a life or death situation.  

    TASK: Given the following text extracted using an OCR from a blood test report, please extract and structure the following information:
    - Date of the test
    - Patient information (if available)
    - Test results, including:
        - Test name
        - Result value
        - Unit of measurement (if available)
        - Reference range (if available)

    Format the output as a JSON object. If a piece of information is not available, use null for its value.

    EXAMPLE OF YOUR EXPECTED OUTPUT:
    {
    "Date": "21.05.1995",
    "patient_information": {
        "patient_id": "12",
        "patient_name": "Max Mustermann",
        "patient_sex": "Female",
        "patient_age": "21"
        },
    "test_results": [
        {
            "test_name": "Hemoglobin (Hb)",
            "result_value": "12.5",
            "unit_of_measurement": "g/dl",
            "reference_range": "13.0-17.0 g/dL"
        },
        {
            "test_name": "Mean Corpuscular Volume (MCV)",
            "result_value": "87.75",
            "unit_of_measurement": "fL",
            "reference_range": "83-101 fL"
        }
        ]
    }
    
    IMPORTANT: Just return the JSON object. Do not make any further comment. Otherwise, the patient will die. Make sure that the JSON is efficiently formatted.
    """
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
