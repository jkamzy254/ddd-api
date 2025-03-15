import textwrap
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from telegram import Bot
from telegram.request import HTTPXRequest
import json
import requests
import datetime
from django.db import connection
from asgiref.sync import async_to_sync, sync_to_async
# from ddd.utils import send_push_notification


from apis.Telegram.Jira.functions.jira_comment_functions import process_data

from dotenv import load_dotenv, find_dotenv
import os
load_dotenv(find_dotenv())

trequest = HTTPXRequest(connection_pool_size=20)
bot = Bot(token=os.environ.get('JIRA_BOT_TOKEN'), request=trequest)
CHAT_ID = os.environ.get('IT_DEPT_CHAT_ID')
MSG_THREAD_ID = os.environ.get('TELEGRAM_TICKET_MSG_THREAD_ID')


@csrf_exempt
@async_to_sync
async def ticket_webhook(request):
    def update_issue():
        with connection.cursor() as cursor:
            cursor.execute(
                "EXEC spJiraSaveIssue @IssueKey=%s, @IssueData=%s, @IssueAction=%s, @SenderID=%s",
                [issue_id, issue_json, action, sender_id]
            )
            cursor.execute("SELECT ID, UID, Group_IMWY, MemberGroup, Name FROM MemberData WHERE UID = %s", [sender_id])
            recs = cursor.fetchone()
            if recs:
                rec = dict(zip([column[0] for column in cursor.description], recs))
            else:
                rec = None
        return rec
        
    # def delete_comment():
    #     with connection.cursor() as cursor:
    #         cursor.execute(f"""EXEC spJiraDeleteComment @CommentId='{comment_id}'""")
    #         recs = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
    #     return recs
    
    if request.method == 'POST':
        data = json.loads(request.body)
        print(data)
        issue = data.get("issue", {})
        issue_id = issue.get("id", "")
        issue_key = issue.get("key", "")
        fields = data.get("issue", {}).get("fields", "")
        sender_id = fields.get("customfield_10073", "")
        description = fields.get("description", "")
        created = fields.get("created", "")
        title = fields.get("summary", "")
        action = data.get('webhookEvent', 'Unknown event')
        issue_json = json.dumps(issue, indent=2).replace("'","''")
        
        message_title = 'DDD Ticket Update'
        if action == 'jira:issue_updated':
            message_body = 'Your ticket has a new update. Please check at your own convenience'

        
        rec = await sync_to_async(update_issue)()   
        msg = textwrap.dedent(f"""
        🔧DDD CORRECTION ISSUE🌐

        * Department: {rec['Group_IMWY']}
        * Group: {rec['MemebrGroup']}
        * Contact person: {rec['Name']}
        * Ticket Date: {created}
        * Title: {title}
        - 
        ...............................................
        Operation Checklist: 
        {description}

        Issue Link: https://dddmelb84.atlassian.net/browse/DTT-{issue_key}
        Please check all issues assigned to you as first priority ‼️
        """)
    
            
        await bot.send_message(chat_id=CHAT_ID, text=msg, message_thread_id=MSG_THREAD_ID)
        
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'failed'}, status=400)
