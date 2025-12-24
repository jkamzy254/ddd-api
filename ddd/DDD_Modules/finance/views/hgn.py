from django.shortcuts import get_object_or_404, render
from django.http import Http404
from rest_framework.decorators import api_view
from ddd.utils import decode_jwt

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.db import connection


########### GET REQUESTS ###########


class FinAccess(APIView): # https://id.ngrok-free.app/api/finance/getFinAccess/
    def get(self, request):
        try:
            token = decode_jwt(request)
            uid = token['UID']
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT Access FROM FinAccess WHERE UID = '{uid}'")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class FinIncomeSummary(APIView): # https://id.ngrok-free.app/api/finance/getFinIncomeSummary?yrmth=Mar-25&grp=G21
    def get(self, request):
        try:
            token = decode_jwt(request)
            uid = token['UID']
            yrmth = f", '{request.GET.get('yrmth')}'" if request.GET.get('yrmth') else ''
            grp = f", '{request.GET.get('grp')}'" if request.GET.get('grp') else ''
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spFinIncomeSummary '{uid}'{yrmth}{grp}")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class FinIncomeList(APIView):
    def get(self, request):
        try:
            token = decode_jwt(request)
            uid = token['UID']
            yrmth = ", '" + request.GET.get('yrmth') + "'" if request.GET.get('yrmth') else ''
            grp = ", '" + request.GET.get('grp') + "'" if request.GET.get('grp') else ''
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spFinIncomeList '{uid}'{yrmth}{grp}")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class FinTransferList(APIView):
    def get(self, request):
        try:
            token = decode_jwt(request)
            uid = token['UID']
            yrmth = ", '" + request.GET.get('yrmth') + "'" if request.GET.get('yrmth') else ''
            grp = ", '" + request.GET.get('grp') + "'" if request.GET.get('grp') else ''
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spFinTransferList '{uid}'{yrmth}{grp}")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



class FinExpenseSummary(APIView):
    def get(self, request):
        try:
            token = decode_jwt(request)
            uid = token['UID']
            yrmth = ", '" + request.GET.get('yrmth') + "'" if request.GET.get('yrmth') else ''
            grp = ", '" + request.GET.get('grp') + "'" if request.GET.get('grp') else ''
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spFinExpenseSummary '{uid}'{yrmth}{grp}")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





class FinClaimsList(APIView):
    def get(self, request):
        try:
            token = decode_jwt(request)
            uid = token['UID']
            yrmth = ", '" + request.GET.get('yrmth') + "'" if request.GET.get('yrmth') else ''
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spFinClaimsList '{uid}'{yrmth}")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class FinClaimPopUp(APIView):
    def get(self, request):
        try:
            token = decode_jwt(request)
            uid = token['UID']
            status_parameter = request.GET.get('status') # 'status' is a reserved word
            grp = request.GET.get('grp')
            claimid = request.GET.get('claimid')
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spFinClaimPopUp '{uid}', '{status_parameter}', '{grp}', {claimid}")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



class FinReceiptPopUp(APIView):
    def get(self, request):
        try:
            token = decode_jwt(request)
            uid = token['UID']
            claimid = request.GET.get('claimid')
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spFinReceiptPopUp '{uid}', {claimid}")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class FinHgnSummaryMonth(APIView):
    def get(self, request):
        try:
            token = decode_jwt(request)
            uid = token['UID']
            yrmth = ", '" + request.GET.get('yrmth') + "'" if request.GET.get('yrmth') else ''
            grp = ", '" + request.GET.get('grp') + "'" if request.GET.get('grp') else ''
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spFinHgnSummaryMonth '{uid}'{yrmth}{grp}")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        


class FinBalanceSummary(APIView):
    def get(self, request):
        try:
            token = decode_jwt(request)
            uid = token['UID']
            grp = f", '{request.GET.get('grp')}'" if request.GET.get('grp') else ''
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spFinBalanceSummary '{uid}'{grp}")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


########### POST REQUESTS ###########



