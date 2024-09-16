from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from telegram import Bot
from telegram.request import HTTPXRequest
import json
import requests
import datetime
from django.db import connection
from asgiref.sync import async_to_sync, sync_to_async


from apis.Telegram.Jira.functions.jira_comment_functions import process_data

from dotenv import load_dotenv, find_dotenv
import os
load_dotenv(find_dotenv())

trequest = HTTPXRequest(connection_pool_size=20)
bot = Bot(token=os.environ.get('AV_BOT_TOKEN'), request=trequest)
CHAT_ID = os.environ.get('TELEGRAM_AV_CHAT_ID')
MSG_THREAD_ID = os.environ.get('TELEGRAM_AV_MSG_THREAD_ID')

@csrf_exempt
@async_to_sync
async def av_form_webhook(request):
    if request.method == 'POST':
        req = json.loads(request.body)
        print(req)
        
        def create_page(data: dict):
            headers = {
                "Authorization": "Bearer " + os.environ.get('NOTION_TOKEN'),
                "Content-Type": "application/json",
                "Notion-Version": "2022-06-28",
            }
            
            create_url = "https://api.notion.com/v1/pages"

            payload = {"parent": {"database_id": os.environ.get('NOTION_DB_ID')}, "properties": data}
            print(headers)
            print(payload)

            res = requests.post(create_url, headers=headers, json=payload)
            # print(res.status_code)
            return res.status_code
        
        async def send_telegram_msg():
            msg = f"""
            🎤AV EQ Request Form🎤

            * Department/Group: {req['borrower_dept']}
            * Contact person: {req['borrower_name']}
            * Event: {req['event']}

            * Date of request: {req['claim_date']}
            * Date of event: {req['claim_date']}
            * Event start time: {req['start_time']}
            * Event End Time (return time): {req['end_time']}
            * Location: {req['claim_location']}
            * Attendees(#): 
            * Equipment required: {req['item']}
            - 
            ...............................................
            Operation Checklist: 
            (✔️Please tick below)

            {'✅Canva' if req['slides_needed'] == 'Canva' else '▫️Canva'}
            {'✅PPT (no animation)' if req['slides_needed'] == 'PPT (no animation)' else '▫️PPT (no animation)'}
            {'✅PPT (with animation)' if req['slides_needed'] == 'PPT (with animation)' else '▫️PPT (with animation)'}
            {'✅Videos' if req['need_bgm'] == 'Yes' else '▫️Videos'}
            {'✅BGM' if req['need_bgm'] == 'Yes' else '▫️BGM'}
            {'✅External link (e.g. Kahoot, Menti etc.): '+req['ext_link'] if req['ext_link'] != '' and req['ext_link'] != 'No' else '▫️External link (e.g. Kahoot, Menti etc.)'}


            ▫️Zoom required
            ▫️Recording required

            All materials must be sent at least a day prior to the event ‼️
            """

            await bot.send_message(chat_id=CHAT_ID, text=msg, message_thread_id=MSG_THREAD_ID)
            return JsonResponse({'status': 'success'})
        
        start_time = req["claim_date"]+"T"+req["start_time"]+":00+10:00"
        end_time = req["claim_date"]+"T"+req["end_time"]+":00+10:00"

        data = {
            "URL": {"title": [{"text": {"content": req["borrower_dept"]+": "+req["borrower_name"]}}]},
            "Title": {"rich_text": [{"text": {"content": "Request for "+req["item"]}}]},
            "Published": {"date": {"start":start_time, "end": end_time}}
        }
        notion_res = create_page(data)
        print(notion_res)
        if notion_res == 200:
            telegram_res = await send_telegram_msg()
            
            if telegram_res.status_code == 200:
                return JsonResponse({'status': 'success'})
            return JsonResponse({'status': 'failed for Telegram'}, status=400)
        
        return JsonResponse({'status': 'failed for Notion'}, status=400)



