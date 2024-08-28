from pathlib import Path

current_dir = Path(__file__).resolve().parent
# print(current_dir)

from datetime import datetime, timezone
def get_current_time():
    # Get current time in UTC
    utc_time = datetime.now(timezone.utc)
    
    # Format the date and time in European style
    # %d/%m/%Y for day/month/year
    # %H:%M:%S for 24-hour time
    formatted_time = utc_time.strftime("%d/%m/%Y %H:%M:%S")
    
    return formatted_time

# print(get_current_time())