class FinInsertIncome(APIView):
    def post(self, request):
        try:   
            token = decode_jwt(request)
            uid = token['UID']
            payload = request.data
            src = payload['src']
            amt = payload['amt']
            det = payload['det']
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spFinInsertIncome '{uid}', '{src}', {amt}, '{det}'")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class FinInsertClaim(APIView):
    def post(self, request):
        try:   
            token = decode_jwt(request)
            uid = token['UID']
            payload = request.data
            grp = payload['grp']
            reqcategory = payload['reqcategory']
            claimname = payload['claimname'].replace("'", "''")
            reqamount = payload['reqamount']
            claimdate = payload['claimdate']
            detailedinfo = payload['detailedinfo'].replace("'", "''")
            expensetype = payload['expensetype']
            bankname = payload['bankname'].replace("'", "''")
            accountname = payload['accountname'].replace("'", "''")
            bsb = payload['bsb']
            accountnumber = payload['accountnumber']
            transfergroups = f"'{payload['transfergroups']}'" if payload['transfergroups'] is not None else 'NULL'
            claimid = f", {(payload['claimid'])}" if 'claimid' in payload else ''
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spFinInsertClaim '{uid}','{grp}','{reqcategory}','{claimname}',{reqamount},'{claimdate}','{detailedinfo}','{expensetype}','{bankname}','{accountname}',{bsb},{accountnumber},{transfergroups}{claimid}")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        




class FinInsertReceipt(APIView):
    def post(self, request):
        try:   
            token = decode_jwt(request)
            uid = token['UID']
            payload = request.data
            claimid = payload['claimid']
            receipturl = payload['receipturl'].replace("'", "''")
            transferurl = payload['transferurl']
            itemsjson = payload['itemsjson'].replace("'", "''")
            grp = f", '{(payload['grp'])}'" if 'grp' in payload else ''
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spFinInsertReceipt {claimid}, '{uid}', '{receipturl}', '{transferurl}', '{itemsjson}'{grp}")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      



class FinInsertBalanceSS(APIView):
    def post(self, request):
        try:   
            token = decode_jwt(request)
            uid = token['UID']
            payload = request.data
            url = payload['url'].replace("'", "''")
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spFinInsertBalanceSS '{uid}', '{url}'")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


########### PUT REQUESTS ###########



class FinInsertSpending(APIView):
    def put(self, request):
        try:   
            token = decode_jwt(request)
            uid = token['UID']
            payload = request.data
            claimid = payload['claimid']
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spFinInsertSpending {claimid}")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class FinDeleteBalanceSS(APIView):
    def put(self, request):
        try:   
            token = decode_jwt(request)
            uid = token['UID']
            payload = request.data
            id = payload['id']
            deleted = payload['deleted']
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spFinDeleteBalanceSS {id}, {deleted}")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



class FinDeleteClaim(APIView):
    def put(self, request):
        try:   
            token = decode_jwt(request)
            uid = token['UID']
            payload = request.data
            claimid = payload['claimid']
            deleted = payload['deleted']
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spFinDeleteClaim {claimid}, {deleted}")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class FinDeleteDonation(APIView):
    def put(self, request):
        try:   
            token = decode_jwt(request)
            uid = token['UID']
            payload = request.data
            id = payload['id']
            deleted = payload['deleted']
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spFinDeleteDonation {id}, {deleted}")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



class FinDeleteIncome(APIView):
    def put(self, request):
        try:   
            token = decode_jwt(request)
            uid = token['UID']
            payload = request.data
            incomeid = payload['incomeid']
            deleted = payload['deleted']
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spFinDeleteIncome {incomeid}, {deleted}")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class FinDeleteTransfer(APIView):
    def put(self, request):
        try:   
            token = decode_jwt(request)
            uid = token['UID']
            payload = request.data
            transferid = payload['transferid']
            deleted = payload['deleted']
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spFinDeleteTransfer {transferid}, {deleted}")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



########### DELETE REQUESTS ###########



class FinDeleteReceipt(APIView):
    def delete(self, request):
        try:   
            token = decode_jwt(request)
            uid = token['UID']
            payload = request.data
            receiptid = payload['receiptid']
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spFinDeleteReceipt {receiptid}")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
