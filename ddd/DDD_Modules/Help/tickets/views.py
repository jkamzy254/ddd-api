from django.shortcuts import render
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view

    
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.db import connection
import datetime, json, pandas as pd
from azure.storage.blob import BlobServiceClient
import os
from dotenv import load_dotenv, find_dotenv
import base64
import requests
from jira import JIRA, JIRAError
from jira.resources import Issue
from ddd.utils import decode_jwt

load_dotenv(find_dotenv())

# Create your views here.

def get_jira_client():
    jira_options = {'server': os.environ.get('JIRA_URL')}
    jira = JIRA(options=jira_options, basic_auth=(os.environ.get('JIRA_USERNAME'), os.environ.get('TICKET_TOKEN')))
    return jira

class AddTicketViewSet(APIView):
    
    def post(self, request):
        print("Request Received")
        form = request.data
        upload_files = form.getlist('ticketFiles')
        date_time = datetime.datetime.now()
        epoch_time = int(date_time.timestamp())
        token = decode_jwt(request)
        

        # Create Jira issue
        def create_jira_issue(project_key, summary, description, issue_type_id, uploads=None):
            jira = get_jira_client()
            
            # Define issue details
            issue_dict = {
                'project': {'key':project_key},
                'summary': summary,
                'description': description,
                'issuetype': {'id': issue_type_id},
                'customfield_10073': token['UID']
            }
            
            # Create the issue
            new_issue = jira.create_issue(fields=issue_dict)
            if uploads:
                for file in uploads:
                    jira.add_attachment(issue=new_issue, attachment=file, filename=file.name  )

        try:
            image_urls=[]
            if upload_files:
                # Create a BlobServiceClient using the connection string
                blob_service_client = BlobServiceClient.from_connection_string(os.environ.get('AZURE_STORAGE_CONNECTION_STRING'))

                # Get the container client
                container_client = blob_service_client.get_container_client(os.environ.get('TICKET_CONTAINER'))

                # Upload the file to Azure Blob Storage
                for file in upload_files:
                    blob_client = container_client.get_blob_client(token['UID']+str(epoch_time)+file.name)
                    blob_client.upload_blob(file.read(), overwrite=True)
                    image_urls.append(blob_client.url)
                    
            description = ''
            if form.get('rectype'):
                description = f"{form['rectype']}: {form['record']}\n\n{form['description']}\n\nUID: {form['uid']}"
            else:
                description = form['description']

            
            create_jira_issue('DTT', form['subject'], description, form['type'], upload_files)
            
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
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM JiraTicket WHERE SenderId = '{0}'".format(token['UID']))
                issuerecs = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
                for rec in issuerecs:
                    issue = jira.issue(rec['JiraID'])
                    # Issue._parse_raw(issue)
                    print(issue.raw)
            
                    issues.append(issue.raw)  
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(issues, status=status.HTTP_200_OK)


class GetGroupIssuesViewSet(APIView):
    def get(self, request):
        jira = get_jira_client()
        
        try:
            token = decode_jwt(request)   
            issues = []
            with connection.cursor() as cursor:
                cursor.execute("""SELECT * FROM JiraTicket J LEFT JOIN MemberData M ON M.UID = J.SenderId 
                                WHERE M.MemberGroup = (Select MemberGroup From MemberData WHERE UID = '{0}')""".format(token['UID']))
                issuerecs = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
                for rec in issuerecs:
                    issue = jira.issue(rec['JiraID'])
                    # Issue._parse_raw(issue)
                    print(issue.raw)
            
                    issues.append(issue.raw)  
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(issues, status=status.HTTP_200_OK)