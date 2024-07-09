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

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

ANYSCALE_API_KEY = os.getenv("ANYSCALE_API_KEY").strip()
print(f"ANYSCALE_API_KEY:{ANYSCALE_API_KEY}")
# MODEL = "mistralai/Mistral-7B-Instruct-v0.1"
MODEL = "mistralai/Mistral-7B-Instruct-v0.1:Ted:iGZ9Hwf"
DB = SQLDatabase.from_uri("sqlite:///C:/Users/MI/Sqlite/med_assist.db")

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

        # Fetch user info from the database using Django ORM
        user = User.objects.filter(first_name='Belen').first()

        if user:
            user_info = {
                "username": user.username,
                "email": user.email,
            }
            logger.info(f"Fetched user information: {user_info}")
        else:
            user_info = None
            logger.warning("No user found with first name 'Belen'.")

        return render(request, 'ui/page1_1.html', {'user_info': user_info})

    except Exception as e:
        logger.error(f"Error fetching user information: {e}")
        return render(request, 'ui/page1_1.html', {'error': 'Error fetching user information'})
    # return render(request, 'ui/page1_1.html')

def page2_view(request):
    return render(request, 'ui/page2.html')

def page3_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            question = data.get("question", "")
            if not question:
                return JsonResponse({"error": "No question provided"}, status=400)

            if not test_db_connection("sqlite:///C:/Users/MI/Sqlite/med_assist.db"):
                return JsonResponse({"error": "Database connection failed"}, status=500)

            logger.debug(f"Instantiating AnyScaleLLM with model_name={MODEL} and api_key={ANYSCALE_API_KEY}")
            llm = AnyScaleLLM(model_name=MODEL, api_key=ANYSCALE_API_KEY)
            logger.debug("AnyScaleLLM instantiated successfully.")

            chat_history = []
            while True:
                query = generate_query(llm=llm, template=SUBCHAIN_PROMPT, question=question, db=DB)
                response = generate_response(llm=llm, query=query, template=FULLCHAIN_PROMPT, question=question, db=DB)

                logger.debug(f"User question: {question}")
                logger.debug(f"Generated query: {query}")
                logger.debug(f"LLM response: {response}")

                chat_history.append({"user_question": question, "bot_response": response})

                # Check termination condition (e.g., specific keyword or number of interactions)
                if "exit" in response.lower():
                    break

                # Prepare for next iteration based on user input or continue loop
                question = response

            return JsonResponse({"chat_history": chat_history})

        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return JsonResponse({"error": "Internal server error"}, status=500)

    return render(request, 'ui/page3_2.html')
