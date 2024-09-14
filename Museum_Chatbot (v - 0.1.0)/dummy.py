from datetime import datetime

now = datetime.now()

formatted_date = now.strftime("%d %B, %Y")

print(f"Current date: {formatted_date}")

from datetime import datetime

# Get the current time
now = datetime.now()

# Format the time as "HH:MM:SS AM/PM"
formatted_time = now.strftime("%I:%M %p")

print(f"Current time: {formatted_time}")
