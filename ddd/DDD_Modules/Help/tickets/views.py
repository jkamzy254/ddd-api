from django.shortcuts import render
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt

from asgiref.sync import async_to_sync, sync_to_async

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status
from rest_framework.views import APIView
from django.db import connection
from azure.storage.blob import BlobServiceClient
import os
from dotenv import load_dotenv, find_dotenv
from jira import JIRA, JIRAError
from jira.resources import Issue
from ddd.utils import decode_jwt, send_push_notification

from telegram import Bot
from telegram.request import HTTPXRequest

import datetime, json, pandas as pd

load_dotenv(find_dotenv())

trequest = HTTPXRequest(connection_pool_size=20)
bot = Bot(token=os.environ.get('TICKET_BOT_TOKEN'), request=trequest)
CHAT_ID = os.environ.get('TELEGRAM_JIRA_CHAT_ID')
MSG_THREAD_ID = os.environ.get('TELEGRAM_JIRA_MSG_THREAD_ID')

# Create your views here.

def get_jira_client():
    jira_options = {'server': os.environ.get('JIRA_URL')}
    jira = JIRA(options=jira_options, basic_auth=(os.environ.get('JIRA_USERNAME'), os.environ.get('TICKET_TOKEN')))
    return jira

class AddTicketViewSet(APIView):
    
    def post(self, request):
        form = request.data
        upload_files = form.getlist('ticketFiles')
        date_time = datetime.datetime.now()
        epoch_time = int(date_time.timestamp())
        token = decode_jwt(request)
        
        # Create Jira issue
        def create_jira_issue(project_key, summary, description, issue_type_id, uploads=None, urls=None):
            jira = get_jira_client()
            
            # Define issue details
            issue_dict = {
                'project': {'key':project_key},
                'summary': summary,
                'description': description,
                'issuetype': {'id': issue_type_id},
                'customfield_10073': token['UID']
            }
            if len(urls) > 0:
                issue_dict['customfield_10114'] = urls
            
            # Create the issue
            new_issue = jira.create_issue(fields=issue_dict)
            with connection.cursor() as cursor:
                cursor.execute(f"""
                    DECLARE @CurrDate DATE = CAST((SELECT SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time') AS DATE);
                    Insert into JiraTicket (JiraID, Timestamp, SenderID) VALUES ({new_issue.id}, @CurrDate, '{token['UID']}')
                """)
            if uploads:
                for file in uploads:
                    jira.add_attachment(issue=new_issue, attachment=file, filename=file.name  )

        try:
            image_urls=[]
            if upload_files:
                # Create a BlobServiceClient using the connection string
                blob_service_client = BlobServiceClient.from_connection_string(os.environ.get('AZURE_STORAGE_CONNECTION_STRING'))
                container_client = blob_service_client.get_container_client(os.environ.get('TICKET_CONTAINER'))

                for file in upload_files:
                    blob_client = container_client.get_blob_client(token['UID']+str(epoch_time)+file.name)
                    blob_client.upload_blob(file.read(), overwrite=True)
                    image_urls.append(blob_client.url)
                    
            description = ''
            if form.get('rectype'):
                description = f"{form['rectype']}: {form['record']}\n\n{form['description']}\n\nUID: {form['uid']}"
            else:
                description = form['description']

            
            create_jira_issue('DTT', form['subject'], description, form['type'], upload_files, ','.join(image_urls))
            
            resp = {
                'message': 'Ticket Added.',
                'imglink': image_urls,
                'comment': form['subject']
            }

            return Response(resp, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(str(e))
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateTicketViewSet(APIView):
    
    def post(self, request):
        print("Request Received")
        files = request.data
        upload_files = request.data.getlist('profileImage')
        comment_text = request.data.get('profileText')
        issue_id = request.data.get('issueId')
        comment_id = request.data.get('commentId')
        date_time = datetime.datetime.now()
        epoch_time = int(date_time.timestamp())
        uid = 'A006Z'
        
        print(files)
        print(files['profileImage'])
        for file in upload_files:
            print(file)  
        print(comment_text)

        # Create Jira issue
        def update_comment(issue_id, comment_id, new_comment_text):
            jira = get_jira_client()
            url = f'{jira._options["server"]}/rest/api/2/issue/{issue_id}/comment/{comment_id}'

            # Prepare the payload (body) for the PUT request
            payload = {
                "body": new_comment_text
            }
            
            # Make the PUT request to Jira's API
            try:
                response = jira._session.put(url, data=json.dumps(payload), headers={"Content-Type": "application/json"})
                if response.status_code == 200:
                    print(f"Comment {comment_id} updated successfully.")
                else:
                    print(f"Failed to update comment {comment_id}. Status: {response.status_code}")
            except JIRAError as e:
                print(f"Error updating comment: {e}")
                
        def add_comment_to_issue(issue_key, comment):
            jira = get_jira_client()  # Assuming you have this function from previous examples
            jira.add_comment(issue_key, comment)

        # Example usage


        try:
            image_urls=[]
            if upload_files:
                # Create a BlobServiceClient using the connection string
                blob_service_client = BlobServiceClient.from_connection_string(os.environ.get('AZURE_STORAGE_CONNECTION_STRING'))

                # Get the container client
                container_client = blob_service_client.get_container_client(os.environ.get('TICKET_CONTAINER'))

                # Upload the file to Azure Blob Storage
                for file in upload_files:
                    print(file)  
                    blob_client = container_client.get_blob_client(uid+str(epoch_time)+file.name)
                    blob_client.upload_blob(file.read(), overwrite=True)
                    image_urls.append(blob_client.url)
                print('Printing Upload File')
                print(upload_files)
            
            
            resp = {
                'message': 'Jira Comment Sent.',
                'imglink': image_urls,
                'comment': comment_text
            }

            return Response(resp, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(str(e))
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteTicketViewSet(APIView):
    
    def post(self, request):
        print("Request Received")
        issue_id = request.data.get('issueId')
        comment_id = request.data.get('commentId')


        # Delete a comment using its ID
        def delete_comment(issue_id, comment_id):
            jira = get_jira_client()
            issue = jira.issue(issue_id)
            url = f'{jira._options["server"]}/rest/api/2/issue/{issue_id}/comment/{comment_id}'
            
            # Make the DELETE request to Jira's API
            try:
                response = jira._session.delete(url)
                if response.status_code == 204:
                    print(f"Comment {comment_id} deleted successfully.")
                else:
                    print(f"Failed to delete comment {comment_id}. Status: {response.status_code}")
            except JIRAError as e:
                print(f"Error deleting comment: {e}")


        try:
            delete_comment(issue_id, comment_id)
            
            resp = {
                'message': 'Jira Comment Deleted.'
            }

            return Response(resp, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(str(e))
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AddCommentViewSet(APIView):
    
    def post(self, request):
        print("Request Received")
        issue_id = request.data.get('issue_id')
        comment_text = request.data.get('comment_text')
        
        try:
            jira = get_jira_client()  # Assuming you have this function from previous examples
            jira.add_comment(issue_id, comment_text)
            
            resp = {
                'message': 'Jira Comment Added.'
            }

            return Response(resp, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(str(e))
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class UpdateCommentViewSet(APIView):
    
    def post(self, request):
        print("Request Received")
        files = request.data
        upload_files = request.data.getlist('profileImage')
        comment_text = request.data.get('profileText')
        issue_id = request.data.get('issueId')
        comment_id = request.data.get('commentId')
        date_time = datetime.datetime.now()
        epoch_time = int(date_time.timestamp())
        uid = 'A006Z'
        
        print(files)
        print(files['profileImage'])
        for file in upload_files:
            print(file)  
        print(comment_text)

        # Create Jira issue
        def update_comment(issue_id, comment_id, new_comment_text):
            jira = get_jira_client()
            url = f'{jira._options["server"]}/rest/api/2/issue/{issue_id}/comment/{comment_id}'

            # Prepare the payload (body) for the PUT request
            payload = {
                "body": new_comment_text
            }
            
            # Make the PUT request to Jira's API
            try:
                response = jira._session.put(url, data=json.dumps(payload), headers={"Content-Type": "application/json"})
                if response.status_code == 200:
                    print(f"Comment {comment_id} updated successfully.")
                else:
                    print(f"Failed to update comment {comment_id}. Status: {response.status_code}")
            except JIRAError as e:
                print(f"Error updating comment: {e}")
                
        def add_comment_to_issue(issue_key, comment):
            jira = get_jira_client()  # Assuming you have this function from previous examples
            jira.add_comment(issue_key, comment)

        # Example usage


        try:
            image_urls=[]
            if upload_files:
                # Create a BlobServiceClient using the connection string
                blob_service_client = BlobServiceClient.from_connection_string(os.environ.get('AZURE_STORAGE_CONNECTION_STRING'))

                # Get the container client
                container_client = blob_service_client.get_container_client(os.environ.get('TICKET_CONTAINER'))

                # Upload the file to Azure Blob Storage
                for file in upload_files:
                    print(file)  
                    blob_client = container_client.get_blob_client(uid+str(epoch_time)+file.name)
                    blob_client.upload_blob(file.read(), overwrite=True)
                    image_urls.append(blob_client.url)
                print('Printing Upload File')
                print(upload_files)
            
            
            resp = {
                'message': 'Jira Comment Sent.',
                'imglink': image_urls,
                'comment': comment_text
            }

            return Response(resp, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(str(e))
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteCommentViewSet(APIView):
    
    def post(self, request):
        print("Request Received")
        issue_id = request.data.get('issueId')
        comment_id = request.data.get('commentId')


        # Delete a comment using its ID
        def delete_comment(issue_id, comment_id):
            jira = get_jira_client()
            issue = jira.issue(issue_id)
            url = f'{jira._options["server"]}/rest/api/2/issue/{issue_id}/comment/{comment_id}'
            
            # Make the DELETE request to Jira's API
            try:
                response = jira._session.delete(url)
                if response.status_code == 204:
                    print(f"Comment {comment_id} deleted successfully.")
                else:
                    print(f"Failed to delete comment {comment_id}. Status: {response.status_code}")
            except JIRAError as e:
                print(f"Error deleting comment: {e}")


        try:
            delete_comment(issue_id, comment_id)
            
            resp = {
                'message': 'Jira Comment Deleted.'
            }

            return Response(resp, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(str(e))
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        

# Django View to get an issue by its ID
class GetMyIssuesViewSet(APIView):
    def get(self, request):
        jira = get_jira_client()
        
        
        try:
            token = decode_jwt(request)   
            issues = []
            fields = "summary,status,assignee,customfield_10114,customfield_10073, issuetype, created, updated, description, attachment, comment"  # Limit fields to only required ones
            issue_ids = []
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM JiraTicket WHERE SenderId = '{0}'".format(token['UID']))
                issuerecs = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
                for rec in issuerecs:
                    issue_ids.append(str(rec['JiraID']))
                    
                jql_query = 'key in ({})'.format(','.join(issue_ids))
                issues = jira.search_issues(jql_query, maxResults=len(issue_ids), json_result=True, fields=fields)
                
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(issues, status=status.HTTP_200_OK)
        

# Django View to get an issue by its ID

@csrf_exempt
@async_to_sync
async def issue_webhook(request):
    def update_issue():
        with connection.cursor() as cursor:
            cursor.execute(f"EXEC spJiraSaveIssue  @IssueKey={issue_id}, @IssueData='{issue_json}', @IssueAction='{action}', @IssueAction='{action}'")
            recs = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
        return recs
        
    # def delete_comment():
    #     with connection.cursor() as cursor:
    #         cursor.execute(f"""EXEC spJiraDeleteComment @CommentId='{comment_id}'""")
    #         recs = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
    #     return recs
    
    if request.method == 'POST':
        data = json.loads(request.body)
        issue = data.get("issue", {})
        issue_id = issue.get("id", "")
        sender_id = data.get("issue", {}).get("fields", "").get("customfield_10073", "")
        action = data.get('webhookEvent', 'Unknown event')
        issue_json = json.dumps(issue, indent=2).replace("'","''")
        
        message_title = 'DDD Ticket Update'
        if action == 'jira:issue_updated':
            message_body = 'Your ticket has a new update. Please check at your own convenience'

        result = send_push_notification(sender_id, message_title, message_body) 
        
        rec = await sync_to_async(update_issue)()   
    
        # if project_id == "10000" or project_id == "10003":
        #     if event == "comment_created":
        #         recs = await sync_to_async(create_comment)()
                
        #     elif event == "comment_deleted":
        #         recs = await sync_to_async(delete_comment)()
                

                
        #     formatted_text = process_data(recs,comment_author_name)
            
        #     await bot.send_message(chat_id=CHAT_ID, text=formatted_text, message_thread_id=MSG_THREAD_ID)
        
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'failed'}, status=400)



class GetGroupIssuesViewSet(APIView):
    def get(self, request):
        jira = get_jira_client()
        
        try:
            token = decode_jwt(request)   
            issues = []
            with connection.cursor() as cursor:
                cursor.execute("""SELECT M.Name 'Mname', J.* FROM JiraTicket J LEFT JOIN MemberData M ON M.UID = J.SenderId 
                                WHERE M.MemberGroup = (Select MemberGroup From MemberData WHERE UID = '{0}')""".format(token['UID']))
                issuerecs = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
                for rec in issuerecs:
                    issue = jira.issue(rec['JiraID'])
                    issue_raw = issue.raw
                    issue_raw['Member'] = rec['Mname']
            
                    issues.append(issue_raw)  
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(issues, status=status.HTTP_200_OK)