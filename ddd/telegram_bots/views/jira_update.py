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
    
    if request.method == 'POST':
        data = json.loads(request.body)
        print(data)
        timestamp = data["timestamp"] / 1000
        hook_time = datetime.datetime.fromtimestamp(timestamp)
        issue = data["issue"]
        comment = data.get("comment", {})
        event = data.get('webhookEvent', 'Unknown event')
        
        # comment
        comment_id = comment.get("id", '')
        comment_Text = comment.get("body", '')
        comment_author = comment.get("author", {})
        comment_author_id = comment_author.get("accountId", '')
        comment_author_name = comment_author.get("displayName", '')
        
        issue_fields = issue.get("fields", {}) if issue else {}
        comment_issue = issue_fields.get("summary", '')
        comment_assignee = issue_fields.get("assignee", {}).get("accountId", '')
        project_id = issue_fields.get("project", {}).get("id", '')        
    
        if project_id == "10000" or project_id == "10003":
            if event == "comment_created":
                recs = await sync_to_async(create_comment)()
                
            elif event == "comment_deleted":
                recs = await sync_to_async(delete_comment)()
                

                
            formatted_text = process_data(recs,comment_author_name)
            
            await bot.send_message(chat_id=CHAT_ID, text=formatted_text, message_thread_id=MSG_THREAD_ID)
        
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'failed'}, status=400)
