import sqlite3
import json

def fetch_data(cursor, table_name):
    cursor.execute(f"SELECT * FROM {table_name}")
    columns = [description[0] for description in cursor.description]
    rows = cursor.fetchall()
    return [dict(zip(columns, row)) for row in rows]

def export_db_to_json(db_path, json_path):
    # Connect to the SQLite database
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    
    # Fetch the list of all tables in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    # Dictionary to hold data of all tables
    db_data = {}
    
    # Loop through the tables, fetch data, and add it to the dictionary
    for table_name in tables:
        table_data = fetch_data(cursor, table_name[0])
        db_data[table_name[0]] = table_data
    
    # Write the dictionary to a JSON file
    with open(json_path, 'w') as json_file:
        json.dump(db_data, json_file, indent=4)
    
    # Close the database connection
    connection.close()
    print(f"Database exported to JSON format at: {json_path}")

# Usage
db_path = '/Users/mymac/LLM/Personal-Medical-Assistant/desktop_app/ui/DB_query/med_assist.db'
json_path = '/Users/mymac/LLM/Personal-Medical-Assistant/backend/full_chain/med_assist.json'
export_db_to_json(db_path, json_path)