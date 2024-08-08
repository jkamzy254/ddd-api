from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from telegram import Bot
import json
import datetime
from django.db import connection
from asgiref.sync import async_to_sync, sync_to_async

from apis.Telegram.Jira.functions.jira_comment_functions import process_data

from dotenv import load_dotenv, find_dotenv
import os
load_dotenv(find_dotenv())

bot = Bot(token=os.environ.get('JIRA_BOT_TOKEN'))
CHAT_ID = os.environ.get('TELEGRAM_JIRA_CHAT_ID')
MSG_THREAD_ID = os.environ.get('TELEGRAM_JIRA_MSG_THREAD_ID')

@csrf_exempt
@async_to_sync
async def jira_webhook(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print(data)
        timestamp = data["timestamp"] / 1000
        hook_time = datetime.datetime.fromtimestamp(timestamp)
        comment = data["comment"]
        issue = data["issue"]
        event = data.get('webhookEvent', 'Unknown event')
        
        print(hook_time)

        
        def create_comment():
            with connection.cursor() as cursor:
                cursor.execute(f"""
                    EXEC spJiraAddComments 
                    @CommentId='{comment["id"]}',
                    @CommentText='{comment["body"]}',
                    @Commenter='{comment["author"]["accountId"]}',
                    @IssueName='{issue["fields"]["summary"]}',
                    @IssueAssigned='{issue["fields"]["assignee"]["accountId"]}',
                    @Timestamp='{str(hook_time).split('.')[0]}'
                """)
                recs = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return recs
        
        def delete_comment():
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spJiraDeleteComment @CommentId='{comment["id"]}'")
                recs = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return recs
        
    
        if issue["fields"]["project"]["id"] == "10000" or issue["fields"]["project"]["id"] == "10003":
            if event == "comment_created":
                recs = await sync_to_async(create_comment)()
                
            elif event == "comment_deleted":
                recs = await sync_to_async(delete_comment)()
                
            formatted_text = process_data(recs,comment["author"]["displayName"])
            
            await bot.send_message(chat_id=CHAT_ID, text=formatted_text, message_thread_id=MSG_THREAD_ID)
        
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'failed'}, status=400)
