import pandas as pd
import warnings
import random
import asyncio
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status
from ddd.models import Memberdata
from django.db import connection as conn
from telegram import Bot
from ddd.utils import decode_jwt
from api.redis import Redis

bot = Bot(token='6501158473:AAEV7rkaYWW0k6RKdCx6v2DwZZbK3vQr7C8')

class OTP(APIView):
    def post(self, request):
        try:
            payload = decode_jwt(request)
            userID = payload['UID']
            print(os.environ.get('BOT_TOKEN'))

            tel_id_dataframe = pd.read_sql(f"SELECT TOP 1 TelID FROM TelegramBotData WHERE UID = '{userID}'",conn).to_dict(orient='records')
            if len(tel_id_dataframe) == 0:
                print("Telegram ID not found")
                return Response("Telegram ID not found")


            tel_id = str(tel_id_dataframe[0]['TelID'])

            otp_dataframe = pd.read_sql(f"""SELECT TOP 1 OTP FROM OtpLog WHERE UID = '{userID}'
        AND ValidUntil > CONVERT(DateTime, SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time') ORDER BY ValidUntil DESC""",conn)

            if len(otp_dataframe) == 1:
                print("Valid Code Already Active")
                return

            otp = ''.join([str(random.randint(0,9)) for _ in range(6)])
            conn.cursor().execute(f"""INSERT INTO OtpLog (UID, OTP, ValidUntil)
        VALUES ('{userID}', {otp}, DATEADD(MINUTE,1,CONVERT(DateTime, SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')))""")
            conn.cursor().close()
            message = f"Your OTP for the website login is: {otp}"
            async def send_message():
                bot.send_message(chat_id=tel_id, text=message)
            asyncio.run(send_message())
        except Exception as e:
            print(f"An error occurred: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            return Response('Code Sent!', status=status.HTTP_200_OK)


class CheckAuthenticated(APIView):
    def post(self,request):
        try:
            payload = decode_jwt(request)
            userID = payload['UID']
            auth_hash = request.data['authenticated_hash']
            if(Redis.checkExists('getAuthenticatedUser', userID)):
                print("Key exists in Redis")
                redis_auth_hash = Redis.hget("getAuthenticatedUser", userID)
            else:
                return Response('No Multi-Factor Authentication Found', status=status.HTTP_404_NOT_FOUND)

            if auth_hash != redis_auth_hash:
                print("Multi-Factor Authentication Invalid!")
                return Response('Multi-Factor Authentication Invalid', status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"An error occurred: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            return Response('Valid Authentication', status=status.HTTP_200_OK)

class RemoveAuthenticated(APIView):
    def delete(self, request):
        payload = decode_jwt(request)
        userID = payload['UID']

        print('Revoked User MFA')
        return Redis.delete("getAuthenticatedUser", userID)

class VerifyOTP(APIView):
    def post(self, request):
        warnings.filterwarnings('ignore')

        try:
            payload = decode_jwt(request)
            userID = payload['UID']
            otp = request.data['otp']

            otp_dataframe = pd.read_sql(f"""SELECT TOP 1 OTP FROM OtpLog WHERE UID = '{userID}'
        AND ValidUntil > CONVERT(DateTime, SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time') ORDER BY ValidUntil DESC""",conn)
            if len(otp_dataframe) == 0:
                print("OTP Expired")
                return Response('OTP Expired!', status=status.HTTP_400_BAD_REQUEST)

            otp_db = otp_dataframe.iloc[0,0]

            if otp != otp_db:
                print("Invalid OTP")
                return Response('Invalid OTP!', status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"An error occurred: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            print("Authentication successful")
            authenticated_hash = hash(userID + str(request.data['otp']))
            Redis.hset('getAuthenticatedUser', userID, authenticated_hash)
            return Response(authenticated_hash, status=status.HTTP_200_OK)

