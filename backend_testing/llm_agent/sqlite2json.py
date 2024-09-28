"""
Convert SQlite database into json file (JSON method)
"""

import sqlite3
import json


#sql database filepath
db_path = '/Users/mymac/LLM/Personal-Medical-Assistant/desktop_app/ui/DB_query/drew.db'

#NEW JSON filepath
json_path = '/Users/mymac/LLM/Personal-Medical-Assistant/backend/full_chain/drew.json'



def fetch_data(cursor, table_name):
    cursor.execute(f"SELECT * FROM {table_name}")
    columns = [description[0] for description in cursor.description]
    rows = cursor.fetchall()
    return [dict(zip(columns, row)) for row in rows]

def export_db_to_json(db_path, json_path):

    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    db_data = {}
    
    for table_name in tables:
        table_data = fetch_data(cursor, table_name[0])
        db_data[table_name[0]] = table_data
    
    with open(json_path, 'w') as json_file:
        json.dump(db_data, json_file, indent=4)
    
    connection.close()
    print(f"Database exported to JSON format at: {json_path}")

export_db_to_json(db_path, json_path)