import textwrap
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from telegram import Bot
from telegram.request import HTTPXRequest
import json
import re
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
            cursor.execute("SELECT ID, UID, Group_IMWY, MemberGroup, Name, (Select TelID From TelegramID Where UID = M.UID) TelId FROM MemberData M WHERE UID = %s", [sender_id])
            creator = cursor.fetchone()
            if creator:
                added_by = dict(zip([column[0] for column in cursor.description], creator))
            else:
                added_by = None
            cursor.execute("SELECT TelID FROM TelegramID WHERE UID = (Select UID From JiraUserTable Where JiraID = %s)", [assigned])
            assigned_to = cursor.fetchone()
            if assigned_to:
                assign = dict(zip([column[0] for column in cursor.description], assigned_to))
            else:
                assign = None
        return {
            "added_by": added_by,
            "assigned": assign['TelID'],
        }
    
    if request.method == 'POST':
        data = json.loads(request.body)
        issue = data.get("issue", {})
        issue_id = issue.get("id", "")
        issue_key = issue.get("key", "")
        fields = data.get("issue", {}).get("fields", "")
        sender_id = fields.get("customfield_10073", "")
        assigned = fields.get("assignee", {}).get("accountId", "")
        description = fields.get("description", "")
        created = fields.get("created", "")
        title = fields.get("summary", "")
        attachment = fields.get("attachment", "")
        action = data.get('webhookEvent', 'Unknown event')
        issue_json = json.dumps(issue, indent=2).replace("'","''")
        
        message_title = 'DDD Ticket Update'
        if action == 'jira:issue_updated':
            message_body = 'Your ticket has a new update. Please check at your own convenience'
            
        dt = datetime.datetime.strptime(created[:19], "%Y-%m-%dT%H:%M:%S")

        # Format the date as '15th Mar, 2025'
        formatted_date = dt.strftime("%d %b, %Y")

        
        resp = await sync_to_async(update_issue)()   
        sender = resp['added_by'] 
        assigned_to = resp['assigned']
        print("Assigned To: ", assigned_to)
        
        user_info = await bot.get_chat(str(assigned_to))
        print(user_info)
        username = user_info.username  # This is None if the user has no username

        if username:
                assignee = f"@{username}"
        else:
            assignee = f"[Check Here](tg://user?id={str(assigned_to)})"
            
        def escape_markdown_v2(text):
            reserved_chars = r'\_*[]()~`>#+-=|{}.!'
            return re.sub(f'([{re.escape(reserved_chars)}])', r'\\\1', text)

        # Escape all dynamic parts of the message
        msg = textwrap.dedent(f"""
        🔧 DDD CORRECTION TICKET 🌐

        \\* Department: {escape_markdown_v2(sender['Group_IMWY'])}
        \\* Group: {escape_markdown_v2(sender['MemberGroup'])}
        \\* Created By: {escape_markdown_v2(sender['Name'])}
        \\* Ticket Date: {escape_markdown_v2(formatted_date)}
        \\* Title: {escape_markdown_v2(title)}
        \\* Attachments: {escape_markdown_v2(str(len(attachment)))}
        \\- 
        ...............................................
        Description: 
        {escape_markdown_v2(description)}

        Issue Link: {escape_markdown_v2(f"https://dddmelb84.atlassian.net/browse/{issue_key}")}
        Assignee: {escape_markdown_v2(assignee)}
        Please check all issues assigned to you as first priority ‼️
        """)
                
        print(msg)

        await bot.send_message(chat_id=CHAT_ID, text=msg, message_thread_id=MSG_THREAD_ID, parse_mode="MarkdownV2")
        
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'failed'}, status=400)
