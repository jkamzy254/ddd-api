"""
Church Regrouping — Django views for the Apps Script app.

Paste into the app's views.py (fetch_rows is the same helper the BBT views
already use; keep one copy) and route them in urls.py:

    path('churchRegrpGetMember/',      ChurchRegrpGetMemberViewSet.as_view()),
    path('churchRegrpGetContext/',     ChurchRegrpGetContextViewSet.as_view()),
    path('churchRegrpGetGroups/',      ChurchRegrpGetGroupsViewSet.as_view()),
    path('churchRegrpGetTasks/',       ChurchRegrpGetTasksViewSet.as_view()),
    path('churchRegrpGetTaskRefs/',    ChurchRegrpGetTaskRefsViewSet.as_view()),
    path('churchRegrpGetMembers/',     ChurchRegrpGetMembersViewSet.as_view()),
    path('churchRegrpGetRequests/',    ChurchRegrpGetRequestsViewSet.as_view()),
    path('churchRegrpSearchMembers/',  ChurchRegrpSearchMembersViewSet.as_view()),
    path('churchRegrpSaveRequest/',    ChurchRegrpSaveRequestViewSet.as_view()),
    path('churchRegrpResolve/',        ChurchRegrpResolveViewSet.as_view()),
    path('churchRegrpSetDeptLeader/',  ChurchRegrpSetDeptLeaderViewSet.as_view()),
    path('churchRegrpMoveGroup/',      ChurchRegrpMoveGroupViewSet.as_view()),
    path('churchRegrpGroupHistory/',   ChurchRegrpGroupHistoryViewSet.as_view()),
    path('churchRegrpArchive/',        ChurchRegrpArchiveViewSet.as_view()),
    path('churchRegrpSetGroupRule/',   ChurchRegrpSetGroupRuleViewSet.as_view()),
    path('churchRegrpSetMemberProfile/', ChurchRegrpSetMemberProfileViewSet.as_view()),
    path('churchRegrpProfileHistory/', ChurchRegrpProfileHistoryViewSet.as_view()),
    path('churchRegrpCTGetMembers/',   ChurchRegrpCTGetMembersViewSet.as_view()),
    path('churchRegrpCTGetGroups/',    ChurchRegrpCTGetGroupsViewSet.as_view()),
    path('churchRegrpCTMove/',         ChurchRegrpCTMoveViewSet.as_view()),
    path('churchRegrpCTSetLeader/',    ChurchRegrpCTSetLeaderViewSet.as_view()),
    path('churchRegrpCTHistory/',      ChurchRegrpCTHistoryViewSet.as_view()),
    path('churchRegrpCTSaveGroup/',    ChurchRegrpCTSaveGroupViewSet.as_view()),
    path('churchRegrpGetSubdivisions/', ChurchRegrpGetSubdivisionsViewSet.as_view()),
    path('churchRegrpSetSubdivLeader/', ChurchRegrpSetSubdivLeaderViewSet.as_view()),
    path('churchRegrpMemberSheet/',    ChurchRegrpMemberSheetViewSet.as_view()),   # needs X-Sync-Key

If the login view you already have is routed somewhere else, either route
this one as above or change ENDPOINTS.member in Code.js.

Every value is bound with %s. Nothing from the request is formatted into SQL.
"""

import re

from django.db import connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


def fetch_rows(cursor):
    """Rows as dicts; [] when the statement returned no result set."""
    if cursor.description is None:
        return []
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, record)) for record in cursor.fetchall()]


def blank_to_none(value):
    """A GET parameter or JSON field left empty means NULL, not ''."""
    if value is None:
        return None
    if isinstance(value, str) and value.strip() == '':
        return None
    return value


def sql_error(e):
    """
    The procedures THROW sentences meant for the user, with error numbers
    50000 and up. pyodbc wraps them as
    "... [SQL Server]You do not have access to this department. (50002) (SQLExecDirectW)".
    Only those sentences are passed on. Anything else (a missing object, a
    type error, a lost connection) would show the database's structure, so it
    goes to the server log and the page gets a plain message.
    """
    found = re.findall(r'\[SQL Server\](.*?)\s*\((\d+)\)', str(e))
    if found and int(found[-1][1]) >= 50000:
        return found[-1][0].strip()
    print('Church Regrouping — server error:', e)
    return 'The server could not complete that. Please try again, or tell the administrator if it keeps happening.'


