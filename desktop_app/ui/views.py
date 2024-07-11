from django.shortcuts import render
from django.http import JsonResponse
import os
import json
from .models import User
from langchain_community.utilities.sql_database import SQLDatabase
import sqlalchemy
from .DB_query.helper import generate_query, generate_response, SUBCHAIN_PROMPT, FULLCHAIN_PROMPT
from .DB_query.AnyScaleLLM import AnyScaleLLM
import logging
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.db import connection
from django.contrib.sessions.models import Session
from django.utils import timezone
from pathlib import Path
from django.http import HttpResponseRedirect
from django.urls import reverse
import tempfile
import subprocess


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

DB = SQLDatabase.from_uri(f"sqlite:///////home/leonnico/Documents/UP/Personal-Medical-Assistant/desktop_app/med_assist.db") 
#DB = SQLDatabase.from_uri(f"sqlite:////Users/mymac/Downloads/desktop_app/med_assist.db")

ANYSCALE_API_KEY = os.getenv("ANYSCALE_API_KEY").strip()

# print(f"ANYSCALE_API_KEY:{ANYSCALE_API_KEY}")
MODEL = "mistralai/Mistral-7B-Instruct-v0.1"
#MODEL = "mistralai/Mistral-7B-Instruct-v0.1:Ted:iGZ9Hwf"
# DB = SQLDatabase.from_uri("sqlite:///Users/mymac/Downloads/desktop_app/ui/DB_query/med_assist.db")

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
            # TODO: Change the filepath to your case
            ['python3', '/home/leonnico/Documents/UP/Personal-Medical-Assistant/backend/content_extractor/extraction.py', 
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
            # Delete the temporary file
            os.unlink(temp_file.name)
            return render(request, 'ui/page2_1.html', {'output': json.dumps(json_output, indent=4)})
        except json.JSONDecodeError:
            print("Script did not return valid JSON. Please try again.")
            return render(request, 'ui/page2_1.html', {'error': "Invalid JSON output"})

    return HttpResponseRedirect(reverse('upload_success'))

def convert_to_sql(request):
    json_data = request.POST.get('json_data')
    if json_data:
        try:
            data = json.loads(json_data)
            # Here, implement your logic to convert JSON to SQL
            # This is a placeholder function - you'll need to replace it with your actual conversion logic
            sql_query = json_to_sql(data)
            return render(request, 'ui/page2_1.html', {'output': data, 'sql_query': sql_query})
        except json.JSONDecodeError:
            return render(request, 'ui/page2_1.html', {'error': "Invalid JSON data"})
    return render(request, 'ui/page2_1.html', {'error': "No JSON data provided"})

def json_to_sql(data):
    json_output = json.dumps(data, indent=4)

    # Prepare the prompt for the LLM
    prompt = f"""
    Given the following JSON data, generate an SQL query to update this data from a database. 
    Assume the table name is 'medical_reports'.
    The query should select all fields and include appropriate WHERE clauses based on the JSON data.
    """

    llm = AnyScaleLLM(model_name=MODEL, api_key=ANYSCALE_API_KEY)
    logger.debug("AnyScaleLLM instantiated successfully.")

    answer = llm.chat_completion(prompt, str(json_output))
    return str(answer)


def upload_success(request):
    return render(request, 'ui/page2_1.html')

def page2_view(request):
    return render(request, 'ui/page2_1.html')

def page3_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            question = data.get("question", "")
            if not question:
                return JsonResponse({"error": "No question provided"}, status=400)

            if not test_db_connection("sqlite:///////home/leonnico/Documents/UP/Personal-Medical-Assistant/desktop_app/med_assist.db"):
                return JsonResponse({"error": "Database connection failed"}, status=500)

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
            return JsonResponse({"error": "Internal server error"}, status=500)

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
