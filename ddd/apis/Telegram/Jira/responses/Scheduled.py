from telegram import Bot
import json
import datetime
from django.db import connection
from asgiref.sync import async_to_sync, sync_to_async

from dotenv import load_dotenv, find_dotenv
import os
load_dotenv(find_dotenv())

bot = Bot(token=os.environ.get('JIRA_BOT_TOKEN'))
CHAT_ID = os.environ.get('TELEGRAM_JIRA_CHAT_ID')
MSG_THREAD_ID = os.environ.get('TELEGRAM_JIRA_MSG_THREAD_ID')



# async def update_reminder():  
#     def create_comment():
#         with connection.cursor() as cursor:
#             cursor.execute("SELECT * FROM JiraUpdatesTodayView")
#             recs = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            
            
        
#         def format_date(dt):
#             day = dt.strftime('%d')  # Extract the day part
#             day_ordinal = int(day)
#             if 10 <= day_ordinal % 100 <= 20:
#                 suffix = 'th'
#             else:
#                 suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day_ordinal % 10, 'th')
#             return dt.strftime(f'%d{suffix} %b, %Y')

#         # Format the time
#         def format_time(dt):
#             return dt.strftime('%I:%M%p').lower()
        
#         today = datetime.now()
#         intro = f'JIRA UPDATES\n\n📆 {format_date(today)}\n\n'
#         def process_data(data):
#             output_lines = []
        
#             for user in data:
#                 name = user["Name"]
#                 comments = user.get('Comments')
                
#                 if comments:
#                     try:
#                         comments_list = json.loads(comments)
#                         issues = set(comment['IssueName'] for comment in comments_list)
#                     except (json.JSONDecodeError, TypeError):
#                         issues = set()
#                 else:
#                     issues = set()
                
#                 # Format the output
#                 if issues:
#                     issues_str = ', '.join(issues)
#                     output_lines.append(f"▪️{name}:\n- {issues_str}")
#                 else:
#                     output_lines.append(f"{name}:")
            
#             return intro+'\n\n'.join(output_lines) + f"\n\n---------------------\nLast Edited by {comment["author"]["displayName"]} ({format_time(hook_time)})"
#         return recs