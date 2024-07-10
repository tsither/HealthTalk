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
DB = SQLDatabase.from_uri(f"sqlite:////Users/mymac/Downloads/desktop_app/med_assist.db")
print(DB)
ANYSCALE_API_KEY = os.getenv("ANYSCALE_API_KEY").strip()
# print(f"ANYSCALE_API_KEY:{ANYSCALE_API_KEY}")
# MODEL = "mistralai/Mistral-7B-Instruct-v0.1"
MODEL = "mistralai/Mistral-7B-Instruct-v0.1:Ted:iGZ9Hwf"
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

def page2_view(request):

    '''
    Hana: you need to do the following:

    1. Install all requirements under:
    Personal-Medical-Assistant/backend/content_extractor/requirements/extraction_venv_requirements.txt
    
    2. Run the following script:
    Personal-Medical-Assistant/backend/content_extractor/extraction.py

    It works like this: "extraction.py -f path/to/image.png" <- here comes the filepath from your html (OJO: I changed the accepted files as follows: accept=".pdf,.png,.jpg,.webp" )

    3. A json file will be saved in the same directory as your imported file

    4. Then read the json file and create a prompt to the LLM to create a SQL based on the info to update our database

    5. Print the output of the LLM. Do not focus on updating the database.
    
    Comment: I talked with Ted and there is no real reason to focus on updating the database just now.
    Its just enough if we show the json and the possible query. The updating is gonna be messy, so do
    not try it.
    
    For the prompting, you can consider this:

    a) Prompt the LLM with my gold standard (json) and Teds gold standard (SQL query) as an example.
    He said it should work like that. I sent you his gold standard on telegram. Mine is under:
    Personal-Medical-Assistant/backend/content_extractor/data/json/example3_goldstandard.json 
    According to him, it should be able to do a correct guess.

    b) Do a properly parsing of the json to the SQL query. This seems like a lot of work.

    Comment: Ill leave my phone on, so you can call me. Im going to sleep now (its 00:20).

    See ya!
    '''

    return render(request, 'ui/page2.html')

def page3_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            question = data.get("question", "")
            if not question:
                return JsonResponse({"error": "No question provided"}, status=400)

            if not test_db_connection("sqlite:////Users/mymac/Downloads/desktop_app/med_assist.db"):
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