def error_response(e):
    return Response({'error': sql_error(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# --- login ----------------------------------------------------------------------------

# Replaces GetMemberViewSet: the old one formatted the username and password
# straight into the EXEC, so a quote in either field was SQL injection.
# Accepts POST (what Code.js sends, so the password stays out of URLs and
# access logs) and GET (so anything still calling it the old way keeps working).
class ChurchRegrpGetMemberViewSet(APIView):
    def login(self, source):
        username = source.get('username') or ''
        password = source.get('password') or ''

        if not username or not password:
            return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "EXEC spChurchRegrpAppsScriptLogin @Username = %s, @Password = %s",
                    [username, password]
                )
                result = fetch_rows(cursor)

            if len(result) == 0:
                return Response({'error': 'Unauthorized Access'}, status=status.HTTP_401_UNAUTHORIZED)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)

    def get(self, request):
        return self.login(request.GET)

    def post(self, request):
        return self.login(request.data)


# --- reads ----------------------------------------------------------------------------

class ChurchRegrpGetContextViewSet(APIView):
    def get(self, request):
        uid = request.GET.get('UID')
        if not uid:
            return Response({'error': 'UID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute("EXEC spChurchRegrpGetContext @UID = %s", [uid])
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


class ChurchRegrpGetGroupsViewSet(APIView):
    def get(self, request):
        uid = request.GET.get('UID')
        if not uid:
            return Response({'error': 'UID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute("EXEC spChurchRegrpGetGroups @UID = %s", [uid])
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


class ChurchRegrpGetTasksViewSet(APIView):
    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("EXEC spChurchRegrpGetTasks")
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


class ChurchRegrpGetTaskRefsViewSet(APIView):
    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("EXEC spChurchRegrpGetTaskRefs")
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


class ChurchRegrpGetMembersViewSet(APIView):
    def get(self, request):
        uid = request.GET.get('UID')
        did = request.GET.get('DID', '')
        if not uid or not did.isdigit():
            return Response({'error': 'UID and DID are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute("EXEC spChurchRegrpGetMembers @UID = %s, @DID = %s", [uid, int(did)])
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


class ChurchRegrpGetRequestsViewSet(APIView):
    def get(self, request):
        uid = request.GET.get('UID')
        req_status = blank_to_none(request.GET.get('Status')) or 'Pending'
        days = request.GET.get('Days', '')

        if not uid:
            return Response({'error': 'UID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "EXEC spChurchRegrpGetRequests @UID = %s, @Status = %s, @Days = %s",
                    [uid, req_status, int(days) if days.isdigit() else None]
                )
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


class ChurchRegrpSearchMembersViewSet(APIView):
    def get(self, request):
        uid = request.GET.get('UID')
        q = (request.GET.get('q') or '').strip()
        if not uid:
            return Response({'error': 'UID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute("EXEC spChurchRegrpSearchMembers @UID = %s, @Q = %s", [uid, q[:50]])
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


# --- writes ---------------------------------------------------------------------------
#
# Each procedure answers with rows carrying Ok (1/0) and Res (a sentence), so
# a refusal such as "This member is not in one of your departments." arrives
# as a 200 with Ok = 0. Code.js turns Ok = 0 into an error for the page.

class ChurchRegrpSaveRequestViewSet(APIView):
    def post(self, request):
        data = request.data
        actor = data.get('ActorUID')
        uid = data.get('UID')

        if not actor or not uid:
            return Response({'error': 'ActorUID and UID are required.'}, status=status.HTTP_400_BAD_REQUEST)

        keep = data.get('KeepPrevious')

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "EXEC spChurchRegrpSaveRequest @ActorUID = %s, @UID = %s, @ToGID = %s, "
                    "@ToTaskCode = %s, @Notes = %s, @KeepPrevious = %s, @ToTID = %s, @ToPID = %s",
                    [actor, uid,
                     blank_to_none(data.get('ToGID')),
                     blank_to_none(data.get('ToTaskCode')),
                     blank_to_none(data.get('Notes')),
                     None if keep is None else (1 if keep in (True, 1, '1', 'true') else 0),
                     blank_to_none(data.get('ToTID')),
                     blank_to_none(data.get('ToPID'))]
                )
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


class ChurchRegrpResolveViewSet(APIView):
    def post(self, request):
        data = request.data
        actor = data.get('ActorUID')
        ids = data.get('IDs')
        action = data.get('Action')

        if not actor or not ids or action not in ('Apply', 'Reject', 'Cancel', 'Accept', 'Decline'):
            return Response({'error': 'ActorUID, IDs and a valid Action are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if isinstance(ids, (list, tuple)):
            ids = ','.join(str(i) for i in ids)

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "EXEC spChurchRegrpResolve @ActorUID = %s, @IDs = %s, @Action = %s, "
                    "@EffectiveDate = %s, @Note = %s",
                    [actor, str(ids), action,
                     blank_to_none(data.get('EffectiveDate')),
                     blank_to_none(data.get('Note'))]
                )
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


class ChurchRegrpSetDeptLeaderViewSet(APIView):
    def post(self, request):
        data = request.data
        actor = data.get('ActorUID')
        dept = data.get('Dept')

        if not actor or not dept:
            return Response({'error': 'ActorUID and Dept are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "EXEC spChurchRegrpSetDeptLeader @ActorUID = %s, @Dept = %s, @LeaderUID = %s, "
                    "@NF = %s, @EffectiveDate = %s",
                    [actor, dept,
                     blank_to_none(data.get('LeaderUID')),
                     1 if data.get('NF') in (True, 1, '1', 'true') else 0,
                     blank_to_none(data.get('EffectiveDate'))]
                )
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


class ChurchRegrpMoveGroupViewSet(APIView):
    def post(self, request):
        data = request.data
        actor = data.get('ActorUID')
        gid = data.get('GID')
        did = data.get('DID')

        if not actor or gid in (None, '') or did in (None, ''):
            return Response({'error': 'ActorUID, GID and DID are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "EXEC spChurchRegrpMoveGroup @ActorUID = %s, @GID = %s, @DID = %s, @EffectiveDate = %s",
                    [actor, int(gid), int(did), blank_to_none(data.get('EffectiveDate'))]
                )
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


class ChurchRegrpGroupHistoryViewSet(APIView):
    def get(self, request):
        uid = request.GET.get('UID')
        gid = request.GET.get('GID', '')
        if not uid or not gid.isdigit():
            return Response({'error': 'UID and GID are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute("EXEC spChurchRegrpGetGroupHistory @UID = %s, @GID = %s", [uid, int(gid)])
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


class ChurchRegrpArchiveViewSet(APIView):
    def post(self, request):
        data = request.data
        actor = data.get('ActorUID')
        kind = data.get('Kind')
        ref_id = data.get('RefID')

        if not actor or kind not in ('Group', 'Dept') or ref_id in (None, ''):
            return Response({'error': 'ActorUID, Kind and RefID are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "EXEC spChurchRegrpArchive @ActorUID = %s, @Kind = %s, @RefID = %s, @Archive = %s, @Reason = %s",
                    [actor, kind, int(ref_id),
                     1 if data.get('Archive') in (True, 1, '1', 'true') else 0,
                     blank_to_none(data.get('Reason'))]
                )
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


class ChurchRegrpSetGroupRuleViewSet(APIView):
    def post(self, request):
        data = request.data
        actor = data.get('ActorUID')
        gid = data.get('GID')

        if not actor or gid in (None, ''):
            return Response({'error': 'ActorUID and GID are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "EXEC spChurchRegrpSetGroupRule @ActorUID = %s, @GID = %s, @NoGYJN = %s",
                    [actor, int(gid), 1 if data.get('NoGYJN') in (True, 1, '1', 'true') else 0]
                )
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


class ChurchRegrpSetMemberProfileViewSet(APIView):
    def post(self, request):
        data = request.data
        actor = data.get('ActorUID')
        uid = data.get('UID')

        if not actor or not uid:
            return Response({'error': 'ActorUID and UID are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "EXEC spChurchRegrpSetMemberProfile @ActorUID = %s, @UID = %s, @Category = %s, @Schedule = %s",
                    [actor, uid, blank_to_none(data.get('Category')), blank_to_none(data.get('Schedule'))]
                )
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


class ChurchRegrpProfileHistoryViewSet(APIView):
    def get(self, request):
        uid = request.GET.get('UID')
        member = request.GET.get('MemberUID')
        if not uid or not member:
            return Response({'error': 'UID and MemberUID are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute("EXEC spChurchRegrpGetProfileHistory @UID = %s, @MemberUID = %s", [uid, member])
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


# --- MCT internal groups (IT admin / CT leadership only; the procedures check) ------------

class ChurchRegrpCTGetMembersViewSet(APIView):
    def get(self, request):
        uid = request.GET.get('UID')
        if not uid:
            return Response({'error': 'UID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute("EXEC spChurchRegrpCTGetMembers @UID = %s", [uid])
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


class ChurchRegrpCTGetGroupsViewSet(APIView):
    def get(self, request):
        uid = request.GET.get('UID')
        if not uid:
            return Response({'error': 'UID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute("EXEC spChurchRegrpCTGetGroups @UID = %s", [uid])
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


class ChurchRegrpCTMoveViewSet(APIView):
    def post(self, request):
        data = request.data
        actor = data.get('ActorUID')
        uids = data.get('UIDs')

        if not actor or not uids:
            return Response({'error': 'ActorUID and UIDs are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if isinstance(uids, (list, tuple)):
            uids = ','.join(str(u) for u in uids)

        ct_gid = blank_to_none(data.get('CTGID'))

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "EXEC spChurchRegrpCTMove @ActorUID = %s, @UIDs = %s, @CTGID = %s, @EffectiveDate = %s",
                    [actor, str(uids), None if ct_gid is None else int(ct_gid),
                     blank_to_none(data.get('EffectiveDate'))]
                )
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


class ChurchRegrpCTSetLeaderViewSet(APIView):
    def post(self, request):
        data = request.data
        actor = data.get('ActorUID')
        uids = data.get('UIDs')

        if not actor or not uids:
            return Response({'error': 'ActorUID and UIDs are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if isinstance(uids, (list, tuple)):
            uids = ','.join(str(u) for u in uids)

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "EXEC spChurchRegrpCTSetLeader @ActorUID = %s, @UIDs = %s, @IsLeader = %s, @EffectiveDate = %s",
                    [actor, str(uids),
                     1 if data.get('IsLeader') in (True, 1, '1', 'true') else 0,
                     blank_to_none(data.get('EffectiveDate'))]
                )
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


class ChurchRegrpCTHistoryViewSet(APIView):
    def get(self, request):
        uid = request.GET.get('UID')
        member = request.GET.get('MemberUID')
        if not uid or not member:
            return Response({'error': 'UID and MemberUID are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute("EXEC spChurchRegrpCTHistory @UID = %s, @MemberUID = %s", [uid, member])
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


class ChurchRegrpCTSaveGroupViewSet(APIView):
    def post(self, request):
        data = request.data
        actor = data.get('ActorUID')
        name = (data.get('Grp') or '').strip()

        if not actor or not name:
            return Response({'error': 'ActorUID and Grp are required.'}, status=status.HTTP_400_BAD_REQUEST)

        gid = blank_to_none(data.get('GID'))
        active = data.get('AccountActive')

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "EXEC spChurchRegrpCTSaveGroup @ActorUID = %s, @GID = %s, @Grp = %s, @AccountActive = %s",
                    [actor, None if gid is None else int(gid), name[:50],
                     None if active is None else (1 if active in (True, 1, '1', 'true') else 0)]
                )
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


# --- subdivisions (admin) -----------------------------------------------------------------

class ChurchRegrpGetSubdivisionsViewSet(APIView):
    def get(self, request):
        uid = request.GET.get('UID')
        if not uid:
            return Response({'error': 'UID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute("EXEC spChurchRegrpGetSubdivisions @UID = %s", [uid])
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


class ChurchRegrpSetSubdivLeaderViewSet(APIView):
    def post(self, request):
        data = request.data
        actor = data.get('ActorUID')
        sid = data.get('SID')

        if not actor or sid in (None, ''):
            return Response({'error': 'ActorUID and SID are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "EXEC spChurchRegrpSetSubdivLeader @ActorUID = %s, @SID = %s, @LeaderUID = %s, @EffectiveDate = %s",
                    [actor, int(sid), blank_to_none(data.get('LeaderUID')), blank_to_none(data.get('EffectiveDate'))]
                )
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


# --- member sheet sync ---------------------------------------------------------------------
#
# Returns every member's row for the Google Sheet — INCLUDING usernames and
# passwords — so it answers only a request carrying the shared sync key:
#
#     settings.py (or the environment):  CHURCH_REGRP_SYNC_KEY = '<long random string>'
#     Apps Script script property:       SYNC_KEY = the same string
#
# With no key configured it refuses everything rather than serving openly.

import hmac
import os

from django.conf import settings


def sync_key_ok(request):
    expected = getattr(settings, 'CHURCH_REGRP_SYNC_KEY', None) or os.environ.get('CHURCH_REGRP_SYNC_KEY')
    given = request.headers.get('X-Sync-Key') or ''
    return bool(expected) and hmac.compare_digest(str(expected), str(given))


class ChurchRegrpMemberSheetViewSet(APIView):
    def get(self, request):
        if not sync_key_ok(request):
            return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

        try:
            with connection.cursor() as cursor:
                cursor.execute("EXEC spChurchRegrpMemberSheet")
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)
