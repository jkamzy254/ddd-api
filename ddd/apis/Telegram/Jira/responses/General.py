from django.db import connection
from apis.Telegram.Jira.functions.jira_comment_functions import process_data
from asgiref.sync import async_to_sync, sync_to_async

async def no_comment(user):
    name = user.first_name
    id = user.id
    print(name)
    print(id)
    
    def add_no_comment():
        with connection.cursor() as cursor:
            cursor.execute(f"EXEC spJiraAddNoComment @TelId={id}")
            recs = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
        return recs
    
    recs = await sync_to_async(add_no_comment)()
    formatted_text = process_data(recs,name)
    return formatted_text