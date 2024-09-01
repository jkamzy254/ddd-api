from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from telegram import Bot
from telegram.request import HTTPXRequest
import json
import datetime
from django.db import connection
from asgiref.sync import async_to_sync, sync_to_async

from apis.Telegram.Jira.functions.jira_comment_functions import process_data

from dotenv import load_dotenv, find_dotenv
import os
load_dotenv(find_dotenv())

trequest = HTTPXRequest(connection_pool_size=20)
bot = Bot(token=os.environ.get('JIRA_BOT_TOKEN'), request=trequest)
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
        
        project_id = issue["fields"]["project"]["id"]
        
        # print(hook_time)

        # comment
        comment_id = comment["id"]
        comment_Text = comment["body"]
        comment_author_id = comment["author"]["accountId"]
        comment_author_name = comment["author"]["displayName"]
        comment_issue = issue["fields"]["summary"]
        comment_assignee = issue["fields"]["assignee"]["accountId"]
        
        def create_comment():
            with connection.cursor() as cursor:
                cursor.execute(f"""
                    EXEC spJiraAddComments 
                    @CommentId='{comment_id}',
                    @CommentText='{comment_Text}',
                    @Commenter='{comment_author_id}',
                    @IssueName='{comment_issue}',
                    @IssueAssigned='{comment_assignee}',
                    @Timestamp='{str(hook_time).split('.')[0]}'
                """)
                recs = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return recs
        
        def delete_comment():
            with connection.cursor() as cursor:
                cursor.execute(f"""EXEC spJiraDeleteComment @CommentId='{comment_id}'""")
                recs = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return recs
        
    
        if project_id == "10000" or project_id == "10003":
            if event == "comment_created":
                recs = await sync_to_async(create_comment)()
                
            elif event == "comment_deleted":
                recs = await sync_to_async(delete_comment)()
                
            formatted_text = process_data(recs,comment_author_name)
            
            await bot.send_message(chat_id=CHAT_ID, text=formatted_text, message_thread_id=MSG_THREAD_ID)
        
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'failed'}, status=400)
