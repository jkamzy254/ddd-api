import pandas as pd
import numpy as np
import pypyodbc as odbc
import re
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

HOST = os.environ.get('HOST')
DRIVER = os.environ.get('DRIVER')
DBPORT = os.environ.get('DBPORT')
DB = os.environ.get('DB')
DB_USER = os.environ.get('DB_USER')
PASS = os.environ.get('PASS')
PORT = os.environ.get('PORT')

conn_str = """
    Driver={{{0}}};
    Server={1},{2};
    Database={3};
    Uid={4};
    Pwd={5};
""".format(DRIVER,HOST,DBPORT,DB,DB_USER,PASS)

# All functions categorised as:

# IT FUNCTIONS
# ACCESS FUNCTIONS
# FMP FUNCTIONS
# BB FUNCTIONS
# BBT FUNCTIONS
# EDU FUNCTIONS
# MT FUNCTIONS

def format_display_name(value): # EDU FUNCTIONS (used in bb "list" functions that use case-sensitive pandas filtering to avoid the slow "OR" condition filtering in SQL when searching both leaves. Potentially could be used in any bb or fmp function involving both leaf )
    print(f"\n>>>calling format_display_name: value={value}")
    """Format g or d for display in the header only"""
    known = {
        'm&w dept': 'M&W Dept',
        'ct': 'CT',
        'innersft': 'InnerSFT',
        'sft': 'SFT',
        'mwdept': 'MWDept',
        'mwscm': 'MWSCM',
        'hwpl': 'HWPL',
        'gd': 'GD'
    }
    lookup = value.lower()
    if lookup in known:
        print(">>>Format display name: returning known value")
        return known[lookup]
    if re.match(r'^d\d+$', lookup, re.IGNORECASE):
        print(">>>Format display name: returning uppercase D value")
        return value.upper()  # D6, D11 etc.
    if re.match(r'^g\d+$', lookup, re.IGNORECASE):
        print(">>>Format display name: returning uppercase G value")
        return value.upper()  # G1, G26 etc.
    print(">>>Format display name: returning original value")
    return value  # fallback: return as-is

def commands(access): # ACCESS FUNCTIONS
    print(f"\n>>>commands: access={access}")
    if access in ('IT','All'):
        print(">>>Return")
        return '<b>🤖Using Codey🤖</b>\n____________________________________________________________________\n\n<u>📣General command structure📣</u>\n<b><i>&lt;CT&gt;</i></b><code>&lt;command&gt;</code><b><i>&lt;/g or //D&gt;</i></b>\n\n<u><b>👨‍🏫&lt;CT&gt;</b> = optional <b>prefix👩‍🏫</b></u>\n<i>▪️phys = physical CT (default if omitted)\n▪️sft = online CT\n▪️all = both physical + online</i>\n\n<u><b>👥&lt;/g or //D&gt;</b> = optional <b>suffix👥</b></u>\n<i>▪️/g = filters specific group (e.g. /G1, /EST2)\n▪️//D = filters specific department (e.g. //D1, //SFT, //InnerSFT)</i>\n____________________________________________________________________\n\n<b><i><u>📣Group FMP</u></i></b>\n\n<code>➡️&lt;timespan&gt;fmp\n\n&lt;timespan&gt;</code>\n<i>▪️today\n▪️yesterday\n▪️week\n▪️lastweek\n▪️season\n\ne.g. </i><code>todayfmp</code>\n____________________________________________________________________\n\n<b><u><i>📣Church FMP</i></u></b>\n\n<code>➡️&lt;Division or Task&gt;&lt;Timespan&gt;\n\n&lt;Division or Task&gt;</code>\n<i>▪️youth = all youth\n▪️tgw = all youth TGW only\n▪️member = all youth member only\n▪️gyjn/oev/iev/edu/sv = all youth specific task only\n▪️dept = department totals only\n\n💡Adding //SFT or //InnerSFT will replace youth groups with SFT groups\n\ne.g. </i><code>youthtoday</code>\n____________________________________________________________________\n\n<b><i><u>📣BB Commands</u></i></b>\n\n<code>➡️bb&lt;format&gt;\n\n&lt;format&gt;</code>\n<i>▪️status = table of status numbers per group\n▪️active = table: active statuses only\n▪️inactive = table: inactive statuses only\n▪️list = list of bb fruits\n\n💡Adding /g or //D will also show individual bbt result\n💡Make sure to filter bblist with /g or //D to reduce output\n\ne.g. </i><code>bblist//D1</code>\n____________________________________________________________________\n\n<b><i><u>📣BBT Commands</u></i></b>\n\n<code>➡️&lt;BbtType&gt;&lt;Format&gt;\n\n&lt;BbtType&gt;</code>\n<i>▪️bbt = all bbt + prebbt\n▪️gyjnbbt = all gyjns\n▪️btm# = all bbt/btm from specified btm number\n\ne.g.</i><code> bbtstatus</code>\n____________________________________________________________________\n\n<b><i><u>📣Other Commands</u></i></b>\n\n<code>➡️&lt;0411111111&gt;</code><i> = double fish check</i>'
    if access in ['D[0-9]%','D1','D2','D3','D4','D5','D6','D7','D8','D9','D10','D11','D12','D13','D14','D15','D16','D17','D18','D19','D20','¹D[0-9]%','²D[0-9]%','¹D1','¹D2','¹D3','¹D4','¹D5','¹D6','¹D7','¹D8','¹D9','²D1','²D2','²D3','²D4','²D5','²D6','²D7','²D8','²D9','SFT','Geelong','Dept','M&W Dept','InnerSFT']:
        print(">>>Return")
        return f'<b>🤖Using Codey🤖</b>\n____________________________________________________________________\n\n<u>📣General command structure📣</u>\n<b><i>&lt;CT&gt;</i></b><code>&lt;command&gt;</code><b><i>&lt;/g&gt;</i></b>\n\n<u><b>👨‍🏫&lt;CT&gt;</b> = optional <b>prefix👩‍🏫</b></u>\n<i>▪️phys = physical CT (default if omitted)\n▪️sft = online CT\n▪️all = both physical + online</i>\n\n<u><b>👥&lt;/g&gt;</b> = optional <b>suffix👥</b></u>\n<i>▪️/g = filters specific group (e.g. /G1, /EST2)</i>\n____________________________________________________________________\n\n<b><i><u>📣Group FMP</u></i></b>\n\n<code>➡️&lt;timespan&gt;fmp\n\n&lt;timespan&gt;</code>\n<i>▪️today\n▪️yesterday\n▪️week\n▪️lastweek\n▪️season\n\ne.g. </i><code>todayfmp</code>\n____________________________________________________________________\n\n<b><u><i>📣Dept FMP</i></u></b>\n\n<code>➡️&lt;Division or Task&gt;&lt;Timespan&gt;\n\n&lt;Division or Task&gt;</code>\n<i>▪️dept = all dept\n▪️tgw = all dept TGW only\n▪️member = all dept member only\n▪️gyjn/oev/iev/edu/sv = all dept specific task only\n\n💡Adding //SFT or //InnerSFT will replace dept groups with SFT groups\n\ne.g. </i><code>depttoday</code>\n____________________________________________________________________\n\n<b><i><u>📣BB Commands</u></i></b>\n\n<code>➡️bb&lt;format&gt;\n\n&lt;format&gt;</code>\n<i>▪️status = table of status numbers per group\n▪️active = table: active statuses only\n▪️inactive = table: inactive statuses only\n▪️list = list of bb fruits\n\ne.g. </i><code>bblist/G1</code>\n____________________________________________________________________\n\n<b><i><u>📣BBT Commands</u></i></b>\n\n<code>➡️&lt;BbtType&gt;&lt;Format&gt;\n\n&lt;BbtType&gt;</code>\n<i>▪️bbt = all bbt + prebbt\n▪️gyjnbbt = all gyjns\n▪️btm# = all bbt/btm from specified btm number\n\ne.g.</i><code> bbtstatus</code>\n____________________________________________________________________\n\n<b><i><u>📣Other Commands</u></i></b>\n\n<code>➡️&lt;0411111111&gt;</code><i> = double fish check</i>'
    if access in ('Group','CUL'):
        print(">>>Return")
        return f'<b>🤖Using Codey🤖</b>\n____________________________________________________________________\n\n<u>📣General command structure📣</u>\n<b><i>&lt;CT&gt;</i></b><code>&lt;command&gt;</code>\n\n<u><b>👨‍🏫&lt;CT&gt;</b> = optional <b>prefix👩‍🏫</b></u>\n<i>▪️phys = physical CT (default if omitted)\n▪️sft = online CT\n▪️all = both physical + online</i>\n____________________________________________________________________\n\n<b><i><u>📣Group FMP</u></i></b>\n\n<code>➡️&lt;timespan&gt;fmp\n\n&lt;timespan&gt;</code>\n<i>▪️today\n▪️yesterday\n▪️week\n▪️lastweek\n▪️season\n\ne.g. </i><code>todayfmp</code>\n____________________________________________________________________\n\n<b><i><u>📣BB Commands</u></i></b>\n\n<code>➡️bb&lt;format&gt;\n\n&lt;format&gt;</code>\n<i>▪️status = table of status numbers per group\n▪️active = table: active statuses only\n▪️inactive = table: inactive statuses only\n▪️list = list of bb fruits\n\ne.g. </i><code>bblist/G1</code>\n____________________________________________________________________\n\n<b><i><u>📣BBT Commands</u></i></b>\n\n<code>➡️&lt;BbtType&gt;&lt;Format&gt;\n\n&lt;BbtType&gt;</code>\n<i>▪️bbt = all bbt + prebbt\n▪️btm# = all bbt/btm from specified btm number\n\ne.g.</i><code> bbtstatus</code>\n____________________________________________________________________\n\n<b><i><u>📣Other Commands</u></i></b>\n\n<code>➡️&lt;0411111111&gt;</code><i> = double fish check</i>'


def reg_new_user_request(id,tname,user,pw): # ACCESS FUNCTIONS
    print(f"\n>>>reg_new_user_request: id={id}, tname={tname}, user={user}, pw={pw}")
    
    conn = odbc.connect(conn_str)

    selectquery = f"""SELECT b.Access, m.GrpName, m.Name, m.UID
    FROM BotAccess b
	LEFT JOIN MemberData m ON m.UID = b.UID
	WHERE b.UID = (SELECT UID FROM LoginData WHERE Username = '{user}' AND Password = '{pw}')"""
 
 
    ds = pd.read_sql(selectquery, conn)
    if len(ds) == 0:
        print(">>>Return")
        return 'Invalid username or password'
    
    ds.columns = ['Access','Grp','Name','UID']
    
    uid = ds.loc[0,'UID']
    name = ds.loc[0,'Name']
    grp = ds.loc[0,'Grp']
    access = ds.loc[0,'Access']
    
    insertvalidity = f"SELECT 1 FROM TelegramID WHERE UID = '{uid}' OR TelID = {id}"

    dv = pd.read_sql(insertvalidity, conn)
    if len(dv) > 0:
        print(">>>Return")
        return 'Request has already been made under these credentials or this telegram account. Please follow up with your department leader.'
    
    insertquery = f"""IF NOT EXISTS (SELECT 1 FROM TelegramID WHERE UID = '{uid}' OR TelID = {id})
                      INSERT INTO TelegramID (UID, TelID, Active) VALUES ('{uid}', {id}, 0)"""
    bjnquery = f"SELECT ApproverID FROM CodeyUserRequest WHERE CodeyUser = '{uid}'"
    
    
    db = pd.read_sql(bjnquery, conn)
 
    conn.cursor().execute(insertquery)
    conn.commit()
    conn.cursor().close()
    
    reply_message = f"Codey registration request has been received and is awaiting approval. Please follow up with your department leader."
    bjn_message = f"Telegram user [{tname}](tg://user?id={id}) has requested Codey access as:\n\nName: {name}\nGroup: {grp}\nAccess Level: {access}\n\nIf this is the correct telegram account, please reply with the following text: ```\nApprove: #{uid}#{id}#```"
    bjn_id = int(db.iloc[0,0])
    
    print(bjn_id)
    
    print(">>>Return")
    return [reply_message,bjn_message,bjn_id]



def approve_new_user_request(userUID,telID): # ACCESS FUNCTIONS
    print(f"\n>>>approve_new_user_request: userUID={userUID}, telID={telID}")

    conn = odbc.connect(conn_str)

    checkvalid = f"SELECT 1 FROM TelegramID WHERE UID = '{userUID}' AND TelID = {telID} AND Active = 0"
    dv = pd.read_sql(checkvalid, conn)
    if len(dv) == 0:
        print(">>>Return")
        return 'Could not find registration request'
    
    updatequery = f"""UPDATE TelegramID SET Active = 1 WHERE UID = '{userUID}' AND TelID = {telID}"""
 
    conn.cursor().execute(updatequery)
    conn.commit()
    conn.cursor().close()
    
    reply_message = "<i>Approved</i>"
    member_message = "<i>You may now use Codey</i>"
    member_id = telID
    
    print(">>>Return")
    return [reply_message,member_message,member_id]



def deptgroup(d): # ACCESS FUNCTIONS
    print(f"\n>>>deptgroup: d={d}")
    conn = odbc.connect(conn_str)
    group_query = f"SELECT Grp FROM GroupInfo WHERE Dept LIKE '{d}'".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    ga = pd.read_sql(group_query, conn)
    conn.cursor().close()
    grouplist = []
    for n in range(len(ga)):
        grouplist.append(ga.iloc[n,0].lower())
    print(">>>Return")
    return grouplist

def maillist(): # IT FUNCTIONS
    print(f"\n>>>maillist")
    conn = odbc.connect(conn_str)
    ga = pd.read_sql("SELECT m.Name, t.TelID FROM TelegramBotData t LEFT JOIN MemberData m ON m.UID = t.UID WHERE Access = 'Group'", conn)
    da = pd.read_sql("SELECT m.Name, t.TelID FROM TelegramBotData t LEFT JOIN MemberData m ON m.UID = t.UID WHERE Access LIKE 'D_'", conn)
    aa = pd.read_sql("SELECT m.Name, t.TelID FROM TelegramBotData t LEFT JOIN MemberData m ON m.UID = t.UID WHERE Access = 'All'", conn)
    ma = pd.read_sql("SELECT m.Name, t.TelID FROM TelegramBotData t LEFT JOIN MemberData m ON m.UID = t.UID WHERE Access = 'M&W Dept'", conn)
    ia = pd.read_sql("SELECT m.Name, t.TelID FROM TelegramBotData t LEFT JOIN MemberData m ON m.UID = t.UID WHERE Access = 'Israel'", conn)
    conn.cursor().close()
    groupid = []
    deptid = []
    allid = []
    mwid = []
    israelid = []
    groupname = []
    deptname = []
    allname = []
    mwname = []
    israelname = []  
    
    for r in range(len(ga)):
        groupid.append(int(ga.loc[r,'telid']))
    for r in range(len(da)):
        deptid.append(int(da.loc[r,'telid']))
    for r in range(len(aa)):
        allid.append(int(aa.loc[r,'telid']))
    for r in range(len(ma)):
        mwid.append(int(ma.loc[r,'telid']))
    for r in range(len(ia)):
        israelid.append(int(ia.loc[r,'telid']))
    for r in range(len(ga)):
        groupname.append(str(ga.loc[r,'name']))
    for r in range(len(da)):
        deptname.append(str(da.loc[r,'name']))
    for r in range(len(aa)):
        allname.append(str(aa.loc[r,'name']))
    for r in range(len(ma)):
        mwname.append(str(ma.loc[r,'name']))
    for r in range(len(ia)):
        israelname.append(str(ia.loc[r,'name']))
    telIDs = {'groupid': groupid,
              'deptid': deptid,
              'allid': allid,
              'mwid': mwid,
              'israelid': israelid,
              'groupname': groupname,
              'deptname': deptname,
              'allname': allname,
              'mwname': mwname,
              'israelname': israelname}
    print(">>>Return")
    return telIDs

def idlist(access,group_or_dept): # ACCESS FUNCTIONS
    print(f"\n>>>idlist: access={access}, group_or_dept={group_or_dept}")
    filter = 'MemberGroup' if access in ('Group','CUL') else 'Group_IMWY'
    conn = odbc.connect(conn_str)
    idtable = pd.read_sql(f"SELECT ID FROM MemberData WHERE {filter} = '{group_or_dept}'", conn)
    conn.cursor().close()
    idlist = []
    for r in range(len(idtable)):
        idlist.append(int(idtable.iloc[r,0]))
    print(">>>Return")
    return idlist


def functionlog(uid, name, input_text, command): # IT FUNCTIONS
    print(f"\n>>>functionlog: uid={uid}, name={name}, input_text={input_text}, command={command}")
    conn = odbc.connect(conn_str)
    input_text = input_text.replace("'","''")
    command = command.replace("'","''")
    logSQL = f"INSERT INTO CodeyFunctionLogs (UID, Name, CommandSent, FunctionName, TStamp) VALUES ('{uid}', '{name}', '{input_text}', '{command}', CONVERT(SmallDateTime, SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time'))"
    conn.cursor().execute(logSQL)
    conn.commit()
    conn.cursor().close()


def teledata(id): # ACCESS FUNCTIONS
    print(f"\n>>>teledata: id={id}")
    with odbc.connect(conn_str) as conn:
        access = f"SELECT * FROM CodeyTeleData({id})" # Refactoring: Updated new variables
        da = pd.read_sql(access, conn)
    
    if len(da) == 0:
        print(">>>Return")
        return "None/None/None/None/None/None/None/None/None/None/None/None"
    else:
        print(">>>Return")
        return f"{da.iloc[0,0]}/{da.iloc[0,1]}/{da.iloc[0,2]}/{da.iloc[0,3]}/{da.iloc[0,4]}/{da.iloc[0,5]}/{da.iloc[0,6]}/{da.iloc[0,7]}/{da.iloc[0,8]}/{da.iloc[0,9]}/{da.iloc[0,10]}/{da.iloc[0,11]}/{da.iloc[0,12]}"
    
def namedata(user_name): # ACCESS FUNCTIONS
    print(f"\n>>>namedata: user_name={user_name}")
    conn = odbc.connect(conn_str)
    access = f"SELECT * FROM CodeyNameData('{user_name}')" # Refactoring: Updated new variables
    print(access)
    da = pd.read_sql(access, conn)
    conn.cursor().close()
    
    if len(da) == 0:
        print(">>>Return")
        return "None/None/None/None/None/None/None/None/None/None"
    else:
        print(">>>Return")
        return f"{da.iloc[0,0]}/{da.iloc[0,1]}/{da.iloc[0,2]}/{da.iloc[0,3]}/{da.iloc[0,4]}/{da.iloc[0,5]}/{da.iloc[0,6]}/{da.iloc[0,7]}/{da.iloc[0,8]}/{da.iloc[0,9]}"

def groupinfo(g): # ACCESS FUNCTIONS
    print(f"\n>>>groupinfo: g={g}")
    conn = odbc.connect(conn_str)
    seasondata = f"SELECT Dept, FMP_SID, FMP_SeasonStart, BB_SID, BB_SeasonStart FROM CodeyTeleDataGroup('{g}')" # Replace the first 'All' with GROUP_IMWY to change M&W season back to M&W CT (Change also on teledata function!)
    dr = pd.read_sql(seasondata, conn)
    conn.cursor().close()

    if len(dr) == 0:
        print(">>>Return")
        return "None/None/None/None/None"
    else:
        print(">>>Return")
        return f"{dr.iloc[0,0]}/{dr.iloc[0,1]}/{dr.iloc[0,2]}/{dr.iloc[0,3]}/{dr.iloc[0,4]}"
    
    
def specifyct(ct): # ACCESS FUNCTIONS
    print(f"\n>>>specifyct: ct={ct}")
    conn = odbc.connect(conn_str)
    if ct == 'sft':
        sql = 'SELECT FMP_Online, BB_Online FROM PhysicalOnline'
    if ct == 'phys':
        sql = 'SELECT FMP_Physical, BB_Physical FROM PhysicalOnline'
    ds = pd.read_sql(sql, conn)
    if len(ds) == 0:
        print(">>>Return")
        return "None/None"
    else:
        print(">>>Return")
        return f"{ds.iloc[0,0]}/{ds.iloc[0,1]}"
    

def duplicate_check(ph): # FMP FUNCTIONS
    print(f"\n>>>duplicate_check: ph={ph}")
    conn = odbc.connect(conn_str)
    phonecheck = f"SELECT Locked FROM FruitData WHERE FishPhone = {ph} ORDER BY Locked DESC"
    print(phonecheck)
    
    dp = pd.read_sql(phonecheck, conn)
    
    conn.cursor().close()
    
    if len(dp) == 0:
        print(">>>Return")
        return 'New fish - can proceed'
    elif str(dp.iloc[0,0]) == 'Yes':
        print(">>>Return")
        return 'Duplicate - cannot proceed'
    else:
        print(">>>Return")
        return 'Fished before but proceedable'





def todayfish(g): # FMP FUNCTIONS
    print(f"\n>>>todayfish: g={g}")
    sql_fish = f"SELECT * FROM ScottTodayFish('{g}')"
    sql_pts = f"SELECT(ISNULL((SELECT SUM(F1P) FROM ScottTodayFish('{g}') WHERE F1G LIKE '{g}'),0) + ISNULL((SELECT SUM(F2P) FROM ScottTodayFish('{g}') WHERE F2G LIKE '{g}'),0)) AS Points"
    with odbc.connect(conn_str) as conn:
        dp = pd.read_sql(sql_fish, conn)
    g = g.capitalize()
    g = re.sub(r'(¹|²)g([0-9]*)',r'\1G\2',g)
    
    if len(dp) == 0:
        print(">>>Return")
        return "No fish found"
    else:  
        dp.columns = dp.columns.str.capitalize()
        dp['Timestamp'] = dp['Timestamp'].dt.strftime('%a %d/%m, %I:%M %p')
        dp.replace(np.nan, '', regex = True, inplace = True)
        
        pts_result = pd.read_sql(sql_pts, conn).iloc[0,0]
        pts = str(int(pts_result)) if pts_result is not None and not pd.isna(pts_result) else '0'

        fish = str()
        for r in range(len(dp)):
            fish = f"{fish}🐟{r+1}.{dp.iloc[r,0]} - {dp.iloc[r,1]} ({dp.iloc[r,2]}) / {dp.iloc[r,4]} ({dp.iloc[r,5]}) — [{dp.iloc[r,7]}]\n"
        fish = f"🐠<b><u>{g} Fish Today</u></b>🐡\n\n<pre>{fish.replace('/  () ','')}</pre>\\n<b>{g} Points: {pts}</b>"
        print(">>>Return")
    return fish
        


def weekfish(g): # FMP FUNCTIONS
    print(f"\n>>>weekfish: g={g}")
    sql_fish = f"SELECT * FROM ScottWeekFish('{g}')"
    sql_pts = f"SELECT(ISNULL((SELECT SUM(F1P) FROM ScottWeekFish('{g}') WHERE F1G LIKE '{g}'),0) + ISNULL((SELECT SUM(F2P) FROM ScottWeekFish('{g}') WHERE F2G LIKE '{g}'),0)) AS Points"
    with odbc.connect(conn_str) as conn:
        dp = pd.read_sql(sql_fish, conn)
    g = g.capitalize()
    g = re.sub(r'(¹|²)g([0-9]*)',r'\1G\2',g)
    
    if len(dp) == 0:
        print(">>>Return")
        return "No fish found"
    else:  
        dp.columns = dp.columns.str.capitalize()
        dp['Timestamp'] = dp['Timestamp'].dt.strftime('%a %d/%m, %I:%M %p')
        dp.replace(np.nan, '', regex = True, inplace = True)
        
        pts_result = pd.read_sql(sql_pts, conn).iloc[0,0]
        pts = str(int(pts_result)) if pts_result is not None and not pd.isna(pts_result) else '0'
        conn.cursor().close()
        
        
        
        fish = str()
        for r in range(len(dp)):
            fish = fish + '🐟' + str(r+1) + '. ' + str(dp.iloc[r,0]) + ' - ' + str(dp.iloc[r,1]) + ' (' + str(dp.iloc[r,2]) + ') / ' + str(dp.iloc[r,4]) + ' (' + str(dp.iloc[r,5]) + ') — [' + str(dp.iloc[r,7]) + ']' + '\n'
        fish = '🐠<b><u>' + str(g) + ' Fish This Week</u></b>🐡\n\n<pre>' + fish.replace('/  () ','') + '</pre>\n' + '<b>' + str(g) + ' Points: ' + pts + '</b>'
        print(">>>Return")
    return fish



def seasonpick(g): # FMP FUNCTIONS
    print(f"\n>>>seasonpick: g={g}")
    conn = odbc.connect(conn_str)
    sql_fish = f"SELECT * FROM ScottSeasonPick('{g}')"
    sql_pts = f"SELECT(ISNULL((SELECT SUM(P1P) FROM ScottSeasonPick('{g}') WHERE P1G LIKE '{g}'),0) + ISNULL((SELECT SUM(P2P) FROM ScottSeasonPick('{g}') WHERE P2G LIKE '{g}'),0)) AS Points"
    dp = pd.read_sql(sql_fish, conn)
    g = g.capitalize()
    g = re.sub(r'(¹|²)g([0-9]*)',r'\1G\2',g)
    
    if len(dp) == 0:
        print(">>>Return")
        return "No fish found"
    else:  
        dp.columns = dp.columns.str.capitalize()
        dp['Timestamp'] = dp['Timestamp'].dt.strftime('%a %d/%m')
        dp.replace(np.nan, '', regex = True, inplace = True)
        
        pts_result = pd.read_sql(sql_pts, conn).iloc[0,0]
        pts = str(int(pts_result)) if pts_result is not None and not pd.isna(pts_result) else '0'
        conn.cursor().close()

        fish = str()
        for r in range(len(dp)):
            fish = fish + '<pre>🍊' + str(r+1) + '. ' + str(dp.iloc[r,0]) + ' - ' + str(dp.iloc[r,1]) + ' (' + str(dp.iloc[r,2]) + ') / ' + str(dp.iloc[r,4]) + ' (' + str(dp.iloc[r,5]) + ') — [' + str(dp.iloc[r,7]) + ']' + '</pre>\n'
        fish = '🍎<b><u>' + str(g) + ' Pickings This Season</u></b>🍏\n\n' + fish.replace('/  () ','') + '\n' + '<b>' + str(g) + ' Points: ' + pts + '</b>'
        print(">>>Return")
    return fish



def seasonfe(g): # FMP FUNCTIONS
    print(f"\n>>>seasonfe: g={g}")
    conn = odbc.connect(conn_str)

    sql_fish = f"SELECT * FROM ScottSeasonFE('{g}')"
    sql_pts = f"SELECT(ISNULL((SELECT SUM(L1P) FROM ScottSeasonFE('{g}') WHERE L1G LIKE '{g}'),0) + ISNULL((SELECT SUM(L2P) FROM ScottSeasonFE('{g}') WHERE L2G LIKE '{g}'),0)) AS Points"
    dp = pd.read_sql(sql_fish, conn)
    g = g.capitalize()
    g = re.sub(r'(¹|²)g([0-9]*)',r'\1G\2',g)
    
    if len(dp) == 0:
        print(">>>Return")
        return "No fish found"
    else:  
        dp.columns = dp.columns.str.capitalize()
        dp['Timestamp'] = pd.to_datetime(dp['Timestamp']) # Necessary for First Edu formulas since the Timestamp (i.e. "ClassDate" column) is not actually Timestamp type objects but string objects that need to be converted before "dt." methods can be used on it
        dp['Timestamp'] = dp['Timestamp'].dt.strftime('%a %d/%m')
        dp.replace(np.nan, '', regex = True, inplace = True)
        
        pts = str(pd.read_sql(sql_pts, conn).iloc[0,0])
        conn.cursor().close()

        fish = str()
        for r in range(len(dp)):
            fish = fish + '<pre>🎓' + str(r+1) + '. ' + str(dp.iloc[r,0]) + ' - ' + str(dp.iloc[r,1]) + ' (' + str(dp.iloc[r,2]) + ') / ' + str(dp.iloc[r,4]) + ' (' + str(dp.iloc[r,5]) + ') — [' + str(dp.iloc[r,7]) + ']' + '</pre>\n'
        fish = '👩‍🎓<b><u>' + str(g) + ' First Education This Season</u></b>👨‍🎓\n\n' + fish.replace('/  () ','') + '\n' + '<b>' + str(g) + ' Points: ' + pts + '</b>'
        print(">>>Return")
    return fish


def todaympfe(g): # FMP FUNCTIONS
    print(f"\n>>>todaympfe: g={g}")
    conn = odbc.connect(conn_str)
    sql_TM = f"SELECT * FROM ScottTodayMeet('{g}')"
    sql_TM_pts = f"SELECT(ISNULL((SELECT SUM(M1P) FROM ScottTodayMeet('{g}') WHERE M1G LIKE '{g}'),0) + ISNULL((SELECT SUM(M2P) FROM ScottTodayMeet('{g}') WHERE M2G LIKE '{g}'),0)) AS Points"
    dpm = pd.read_sql(sql_TM, conn)

    sql_TP = f"SELECT * FROM ScottTodayPick('{g}')"
    sql_TP_pts = f"SELECT(ISNULL((SELECT SUM(P1P) FROM ScottTodayPick('{g}') WHERE P1G LIKE '{g}'),0) + ISNULL((SELECT SUM(P2P) FROM ScottTodayPick('{g}') WHERE P2G LIKE '{g}'),0)) AS Points"
    dpp = pd.read_sql(sql_TP, conn)

    sql_TFE = f"SELECT * FROM ScottTodayFE('{g}')"
    sql_TFE_pts = f"SELECT(ISNULL((SELECT SUM(L1P) FROM ScottTodayFE('{g}') WHERE L1G LIKE '{g}'),0) + ISNULL((SELECT SUM(L2P) FROM ScottTodayFE('{g}') WHERE L2G LIKE '{g}'),0)) AS Points"
    dpfe = pd.read_sql(sql_TFE, conn)

    conn.cursor().close()
    g = g.capitalize()
    g = re.sub(r'(¹|²)g([0-9]*)',r'\1G\2',g)
    
    if len(dpm) == 0:
        meet = 'No meetings'
    else:  
        dpm.columns = dpm.columns.str.capitalize()
        dpm['Timestamp'] = dpm['Timestamp'].dt.strftime('%a %d/%m')
        dpm.replace(np.nan, '', regex = True, inplace = True)
        mpts = str(pd.read_sql(sql_TM_pts, conn).iloc[0,0])
        meet = str()
        for r in range(len(dpm)):
            meet = meet + '<pre>🤝' + str(r+1) + '. ' + str(dpm.iloc[r,0]) + ' - ' + str(dpm.iloc[r,1]) + ' (' + str(dpm.iloc[r,2]) + ') / ' + str(dpm.iloc[r,4]) + ' (' + str(dpm.iloc[r,5]) + ') — [' + str(dpm.iloc[r,7]) + ']' + '</pre>\n'
        meet = '👥<b><u><i>' + str(g) + ' Meetings Today</i></u></b>👥\n' + meet.replace('/  () ','') + '<b><i>' + str(g) + ' Points: ' + mpts + '</i></b>'
    
    if len(dpp) == 0:
        pick = 'No pickings'
    else:  
        dpp.columns = dpp.columns.str.capitalize()
        dpp['Timestamp'] = dpp['Timestamp'].dt.strftime('%a %d/%m')
        dpp.replace(np.nan, '', regex = True, inplace = True)
        ppts = str(pd.read_sql(sql_TP_pts, conn).iloc[0,0])
        pick = str()
        for r in range(len(dpp)):
            pick = pick + '<pre>🍊' + str(r+1) + '. ' + str(dpp.iloc[r,0]) + ' - ' + str(dpp.iloc[r,1]) + ' (' + str(dpp.iloc[r,2]) + ') / ' + str(dpp.iloc[r,4]) + ' (' + str(dpp.iloc[r,5]) + ') — [' + str(dpp.iloc[r,7]) + ']' + '</pre>\n'
        pick = '🍎<b><u><i>' + str(g) + ' Pickings Today</i></u></b>🍏\n' + pick.replace('/  () ','') + '<b><i>' + str(g) + ' Points: ' + ppts + '</i></b>'
        
    if len(dpfe) == 0:
        fe =  'No first education'
    else:  
        dpfe.columns = dpfe.columns.str.capitalize()
        dpfe['Timestamp'] = pd.to_datetime(dpfe['Timestamp']) # Necessary for First Edu formulas since the Timestamp (i.e. "ClassDate" column) is not actually Timestamp type objects but string objects that need to be converted before "dt." methods can be used on it
        dpfe['Timestamp'] = dpfe['Timestamp'].dt.strftime('%a %d/%m')
        dpfe.replace(np.nan, '', regex = True, inplace = True)
        fepts = str(pd.read_sql(sql_TFE_pts, conn).iloc[0,0])
        fe = str()
        for r in range(len(dpfe)):
            fe = fe + '<pre>🎓' + str(r+1) + '. ' + str(dpfe.iloc[r,0]) + ' - ' + str(dpfe.iloc[r,1]) + ' (' + str(dpfe.iloc[r,2]) + ') / ' + str(dpfe.iloc[r,4]) + ' (' + str(dpfe.iloc[r,5]) + ') — [' + str(dpfe.iloc[r,7]) + ']' + '</pre>\n'
        fe = '👩‍🎓<b><u><i>' + str(g) + ' First Education Today</i></u></b>👨‍🎓\n' + fe.replace('/  () ','') + '<b><i>' + str(g) + ' Points: ' + fepts + '</i></b>'
    
    print(">>>Return")
    return meet + '\n\n' + pick + '\n\n' + fe


def weekmpfe(g): # FMP FUNCTIONS
    print(f"\n>>>weekmpfe: g={g}")
    conn = odbc.connect(conn_str)
    sql_TM = f"SELECT * FROM ScottWeekMeet('{g}')"
    sql_TM_pts = f"SELECT (ISNULL((SELECT SUM(M1P) FROM ScottWeekMeet('{g}') WHERE M1G LIKE '{g}'),0) + ISNULL((SELECT SUM(M2P) FROM ScottWeekMeet('{g}') WHERE M2G LIKE '{g}'),0)) AS Points"
    dpm = pd.read_sql(sql_TM, conn)

    sql_TP = f"SELECT * FROM ScottWeekPick('{g}')"
    sql_TP_pts = f"SELECT (ISNULL((SELECT SUM(P1P) FROM ScottWeekPick('{g}') WHERE P1G LIKE '{g}'),0) + ISNULL((SELECT SUM(P2P) FROM ScottWeekPick('{g}') WHERE P2G LIKE '{g}'),0)) AS Points"
    dpp = pd.read_sql(sql_TP, conn)

    sql_TFE = f"SELECT * FROM ScottWeekFE('{g}')"
    sql_TFE_pts = f"SELECT (ISNULL((SELECT SUM(L1P) FROM ScottWeekFE('{g}') WHERE L1G LIKE '{g}'),0) + ISNULL((SELECT SUM(L2P) FROM ScottWeekFE('{g}') WHERE L2G LIKE '{g}'),0)) AS Points"
    dpfe = pd.read_sql(sql_TFE, conn)

    conn.cursor().close()
    g = g.capitalize()
    g = re.sub(r'(¹|²)g([0-9]*)',r'\1G\2',g)
    
    if len(dpm) == 0:
        meet = 'No meetings'
    else:  
        dpm.columns = dpm.columns.str.capitalize()
        dpm['Timestamp'] = dpm['Timestamp'].dt.strftime('%a %d/%m')
        dpm.replace(np.nan, '', regex = True, inplace = True)
        mpts = str(pd.read_sql(sql_TM_pts, conn).iloc[0,0])
        meet = str()
        for r in range(len(dpm)):
            meet = meet + '<pre>🤝' + str(r+1) + '. ' + str(dpm.iloc[r,0]) + ' - ' + str(dpm.iloc[r,1]) + ' (' + str(dpm.iloc[r,2]) + ') / ' + str(dpm.iloc[r,4]) + ' (' + str(dpm.iloc[r,5]) + ') — [' + str(dpm.iloc[r,7]) + ']' + '</pre>\n'
        meet = '👥<b><u><i>' + str(g) + ' Meetings This Week</i></u></b>👥\n' + meet.replace('/  () ','') + '<b><i>Points: ' + mpts + '</i></b>'
    
    if len(dpp) == 0:
        pick = 'No pickings'
    else:  
        dpp.columns = dpp.columns.str.capitalize()
        dpp['Timestamp'] = dpp['Timestamp'].dt.strftime('%a %d/%m')
        dpp.replace(np.nan, '', regex = True, inplace = True)
        ppts = str(pd.read_sql(sql_TP_pts, conn).iloc[0,0])
        pick = str()
        for r in range(len(dpp)):
            pick = pick + '<pre>🍊' + str(r+1) + '. ' + str(dpp.iloc[r,0]) + ' - ' + str(dpp.iloc[r,1]) + ' (' + str(dpp.iloc[r,2]) + ') / ' + str(dpp.iloc[r,4]) + ' (' + str(dpp.iloc[r,5]) + ') — [' + str(dpp.iloc[r,7]) + ']' + '</pre>\n'
        pick = '🍎<b><u><i>' + str(g) + ' Pickings This Week</i></u></b>🍏\n' + pick.replace('/  () ','') + '<b><i>Points: ' + ppts + '</i></b>'
        
    if len(dpfe) == 0:
        fe =  'No first education'
    else:  
        dpfe.columns = dpfe.columns.str.capitalize()
        dpfe['Timestamp'] = pd.to_datetime(dpfe['Timestamp']) # Necessary for First Edu formulas since the Timestamp (i.e. "ClassDate" column) is not actually Timestamp type objects but string objects that need to be converted before "dt." methods can be used on it
        dpfe['Timestamp'] = dpfe['Timestamp'].dt.strftime('%a %d/%m')
        dpfe.replace(np.nan, '', regex = True, inplace = True)
        fepts = str(pd.read_sql(sql_TFE_pts, conn).iloc[0,0])
        fe = str()
        for r in range(len(dpfe)):
            fe = fe + '<pre>🎓' + str(r+1) + '. ' + str(dpfe.iloc[r,0]) + ' - ' + str(dpfe.iloc[r,1]) + ' (' + str(dpfe.iloc[r,2]) + ') / ' + str(dpfe.iloc[r,4]) + ' (' + str(dpfe.iloc[r,5]) + ') — [' + str(dpfe.iloc[r,7]) + ']' + '</pre>\n'
        fe = '👩‍🎓<b><u><i>' + str(g) + ' First Education This Week</i></u></b>👨‍🎓\n' + fe.replace('/  () ','') + '<b><i>Points: ' + fepts + '</i></b>'
    
    print(">>>Return")
    return meet + '\n\n' + pick + '\n\n' + fe


# UNIVERSAL MEMBER FMP FUNCTION

def memberfmp(timerange,g,sid,ss,access): # FMP FUNCTIONS
    print(f"\n>>>memberfmp: timerange={timerange}, group={g}, sid={sid}, seasonstart={ss}, access={access}")
    
    name = 'Member' if access == 'IT' else 'MemberCode'
  
    timevalues = {'today':     ['SELECT dbo.today()', 'SELECT dbo.tomorrow()', 'Today'],
                  'yesterday': ['SELECT dbo.yesterday()', 'SELECT dbo.today()', 'Yesterday'],
                  'week':      ['SELECT dbo.weekstart()', 'SELECT dbo.nextweekstart()', 'This Week'],
                  'lastweek':  ['SELECT dbo.lastweekstart()', 'SELECT dbo.weekstart()', 'Last Week'],
                  'season':    [f"'{ss}'", 'SELECT dbo.tomorrow()', 'EV Season'],
                  'lastseason':    [f"'{ss}'", 'SELECT dbo.tomorrow()', 'EV Season']}
   
    s,e,title = timevalues[timerange]
        
    memberQ = f"""SELECT {name}, F, M, PP, P, FE FROM CodeyFMPPP('{sid}', ({s}), ({e})) WHERE Grp LIKE '{g}'
                  ORDER BY CASE
                  WHEN Title = 'GYJN' THEN 1
                  WHEN Task = 'OEV' AND Title = 'TJN' THEN 2
                  WHEN Task = 'IEV' AND Title = 'TJN' THEN 3
                  WHEN Task = 'EDU' AND Title = 'TJN' THEN 4
                  WHEN Task = 'SV' AND Title = 'TJN' THEN 5
                  WHEN Title = 'GGN' THEN 6
                  ELSE 7
                  END, MemberCode"""
    
    totalQ  = f"SELECT SUM(F)F, SUM(M)M, SUM(PP)PP, SUM(P)P, SUM(FE)FE FROM CodeyFMPPP('{sid}', ({s}), ({e})) WHERE Grp LIKE '{g}'"
    print(memberQ)
    
    with odbc.connect(conn_str) as conn:
        dm = pd.read_sql(memberQ, conn)
        dt = pd.read_sql(totalQ, conn)

    dm.columns = ['Member','F','M','PP','P','FE']
    dt.columns = ['F','M','PP','P','FE']
    g = g.capitalize()
    g = re.sub(r'(¹|²)g([0-9]*)',r'\1G\2',g)
    if len(dm) == 0:
        print(">>>Return")
        return "No members found"
    else:  
        member = str()
        
        for r in range(len(dm)):
            mem = str(dm.loc[r,'Member'])[:8] + ' '*(8-len(str(dm.loc[r,'Member'])[:8]))
            f      = ' '*(4-len(str(dm.loc[r,'F'])))  + str(dm.loc[r,'F'])
            m      = ' '*(4-len(str(dm.loc[r,'M'])))  + str(dm.loc[r,'M'])
            pp     = ' '*(3-len(str(dm.loc[r,'PP']))) + str(dm.loc[r,'PP'])
            p      = ' '*(3-len(str(dm.loc[r,'P'])))  + str(dm.loc[r,'P'])
            fe     = ' '*(3-len(str(dm.loc[r,'FE']))) + str(dm.loc[r,'FE'])
            
            member = f'{member}{mem}[{f}|{m}|{pp}|{p}|{fe}]\n'
            
        f      = ' '*(4-len(str(dt.loc[0,'F'])))  + str(dt.loc[0,'F'])
        m      = ' '*(4-len(str(dt.loc[0,'M'])))  + str(dt.loc[0,'M'])
        pp     = ' '*(3-len(str(dt.loc[0,'PP']))) + str(dt.loc[0,'PP'])
        p      = ' '*(3-len(str(dt.loc[0,'P'])))  + str(dt.loc[0,'P'])
        fe     = ' '*(3-len(str(dt.loc[0,'FE']))) + str(dt.loc[0,'FE'])
        
        total = f'Total   [{f}|{m}|{pp}|{p}|{fe}]'
        
        member = f'<b><u>{g} FMP : {title}</u></b>\n\n<pre>Member  [ F  | M  |PP |P  |FE ]\n\n{member}\n{total}</pre>'
        member = re.sub(r'\.0',r'  ',member) # Replaces '.0' with empty space
        member = re.sub(r'(\D)0([^.])',r'\1-\2',member)   # Replaces lone '0' with '-'
        print(">>>Return")
    return member
    

# UNIVERSAL DEPT FMP FUNCTION:

def deptfmp(task,timerange,d,sid,ss,access): # FMP FUNCTIONS
    print(f"\n>>>deptfmp: task={task}, timerange={timerange}, dept={d}, sid={sid}, seasonstart={ss}, access={access}")
    
    displayGroups = False if task == 'dept' and access in ('All','IT','EDU') else True
    topleft = 'Grp ' if displayGroups == True else 'Dept'
       
    taskvalues = {'church' : [''       , ''            ],
                  'dept'   : [''       , ''            ],
                  'youth'  : [''       , ''            ],
                  'mw'     : [''       , ''            ],
                  'tgw'    : [' TGW'   , " AND Title IN ('TJN','GYJN')"],
                  'member' : [' Member', " AND (Title IS NULL OR Title NOT IN ('TJN','GYJN'))"]}
    tasktitle = taskvalues[task][0]
    taskQ = taskvalues[task][1]
  
    if timerange in {'today','yesterday'}:
        spc = [6,5,4,4,4,4,f'{topleft}  [  F  | M  |PP  | P  |FE  ]',   'Total ']
    if timerange in {'week','lastweek'}:
        spc = [5,5,5,4,4,4,f'{topleft} [  F  |  M  |PP  | P  |FE  ]',   'Total']
    if timerange == 'season':
        spc = [4,6,6,5,5,5,f'{topleft}[   F  |   M  | PP  |  P  | FE  ]','Tot ']

    timevalues = {'today':     ['SELECT dbo.today()', 'SELECT dbo.tomorrow()', 'Today'],
                  'yesterday': ['SELECT dbo.yesterday()', 'SELECT dbo.today()', 'Yesterday'],
                  'week':      ['SELECT dbo.weekstart()', 'SELECT dbo.nextweekstart()', 'This Week'],
                  'lastweek':  ['SELECT dbo.lastweekstart()', 'SELECT dbo.weekstart()', 'Last Week'],
                  'season':    [f"'{ss}'", 'SELECT dbo.tomorrow()', 'EV Season']}
    
    s,e,timetitle = timevalues[timerange]
       
    memberQ = f"SELECT Grp, SUM(F)F, SUM(M)M, SUM(PP)PP, SUM(P)P, SUM(FE)FE FROM CodeyFMPPP('{sid}', ({s}), ({e})) WHERE Dept LIKE '{d}'{taskQ} GROUP BY Grp, GID ORDER BY GID".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'MW[0-9]%'","Grp LIKE 'MW[0-9]%'")
    deptQ   = f"SELECT Dept, SUM(F)F, SUM(M)M, SUM(PP)PP, SUM(P)P, SUM(FE)FE FROM CodeyFMPPP('{sid}', ({s}), ({e})) WHERE Dept LIKE '{d}'{taskQ} GROUP BY Dept, DID ORDER BY DID".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'MW[0-9]%'","Grp LIKE 'MW[0-9]%'")
    # regionQ = f"SELECT District, SUM(F)F, SUM(M)M, SUM(PP)PP, SUM(P)P, SUM(FE)FE FROM CodeyFMPPP('{sid}', ({s}), ({e})) WHERE Dept LIKE '{d}'{taskQ} GROUP BY District ORDER BY District".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'MW[0-9]%'","Grp LIKE 'MW[0-9]%'")  
    totalQ  = f"SELECT SUM(F)F, SUM(M)M, SUM(PP)PP, SUM(P)P, SUM(FE)FE FROM CodeyFMPPP('{sid}', ({s}), ({e})) WHERE Dept LIKE '{d}'{taskQ}".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'MW[0-9]%'","Grp LIKE 'MW[0-9]%'")
    print(memberQ)

    with odbc.connect(conn_str) as conn:
        dm = pd.read_sql(memberQ, conn)
        dd = pd.read_sql(deptQ, conn)
        # dr = pd.read_sql(regionQ, conn)
        dt = pd.read_sql(totalQ, conn)

    dm.columns = ['Grp','F','M','PP','P','FE']
    dd.columns = ['Dept','F','M','PP','P','FE']
    # dr.columns = ['Region','F','M','PP','P','FE']
    dt.columns = ['F','M','PP','P','FE']
    dd.replace(r' Dept',r'', regex = True, inplace = True)
    
    group = str()
    
    if displayGroups:
        for r in range(len(dm)):
            grp = str(dm.loc[r,'Grp'])[:spc[0]] + ' '*(spc[0]-len(str(dm.loc[r,'Grp'])[:spc[0]]))
            f  = ' '*(spc[1]-len(str(dm.loc[r,'F'])))  + str(dm.loc[r,'F'])
            m  = ' '*(spc[2]-len(str(dm.loc[r,'M'])))  + str(dm.loc[r,'M'])
            pp = ' '*(spc[3]-len(str(dm.loc[r,'PP']))) + str(dm.loc[r,'PP'])
            p  = ' '*(spc[4]-len(str(dm.loc[r,'P'])))  + str(dm.loc[r,'P'])
            fe = ' '*(spc[5]-len(str(dm.loc[r,'FE']))) + str(dm.loc[r,'FE'])
            group = f'{group}{grp}[{f}|{m}|{pp}|{p}|{fe}]\n'
        group = group + '\n'

    dept = str()    
    for r in range(len(dd)):
        dpt = str(dd.loc[r,'Dept'][:spc[0]]) + ' '*(spc[0]-len(str(dd.loc[r,'Dept'][:spc[0]])))
        f  = ' '*(spc[1]-len(str(dd.loc[r,'F'])))  + str(dd.loc[r,'F'])
        m  = ' '*(spc[2]-len(str(dd.loc[r,'M'])))  + str(dd.loc[r,'M'])
        pp = ' '*(spc[3]-len(str(dd.loc[r,'PP']))) + str(dd.loc[r,'PP'])
        p  = ' '*(spc[4]-len(str(dd.loc[r,'P'])))  + str(dd.loc[r,'P'])
        fe = ' '*(spc[5]-len(str(dd.loc[r,'FE']))) + str(dd.loc[r,'FE'])
        dept = f'{dept}{dpt}[{f}|{m}|{pp}|{p}|{fe}]\n'
    dept = dept + '\n'
    
    # region = str()
    # if d.endswith('D[0-9]%'):    
    #     for r in range(len(dr)):
    #         reg = str(dr.loc[r,'Region']) + ' '*(spc[0]-len(str(dr.loc[r,'Region'])))
    #         f  = ' '*(spc[1]-len(str(dr.loc[r,'F'])))  + str(dr.loc[r,'F'])
    #         m  = ' '*(spc[2]-len(str(dr.loc[r,'M'])))  + str(dr.loc[r,'M'])
    #         p  = ' '*(spc[3]-len(str(dr.loc[r,'P'])))  + str(dr.loc[r,'P'])
    #         fe = ' '*(spc[4]-len(str(dr.loc[r,'FE']))) + str(dr.loc[r,'FE'])
    #         region = f'{region}{reg}[{f}|{m}|{p}|{fe}]\n'
    #     region = region + '\n'

    if d in ('D[0-9]%','%'):
        f  = ' '*(spc[1]-len(str(dt.loc[0,'F'])))  + str(dt.loc[0,'F'])
        m  = ' '*(spc[2]-len(str(dt.loc[0,'M'])))  + str(dt.loc[0,'M'])
        pp = ' '*(spc[3]-len(str(dt.loc[0,'PP']))) + str(dt.loc[0,'PP'])
        p  = ' '*(spc[4]-len(str(dt.loc[0,'P'])))  + str(dt.loc[0,'P'])
        fe = ' '*(spc[5]-len(str(dt.loc[0,'FE']))) + str(dt.loc[0,'FE'])
        total = f'{spc[7]}[{f}|{m}|{pp}|{p}|{fe}]\n'
    else:
        total = str()
        
    depttitle = d.replace('D[0-9]%','Youth').replace('MW[0-9]%','MW').replace('24', '24 Dept').replace('%', 'Church')

    fmp = f"<b><u>{depttitle}{tasktitle} FMP : {timetitle}</u></b>\n\n<pre>{spc[6]}\n\n{group}{dept}{total}</pre>"
    fmp = re.sub(r'\.0',r'  ',fmp) # Replaces '.0' with empty space
    fmp = re.sub(r'(\D)0([^.])',r'\1-\2',fmp)   # Replaces lone '0' with '-'
    print(">>>Return")
    return fmp



def taskfmp(task,timerange,d,sid,ss,access): # FMP FUNCTIONS
    print(f"\n>>>taskfmp: task={task}, timerange={timerange}, dept={d}, sid={sid}, seasonstart={ss}, access={access}")
    
    name = 'MemberFull' if access == 'IT' else 'MemberInitial'
        
    taskvalues = {'gyjn': [' GYJN'   , " AND Title = 'GYJN'"],
                  'oev' : [' OEV TJN', " AND Task = 'OEV'"],
                  'iev' : [' IEV TJN', " AND Task = 'IEV'"],
                  'edu' : [' EDU TJN', " AND Task = 'EDU'"],
                  'sv'  : [' SV TJN' , " AND Task = 'SV'"]}
    tasktitle = taskvalues[task][0]
    taskquery = taskvalues[task][1]
    
    if access == 'IT':
        if timerange in {'today','yesterday'}:
            spc = [10,4,4,4,4,4,'TGW       [ F  | M  |PP  | P  |FE  ]','Total     ']
        elif timerange in {'week','lastweek'}:
            spc = [9,5,4,4,4,4,'TGW      [  F  | M  |PP  | P  |FE  ]','Total    ']
        elif timerange == 'season':
            spc = [8,5,5,4,4,4,'TGW     [  F  |  M  |PP  | P  |FE  ]','Total   ']
    else:
        if timerange in {'today','yesterday'}:
            spc = [7,4,4,4,4,4,'TGW    [ F  | M  |PP  | P  |FE  ]',  'Total  ']
        elif timerange in {'week','lastweek'}:
            spc = [7,5,4,4,4,4,'TGW    [  F  | M  |PP  | P  |FE  ]', 'Total  ']
        elif timerange == 'season':
            spc = [7,5,5,4,4,4,'TGW    [  F  |  M  |PP  | P  |FE  ]','Total  ']

    timevalues = {'today':     ['SELECT dbo.today()', 'SELECT dbo.tomorrow()', 'Today'],
                  'yesterday': ['SELECT dbo.yesterday()', 'SELECT dbo.today()', 'Yesterday'],
                  'week':      ['SELECT dbo.weekstart()', 'SELECT dbo.nextweekstart()', 'This Week'],
                  'lastweek':  ['SELECT dbo.lastweekstart()', 'SELECT dbo.weekstart()', 'Last Week'],
                  'season':    [f"'{ss}'", 'SELECT dbo.tomorrow()', 'EV Season']}
    
    s,e,timetitle = timevalues[timerange]
       
    baseQ   = f"{name}, F, M, PP, P, FE FROM CodeyFMPPP('{sid}', ({s}), ({e})) s WHERE Dept LIKE '{d}'{taskquery}".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    memberQ = f"SELECT Grp, {baseQ} ORDER BY GID"
    deptQ   = f"SELECT Dept, SUM(F)F, SUM(M)M, SUM(PP)PP, SUM(P)P, SUM(FE)FE FROM (SELECT Dept, DID, {baseQ})b GROUP BY Dept, DID ORDER BY DID"
    # regionQ = f"SELECT District, SUM(F)F, SUM(M)M, SUM(PP)PP, SUM(P)P, SUM(FE)FE FROM (SELECT District, {baseQ})b GROUP BY District ORDER BY District" 
    totalQ  = f"SELECT SUM(F)F, SUM(M)M, SUM(PP)PP, SUM(P)P, SUM(FE)FE FROM CodeyFMPPP('{sid}', ({s}), ({e})) s WHERE Dept LIKE '{d}'{taskquery}".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    print(deptQ)
    
    with odbc.connect(conn_str) as conn:
        dm = pd.read_sql(memberQ, conn)
        dd = pd.read_sql(deptQ, conn)
        # dr = pd.read_sql(regionQ, conn)
        dt = pd.read_sql(totalQ, conn)
    
    dm.columns = ['Grp','Member','F','M','PP','P','FE']
    dd.columns = ['Dept','F','M','PP','P','FE']
    # dr.columns = ['Region','F','M','PP','P','FE']
    dt.columns = ['F','M','PP','P','FE']
    dd.replace(r' Dept',r'', regex = True, inplace = True)

    group = str()
    for r in range(len(dm)):
        mem = f"{dm.loc[r,'Member'][:spc[0]]}{' '*(spc[0]-len(dm.loc[r,'Member'][:spc[0]]))}"
        f  = ' '*(spc[1]-len(str(dm.loc[r,'F'])))  + str(dm.loc[r,'F'])
        m  = ' '*(spc[2]-len(str(dm.loc[r,'M'])))  + str(dm.loc[r,'M'])
        pp = ' '*(spc[3]-len(str(dm.loc[r,'PP']))) + str(dm.loc[r,'PP'])
        p  = ' '*(spc[4]-len(str(dm.loc[r,'P'])))  + str(dm.loc[r,'P'])
        fe = ' '*(spc[5]-len(str(dm.loc[r,'FE']))) + str(dm.loc[r,'FE'])
        group = f'{group}{mem}[{f}|{m}|{pp}|{p}|{fe}]\n'
    group = group + '\n'

    dept = str()    
    for r in range(len(dd)):
        dpt = str(dd.loc[r,'Dept'][:spc[0]]) + ' '*(spc[0]-len(str(dd.loc[r,'Dept'][:spc[0]])))
        f  = ' '*(spc[1]-len(str(dd.loc[r,'F'])))  + str(dd.loc[r,'F'])
        m  = ' '*(spc[2]-len(str(dd.loc[r,'M'])))  + str(dd.loc[r,'M'])
        pp = ' '*(spc[3]-len(str(dd.loc[r,'PP']))) + str(dd.loc[r,'PP'])
        p  = ' '*(spc[4]-len(str(dd.loc[r,'P'])))  + str(dd.loc[r,'P'])
        fe = ' '*(spc[5]-len(str(dd.loc[r,'FE']))) + str(dd.loc[r,'FE'])
        dept = f'{dept}{dpt}[{f}|{m}|{pp}|{p}|{fe}]\n'
    dept = dept + '\n'

    # region = str()
    # if d.endswith('D[0-9]%'):    
    #     for r in range(len(dr)):
    #         reg = str(dr.loc[r,'Region']) + ' '*(spc[0]-len(str(dr.loc[r,'Region'])))
    #         f  = ' '*(spc[1]-len(str(dr.loc[r,'F'])))  + str(dr.loc[r,'F'])
    #         m  = ' '*(spc[2]-len(str(dr.loc[r,'M'])))  + str(dr.loc[r,'M'])
    #         pp = ' '*(spc[3]-len(str(dr.loc[r,'PP']))) + str(dr.loc[r,'PP'])
    #         p  = ' '*(spc[4]-len(str(dr.loc[r,'P'])))  + str(dr.loc[r,'P'])
    #         fe = ' '*(spc[5]-len(str(dr.loc[r,'FE']))) + str(dr.loc[r,'FE'])
    #         region = f'{region}{reg}[{f}|{m}|{pp}|{p}|{fe}]\n'
    #     region = region + '\n'
    
    total = str()
    if d in ('D[0-9]%','%'):
        f  = ' '*(spc[1]-len(str(dt.loc[0,'F'])))  + str(dt.loc[0,'F'])
        m  = ' '*(spc[2]-len(str(dt.loc[0,'M'])))  + str(dt.loc[0,'M'])
        pp = ' '*(spc[3]-len(str(dt.loc[0,'PP']))) + str(dt.loc[0,'PP'])
        p  = ' '*(spc[4]-len(str(dt.loc[0,'P'])))  + str(dt.loc[0,'P'])
        fe = ' '*(spc[5]-len(str(dt.loc[0,'FE']))) + str(dt.loc[0,'FE'])
        total = f'{spc[7]}[{f}|{m}|{pp}|{p}|{fe}]\n'
        
    depttitle = d.replace('D[0-9]%','Youth').replace('Mw[0-9]%','MW').replace('24', '24 Dept').replace('%', 'Church')

    fmp = f"<b><u>{depttitle}{tasktitle} FMP : {timetitle}</u></b>\n\n<pre>{spc[6]}\n\n{group}{dept}{total}</pre>"
    fmp = re.sub(r'\.0',r'  ',fmp) # Replaces '.0' with empty space
    fmp = re.sub(r'(\D)0([^.])',r'\1-\2',fmp)   # Replaces lone '0' with '-'
    print(">>>Return")
    return fmp



def youthmxpx(d): # FMP FUNCTIONS
    print(f"\n>>>youthmxpx: dept={d}")
    conn = odbc.connect(conn_str)
    exp_group = f"SELECT Grp, SUM(Mx)Mx, SUM(Px)Px FROM ScottFutureMxPx WHERE DEPT LIKE '{d}' GROUP BY Grp ORDER BY LEN(Grp),Grp".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    exp_dept = f"SELECT Dept, SUM(Mx)Mx, SUM(Px)Px FROM ScottFutureMxPx WHERE DEPT LIKE '{d}' GROUP BY Dept".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    exp_youth = f"SELECT SUM(Mx)Mx, SUM(Px)Px FROM ScottFutureMxPx WHERE DEPT LIKE '{d}'".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    
    dg = pd.read_sql(exp_group, conn)
    dd = pd.read_sql(exp_dept, conn)
    dy = pd.read_sql(exp_youth, conn)
    
    dg.columns = ['Grp','Mx','Px']
    dd.columns = ['Dept','Mx','Px']
    dy.columns = ['Mx','Px']
    dd.replace(r' Dept',r'', regex = True, inplace = True)

    conn.cursor().close()

    group = str()
    for r in range(len(dg)):
        grp = str(dg.loc[r,'Grp']) + '.'*(6-len(str(dg.loc[r,'Grp'])))
        mx = ' '*(4-len(str(dg.loc[r,'Mx']))) + str(dg.loc[r,'Mx'])
        px = ' '*(4-len(str(dg.loc[r,'Px']))) + str(dg.loc[r,'Px'])
        group = f'{group}{grp}[{mx}|{px}]\n'
    
    dept = str()    
    for r in range(len(dd)):
        dpt = str(dd.loc[r,'Dept']) + '.'*(6-len(str(dd.loc[r,'Dept'])))
        mx = ' '*(4-len(str(dd.loc[r,'Mx']))) + str(dd.loc[r,'Mx'])
        px = ' '*(4-len(str(dd.loc[r,'Px']))) + str(dd.loc[r,'Px'])
        dept = f'{dept}{dpt}[{mx}|{px}]\n'
    
    if d.endswith('D[0-9]%'):
        spc = ' '*(4-len(str(dy.iloc[0,0])))
        mx = ' '*(4-len(str(dy.loc[0,'Mx']))) + str(dy.loc[0,'Mx'])
        px = ' '*(4-len(str(dy.loc[0,'Px']))) + str(dy.loc[0,'Px'])
        youth = f'\nTotal{spc}[{mx}|{px}]'
    else:
        youth = str()
        
    result = f'<b><u>Meeting and Picking Expectants: </u></b>\n\n<pre>Grp   [MM.X|PP.X]\n\n{group}\n{dept}{youth}</pre>'
    result = re.sub(r'\.0',r'  ',result) # Replaces '.0' with empty space
    result = re.sub(r'(\D)0([^.])',r'\1-\2',result)   # Replaces lone '0' with '-'
    print(">>>Return")
    return result


    
    
def mxlist(g): # FMP FUNCTIONS
    print(f"\n>>>mxlist: g={g}")
    conn = odbc.connect(conn_str)
    dd1 = pd.read_sql(f"SELECT * FROM ScottFutureMxList WHERE ExpMeet >= DATEADD(DAY,0,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND ExpMeet < DATEADD(DAY,1,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND (L1G LIKE '{g}' OR L2G LIKE '{g}')", conn)
    dd2 = pd.read_sql(f"SELECT * FROM ScottFutureMxList WHERE ExpMeet >= DATEADD(DAY,1,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND ExpMeet < DATEADD(DAY,2,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND (L1G LIKE '{g}' OR L2G LIKE '{g}')", conn)
    dd3 = pd.read_sql(f"SELECT * FROM ScottFutureMxList WHERE ExpMeet >= DATEADD(DAY,2,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND ExpMeet < DATEADD(DAY,3,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND (L1G LIKE '{g}' OR L2G LIKE '{g}')", conn)
    dd4 = pd.read_sql(f"SELECT * FROM ScottFutureMxList WHERE ExpMeet >= DATEADD(DAY,3,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND ExpMeet < DATEADD(DAY,4,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND (L1G LIKE '{g}' OR L2G LIKE '{g}')", conn)
    dd5 = pd.read_sql(f"SELECT * FROM ScottFutureMxList WHERE ExpMeet >= DATEADD(DAY,4,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND ExpMeet < DATEADD(DAY,5,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND (L1G LIKE '{g}' OR L2G LIKE '{g}')", conn)
    dd6 = pd.read_sql(f"SELECT * FROM ScottFutureMxList WHERE ExpMeet >= DATEADD(DAY,5,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND ExpMeet < DATEADD(DAY,6,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND (L1G LIKE '{g}' OR L2G LIKE '{g}')", conn)
    dd7 = pd.read_sql(f"SELECT * FROM ScottFutureMxList WHERE ExpMeet >= DATEADD(DAY,6,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND ExpMeet < DATEADD(DAY,7,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND (L1G LIKE '{g}' OR L2G LIKE '{g}')", conn)
    conn.cursor().close()
    
    if len(dd1) == 0:
        mx1 = ''
    else:
        mx1 = '\n<b><u><i>🗓' + str(dd1.loc[0,'dow']).capitalize() + '🗓</i></u></b>\n'
        for r in range(len(dd1)):
            fish = f'🤝{r+1}. ' + dd1.loc[r,'fish']
            l1 = ' - ' + dd1.loc[r,'l1']
            l1g = ' (' + dd1.loc[r,'l1g'] + ')'
            l2 = ' / ' + dd1.loc[r,'l2'] if dd1.loc[r,'l2'] != '' else ''
            l2g = ' (' + dd1.loc[r,'l2g'] + ')' if dd1.loc[r,'l2g'] != '' else ''
            mx1 = mx1 + f'<pre>{fish}{l1}{l1g}{l2}{l2g}</pre>\n'
    if len(dd2) == 0:
        mx2 = ''
    else:
        mx2 = '\n<b><u><i>🗓' + str(dd2.loc[0,'dow']).capitalize() + '🗓</i></u></b>\n'
        for r in range(len(dd2)):
            fish = f'🤝{r+1}. ' + dd2.loc[r,'fish']
            l1 = ' - ' + dd2.loc[r,'l1']
            l1g = ' (' + dd2.loc[r,'l1g'] + ')'
            l2 = ' / ' + dd2.loc[r,'l2'] if dd2.loc[r,'l2'] != '' else ''
            l2g = ' (' + dd2.loc[r,'l2g'] + ')' if dd2.loc[r,'l2g'] != '' else ''
            mx2 = mx2 + f'<pre>{fish}{l1}{l1g}{l2}{l2g}</pre>\n'
    if len(dd3) == 0:
        mx3 = ''
    else:
        mx3 = '\n<b><u><i>🗓' + str(dd3.loc[0,'dow']).capitalize() + '🗓</i></u></b>\n'
        for r in range(len(dd3)):
            fish = f'🤝{r+1}. ' + dd3.loc[r,'fish']
            l1 = ' - ' + dd3.loc[r,'l1']
            l1g = ' (' + dd3.loc[r,'l1g'] + ')'
            l2 = ' / ' + dd3.loc[r,'l2'] if dd3.loc[r,'l2'] != '' else ''
            l2g = ' (' + dd3.loc[r,'l2g'] + ')' if dd3.loc[r,'l2g'] != '' else ''
            mx3 = mx3 + f'<pre>{fish}{l1}{l1g}{l2}{l2g}</pre>\n'
    if len(dd4) == 0:
        mx4 = ''
    else:
        mx4 = '\n<b><u><i>🗓' + str(dd4.loc[0,'dow']).capitalize() + '🗓</i></u></b>\n'
        for r in range(len(dd4)):
            fish = f'🤝{r+1}. ' + dd4.loc[r,'fish']
            l1 = ' - ' + dd4.loc[r,'l1']
            l1g = ' (' + dd4.loc[r,'l1g'] + ')'
            l2 = ' / ' + dd4.loc[r,'l2'] if dd4.loc[r,'l2'] != '' else ''
            l2g = ' (' + dd4.loc[r,'l2g'] + ')' if dd4.loc[r,'l2g'] != '' else ''
            mx4 = mx4 + f'<pre>{fish}{l1}{l1g}{l2}{l2g}</pre>\n'
    if len(dd5) == 0:
        mx5 = ''
    else:
        mx5 = '\n<b><u><i>🗓' + str(dd5.loc[0,'dow']).capitalize() + '🗓</i></u></b>\n'
        for r in range(len(dd5)):
            fish = f'🤝{r+1}. ' + dd5.loc[r,'fish']
            l1 = ' - ' + dd5.loc[r,'l1']
            l1g = ' (' + dd5.loc[r,'l1g'] + ')'
            l2 = ' / ' + dd5.loc[r,'l2'] if dd5.loc[r,'l2'] != '' else ''
            l2g = ' (' + dd5.loc[r,'l2g'] + ')' if dd5.loc[r,'l2g'] != '' else ''
            mx5 = mx5 + f'<pre>{fish}{l1}{l1g}{l2}{l2g}</pre>\n'
    if len(dd6) == 0:
        mx6 = ''
    else:
        mx6 = '\n<b><u><i>🗓' + str(dd6.loc[0,'dow']).capitalize() + '🗓</i></u></b>\n'
        for r in range(len(dd6)):
            fish = f'🤝{r+1}. ' + dd6.loc[r,'fish']
            l1 = ' - ' + dd6.loc[r,'l1']
            l1g = ' (' + dd6.loc[r,'l1g'] + ')'
            l2 = ' / ' + dd6.loc[r,'l2'] if dd6.loc[r,'l2'] != '' else ''
            l2g = ' (' + dd6.loc[r,'l2g'] + ')' if dd6.loc[r,'l2g'] != '' else ''
            mx6 = mx6 + f'<pre>{fish}{l1}{l1g}{l2}{l2g}</pre>\n'
    if len(dd7) == 0:
        mx7 = ''
    else:
        mx7 = '\n<b><u><i>🗓' + str(dd7.loc[0,'dow']).capitalize() + '🗓</i></u></b>\n'
        for r in range(len(dd7)):
            fish = f'🤝{r+1}. ' + dd7.loc[r,'fish']
            l1 = ' - ' + dd7.loc[r,'l1']
            l1g = ' (' + dd7.loc[r,'l1g'] + ')'
            l2 = ' / ' + dd7.loc[r,'l2'] if dd7.loc[r,'l2'] != '' else ''
            l2g = ' (' + dd7.loc[r,'l2g'] + ')' if dd7.loc[r,'l2g'] != '' else ''
            mx1 = mx1 + f'<pre>{fish}{l1}{l1g}{l2}{l2g}</pre>\n'
    print(">>>Return")
    return f'<i><b><u>👥Meeting Expectants👥</u></b>\n. . . . Next seven days . . . .</i>\n{mx1}{mx2}{mx3}{mx4}{mx5}{mx6}{mx7}'  if len(f'{mx1}{mx2}{mx3}{mx4}{mx5}{mx6}{mx7}') != 0 else '<i>No meeting expectants in next 7 days</i>'







def pxlist(g): # FMP FUNCTIONS
    print(f"\n>>>pxlist: g={g}")
    conn = odbc.connect(conn_str)
    dd1 = pd.read_sql(f"SELECT * FROM ScottFuturePxList WHERE ExpPick >= DATEADD(DAY,0,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND ExpPick < DATEADD(DAY,1,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND (L1G LIKE '{g}' OR L2G LIKE '{g}')", conn)
    dd2 = pd.read_sql(f"SELECT * FROM ScottFuturePxList WHERE ExpPick >= DATEADD(DAY,1,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND ExpPick < DATEADD(DAY,2,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND (L1G LIKE '{g}' OR L2G LIKE '{g}')", conn)
    dd3 = pd.read_sql(f"SELECT * FROM ScottFuturePxList WHERE ExpPick >= DATEADD(DAY,2,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND ExpPick < DATEADD(DAY,3,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND (L1G LIKE '{g}' OR L2G LIKE '{g}')", conn)
    dd4 = pd.read_sql(f"SELECT * FROM ScottFuturePxList WHERE ExpPick >= DATEADD(DAY,3,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND ExpPick < DATEADD(DAY,4,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND (L1G LIKE '{g}' OR L2G LIKE '{g}')", conn)
    dd5 = pd.read_sql(f"SELECT * FROM ScottFuturePxList WHERE ExpPick >= DATEADD(DAY,4,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND ExpPick < DATEADD(DAY,5,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND (L1G LIKE '{g}' OR L2G LIKE '{g}')", conn)
    dd6 = pd.read_sql(f"SELECT * FROM ScottFuturePxList WHERE ExpPick >= DATEADD(DAY,5,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND ExpPick < DATEADD(DAY,6,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND (L1G LIKE '{g}' OR L2G LIKE '{g}')", conn)
    dd7 = pd.read_sql(f"SELECT * FROM ScottFuturePxList WHERE ExpPick >= DATEADD(DAY,6,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND ExpPick < DATEADD(DAY,7,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND (L1G LIKE '{g}' OR L2G LIKE '{g}')", conn)
    conn.cursor().close()
    
    if len(dd1) == 0:
        px1 = ''
    else:
        px1 = '\n<b><u><i>🗓' + str(dd1.loc[0,'dow']).capitalize() + '🗓</i></u></b>\n'
        for r in range(len(dd1)):
            fish = f'🙏{r+1}. ' + dd1.loc[r,'fish']
            l1 = ' - ' + dd1.loc[r,'l1']
            l1g = ' (' + dd1.loc[r,'l1g'] + ')'
            l2 = ' / ' + dd1.loc[r,'l2'] if dd1.loc[r,'l2'] != '' else ''
            l2g = ' (' + dd1.loc[r,'l2g'] + ')' if dd1.loc[r,'l2g'] != '' else ''
            px1 = px1 + f'<pre>{fish}{l1}{l1g}{l2}{l2g}</pre>\n'
    if len(dd2) == 0:
        px2 = ''
    else:
        px2 = '\n<b><u><i>🗓' + str(dd2.loc[0,'dow']).capitalize() + '🗓</i></u></b>\n'
        for r in range(len(dd2)):
            fish = f'🙏{r+1}. ' + dd2.loc[r,'fish']
            l1 = ' - ' + dd2.loc[r,'l1']
            l1g = ' (' + dd2.loc[r,'l1g'] + ')'
            l2 = ' / ' + dd2.loc[r,'l2'] if dd2.loc[r,'l2'] != '' else ''
            l2g = ' (' + dd2.loc[r,'l2g'] + ')' if dd2.loc[r,'l2g'] != '' else ''
            px2 = px2 + f'<pre>{fish}{l1}{l1g}{l2}{l2g}</pre>\n'
    if len(dd3) == 0:
        px3 = ''
    else:
        px3 = '\n<b><u><i>🗓' + str(dd3.loc[0,'dow']).capitalize() + '🗓</i></u></b>\n'
        for r in range(len(dd3)):
            fish = f'🙏{r+1}. ' + dd3.loc[r,'fish']
            l1 = ' - ' + dd3.loc[r,'l1']
            l1g = ' (' + dd3.loc[r,'l1g'] + ')'
            l2 = ' / ' + dd3.loc[r,'l2'] if dd3.loc[r,'l2'] != '' else ''
            l2g = ' (' + dd3.loc[r,'l2g'] + ')' if dd3.loc[r,'l2g'] != '' else ''
            px3 = px3 + f'<pre>{fish}{l1}{l1g}{l2}{l2g}</pre>\n'
    if len(dd4) == 0:
        px4 = ''
    else:
        px4 = '\n<b><u><i>🗓' + str(dd4.loc[0,'dow']).capitalize() + '🗓</i></u></b>\n'
        for r in range(len(dd4)):
            fish = f'🙏{r+1}. ' + dd4.loc[r,'fish']
            l1 = ' - ' + dd4.loc[r,'l1']
            l1g = ' (' + dd4.loc[r,'l1g'] + ')'
            l2 = ' / ' + dd4.loc[r,'l2'] if dd4.loc[r,'l2'] != '' else ''
            l2g = ' (' + dd4.loc[r,'l2g'] + ')' if dd4.loc[r,'l2g'] != '' else ''
            px4 = px4 + f'<pre>{fish}{l1}{l1g}{l2}{l2g}</pre>\n'
    if len(dd5) == 0:
        px5 = ''
    else:
        px5 = '\n<b><u><i>🗓' + str(dd5.loc[0,'dow']).capitalize() + '🗓</i></u></b>\n'
        for r in range(len(dd5)):
            fish = f'🙏{r+1}. ' + dd5.loc[r,'fish']
            l1 = ' - ' + dd5.loc[r,'l1']
            l1g = ' (' + dd5.loc[r,'l1g'] + ')'
            l2 = ' / ' + dd5.loc[r,'l2'] if dd5.loc[r,'l2'] != '' else ''
            l2g = ' (' + dd5.loc[r,'l2g'] + ')' if dd5.loc[r,'l2g'] != '' else ''
            px5 = px5 + f'<pre>{fish}{l1}{l1g}{l2}{l2g}</pre>\n'
    if len(dd6) == 0:
        px6 = ''
    else:
        px6 = '\n<b><u><i>🗓' + str(dd6.loc[0,'dow']).capitalize() + '🗓</i></u></b>\n'
        for r in range(len(dd6)):
            fish = f'🙏{r+1}. ' + dd6.loc[r,'fish']
            l1 = ' - ' + dd6.loc[r,'l1']
            l1g = ' (' + dd6.loc[r,'l1g'] + ')'
            l2 = ' / ' + dd6.loc[r,'l2'] if dd6.loc[r,'l2'] != '' else ''
            l2g = ' (' + dd6.loc[r,'l2g'] + ')' if dd6.loc[r,'l2g'] != '' else ''
            px6 = px6 + f'<pre>{fish}{l1}{l1g}{l2}{l2g}</pre>\n'
    if len(dd7) == 0:
        px7 = ''
    else:
        px7 = '\n<b><u><i>🗓' + str(dd7.loc[0,'dow']).capitalize() + '🗓</i></u></b>\n'
        for r in range(len(dd7)):
            fish = f'🙏{r+1}. ' + dd7.loc[r,'fish']
            l1 = ' - ' + dd7.loc[r,'l1']
            l1g = ' (' + dd7.loc[r,'l1g'] + ')'
            l2 = ' / ' + dd7.loc[r,'l2'] if dd7.loc[r,'l2'] != '' else ''
            l2g = ' (' + dd7.loc[r,'l2g'] + ')' if dd7.loc[r,'l2g'] != '' else ''
            px1 = px1 + f'<pre>{fish}{l1}{l1g}{l2}{l2g}</pre>\n'
    print(">>>Return")
    return f'<i><b><u>👥Picking Expectants</u></b>\n. . . . Next seven days . . . .</i>\n{px1}{px2}{px3}{px4}{px5}{px6}{px7}' if len(f'{px1}{px2}{px3}{px4}{px5}{px6}{px7}') != 0 else '<i>No picking expectants in next 7 days</i>'







def bbstatus(g, d, sid, access, v2=False): # BB FUNCTIONS
    print(f"\n>>>bbstatus: g={g}, d={d}, sid={sid}, access={access}, v2={v2}")
    g = g if access in ('Group','CUL') else '%'
    d = d.capitalize().replace('d','D')
    d = re.sub(r'(¹|²)d([0-9]*)',r'\1D\2',d)
    if access in ('Group','CUL'):
        grpdept = g.capitalize()
        grpdept = re.sub(r'(¹|²)g([0-9]*)',r'\1G\2',g)
    else:
        grpdept = d.replace('D[0-9]%','Youth').replace('Mw[0-9]%','MW').replace('24', '24 Dept').replace('%', 'Church')
        
    codeybbstatusmembers = 'CodeyBBStatusMembers2' if v2 else 'CodeyBBStatusMembers'
    fe_col = ', FE' if v2 else ''
    fe_sum = ', SUM(FE)FE' if v2 else ''
    
    print(f"bbstatus parameters:          g = '{g}'          d = '{d}'          sid = {sid}          access = '{access}'          v2 = {v2}")
    
    bb_mem    = f"SELECT Dept, Grp, MemberCode, pNew, pOld{fe_col}, bbA, cctA, bbME, cctI, pFA, bbFA, Total FROM {codeybbstatusmembers}('{sid}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}' ORDER BY GID".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    bb_group  = f"SELECT Grp, SUM(pNew)pNew, SUM(pOld)pOld{fe_sum}, SUM(bbA)bbA, SUM(cctA)cctA, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA, SUM(Total)Total FROM {codeybbstatusmembers}('{sid}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}' GROUP BY Grp, GID ORDER BY GID".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    bb_dept   = f"SELECT Dept, SUM(pNew)pNew, SUM(pOld)pOld{fe_sum}, SUM(bbA)bbA, SUM(cctA)cctA, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA, SUM(Total)Total FROM {codeybbstatusmembers}('{sid}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}' GROUP BY Dept, DID ORDER BY DID".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    bb_youth  = f"SELECT SUM(pNew)pNew, SUM(pOld)pOld{fe_sum}, SUM(bbA)bbA, SUM(cctA)cctA, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA, SUM(Total)Total FROM {codeybbstatusmembers}('{sid}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}'".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    
    print(bb_group)
    
    with odbc.connect(conn_str) as conn:
        dm = pd.read_sql(bb_mem, conn)
        dg = pd.read_sql(bb_group, conn)
        dd = pd.read_sql(bb_dept, conn)
        dy = pd.read_sql(bb_youth, conn)


    dg.replace(r'MWDept',r'MWDpt', regex = True, inplace = True)
    dg.replace(r'Serving',r'Sv', regex = True, inplace = True)
    dg.replace(r'Culture',r'Cul', regex = True, inplace = True)
    dd.replace(r'InnerSFT',r'InSFT', regex = True, inplace = True)

    if v2:
        dm.columns = ['Dept','Grp','Member','pNew','pOld','FE','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
        dg.columns = ['Grp','pNew','pOld','FE','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
        dd.columns = ['Dept','pNew','pOld','FE','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
        dy.columns = ['pNew','pOld','FE','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
    else:
        dm.columns = ['Dept','Grp','Member','pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
        dg.columns = ['Grp','pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
        dd.columns = ['Dept','pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
        dy.columns = ['pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
    
    dd.replace(r' Dept',r'', regex = True, inplace = True)
    
    member = str()
    if access in ('Group','CUL'):
        for r in range(len(dm)):
            bbt =   str(dm.loc[r,'Member'])[:5] + ' '*(5-len(str(dm.loc[r,'Member'])[:5]))
            pn  = ' '*(4-len(str(dm.loc[r,'pNew']))) + str(dm.loc[r,'pNew'])
            po  = ' '*(4-len(str(dm.loc[r,'pOld']))) + str(dm.loc[r,'pOld'])
            ba  = ' '*(4-len(str(dm.loc[r,'bbA'])))  + str(dm.loc[r,'bbA'])
            ba  = ' '*(4-len(str(dm.loc[r,'FE'])))   + str(dm.loc[r,'FE']) + '|' + ba if v2 else ba
            ca  = ' '*(4-len(str(dm.loc[r,'cctA']))) + str(dm.loc[r,'cctA'])
            bm  = ' '*(4-len(str(dm.loc[r,'bbME']))) + str(dm.loc[r,'bbME'])
            ci  = ' '*(4-len(str(dm.loc[r,'cctI']))) + str(dm.loc[r,'cctI'])
            pf  = ' '*(4-len(str(dm.loc[r,'pFA'])))  + str(dm.loc[r,'pFA'])
            bf  = ' '*(4-len(str(dm.loc[r,'bbFA']))) + str(dm.loc[r,'bbFA'])
            t   = ' '*(5-len(str(dm.loc[r,'Tot'])))  + str(dm.loc[r,'Tot'])
            member = f'{member}{bbt}[{pn}|{po}|{ba}|{ca}|{bm}|{ci}|{pf}|{bf}|{t}]\n'        
        member = member + '\n'
            
            
    group = str()    
    for r in range(len(dg)):
        grp =   str(dg.loc[r,'Grp'])[:5] + ' '*(5-len(str(dg.loc[r,'Grp'])[:5]))
        pn  = ' '*(4-len(str(dg.loc[r,'pNew']))) + str(dg.loc[r,'pNew'])
        po  = ' '*(4-len(str(dg.loc[r,'pOld']))) + str(dg.loc[r,'pOld'])
        ba  = ' '*(4-len(str(dg.loc[r,'bbA'])))  + str(dg.loc[r,'bbA'])
        ba  = ' '*(4-len(str(dg.loc[r,'FE'])))   + str(dg.loc[r,'FE']) + '|' + ba if v2 else ba
        ca  = ' '*(4-len(str(dg.loc[r,'cctA']))) + str(dg.loc[r,'cctA'])
        bm  = ' '*(4-len(str(dg.loc[r,'bbME']))) + str(dg.loc[r,'bbME'])
        ci  = ' '*(4-len(str(dg.loc[r,'cctI']))) + str(dg.loc[r,'cctI'])
        pf  = ' '*(4-len(str(dg.loc[r,'pFA'])))  + str(dg.loc[r,'pFA'])
        bf  = ' '*(4-len(str(dg.loc[r,'bbFA']))) + str(dg.loc[r,'bbFA'])
        t   = ' '*(5-len(str(dg.loc[r,'Tot'])))  + str(dg.loc[r,'Tot'])
        group = f'{group}{grp}[{pn}|{po}|{ba}|{ca}|{bm}|{ci}|{pf}|{bf}|{t}]\n'
    group = group + '\n'
            
    dept = str()  
    if access not in ('Group','CUL'):
        for r in range(len(dd)):
            dpt =   str(dd.loc[r,'Dept'])[:5] + ' '*(5-len(str(dd.loc[r,'Dept'])[:5]))
            pn  = ' '*(4-len(str(dd.loc[r,'pNew']))) + str(dd.loc[r,'pNew'])
            po  = ' '*(4-len(str(dd.loc[r,'pOld']))) + str(dd.loc[r,'pOld'])
            ba  = ' '*(4-len(str(dd.loc[r,'bbA'])))  + str(dd.loc[r,'bbA'])
            ba  = ' '*(4-len(str(dd.loc[r,'FE'])))   + str(dd.loc[r,'FE']) + '|' + ba if v2 else ba
            ca  = ' '*(4-len(str(dd.loc[r,'cctA']))) + str(dd.loc[r,'cctA'])
            bm  = ' '*(4-len(str(dd.loc[r,'bbME']))) + str(dd.loc[r,'bbME'])
            ci  = ' '*(4-len(str(dd.loc[r,'cctI']))) + str(dd.loc[r,'cctI'])
            pf  = ' '*(4-len(str(dd.loc[r,'pFA'])))  + str(dd.loc[r,'pFA'])
            bf  = ' '*(4-len(str(dd.loc[r,'bbFA']))) + str(dd.loc[r,'bbFA'])
            t   = ' '*(5-len(str(dd.loc[r,'Tot'])))  + str(dd.loc[r,'Tot'])
            dept = f'{dept}{dpt}[{pn}|{po}|{ba}|{ca}|{bm}|{ci}|{pf}|{bf}|{t}]\n'
        dept = dept + '\n'
    
    total = str()
    if d in ('D[0-9]%','%'):
        pn  = ' '*(4-len(str(dy.loc[0,'pNew']))) + str(dy.loc[0,'pNew'])
        po  = ' '*(4-len(str(dy.loc[0,'pOld']))) + str(dy.loc[0,'pOld'])
        ba  = ' '*(4-len(str(dy.loc[0,'bbA'])))  + str(dy.loc[0,'bbA'])
        ba  = ' '*(4-len(str(dy.loc[0,'FE'])))   + str(dy.loc[0,'FE']) + '|' + ba if v2 else ba
        ca  = ' '*(4-len(str(dy.loc[0,'cctA']))) + str(dy.loc[0,'cctA'])
        bm  = ' '*(4-len(str(dy.loc[0,'bbME']))) + str(dy.loc[0,'bbME'])
        ci  = ' '*(4-len(str(dy.loc[0,'cctI']))) + str(dy.loc[0,'cctI'])
        pf  = ' '*(4-len(str(dy.loc[0,'pFA'])))  + str(dy.loc[0,'pFA'])
        bf  = ' '*(4-len(str(dy.loc[0,'bbFA']))) + str(dy.loc[0,'bbFA'])
        t   = ' '*(5-len(str(dy.loc[0,'Tot'])))  + str(dy.loc[0,'Tot'])
        total = f'Total[{pn}|{po}|{ba}|{ca}|{bm}|{ci}|{pf}|{bf}|{t}]'
    
    ab = 'FE | ' if v2 else ''
    header = f"     [ NP | OP | {ab}AB | CA | ME | CI | FP | FA | TOT ]"
    summary = f"<b><u>{grpdept} BB Status Summary</u></b>\n\n<pre>{header}\n\n{member}{group}{dept}{total}</pre>"
    summary = re.sub(r'\.0',r'  ',summary) # Replaces '.0' with empty space
    summary = re.sub(r'(\D)0([^.])',r'\1-\2',summary)   # Replaces lone '0' with '-'
    print(">>>Return")
    return summary








def bbtstatus(q, g, d, sid, access, bbtdept, v2=False): # BBT FUNCTIONS
    print(f"\n>>>bbtstatus: g={g}, d={d}, sid={sid}, access={access}, v2={v2}")
    name = 'BBTCode' if access in ('Group','CUL') else 'BBTGrp'

    g = g if access in ('Group','CUL') else '%'
    d = d.capitalize().replace('d','D')
    d = re.sub(r'(¹|²)d([0-9]*)',r'\1D\2',d)
    if access in ('Group','CUL'):
        grpdept = g.capitalize()
        grpdept = re.sub(r'(¹|²)g([0-9]*)',r'\1G\2',g)
    else:
        grpdept = d.replace('D[0-9]%','Youth').replace('Mw[0-9]%','MW').replace('24', '24 Dept').replace('%', 'Church')
    
    prebbtfilt = f" AND BtmNo = '{q[6:]}'" if q[6:] != '' else ''
    btmfilt = f" AND BtmNo = '{q[3:]}'" if q[3:] != '' else ''

    i = q[:3]
    bbtvalues = {'bbt' : ['BBT',   " AND BBTStatus = 'BBT'"],
                 'pre' : [q.upper(), f"{prebbtfilt} AND BBTStatus = 'Pre-BBT'"],
                 'gyj' : ['GYJN BBT',  " AND UID IN (SELECT UID FROM TGWPositionCurrent WHERE PID = 30)"],
                 'btm' : [q.upper(), f"{btmfilt} AND BBTStatus = 'BTM'"]}
    bbttype,query = bbtvalues[i]
    
    codeybbtstatusmembers = 'CodeyBBTStatusMembers2' if v2 else 'CodeyBBTStatusMembers'
    # d_filt = '%' if v2 and d in ('D[0-9]%','%') else d
    d_filt = d
    fe_col = ', FE' if v2 else ''
    fe_sum = ', SUM(FE)FE' if v2 else ''
    
    bb_mem = f"SELECT Dept, Grp, {name}, pNew, pOld{fe_col}, bbA, cctA, bbME, cctI, pFA, bbFA, Total FROM {codeybbtstatusmembers}('{sid}') WHERE Dept LIKE '{d_filt}' AND Grp NOT IN ('SCM','MWSCM','Inert') AND Grp LIKE '{g}'{query} ORDER BY GID, {name}".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    bb_group = f"SELECT Grp, SUM(pNew)pNew, SUM(pOld)pOld{fe_sum}, SUM(bbA)bbA, SUM(cctA)cctA, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA, SUM(Total)Total FROM {codeybbtstatusmembers}('{sid}') WHERE Dept LIKE '{d_filt}' AND Grp NOT IN ('SCM','MWSCM','Inert') AND Grp LIKE '{g}'{query} GROUP BY Grp, GID ORDER BY GID".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    bb_dept = f"SELECT Dept, SUM(pNew)pNew, SUM(pOld)pOld{fe_sum}, SUM(bbA)bbA, SUM(cctA)cctA, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA, SUM(Total)Total FROM {codeybbtstatusmembers}('{sid}') WHERE Dept LIKE '{d_filt}' AND Grp NOT IN ('SCM','MWSCM','Inert') AND Grp LIKE '{g}'{query} GROUP BY Dept, DID ORDER BY DID".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    bb_youth = f"SELECT SUM(pNew)pNew, SUM(pOld)pOld{fe_sum}, SUM(bbA)bbA, SUM(cctA)cctA, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA, SUM(Total)Total FROM {codeybbtstatusmembers}('{sid}') WHERE Dept LIKE '{d_filt}' AND Grp NOT IN ('SCM','MWSCM','Inert') AND Grp LIKE '{g}'{query}".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    
    print(bb_group)
    
    with odbc.connect(conn_str) as conn:
        dm = pd.read_sql(bb_mem, conn)
        dg = pd.read_sql(bb_group, conn)
        dd = pd.read_sql(bb_dept, conn)
        dy = pd.read_sql(bb_youth, conn)


    dg.replace(r'MWDept',r'MWDpt', regex = True, inplace = True)
    dg.replace(r'Serving',r'Sv', regex = True, inplace = True)
    dg.replace(r'Culture',r'Cul', regex = True, inplace = True)
    dd.replace(r'InnerSFT',r'InSFT', regex = True, inplace = True)

    if v2:
        dm.columns = ['Dept','Grp','BBT','pNew','pOld','FE','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
        dg.columns = ['Grp','pNew','pOld','FE','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
        dd.columns = ['Dept','pNew','pOld','FE','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
        dy.columns = ['pNew','pOld','FE','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
    else:
        dm.columns = ['Dept','Grp','BBT','pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
        dg.columns = ['Grp','pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
        dd.columns = ['Dept','pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
        dy.columns = ['pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
    
    dd.replace(r' Dept',r'', regex = True, inplace = True)
    
    member = str()
    if bbtdept is False and not d.endswith('D[0-9]%'):
        for r in range(len(dm)):
            bbt =   str(dm.loc[r,'BBT'])[:5] + ' '*(5-len(str(dm.loc[r,'BBT'])[:5]))
            pn  = ' '*(3-len(str(dm.loc[r,'pNew']))) + str(dm.loc[r,'pNew'])
            po  = ' '*(3-len(str(dm.loc[r,'pOld']))) + str(dm.loc[r,'pOld'])
            ba  = ' '*(3-len(str(dm.loc[r,'bbA'])))  + str(dm.loc[r,'bbA'])
            ba  = ' '*(3-len(str(dm.loc[r,'FE'])))   + str(dm.loc[r,'FE']) + '|' + ba if v2 else ba
            ca  = ' '*(3-len(str(dm.loc[r,'cctA']))) + str(dm.loc[r,'cctA'])
            bm  = ' '*(3-len(str(dm.loc[r,'bbME']))) + str(dm.loc[r,'bbME'])
            ci  = ' '*(3-len(str(dm.loc[r,'cctI']))) + str(dm.loc[r,'cctI'])
            pf  = ' '*(3-len(str(dm.loc[r,'pFA'])))  + str(dm.loc[r,'pFA'])
            bf  = ' '*(3-len(str(dm.loc[r,'bbFA']))) + str(dm.loc[r,'bbFA'])
            t   = ' '*(3-len(str(dm.loc[r,'Tot'])))  + str(dm.loc[r,'Tot'])
            member = f'{member}{bbt}[{pn}|{po}|{ba}|{ca}|{bm}|{ci}|{pf}|{bf}|{t}]\n'        
        member = member + '\n'
            
    group = str()
    if bbtdept is False:    
        for r in range(len(dg)):
            grp =   str(dg.loc[r,'Grp'])[:5] + ' '*(5-len(str(dg.loc[r,'Grp'])[:5]))
            pn  = ' '*(3-len(str(dg.loc[r,'pNew']))) + str(dg.loc[r,'pNew'])
            po  = ' '*(3-len(str(dg.loc[r,'pOld']))) + str(dg.loc[r,'pOld'])
            ba  = ' '*(3-len(str(dg.loc[r,'bbA'])))  + str(dg.loc[r,'bbA'])
            ba  = ' '*(3-len(str(dg.loc[r,'FE'])))   + str(dg.loc[r,'FE']) + '|' + ba if v2 else ba
            ca  = ' '*(3-len(str(dg.loc[r,'cctA']))) + str(dg.loc[r,'cctA'])
            bm  = ' '*(3-len(str(dg.loc[r,'bbME']))) + str(dg.loc[r,'bbME'])
            ci  = ' '*(3-len(str(dg.loc[r,'cctI']))) + str(dg.loc[r,'cctI'])
            pf  = ' '*(3-len(str(dg.loc[r,'pFA'])))  + str(dg.loc[r,'pFA'])
            bf  = ' '*(3-len(str(dg.loc[r,'bbFA']))) + str(dg.loc[r,'bbFA'])
            t   = ' '*(3-len(str(dg.loc[r,'Tot'])))  + str(dg.loc[r,'Tot'])
            group = f'{group}{grp}[{pn}|{po}|{ba}|{ca}|{bm}|{ci}|{pf}|{bf}|{t}]\n'
        group = group + '\n'
            
    dept = str()  
    if access not in ('Group','CUL'):  
        for r in range(len(dd)):
            dpt =   str(dd.loc[r,'Dept'])[:5] + ' '*(5-len(str(dd.loc[r,'Dept'])[:5]))
            pn  = ' '*(3-len(str(dd.loc[r,'pNew']))) + str(dd.loc[r,'pNew'])
            po  = ' '*(3-len(str(dd.loc[r,'pOld']))) + str(dd.loc[r,'pOld'])
            ba  = ' '*(3-len(str(dd.loc[r,'bbA'])))  + str(dd.loc[r,'bbA'])
            ba  = ' '*(3-len(str(dd.loc[r,'FE'])))   + str(dd.loc[r,'FE']) + '|' + ba if v2 else ba
            ca  = ' '*(3-len(str(dd.loc[r,'cctA']))) + str(dd.loc[r,'cctA'])
            bm  = ' '*(3-len(str(dd.loc[r,'bbME']))) + str(dd.loc[r,'bbME'])
            ci  = ' '*(3-len(str(dd.loc[r,'cctI']))) + str(dd.loc[r,'cctI'])
            pf  = ' '*(3-len(str(dd.loc[r,'pFA'])))  + str(dd.loc[r,'pFA'])
            bf  = ' '*(3-len(str(dd.loc[r,'bbFA']))) + str(dd.loc[r,'bbFA'])
            t   = ' '*(3-len(str(dd.loc[r,'Tot'])))  + str(dd.loc[r,'Tot'])
            dept = f'{dept}{dpt}[{pn}|{po}|{ba}|{ca}|{bm}|{ci}|{pf}|{bf}|{t}]\n'
        dept = dept + '\n'
        
    total = str()
    if d in ('D[0-9]%','%'):
        pn  = ' '*(3-len(str(dy.loc[0,'pNew']))) + str(dy.loc[0,'pNew'])
        po  = ' '*(3-len(str(dy.loc[0,'pOld']))) + str(dy.loc[0,'pOld'])
        ba  = ' '*(3-len(str(dy.loc[0,'bbA'])))  + str(dy.loc[0,'bbA'])
        ba  = ' '*(3-len(str(dy.loc[0,'FE'])))   + str(dy.loc[0,'FE']) + '|' + ba if v2 else ba
        ca  = ' '*(3-len(str(dy.loc[0,'cctA']))) + str(dy.loc[0,'cctA'])
        bm  = ' '*(3-len(str(dy.loc[0,'bbME']))) + str(dy.loc[0,'bbME'])
        ci  = ' '*(3-len(str(dy.loc[0,'cctI']))) + str(dy.loc[0,'cctI'])
        pf  = ' '*(3-len(str(dy.loc[0,'pFA'])))  + str(dy.loc[0,'pFA'])
        bf  = ' '*(3-len(str(dy.loc[0,'bbFA']))) + str(dy.loc[0,'bbFA'])
        t   = ' '*(3-len(str(dy.loc[0,'Tot'])))  + str(dy.loc[0,'Tot'])
        total = f'Total[{pn}|{po}|{ba}|{ca}|{bm}|{ci}|{pf}|{bf}|{t}]'
    
    ab = 'FE| ' if v2 else ''
    header = f"     [ NP| OP| {ab}AB| CA| ME| CI| FP| FA|TOT]"
    summary = f"<b><u>{grpdept} {bbttype} Status Summary</u></b>\n\n<pre>{header}\n\n{member}{group}{dept}{total}</pre>"
    summary = re.sub(r'\.0',r'  ',summary) # Replaces '.0' with empty space
    summary = re.sub(r'(\D)0([^.])',r'\1-\2',summary)   # Replaces lone '0' with '-'
    print(">>>Return")
    return summary






def newbbstatus(g, d, sid, access): # BB FUNCTIONS
    print(f"\n>>>bbstatus: g={g}, d={d}, sid={sid}, access={access}")
    g = g if access in ('Group','CUL') else '%'
    d = d.capitalize().replace('d','D')
    d = re.sub(r'(¹|²)d([0-9]*)',r'\1D\2',d)
    if access in ('Group','CUL'):
        grpdept = g.capitalize()
        grpdept = re.sub(r'(¹|²)g([0-9]*)',r'\1G\2',g)
    else:
        grpdept = d.replace('D[0-9]%','Youth').replace('Mw[0-9]%','MW').replace('24', '24 Dept').replace('%', 'Church')
        
    
    print(f"bbstatus parameters:          g = '{g}'          d = '{d}'          sid = {sid}          access = '{access}'")
    
    table = f"CodeyBBStatusMembersUBB('{sid}')"
    cols = "Dept, Grp, MemberCode, pNew, pOld, pFA, FE, bbA, cct1, cct2, cctI, UBB, bbME, bbFA, Total"
    sums = "SUM(pNew)pNew, SUM(pOld)pOld, SUM(pFA)pFA, SUM(FE)FE, SUM(bbA)bbA, SUM(cct1)cct1, SUM(cct2)cct2, SUM(cctI)cctI, SUM(UBB)UBB, SUM(bbME)bbME, SUM(bbFA)bbFA, SUM(Total)Total"
    conditions = f"Dept LIKE '{d}' AND Grp LIKE '{g}'".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    
    bb_mem    = f"SELECT {cols} FROM {table} WHERE {conditions} ORDER BY GID"
    bb_group  = f"SELECT Grp, {sums} FROM {table} WHERE {conditions} GROUP BY Grp, GID ORDER BY GID"
    bb_dept   = f"SELECT Dept, {sums} FROM {table} WHERE {conditions} GROUP BY Dept, DID ORDER BY DID"
    # bb_region = f"SELECT District, {sums} FROM {table} WHERE {conditions} GROUP BY District"
    bb_youth  = f"SELECT {sums} FROM {table} WHERE {conditions}"
    
    print(bb_group)
    
    with odbc.connect(conn_str) as conn:
        dm = pd.read_sql(bb_mem, conn)
        dg = pd.read_sql(bb_group, conn)
        dd = pd.read_sql(bb_dept, conn)
        # dr = pd.read_sql(bb_region, conn)
        dy = pd.read_sql(bb_youth, conn)

    dm.columns = ['Dept','Grp','Member','pNew','pOld','pFA','FE','bbA','cct1','cct2','cctI','UBB','bbME','bbFA','Tot']
    dg.columns = ['Grp','pNew','pOld','pFA','FE','bbA','cct1','cct2','cctI','UBB','bbME','bbFA','Tot']
    dd.columns = ['Dept','pNew','pOld','pFA','FE','bbA','cct1','cct2','cctI','UBB','bbME','bbFA','Tot']
    # dr.columns = ['Region','pNew','pOld','pFA','FE','bbA','cct1','cct2','cctI','UBB','bbME','bbFA','Tot']
    dy.columns = ['pNew','pOld','pFA','FE','bbA','cct1','cct2','cctI','UBB','bbME','bbFA','Tot']
    dd.replace(r' Dept',r'', regex = True, inplace = True)
    
    member = str()
    if access in ('Group','CUL'):
        for r in range(len(dm)):
            bbt =   str(dm.loc[r,'Member'])[:5] + ' '*(5-len(str(dm.loc[r,'Member'])[:5]))
            pn  = ' '*(4-len(str(dm.loc[r,'pNew']))) + str(dm.loc[r,'pNew'])
            po  = ' '*(4-len(str(dm.loc[r,'pOld']))) + str(dm.loc[r,'pOld'])
            pf  = ' '*(4-len(str(dm.loc[r,'pFA'])))  + str(dm.loc[r,'pFA'])
            fe  = ' '*(4-len(str(dm.loc[r,'FE'])))   + str(dm.loc[r,'FE'])
            ba  = ' '*(4-len(str(dm.loc[r,'bbA'])))  + str(dm.loc[r,'bbA'])
            c1  = ' '*(4-len(str(dm.loc[r,'cct1']))) + str(dm.loc[r,'cct1'])
            c2  = ' '*(4-len(str(dm.loc[r,'cct2']))) + str(dm.loc[r,'cct2'])
            ci  = ' '*(4-len(str(dm.loc[r,'cctI']))) + str(dm.loc[r,'cctI'])
            ub  = ' '*(4-len(str(dm.loc[r,'UBB'])))  + str(dm.loc[r,'UBB'])
            bm  = ' '*(4-len(str(dm.loc[r,'bbME']))) + str(dm.loc[r,'bbME'])
            fa  = ' '*(4-len(str(dm.loc[r,'bbFA']))) + str(dm.loc[r,'bbFA'])
            t   = ' '*(5-len(str(dm.loc[r,'Tot'])))  + str(dm.loc[r,'Tot'])
            member = f'{member}{bbt}[{pn}|{po}|{pf}|{fe}|{ba}|{c1}|{c2}|{ci}|{ub}|{bm}|{fa}|{t}]\n'
        member = member + '\n'
            
            
    group = str()    
    for r in range(len(dg)):
        grp =   str(dg.loc[r,'Grp'])[:5] + ' '*(5-len(str(dg.loc[r,'Grp'])[:5]))
        pn  = ' '*(4-len(str(dg.loc[r,'pNew']))) + str(dg.loc[r,'pNew'])
        po  = ' '*(4-len(str(dg.loc[r,'pOld']))) + str(dg.loc[r,'pOld'])
        pf  = ' '*(4-len(str(dg.loc[r,'pFA'])))  + str(dg.loc[r,'pFA'])
        fe  = ' '*(4-len(str(dg.loc[r,'FE'])))   + str(dg.loc[r,'FE'])
        ba  = ' '*(4-len(str(dg.loc[r,'bbA'])))  + str(dg.loc[r,'bbA'])
        c1  = ' '*(4-len(str(dg.loc[r,'cct1']))) + str(dg.loc[r,'cct1'])
        c2  = ' '*(4-len(str(dg.loc[r,'cct2']))) + str(dg.loc[r,'cct2'])
        ci  = ' '*(4-len(str(dg.loc[r,'cctI']))) + str(dg.loc[r,'cctI'])
        ub  = ' '*(4-len(str(dg.loc[r,'UBB'])))  + str(dg.loc[r,'UBB'])
        bm  = ' '*(4-len(str(dg.loc[r,'bbME']))) + str(dg.loc[r,'bbME'])
        fa  = ' '*(4-len(str(dg.loc[r,'bbFA']))) + str(dg.loc[r,'bbFA'])
        t   = ' '*(5-len(str(dg.loc[r,'Tot'])))  + str(dg.loc[r,'Tot'])
        group = f'{group}{grp}[{pn}|{po}|{pf}|{fe}|{ba}|{c1}|{c2}|{ci}|{ub}|{bm}|{fa}|{t}]\n'
    group = group + '\n'
            
    dept = str()  
    if access not in ('Group','CUL'):
        for r in range(len(dd)):
            dpt =   str(dd.loc[r,'Dept'])[:5] + ' '*(5-len(str(dd.loc[r,'Dept'])[:5]))
            pn  = ' '*(4-len(str(dd.loc[r,'pNew']))) + str(dd.loc[r,'pNew'])
            po  = ' '*(4-len(str(dd.loc[r,'pOld']))) + str(dd.loc[r,'pOld'])
            pf  = ' '*(4-len(str(dd.loc[r,'pFA'])))  + str(dd.loc[r,'pFA'])
            fe  = ' '*(4-len(str(dd.loc[r,'FE'])))   + str(dd.loc[r,'FE'])
            ba  = ' '*(4-len(str(dd.loc[r,'bbA'])))  + str(dd.loc[r,'bbA'])
            c1  = ' '*(4-len(str(dd.loc[r,'cct1']))) + str(dd.loc[r,'cct1'])
            c2  = ' '*(4-len(str(dd.loc[r,'cct2']))) + str(dd.loc[r,'cct2'])
            ci  = ' '*(4-len(str(dd.loc[r,'cctI']))) + str(dd.loc[r,'cctI'])
            ub  = ' '*(4-len(str(dd.loc[r,'UBB'])))  + str(dd.loc[r,'UBB'])
            bm  = ' '*(4-len(str(dd.loc[r,'bbME']))) + str(dd.loc[r,'bbME'])
            fa  = ' '*(4-len(str(dd.loc[r,'bbFA']))) + str(dd.loc[r,'bbFA'])
            t   = ' '*(5-len(str(dd.loc[r,'Tot'])))  + str(dd.loc[r,'Tot'])
            dept = f'{dept}{dpt}[{pn}|{po}|{pf}|{fe}|{ba}|{c1}|{c2}|{ci}|{ub}|{bm}|{fa}|{t}]\n'
        dept = dept + '\n'
    
    # region = str()
    # if d.endswith('D[0-9]%'):    
    #     for r in range(len(dr)):
    #         reg =   str(dr.loc[r,'Region']) + ' '*(5-len(str(dr.loc[r,'Region'])))
    #         pn  = ' '*(4-len(str(dr.loc[r,'pNew']))) + str(dr.loc[r,'pNew'])
    #         po  = ' '*(4-len(str(dr.loc[r,'pOld']))) + str(dr.loc[r,'pOld'])
    #         pf  = ' '*(4-len(str(dr.loc[r,'pFA'])))  + str(dr.loc[r,'pFA'])
    #         fe  = ' '*(4-len(str(dr.loc[r,'FE'])))   + str(dr.loc[r,'FE'])
    #         ba  = ' '*(4-len(str(dr.loc[r,'bbA'])))  + str(dr.loc[r,'bbA'])
    #         c1  = ' '*(4-len(str(dr.loc[r,'cct1']))) + str(dr.loc[r,'cct1'])
    #         c2  = ' '*(4-len(str(dr.loc[r,'cct2']))) + str(dr.loc[r,'cct2'])
    #         ci  = ' '*(4-len(str(dr.loc[r,'cctI']))) + str(dr.loc[r,'cctI'])
    #         ub  = ' '*(4-len(str(dr.loc[r,'UBB'])))  + str(dr.loc[r,'UBB'])
    #         bm  = ' '*(4-len(str(dr.loc[r,'bbME']))) + str(dr.loc[r,'bbME'])
    #         fa  = ' '*(4-len(str(dr.loc[r,'bbFA']))) + str(dr.loc[r,'bbFA'])
    #         t   = ' '*(5-len(str(dr.loc[r,'Tot'])))  + str(dr.loc[r,'Tot'])
    #         region = f'{region}{reg}[{pn}|{po}|{pf}|{fe}|{ba}|{c1}|{c2}|{ci}|{ub}|{bm}|{fa}|{t}]\n'
    #     region = region + '\n'
    
    total = str()
    if d in ('D[0-9]%','%'):
        pn  = ' '*(4-len(str(dy.loc[0,'pNew']))) + str(dy.loc[0,'pNew'])
        po  = ' '*(4-len(str(dy.loc[0,'pOld']))) + str(dy.loc[0,'pOld'])
        pf  = ' '*(4-len(str(dy.loc[0,'pFA'])))  + str(dy.loc[0,'pFA'])
        fe  = ' '*(4-len(str(dy.loc[0,'FE'])))   + str(dy.loc[0,'FE'])
        ba  = ' '*(4-len(str(dy.loc[0,'bbA'])))  + str(dy.loc[0,'bbA'])
        c1  = ' '*(4-len(str(dy.loc[0,'cct1']))) + str(dy.loc[0,'cct1'])
        c2  = ' '*(4-len(str(dy.loc[0,'cct2']))) + str(dy.loc[0,'cct2'])
        ci  = ' '*(4-len(str(dy.loc[0,'cctI']))) + str(dy.loc[0,'cctI'])
        ub  = ' '*(4-len(str(dy.loc[0,'UBB'])))  + str(dy.loc[0,'UBB'])
        bm  = ' '*(4-len(str(dy.loc[0,'bbME']))) + str(dy.loc[0,'bbME'])
        fa  = ' '*(4-len(str(dy.loc[0,'bbFA']))) + str(dy.loc[0,'bbFA'])
        t   = ' '*(5-len(str(dy.loc[0,'Tot'])))  + str(dy.loc[0,'Tot'])
        total = f'Total[{pn}|{po}|{pf}|{fe}|{ba}|{c1}|{c2}|{ci}|{ub}|{bm}|{fa}|{t}]'
    
    summary = f"<b><u>{grpdept} BB Status Summary</u></b>\n\n<pre>     [ NP | OP | FP | FE | AB | C1 | C2 | CI | UB | ME | FA | TOT ]\n\n{member}{group}{dept}{total}</pre>"
    summary = re.sub(r'\.0',r'  ',summary) # Replaces '.0' with empty space
    summary = re.sub(r'(\D)0([^.])',r'\1-\2',summary)   # Replaces lone '0' with '-'
    print(">>>Return")
    return summary




def newbbtstatus(q, g, d, sid, access): # BBT FUNCTIONS
    print(f"\n>>>newbbtstatus: q={q}, g={g}, d={d}, sid={sid}, access={access}")
    name = 'BBTCode' if access in ('Group','CUL') else 'BBTGrp'
        
    g = g if access in ('Group','CUL') else '%'
    d = d.capitalize().replace('d','D')
    d = re.sub(r'(¹|²)d([0-9]*)',r'\1D\2',d)
    if access in ('Group','CUL'):
        grpdept = g.capitalize()
        grpdept = re.sub(r'(¹|²)g([0-9]*)',r'\1G\2',g)
    else:
        grpdept = d.replace('D[0-9]%','Youth').replace('Mw[0-9]%','MW').replace('24', '24 Dept').replace('%', 'Church')
    
    i = q[:3]
    bbtvalues = {'bbt' : ['BBT',   " AND BBTStatus IN ('BBT','Pre-BBT')"],
                 'pre' : [q.upper(), f" AND BtmNo = '{q[6:]}' AND BBTStatus = 'Pre-BBT'"],
                 'gyj' : ['GYJN BBT',  " AND UID IN (SELECT UID FROM TGWPositionCurrent WHERE PID = 30)"],
                 'btm' : [q.upper(), f" AND BtmNo = '{q[3:]}' AND BBTStatus = 'BTM'"]}
    bbttype,query = bbtvalues[i]
    
    table = f"CodeyBBTStatusMembersUBB('{sid}')"
    cols = f"Dept, Grp, {name}, pNew, pOld, pFA, FE, bbA, cct1, cct2, cctI, UBB, bbME, bbFA, Total"
    sums = "SUM(pNew)pNew, SUM(pOld)pOld, SUM(pFA)pFA, SUM(FE)FE, SUM(bbA)bbA, SUM(cct1)cct1, SUM(cct2)cct2, SUM(cctI)cctI, SUM(UBB)UBB, SUM(bbME)bbME, SUM(bbFA)bbFA, SUM(Total)Total"
    conditions = f"Dept LIKE '{d}' AND Grp LIKE '{g}'{query}".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    
    conn = odbc.connect(conn_str)
    bb_mem = f"SELECT {cols} FROM {table} WHERE {conditions} ORDER BY GID, {name}"
    bb_group = f"SELECT Grp, {sums} FROM {table} WHERE {conditions} GROUP BY Grp, GID ORDER BY GID"
    bb_dept = f"SELECT Dept, {sums} FROM {table} WHERE {conditions} GROUP BY Dept, DID ORDER BY DID"
    # bb_region = f"SELECT District, {sums} FROM {table} WHERE {conditions} GROUP BY District"
    bb_youth = f"SELECT {sums} FROM {table} WHERE {conditions}"
    
    print(bb_group)
    
    dm = pd.read_sql(bb_mem, conn)
    dg = pd.read_sql(bb_group, conn)
    dd = pd.read_sql(bb_dept, conn)
    # dr = pd.read_sql(bb_region, conn)
    dy = pd.read_sql(bb_youth, conn)

    dm.columns = ['Dept','Grp','Member','pNew','pOld','pFA','FE','bbA','cct1','cct2','cctI','UBB','bbME','bbFA','Tot']
    dg.columns = ['Grp','pNew','pOld','pFA','FE','bbA','cct1','cct2','cctI','UBB','bbME','bbFA','Tot']
    dd.columns = ['Dept','pNew','pOld','pFA','FE','bbA','cct1','cct2','cctI','UBB','bbME','bbFA','Tot']
    # dr.columns = ['Region','pNew','pOld','pFA','FE','bbA','cct1','cct2','cctI','UBB','bbME','bbFA','Tot']
    dy.columns = ['pNew','pOld','pFA','FE','bbA','cct1','cct2','cctI','UBB','bbME','bbFA','Tot']
    dd.replace(r' Dept',r'', regex = True, inplace = True)
    
    conn.cursor().close()

    member = str()
    if not d.endswith('D[0-9]%'):
        for r in range(len(dm)):
            bbt =   str(dm.loc[r,'Member'])[:5] + ' '*(5-len(str(dm.loc[r,'Member'])[:5]))
            pn  = ' '*(3-len(str(dm.loc[r,'pNew']))) + str(dm.loc[r,'pNew'])
            po  = ' '*(3-len(str(dm.loc[r,'pOld']))) + str(dm.loc[r,'pOld'])
            pf  = ' '*(3-len(str(dm.loc[r,'pFA'])))  + str(dm.loc[r,'pFA'])
            fe  = ' '*(3-len(str(dm.loc[r,'FE'])))   + str(dm.loc[r,'FE'])
            ba  = ' '*(3-len(str(dm.loc[r,'bbA'])))  + str(dm.loc[r,'bbA'])
            c1  = ' '*(3-len(str(dm.loc[r,'cct1']))) + str(dm.loc[r,'cct1'])
            c2  = ' '*(3-len(str(dm.loc[r,'cct2']))) + str(dm.loc[r,'cct2'])
            ci  = ' '*(3-len(str(dm.loc[r,'cctI']))) + str(dm.loc[r,'cctI'])
            ub  = ' '*(3-len(str(dm.loc[r,'UBB'])))  + str(dm.loc[r,'UBB'])
            bm  = ' '*(3-len(str(dm.loc[r,'bbME']))) + str(dm.loc[r,'bbME'])
            fa  = ' '*(3-len(str(dm.loc[r,'bbFA']))) + str(dm.loc[r,'bbFA'])
            t   = ' '*(3-len(str(dm.loc[r,'Tot'])))  + str(dm.loc[r,'Tot'])
            member = f'{member}{bbt}[{pn}|{po}|{pf}|{fe}|{ba}|{c1}|{c2}|{ci}|{ub}|{bm}|{fa}|{t}]\n'
        member = member + '\n'
            
    group = str()    
    for r in range(len(dg)):
        grp =   str(dg.loc[r,'Grp'])[:5] + ' '*(5-len(str(dg.loc[r,'Grp'])[:5]))
        pn  = ' '*(3-len(str(dg.loc[r,'pNew']))) + str(dg.loc[r,'pNew'])
        po  = ' '*(3-len(str(dg.loc[r,'pOld']))) + str(dg.loc[r,'pOld'])
        pf  = ' '*(3-len(str(dg.loc[r,'pFA'])))  + str(dg.loc[r,'pFA'])
        fe  = ' '*(3-len(str(dg.loc[r,'FE'])))   + str(dg.loc[r,'FE'])
        ba  = ' '*(3-len(str(dg.loc[r,'bbA'])))  + str(dg.loc[r,'bbA'])
        c1  = ' '*(3-len(str(dg.loc[r,'cct1']))) + str(dg.loc[r,'cct1'])
        c2  = ' '*(3-len(str(dg.loc[r,'cct2']))) + str(dg.loc[r,'cct2'])
        ci  = ' '*(3-len(str(dg.loc[r,'cctI']))) + str(dg.loc[r,'cctI'])
        ub  = ' '*(3-len(str(dg.loc[r,'UBB'])))  + str(dg.loc[r,'UBB'])
        bm  = ' '*(3-len(str(dg.loc[r,'bbME']))) + str(dg.loc[r,'bbME'])
        fa  = ' '*(3-len(str(dg.loc[r,'bbFA']))) + str(dg.loc[r,'bbFA'])
        t   = ' '*(3-len(str(dg.loc[r,'Tot'])))  + str(dg.loc[r,'Tot'])
        group = f'{group}{grp}[{pn}|{po}|{pf}|{fe}|{ba}|{c1}|{c2}|{ci}|{ub}|{bm}|{fa}|{t}]\n'
    group = group + '\n'
            
    dept = str()  
    if access not in ('Group','CUL'):  
        for r in range(len(dd)):
            dpt =   str(dd.loc[r,'Dept'])[:5] + ' '*(5-len(str(dd.loc[r,'Dept'])[:5]))
            pn  = ' '*(3-len(str(dd.loc[r,'pNew']))) + str(dd.loc[r,'pNew'])
            po  = ' '*(3-len(str(dd.loc[r,'pOld']))) + str(dd.loc[r,'pOld'])
            pf  = ' '*(3-len(str(dd.loc[r,'pFA'])))  + str(dd.loc[r,'pFA'])
            fe  = ' '*(3-len(str(dd.loc[r,'FE'])))   + str(dd.loc[r,'FE'])
            ba  = ' '*(3-len(str(dd.loc[r,'bbA'])))  + str(dd.loc[r,'bbA'])
            c1  = ' '*(3-len(str(dd.loc[r,'cct1']))) + str(dd.loc[r,'cct1'])
            c2  = ' '*(3-len(str(dd.loc[r,'cct2']))) + str(dd.loc[r,'cct2'])
            ci  = ' '*(3-len(str(dd.loc[r,'cctI']))) + str(dd.loc[r,'cctI'])
            ub  = ' '*(3-len(str(dd.loc[r,'UBB'])))  + str(dd.loc[r,'UBB'])
            bm  = ' '*(3-len(str(dd.loc[r,'bbME']))) + str(dd.loc[r,'bbME'])
            fa  = ' '*(3-len(str(dd.loc[r,'bbFA']))) + str(dd.loc[r,'bbFA'])
            t   = ' '*(3-len(str(dd.loc[r,'Tot'])))  + str(dd.loc[r,'Tot'])
            dept = f'{dept}{dpt}[{pn}|{po}|{pf}|{fe}|{ba}|{c1}|{c2}|{ci}|{ub}|{bm}|{fa}|{t}]\n'
        dept = dept + '\n'

    # region = str()
    # if d.endswith('D[0-9]%'):    
    #     for r in range(len(dr)):
    #         reg =   str(dr.loc[r,'Region']) + ' '*(5-len(str(dr.loc[r,'Region'])))
    #         pn  = ' '*(3-len(str(dr.loc[r,'pNew']))) + str(dr.loc[r,'pNew'])
    #         po  = ' '*(3-len(str(dr.loc[r,'pOld']))) + str(dr.loc[r,'pOld'])
    #         pf  = ' '*(3-len(str(dr.loc[r,'pFA'])))  + str(dr.loc[r,'pFA'])
    #         fe  = ' '*(3-len(str(dr.loc[r,'FE'])))   + str(dr.loc[r,'FE'])
    #         ba  = ' '*(3-len(str(dr.loc[r,'bbA'])))  + str(dr.loc[r,'bbA'])
    #         c1  = ' '*(3-len(str(dr.loc[r,'cct1']))) + str(dr.loc[r,'cct1'])
    #         c2  = ' '*(3-len(str(dr.loc[r,'cct2']))) + str(dr.loc[r,'cct2'])
    #         ci  = ' '*(3-len(str(dr.loc[r,'cctI']))) + str(dr.loc[r,'cctI'])
    #         ub  = ' '*(3-len(str(dr.loc[r,'UBB'])))  + str(dr.loc[r,'UBB'])
    #         bm  = ' '*(3-len(str(dr.loc[r,'bbME']))) + str(dr.loc[r,'bbME'])
    #         fa  = ' '*(3-len(str(dr.loc[r,'bbFA']))) + str(dr.loc[r,'bbFA'])
    #         t   = ' '*(3-len(str(dr.loc[r,'Tot'])))  + str(dr.loc[r,'Tot'])
    #         region = f'{region}{reg}[{pn}|{po}|{pf}|{fe}|{ba}|{c1}|{c2}|{ci}|{ub}|{bm}|{fa}|{t}]\n'
    #     region = region + '\n'
        
    total = str()
    if d in ('D[0-9]%','%'):
        pn  = ' '*(3-len(str(dy.loc[0,'pNew']))) + str(dy.loc[0,'pNew'])
        po  = ' '*(3-len(str(dy.loc[0,'pOld']))) + str(dy.loc[0,'pOld'])
        pf  = ' '*(3-len(str(dy.loc[0,'pFA'])))  + str(dy.loc[0,'pFA'])
        fe  = ' '*(3-len(str(dy.loc[0,'FE'])))   + str(dy.loc[0,'FE'])
        ba  = ' '*(3-len(str(dy.loc[0,'bbA'])))  + str(dy.loc[0,'bbA'])
        c1  = ' '*(3-len(str(dy.loc[0,'cct1']))) + str(dy.loc[0,'cct1'])
        c2  = ' '*(3-len(str(dy.loc[0,'cct2']))) + str(dy.loc[0,'cct2'])
        ci  = ' '*(3-len(str(dy.loc[0,'cctI']))) + str(dy.loc[0,'cctI'])
        ub  = ' '*(3-len(str(dy.loc[0,'UBB'])))  + str(dy.loc[0,'UBB'])
        bm  = ' '*(3-len(str(dy.loc[0,'bbME']))) + str(dy.loc[0,'bbME'])
        fa  = ' '*(3-len(str(dy.loc[0,'bbFA']))) + str(dy.loc[0,'bbFA'])
        t   = ' '*(3-len(str(dy.loc[0,'Tot'])))  + str(dy.loc[0,'Tot'])
        total = f'Total[{pn}|{po}|{pf}|{fe}|{ba}|{c1}|{c2}|{ci}|{ub}|{bm}|{fa}|{t}]'
    
    summary = f"<b><u>{grpdept} {bbttype} Status Summary</u></b>\n\n<pre>     [ NP| OP| FP| FE| AB| C1| C2| CI| UB| ME| FA|TOT]\n\n{member}{group}{dept}{total}</pre>"
    summary = re.sub(r'\.0',r'  ',summary) # Replaces '.0' with empty space
    summary = re.sub(r'(\D)0([^.])',r'\1-\2',summary)   # Replaces lone '0' with '-'
    print(">>>Return")
    return summary




def deptbbtstatus(q, d, r, access): # BBT FUNCTIONS
    print(f"\n>>>deptbbtstatus: q={q}, d={d}, r={r}, access={access}")
    name = 'BBT' if access == 'IT' else 'BBTCode'
    d = d.capitalize()
    d = re.sub(r'(¹|²)d([0-9]*)',r'\1D\2',d)
    
    i = q[:3]
    bbtvalues = {'bbt' : ['BBT',   " AND BBTStatus IN ('BBT','Pre-BBT')"],
                 'pre' : [q.upper(), f" AND BtmNo = '{q[6:]}' AND BBTStatus = 'Pre-BBT'"],
                 'gyj' : ['GYJN BBT',  " AND UID IN (SELECT UID FROM TGWPositionCurrent WHERE PID = 30)"],
                 'btm' : [q.upper(), f" AND BtmNo = '{q[3:]}' AND BBTStatus = 'BTM'"]}
    bbttype,query = bbtvalues[i]
    
    conn = odbc.connect(conn_str)
    bb_dept = f"SELECT Dept, SUM(pNew)pNew, SUM(pOld)pOld, SUM(bbA)bbA, SUM(cctA)cctA, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA, SUM(Total)Total FROM CodeyBBTStatusMembers('{r}') WHERE Dept LIKE '{d}'{query} Group BY Dept".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    bb_youth = f"SELECT SUM(pNew)pNew, SUM(pOld)pOld, SUM(bbA)bbA, SUM(cctA)cctA, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA, SUM(Total)Total FROM CodeyBBTStatusMembers('{r}') WHERE Dept LIKE '{d}'{query}".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    
    dd = pd.read_sql(bb_dept, conn)
    dy = pd.read_sql(bb_youth, conn)

    dd.columns = ['Dept','pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
    dy.columns = ['pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
    dd.replace(r' Dept',r'', regex = True, inplace = True)
    
    conn.cursor().close()

    dept = str()    
    for r in range(len(dd)):
        dpt =   str(dd.loc[r,'Dept'])[:3] + ' '*(3-len(str(dd.loc[r,'Dept'])))[:3]
        pn  = ' '*(3-len(str(dd.loc[r,'pNew']))) + str(dd.loc[r,'pNew'])
        po  = ' '*(3-len(str(dd.loc[r,'pOld']))) + str(dd.loc[r,'pOld'])
        ba  = ' '*(3-len(str(dd.loc[r,'bbA'])))  + str(dd.loc[r,'bbA'])
        ca  = ' '*(3-len(str(dd.loc[r,'cctA']))) + str(dd.loc[r,'cctA'])
        bm  = ' '*(3-len(str(dd.loc[r,'bbME']))) + str(dd.loc[r,'bbME'])
        ci  = ' '*(3-len(str(dd.loc[r,'cctI']))) + str(dd.loc[r,'cctI'])
        pf  = ' '*(3-len(str(dd.loc[r,'pFA'])))  + str(dd.loc[r,'pFA'])
        bf  = ' '*(3-len(str(dd.loc[r,'bbFA']))) + str(dd.loc[r,'bbFA'])
        t   = ' '*(3-len(str(dd.loc[r,'Tot'])))  + str(dd.loc[r,'Tot'])
        dept = f'{dept}{dpt}[{pn}|{po}|{ba}|{ca}|{bm}|{ci}|{pf}|{bf}|{t}]\n'
            
    if d.endswith('D[0-9]%'):
        pn  = ' '*(3-len(str(dy.loc[0,'pNew']))) + str(dy.loc[0,'pNew'])
        po  = ' '*(3-len(str(dy.loc[0,'pOld']))) + str(dy.loc[0,'pOld'])
        ba  = ' '*(3-len(str(dy.loc[0,'bbA'])))  + str(dy.loc[0,'bbA'])
        ca  = ' '*(3-len(str(dy.loc[0,'cctA']))) + str(dy.loc[0,'cctA'])
        bm  = ' '*(3-len(str(dy.loc[0,'bbME']))) + str(dy.loc[0,'bbME'])
        ci  = ' '*(3-len(str(dy.loc[0,'cctI']))) + str(dy.loc[0,'cctI'])
        pf  = ' '*(3-len(str(dy.loc[0,'pFA'])))  + str(dy.loc[0,'pFA'])
        bf  = ' '*(3-len(str(dy.loc[0,'bbFA']))) + str(dy.loc[0,'bbFA'])
        t   = ' '*(3-len(str(dy.loc[0,'Tot'])))  + str(dy.loc[0,'Tot'])
        youth = f'\nTot[{pn}|{po}|{ba}|{ca}|{bm}|{ci}|{pf}|{bf}|{t}]'

    else:
        youth = str()
    
    summary = f"<b><u>{str(d).replace('D[0-9]%','Youth')} {bbttype} Status Summary</u></b>\n\n<pre>   [ NP| OP| AB| CA| ME| CI| FP| FA|TOT]\n\n{dept}{youth}</pre>"
    summary = re.sub(r'\.0',r'  ',summary) # Replaces '.0' with empty space
    summary = re.sub(r'(\D)0([^.])',r'\1-\2',summary)   # Replaces lone '0' with '-'
    print(">>>Return")
    return summary





def bbtactive(q, g, d, r, access): # BBT FUNCTIONS
    print(f"\n>>>bbtactive: q={q}, g={g}, d={d}, r={r}, access={access}")
    name = 'BBT' if access == 'IT' else 'BBTCode2'
    g = g if access in ('Group','CUL') else '%'
    d = d.capitalize()
    d = re.sub(r'(¹|²)d([0-9]*)',r'\1D\2',d)
    if access in ('Group','CUL'):
        grpdept = g.capitalize()
        grpdept = re.sub(r'(¹|²)g([0-9]*)',r'\1G\2',g)
    else:
        grpdept = str(d).replace('D[0-9]%','Youth')
    
    i = q[:3]
    bbtvalues = {'bbt' : ['BBT',   " AND BBTStatus IN ('BBT','Pre-BBT')"],
                 'pre' : [q.upper(), f" AND BtmNo = '{q[6:]}' AND BBTStatus = 'Pre-BBT'"],
                 'gyj' : ['GYJN BBT',  " AND UID IN (SELECT UID FROM TGWPositionCurrent WHERE PID = 30)"],
                 'btm' : [q.upper(), f" AND BtmNo = '{q[3:]}' AND BBTStatus = 'BTM'"]}
    bbttype,query = bbtvalues[i]
    
    conn = odbc.connect(conn_str)
    bb_mem = f"SELECT Dept, Grp, {name}, pNew, pOld, bbA, cctA, bbME, cctI, pFA, bbFA, Total FROM CodeyBBTStatusMembers('{r}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}'{query} ORDER BY LEN(Grp), Grp, {name}".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    bb_group = f"SELECT Grp, SUM(pNew)pNew, SUM(pOld)pOld, SUM(bbA)bbA, SUM(cctA)cctA, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA, SUM(Total)Total FROM CodeyBBTStatusMembers('{r}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}'{query} Group BY Grp ORDER BY LEN(Grp), Grp".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    bb_dept = f"SELECT Dept, SUM(pNew)pNew, SUM(pOld)pOld, SUM(bbA)bbA, SUM(cctA)cctA, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA, SUM(Total)Total FROM CodeyBBTStatusMembers('{r}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}'{query} Group BY Dept".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    bb_youth = f"SELECT SUM(pNew)pNew, SUM(pOld)pOld, SUM(bbA)bbA, SUM(cctA)cctA, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA, SUM(Total)Total FROM CodeyBBTStatusMembers('{r}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}'{query}".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    
    dm = pd.read_sql(bb_mem, conn)
    dg = pd.read_sql(bb_group, conn)
    dd = pd.read_sql(bb_dept, conn)
    dy = pd.read_sql(bb_youth, conn)

    dm.columns = ['Dept','Grp','BBT','pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
    dg.columns = ['Grp','pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
    dd.columns = ['Dept','pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
    dy.columns = ['pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
    dd.replace(r' Dept',r'', regex = True, inplace = True)
    
    conn.cursor().close()

    member = str()
    if d != 'D[0-9]%':
        member = '\n'
        for r in range(len(dm)):
            bbt =   str(dm.loc[r,'BBT'])[:5] + ' '*(5-len(str(dm.loc[r,'BBT'])[:5]))
            pn  = ' '*(3-len(str(dm.loc[r,'pNew']))) + str(dm.loc[r,'pNew'])
            ba  = ' '*(3-len(str(dm.loc[r,'bbA'])))  + str(dm.loc[r,'bbA'])
            ca  = ' '*(3-len(str(dm.loc[r,'cctA']))) + str(dm.loc[r,'cctA'])
            t   = ' '*(3-len(str(dm.loc[r,'Tot'])))  + str(dm.loc[r,'Tot'])
            member = f'{member}{bbt}[{pn}|{ba}|{ca}]\n'
            
            
    group = str()
    for r in range(len(dg)):
        grp =    str(dg.loc[r,'Grp'])[:5] + ' '*(5-len(str(dg.loc[r,'Grp'])[:5]))
        pn  = ' '*(3-len(str(dg.loc[r,'pNew']))) + str(dg.loc[r,'pNew'])
        ba  = ' '*(3-len(str(dg.loc[r,'bbA'])))  + str(dg.loc[r,'bbA'])
        ca  = ' '*(3-len(str(dg.loc[r,'cctA']))) + str(dg.loc[r,'cctA'])
        group = f'{group}{grp}[{pn}|{ba}|{ca}]\n'
    
    dept = str()  
    if access not in ('Group','CUL'):  
        for r in range(len(dd)):
            dpt = str(dd.loc[r,'Dept'])[:5] + ' '*(5-len(str(dd.loc[r,'Dept'])[:5]))
            pn  = ' '*(3-len(str(dd.loc[r,'pNew']))) + str(dd.loc[r,'pNew'])
            ba  = ' '*(3-len(str(dd.loc[r,'bbA'])))  + str(dd.loc[r,'bbA'])
            ca  = ' '*(3-len(str(dd.loc[r,'cctA']))) + str(dd.loc[r,'cctA'])
            dept = f'{dept}{dpt}[{pn}|{ba}|{ca}]\n'
            
    if d.endswith('D[0-9]%'):
        pn = ' '*(3-len(str(dy.loc[0,'pNew']))) + str(dy.loc[0,'pNew'])
        ba = ' '*(3-len(str(dy.loc[0,'bbA'])))  + str(dy.loc[0,'bbA'])
        ca = ' '*(3-len(str(dy.loc[0,'cctA']))) + str(dy.loc[0,'cctA'])
        youth = f'\nTot  [{pn}|{ba}|{ca}]\n'

    else:
        youth = str()
    
    result = f"""<b><u>{grpdept} {bbttype} Active BB Status </u></b>\n\n<pre>Grp  [ NP| AB| CA]\n{member}\n{group}\n{dept}{youth}</pre>"""
    result = re.sub(r'\.0',r'  ',result) # Replaces '.0' with empty space
    result = re.sub(r'(\D)0([^.])',r'\1-\2',result)   # Replaces lone '0' with '-'
    print(">>>Return")
    return result









def deptbbtactive(q, d, r, access): # BBT FUNCTIONS
    print(f"\n>>>deptbbtactive: q={q}, d={d}, r={r}, access={access}")
    name = 'BBT' if access == 'IT' else 'BBTCode'
    d = d.capitalize()
    d = re.sub(r'(¹|²)d([0-9]*)',r'\1D\2',d)
    
    i = q if q in ['bbt','gyjnbbt'] else 'btm'
    
    i = q[:3]
    bbtvalues = {'bbt' : ['BBT',   " AND BBTStatus IN ('BBT','Pre-BBT')"],
                 'pre' : [q.upper(), f" AND BtmNo = '{q[6:]}' AND BBTStatus = 'Pre-BBT'"],
                 'gyj' : ['GYJN BBT',  " AND UID IN (SELECT UID FROM TGWPositionCurrent WHERE PID = 30)"],
                 'btm' : [q.upper(), f" AND BtmNo = '{q[3:]}' AND BBTStatus = 'BTM'"]}
    bbttype,query = bbtvalues[i]
    
    conn = odbc.connect(conn_str)
    bb_dept = f"SELECT Dept, SUM(pNew)pNew, SUM(pOld)pOld, SUM(bbA)bbA, SUM(cctA)cctA, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA, SUM(Total)Total FROM CodeyBBTStatusMembers('{r}') WHERE Dept LIKE '{d}'{query} Group BY Dept".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    bb_youth = f"SELECT SUM(pNew)pNew, SUM(pOld)pOld, SUM(bbA)bbA, SUM(cctA)cctA, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA, SUM(Total)Total FROM CodeyBBTStatusMembers('{r}') WHERE Dept LIKE '{d}'{query}".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    
    dd = pd.read_sql(bb_dept, conn)
    dy = pd.read_sql(bb_youth, conn)

    dd.columns = ['Dept','pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
    dy.columns = ['pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
    dd.replace(r' Dept',r'', regex = True, inplace = True)
    
    conn.cursor().close()
    
    dept = str()    
    for r in range(len(dd)):
        dpt = str(dd.loc[r,'Dept'])[:4] + ' '*(4-len(str(dd.loc[r,'Dept'])[:4]))
        pn  = ' '*(3-len(str(dd.loc[r,'pNew']))) + str(dd.loc[r,'pNew'])
        ba  = ' '*(3-len(str(dd.loc[r,'bbA'])))  + str(dd.loc[r,'bbA'])
        ca  = ' '*(3-len(str(dd.loc[r,'cctA']))) + str(dd.loc[r,'cctA'])
        dept = f'{dept}{dpt}[{pn}|{ba}|{ca}]\n'
            
    if d.endswith('D[0-9]%'):
        pn = ' '*(3-len(str(dy.loc[0,'pNew']))) + str(dy.loc[0,'pNew'])
        ba = ' '*(3-len(str(dy.loc[0,'bbA'])))  + str(dy.loc[0,'bbA'])
        ca = ' '*(3-len(str(dy.loc[0,'cctA']))) + str(dy.loc[0,'cctA'])
        youth = f'\nTot [{pn}|{ba}|{ca}]\n'

    else:
        youth = str()
    
    result = f"""<b><u>{str(d).replace('D[0-9]%','Youth')} {bbttype} Active BB Status </u></b>\n\n<pre>Grp [ NP| AB| CA]\n\n{dept}{youth}</pre>"""
    result = re.sub(r'\.0',r'  ',result) # Replaces '.0' with empty space
    result = re.sub(r'(\D)0([^.])',r'\1-\2',result)   # Replaces lone '0' with '-'
    print(">>>Return")
    return result









def bbtinactive(q, g, d, r, access): # BBT FUNCTIONS
    print(f"\n>>>bbtinactive: q={q}, g={g}, d={d}, r={r}, access={access}")
    name = 'BBT' if access == 'IT' else 'BBTCode2'
    g = g if access in ('Group','CUL') else '%'
    d = d.capitalize()
    d = re.sub(r'(¹|²)d([0-9]*)',r'\1D\2',d)
    if access in ('Group','CUL'):
        grpdept = g.capitalize()
        grpdept = re.sub(r'(¹|²)g([0-9]*)',r'\1G\2',g)
    else:
        grpdept = str(d).replace('D[0-9]%','Youth')
    
    i = q[:3]
    bbtvalues = {'bbt' : ['BBT',   " AND BBTStatus IN ('BBT','Pre-BBT')"],
                 'pre' : [q.upper(), f" AND BtmNo = '{q[6:]}' AND BBTStatus = 'Pre-BBT'"],
                 'gyj' : ['GYJN BBT',  " AND UID IN (SELECT UID FROM TGWPositionCurrent WHERE PID = 30)"],
                 'btm' : [q.upper(), f" AND BtmNo = '{q[3:]}' AND BBTStatus = 'BTM'"]}
    bbttype,query = bbtvalues[i]
    
    conn = odbc.connect(conn_str)
    bb_mem = f"SELECT Dept, Grp, {name}, pNew, pOld, bbA, cctA, bbME, cctI, pFA, bbFA, Total FROM CodeyBBTStatusMembers('{r}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}'{query} ORDER BY LEN(Grp), Grp, {name}".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    bb_group = f"SELECT Grp, SUM(pNew)pNew, SUM(pOld)pOld, SUM(bbA)bbA, SUM(cctA)cctA, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA, SUM(Total)Total FROM CodeyBBTStatusMembers('{r}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}'{query} Group BY Grp ORDER BY LEN(Grp), Grp".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    bb_dept = f"SELECT Dept, SUM(pNew)pNew, SUM(pOld)pOld, SUM(bbA)bbA, SUM(cctA)cctA, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA, SUM(Total)Total FROM CodeyBBTStatusMembers('{r}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}'{query} Group BY Dept".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    bb_youth = f"SELECT SUM(pNew)pNew, SUM(pOld)pOld, SUM(bbA)bbA, SUM(cctA)cctA, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA, SUM(Total)Total FROM CodeyBBTStatusMembers('{r}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}'{query}".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    
    dm = pd.read_sql(bb_mem, conn)
    dg = pd.read_sql(bb_group, conn)
    dd = pd.read_sql(bb_dept, conn)
    dy = pd.read_sql(bb_youth, conn)

    dm.columns = ['Dept','Grp','BBT','pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
    dg.columns = ['Grp','pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
    dd.columns = ['Dept','pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
    dy.columns = ['pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
    dd.replace(r' Dept',r'', regex = True, inplace = True)
    
    conn.cursor().close()

    member = str()
    if d != 'D[0-9]%':
        member = '\n'
        for r in range(len(dm)):
            bbt =   str(dm.loc[r,'BBT'])[:5] + ' '*(5-len(str(dm.loc[r,'BBT'])[:5]))
            po  = ' '*(3-len(str(dm.loc[r,'pOld']))) + str(dm.loc[r,'pOld'])
            bm  = ' '*(3-len(str(dm.loc[r,'bbME']))) + str(dm.loc[r,'bbME'])
            ci  = ' '*(3-len(str(dm.loc[r,'cctI']))) + str(dm.loc[r,'cctI'])
            pf  = ' '*(3-len(str(dm.loc[r,'pFA'])))  + str(dm.loc[r,'pFA'])
            bf  = ' '*(3-len(str(dm.loc[r,'bbFA']))) + str(dm.loc[r,'bbFA'])
            t   = ' '*(3-len(str(dm.loc[r,'Tot'])))  + str(dm.loc[r,'Tot'])
            member = f'{member}{bbt}[{po}|{bm}|{ci}|{pf}|{bf}]\n'
            
            
    group = str()
    for r in range(len(dg)):
        grp =    str(dg.loc[r,'Grp']) + ' '*(5-len(str(dg.loc[r,'Grp'])))
        po  = ' '*(3-len(str(dg.loc[r,'pOld']))) + str(dg.loc[r,'pOld'])
        bm  = ' '*(3-len(str(dg.loc[r,'bbME']))) + str(dg.loc[r,'bbME'])
        ci  = ' '*(3-len(str(dg.loc[r,'cctI']))) + str(dg.loc[r,'cctI'])
        pf  = ' '*(3-len(str(dg.loc[r,'pFA'])))  + str(dg.loc[r,'pFA'])
        bf  = ' '*(3-len(str(dg.loc[r,'bbFA']))) + str(dg.loc[r,'bbFA'])
        group = f'{group}{grp}[{po}|{bm}|{ci}|{pf}|{bf}]\n'
    
    dept = str()  
    if access not in ('Group','CUL'):    
        for r in range(len(dd)):
            dpt = str(dd.loc[r,'Dept'])   + ' '*(5-len(str(dd.loc[r,'Dept'])))
            po  = ' '*(3-len(str(dd.loc[r,'pOld']))) + str(dd.loc[r,'pOld'])
            bm  = ' '*(3-len(str(dd.loc[r,'bbME']))) + str(dd.loc[r,'bbME'])
            ci  = ' '*(3-len(str(dd.loc[r,'cctI']))) + str(dd.loc[r,'cctI'])
            pf  = ' '*(3-len(str(dd.loc[r,'pFA'])))  + str(dd.loc[r,'pFA'])
            bf  = ' '*(3-len(str(dd.loc[r,'bbFA']))) + str(dd.loc[r,'bbFA'])
            dept = f'{dept}{dpt}[{po}|{bm}|{ci}|{pf}|{bf}]\n'
            
    if d.endswith('D[0-9]%'):
        bm = ' '*(3-len(str(dy.loc[0,'bbME']))) + str(dy.loc[0,'bbME'])
        po = ' '*(3-len(str(dy.loc[0,'pOld']))) + str(dy.loc[0,'pOld'])
        ci = ' '*(3-len(str(dy.loc[0,'cctI']))) + str(dy.loc[0,'cctI'])
        pf = ' '*(3-len(str(dy.loc[0,'pFA'])))  + str(dy.loc[0,'pFA'])
        bf = ' '*(3-len(str(dy.loc[0,'bbFA']))) + str(dy.loc[0,'bbFA']) 
        youth = f'\nTot  [{po}|{bm}|{ci}|{pf}|{bf}]\n'

    else:
        youth = str()
    
    result = f"""<b><u>{grpdept} {bbttype} Inactive BB Status </u></b>\n\n<pre>Grp  [ OP| ME| CI| FP| FA]\n{member}\n{group}\n{dept}{youth}</pre>"""
    result = re.sub(r'\.0',r'  ',result) # Replaces '.0' with empty space
    result = re.sub(r'(\D)0([^.])',r'\1-\2',result)   # Replaces lone '0' with '-'
    print(">>>Return")
    return result








def deptbbtinactive(q, d, r, access): # BBT FUNCTIONS
    print(f"\n>>>deptbbtinactive: q={q}, d={d}, r={r}, access={access}")
    name = 'BBT' if access == 'IT' else 'BBTCode'
    d = d.capitalize()
    d = re.sub(r'(¹|²)d([0-9]*)',r'\1D\2',d)
    
    i = q[:3]
    bbtvalues = {'bbt' : ['BBT',   " AND BBTStatus IN ('BBT','Pre-BBT')"],
                 'pre' : [q.upper(), f" AND BtmNo = '{q[6:]}' AND BBTStatus = 'Pre-BBT'"],
                 'gyj' : ['GYJN BBT',  " AND UID IN (SELECT UID FROM TGWPositionCurrent WHERE PID = 30)"],
                 'btm' : [q.upper(), f" AND BtmNo = '{q[3:]}' AND BBTStatus = 'BTM'"]}
    bbttype,query = bbtvalues[i]
    
    conn = odbc.connect(conn_str)
    bb_dept = f"SELECT Dept, SUM(pNew)pNew, SUM(pOld)pOld, SUM(bbA)bbA, SUM(cctA)cctA, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA, SUM(Total)Total FROM CodeyBBTStatusMembers('{r}') WHERE Dept LIKE '{d}'{query} Group BY Dept".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    bb_youth = f"SELECT SUM(pNew)pNew, SUM(pOld)pOld, SUM(bbA)bbA, SUM(cctA)cctA, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA, SUM(Total)Total FROM CodeyBBTStatusMembers('{r}') WHERE Dept LIKE '{d}'{query}".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    
    dd = pd.read_sql(bb_dept, conn)
    dy = pd.read_sql(bb_youth, conn)

    dd.columns = ['Dept','pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
    dy.columns = ['pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
    dd.replace(r' Dept',r'', regex = True, inplace = True)
    
    conn.cursor().close()
    
    dept = str()    
    for r in range(len(dd)):
        dpt = str(dd.loc[r,'Dept'])   + ' '*(4-len(str(dd.loc[r,'Dept'])))
        po  = ' '*(3-len(str(dd.loc[r,'pOld']))) + str(dd.loc[r,'pOld'])
        bm  = ' '*(3-len(str(dd.loc[r,'bbME']))) + str(dd.loc[r,'bbME'])
        ci  = ' '*(3-len(str(dd.loc[r,'cctI']))) + str(dd.loc[r,'cctI'])
        pf  = ' '*(3-len(str(dd.loc[r,'pFA'])))  + str(dd.loc[r,'pFA'])
        bf  = ' '*(3-len(str(dd.loc[r,'bbFA']))) + str(dd.loc[r,'bbFA'])
        dept = f'{dept}{dpt}[{po}|{bm}|{ci}|{pf}|{bf}]\n'
            
    if d.endswith('D[0-9]%'):
        bm = ' '*(3-len(str(dy.loc[0,'bbME']))) + str(dy.loc[0,'bbME'])
        po = ' '*(3-len(str(dy.loc[0,'pOld']))) + str(dy.loc[0,'pOld'])
        ci = ' '*(3-len(str(dy.loc[0,'cctI']))) + str(dy.loc[0,'cctI'])
        pf = ' '*(3-len(str(dy.loc[0,'pFA'])))  + str(dy.loc[0,'pFA'])
        bf = ' '*(3-len(str(dy.loc[0,'bbFA']))) + str(dy.loc[0,'bbFA']) 
        youth = f'\nTot [{po}|{bm}|{ci}|{pf}|{bf}]\n'

    else:
        youth = str()
    
    result = f"""<b><u>{str(d).replace('D[0-9]%','Youth')} {bbttype} Inactive BB Status </u></b>\n\n<pre>Grp [ OP| ME| CI| FP| FA]\n\n{dept}{youth}</pre>"""
    result = re.sub(r'\.0',r'  ',result) # Replaces '.0' with empty space
    result = re.sub(r'(\D)0([^.])',r'\1-\2',result)   # Replaces lone '0' with '-'
    print(">>>Return")
    return result





def bblistold(d,g,sid,access): # BB FUNCTIONS
    print(f"\n>>>bblistold: d={d}, g={g}, sid={sid}, access={access}")
    print(">>>Return")
    return 'This function is deprecated'
    d = d.capitalize()
    g = '%' if access not in ('Group','CUL') else g
    if access in ('Group','CUL'):
        grpdept = g.capitalize()
    else:
        grpdept = str(d).replace('D[0-9]%','Youth')
    
    query = f"FROM CodeyBBList('{sid}') c LEFT JOIN TaskHigh t ON t.UID = c.BBTID WHERE (L1G LIKE '{g}' OR L2G LIKE '{g}') AND (L1D LIKE '{d}' OR L2D LIKE '{d}')"
    
    print(f"SELECT LastClass, BBTN, FruitName, L1N, L2N, LastTopic, NextClassDate, Points, DPoints {query} AND NewStatus = 'New P'    ORDER BY BBTN")
    
    conn = odbc.connect(conn_str)   

    dNP = pd.read_sql(f"SELECT LastClass, BBTN, FruitName, L1N, L2N, LastTopic, NextClassDate, Points, DPoints {query} AND NewStatus = 'New P'    ORDER BY BBTN", conn)
    dOP = pd.read_sql(f"SELECT LastClass, BBTN, FruitName, L1N, L2N, LastTopic, NextClassDate, Points, DPoints {query} AND NewStatus = 'Old P'    ORDER BY BBTN", conn)
    dAB = pd.read_sql(f"SELECT LastClass, BBTN, FruitName, L1N, L2N, LastTopic, NextClassDate, Points, DPoints {query} AND NewStatus = 'ABB'      ORDER BY BBTN", conn)
    dIM = pd.read_sql(f"SELECT LastClass, BBTN, FruitName, L1N, L2N, LastTopic, NextClassDate, Points, DPoints {query} AND NewStatus = 'IBB ME'   ORDER BY BBTN", conn)
    dIF = pd.read_sql(f"SELECT LastClass, BBTN, FruitName, L1N, L2N, LastTopic, NextClassDate, Points, DPoints {query} AND NewStatus = 'IBB FA'   ORDER BY BBTN", conn)
    dFP = pd.read_sql(f"SELECT LastClass, BBTN, FruitName, L1N, L2N, LastTopic, NextClassDate, Points, DPoints {query} AND NewStatus = 'Fallen P' ORDER BY BBTN", conn)
    dAC = pd.read_sql(f"SELECT LastClass, BBTN, FruitName, L1N, L2N, LastTopic, NextClassDate, Points, DPoints {query} AND NewStatus = 'ABB CCT'  ORDER BY BBTN", conn)
    dIC = pd.read_sql(f"SELECT LastClass, BBTN, FruitName, L1N, L2N, LastTopic, NextClassDate, Points, DPoints {query} AND NewStatus = 'IBB CCT'  ORDER BY BBTN", conn)
    dNP.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    dOP.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    dAB.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    dIM.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    dIF.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    dFP.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    dAC.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    dIC.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    conn.cursor().close()
        
    if access in ('Group','CUL'):
        pts = [dNP['Points'].sum(), dOP['Points'].sum(), dAB['Points'].sum(), dIM['Points'].sum(), dIF['Points'].sum(), dFP['Points'].sum(), dAC['Points'].sum(), dIC['Points'].sum()]
        pt = 'Points'
    elif d != 'D[0-9]%':
        pts = [dNP['DPoints'].sum(), dOP['DPoints'].sum(), dAB['DPoints'].sum(), dIM['DPoints'].sum(), dIF['DPoints'].sum(), dFP['DPoints'].sum(), dAC['DPoints'].sum(), dIC['DPoints'].sum()]
        pt = 'DPoints'
    else:
        pts = [len(dNP),len(dOP),len(dAB),len(dIM),len(dIF),len(dFP),len(dAC),len(dIC)]
        
    if len(dNP) == 0:
        np = ''
    else:
        np = f"<i><b><u>New Picking ({pts[0]} Pt)</u></b></i>\n<pre>"
        for r in range(len(dNP)):
            np = f"{np}💛{r+1}. [{dNP.loc[r,'LastClass']}] [{dNP.loc[r,pt] if d != 'D[0-9]%' else '1'}] {dNP.loc[r,'FruitName'][:8]} - {dNP.loc[r,'L1N']}{dNP.loc[r,'L2N']} - {(dNP.loc[r,'BBTN'])}\n"
        np = np + '</pre>\n'
        
    if len(dOP) == 0:
        op = ''
    else:
        op = f"<i><b><u>Old Picking ({pts[1]} Pt)</u></b></i>\n<pre>"
        for r in range(len(dOP)):
            op = f"{op}⛔️{r+1}. [{dOP.loc[r,'LastClass']}] [{dOP.loc[r,pt] if d != 'D[0-9]%' else '1'}] {dOP.loc[r,'FruitName'][:8]} - {dOP.loc[r,'L1N']}{dOP.loc[r,'L2N']} - {(dOP.loc[r,'BBTN'])}\n"
        op = op + '</pre>\n'
    
    if len(dAB) == 0:
        ab = ''
    else:
        ab = f"<i><b><u>Active BB ({pts[2]} Pt)</u></b></i>\n<pre>"
        for r in range(len(dAB)):
            ab = f"{ab}🟢{r+1}. [{dAB.loc[r,'LastClass']}] [{dAB.loc[r,pt] if d != 'D[0-9]%' else '1'}] {dAB.loc[r,'FruitName'][:8]} - {dAB.loc[r,'L1N']}{dAB.loc[r,'L2N']} - {(dAB.loc[r,'BBTN'])} - {(dAB.loc[r,'LastTopic'])} → [{(dAB.loc[r,'NextClassDate'])}]\n"
        ab = ab + '</pre>\n'
        
    if len(dIM) == 0:
        im = ''
    else:
        im = f"<i><b><u>IBB Missed Education ({pts[3]} Pt)</u></b></i>\n<pre>"
        for r in range(len(dIM)):
            im = f"{im}🔴{r+1}. [{dIM.loc[r,'LastClass']}] [{dIM.loc[r,pt] if d != 'D[0-9]%' else '1'}] {dIM.loc[r,'FruitName'][:8]} - {dIM.loc[r,'L1N']}{dIM.loc[r,'L2N']} - {(dIM.loc[r,'BBTN'])} - {(dIM.loc[r,'LastTopic'])} → [{(dIM.loc[r,'NextClassDate'])}]\n"
        im = im + '</pre>\n'
        
    if len(dIF) == 0:
        fa = ''
    else:
        fa = f"<i><b><u>IBB Fallen ({pts[4]} Pt)</u></b></i>\n<pre>"
        for r in range(len(dIF)):
            fa = f"{fa}⚫️{r+1}. [{dIF.loc[r,'LastClass']}] [{dIF.loc[r,pt] if d != 'D[0-9]%' else '1'}] {dIF.loc[r,'FruitName'][:8]} - {dIF.loc[r,'L1N']}{dIF.loc[r,'L2N']} - {(dIF.loc[r,'BBTN'])} - {(dIF.loc[r,'LastTopic'])} → [{(dIF.loc[r,'NextClassDate'])}]\n"
        fa = fa + '</pre>\n'
        
    if len(dFP) == 0:
        fp = ''
    else:
        fp = f"<i><b><u>Fallen Picking ({pts[5]} Pt)</u></b></i>\n<pre>"
        for r in range(len(dFP)):
            fp = f"{fp}❌{r+1}. [{dFP.loc[r,'LastClass']}] [{dFP.loc[r,pt] if d != 'D[0-9]%' else '1'}] {dFP.loc[r,'FruitName'][:8]} - {dFP.loc[r,'L1N']}{dFP.loc[r,'L2N']} - {(dFP.loc[r,'BBTN'])}\n"
        fp = fp + '</pre>\n'
        
    if len(dAC) == 0:
        ac = ''
    else:
        ac = f"<i><b><u>CCT ABB ({pts[6]} Pt)</u></b></i>\n<pre>"
        for r in range(len(dAC)):
            ac = f"{ac}⭐️{r+1}. [{dAC.loc[r,'LastClass']}] [{dAC.loc[r,pt] if d != 'D[0-9]%' else '1'}] {dAC.loc[r,'FruitName'][:8]} - {dAC.loc[r,'L1N']}{dAC.loc[r,'L2N']} - {(dAC.loc[r,'BBTN'])} - {(dAC.loc[r,'LastTopic'])} → [{(dAC.loc[r,'NextClassDate'])}]\n"
        ac = ac + '</pre>\n'
        
    if len(dIC) == 0:
        ic = ''
    else:
        ic = f"<i><b><u>CCT IBB ({pts[7]} Pt)</u></b></i>\n<pre>"
        for r in range(len(dIC)):
            ic = f"{ic}⭐️{r+1}. [{dIC.loc[r,'LastClass']}] [{dIC.loc[r,pt] if d != 'D[0-9]%' else '1'}] {dIC.loc[r,'FruitName'][:8]} - {dIC.loc[r,'L1N']}{dIC.loc[r,'L2N']} - {(dIC.loc[r,'BBTN'])} - {(dIC.loc[r,'LastTopic'])} → [{(dIC.loc[r,'NextClassDate'])}]\n"
        ic = ic + '</pre>\n'
    
    result = f"<b><u>📚{grpdept} BB Fruit List📚</u></b>\n\n<i>▫️Status▫️\n#. [LastClassDate] [Pts] - Fruit - L1 / L2 - BBT - LastTopic → [NextClassDate]</i>\n\n{np}{op}{ab}{im}{fa}{fp}{ac}{ic}<b><i><u>Total: {sum(pts)} Pts</u></i></b>"
    result = re.sub(r'\.0',r'',result)
    result = re.sub(r' \(\)',r'',result)
    result = re.sub(r'\((\d+)\)', r'(G\1)', result)
    result = re.sub(r'\[1\] ', r'', result)
    print(">>>Return")
    return result




def bblist(d, g, sid, access):
    print(f"\n>>>bblist: d={d}, g={g}, sid={sid}, access={access}")
    g = '%' if access not in ('Group','CUL') else g
    if access in ('Group','CUL'):
        grpdept = format_display_name(g)
    else:
        grpdept = 'Youth' if '%' in d else format_display_name(d)

    sql = f"SET NOCOUNT ON; EXEC CodeyBBList2 @sid='{sid}'"
    print(sql)
    with odbc.connect(conn_str) as conn:
        df = pd.read_sql(sql, conn)
    df.columns = ['FruitName','L1N','L1G','L1D','L2N','L2G','L2D','L1P','L2P','BBTN','BBTG','BBTD','BbtStatus','BtmNo','NewStatus','Points','DPoints','UID','BBTID','LastClass','LastTopic','NextClassDate']

    # Filter by group and dept in Python (case-insensitive)
    if g != '%':
        g_lower = g.lower()
        df = df[(df['L1G'].str.lower() == g_lower) | (df['L2G'].str.lower() == g_lower)]
    if d != '%':
        if '%' in d:
            pattern = d.replace('[0-9]', r'\d').replace('%', '.*')
            df = df[df['L1D'].str.match(pattern, case=False, na=False) | df['L2D'].str.match(pattern, case=False, na=False)]
        else:
            d_lower = d.lower()
            df = df[(df['L1D'].str.lower() == d_lower) | (df['L2D'].str.lower() == d_lower)]

    df = df[df['NewStatus'].isin(['New P','Old P','ABB','IBB ME','IBB FA','Fallen P','ABB CCT','IBB CCT'])]

    if access in ('Group','CUL'):
        pt = 'Points'
    elif d.lower() not in ('d[0-9]%', '%'):
        pt = 'DPoints'
    else:
        pt = None

    groups = {status: sub for status, sub in df.groupby('NewStatus', sort=False)}

    sections = [
        ('New P',    'New Picking',          '💛', False),
        ('Old P',    'Old Picking',          '⛔️', False),
        ('ABB',      'Active BB',            '🟢', True),
        ('IBB ME',   'IBB Missed Education', '🔴', True),
        ('IBB FA',   'IBB Fallen',           '⚫️', True),
        ('Fallen P', 'Fallen Picking',       '❌', False),
        ('ABB CCT',  'CCT ABB',              '⭐️', True),
        ('IBB CCT',  'CCT IBB',              '⭐️', True),
    ]

    parts = []
    total_pts = 0
    for status, label, emoji, show_topic in sections:
        sub = groups.get(status)
        if sub is None or len(sub) == 0:
            continue
        section_pts = len(sub) if pt is None else sub[pt].sum()
        total_pts += section_pts
        lines = [f"<i><b><u>{label} ({section_pts} Pt)</u></b></i>\n<pre>"]
        for r, (_, row) in enumerate(sub.iterrows(), 1):
            pts_display = f"[{row[pt]}] " if pt is not None else ""
            line = f"{emoji}{r}. [{row['LastClass']}] {pts_display}{row['FruitName'][:8]} - {row['L1N']}{row['L2N']} - {row['BBTN']}"
            if show_topic:
                line += f" - {row['LastTopic']} → [{row['NextClassDate']}]"
            lines.append(line)
        lines.append('</pre>\n')
        parts.append('\n'.join(lines))

    body = ''.join(parts)
    result = (
        f"<b><u>📚{grpdept} BB Fruit List📚</u></b>\n\n"
        f"<i>▫️Status▫️\n#. [LastClassDate] [Pts] - Fruit - L1 / L2 - BBT - LastTopic → [NextClassDate]</i>\n\n"
        f"{body}"
        f"<b><i><u>Total: {total_pts} Pts</u></i></b>"
    )
    result = re.sub(r'\.0', '', result)
    result = re.sub(r' \(\)', '', result)
    result = re.sub(r'\((\d+)\)', r'(G\1)', result)
    result = re.sub(r'\[1\] ', '', result)
    result = result.replace('<pre>\n','<pre>')
    print(">>>Return")
    return result



def bblistsold(d,g,physical,online,access): # BB FUNCTIONS
    print(f"\n>>>bblistsold: d={d}, g={g}, physical={physical}, online={online}, access={access}")
    print(">>>Return")
    return 'This function is deprecated'
    d = d.capitalize()
    d = re.sub(r'(¹|²)d([0-9]*)',r'\1D\2',d)
    g = '%' if access not in ('Group','CUL') else g
    if access in ('Group','CUL'):
        grpdept = g.capitalize()
        grpdept = re.sub(r'(¹|²)g([0-9]*)',r'\1G\2',g)
    else:
        grpdept = str(d).replace('D[0-9]%','Youth')

    queryP = f"FROM CodeyBBList('{physical}') c LEFT JOIN TaskHigh t ON t.UID = c.BBTID WHERE (L1G LIKE '{g}' OR L2G LIKE '{g}') AND (L1D LIKE '{d}' OR L2D LIKE '{d}')"
    queryO = f"FROM CodeyBBList('{online}') c LEFT JOIN TaskHigh t ON t.UID = c.BBTID WHERE (L1G LIKE '{g}' OR L2G LIKE '{g}') AND (L1D LIKE '{d}' OR L2D LIKE '{d}')"

    
    print(f"SELECT LastClass, BBTN, FruitName, L1N, L2N, LastTopic, NextClassDate, Points, DPoints {queryP} AND NewStatus = 'New P'    ORDER BY BBTN")
    
    conn = odbc.connect(conn_str)   

    dNP = pd.read_sql(f"SELECT LastClass, BBTN, FruitName, L1N, L2N, LastTopic, NextClassDate, Points, DPoints {queryP} AND NewStatus = 'New P'    ORDER BY BBTN", conn)
    dOP = pd.read_sql(f"SELECT LastClass, BBTN, FruitName, L1N, L2N, LastTopic, NextClassDate, Points, DPoints {queryP} AND NewStatus = 'Old P'    ORDER BY BBTN", conn)
    dAB = pd.read_sql(f"SELECT LastClass, BBTN, FruitName, L1N, L2N, LastTopic, NextClassDate, Points, DPoints {queryP} AND NewStatus = 'ABB'      ORDER BY BBTN", conn)
    dIM = pd.read_sql(f"SELECT LastClass, BBTN, FruitName, L1N, L2N, LastTopic, NextClassDate, Points, DPoints {queryP} AND NewStatus = 'IBB ME'   ORDER BY BBTN", conn)
    dIF = pd.read_sql(f"SELECT LastClass, BBTN, FruitName, L1N, L2N, LastTopic, NextClassDate, Points, DPoints {queryP} AND NewStatus = 'IBB FA'   ORDER BY BBTN", conn)
    dFP = pd.read_sql(f"SELECT LastClass, BBTN, FruitName, L1N, L2N, LastTopic, NextClassDate, Points, DPoints {queryP} AND NewStatus = 'Fallen P' ORDER BY BBTN", conn)
    dAC = pd.read_sql(f"SELECT LastClass, BBTN, FruitName, L1N, L2N, LastTopic, NextClassDate, Points, DPoints {queryP} AND NewStatus = 'ABB CCT'  ORDER BY BBTN", conn)
    dIC = pd.read_sql(f"SELECT LastClass, BBTN, FruitName, L1N, L2N, LastTopic, NextClassDate, Points, DPoints {queryP} AND NewStatus = 'IBB CCT'  ORDER BY BBTN", conn)
    oNP = pd.read_sql(f"SELECT LastClass, BBTN, FruitName, L1N, L2N, LastTopic, NextClassDate, Points, DPoints {queryO} AND NewStatus = 'New P'    ORDER BY BBTN", conn)
    oOP = pd.read_sql(f"SELECT LastClass, BBTN, FruitName, L1N, L2N, LastTopic, NextClassDate, Points, DPoints {queryO} AND NewStatus = 'Old P'    ORDER BY BBTN", conn)
    oAB = pd.read_sql(f"SELECT LastClass, BBTN, FruitName, L1N, L2N, LastTopic, NextClassDate, Points, DPoints {queryO} AND NewStatus = 'ABB'      ORDER BY BBTN", conn)
    oIM = pd.read_sql(f"SELECT LastClass, BBTN, FruitName, L1N, L2N, LastTopic, NextClassDate, Points, DPoints {queryO} AND NewStatus = 'IBB ME'   ORDER BY BBTN", conn)
    oIF = pd.read_sql(f"SELECT LastClass, BBTN, FruitName, L1N, L2N, LastTopic, NextClassDate, Points, DPoints {queryO} AND NewStatus = 'IBB FA'   ORDER BY BBTN", conn)
    oFP = pd.read_sql(f"SELECT LastClass, BBTN, FruitName, L1N, L2N, LastTopic, NextClassDate, Points, DPoints {queryO} AND NewStatus = 'Fallen P' ORDER BY BBTN", conn)
    oAC = pd.read_sql(f"SELECT LastClass, BBTN, FruitName, L1N, L2N, LastTopic, NextClassDate, Points, DPoints {queryO} AND NewStatus = 'ABB CCT'  ORDER BY BBTN", conn)
    oIC = pd.read_sql(f"SELECT LastClass, BBTN, FruitName, L1N, L2N, LastTopic, NextClassDate, Points, DPoints {queryO} AND NewStatus = 'IBB CCT'  ORDER BY BBTN", conn)
    dNP.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    dOP.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    dAB.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    dIM.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    dIF.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    dFP.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    dAC.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    dIC.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    oNP.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    oOP.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    oAB.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    oIM.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    oIF.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    oFP.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    oAC.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    oIC.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    conn.cursor().close()
        
    if access in ('Group','CUL'):
        pts = [dNP['Points'].sum(), dOP['Points'].sum(), dAB['Points'].sum(), dIM['Points'].sum(), dIF['Points'].sum(), dFP['Points'].sum(), dAC['Points'].sum(), dIC['Points'].sum()]
        opts = [oNP['Points'].sum(), oOP['Points'].sum(), oAB['Points'].sum(), oIM['Points'].sum(), oIF['Points'].sum(), oFP['Points'].sum(), oAC['Points'].sum(), oIC['Points'].sum()]
        pt = 'Points'
    elif d != 'D[0-9]%':
        pts = [dNP['DPoints'].sum(), dOP['DPoints'].sum(), dAB['DPoints'].sum(), dIM['DPoints'].sum(), dIF['DPoints'].sum(), dFP['DPoints'].sum(), dAC['DPoints'].sum(), dIC['DPoints'].sum()]
        opts = [oNP['DPoints'].sum(), oOP['DPoints'].sum(), oAB['DPoints'].sum(), oIM['DPoints'].sum(), oIF['DPoints'].sum(), oFP['DPoints'].sum(), oAC['DPoints'].sum(), oIC['DPoints'].sum()]
        pt = 'DPoints'
    else:
        pts = [len(dNP),len(dOP),len(dAB),len(dIM),len(dIF),len(dFP),len(dAC),len(dIC)]
        opts = [len(oNP),len(oOP),len(oAB),len(oIM),len(oIF),len(oFP),len(oAC),len(oIC)]
        
    if len(dNP) == 0:
        np = ''
    else:
        np = f"<i><b><u>New Picking ({pts[0]} Pt)</u></b></i>\n<pre>"
        for r in range(len(dNP)):
            np = f"{np}💛{r+1}. [{dNP.loc[r,'LastClass']}] [{dNP.loc[r,pt] if d != 'D[0-9]%' else '1'}] {dNP.loc[r,'FruitName'][:8]} - {dNP.loc[r,'L1N']}{dNP.loc[r,'L2N']} - {(dNP.loc[r,'BBTN'])}\n"
        np = np + '</pre>\n'
        
    if len(dOP) == 0:
        op = ''
    else:
        op = f"<i><b><u>Old Picking ({pts[1]} Pt)</u></b></i>\n<pre>"
        for r in range(len(dOP)):
            op = f"{op}⛔️{r+1}. [{dOP.loc[r,'LastClass']}] [{dOP.loc[r,pt] if d != 'D[0-9]%' else '1'}] {dOP.loc[r,'FruitName'][:8]} - {dOP.loc[r,'L1N']}{dOP.loc[r,'L2N']} - {(dOP.loc[r,'BBTN'])}\n"
        op = op + '</pre>\n'
    
    if len(dAB) == 0:
        ab = ''
    else:
        ab = f"<i><b><u>Active BB ({pts[2]} Pt)</u></b></i>\n<pre>"
        for r in range(len(dAB)):
            ab = f"{ab}🟢{r+1}. [{dAB.loc[r,'LastClass']}] [{dAB.loc[r,pt] if d != 'D[0-9]%' else '1'}] {dAB.loc[r,'FruitName'][:8]} - {dAB.loc[r,'L1N']}{dAB.loc[r,'L2N']} - {(dAB.loc[r,'BBTN'])} - {(dAB.loc[r,'LastTopic'])} → [{(dAB.loc[r,'NextClassDate'])}]\n"
        ab = ab + '</pre>\n'
        
    if len(dIM) == 0:
        im = ''
    else:
        im = f"<i><b><u>IBB Missed Education ({pts[3]} Pt)</u></b></i>\n<pre>"
        for r in range(len(dIM)):
            im = f"{im}🔴{r+1}. [{dIM.loc[r,'LastClass']}] [{dIM.loc[r,pt] if d != 'D[0-9]%' else '1'}] {dIM.loc[r,'FruitName'][:8]} - {dIM.loc[r,'L1N']}{dIM.loc[r,'L2N']} - {(dIM.loc[r,'BBTN'])} - {(dIM.loc[r,'LastTopic'])} → [{(dIM.loc[r,'NextClassDate'])}]\n"
        im = im + '</pre>\n'
        
    if len(dIF) == 0:
        fa = ''
    else:
        fa = f"<i><b><u>IBB Fallen ({pts[4]} Pt)</u></b></i>\n<pre>"
        for r in range(len(dIF)):
            fa = f"{fa}⚫️{r+1}. [{dIF.loc[r,'LastClass']}] [{dIF.loc[r,pt] if d != 'D[0-9]%' else '1'}] {dIF.loc[r,'FruitName'][:8]} - {dIF.loc[r,'L1N']}{dIF.loc[r,'L2N']} - {(dIF.loc[r,'BBTN'])} - {(dIF.loc[r,'LastTopic'])} → [{(dIF.loc[r,'NextClassDate'])}]\n"
        fa = fa + '</pre>\n'
        
    if len(dFP) == 0:
        fp = ''
    else:
        fp = f"<i><b><u>Fallen Picking ({pts[5]} Pt)</u></b></i>\n<pre>"
        for r in range(len(dFP)):
            fp = f"{fp}❌{r+1}. [{dFP.loc[r,'LastClass']}] [{dFP.loc[r,pt] if d != 'D[0-9]%' else '1'}] {dFP.loc[r,'FruitName'][:8]} - {dFP.loc[r,'L1N']}{dFP.loc[r,'L2N']} - {(dFP.loc[r,'BBTN'])}\n"
        fp = fp + '</pre>\n'
        
    if len(dAC) == 0:
        ac = ''
    else:
        ac = f"<i><b><u>CCT ABB ({pts[6]} Pt)</u></b></i>\n<pre>"
        for r in range(len(dAC)):
            ac = f"{ac}⭐️{r+1}. [{dAC.loc[r,'LastClass']}] [{dAC.loc[r,pt] if d != 'D[0-9]%' else '1'}] {dAC.loc[r,'FruitName'][:8]} - {dAC.loc[r,'L1N']}{dAC.loc[r,'L2N']} - {(dAC.loc[r,'BBTN'])} - {(dAC.loc[r,'LastTopic'])} → [{(dAC.loc[r,'NextClassDate'])}]\n"
        ac = ac + '</pre>\n'
        
    if len(dIC) == 0:
        ic = ''
    else:
        ic = f"<i><b><u>CCT IBB ({pts[7]} Pt)</u></b></i>\n<pre>"
        for r in range(len(dIC)):
            ic = f"{ic}⭐️{r+1}. [{dIC.loc[r,'LastClass']}] [{dIC.loc[r,pt] if d != 'D[0-9]%' else '1'}] {dIC.loc[r,'FruitName'][:8]} - {dIC.loc[r,'L1N']}{dIC.loc[r,'L2N']} - {(dIC.loc[r,'BBTN'])} - {(dIC.loc[r,'LastTopic'])} → [{(dIC.loc[r,'NextClassDate'])}]\n"
        ic = ic + '</pre>\n'

    # ^^^ Physical ^^^
    # -----------------
    # vvv  Online  vvv

    npo = opo = abo = imo = fao = fpo = aco = ico = ''
    c = 0

    if len(oNP) > 0:
        for r in range(len(oNP)):
            c += 1
            npo = f"{npo}💛{c}. [{oNP.loc[r,'LastClass']}] [{oNP.loc[r,pt] if d != 'D[0-9]%' else '1'}] {oNP.loc[r,'FruitName'][:8]} - {oNP.loc[r,'L1N']}{oNP.loc[r,'L2N']} - {(oNP.loc[r,'BBTN'])}\n"
    if len(oOP) > 0:
        for r in range(len(oOP)):
            c += 1
            opo = f"{opo}⛔️{c}. [{oOP.loc[r,'LastClass']}] [{oOP.loc[r,pt] if d != 'D[0-9]%' else '1'}] {oOP.loc[r,'FruitName'][:8]} - {oOP.loc[r,'L1N']}{oOP.loc[r,'L2N']} - {(oOP.loc[r,'BBTN'])}\n"
    if len(oAB) > 0:
        for r in range(len(oAB)):
            c += 1
            abo = f"{abo}🟢{c}. [{oAB.loc[r,'LastClass']}] [{oAB.loc[r,pt] if d != 'D[0-9]%' else '1'}] {oAB.loc[r,'FruitName'][:8]} - {oAB.loc[r,'L1N']}{oAB.loc[r,'L2N']} - {(oAB.loc[r,'BBTN'])} - {(oAB.loc[r,'LastTopic'])} → [{(oAB.loc[r,'NextClassDate'])}]\n"
    if len(oIM) > 0:
        for r in range(len(oIM)):
            c += 1
            imo = f"{imo}🔴{c}. [{oIM.loc[r,'LastClass']}] [{oIM.loc[r,pt] if d != 'D[0-9]%' else '1'}] {oIM.loc[r,'FruitName'][:8]} - {oIM.loc[r,'L1N']}{oIM.loc[r,'L2N']} - {(oIM.loc[r,'BBTN'])} - {(oIM.loc[r,'LastTopic'])} → [{(oIM.loc[r,'NextClassDate'])}]\n"
    if len(oIF) > 0:
        for r in range(len(oIF)):
            c += 1
            fao = f"{fao}⚫️{c}. [{oIF.loc[r,'LastClass']}] [{oIF.loc[r,pt] if d != 'D[0-9]%' else '1'}] {oIF.loc[r,'FruitName'][:8]} - {oIF.loc[r,'L1N']}{oIF.loc[r,'L2N']} - {(oIF.loc[r,'BBTN'])} - {(oIF.loc[r,'LastTopic'])} → [{(oIF.loc[r,'NextClassDate'])}]\n"
    if len(oFP) > 0:
        for r in range(len(oFP)):
            c += 1
            fpo = f"{fpo}❌{c}. [{oFP.loc[r,'LastClass']}] [{oFP.loc[r,pt] if d != 'D[0-9]%' else '1'}] {oFP.loc[r,'FruitName'][:8]} - {oFP.loc[r,'L1N']}{oFP.loc[r,'L2N']} - {(oFP.loc[r,'BBTN'])}\n"   
    if len(oAC) > 0:
        for r in range(len(oAC)):
            c += 1
            aco = f"{aco}⭐️{c}. [{oAC.loc[r,'LastClass']}] [{oAC.loc[r,pt] if d != 'D[0-9]%' else '1'}] {oAC.loc[r,'FruitName'][:8]} - {oAC.loc[r,'L1N']}{oAC.loc[r,'L2N']} - {(oAC.loc[r,'BBTN'])} - {(oAC.loc[r,'LastTopic'])} → [{(oAC.loc[r,'NextClassDate'])}]\n"
    if len(oIC) > 0:
        for r in range(len(oIC)):
            c += 1
            ico = f"{ico}⭐️{c}. [{oIC.loc[r,'LastClass']}] [{oIC.loc[r,pt] if d != 'D[0-9]%' else '1'}] {oIC.loc[r,'FruitName'][:8]} - {oIC.loc[r,'L1N']}{oIC.loc[r,'L2N']} - {(oIC.loc[r,'BBTN'])} - {(oIC.loc[r,'LastTopic'])} → [{(oIC.loc[r,'NextClassDate'])}]\n"
    
    physical = 'Total' if sum(opts) == 0 else 'Physical'
    online = '' if sum(opts) == 0 else f"\n\n<i><b><u>Online ({sum(opts)} Pt)</u></b></i>\n<pre>{npo}{opo}{abo}{imo}{fao}{fpo}{aco}{ico}</pre>"

    result = f"<b><u>📚{grpdept} BB Fruit List📚</u></b>\n\n<i>▫️Status▫️\n#. [LastClassDate] [Pts] - Fruit - L1 / L2 - BBT - LastTopic → [NextClassDate]</i>\n\n{np}{op}{ab}{im}{fa}{fp}{ac}{ic}<b><i><u>{physical}: {sum(pts)} Pts</u></i></b>{online}"
    result = re.sub(r'\.0',r'',result)
    result = re.sub(r' \(\)',r'',result)
    result = re.sub(r'\((\d+)\)', r'(G\1)', result)
    result = re.sub(r'\[1\] ', r'', result)
    result = re.sub(r'\n<b><i><u>Physical',r'<b><i><u>Physical',result)
    print(">>>Return")
    return result



def bblists(d, g, physical, online, access):
    print(f"\n>>>bblists: d={d}, g={g}, physical={physical}, online={online}, access={access}")
    d = d.capitalize()
    d = re.sub(r'(¹|²)d([0-9]*)', r'\1D\2', d)
    g = '%' if access not in ('Group','CUL') else g
    if access in ('Group','CUL'):
        grpdept = g.capitalize()
        grpdept = re.sub(r'(¹|²)g([0-9]*)', r'\1G\2', g)
    else:
        grpdept = str(d).replace('D[0-9]%', 'Youth')

    conn = odbc.connect(conn_str)
    dfP = pd.read_sql(f"SET NOCOUNT ON; EXEC CodeyBBList2 @sid='{physical}'", conn)
    dfO = pd.read_sql(f"SET NOCOUNT ON; EXEC CodeyBBList2 @sid='{online}'", conn)
    conn.close()

    cols = ['FruitName','L1N','L1G','L1D','L2N','L2G','L2D','L1P','L2P','BBTN','BBTG','BBTD','BbtStatus','BtmNo','NewStatus','Points','DPoints','UID','BBTID','LastClass','LastTopic','NextClassDate']
    dfP.columns = cols
    dfO.columns = cols

    # Filter by group and dept in Python (case-insensitive)
    if g != '%':
        g_lower = g.lower()
        dfP = dfP[(dfP['L1G'].str.lower() == g_lower) | (dfP['L2G'].str.lower() == g_lower)]
        dfO = dfO[(dfO['L1G'].str.lower() == g_lower) | (dfO['L2G'].str.lower() == g_lower)]
    if d != '%':
        if '%' in d:
            pattern = d.replace('[0-9]', r'\d').replace('%', '.*')
            dfP = dfP[dfP['L1D'].str.match(pattern, case=False, na=False) | dfP['L2D'].str.match(pattern, case=False, na=False)]
            dfO = dfO[dfO['L1D'].str.match(pattern, case=False, na=False) | dfO['L2D'].str.match(pattern, case=False, na=False)]
        else:
            d_lower = d.lower()
            dfP = dfP[(dfP['L1D'].str.lower() == d_lower) | (dfP['L2D'].str.lower() == d_lower)]
            dfO = dfO[(dfO['L1D'].str.lower() == d_lower) | (dfO['L2D'].str.lower() == d_lower)]

    dfP = dfP[dfP['NewStatus'].isin(['New P','Old P','ABB','IBB ME','IBB FA','Fallen P','ABB CCT','IBB CCT'])]
    dfO = dfO[dfO   ['NewStatus'].isin(['New P','Old P','ABB','IBB ME','IBB FA','Fallen P','ABB CCT','IBB CCT'])]

    if access in ('Group','CUL'):
        pt = 'Points'
    elif d.lower() not in ('d[0-9]%', '%'):
        pt = 'DPoints'
    else:
        pt = None

    sections = [
        ('New P',    'New Picking',          '💛', False),
        ('Old P',    'Old Picking',          '⛔️', False),
        ('ABB',      'Active BB',            '🟢', True),
        ('IBB ME',   'IBB Missed Education', '🔴', True),
        ('IBB FA',   'IBB Fallen',           '⚫️', True),
        ('Fallen P', 'Fallen Picking',       '❌', False),
        ('ABB CCT',  'CCT ABB',              '⭐️', True),
        ('IBB CCT',  'CCT IBB',              '⭐️', True),
    ]

    def fmt_row(num, row, emoji, show_topic):
        print(f"\n>>>fmt_row: num={num}, emoji={emoji}, show_topic={show_topic}")
        pts_display = f"[{row[pt]}] " if pt is not None else ""
        line = f"{emoji}{num}. [{row['LastClass']}] {pts_display}{row['FruitName'][:8]} - {row['L1N']}{row['L2N']} - {row['BBTN']}"
        if show_topic:
            line += f" - {row['LastTopic']} → [{row['NextClassDate']}]"
        print(">>>Return")
        return line

    # --- Physical sections ---
    groupsP = {s: sub for s, sub in dfP.groupby('NewStatus', sort=False)}
    parts = []
    total_phys = 0
    for status, label, emoji, show_topic in sections:
        sub = groupsP.get(status)
        if sub is None or len(sub) == 0:
            continue
        section_pts = len(sub) if pt is None else sub[pt].sum()
        total_phys += section_pts
        lines = [f"<i><b><u>{label} ({section_pts} Pt)</u></b></i>\n<pre>"]
        for r, (_, row) in enumerate(sub.iterrows(), 1):
            lines.append(fmt_row(r, row, emoji, show_topic))
        lines.append('</pre>\n')
        parts.append('\n'.join(lines))
    phys_body = ''.join(parts)

    # --- Online section ---
    groupsO = {s: sub for s, sub in dfO.groupby('NewStatus', sort=False)}
    online_lines = []
    total_online = 0
    c = 0
    for status, _, emoji, show_topic in sections:
        sub = groupsO.get(status)
        if sub is None or len(sub) == 0:
            continue
        total_online += len(sub) if pt is None else sub[pt].sum()
        for _, row in sub.iterrows():
            c += 1
            online_lines.append(fmt_row(c, row, emoji, show_topic))

    if total_online == 0:
        phys_label = 'Total'
        online_section = ''
    else:
        phys_label = 'Physical'
        online_section = f"\n\n<i><b><u>Online ({total_online} Pt)</u></b></i>\n<pre>{''.join(line + chr(10) for line in online_lines)}</pre>"

    result = (
        f"<b><u>📚{grpdept} BB Fruit List📚</u></b>\n\n"
        f"<i>▫️Status▫️\n#. [LastClassDate] [Pts] - Fruit - L1 / L2 - BBT - LastTopic → [NextClassDate]</i>\n\n"
        f"{phys_body}"
        f"<b><i><u>{phys_label}: {total_phys} Pts</u></i></b>{online_section}"
    )
    result = re.sub(r'\.0', '', result)
    result = re.sub(r' \(\)', '', result)
    result = re.sub(r'\((\d+)\)', r'(G\1)', result)
    result = re.sub(r'\[1\] ', '', result)
    result = re.sub(r'\n<b><i><u>Physical', r'<b><i><u>Physical', result)
    result = result.replace('<pre>\n', '<pre>')
    print(">>>Return")
    return result



def bbtlistold(q,d,g,sid,access): # BBT FUNCTIONS
    print(f"\n>>>bbtlistold: q={q}, d={d}, g={g}, sid={sid}, access={access}")
    print(">>>Return")
    return 'This function is deprecated'
    d = d.capitalize()
    d = re.sub(r'(¹|²)d([0-9]*)',r'\1D\2',d)

    i = q[:3]
    bbtvalues = {'bbt' : ['BBT',   " AND BBTStatus IN ('BBT','Pre-BBT')"],
                 'pre' : [q.upper(), f" AND BtmNo = '{q[6:]}' AND BBTStatus = 'Pre-BBT'"],
                 'gyj' : ['GYJN BBT',  " AND UID IN (SELECT UID FROM TGWPositionCurrent WHERE PID = 30)"],
                 'btm' : [q.upper(), f" AND BtmNo = '{q[3:]}' AND BBTStatus = 'BTM'"]}
    bbttype,query = bbtvalues[i]

    g = '%' if access not in ('Group','CUL') else g
    if access in ('Group','CUL'):
        grpdept = g.capitalize()
        grpdept = re.sub(r'(¹|²)g([0-9]*)',r'\1G\2',g)
    else:
        grpdept = str(d).replace('D[0-9]%','Youth')
    
    columns = "LastClass, BBTN, FruitName, ISNULL(L1N,'NULL')L1N, L2N, LastTopic, NextClassDate"
    grp_dept_filter = f"BBTG LIKE '{g}' AND BBTD LIKE '{d}'{query} ORDER BY BBTN"
    
    print(f"SELECT {columns} FROM CodeyBBList('{sid}') c WHERE NewStatus = 'New P' AND {grp_dept_filter}")
    
    conn = odbc.connect(conn_str)   

    dNP = pd.read_sql(f"SELECT {columns} FROM CodeyBBList('{sid}') c WHERE NewStatus = 'New P'    AND {grp_dept_filter}", conn)
    dOP = pd.read_sql(f"SELECT {columns} FROM CodeyBBList('{sid}') c WHERE NewStatus = 'Old P'    AND {grp_dept_filter}", conn)
    dAB = pd.read_sql(f"SELECT {columns} FROM CodeyBBList('{sid}') c WHERE NewStatus = 'ABB'      AND {grp_dept_filter}", conn)
    dIM = pd.read_sql(f"SELECT {columns} FROM CodeyBBList('{sid}') c WHERE NewStatus = 'IBB ME'   AND {grp_dept_filter}", conn)
    dIF = pd.read_sql(f"SELECT {columns} FROM CodeyBBList('{sid}') c WHERE NewStatus = 'IBB FA'   AND {grp_dept_filter}", conn)
    dFP = pd.read_sql(f"SELECT {columns} FROM CodeyBBList('{sid}') c WHERE NewStatus = 'Fallen P' AND {grp_dept_filter}", conn)
    dAC = pd.read_sql(f"SELECT {columns} FROM CodeyBBList('{sid}') c WHERE NewStatus = 'ABB CCT'  AND {grp_dept_filter}", conn)
    dIC = pd.read_sql(f"SELECT {columns} FROM CodeyBBList('{sid}') c WHERE NewStatus = 'IBB CCT'  AND {grp_dept_filter}", conn)
    dNP.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate']
    dOP.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate']
    dAB.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate']
    dIM.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate']
    dIF.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate']
    dFP.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate']
    dAC.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate']
    dIC.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate']
    conn.cursor().close()

    if len(dNP) == 0:
        np = ''
    else:
        np = f"<i><b><u>New Picking ({len(dNP)} Pt)</u></b></i>\n<pre>"
        for r in range(len(dNP)):
            np = f"{np}💛{r+1}. [{dNP.loc[r,'LastClass']}] {(dNP.loc[r,'BBTN'])[:8]} - {dNP.loc[r,'FruitName'][:8]} - {dNP.loc[r,'L1N'][:8]}{dNP.loc[r,'L2N'][:11]}\n"
        np = np + '</pre>\n'
        
    if len(dOP) == 0:
        op = ''
    else:
        op = f"<i><b><u>Old Picking ({len(dOP)} Pt)</u></b></i>\n<pre>"
        for r in range(len(dOP)):
            op = f"{op}⛔️{r+1}. [{dOP.loc[r,'LastClass']}] {(dOP.loc[r,'BBTN'])[:8]} - {dOP.loc[r,'FruitName'][:8]} - {dOP.loc[r,'L1N'][:8]}{dOP.loc[r,'L2N'][:11]}\n"
        op = op + '</pre>\n'
    
    if len(dAB) == 0:
        ab = ''
    else:
        ab = f"<i><b><u>Active BB ({len(dAB)} Pt)</u></b></i>\n<pre>"
        for r in range(len(dAB)):
            ab = f"{ab}🟢{r+1}. [{dAB.loc[r,'LastClass']}] {(dAB.loc[r,'BBTN'])[:8]} - {dAB.loc[r,'FruitName'][:8]} - {dAB.loc[r,'L1N'][:8]}{dAB.loc[r,'L2N'][:11]} - {(dAB.loc[r,'LastTopic'])} → [{(dAB.loc[r,'NextClassDate'])}]\n"
        ab = ab + '</pre>\n'
        
    if len(dIM) == 0:
        im = ''
    else:
        im = f"<i><b><u>IBB Missed Education ({len(dIM)} Pt)</u></b></i>\n<pre>"
        for r in range(len(dIM)):
            im = f"{im}🔴{r+1}. [{dIM.loc[r,'LastClass']}] {(dIM.loc[r,'BBTN'])[:8]} - {dIM.loc[r,'FruitName'][:8]} - {dIM.loc[r,'L1N'][:8]}{dIM.loc[r,'L2N'][:11]} - {(dIM.loc[r,'LastTopic'])} → [{(dIM.loc[r,'NextClassDate'])}]\n"
        im = im + '</pre>\n'
        
    if len(dIF) == 0:
        fa = ''
    else:
        fa = f"<i><b><u>IBB Fallen ({len(dIF)} Pt)</u></b></i>\n<pre>"
        for r in range(len(dIF)):
            fa = f"{fa}⚫️{r+1}. [{dIF.loc[r,'LastClass']}] {(dIF.loc[r,'BBTN'])[:8]} - {dIF.loc[r,'FruitName'][:8]} - {dIF.loc[r,'L1N'][:8]}{dIF.loc[r,'L2N'][:11]} - {(dIF.loc[r,'LastTopic'])} → [{(dIF.loc[r,'NextClassDate'])}]\n"
        fa = fa + '</pre>\n'
        
    if len(dFP) == 0:
        fp = ''
    else:
        fp = f"<i><b><u>Fallen Picking ({len(dFP)} Pt)</u></b></i>\n<pre>"
        for r in range(len(dFP)):
            fp = f"{fp}❌{r+1}. [{dFP.loc[r,'LastClass']}] {(dFP.loc[r,'BBTN'])[:8]} - {dFP.loc[r,'FruitName'][:8]} - {dFP.loc[r,'L1N'][:8]}{dFP.loc[r,'L2N'][:11]}\n"
        fp = fp + '</pre>\n'
        
    if len(dAC) == 0:
        ac = ''
    else:
        ac = f"<i><b><u>CCT ABB ({len(dAC)} Pt)</u></b></i>\n<pre>"
        for r in range(len(dAC)):
            ac = f"{ac}⭐️{r+1}. [{dAC.loc[r,'LastClass']}] {(dAC.loc[r,'BBTN'])[:8]} - {dAC.loc[r,'FruitName'][:8]} - {dAC.loc[r,'L1N'][:8]}{dAC.loc[r,'L2N'][:11]} - {(dAC.loc[r,'LastTopic'])} → [{(dAC.loc[r,'NextClassDate'])}]\n"
        ac = ac + '</pre>\n'
        
    if len(dIC) == 0:
        ic = ''
    else:
        ic = f"<i><b><u>CCT IBB ({len(dIC)} Pt)</u></b></i>\n<pre>"
        for r in range(len(dIC)):
            ic = f"{ic}⭐️{r+1}. [{dIC.loc[r,'LastClass']}] {(dIC.loc[r,'BBTN'])[:8]} - {dIC.loc[r,'FruitName'][:8]} - {dIC.loc[r,'L1N'][:8]}{dIC.loc[r,'L2N'][:11]} - {(dIC.loc[r,'LastTopic'])} → [{(dIC.loc[r,'NextClassDate'])}]\n"
        ic = ic + '</pre>\n'
    
    result = f"<b><u>📖{grpdept} {bbttype} Student List📖</u></b>\n\n<i>▫️Status▫️\n#. [LastClassDate] BBT - Student - Leaf1 / Leaf2 - LastTopic → [NextClassDate]</i>\n\n{np}{op}{ab}{im}{fa}{fp}{ac}{ic}<b><i><u>Total: {sum([len(dNP),len(dOP),len(dAB),len(dIM),len(dIF),len(dFP),len(dAC),len(dIC)])} Pts</u></i></b>"
    result = re.sub(r'\.0',r'',result)
    result = re.sub(r' \(\)',r'',result)
    result = re.sub(r'\((\d+)\)', r'(G\1)', result)
    print(">>>Return")
    return result


def bbtlist(q, d, g, sid, access): # BBT FUNCTIONS
    print(f"\n>>>bbtlist: q={q}, d={d}, g={g}, sid={sid}, access={access}")
    d = d.capitalize()
    i = q[:3]

    # Build SP parameters
    params = {'sid': sid, 'bbtg': '%', 'bbtd': '%', 'bbtstatus': None, 'btmno': None, 'gyjfilter': 0}


    # the following commented-out code is from bbtstatus function but not compatible with this one as it uses stored procedure. Need to find way
    # to properly remove btm number filter when no btm number is provided
    # Currently, it sets btmno to None when no btm number is provided, which is handled in the SQL query by passing NULL to the stored procedure
    # But it doesn't seem to work

    # prebbtfilt = f" AND BtmNo = '{q[6:]}'" if q[6:] != '' else ''
    # btmfilt = f" AND BtmNo = '{q[3:]}'" if q[3:] != '' else ''

    # i = q[:3]
    # bbtvalues = {'bbt' : ['BBT',   " AND BBTStatus IN ('BBT','Pre-BBT')"],
    #              'pre' : [q.upper(), f"{prebbtfilt} AND BBTStatus = 'Pre-BBT'"],
    #              'gyj' : ['GYJN BBT',  " AND UID IN (SELECT UID FROM TGWPositionCurrent WHERE PID = 30)"],
    #              'btm' : [q.upper(), f"{btmfilt} AND BBTStatus = 'BTM'"]}
    # bbttype,query = bbtvalues[i]

    if i == 'bbt':
        bbttype = 'BBT'
        params['bbtstatus'] = 'BBT'
    elif i == 'pre':
        bbttype = q.upper()
        params['btmno'] = q[6:]
        params['bbtstatus'] = 'Pre-BBT'
    elif i == 'gyj':
        bbttype = 'GYJN BBT'
        params['gyjfilter'] = 1
    elif i == 'btm':
        bbttype = q.upper()
        params['btmno'] = q[3:]

    g = '%' if access not in ('Group','CUL') else g
    params['bbtg'] = g
    params['bbtd'] = d

    if access in ('Group','CUL'):
        grpdept = g.capitalize()
    else:
        grpdept = str(d).replace('D[0-9]%', 'Youth')

    sql = (
        f"EXEC CodeyBBTList2 @sid='{params['sid']}', @bbtg='{params['bbtg']}', "
        f"@bbtd='{params['bbtd']}', "
        f"@bbtstatus={'NULL' if params['bbtstatus'] is None else chr(39)+params['bbtstatus']+chr(39)}, "
        f"@btmno={'NULL' if params['btmno'] is None else chr(39)+params['btmno']+chr(39)}, "
        f"@gyjfilter={params['gyjfilter']}"
        )

    print(sql)

    with odbc.connect(conn_str) as conn:
        df = pd.read_sql(sql,conn)

    df.columns = ['FruitName','L1N','L1G','L1D','L2N','L2G','L2D','L1P','L2P','BBTN','BBTG','BBTD','BbtStatus','BtmNo','NewStatus','Points','DPoints','UID','BBTID','LastClass','LastTopic','NextClassDate']

    df = df[df['NewStatus'].isin(['New P','Old P','ABB','IBB ME','IBB FA','Fallen P','ABB CCT','IBB CCT'])]

    # Split into groups via a dict
    groups = {status: sub for status, sub in df.groupby('NewStatus', sort=False)}

    # Config: (status_key, label, emoji, show_topic)
    sections = [
        ('New P',    'New Picking',          '💛', False),
        ('Old P',    'Old Picking',          '⛔️', False),
        ('ABB',      'Active BB',            '🟢', True),
        ('IBB ME',   'IBB Missed Education', '🔴', True),
        ('IBB FA',   'IBB Fallen',           '⚫️', True),
        ('Fallen P', 'Fallen Picking',       '❌', False),
        ('ABB CCT',  'CCT ABB',              '⭐️', True),
        ('IBB CCT',  'CCT IBB',              '⭐️', True),
    ]

    parts = []
    total = 0
    for status, label, emoji, show_topic in sections:
        sub = groups.get(status)
        if sub is None or len(sub) == 0:
            continue
        total += len(sub)
        lines = [f"<i><b><u>{label} ({len(sub)} Pt)</u></b></i>\n<pre>"] 
        for r, (_, row) in enumerate(sub.iterrows(), 1):
            line = f"{emoji}{r}. [{row['LastClass']}] {row['BBTN'][:8]} - {row['FruitName'][:8]} - {row['L1N'][:8]}{row['L2N'][:11]}"
            if show_topic:
                line += f" - {row['LastTopic']} → [{row['NextClassDate']}]"
            lines.append(line)
        lines.append('</pre>\n')
        parts.append('\n'.join(lines))

    body = ''.join(parts)
    result = (
        f"<b><u>📖{grpdept} {bbttype} Student List📖</u></b>\n\n"
        f"<i>▫️Status▫️\n#. [LastClassDate] BBT - Student - Leaf1 / Leaf2 - LastTopic → [NextClassDate]</i>\n\n"
        f"{body}"
        f"<b><i><u>Total: {total} Pts</u></i></b>"
    )
    result = re.sub(r'\.0', '', result)
    result = re.sub(r' \(\)', '', result)
    result = re.sub(r'\((\d+)\)', r'(G\1)', result)
    result = result.replace('<pre>\n','<pre>')
    print(">>>Return")
    return result






def bblistfe(d,g,sid,access): # BB FUNCTIONS
    print(f"\n>>>bblistfe: d={d}, g={g}, sid={sid}, access={access}")
    print(">>>Return")
    return 'This function is deprecated'
    d = d.capitalize()
    g = '%' if access not in ('Group','CUL') else g
    if access in ('Group','CUL'):
        grpdept = g.capitalize()
    else:
        grpdept = str(d).replace('D[0-9]%','Youth')
    
    cols = "LastClass, BBTN, FruitName, L1N, L2N, LastTopic, NextClassDate, Points, DPoints"
    view = f"CodeyBBListUBB('{sid}') c LEFT JOIN TaskHigh t ON t.UID = c.BBTID"
    conditions = f"(L1G LIKE '{g}' OR L2G LIKE '{g}') AND (L1D LIKE '{d}' OR L2D LIKE '{d}')"
    q1 = f"SELECT {cols} FROM {view} WHERE {conditions} AND NewStatus = '"
    q2 = "' ORDER BY BBTN"
        
    conn = odbc.connect(conn_str)   

    dPN = pd.read_sql(f"{q1}pNew{q2}", conn)
    dPO = pd.read_sql(f"{q1}pOld{q2}", conn)
    dPF = pd.read_sql(f"{q1}pFA{q2}" , conn)
    dFE = pd.read_sql(f"{q1}FE{q2}"  , conn)
    dBA = pd.read_sql(f"{q1}bbA{q2}" , conn)
    dC1 = pd.read_sql(f"{q1}cct1{q2}", conn)
    dC2 = pd.read_sql(f"{q1}cct2{q2}", conn)
    dCI = pd.read_sql(f"{q1}cctI{q2}", conn)
    dUB = pd.read_sql(f"{q1}UBB{q2}" , conn)
    dME = pd.read_sql(f"{q1}bbME{q2}", conn)
    dFA = pd.read_sql(f"{q1}bbFA{q2}", conn)
    
    dPN.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    dPO.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    dPF.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    dFE.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    dBA.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    dC1.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    dC2.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    dCI.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    dUB.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    dME.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    dFA.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    conn.cursor().close()
        
    if access in ('Group','CUL'):
        pts = [dPN['Points'].sum(), dPO['Points'].sum(), dPF['Points'].sum(), dFE['Points'].sum(), dBA['Points'].sum(), dC1['Points'].sum(), dC2['Points'].sum(), dCI['Points'].sum(), dUB['Points'].sum(), dME['Points'].sum(), dFA['Points'].sum()]
        pt = 'Points'
    elif d != 'D[0-9]%':
        pts = [dPN['DPoints'].sum(), dPO['DPoints'].sum(), dPF['DPoints'].sum(), dFE['DPoints'].sum(), dBA['DPoints'].sum(), dC1['DPoints'].sum(), dC2['DPoints'].sum(), dCI['DPoints'].sum(), dUB['DPoints'].sum(), dME['DPoints'].sum(), dFA['DPoints'].sum()]
        pt = 'DPoints'
    else:
        pts = [len(dPN),len(dPO),len(dPF),len(dFE),len(dBA),len(dC1),len(dC2),len(dCI),len(dUB),len(dME),len(dFA)]
        
        
    if len(dPN) == 0:
        pn = ''
    else:
        pn = f"<i><b><u>New Picking ({pts[0]} Pt)</u></b></i>\n<pre>"
        for r in range(len(dPN)):
            pn = f"{pn}💛{r+1}. [{dPN.loc[r,'LastClass']}] [{dPN.loc[r,pt] if d != 'D[0-9]%' else '1'}] {dPN.loc[r,'FruitName'][:8]} - {dPN.loc[r,'L1N']}{dPN.loc[r,'L2N']} - {(dPN.loc[r,'BBTN'])}\n"
        pn = pn + '</pre>\n'
        
        
    if len(dPO) == 0:
        po = ''
    else:
        po = f"<i><b><u>Old Picking ({pts[1]} Pt)</u></b></i>\n<pre>"
        for r in range(len(dPO)):
            po = f"{po}⛔️{r+1}. [{dPO.loc[r,'LastClass']}] [{dPO.loc[r,pt] if d != 'D[0-9]%' else '1'}] {dPO.loc[r,'FruitName'][:8]} - {dPO.loc[r,'L1N']}{dPO.loc[r,'L2N']} - {(dPO.loc[r,'BBTN'])}\n"
        po = po + '</pre>\n'
    
    
    if len(dPF) == 0:
        pf = ''
    else:
        pf = f"<i><b><u>Fallen Picking ({pts[2]} Pt)</u></b></i>\n<pre>"
        for r in range(len(dPF)):
            pf = f"{pf}❌{r+1}. [{dPF.loc[r,'LastClass']}] [{dPF.loc[r,pt] if d != 'D[0-9]%' else '1'}] {dPF.loc[r,'FruitName'][:8]} - {dPF.loc[r,'L1N']}{dPF.loc[r,'L2N']} - {(dPF.loc[r,'BBTN'])}\n"
        pf = pf + '</pre>\n'
        
        
    if len(dFE) == 0:
        fe = ''
    else:
        fe = f"<i><b><u>First Education ({pts[3]} Pt)</u></b></i>\n<pre>"
        for r in range(len(dFE)):
            fe = f"{fe}🔵{r+1}. [{dFE.loc[r,'LastClass']}] [{dFE.loc[r,pt] if d != 'D[0-9]%' else '1'}] {dFE.loc[r,'FruitName'][:8]} - {dFE.loc[r,'L1N']}{dFE.loc[r,'L2N']} - {(dFE.loc[r,'BBTN'])} - {(dFE.loc[r,'LastTopic'])} → [{(dFE.loc[r,'NextClassDate'])}]\n"
        fe = fe + '</pre>\n'
        
        
    if len(dBA) == 0:
        ba = ''
    else:
        ba = f"<i><b><u>Active BB ({pts[4]} Pt)</u></b></i>\n<pre>"
        for r in range(len(dBA)):
            ba = f"{ba}🟢{r+1}. [{dBA.loc[r,'LastClass']}] [{dBA.loc[r,pt] if d != 'D[0-9]%' else '1'}] {dBA.loc[r,'FruitName'][:8]} - {dBA.loc[r,'L1N']}{dBA.loc[r,'L2N']} - {(dBA.loc[r,'BBTN'])} - {(dBA.loc[r,'LastTopic'])} → [{(dBA.loc[r,'NextClassDate'])}]\n"
        ba = ba + '</pre>\n'
        
        
    if len(dC1) == 0:
        c1 = ''
    else:
        c1 = f"<i><b><u>Confirm Center (Before Deadline) ({pts[5]} Pt)</u></b></i>\n<pre>"
        for r in range(len(dC1)):
            c1 = f"{c1}🌟{r+1}. [{dC1.loc[r,'LastClass']}] [{dC1.loc[r,pt] if d != 'D[0-9]%' else '1'}] {dC1.loc[r,'FruitName'][:8]} - {dC1.loc[r,'L1N']}{dC1.loc[r,'L2N']} - {(dC1.loc[r,'BBTN'])} - {(dC1.loc[r,'LastTopic'])} → [{(dC1.loc[r,'NextClassDate'])}]\n"
        c1 = c1 + '</pre>\n'
        
        
    if len(dC2) == 0:
        c2 = ''
    else:
        c2 = f"<i><b><u>Confirm Center (Late) ({pts[6]} Pt)</u></b></i>\n<pre>"
        for r in range(len(dC2)):
            c2 = f"{c2}⭐️{r+1}. [{dC2.loc[r,'LastClass']}] [{dC2.loc[r,pt] if d != 'D[0-9]%' else '1'}] {dC2.loc[r,'FruitName'][:8]} - {dC2.loc[r,'L1N']}{dC2.loc[r,'L2N']} - {(dC2.loc[r,'BBTN'])} - {(dC2.loc[r,'LastTopic'])} → [{(dC2.loc[r,'NextClassDate'])}]\n"
        c2 = c2 + '</pre>\n'
        
        
    if len(dCI) == 0:
        ci = ''
    else:
        ci = f"<i><b><u>Confirm Center (Inactive) ({pts[7]} Pt)</u></b></i>\n<pre>"
        for r in range(len(dCI)):
            ci = f"{ci}🌠{r+1}. [{dCI.loc[r,'LastClass']}] [{dCI.loc[r,pt] if d != 'D[0-9]%' else '1'}] {dCI.loc[r,'FruitName'][:8]} - {dCI.loc[r,'L1N']}{dCI.loc[r,'L2N']} - {(dCI.loc[r,'BBTN'])} - {(dCI.loc[r,'LastTopic'])} → [{(dCI.loc[r,'NextClassDate'])}]\n"
        ci = ci + '</pre>\n'
        
        
    if len(dUB) == 0:
        ub = ''
    else:
        ub = f"<i><b><u>One Class Per Week (UBB) ({pts[8]} Pt)</u></b></i>\n<pre>"
        for r in range(len(dUB)):
            ub = f"{ub}🟠{r+1}. [{dUB.loc[r,'LastClass']}] [{dUB.loc[r,pt] if d != 'D[0-9]%' else '1'}] {dUB.loc[r,'FruitName'][:8]} - {dUB.loc[r,'L1N']}{dUB.loc[r,'L2N']} - {(dUB.loc[r,'BBTN'])} - {(dUB.loc[r,'LastTopic'])} → [{(dUB.loc[r,'NextClassDate'])}]\n"
        ub = ub + '</pre>\n'
        
        
    if len(dME) == 0:
        me = ''
    else:
        me = f"<i><b><u>Missed Education ({pts[9]} Pt)</u></b></i>\n<pre>"
        for r in range(len(dME)):
            me = f"{me}🔴{r+1}. [{dME.loc[r,'LastClass']}] [{dME.loc[r,pt] if d != 'D[0-9]%' else '1'}] {dME.loc[r,'FruitName'][:8]} - {dME.loc[r,'L1N']}{dME.loc[r,'L2N']} - {(dME.loc[r,'BBTN'])} - {(dME.loc[r,'LastTopic'])} → [{(dME.loc[r,'NextClassDate'])}]\n"
        me = me + '</pre>\n' 


    if len(dFA) == 0:
        fa = ''
    else:
        fa = f"<i><b><u>Fallen BB ({pts[10]} Pt)</u></b></i>\n<pre>"
        for r in range(len(dFA)):
            fa = f"{fa}⚫️{r+1}. [{dFA.loc[r,'LastClass']}] [{dFA.loc[r,pt] if d != 'D[0-9]%' else '1'}] {dFA.loc[r,'FruitName'][:8]} - {dFA.loc[r,'L1N']}{dFA.loc[r,'L2N']} - {(dFA.loc[r,'BBTN'])} - {(dFA.loc[r,'LastTopic'])} → [{(dFA.loc[r,'NextClassDate'])}]\n"
        fa = fa + '</pre>\n'
        
    
    result = f"<b><u>📚{grpdept} BB Fruit List📚</u></b>\n\n<i>▫️Status▫️\n#. [LastClassDate] [Pts] - Fruit - L1 / L2 - BBT - LastTopic → [NextClassDate]</i>\n\n{pn}{po}{pf}{fe}{ba}{c1}{c2}{ci}{ub}{me}{fa}<b><i><u>Total: {sum(pts)} Pts</u></i></b>"
    result = re.sub(r'\.0',r'',result)
    result = re.sub(r' \(\)',r'',result)
    result = re.sub(r'\((\d+)\)', r'(G\1)', result)
    result = re.sub(r'\[1\] ', r'', result)
    print(">>>Return")
    return result




def bbtlistubb(q,d,g,sid,access): # BBT FUNCTIONS
    print(f"\n>>>bbtlistubb: q={q}, d={d}, g={g}, sid={sid}, access={access}")
    print(">>>Return")
    return 'This function is deprecated'
    d = d.capitalize()
    d = re.sub(r'(¹|²)d([0-9]*)',r'\1D\2',d)

    i = q[:3]
    bbtvalues = {'bbt' : ['BBT',   " AND BBTStatus IN ('BBT','Pre-BBT')"],
                 'pre' : [q.upper(), f" AND BtmNo = '{q[6:]}' AND BBTStatus = 'Pre-BBT'"],
                 'gyj' : ['GYJN BBT',  " AND UID IN (SELECT UID FROM TGWPositionCurrent WHERE PID = 30)"],
                 'btm' : [q.upper(), f" AND BtmNo = '{q[3:]}' AND BBTStatus = 'BTM'"]}
    bbttype,query = bbtvalues[i]

    g = '%' if access not in ('Group','CUL') else g
    if access in ('Group','CUL'):
        grpdept = g.capitalize()
        grpdept = re.sub(r'(¹|²)g([0-9]*)',r'\1G\2',g)
    else:
        grpdept = str(d).replace('D[0-9]%','Youth')
    
    cols = "LastClass, BBTN, FruitName, L1N, L2N, LastTopic, NextClassDate, Points, DPoints"
    view = f"CodeyBBListUBB('{sid}') c LEFT JOIN TaskHigh t ON t.UID = c.BBTID"
    conditions = f"BBTG LIKE '{g}' AND BBTD LIKE '{d}'{query}"
    q1 = f"SELECT {cols} FROM {view} WHERE {conditions} AND NewStatus = '"
    q2 = "' ORDER BY BBTN"
    
    print(f"{q1}pNew{q2}")
        
    conn = odbc.connect(conn_str)   

    dPN = pd.read_sql(f"{q1}pNew{q2}", conn)
    dPO = pd.read_sql(f"{q1}pOld{q2}", conn)
    dPF = pd.read_sql(f"{q1}pFA{q2}" , conn)
    dFE = pd.read_sql(f"{q1}FE{q2}"  , conn)
    dBA = pd.read_sql(f"{q1}bbA{q2}" , conn)
    dC1 = pd.read_sql(f"{q1}cct1{q2}", conn)
    dC2 = pd.read_sql(f"{q1}cct2{q2}", conn)
    dCI = pd.read_sql(f"{q1}cctI{q2}", conn)
    dUB = pd.read_sql(f"{q1}UBB{q2}" , conn)
    dME = pd.read_sql(f"{q1}bbME{q2}", conn)
    dFA = pd.read_sql(f"{q1}bbFA{q2}", conn)
    
    dPN.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    dPO.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    dPF.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    dFE.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    dBA.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    dC1.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    dC2.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    dCI.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    dUB.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    dME.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    dFA.columns = ['LastClass','BBTN','FruitName','L1N','L2N','LastTopic','NextClassDate','Points','DPoints']
    conn.cursor().close()
        

    if len(dPN) == 0:
        pn = ''
    else:
        pn = f"<i><b><u>New Picking ({len(dPN)} Pt)</u></b></i>\n<pre>"
        for r in range(len(dPN)):
            pn = f"{pn}💛{r+1}. [{dPN.loc[r,'LastClass']}] {(dPN.loc[r,'BBTN'])[:8]} - {dPN.loc[r,'FruitName'][:8]} - {dPN.loc[r,'L1N'][:8]}{dPN.loc[r,'L2N'][:11]}\n"
        pn = pn + '</pre>\n'
        
        
    if len(dPO) == 0:
        po = ''
    else:
        po = f"<i><b><u>Old Picking ({len(dPO)} Pt)</u></b></i>\n<pre>"
        for r in range(len(dPO)):
            po = f"{po}⛔️{r+1}. [{dPO.loc[r,'LastClass']}] {(dPO.loc[r,'BBTN'])[:8]} - {dPO.loc[r,'FruitName'][:8]} - {dPO.loc[r,'L1N'][:8]}{dPO.loc[r,'L2N'][:11]}\n"
        po = po + '</pre>\n'
    
    
    if len(dPF) == 0:
        pf = ''
    else:
        pf = f"<i><b><u>Fallen Picking ({len(dPF)} Pt)</u></b></i>\n<pre>"
        for r in range(len(dPF)):
            pf = f"{pf}❌{r+1}. [{dPF.loc[r,'LastClass']}] {(dPF.loc[r,'BBTN'])[:8]} - {dPF.loc[r,'FruitName'][:8]} - {dPF.loc[r,'L1N'][:8]}{dPF.loc[r,'L2N'][:11]}\n"
        pf = pf + '</pre>\n'
        
        
    if len(dFE) == 0:
        fe = ''
    else:
        fe = f"<i><b><u>First Education ({len(dFE)} Pt)</u></b></i>\n<pre>"
        for r in range(len(dFE)):
            fe = f"{fe}🔵{r+1}. [{dFE.loc[r,'LastClass']}] {(dFE.loc[r,'BBTN'])[:8]} - {dFE.loc[r,'FruitName'][:8]} - {dFE.loc[r,'L1N'][:8]}{dFE.loc[r,'L2N'][:11]} - {(dFE.loc[r,'LastTopic'])} → [{(dFE.loc[r,'NextClassDate'])}]\n"
        fe = fe + '</pre>\n'
        
        
    if len(dBA) == 0:
        ba = ''
    else:
        ba = f"<i><b><u>Active BB ({len(dBA)} Pt)</u></b></i>\n<pre>"
        for r in range(len(dBA)):
            ba = f"{ba}🟢{r+1}. [{dBA.loc[r,'LastClass']}] {(dBA.loc[r,'BBTN'])[:8]} - {dBA.loc[r,'FruitName'][:8]} - {dBA.loc[r,'L1N'][:8]}{dBA.loc[r,'L2N'][:11]} - {(dBA.loc[r,'LastTopic'])} → [{(dBA.loc[r,'NextClassDate'])}]\n"
        ba = ba + '</pre>\n'
        
        
    if len(dC1) == 0:
        c1 = ''
    else:
        c1 = f"<i><b><u>Confirm Center (Before Deadline) ({len(dC1)} Pt)</u></b></i>\n<pre>"
        for r in range(len(dC1)):
            c1 = f"{c1}🌟{r+1}. [{dC1.loc[r,'LastClass']}] {(dC1.loc[r,'BBTN'])[:8]} - {dC1.loc[r,'FruitName'][:8]} - {dC1.loc[r,'L1N'][:8]}{dC1.loc[r,'L2N'][:11]} - {(dC1.loc[r,'LastTopic'])} → [{(dC1.loc[r,'NextClassDate'])}]\n"
        c1 = c1 + '</pre>\n'
        
        
    if len(dC2) == 0:
        c2 = ''
    else:
        c2 = f"<i><b><u>Confirm Center (Late) ({len(dC2)} Pt)</u></b></i>\n<pre>"
        for r in range(len(dC2)):
            c2 = f"{c2}⭐️{r+1}. [{dC2.loc[r,'LastClass']}] {(dC2.loc[r,'BBTN'])[:8]} - {dC2.loc[r,'FruitName'][:8]} - {dC2.loc[r,'L1N'][:8]}{dC2.loc[r,'L2N'][:11]} - {(dC2.loc[r,'LastTopic'])} → [{(dC2.loc[r,'NextClassDate'])}]\n"
        c2 = c2 + '</pre>\n'
        
        
    if len(dCI) == 0:
        ci = ''
    else:
        ci = f"<i><b><u>Confirm Center (Inactive) ({len(dCI)} Pt)</u></b></i>\n<pre>"
        for r in range(len(dCI)):
            ci = f"{ci}🌠{r+1}. [{dCI.loc[r,'LastClass']}] {(dCI.loc[r,'BBTN'])[:8]} - {dCI.loc[r,'FruitName'][:8]} - {dCI.loc[r,'L1N'][:8]}{dCI.loc[r,'L2N'][:11]} - {(dCI.loc[r,'LastTopic'])} → [{(dCI.loc[r,'NextClassDate'])}]\n"
        ci = ci + '</pre>\n'
        
        
    if len(dUB) == 0:
        ub = ''
    else:
        ub = f"<i><b><u>One Class Per Week (UBB) ({len(dUB)} Pt)</u></b></i>\n<pre>"
        for r in range(len(dUB)):
            ub = f"{ub}🟠{r+1}. [{dUB.loc[r,'LastClass']}] {(dUB.loc[r,'BBTN'])[:8]} - {dUB.loc[r,'FruitName'][:8]} - {dUB.loc[r,'L1N'][:8]}{dUB.loc[r,'L2N'][:11]} - {(dUB.loc[r,'LastTopic'])} → [{(dUB.loc[r,'NextClassDate'])}]\n"
        ub = ub + '</pre>\n'
        
        
    if len(dME) == 0:
        me = ''
    else:
        me = f"<i><b><u>Missed Education ({len(dME)} Pt)</u></b></i>\n<pre>"
        for r in range(len(dME)):
            me = f"{me}🔴{r+1}. [{dME.loc[r,'LastClass']}] {(dME.loc[r,'BBTN'])[:8]} - {dME.loc[r,'FruitName'][:8]} - {dME.loc[r,'L1N'][:8]}{dME.loc[r,'L2N'][:11]} - {(dME.loc[r,'LastTopic'])} → [{(dME.loc[r,'NextClassDate'])}]\n"
        me = me + '</pre>\n' 


    if len(dFA) == 0:
        fa = ''
    else:
        fa = f"<i><b><u>Fallen BB ({len(dFA)} Pt)</u></b></i>\n<pre>"
        for r in range(len(dFA)):
            fa = f"{fa}⚫️{r+1}. [{dFA.loc[r,'LastClass']}] {(dFA.loc[r,'BBTN'])[:8]} - {dFA.loc[r,'FruitName'][:8]} - {dFA.loc[r,'L1N'][:8]}{dFA.loc[r,'L2N'][:11]} - {(dFA.loc[r,'LastTopic'])} → [{(dFA.loc[r,'NextClassDate'])}]\n"
        fa = fa + '</pre>\n'
        
    
    result = f"<b><u>📖{grpdept} {bbttype} Student List📖</u></b>\n\n<i>▫️Status▫️\n#. [LastClassDate] [Pts] - Fruit - L1 / L2 - BBT - LastTopic → [NextClassDate]</i>\n\n{pn}{po}{pf}{fe}{ba}{c1}{c2}{ci}{ub}{me}{fa}<b><i><u>Total: {sum([len(dPN),len(dPO),len(dPF),len(dFE),len(dBA),len(dC1),len(dC2),len(dCI),len(dUB),len(dME),len(dFA)])} Pts</u></i></b>"
    result = re.sub(r'\.0',r'',result)
    result = re.sub(r' \(\)',r'',result)
    result = re.sub(r'\((\d+)\)', r'(G\1)', result)
    result = re.sub(r'\[1\] ', r'', result)
    print(">>>Return")
    return result



def bbpick(g): # BB FUNCTIONS
    print(f"\n>>>bbpick: g={g}")
    conn = odbc.connect(conn_str)
    dn  = pd.read_sql(f"SELECT * FROM ScottPickStatus('{g}') WHERE P_Status = 'New'", conn)
    do  = pd.read_sql(f"SELECT * FROM ScottPickStatus('{g}') WHERE P_Status = 'Old'", conn)
    df  = pd.read_sql(f"SELECT * FROM ScottPickStatus('{g}') WHERE P_Status = 'Fallen'", conn)
    dPts = pd.read_sql(f"SELECT P_Status, SUM(Points)Pts FROM ScottPickStatus('{g}') GROUP BY P_Status", conn)
    dn.columns = ['P_Date','FruitName','L1N','L1G','L2N','L2G','BBTN','BBTG','Points','P_Status']
    do.columns = ['P_Date','FruitName','L1N','L1G','L2N','L2G','BBTN','BBTG','Points','P_Status']
    df.columns = ['P_Date','FruitName','L1N','L1G','L2N','L2G','BBTN','BBTG','Points','P_Status']
    dPts.columns =  ['P_Status','Pts']
    do['P_Date'] = pd.to_datetime(do['P_Date'])
    dn['P_Date'] = pd.to_datetime(dn['P_Date'])
    df['P_Date'] = pd.to_datetime(df['P_Date'])
    do['P_Date'] = do['P_Date'].dt.strftime('%a %d/%m')
    dn['P_Date'] = dn['P_Date'].dt.strftime('%a %d/%m')
    df['P_Date'] = df['P_Date'].dt.strftime('%a %d/%m')
    dPts.set_index('P_Status', inplace=True)
        
    conn.cursor().close()
    
    new = ''
    if len(dn) > 0:
        for r in range(len(dn)):
            new = f"{new}🟡{r+1}. [{dn.loc[r,'Points']}] {dn.loc[r,'FruitName'][:8]} - {dn.loc[r,'L1N'][:8]} ({dn.loc[r,'L1G']}){dn.loc[r,'L2N'][:11]} ({dn.loc[r,'L2G']}) - {(dn.loc[r,'BBTN'])[:8]} ({dn.loc[r,'BBTG']}) [{dn.loc[r,'P_Date']}]\n"
        new = f"<i><b><u>New Picking ({dPts.loc['New','Pts']} pt)</u></b></i>\n<pre>{new}</pre>\n"
    
    old = ''
    if len(do) > 0:
        for r in range(len(do)):
            old = f"{old}⚪️{r+1}. [{do.loc[r,'Points']}] {do.loc[r,'FruitName'][:8]} - {do.loc[r,'L1N'][:8]} ({do.loc[r,'L1G']}){do.loc[r,'L2N'][:11]} ({do.loc[r,'L2G']}) - {(do.loc[r,'BBTN'])[:8]} ({do.loc[r,'BBTG']}) [{do.loc[r,'P_Date']}]\n"
        old = f"<i><b><u>Old Picking ({dPts.loc['Old','Pts']} pt)</u></b></i>\n<pre>{old}</pre>\n"
    
    fallen = ''
    if len(df) > 0:
        for r in range(len(df)):
            fallen = f"{fallen}⚫️{r+1}. [{df.loc[r,'Points']}] {df.loc[r,'FruitName'][:8]} - {df.loc[r,'L1N'][:8]} ({df.loc[r,'L1G']}){df.loc[r,'L2N'][:11]} ({df.loc[r,'L2G']}) - {(df.loc[r,'BBTN'])[:8]} ({df.loc[r,'BBTG']}) [{df.loc[r,'P_Date']}]\n"
        fallen = f"<i><b><u>Fallen Picking ({dPts.loc['Fallen','Pts']} pt)</u></b></i>\n<pre>{fallen}</pre>\n" 
    
    result = f"<b><u>📙{g} Picking Status📙</u></b>\n\n<i>▫️Status▫️\n#. Fruit - Leaf1 / Leaf2 - BBT [Picking Date]</i>\n\n{new}{old}{fallen}"
    result = re.sub(r'\.0',r'',result)
    result = re.sub(r' \(\)',r'',result)
    result = re.sub(r'\((\d+)\)', r'(G\1)', result)
    result = re.sub(r'\[1\] ', r'', result)
    print(">>>Return")
    return result


def bbfe(g): # BB FUNCTIONS
    print(f"\n>>>bbfe: g={g}")
    conn = odbc.connect(conn_str)   
    dFE  = pd.read_sql(f"""SELECT b.FruitName, b.L1N, b.L1G, b.L2N, b.L2G, b.BBTN, b.BBTG, f.FE_Date, Points
FROM ScottBBList('{g}','%') b
LEFT JOIN ScottFEData f ON b.UID = f.UID
LEFT JOIN BBData bb ON bb.UID = b.UID
WHERE FE_Date IS NOT NULL AND Stat_Abbr != 'FA'""", conn)
    dCncl = pd.read_sql(f"""SELECT b.FruitName, b.L1N, b.L1G, b.L2N, b.L2G, b.BBTN, b.BBTG, bb.NextClassDate MissedFEDate, Points
FROM ScottBBList('{g}','%') b
LEFT JOIN ScottFEData f ON b.UID = f.UID
LEFT JOIN BBData bb ON bb.UID = b.UID
WHERE FE_Date IS NULL AND NextClassDate < CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time') AND Stat_Abbr != 'FA'""", conn)
    dSchd = pd.read_sql(f"""SELECT b.FruitName, b.L1N, b.L1G, b.L2N, b.L2G, b.BBTN, b.BBTG, bb.NextClassDate SchedFE, Points
FROM ScottBBList('{g}','%') b
LEFT JOIN ScottFEData f ON b.UID = f.UID
LEFT JOIN BBData bb ON bb.UID = b.UID
WHERE FE_Date IS NULL AND NextClassDate >= CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time') AND Stat_Abbr != 'FA'""", conn)
    dFA = pd.read_sql(f"""SELECT b.FruitName, b.L1N, b.L1G, b.L2N, b.L2G, b.BBTN, b.BBTG,
CASE
	WHEN FE_Date IS NULL THEN 'Cross'
	ELSE 'Tick'
	END AS FEStatus,
Points
FROM ScottBBList('{g}','%') b
LEFT JOIN ScottFEData f ON b.UID = f.UID
LEFT JOIN BBData bb ON bb.UID = b.UID
WHERE Stat_Abbr = 'FA'
ORDER BY FeStatus DESC""", conn)
    dPts = pd.read_sql(f"""SELECT FEStatus, SUM(Points)Points FROM (
SELECT
CASE WHEN Stat_Abbr = 'FA' THEN 'Fallen'
	 WHEN FE_Date IS NOT NULL THEN 'FE'
	 WHEN NextClassDate < CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time') THEN 'Missed'
	 ELSE 'Scheduled'
	 END AS FEStatus,
Points
FROM ScottBBList('{g}','%') b
LEFT JOIN ScottFEData f ON b.UID = f.UID
LEFT JOIN BBData bb ON bb.UID = b.UID
) fe GROUP BY FEStatus ORDER BY FEStatus""", conn)
    dFE.columns =   ['FruitName','L1N','L1G','L2N','L2G','BBTN','BBTG','FE_Date','Points']
    dCncl.columns = ['FruitName','L1N','L1G','L2N','L2G','BBTN','BBTG','MissedFEDate','Points']
    dSchd.columns = ['FruitName','L1N','L1G','L2N','L2G','BBTN','BBTG','SchedFEDate','Points']
    dFA.columns =   ['FruitName','L1N','L1G','L2N','L2G','BBTN','BBTG','FEStatus','Points']
    dPts.columns =  ['FEStatus','Pts']
    dFE['FE_Date'] = pd.to_datetime(dFE['FE_Date'])
    dCncl['MissedFEDate'] = pd.to_datetime(dCncl['MissedFEDate'])
    dSchd['SchedFEDate'] = pd.to_datetime(dSchd['SchedFEDate'])
    dFE['FE_Date'] = dFE['FE_Date'].dt.strftime('%a %d/%m')
    dCncl['MissedFEDate'] = dCncl['MissedFEDate'].dt.strftime('%a %d/%m')
    dSchd['SchedFEDate'] = dSchd['SchedFEDate'].dt.strftime('%a %d/%m')
    dPts.set_index('FEStatus', inplace=True)
        
    conn.cursor().close()
           
    if len(dFE) == 0:
        fe = ''
    else: 
        fe = f"<i><b><u>First Education ({dPts.loc['FE','Pts']} pt)</u></b></i>\n"
        for r in range(len(dFE)):
            fe = f"{fe}<pre>💙{r+1}. [{dFE.loc[r,'Points']}] {dFE.loc[r,'FruitName'][:8]} - {dFE.loc[r,'L1N'][:8]} ({dFE.loc[r,'L1G']}){dFE.loc[r,'L2N'][:11]} ({dFE.loc[r,'L2G']}) - {(dFE.loc[r,'BBTN'])[:8]} ({dFE.loc[r,'BBTG']}) [{dFE.loc[r,'FE_Date']}]</pre>\n"
        fe = fe + '\n'
        
    if len(dCncl) == 0:
        cncl = ''
    else: 
        cncl = f"<i><b><u>Cancelled FE ({dPts.loc['Missed','Pts']} pt)</u></b></i>\n"
        for r in range(len(dCncl)):
            cncl = f"{cncl}<pre>❌{r+1}. [{dCncl.loc[r,'Points']}] {dCncl.loc[r,'FruitName'][:8]} - {dCncl.loc[r,'L1N'][:8]} ({dCncl.loc[r,'L1G']}){dCncl.loc[r,'L2N'][:11]} ({dCncl.loc[r,'L2G']}) - {(dCncl.loc[r,'BBTN'])[:8]} ({dCncl.loc[r,'BBTG']}) [{dCncl.loc[r,'MissedFEDate']}]</pre>\n"
        cncl = cncl + '\n'
    
    if len(dSchd) == 0:
        schd = ''
    else: 
        schd = f"<i><b><u>Scheduled FE ({dPts.loc['Scheduled','Pts']} pt)</u></b></i>\n"
        for r in range(len(dSchd)):
            schd = f"{schd}<pre>💛{r+1}. [{dSchd.loc[r,'Points']}] {dSchd.loc[r,'FruitName'][:8]} - {dSchd.loc[r,'L1N'][:8]} ({dSchd.loc[r,'L1G']}){dSchd.loc[r,'L2N'][:11]} ({dSchd.loc[r,'L2G']}) - {(dSchd.loc[r,'BBTN'])[:8]} ({dSchd.loc[r,'BBTG']}) [{dSchd.loc[r,'SchedFEDate']}]</pre>\n"
        schd = schd + '\n' 
    
    if len(dFA) == 0:
        fallen = ''
    else: 
        fallen = f"<i><b><u>Fallen ({dPts.loc['Fallen','Pts']} pt)</u></b></i>\n"
        for r in range(len(dFA)):
            fallen = f"{fallen}<pre>{dFA.loc[r,'FEStatus'].replace('Tick','⚫️').replace('Cross','❌')}{r+1}. [{dFA.loc[r,'Points']}] {dFA.loc[r,'FruitName'][:8]} - {dFA.loc[r,'L1N'][:8]} ({dFA.loc[r,'L1G']}){dFA.loc[r,'L2N'][:11]} ({dFA.loc[r,'L2G']}) - {(dFA.loc[r,'BBTN'])[:8]} ({dFA.loc[r,'BBTG']})</pre>\n"
        fallen = fallen + '\n' 
        
    result = f"<b><u>📘{g} FE Status📘</u></b>\n\n<i>▫️Status▫️\n#. Fruit - Leaf1 / Leaf2 - BBT [FE Date]</i>\n\n{schd}{fe}{cncl}{fallen}"
    result = re.sub(r'\.0',r'',result)
    result = re.sub(r' \(\)',r'',result)
    result = re.sub(r'\((\d+)\)', r'(G\1)', result)
    result = re.sub(r'\[1\] ', r'', result)
    print(">>>Return")
    return result






def youthfm(d): # FMP FUNCTIONS
    print(f"\n>>>youthfm: d={d}")
    header = f"{str(d).replace('D[0-9]%','Youth')} FMs"
    conn = odbc.connect(conn_str)
    
    bb_group = f"SELECT Grp, NewM mNew, OldM mOld FROM ScottOldNewMGrp WHERE Dept LIKE '{d}'".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    bb_dept = f"SELECT Dept, SUM(NewM)mNew, SUM(OldM)mOld FROM ScottOldNewMGrp WHERE Dept LIKE '{d}' GROUP BY Dept ORDER BY LEN(Dept),Dept".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    bb_youth = f"SELECT SUM(NewM)mNew, SUM(OldM)mOld FROM ScottOldNewMGrp WHERE Dept LIKE '{d}'".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    
    dg = pd.read_sql(bb_group, conn)
    dd = pd.read_sql(bb_dept, conn)
    dy = pd.read_sql(bb_youth, conn)

    dg.columns = ['Grp','mNew','mOld']
    dd.columns = ['Dept','mNew','mOld']
    dy.columns = ['mNew','mOld']
    
    dd.replace(r' Dept',r'', regex = True, inplace = True)
    
    conn.cursor().close()

    separator = '|'
    
    group = str()
    for r in range(len(dg)):
        grp =    str(dg.loc[r,'Grp']) + ' '*(5-len(str(dg.loc[r,'Grp'])))
        mn  = ' '*(5-len(str(dg.loc[r,'mNew']))) + str(dg.loc[r,'mNew'])
        mo  = ' '*(6-len(str(dg.loc[r,'mOld']))) + str(dg.loc[r,'mOld'])
        group = f'{group}{grp}[{mn}|{mo}]\n'
    
    dept = str()    
    for r in range(len(dd)):
        dpt = str(dd.loc[r,'Dept'])   + ' '*(5-len(str(dd.loc[r,'Dept'])))
        mn  = ' '*(5-len(str(dd.loc[r,'mNew']))) + str(dd.loc[r,'mNew'])
        mo  = ' '*(6-len(str(dd.loc[r,'mOld']))) + str(dd.loc[r,'mOld'])
        dept = f'{dept}{dpt}[{mn}|{mo}]\n'
            
    if d.endswith('D[0-9]%'):
        mn = ' '*(5-len(str(dy.loc[0,'mNew']))) + str(dy.loc[0,'mNew'])
        mo = ' '*(6-len(str(dy.loc[0,'mOld']))) + str(dy.loc[0,'mOld'])
        youth = f'\nTotal[{mn}|{mo}]\n'

    else:
        youth = str()
    
    result = f"""<b><u>{header}</u></b>\n\n<pre>Grp  [  NM |  OM  ]\n\n{group}\n{dept}{youth}</pre>"""
    result = re.sub(r'\.0',r'  ',result) # Replaces '.0' with empty space
    result = re.sub(r'(\D)0([^.])',r'\1-\2',result)   # Replaces lone '0' with '-'
    print(">>>Return")
    return result




def bbactive(g, d, sid, access): # BB FUNCTIONS
    print(f"\n>>>bbactive: g={g}, d={d}, sid={sid}, access={access}")

    g = g if access in ('Group','CUL') else '%'
    d = d.capitalize().replace('d','D')
    d = re.sub(r'(¹|²)d([0-9]*)',r'\1D\2',d)
    if access in ('Group','CUL'):
        grpdept = g.capitalize()
        grpdept = re.sub(r'(¹|²)g([0-9]*)',r'\1G\2',g)
    else:
        grpdept = d.replace('D[0-9]%','Youth').replace('Mw[0-9]%','MW').replace('24', '24 Dept').replace('%', 'Church')
        
    
    print(f"bbstatus parameters:          g = '{g}'          d = '{d}'          sid = {sid}          access = '{access}'")
    
    conn = odbc.connect(conn_str)
    bb_mem    = f"SELECT Dept, Grp, MemberCode, Total SP, pNew, bbA, cctA FROM CodeyBBStatusMembers('{sid}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}' ORDER BY GID".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    bb_group  = f"SELECT Grp, SUM(Total)SP, SUM(pNew)pNew, SUM(bbA)bbA, SUM(cctA)cctA FROM CodeyBBStatusMembers('{sid}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}' GROUP BY Grp, GID ORDER BY GID".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    bb_dept   = f"SELECT Dept, SUM(Total)SP, SUM(pNew)pNew, SUM(bbA)bbA, SUM(cctA)cctA FROM CodeyBBStatusMembers('{sid}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}' GROUP BY Dept, DID ORDER BY DID".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    # bb_region = f"SELECT District, SUM(Total)SP, SUM(pNew)pNew, SUM(bbA)bbA, SUM(cctA)cctA FROM CodeyBBStatusMembers('{sid}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}' GROUP BY District".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    bb_youth  = f"SELECT SUM(Total)SP, SUM(pNew)pNew, SUM(bbA)bbA, SUM(cctA)cctA FROM CodeyBBStatusMembers('{sid}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}'".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    
    print(bb_group)
    
    dm = pd.read_sql(bb_mem, conn)
    dg = pd.read_sql(bb_group, conn)
    dd = pd.read_sql(bb_dept, conn)
    # dr = pd.read_sql(bb_region, conn)
    dy = pd.read_sql(bb_youth, conn)

    dm.columns = ['Dept','Grp','Member','SP','pNew','bbA','cctA']
    dg.columns = ['Grp','SP','pNew','bbA','cctA']
    dd.columns = ['Dept','SP','pNew','bbA','cctA']
    # dr.columns = ['Region','SP','pNew','bbA','cctA']
    dy.columns = ['SP','pNew','bbA','cctA']
    dd.replace(r' Dept',r'', regex = True, inplace = True)
    
    conn.cursor().close()

    member = str()
    if access in ('Group','CUL'):
        for r in range(len(dm)):
            bbt =   str(dm.loc[r,'Member'][:5]) + ' '*(5-len(str(dm.loc[r,'Member'][:5])))
            sp  = ' '*(5-len(str(dm.loc[r,'SP']))) + str(dm.loc[r,'SP'])
            pn  = ' '*(5-len(str(dm.loc[r,'pNew']))) + str(dm.loc[r,'pNew'])
            ba  = ' '*(5-len(str(dm.loc[r,'bbA'])))  + str(dm.loc[r,'bbA'])
            ca  = ' '*(4-len(str(dm.loc[r,'cctA']))) + str(dm.loc[r,'cctA'])
            member = f'{member}{bbt}[{sp}][{pn}|{ba}|{ca}]\n'
        member = member + '\n'
            
            
    group = str()    
    for r in range(len(dg)):
        grp =   str(dg.loc[r,'Grp']) + ' '*(5-len(str(dg.loc[r,'Grp'])))
        sp  = ' '*(5-len(str(dg.loc[r,'SP'])))   + str(dg.loc[r,'SP'])
        pn  = ' '*(5-len(str(dg.loc[r,'pNew']))) + str(dg.loc[r,'pNew'])
        ba  = ' '*(5-len(str(dg.loc[r,'bbA'])))  + str(dg.loc[r,'bbA'])
        ca  = ' '*(4-len(str(dg.loc[r,'cctA']))) + str(dg.loc[r,'cctA'])
        group = f'{group}{grp}[{sp}][{pn}|{ba}|{ca}]\n'
    group = group + '\n'
            
    dept = str()  
    if access not in ('Group','CUL'):
        for r in range(len(dd)):
            dpt =   str(dd.loc[r,'Dept']) + ' '*(5-len(str(dd.loc[r,'Dept'])))
            sp  = ' '*(5-len(str(dd.loc[r,'SP'])))   + str(dd.loc[r,'SP'])
            pn  = ' '*(5-len(str(dd.loc[r,'pNew']))) + str(dd.loc[r,'pNew'])
            ba  = ' '*(5-len(str(dd.loc[r,'bbA'])))  + str(dd.loc[r,'bbA'])
            ca  = ' '*(4-len(str(dd.loc[r,'cctA']))) + str(dd.loc[r,'cctA'])
            dept = f'{dept}{dpt}[{sp}][{pn}|{ba}|{ca}]\n'
        dept = dept + '\n'
    
    # region = str()
    # if d.endswith('D[0-9]%'):    
    #     for r in range(len(dr)):
    #         reg =   str(dr.loc[r,'Region']) + ' '*(5-len(str(dr.loc[r,'Region'])))
    #         sp  = ' '*(5-len(str(dr.loc[r,'SP'])))   + str(dr.loc[r,'SP'])
    #         pn  = ' '*(5-len(str(dr.loc[r,'pNew']))) + str(dr.loc[r,'pNew'])
    #         ba  = ' '*(5-len(str(dr.loc[r,'bbA'])))  + str(dr.loc[r,'bbA'])
    #         ca  = ' '*(4-len(str(dr.loc[r,'cctA']))) + str(dr.loc[r,'cctA'])
    #         region = f'{region}{reg}[{sp}][{pn}|{ba}|{ca}]\n'
    #     region = region + '\n'
    
    total = str()
    if d in ('D[0-9]%','%'):
        sp  = ' '*(5-len(str(dy.loc[0,'SP'])))   + str(dy.loc[0,'SP'])
        pn  = ' '*(5-len(str(dy.loc[0,'pNew']))) + str(dy.loc[0,'pNew'])
        ba  = ' '*(5-len(str(dy.loc[0,'bbA'])))  + str(dy.loc[0,'bbA'])
        ca  = ' '*(4-len(str(dy.loc[0,'cctA']))) + str(dy.loc[0,'cctA'])
        total = f'Total[{sp}][{pn}|{ba}|{ca}]'
    
    summary = f"<b><u>{grpdept} Active BB Status Summary</u></b>\n\n<pre>     [  SP ][  NP |  AB | CA ]\n\n{member}{group}{dept}{total}</pre>"
    summary = re.sub(r'\.0',r'  ',summary) # Replaces '.0' with empty space
    summary = re.sub(r'(\D)0([^.])',r'\1-\2',summary)   # Replaces lone '0' with '-'
    print(">>>Return")
    return summary








def bbactive2(g, d, sid, access): # BB FUNCTIONS
    print(f"\n>>>bbactive2: g={g}, d={d}, sid={sid}, access={access}")
                
    g = g if access in ('Group','CUL') else '%'
    d = d.capitalize().replace('d','D')
    d = re.sub(r'(¹|²)d([0-9]*)',r'\1D\2',d)
    if access in ('Group','CUL'):
        grpdept = g.capitalize()
        grpdept = re.sub(r'(¹|²)g([0-9]*)',r'\1G\2',g)
    else:
        grpdept = d.replace('D[0-9]%','Youth').replace('Mw[0-9]%','MW').replace('24', '24 Dept').replace('%', 'Church')
        
    
    print(f"bbstatus parameters:          g = '{g}'          d = '{d}'          sid = {sid}          access = '{access}'")
    
    conn = odbc.connect(conn_str)
    bb_mem    = f"SELECT Dept, Grp, MemberCode, Total SP, pNew, FE, bbA, cctA FROM CodeyBBStatusMembers2('{sid}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}' ORDER BY GID".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    bb_group  = f"SELECT Grp, SUM(Total)SP, SUM(pNew)pNew, SUM(FE)FE, SUM(bbA)bbA, SUM(cctA)cctA FROM CodeyBBStatusMembers2('{sid}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}' GROUP BY Grp, GID ORDER BY GID".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    bb_dept   = f"SELECT Dept, SUM(Total)SP, SUM(pNew)pNew, SUM(FE)FE, SUM(bbA)bbA, SUM(cctA)cctA FROM CodeyBBStatusMembers2('{sid}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}' GROUP BY Dept, DID ORDER BY DID".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    # bb_region = f"SELECT District, SUM(Total)SP, SUM(pNew)pNew, SUM(FE)FE, SUM(bbA)bbA, SUM(cctA)cctA FROM CodeyBBStatusMembers2('{sid}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}' GROUP BY District".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    bb_youth  = f"SELECT SUM(Total)SP, SUM(pNew)pNew, SUM(FE)FE, SUM(bbA)bbA, SUM(cctA)cctA FROM CodeyBBStatusMembers2('{sid}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}'".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    
    print(bb_group)
    
    dm = pd.read_sql(bb_mem, conn)
    dg = pd.read_sql(bb_group, conn)
    dd = pd.read_sql(bb_dept, conn)
    # dr = pd.read_sql(bb_region, conn)
    dy = pd.read_sql(bb_youth, conn)

    dm.columns = ['Dept','Grp','Member','SP','pNew','FE','bbA','cctA']
    dg.columns = ['Grp','SP','pNew','FE','bbA','cctA']
    dd.columns = ['Dept','SP','pNew','FE','bbA','cctA']
    # dr.columns = ['Region','SP','pNew','FE','bbA','cctA']
    dy.columns = ['SP','pNew','FE','bbA','cctA']
    dd.replace(r' Dept',r'', regex = True, inplace = True)
    
    conn.cursor().close()

    member = str()
    if access in ('Group','CUL'):
        for r in range(len(dm)):
            bbt =   str(dm.loc[r,'Member'][:5]) + ' '*(5-len(str(dm.loc[r,'Member'][:5])))
            sp  = ' '*(5-len(str(dm.loc[r,'SP']))) + str(dm.loc[r,'SP'])
            pn  = ' '*(5-len(str(dm.loc[r,'FE']))) + str(dm.loc[r,'FE'])
            fe  = ' '*(5-len(str(dm.loc[r,'pNew']))) + str(dm.loc[r,'pNew'])
            ba  = ' '*(5-len(str(dm.loc[r,'bbA'])))  + str(dm.loc[r,'bbA'])
            ca  = ' '*(4-len(str(dm.loc[r,'cctA']))) + str(dm.loc[r,'cctA'])
            member = f'{member}{bbt}[{sp}][{pn}|{fe}|{ba}|{ca}]\n'
        member = member + '\n'
            
            
    group = str()    
    for r in range(len(dg)):
        grp =   str(dg.loc[r,'Grp']) + ' '*(5-len(str(dg.loc[r,'Grp'])))
        sp  = ' '*(5-len(str(dg.loc[r,'SP'])))   + str(dg.loc[r,'SP'])
        pn  = ' '*(5-len(str(dg.loc[r,'pNew']))) + str(dg.loc[r,'pNew'])
        fe  = ' '*(5-len(str(dg.loc[r,'FE']))) + str(dg.loc[r,'FE'])
        ba  = ' '*(5-len(str(dg.loc[r,'bbA'])))  + str(dg.loc[r,'bbA'])
        ca  = ' '*(4-len(str(dg.loc[r,'cctA']))) + str(dg.loc[r,'cctA'])
        group = f'{group}{grp}[{sp}][{pn}|{fe}|{ba}|{ca}]\n'
    group = group + '\n'
            
    dept = str()  
    if access not in ('Group','CUL'):
        for r in range(len(dd)):
            dpt =   str(dd.loc[r,'Dept']) + ' '*(5-len(str(dd.loc[r,'Dept'])))
            sp  = ' '*(5-len(str(dd.loc[r,'SP'])))   + str(dd.loc[r,'SP'])
            pn  = ' '*(5-len(str(dd.loc[r,'pNew']))) + str(dd.loc[r,'pNew'])
            fe  = ' '*(5-len(str(dd.loc[r,'FE']))) + str(dd.loc[r,'FE'])
            ba  = ' '*(5-len(str(dd.loc[r,'bbA'])))  + str(dd.loc[r,'bbA'])
            ca  = ' '*(4-len(str(dd.loc[r,'cctA']))) + str(dd.loc[r,'cctA'])
            dept = f'{dept}{dpt}[{sp}][{pn}|{fe}|{ba}|{ca}]\n'
        dept = dept + '\n'
    
    # region = str()
    # if d.endswith('D[0-9]%'):    
    #     for r in range(len(dr)):
    #         reg =   str(dr.loc[r,'Region']) + ' '*(5-len(str(dr.loc[r,'Region'])))
    #         sp  = ' '*(5-len(str(dr.loc[r,'SP'])))   + str(dr.loc[r,'SP'])
    #         pn  = ' '*(5-len(str(dr.loc[r,'pNew']))) + str(dr.loc[r,'pNew'])
    #         fe  = ' '*(5-len(str(dr.loc[r,'FE'])))  + str(dr.loc[r,'FE'])
    #         ba  = ' '*(5-len(str(dr.loc[r,'bbA'])))  + str(dr.loc[r,'bbA'])
    #         ca  = ' '*(4-len(str(dr.loc[r,'cctA']))) + str(dr.loc[r,'cctA'])
    #         region = f'{region}{reg}[{sp}][{pn}|{fe}|{ba}|{ca}]\n'
    #     region = region + '\n'
    
    total = str()
    if d in ('D[0-9]%','%'):
        sp  = ' '*(5-len(str(dy.loc[0,'SP'])))   + str(dy.loc[0,'SP'])
        pn  = ' '*(5-len(str(dy.loc[0,'pNew']))) + str(dy.loc[0,'pNew'])
        fe  = ' '*(5-len(str(dy.loc[0,'FE']))) + str(dy.loc[0,'FE'])
        ba  = ' '*(5-len(str(dy.loc[0,'bbA'])))  + str(dy.loc[0,'bbA'])
        ca  = ' '*(4-len(str(dy.loc[0,'cctA']))) + str(dy.loc[0,'cctA'])
        total = f'Total[{sp}][{pn}|{fe}|{ba}|{ca}]'
    
    summary = f"<b><u>{grpdept} Active BB Status Summary</u></b>\n<i>ABB = 2+ classes</i>\n\n<pre>     [  SP ][  NP |  FE |  AB | CA ]\n\n{member}{group}{dept}{total}</pre>"
    summary = re.sub(r'\.0',r'  ',summary) # Replaces '.0' with empty space
    summary = re.sub(r'(\D)0([^.])',r'\1-\2',summary)   # Replaces lone '0' with '-'
    print(">>>Return")
    return summary





def deptbbactive(d, sid, access): # BB FUNCTIONS
    print(f"\n>>>deptbbactive: d={d}, sid={sid}, access={access}")
                
    d = d.capitalize().replace('d','D')
    d = re.sub(r'(¹|²)d([0-9]*)',r'\1D\2',d)
    grpdept = d.replace('D[0-9]%','Youth').replace('Mw[0-9]%','MW').replace('24', '24 Dept').replace('%', 'Church')
        
    
    print(f"bbstatus parameters:          d = '{d}'          sid = {sid}          access = '{access}'")
    
    conn = odbc.connect(conn_str)
    bb_dept   = f"SELECT Dept, SUM(Total)SP, SUM(pNew)pNew, SUM(bbA)bbA, SUM(cctA)cctA FROM CodeyBBStatusMembers('{sid}') WHERE Dept LIKE '{d}' GROUP BY Dept, DID ORDER BY DID".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    # bb_region = f"SELECT District, SUM(Total)SP, SUM(pNew)pNew, SUM(bbA)bbA, SUM(cctA)cctA FROM CodeyBBStatusMembers('{sid}') WHERE Dept LIKE '{d}' GROUP BY District".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    bb_youth  = f"SELECT SUM(Total)SP, SUM(pNew)pNew, SUM(bbA)bbA, SUM(cctA)cctA FROM CodeyBBStatusMembers('{sid}') WHERE Dept LIKE '{d}'".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    
    dd = pd.read_sql(bb_dept, conn)
    # dr = pd.read_sql(bb_region, conn)
    dy = pd.read_sql(bb_youth, conn)

    dd.columns = ['Dept','SP','pNew','bbA','cctA']
    # dr.columns = ['Region','SP','pNew','bbA','cctA']
    dy.columns = ['SP','pNew','bbA','cctA']
    dd.replace(r' Dept',r'', regex = True, inplace = True)
    
    conn.cursor().close()
            
    dept = str()  
    if access not in ('Group','CUL'):
        for r in range(len(dd)):
            dpt =   str(dd.loc[r,'Dept']) + ' '*(5-len(str(dd.loc[r,'Dept'])))
            sp  = ' '*(5-len(str(dd.loc[r,'SP'])))   + str(dd.loc[r,'SP'])
            pn  = ' '*(5-len(str(dd.loc[r,'pNew']))) + str(dd.loc[r,'pNew'])
            ba  = ' '*(5-len(str(dd.loc[r,'bbA'])))  + str(dd.loc[r,'bbA'])
            ca  = ' '*(4-len(str(dd.loc[r,'cctA']))) + str(dd.loc[r,'cctA'])
            dept = f'{dept}{dpt}[{sp}][{pn}|{ba}|{ca}]\n'
        dept = dept + '\n'
    
    # region = str()
    # if d.endswith('D[0-9]%'):    
    #     for r in range(len(dr)):
    #         reg =   str(dr.loc[r,'Region']) + ' '*(5-len(str(dr.loc[r,'Region'])))
    #         sp  = ' '*(5-len(str(dr.loc[r,'SP'])))   + str(dr.loc[r,'SP'])
    #         pn  = ' '*(5-len(str(dr.loc[r,'pNew']))) + str(dr.loc[r,'pNew'])
    #         ba  = ' '*(5-len(str(dr.loc[r,'bbA'])))  + str(dr.loc[r,'bbA'])
    #         ca  = ' '*(4-len(str(dr.loc[r,'cctA']))) + str(dr.loc[r,'cctA'])
    #         region = f'{region}{reg}[{sp}][{pn}|{ba}|{ca}]\n'
    #     region = region + '\n'
    
    total = str()
    if d in ('D[0-9]%','%'):
        sp  = ' '*(5-len(str(dy.loc[0,'SP'])))   + str(dy.loc[0,'SP'])
        pn  = ' '*(5-len(str(dy.loc[0,'pNew']))) + str(dy.loc[0,'pNew'])
        ba  = ' '*(5-len(str(dy.loc[0,'bbA'])))  + str(dy.loc[0,'bbA'])
        ca  = ' '*(4-len(str(dy.loc[0,'cctA']))) + str(dy.loc[0,'cctA'])
        total = f'Total[{sp}][{pn}|{ba}|{ca}]'
    
    summary = f"<b><u>{grpdept} Active BB Status Summary</u></b>\n\n<pre>     [  SP ][  NP |  AB | CA ]\n\n{dept}{total}</pre>"
    summary = re.sub(r'\.0',r'  ',summary) # Replaces '.0' with empty space
    summary = re.sub(r'(\D)0([^.])',r'\1-\2',summary)   # Replaces lone '0' with '-'
    print(">>>Return")
    return summary





def bbinactive(g, d, sid, access): # BB FUNCTIONS
    print(f"\n>>>bbinactive: g={g}, d={d}, sid={sid}, access={access}")

    g = g if access in ('Group','CUL') else '%'
    d = d.capitalize().replace('d','D')
    d = re.sub(r'(¹|²)d([0-9]*)',r'\1D\2',d)
    if access in ('Group','CUL'):
        grpdept = g.capitalize()
        grpdept = re.sub(r'(¹|²)g([0-9]*)',r'\1G\2',g)
    else:
        grpdept = d.replace('D[0-9]%','Youth').replace('Mw[0-9]%','MW').replace('24', '24 Dept').replace('%', 'Church')
        
    
    print(f"bbinactive parameters:          g = '{g}'          d = '{d}'          sid = {sid}          access = '{access}'")
    
    conn = odbc.connect(conn_str)
    bb_mem    = f"SELECT Dept, Grp, MemberCode, pOld, bbME, cctI, pFA, bbFA FROM CodeyBBStatusMembers('{sid}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}' ORDER BY GID".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    bb_group  = f"SELECT Grp, SUM(pOld)pOld, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA FROM CodeyBBStatusMembers('{sid}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}' GROUP BY Grp, GID ORDER BY GID".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    bb_dept   = f"SELECT Dept, SUM(pOld)pOld, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA FROM CodeyBBStatusMembers('{sid}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}' GROUP BY Dept, DID ORDER BY DID".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    # bb_region = f"SELECT District, SUM(pOld)pOld, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA FROM CodeyBBStatusMembers('{sid}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}' GROUP BY District".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    bb_youth  = f"SELECT SUM(pOld)pOld, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA FROM CodeyBBStatusMembers('{sid}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}'".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    
    print(bb_group)
    
    dm = pd.read_sql(bb_mem, conn)
    dg = pd.read_sql(bb_group, conn)
    dd = pd.read_sql(bb_dept, conn)
    # dr = pd.read_sql(bb_region, conn)
    dy = pd.read_sql(bb_youth, conn)

    dm.columns = ['Dept','Grp','Member','pOld','bbME','cctI','pFA','bbFA']
    dg.columns = ['Grp','pOld','bbME','cctI','pFA','bbFA']
    dd.columns = ['Dept','pOld','bbME','cctI','pFA','bbFA']
    # dr.columns = ['Region','pOld','bbME','cctI','pFA','bbFA']
    dy.columns = ['pOld','bbME','cctI','pFA','bbFA']
    dd.replace(r' Dept',r'', regex = True, inplace = True)
    
    conn.cursor().close()

    member = str()
    if access in ('Group','CUL'):
        for r in range(len(dm)):
            bbt =   str(dm.loc[r,'Member'][:5]) + ' '*(5-len(str(dm.loc[r,'Member'][:5])))
            po  = ' '*(4-len(str(dm.loc[r,'pOld']))) + str(dm.loc[r,'pOld'])
            bm  = ' '*(4-len(str(dm.loc[r,'bbME']))) + str(dm.loc[r,'bbME'])
            ci  = ' '*(4-len(str(dm.loc[r,'cctI']))) + str(dm.loc[r,'cctI'])
            pf  = ' '*(4-len(str(dm.loc[r,'pFA'])))  + str(dm.loc[r,'pFA'])
            bf  = ' '*(4-len(str(dm.loc[r,'bbFA']))) + str(dm.loc[r,'bbFA'])
            member = f'{member}{bbt}[{po}|{bm}|{ci}||{pf}|{bf}]\n'
        member = member + '\n'
            
            
    group = str()    
    for r in range(len(dg)):
        grp =   str(dg.loc[r,'Grp']) + ' '*(5-len(str(dg.loc[r,'Grp'])))
        po  = ' '*(4-len(str(dg.loc[r,'pOld']))) + str(dg.loc[r,'pOld'])
        bm  = ' '*(4-len(str(dg.loc[r,'bbME']))) + str(dg.loc[r,'bbME'])
        ci  = ' '*(4-len(str(dg.loc[r,'cctI']))) + str(dg.loc[r,'cctI'])
        pf  = ' '*(4-len(str(dg.loc[r,'pFA'])))  + str(dg.loc[r,'pFA'])
        bf  = ' '*(4-len(str(dg.loc[r,'bbFA']))) + str(dg.loc[r,'bbFA'])
        group = f'{group}{grp}[{po}|{bm}|{ci}||{pf}|{bf}]\n'
    group = group + '\n'
            
    dept = str()  
    if access not in ('Group','CUL'):
        for r in range(len(dd)):
            dpt =   str(dd.loc[r,'Dept']) + ' '*(5-len(str(dd.loc[r,'Dept'])))
            po  = ' '*(4-len(str(dd.loc[r,'pOld']))) + str(dd.loc[r,'pOld'])
            bm  = ' '*(4-len(str(dd.loc[r,'bbME']))) + str(dd.loc[r,'bbME'])
            ci  = ' '*(4-len(str(dd.loc[r,'cctI']))) + str(dd.loc[r,'cctI'])
            pf  = ' '*(4-len(str(dd.loc[r,'pFA'])))  + str(dd.loc[r,'pFA'])
            bf  = ' '*(4-len(str(dd.loc[r,'bbFA']))) + str(dd.loc[r,'bbFA'])
            dept = f'{dept}{dpt}[{po}|{bm}|{ci}||{pf}|{bf}]\n'
        dept = dept + '\n'
    
    # region = str()
    # if d.endswith('D[0-9]%'):    
    #     for r in range(len(dr)):
    #         reg =   str(dr.loc[r,'Region']) + ' '*(5-len(str(dr.loc[r,'Region'])))
    #         po  = ' '*(4-len(str(dr.loc[r,'pOld']))) + str(dr.loc[r,'pOld'])
    #         bm  = ' '*(4-len(str(dr.loc[r,'bbME']))) + str(dr.loc[r,'bbME'])
    #         ci  = ' '*(4-len(str(dr.loc[r,'cctI']))) + str(dr.loc[r,'cctI'])
    #         pf  = ' '*(4-len(str(dr.loc[r,'pFA'])))  + str(dr.loc[r,'pFA'])
    #         bf  = ' '*(4-len(str(dr.loc[r,'bbFA']))) + str(dr.loc[r,'bbFA'])
    #         region = f'{region}{reg}[{po}|{bm}|{ci}||{pf}|{bf}]\n'
    #     region = region + '\n'
    
    total = str()
    if d in ('D[0-9]%','%'):
        po  = ' '*(4-len(str(dy.loc[0,'pOld']))) + str(dy.loc[0,'pOld'])
        bm  = ' '*(4-len(str(dy.loc[0,'bbME']))) + str(dy.loc[0,'bbME'])
        ci  = ' '*(4-len(str(dy.loc[0,'cctI']))) + str(dy.loc[0,'cctI'])
        pf  = ' '*(4-len(str(dy.loc[0,'pFA'])))  + str(dy.loc[0,'pFA'])
        bf  = ' '*(4-len(str(dy.loc[0,'bbFA']))) + str(dy.loc[0,'bbFA'])
        total = f'Total[{po}|{bm}|{ci}||{pf}|{bf}]\n'
    
    summary = f"<b><u>{grpdept} Inactive BB Status Summary</u></b>\n\n<pre>     [ OP | ME | CI || FP | FA ]\n\n{member}{group}{dept}{total}</pre>"
    summary = re.sub(r'\.0',r'  ',summary) # Replaces '.0' with empty space
    summary = re.sub(r'(\D)0([^.])',r'\1-\2',summary)   # Replaces lone '0' with '-'
    print(">>>Return")
    return summary




def deptbbinactive(d, sid, access): # BB FUNCTIONS
    print(f"\n>>>deptbbinactive: d={d}, sid={sid}, access={access}")
                
    d = d.capitalize().replace('d','D')
    d = re.sub(r'(¹|²)d([0-9]*)',r'\1D\2',d)
    grpdept = d.replace('D[0-9]%','Youth').replace('Mw[0-9]%','MW').replace('24', '24 Dept').replace('%', 'Church')
        
    print(f"bbinactive parameters:          d = '{d}'          sid = {sid}          access = '{access}'")
    
    conn = odbc.connect(conn_str)
    bb_dept   = f"SELECT Dept, SUM(pOld)pOld, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA FROM CodeyBBStatusMembers('{sid}') WHERE Dept LIKE '{d}' GROUP BY Dept, DID ORDER BY DID".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    # bb_region = f"SELECT District, SUM(pOld)pOld, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA FROM CodeyBBStatusMembers('{sid}') WHERE Dept LIKE '{d}' GROUP BY District".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    bb_youth  = f"SELECT SUM(pOld)pOld, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA FROM CodeyBBStatusMembers('{sid}') WHERE Dept LIKE '{d}'".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
        
    dd = pd.read_sql(bb_dept, conn)
    # dr = pd.read_sql(bb_region, conn)
    dy = pd.read_sql(bb_youth, conn)

    dd.columns = ['Dept','pOld','bbME','cctI','pFA','bbFA']
    # dr.columns = ['Region','pOld','bbME','cctI','pFA','bbFA']
    dy.columns = ['pOld','bbME','cctI','pFA','bbFA']
    dd.replace(r' Dept',r'', regex = True, inplace = True)
    
    conn.cursor().close()
            
    dept = str()  
    if access not in ('Group','CUL'):
        for r in range(len(dd)):
            dpt =   str(dd.loc[r,'Dept']) + ' '*(5-len(str(dd.loc[r,'Dept'])))
            po  = ' '*(4-len(str(dd.loc[r,'pOld']))) + str(dd.loc[r,'pOld'])
            bm  = ' '*(4-len(str(dd.loc[r,'bbME']))) + str(dd.loc[r,'bbME'])
            ci  = ' '*(4-len(str(dd.loc[r,'cctI']))) + str(dd.loc[r,'cctI'])
            pf  = ' '*(4-len(str(dd.loc[r,'pFA'])))  + str(dd.loc[r,'pFA'])
            bf  = ' '*(4-len(str(dd.loc[r,'bbFA']))) + str(dd.loc[r,'bbFA'])
            dept = f'{dept}{dpt}[{po}|{bm}|{ci}||{pf}|{bf}]\n'
        dept = dept + '\n'
    
    # region = str()
    # if d.endswith('D[0-9]%'):    
    #     for r in range(len(dr)):
    #         reg =   str(dr.loc[r,'Region']) + ' '*(5-len(str(dr.loc[r,'Region'])))
    #         po  = ' '*(4-len(str(dr.loc[r,'pOld']))) + str(dr.loc[r,'pOld'])
    #         bm  = ' '*(4-len(str(dr.loc[r,'bbME']))) + str(dr.loc[r,'bbME'])
    #         ci  = ' '*(4-len(str(dr.loc[r,'cctI']))) + str(dr.loc[r,'cctI'])
    #         pf  = ' '*(4-len(str(dr.loc[r,'pFA'])))  + str(dr.loc[r,'pFA'])
    #         bf  = ' '*(4-len(str(dr.loc[r,'bbFA']))) + str(dr.loc[r,'bbFA'])
    #         region = f'{region}{reg}[{po}|{bm}|{ci}||{pf}|{bf}]\n'
    #     region = region + '\n'
    
    total = str()
    if d in ('D[0-9]%','%'):
        po  = ' '*(4-len(str(dy.loc[0,'pOld']))) + str(dy.loc[0,'pOld'])
        bm  = ' '*(4-len(str(dy.loc[0,'bbME']))) + str(dy.loc[0,'bbME'])
        ci  = ' '*(4-len(str(dy.loc[0,'cctI']))) + str(dy.loc[0,'cctI'])
        pf  = ' '*(4-len(str(dy.loc[0,'pFA'])))  + str(dy.loc[0,'pFA'])
        bf  = ' '*(4-len(str(dy.loc[0,'bbFA']))) + str(dy.loc[0,'bbFA'])
        total = f'Total[{po}|{bm}|{ci}||{pf}|{bf}]\n'
    
    summary = f"<b><u>{grpdept} Inactive BB Status Summary</u></b>\n\n<pre>     [ OP | ME | CI || FP | FA ]\n\n{dept}{total}</pre>"
    summary = re.sub(r'\.0',r'  ',summary) # Replaces '.0' with empty space
    summary = re.sub(r'(\D)0([^.])',r'\1-\2',summary)   # Replaces lone '0' with '-'
    print(">>>Return")
    return summary









def fmlist(g): # FMP FUNCTIONS
    print(f"\n>>>fmlist: g={g}")
    conn = odbc.connect(conn_str)
    dN = pd.read_sql(f"SELECT * FROM ScottNewM('{g}') WHERE M_Status = 'NewM' ORDER BY M_TIME DESC", conn)
    dO = pd.read_sql(f"SELECT * FROM ScottNewM('{g}') WHERE M_Status = 'OldM' ORDER BY M_TIME DESC", conn)
    dPts = pd.read_sql(f"SELECT M_Status, SUM(Pts)Pts FROM ScottNewM('{g}') GROUP BY M_Status", conn)
    dN.columns = ['UID','M_TIME','FishName','M1N','M1G','M1P','M2N','M2G','M2P','P_TIME','M_Status','Pts']
    dO.columns = ['UID','M_TIME','FishName','M1N','M1G','M1P','M2N','M2G','M2P','P_TIME','M_Status','Pts']
    dPts.columns = ['M_Status','Pts']
    dN['M_TIME'] = pd.to_datetime(dN['M_TIME']).dt.strftime('%a %d/%m')
    dO['M_TIME'] = pd.to_datetime(dO['M_TIME']).dt.strftime('%a %d/%m')
    dPts.set_index('M_Status', inplace=True)
    conn.cursor().close()
    
    nPt,oPt = 0,0
    g = g.capitalize()
    g = re.sub(r'(¹|²)g([0-9]*)',r'\1G\2',g)
    
    if len(dN) == 0:
        nM = ''
    else:
        nPt = dPts.loc['NewM','Pts']
        nM = f"<i><b><u>New Meetings ({nPt} pt)</u></b></i>\n"
        for r in range(len(dN)):
            nM = f"{nM}<pre>❤️{r+1}. [{dN.loc[r,'Pts']}] {dN.loc[r,'FishName'][:8]} - {dN.loc[r,'M1N'][:8]} ({dN.loc[r,'M1G']}) / {dN.loc[r,'M2N'][:11]} ({dN.loc[r,'M2G']}) - [{dN.loc[r,'M_TIME']}]</pre>\n"
        nM = nM + '\n'
        
    if len(dO) == 0:
        oM = ''
    else:
        oPt = dPts.loc['OldM','Pts']
        oM = f"<i><b><u>Old Meetings ({oPt} pt)</u></b></i>\n"
        for r in range(len(dO)):
            oM = f"{oM}<pre>🧡{r+1}. [{dO.loc[r,'Pts']}] {dO.loc[r,'FishName'][:8]} - {dO.loc[r,'M1N'][:8]} ({dO.loc[r,'M1G']}) / {dO.loc[r,'M2N'][:11]} ({dO.loc[r,'M2G']}) - [{dO.loc[r,'M_TIME']}]</pre>\n"
        oM = oM + '\n'
    
    result = f"<b><u>{g} Meeting List</u></b>\n\n{nM}{oM}"
    result = result = re.sub(r'\/  \(\) ',r'',result)
    result = re.sub(r'\[1\.0\] ', r'', result)
    print(">>>Return")
    return result



def fmstatus(d,g,ssnstart,access): # FMP FUNCTIONS
    print(f"\n>>>fmstatus: d={d}, g={g}, ssnstart={ssnstart}, access={access}")
        
    conn = odbc.connect(conn_str)                        
    dm = pd.read_sql(f"SELECT MemberCode, NewM, OldM FROM CodeyOldNewM('%','{g}','{ssnstart}') ORDER BY MemberCode", conn)
    dg = pd.read_sql(f"SELECT Grp, SUM(NewM)NewM, SUM(OldM)OldM FROM CodeyOldNewM('{d}','%','{ssnstart}') GROUP BY Grp", conn)
    dg = pd.read_sql(f"SELECT Dept, SUM(NewM)NewM, SUM(OldM)OldM FROM CodeyOldNewM('D[0-9]%','%','{ssnstart}') GROUP BY Dept", conn)
    dt = pd.read_sql(f"SELECT SUM(NewM)NewM, SUM(OldM)OldM FROM CodeyOldNewM('{d}','{g}','{ssnstart}')", conn)
    dm.columns = ['Member','NewM','OldM']
    dt.columns = ['NewM','OldM']
    g = g.capitalize()
    g = re.sub(r'(¹|²)g([0-9]*)',r'\1G\2',g)
    conn.cursor().close()
    
    if len(dm) == 0:
        print(">>>Return")
        return "No members found"
    else:  
        member = str()
        for r in range(len(dm)):
            mem = str(dm.loc[r,'Member'])[:8] + ' '*(8-len(str(dm.loc[r,'Member'])[:8]))
            nm  = ' '*(4-len(str(dm.loc[r,'NewM'])))  + str(dm.loc[r,'NewM'])
            om  = ' '*(4-len(str(dm.loc[r,'OldM'])))  + str(dm.loc[r,'OldM'])
            member = f'{member}{mem}[{nm}|{om}]\n'
        nm = ' '*(4-len(str(dt.loc[0,'NewM'])))  + str(dt.loc[0,'NewM'])
        om = ' '*(4-len(str(dt.loc[0,'OldM'])))  + str(dt.loc[0,'OldM'])
        total = f"Total   [{nm}|{om}]"
        
        member = f"<b><u>{g} FM Status</u></b>\n\n<pre>Member  [NewM|OldM]\n\n{member}\n{total}</pre>"
        member = re.sub(r'\.0',r'  ',member) # Replaces '.0' with empty space
        member = re.sub(r'(\D)0([^.])',r'\1-\2',member)   # Replaces lone '0' with '-'
        print(">>>Return")
    return member
    
    
    


def bbtdept(d,sid): # BBT FUNCTIONS
    print(f"\n>>>bbtdept: d={d}, sid={sid}")
    conn = odbc.connect(conn_str)
    header = "🏛BBT Status Summary🏛"
    bb_dept = f"""SELECT Dept, SUM(pNew)pNew, SUM(pOld)pOld, SUM(bbA)bbA, SUM(bbME)bbME, SUM(bbFA)bbFA, SUM(pFA)pFA, SUM(cctA)cctA,  SUM(cctI)cctI,  SUM(Total)Total
FROM CodeyBBTStatusMembers('{sid}')
WHERE Dept LIKE '{d}'
GROUP BY Dept WITH ROLLUP"""
    print(bb_dept)
    dd = pd.read_sql(bb_dept, conn)
    conn.cursor().close()

    dd.columns = ['Dept','pNew','pOld','bbA','bbME','bbFA','pFA','cctA','cctI','Total']
    
    title = '[ NP| OP| AB| ME| FA| FP| CA| CI|Tot]'

    dept = str()
    for r in range(len(dd)):
        dpt = str(dd.loc[r,'Dept'])[:3] + ' '*(3-len(str(dd.loc[r,'Dept'])[:3]))
        pn  = ' '*(3-len(str(dd.loc[r,'pNew']))) + str(dd.loc[r,'pNew'])
        po  = ' '*(3-len(str(dd.loc[r,'pOld']))) + str(dd.loc[r,'pOld'])
        ba  = ' '*(3-len(str(dd.loc[r,'bbA'])))  + str(dd.loc[r,'bbA'])
        bm  = ' '*(3-len(str(dd.loc[r,'bbME']))) + str(dd.loc[r,'bbME'])
        bf  = ' '*(3-len(str(dd.loc[r,'bbFA']))) + str(dd.loc[r,'bbFA'])
        pf  = ' '*(3-len(str(dd.loc[r,'pFA'])))  + str(dd.loc[r,'pFA'])
        ca  = ' '*(3-len(str(dd.loc[r,'cctA']))) + str(dd.loc[r,'cctA'])
        ci  = ' '*(3-len(str(dd.loc[r,'cctI']))) + str(dd.loc[r,'cctI'])
        t   = ' '*(3-len(str(dd.loc[r,'Total'])))  + str(dd.loc[r,'Total'])
        dept = f'{dept}{dpt}[{pn}|{po}|{ba}|{bm}|{bf}|{pf}|{ca}|{ci}|{t}]\n' 
                
    result = f"<b><u>{header}</u></b>\n\n<pre>Dpt{title}\n\n{dept}</pre>"
    result = re.sub(r'\|]',r']',result)  # Replaces '|]' with ']'
    result = re.sub(r'\.0',r'  ',result) # Replaces '.0' with empty space
    result = re.sub(r'(\D)0([^.])',r'\1-\2',result)   # Replaces lone '0' with '-'
    result = result.replace('\nNon','\n\nTot') # Shifts bottom Title row down one line
    print(">>>Return")
    return result



def bbtbtmstatus(r): # BBT FUNCTIONS
    print(f"\n>>>bbtbtmstatus: r={r}")
    print(">>>Return")
    return 'This function is deprecated'
    conn = odbc.connect(conn_str)
    header = "🏛BBT Status Summary🏛"
    bb_dept = f"""SELECT BBTStatus,NP,OP,AB,IB,FA,FP,CA,CI,Total FROM (
    SELECT CASE WHEN BBTStatus = 'BBT' THEN 2 ELSE 1 END AS Num, BBTStatus, SUM(NP)NP, SUM(OP)OP, SUM(AB)AB, SUM(IB)IB, SUM(FA)FA, SUM(FP)FP, SUM(CA)CA, SUM(CI)CI, SUM(Total)Total
                    FROM (SELECT CASE WHEN Status = 'Active' Then 'BBT' ELSE BTMNO END AS BBTStatus, * FROM BBTPerformanceView) B
                    GROUP BY BBTStatus
    UNION ALL
    SELECT 3 Num, 'Total', SUM(NP)NP, SUM(OP)OP, SUM(AB)AB, SUM(IB)IB, SUM(FA)FA, SUM(FP)FP, SUM(CA)CA, SUM(CI)CI, SUM(Total)Total
                    FROM (SELECT CASE WHEN Status = 'Active' Then 'BBT' ELSE BTMNO END AS BBTStatus, * FROM BBTPerformanceView) B
                    ) s 
                    ORDER BY Num, BBTStatus"""
    dd = pd.read_sql(bb_dept, conn)
    conn.cursor().close()
    dd = dd.transpose()
    dd.reset_index(inplace=True)

    rowtitles = ['BBT Status ','NP   ','OP   ','AB   ','ME   ','FA   ','FP   ','CA   ','CI   ','Tot  ']

    dept = str()
    for r in range(1,10):
        dept = f"{dept}{rowtitles[r]}["
        for c in range(len(dd.columns)-1):
            dept = f"{dept}{' '*(3-len(str(dd.loc[r,c])))}{dd.loc[r,c]}|"
        dept = f"{dept}]\n"
    
    title = '[ 14| 15|W12|BBT|Tot]'
        
    result = f"<b><u>{header}</u></b>\n\n<pre>BBT  {title}\n\n{dept}</pre>"
    result = re.sub(r'\|]',r']',result)  # Replaces '|]' with ']'
    result = re.sub(r'\.0',r'  ',result) # Replaces '.0' with empty space
    result = re.sub(r'(\D)0([^.])',r'\1-\2',result)   # Replaces lone '0' with '-'
    result = result.replace('\nTot','\n\nTot') # Shifts bottom Title row down one line
    print(">>>Return")
    return result


def whofish(ph): # IT FUNCTIONS
    print(f"\n>>>whofish: ph={ph}")
    print(">>>Return")
    return "fished by . . ."







def ev(id): # IT FUNCTIONS
    print(f"\n>>>ev: id={id}")
    conn = odbc.connect(conn_str)
    
    df   = pd.read_sql(f"SELECT * FROM ScottTwoWeekFishID({id})", conn)
    dfPt = pd.read_sql(f"SELECT SUM(Points)Pts FROM ScottTwoWeekFishID({id})", conn)
    
    dN =   pd.read_sql(f"SELECT * FROM ScottNewMID({id}) WHERE M_Status = 'NewM' ORDER BY M_TIME DESC", conn)
    dO =   pd.read_sql(f"SELECT * FROM ScottNewMID({id}) WHERE M_Status = 'OldM' ORDER BY M_TIME DESC", conn)
    dmPt = pd.read_sql(f"SELECT M_Status, SUM(Pts)Pts FROM ScottNewMID({id}) GROUP BY M_Status", conn)
    
    dNP  = pd.read_sql(f"SELECT * FROM ScottNewStatusID({id}) WHERE NewStatus = 'New P'", conn)
    dOP  = pd.read_sql(f"SELECT * FROM ScottNewStatusID({id}) WHERE NewStatus = 'Old P'", conn)
    dAB  = pd.read_sql(f"SELECT * FROM ScottNewStatusID({id}) WHERE NewStatus = 'ABB'", conn)
    dIM  = pd.read_sql(f"SELECT * FROM ScottNewStatusID({id}) WHERE NewStatus = 'IBB ME'", conn)
    dIF  = pd.read_sql(f"SELECT * FROM ScottNewStatusID({id}) WHERE NewStatus = 'IBB FA'", conn)
    dFP  = pd.read_sql(f"SELECT * FROM ScottNewStatusID({id}) WHERE NewStatus = 'Fallen P'", conn)
    dAC  = pd.read_sql(f"SELECT * FROM ScottNewStatusID({id}) WHERE NewStatus = 'ABB CCT'", conn)
    dIC  = pd.read_sql(f"SELECT * FROM ScottNewStatusID({id}) WHERE NewStatus = 'IBB CCT'", conn)
    dpPt = pd.read_sql(f"SELECT NewStatus, SUM(Pts)Pts FROM ScottNewStatusID({id}) GROUP BY NewStatus", conn)
    
    conn.cursor().close()
    
    fish,nm,om,npk,op,ab,im,iff,fp,ac,ic = '','','','','','','','','','',''
    
    if len(df) > 0:
        df.columns = ['Timestamp','Fish','OL','OLG','Pts','HP']
        df['Timestamp'] = df['Timestamp'].dt.strftime('%a %d/%m')
        df.replace(np.nan, '', regex = True, inplace = True)
        pts = dfPt.iloc[0,0]
        
        for r in range(len(df)):
            ts = df.loc[r,'Timestamp']
            hp = df.loc[r,'HP']
            fname = df.loc[r,'Fish']
            ol = df.loc[r,'OL'][:11]
            olg = df.loc[r,'OLG']
            fish = f"{fish}🐟{r+1}. [{ts}] {hp}{fname}{ol} ({olg})\n"
        fish = f"<pre>{fish.replace(' ()','')}</pre>"
        fish = f"<b><u>Fish Last Two Weeks ({pts})</u></b>\n{fish}\n"

    dmPt.columns = ['M_Status','Pts']
    dmPt.set_index('M_Status', inplace=True)
    
    if len(dN) > 0:
        dN.columns = ['Timestamp','Fish','OL','OLG','Pts','HP','M_Status']
        dN['Timestamp'] = pd.to_datetime(dN['Timestamp']).dt.strftime('%a %d/%m')
        pts = dmPt.loc['NewM','Pts']
        for r in range(len(dN)):
            ts = dN.loc[r,'Timestamp']
            hp = dN.loc[r,'HP']
            fname = dN.loc[r,'Fish']
            ol = dN.loc[r,'OL'][:11]
            olg = dN.loc[r,'OLG']
            nm = f"{nm}❤️{r+1}. [{ts}] {hp}{fname}{ol} ({olg})\n"
        nm = f"<pre>{nm.replace(' ()','')}</pre>"
        nm = f"<i><b><u>New Meetings ({pts} pt)</u></b></i>\n{nm}\n"

    if len(dO) > 0:
        dO.columns = ['Timestamp','Fish','OL','OLG','Pts','HP','M_Status']
        dO['Timestamp'] = pd.to_datetime(dO['Timestamp']).dt.strftime('%a %d/%m')
        pts = dmPt.loc['OldM','Pts']
        for r in range(len(dO)):
            ts = dO.loc[r,'Timestamp']
            hp = dO.loc[r,'HP']
            fname = dO.loc[r,'Fish']
            ol = dO.loc[r,'OL'][:11]
            olg = dO.loc[r,'OLG']
            om = f"{om}🧡{r+1}. [{ts}] {hp}{fname}{ol} ({olg})\n"
        om = f"<pre>{om.replace(' ()','')}</pre>"
        om = f"<i><b><u>Old Meetings ({pts} pt)</u></b></i>\n{om}\n"

    dpPt.columns =  ['NewStatus','Pts']
    dpPt.set_index('NewStatus', inplace=True)
    
    if len(dNP) > 0:
        dNP.columns = ['BBT','BBTG','Fish','OL','OLG','Pts','NewStatus']
        pts = dpPt.loc['New P','Pts']
        for r in range(len(dNP)):
            bbt = dNP.loc[r,'BBT'][:8]
            bbtg = dNP.loc[r,'BBTG']
            fname = dNP.loc[r,'Fish']
            ol = dNP.loc[r,'OL'][:11]
            olg = dNP.loc[r,'OLG']
            npk = f"{npk}💛{r+1}. [{bbt} {bbtg}] {fname}{ol} ({olg})\n"
        npk = f"<pre>{npk.replace(' ()','')}</pre>"
        npk = f"<i><b><u>New Picking ({pts} pt)</u></b></i>\n{npk}\n"

    if len(dOP) > 0:
        dOP.columns = ['BBT','BBTG','Fish','OL','OLG','Pts','NewStatus']

        pts = dpPt.loc['Old P','Pts']
        for r in range(len(dOP)):
            bbt = dOP.loc[r,'BBT'][:8]
            bbtg = dOP.loc[r,'BBTG']
            fname = dOP.loc[r,'Fish']
            ol = dOP.loc[r,'OL'][:11]
            olg = dOP.loc[r,'OLG']
            op = f"{op}⛔️{r+1}. [{bbt} {bbtg}] {fname}{ol} ({olg})\n"
        op = f"<pre>{op.replace(' ()','')}</pre>"
        op = f"<i><b><u>Old Picking ({pts} pt)</u></b></i>\n{op}\n"
    
    if len(dAB) > 0:
        dAB.columns = ['BBT','BBTG','Fish','OL','OLG','Pts','NewStatus']
        pts = dpPt.loc['ABB','Pts']
        for r in range(len(dAB)):
            bbt = dAB.loc[r,'BBT'][:8]
            bbtg = dAB.loc[r,'BBTG']
            fname = dAB.loc[r,'Fish']
            ol = dAB.loc[r,'OL'][:11]
            olg = dAB.loc[r,'OLG']
            ab = f"{ab}🟢{r+1}. [{bbt} {bbtg}] {fname}{ol} ({olg})\n"
        ab = f"<pre>{ab.replace(' ()','')}</pre>"
        ab = f"<i><b><u>Active BB ({pts} pt)</u></b></i>\n{ab}\n"
        
    if len(dIM) > 0:
        dIM.columns = ['BBT','BBTG','Fish','OL','OLG','Pts','NewStatus']
        pts = dpPt.loc['IBB ME','Pts']
        for r in range(len(dIM)):
            bbt = dIM.loc[r,'BBT'][:8]
            bbtg = dIM.loc[r,'BBTG']
            fname = dIM.loc[r,'Fish']
            ol = dIM.loc[r,'OL'][:11]
            olg = dIM.loc[r,'OLG']
            im = f"{im}🔴{r+1}. [{bbt} {bbtg}] {fname}{ol} ({olg})\n"
        im = f"<pre>{im.replace(' ()','')}</pre>"
        im = f"<i><b><u>IBB Missed Education ({pts} pt)</u></b></i>\n{im}\n"
        
    if len(dIF) > 0:
        dIF.columns = ['BBT','BBTG','Fish','OL','OLG','Pts','NewStatus']
        pts = dpPt.loc['IBB FA','Pts']
        for r in range(len(dIF)):
            bbt = dIF.loc[r,'BBT'][:8]
            bbtg = dIF.loc[r,'BBTG']
            fname = dIF.loc[r,'Fish']
            ol = dIF.loc[r,'OL'][:11]
            olg = dIF.loc[r,'OLG']
            iff = f"{iff}⚫️{r+1}. [{bbt} {bbtg}] {fname}{ol} ({olg})\n"
        iff = f"<pre>{iff.replace(' ()','')}</pre>"
        iff = f"<i><b><u>IBB Fallen ({pts} pt)</u></b></i>\n{iff}\n"
        
    if len(dFP) > 0:
        dFP.columns = ['BBT','BBTG','Fish','OL','OLG','Pts','NewStatus']
        pts = dpPt.loc['Fallen P','Pts']
        for r in range(len(dFP)):
            bbt = dFP.loc[r,'BBT'][:8]
            bbtg = dFP.loc[r,'BBTG']
            fname = dFP.loc[r,'Fish']
            ol = dFP.loc[r,'OL'][:11]
            olg = dFP.loc[r,'OLG']
            fp = f"{fp}❌{r+1}. [{bbt} {bbtg}] {fname}{ol} ({olg})\n"
        fp = f"<pre>{fp.replace(' ()','')}</pre>"
        fp = f"<i><b><u>Fallen Picking ({pts} pt)</u></b></i>\n{fp}\n"
        
    if len(dAC) > 0:
        dAC.columns = ['BBT','BBTG','Fish','OL','OLG','Pts','NewStatus']
        pts = dpPt.loc['ABB CCT','Pts']
        for r in range(len(dAC)):
            bbt = dAC.loc[r,'BBT'][:8]
            bbtg = dAC.loc[r,'BBTG']
            fname = dAC.loc[r,'Fish']
            ol = dAC.loc[r,'OL'][:11]
            olg = dAC.loc[r,'OLG']
            ac = f"{ac}⭐️{r+1}. [{bbt} {bbtg}] {fname}{ol} ({olg})\n"
        ac = f"<pre>{ac.replace(' ()','')}</pre>"
        ac = f"<i><b><u>CCT ABB ({pts} pt)</u></b></i>\n{ac}\n"
        
    if len(dIC) > 0:
        dIC.columns = ['BBT','BBTG','Fish','OL','OLG','Pts','NewStatus']
        pts = dpPt.loc['IBB CCT','Pts']
        for r in range(len(dIC)):
            bbt = dIC.loc[r,'BBT'][:8]
            bbtg = dIC.loc[r,'BBTG']
            fname = dIC.loc[r,'Fish']
            ol = dIC.loc[r,'OL'][:11]
            olg = dIC.loc[r,'OLG']
            ic = f"{npk}⭐️{r+1}. [{bbt} {bbtg}] {fname}{ol} ({olg})\n"
        ic = f"<pre>{npk.replace(' ()','')}</pre>"
        ic = f"<i><b><u>CCT IBB ({pts} pt)</u></b></i>\n{ic}\n"
    
    
    title = f"<b><u>📖{id} EV Summary📖</u></b>\n\n"
    format1 = f"<i>#. [Date] Fruit - Leaf2</i>\n" if f"{fish}{nm}{om}" != '' else ''
    format2 = f"<i>#. [BBT] Fruit - Leaf2</i>\n" if f"{npk}" != '' else ''
    result = f"{title}{format1}{fish}{nm}{om}{format2}{npk}{op}{ab}{im}{iff}{fp}{ac}{ic}"
    print(">>>Return")
    return result  
    




def classes(g, d, access, time): # BBT FUNCTIONS
    print(f"\n>>>classes: g={g}, d={d}, access={access}, time={time}")
    
    g = g if access in ('Group','CUL') else '%'
    d = d.capitalize()
    d = re.sub(r'(¹|²)d([0-9]*)',r'\1D\2',d)
    if access in ('Group','CUL'):
        grpdept = g.capitalize()
        grpdept = re.sub(r'(¹|²)g([0-9]*)',r'\1G\2',g)
    else:
        grpdept = str(d).replace('D[0-9]%','Youth')
    bbtgrp = 'BBT' if access in ('Group','CUL') else 'Grp'
    if time == 'today':
        timetitle = 'Today'
    if time == 'week':
        timetitle = 'This Week'
    
    conn = odbc.connect(conn_str)
    bb_mem = f"SELECT DisplayName, Classes FROM Classes{time}('{d}','{g}') WHERE DisplayName IS NOT NULL"
    bb_group = f"SELECT Grp, Classes FROM Classes{time}('{d}','{g}') WHERE Grp IS NOT NULL"
    bb_dept = f"SELECT Dept, Classes FROM Classes{time}('{d}','{g}') WHERE Dept IS NOT NULL"
    bb_youth = f"SELECT 'Total', Classes FROM Classes{time}('{d}','{g}') WHERE DisplayName IS NULL AND Grp IS NULL AND Dept IS NULL"

    print(bb_group)
    
    dm = pd.read_sql(bb_mem, conn)
    dg = pd.read_sql(bb_group, conn)
    dd = pd.read_sql(bb_dept, conn)
    dy = pd.read_sql(bb_youth, conn)

    dm.columns = ['Name','Classes']
    dg.columns = ['Grp','Classes']
    dd.columns = ['Dept','Classes']
    dy.columns = ['Total','Classes']
    dd.replace(r' Dept',r'', regex = True, inplace = True)
    
    conn.cursor().close()

    member = str()
    if access in ('Group','CUL'):
        member = '\n'
        for r in range(len(dm)):
            bbt =   str(dm.loc[r,'Name'][:5]) + ' '*(5-len(str(dm.loc[r,'Name'][:5])))
            cl  = ' '*(3-len(str(dm.loc[r,'Classes']))) + str(dm.loc[r,'Classes'])
            member = f'{member}{bbt}[{cl}]\n'
            
    group = '\n'
    for r in range(len(dg)):
        grp =   str(dg.loc[r,'Grp'][:5]) + ' '*(5-len(str(dg.loc[r,'Grp'][:5])))
        cl  = ' '*(3-len(str(dg.loc[r,'Classes']))) + str(dg.loc[r,'Classes'])
        group = f'{group}{grp}[{cl}]\n'
    
    dept = str()
    if g == '%':
        dept = '\n'
        for r in range(len(dd)):
            dpt = str(dd.loc[r,'Dept'])[:5]   + ' '*(5-len(str(dd.loc[r,'Dept'][:5])))
            cl  = ' '*(3-len(str(dd.loc[r,'Classes']))) + str(dd.loc[r,'Classes'])
            dept = f'{dept}{dpt}[{cl}]\n'
            
    youth = f"\nTot  [{' '*(3-len(str(dy.loc[0,'Classes'])))}{dy.loc[0,'Classes']}]\n" if g == '%' and d in ('D[0-9]%','%') else str()
    
    result = f"""<b><u>{grpdept} BB Classes {timetitle} </u></b>\n\n<pre>{bbtgrp}  [#Cl]\n{member}{group}{dept}{youth}</pre>"""
    result = re.sub(r'\.0',r'  ',result) # Replaces '.0' with empty space
    result = re.sub(r'(\D)0([^.])',r'\1-\2',result)   # Replaces lone '0' with '-'
    print(">>>Return")
    return result









def edu(day, g, d, access): # EDU FUNCTIONS
    print(f"\n>>>edu: day={day}, g={g}, d={d}, access={access}")
                
    g = g if access in ('Group','CUL') else '%'
    d = d.capitalize().replace('d','D')
    d = re.sub(r'(¹|²)d([0-9]*)',r'\1D\2',d)
    if access in ('Group','CUL'):
        grpdept = g.capitalize()
        grpdept = re.sub(r'(¹|²)g([0-9]*)',r'\1G\2',g)
    else:
        grpdept = d.replace('D[0-9]%','Youth').replace('Mw[0-9]%','MW').replace('24', '24 Dept').replace('%', 'Church')
    
    days = {'fri': ['FriAtt, FriOnl, FriRep, FriAbs',
                    'SUM(FriAtt), SUM(FriOnl), SUM(FriRep), SUM(FriAbs)',
                    'Friday Education Attendance Summary'],
            'sun': ['SunAtt, SunOnl, SunRep, SunAbs',
                    'SUM(SunAtt), SUM(SunOnl), SUM(SunRep), SUM(SunAbs)',
                    'Sunday Education Attendance Summary'],
            'mon': ['MonAtt, MonOnl, MonRep, MonAbs',
                    'SUM(MonAtt), SUM(MonOnl), SUM(MonRep), SUM(MonAbs)',
                    'Monday Education Attendance Summary'],
            'cubs': ['Cubs1R, Cubs1NR, Cubs2R, Cubs2NR',
                     'SUM(Cubs1R), SUM(Cubs1NR), SUM(Cubs2R), SUM(Cubs2NR)',
                    'CUBS Reading Summary']}
    
    columns = '[1R|1N|2R|2N]' if day == 'cubs' else '[AT|OL|RP|AB]'
    
    print(f"edu parameters:   day = '{day}'       g = '{g}'          d = '{d}'          access = '{access}'")
    
    conn = odbc.connect(conn_str)
    edu_group  = f"SELECT Grp, {days[day][0]} FROM CodeyEduWeekBreakdown WHERE Dept LIKE '{d}' AND Grp LIKE '{g}'".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    edu_dept   = f"SELECT Dept, {days[day][1]} FROM CodeyEduWeekBreakdown WHERE Dept LIKE '{d}' AND Grp LIKE '{g}' GROUP BY Dept, DID ORDER BY DID".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    # edu_region = f"SELECT Region, {days[day][1]} FROM CodeyEduWeekBreakdown WHERE Dept LIKE '{d}' AND Grp LIKE '{g}' GROUP BY Region".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    edu_youth  = f"SELECT {days[day][1]} FROM CodeyEduWeekBreakdown WHERE Dept LIKE '{d}' AND Grp LIKE '{g}'".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    
    print(edu_group)
    
    dg = pd.read_sql(edu_group, conn)
    dd = pd.read_sql(edu_dept, conn)
    # dr = pd.read_sql(edu_region, conn)
    dy = pd.read_sql(edu_youth, conn)

    dg.columns = ['Grp','Att','Onl','Rep','Abs']
    dd.columns = ['Dept','Att','Onl','Rep','Abs']
    # dr.columns = ['Region','Att','Onl','Rep','Abs']
    dy.columns = ['Att','Onl','Rep','Abs']
    dd.replace(r' Dept',r'', regex = True, inplace = True)
    
    conn.cursor().close()
          
    group = str()    
    for r in range(len(dg)):
        grp =   str(dg.loc[r,'Grp'])[:5] + ' '*(5-len(str(dg.loc[r,'Grp'])[:5]))
        at  = ' '*(2-len(str(dg.loc[r,'Att']))) + str(dg.loc[r,'Att'])
        on  = ' '*(2-len(str(dg.loc[r,'Onl']))) + str(dg.loc[r,'Onl'])
        rp  = ' '*(2-len(str(dg.loc[r,'Rep']))) + str(dg.loc[r,'Rep'])
        ab  = ' '*(2-len(str(dg.loc[r,'Abs']))) + str(dg.loc[r,'Abs'])
        group = f'{group}{grp}[{at}|{on}|{rp}|{ab}]\n'
    group = group + '\n'
            
    dept = str()  
    if access not in ('Group','CUL'):
        for r in range(len(dd)):
            dpt =   str(dd.loc[r,'Dept'])[:5] + ' '*(5-len(str(dd.loc[r,'Dept'])[:5]))
            at  = ' '*(2-len(str(dd.loc[r,'Att']))) + str(dd.loc[r,'Att'])
            on  = ' '*(2-len(str(dd.loc[r,'Onl']))) + str(dd.loc[r,'Onl'])
            rp  = ' '*(2-len(str(dd.loc[r,'Rep']))) + str(dd.loc[r,'Rep'])
            ab  = ' '*(2-len(str(dd.loc[r,'Abs']))) + str(dd.loc[r,'Abs'])
            dept = f'{dept}{dpt}[{at}|{on}|{rp}|{ab}]\n'
        dept = dept + '\n'
    
    # region = str()
    # if d.endswith('D[0-9]%'):    
    #     for r in range(len(dr)):
    #         reg =   str(dr.loc[r,'Region']) + ' '*(5-len(str(dr.loc[r,'Region'])))
    #         at  = ' '*(2-len(str(dr.loc[r,'Att']))) + str(dr.loc[r,'Att'])
    #         on  = ' '*(2-len(str(dr.loc[r,'Onl']))) + str(dr.loc[r,'Onl'])
    #         rp  = ' '*(2-len(str(dr.loc[r,'Rep']))) + str(dr.loc[r,'Rep'])
    #         ab  = ' '*(2-len(str(dr.loc[r,'Abs']))) + str(dr.loc[r,'Abs'])
    #         region = f'{region}{reg}[{at}|{on}|{rp}|{ab}]\n'
    #     region = region + '\n'
    
    total = str()
    if d in ('D[0-9]%','%'):
        at  = ' '*(2-len(str(dy.loc[0,'Att']))) + str(dy.loc[0,'Att'])
        on  = ' '*(2-len(str(dy.loc[0,'Onl']))) + str(dy.loc[0,'Onl'])
        rp  = ' '*(2-len(str(dy.loc[0,'Rep']))) + str(dy.loc[0,'Rep'])
        ab  = ' '*(2-len(str(dy.loc[0,'Abs']))) + str(dy.loc[0,'Abs'])
        total = f'Total[{at}|{on}|{rp}|{ab}]'
    
    summary = f"<b><u>{grpdept} {days[day][2]}</u></b>\n\n<pre>     {columns}\n\n{group}{dept}{total}</pre>"
    summary = re.sub(r'\.0',r'  ',summary) # Replaces '.0' with empty space
    summary = re.sub(r'(\D)0([^.])',r'\1-\2',summary)   # Replaces lone '0' with '-'
    print(">>>Return")
    return summary




def edurev(g, d, access): # EDU FUNCTIONS
    print(f"\n>>>edu: g={g}, d={d}, access={access}")
                
    g = g if access in ('Group','CUL') else '%'
    d = d.capitalize().replace('d','D')
    d = re.sub(r'(¹|²)d([0-9]*)',r'\1D\2',d)
    if access in ('Group','CUL'):
        grpdept = g.capitalize()
        grpdept = re.sub(r'(¹|²)g([0-9]*)',r'\1G\2',g)
    else:
        grpdept = d.replace('D[0-9]%','Youth').replace('Mw[0-9]%','MW').replace('24', '24 Dept').replace('%', 'Church')
        
    print(f"edu parameters:   g = '{g}'          d = '{d}'          access = '{access}'")
    
    conn = odbc.connect(conn_str)
    edu_group  = f"SELECT Grp, RevS, RevNS FROM CodeyEduWeekBreakdown WHERE Dept LIKE '{d}' AND Grp LIKE '{g}'".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    edu_dept   = f"SELECT Dept, SUM(RevS), SUM(RevNS) FROM CodeyEduWeekBreakdown WHERE Dept LIKE '{d}' AND Grp LIKE '{g}' GROUP BY Dept, DID ORDER BY DID".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    # edu_region = f"SELECT Region, SUM(RevS), SUM(RevNS) FROM CodeyEduWeekBreakdown WHERE Dept LIKE '{d}' AND Grp LIKE '{g}' GROUP BY Region".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    edu_youth  = f"SELECT SUM(RevS), SUM(RevNS) FROM CodeyEduWeekBreakdown WHERE Dept LIKE '{d}' AND Grp LIKE '{g}'".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    
    print(edu_group)
    
    dg = pd.read_sql(edu_group, conn)
    dd = pd.read_sql(edu_dept, conn)
    # dr = pd.read_sql(edu_region, conn)
    dy = pd.read_sql(edu_youth, conn)

    dg.columns = ['Grp','RevS','RevNS']
    dd.columns = ['Dept','RevS','RevNS']
    # dr.columns = ['Region','RevS','RevNS']
    dy.columns = ['RevS','RevNS']
    dd.replace(r' Dept',r'', regex = True, inplace = True)
    
    conn.cursor().close()
          
    group = str()    
    for r in range(len(dg)):
        grp =   str(dg.loc[r,'Grp']) + ' '*(5-len(str(dg.loc[r,'Grp'])))
        rs  = ' '*(2-len(str(dg.loc[r,'RevS']))) + str(dg.loc[r,'RevS'])
        rn  = ' '*(2-len(str(dg.loc[r,'RevNS']))) + str(dg.loc[r,'RevNS'])
        group = f'{group}{grp}[{rs}|{rn}]\n'
    group = group + '\n'
            
    dept = str()  
    if access not in ('Group','CUL'):
        for r in range(len(dd)):
            dpt =   str(dd.loc[r,'Dept']) + ' '*(5-len(str(dd.loc[r,'Dept'])))
            rs  = ' '*(2-len(str(dd.loc[r,'RevS']))) + str(dd.loc[r,'RevS'])
            rn  = ' '*(2-len(str(dd.loc[r,'RevNS']))) + str(dd.loc[r,'RevNS'])
            dept = f'{dept}{dpt}[{rs}|{rn}]\n'
        dept = dept + '\n'
    
    # region = str()
    # if d.endswith('D[0-9]%'):    
    #     for r in range(len(dr)):
    #         reg =   str(dr.loc[r,'Region']) + ' '*(5-len(str(dr.loc[r,'Region'])))
    #         rs  = ' '*(2-len(str(dr.loc[r,'RevS']))) + str(dr.loc[r,'RevS'])
    #         rn  = ' '*(2-len(str(dr.loc[r,'RevNS']))) + str(dr.loc[r,'RevNS'])
    #         region = f'{region}{reg}[{rs}|{rn}]\n'
    #     region = region + '\n'
    
    total = str()
    if d in ('D[0-9]%','%'):
        rs  = ' '*(2-len(str(dy.loc[0,'RevS']))) + str(dy.loc[0,'RevS'])
        rn  = ' '*(2-len(str(dy.loc[0,'RevNS']))) + str(dy.loc[0,'RevNS'])
        total = f'Total[{rs}|{rn}]'
    
    summary = f"<b><u>{grpdept} Revelation Speech Summary (Mon → Sun) </u></b>\n\n<pre>     [ S|NS]\n\n{group}{dept}{total}</pre>"
    summary = re.sub(r'\.0',r'  ',summary) # Replaces '.0' with empty space
    summary = re.sub(r'(\D)0([^.])',r'\1-\2',summary)   # Replaces lone '0' with '-'
    print(">>>Return")
    return summary


















def bbstatusdate(g, d, ssn, dt, access): # BB FUNCTIONS
    print(f"\n>>>bbstatusdate: g={g}, d={d}, ssn={ssn}, dt={dt}, access={access}")

    g = g if access in ('Group','CUL') else '%'
    d = d.capitalize().replace('d','D')
    d = re.sub(r'(¹|²)d([0-9]*)',r'\1D\2',d)
    if access in ('Group','CUL'):
        grpdept = g.capitalize()
        grpdept = re.sub(r'(¹|²)g([0-9]*)',r'\1G\2',g)
    else:
        grpdept = d.replace('D[0-9]%','Youth').replace('Mw[0-9]%','MW').replace('24', '24 Dept').replace('%', 'Church')
        
    
    print(f"bbstatus parameters:          g = '{g}'          d = '{d}'       ssn = '{ssn}'       dt = '{dt}'       access = '{access}'")
    
    conn = odbc.connect(conn_str)
    bb_mem    = f"SELECT Dept, Grp, MemberCode, pNew, pOld, bbA, cctA, bbME, cctI, pFA, bbFA, Total FROM CodeyBBStatusDate('{dt}','{ssn}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}' ORDER BY GID".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    bb_group  = f"SELECT Grp, SUM(pNew)pNew, SUM(pOld)pOld, SUM(bbA)bbA, SUM(cctA)cctA, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA, SUM(Total)Total FROM CodeyBBStatusDate('{dt}','{ssn}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}' GROUP BY Grp, GID ORDER BY GID".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    bb_dept   = f"SELECT Dept, SUM(pNew)pNew, SUM(pOld)pOld, SUM(bbA)bbA, SUM(cctA)cctA, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA, SUM(Total)Total FROM CodeyBBStatusDate('{dt}','{ssn}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}' GROUP BY Dept, DID ORDER BY DID".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    # bb_region = f"SELECT District, SUM(pNew)pNew, SUM(pOld)pOld, SUM(bbA)bbA, SUM(cctA)cctA, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA, SUM(Total)Total FROM CodeyBBStatusDate('{dt}','{ssn}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}' GROUP BY District".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    bb_youth  = f"SELECT SUM(pNew)pNew, SUM(pOld)pOld, SUM(bbA)bbA, SUM(cctA)cctA, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA, SUM(Total)Total FROM CodeyBBStatusDate('{dt}','{ssn}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}'".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    
    print(bb_group)
    
    dm = pd.read_sql(bb_mem, conn)
    dg = pd.read_sql(bb_group, conn)
    dd = pd.read_sql(bb_dept, conn)
    # dr = pd.read_sql(bb_region, conn)
    dy = pd.read_sql(bb_youth, conn)

    dm.columns = ['Dept','Grp','Member','pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
    dg.columns = ['Grp','pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
    dd.columns = ['Dept','pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
    # dr.columns = ['Region','pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
    dy.columns = ['pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
    dd.replace(r' Dept',r'', regex = True, inplace = True)
    
    conn.cursor().close()

    member = str()
    if access in ('Group','CUL'):
        for r in range(len(dm)):
            bbt =   str(dm.loc[r,'Member'][:5]) + ' '*(5-len(str(dm.loc[r,'Member'][:5])))
            pn  = ' '*(4-len(str(dm.loc[r,'pNew']))) + str(dm.loc[r,'pNew'])
            po  = ' '*(4-len(str(dm.loc[r,'pOld']))) + str(dm.loc[r,'pOld'])
            ba  = ' '*(4-len(str(dm.loc[r,'bbA'])))  + str(dm.loc[r,'bbA'])
            ca  = ' '*(4-len(str(dm.loc[r,'cctA']))) + str(dm.loc[r,'cctA'])
            bm  = ' '*(4-len(str(dm.loc[r,'bbME']))) + str(dm.loc[r,'bbME'])
            ci  = ' '*(4-len(str(dm.loc[r,'cctI']))) + str(dm.loc[r,'cctI'])
            pf  = ' '*(4-len(str(dm.loc[r,'pFA'])))  + str(dm.loc[r,'pFA'])
            bf  = ' '*(4-len(str(dm.loc[r,'bbFA']))) + str(dm.loc[r,'bbFA'])
            t   = ' '*(5-len(str(dm.loc[r,'Tot'])))  + str(dm.loc[r,'Tot'])
            member = f'{member}{bbt}[{pn}|{po}|{ba}|{ca}|{bm}|{ci}|{pf}|{bf}|{t}]\n'
        member = member + '\n'
            
            
    group = str()    
    for r in range(len(dg)):
        grp =   str(dg.loc[r,'Grp']) + ' '*(5-len(str(dg.loc[r,'Grp'])))
        pn  = ' '*(4-len(str(dg.loc[r,'pNew']))) + str(dg.loc[r,'pNew'])
        po  = ' '*(4-len(str(dg.loc[r,'pOld']))) + str(dg.loc[r,'pOld'])
        ba  = ' '*(4-len(str(dg.loc[r,'bbA'])))  + str(dg.loc[r,'bbA'])
        ca  = ' '*(4-len(str(dg.loc[r,'cctA']))) + str(dg.loc[r,'cctA'])
        bm  = ' '*(4-len(str(dg.loc[r,'bbME']))) + str(dg.loc[r,'bbME'])
        ci  = ' '*(4-len(str(dg.loc[r,'cctI']))) + str(dg.loc[r,'cctI'])
        pf  = ' '*(4-len(str(dg.loc[r,'pFA'])))  + str(dg.loc[r,'pFA'])
        bf  = ' '*(4-len(str(dg.loc[r,'bbFA']))) + str(dg.loc[r,'bbFA'])
        t   = ' '*(5-len(str(dg.loc[r,'Tot'])))  + str(dg.loc[r,'Tot'])
        group = f'{group}{grp}[{pn}|{po}|{ba}|{ca}|{bm}|{ci}|{pf}|{bf}|{t}]\n'
    group = group + '\n'
            
    dept = str()  
    if access not in ('Group','CUL'):
        for r in range(len(dd)):
            dpt =   str(dd.loc[r,'Dept']) + ' '*(5-len(str(dd.loc[r,'Dept'])))
            pn  = ' '*(4-len(str(dd.loc[r,'pNew']))) + str(dd.loc[r,'pNew'])
            po  = ' '*(4-len(str(dd.loc[r,'pOld']))) + str(dd.loc[r,'pOld'])
            ba  = ' '*(4-len(str(dd.loc[r,'bbA'])))  + str(dd.loc[r,'bbA'])
            ca  = ' '*(4-len(str(dd.loc[r,'cctA']))) + str(dd.loc[r,'cctA'])
            bm  = ' '*(4-len(str(dd.loc[r,'bbME']))) + str(dd.loc[r,'bbME'])
            ci  = ' '*(4-len(str(dd.loc[r,'cctI']))) + str(dd.loc[r,'cctI'])
            pf  = ' '*(4-len(str(dd.loc[r,'pFA'])))  + str(dd.loc[r,'pFA'])
            bf  = ' '*(4-len(str(dd.loc[r,'bbFA']))) + str(dd.loc[r,'bbFA'])
            t   = ' '*(5-len(str(dd.loc[r,'Tot'])))  + str(dd.loc[r,'Tot'])
            dept = f'{dept}{dpt}[{pn}|{po}|{ba}|{ca}|{bm}|{ci}|{pf}|{bf}|{t}]\n'
        dept = dept + '\n'
    
    # region = str()
    # if d.endswith('D[0-9]%'):    
    #     for r in range(len(dr)):
    #         reg =   str(dr.loc[r,'Region']) + ' '*(5-len(str(dr.loc[r,'Region'])))
    #         pn  = ' '*(4-len(str(dr.loc[r,'pNew']))) + str(dr.loc[r,'pNew'])
    #         po  = ' '*(4-len(str(dr.loc[r,'pOld']))) + str(dr.loc[r,'pOld'])
    #         ba  = ' '*(4-len(str(dr.loc[r,'bbA'])))  + str(dr.loc[r,'bbA'])
    #         ca  = ' '*(4-len(str(dr.loc[r,'cctA']))) + str(dr.loc[r,'cctA'])
    #         bm  = ' '*(4-len(str(dr.loc[r,'bbME']))) + str(dr.loc[r,'bbME'])
    #         ci  = ' '*(4-len(str(dr.loc[r,'cctI']))) + str(dr.loc[r,'cctI'])
    #         pf  = ' '*(4-len(str(dr.loc[r,'pFA'])))  + str(dr.loc[r,'pFA'])
    #         bf  = ' '*(4-len(str(dr.loc[r,'bbFA']))) + str(dr.loc[r,'bbFA'])
    #         t   = ' '*(5-len(str(dr.loc[r,'Tot'])))  + str(dr.loc[r,'Tot'])
    #         region = f'{region}{reg}[{pn}|{po}|{ba}|{ca}|{bm}|{ci}|{pf}|{bf}|{t}]\n'
    #     region = region + '\n'
    
    total = str()
    if d in ('D[0-9]%','%'):
        pn  = ' '*(4-len(str(dy.loc[0,'pNew']))) + str(dy.loc[0,'pNew'])
        po  = ' '*(4-len(str(dy.loc[0,'pOld']))) + str(dy.loc[0,'pOld'])
        ba  = ' '*(4-len(str(dy.loc[0,'bbA'])))  + str(dy.loc[0,'bbA'])
        ca  = ' '*(4-len(str(dy.loc[0,'cctA']))) + str(dy.loc[0,'cctA'])
        bm  = ' '*(4-len(str(dy.loc[0,'bbME']))) + str(dy.loc[0,'bbME'])
        ci  = ' '*(4-len(str(dy.loc[0,'cctI']))) + str(dy.loc[0,'cctI'])
        pf  = ' '*(4-len(str(dy.loc[0,'pFA'])))  + str(dy.loc[0,'pFA'])
        bf  = ' '*(4-len(str(dy.loc[0,'bbFA']))) + str(dy.loc[0,'bbFA'])
        t   = ' '*(5-len(str(dy.loc[0,'Tot'])))  + str(dy.loc[0,'Tot'])
        total = f'Total[{pn}|{po}|{ba}|{ca}|{bm}|{ci}|{pf}|{bf}|{t}]'
    
    summary = f"<b><u>{grpdept} BB Status Summary</u></b>\n\n<pre>     [ NP | OP | AB | CA | ME | CI | FP | FA | TOT ]\n\n{member}{group}{dept}{total}</pre>"
    summary = re.sub(r'\.0',r'  ',summary) # Replaces '.0' with empty space
    summary = re.sub(r'(\D)0([^.])',r'\1-\2',summary)   # Replaces lone '0' with '-'
    print(">>>Return")
    return summary



def bbtmission(sid, d, g, standard, ct, access): # BBT FUNCTIONS
    print(f"\n>>>bbtmission: sid={sid}, d={d}, g={g}, standard={standard}, ct={ct}, access={access}")

    g = g if access in ('Group','CUL') else '%'
    grpdept = f'{g} ' if access in ('Group','CUL') else f'{d} '.replace('D[0-9]%','Youth').replace('% ','')
    filt = 0 if access in ('IT','EDU','All') else 1
    gd = 'Dept' if access in ('IT','EDU','All') else 'Grp '
    d = d.capitalize()

    sqlfn = f"ABB, P FROM BBTMissionTieBreaker('{sid}',{filt})" if standard == 'tie' else f"ActiveBBTs, TotalBBTs FROM ActiveBBTsFn('{sid}',{filt},'{standard}')"
    sql = f"SELECT Dept, PercentActive, {sqlfn} WHERE (Dept LIKE '{d}' AND Grp LIKE '{g}') OR Dept = ''".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    print(sql)

    conn = odbc.connect(conn_str)
    ds = pd.read_sql(sql, conn)
    ds.columns = ['Dept','PercentActive','ActiveBBTs','TotalBBTs']
    ds.replace(r' Dept',r'', regex = True, inplace = True)
    ds.replace(r'InnerSFT',r'InSFT', regex = True, inplace = True)
    ds.replace(r'Culture',r'Cul', regex = True, inplace = True)
    ds.replace(r'Serving',r'Sv', regex = True, inplace = True)
    conn.cursor().close()

    table = ''
    for r in range(len(ds)):
        dp =   str(ds.loc[r,'Dept'])[:5] + ' '*(5-len(str(ds.loc[r,'Dept'])))
        pa  = ' '*(4-len(str(ds.loc[r,'PercentActive'])))  + str(ds.loc[r,'PercentActive'])
        ab  = '  (' + ' '*(2-len(str(ds.loc[r,'ActiveBBTs']))) + str(ds.loc[r,'ActiveBBTs']) + '/'
        tb  = ' '*(2-len(str(ds.loc[r,'TotalBBTs']))) + str(ds.loc[r,'TotalBBTs']) + ')'
        table = f'{table}{dp}{pa}{ab}{tb}\n'

    timestamp = datetime.now(ZoneInfo("Australia/Melbourne")).strftime("%a %d %b, %I:%M %p")

    bbtstandard = {'pick': '🏃‍♀️Active BBT Standard: <b>Picking</b>',
                   'se': '🏃‍♀️Active BBT Standard: <b>Second Edu</b>',
                   'tie': '📏Standard: <b>Total SE / Total P</b>'}[standard]
    st = '' if standard == 'tie' else ' Standard'
    ctstandard = f'CT{st}: <b>{ct}</b>'
    info = f"<i>🕐{timestamp}\n{bbtstandard}\n👨‍🏫{ctstandard}</i>"

    title = 'BBT Mission Tiebreaker' if standard == 'tie' else 'Active BBT Rate'
    cols = 'SE/TP' if standard == 'tie' else 'AC/BT'
    summary = f"<b><u>{grpdept}{title}</u></b>\n{info}\n\n<pre>{gd} Prct  ({cols})\n\n{table}</pre>"
    summary = re.sub(r'(?<=\D)0\.0%',r'-   ',summary)
    summary = summary.replace('           ( 0/ 0)','').replace('\n\n\n','\n\n')
    print(">>>Return")
    return summary




def pickfe(g, d, access): # FMP FUNCTIONS
    print(f"\n>>>pickfe: g={g}, d={d}, access={access}")
                
    g = g if access in ('Group','CUL') else '%'
    d = d.capitalize().replace('d','D')
    d = re.sub(r'(¹|²)d([0-9]*)',r'\1D\2',d)
    if access in ('Group','CUL'):
        grpdept = g.capitalize()
        grpdept = re.sub(r'(¹|²)g([0-9]*)',r'\1G\2',g)
    else:
        grpdept = d.replace('D[0-9]%','Youth').replace('Mw[0-9]%','MW').replace('24', '24 Dept').replace('%', 'Church')
        
    conn = odbc.connect(conn_str)
    bb_mem    = f"SELECT Dept, Grp, MemberCode, PhysP, PhysFE, OnP, OnFE FROM CodeyPFE WHERE Dept LIKE '{d}' AND Grp LIKE '{g}' ORDER BY GID".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    bb_group  = f"SELECT Grp, SUM(PhysP)PhysP, SUM(PhysFE)PhysFE, SUM(OnP)OnP, SUM(OnFE)OnFE FROM CodeyPFE WHERE Dept LIKE '{d}' AND Grp LIKE '{g}' GROUP BY Grp, GID ORDER BY GID".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    bb_dept   = f"SELECT Dept, SUM(PhysP)PhysP, SUM(PhysFE)PhysFE, SUM(OnP)OnP, SUM(OnFE)OnFE FROM CodeyPFE WHERE Dept LIKE '{d}' AND Grp LIKE '{g}' GROUP BY Dept, DID ORDER BY DID".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    bb_youth  = f"SELECT SUM(PhysP)PhysP, SUM(PhysFE)PhysFE, SUM(OnP)OnP, SUM(OnFE)OnFE FROM CodeyPFE WHERE Dept LIKE '{d}' AND Grp LIKE '{g}'".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    
    print(bb_group)
    
    dm = pd.read_sql(bb_mem, conn)
    dg = pd.read_sql(bb_group, conn)
    dd = pd.read_sql(bb_dept, conn)
    dy = pd.read_sql(bb_youth, conn)

    dm.columns = ['Dept','Grp','Member','PhysP','PhysFE','OnP','OnFE']
    dg.columns = ['Grp','PhysP','PhysFE','OnP','OnFE']
    dd.columns = ['Dept','PhysP','PhysFE','OnP','OnFE']
    dy.columns = ['PhysP','PhysFE','OnP','OnFE']
    
    dd.replace(r' Dept',r'', regex = True, inplace = True)
    
    conn.cursor().close()

    member = str()
    if access in ('Group','CUL'):
        for r in range(len(dm)):
            mbr =   str(dm.loc[r,'Member'][:5]) + ' '*(5-len(str(dm.loc[r,'Member'][:5])))
            pp  = ' '*(4-len(str(dm.loc[r,'PhysP'])))  + str(dm.loc[r,'PhysP'])
            pf  = ' '*(4-len(str(dm.loc[r,'PhysFE']))) + str(dm.loc[r,'PhysFE'])
            op  = ' '*(4-len(str(dm.loc[r,'OnP'])))    + str(dm.loc[r,'OnP'])
            of  = ' '*(4-len(str(dm.loc[r,'OnFE'])))   + str(dm.loc[r,'OnFE'])
            member = f'{member}{mbr}[{pp}|{pf}|{op}|{of}]\n'        
        member = member + '\n'
            
    group = str()    
    for r in range(len(dg)):
        grp =   str(dg.loc[r,'Grp']) + ' '*(5-len(str(dg.loc[r,'Grp'])))
        pp  = ' '*(4-len(str(dg.loc[r,'PhysP'])))  + str(dg.loc[r,'PhysP'])
        pf  = ' '*(4-len(str(dg.loc[r,'PhysFE']))) + str(dg.loc[r,'PhysFE'])
        op  = ' '*(4-len(str(dg.loc[r,'OnP'])))    + str(dg.loc[r,'OnP'])
        of  = ' '*(4-len(str(dg.loc[r,'OnFE'])))   + str(dg.loc[r,'OnFE'])
        group = f'{group}{grp}[{pp}|{pf}|{op}|{of}]\n'
    group = group + '\n'
            
    dept = str()  
    if access not in ('Group','CUL'):
        for r in range(len(dd)):
            dpt =   str(dd.loc[r,'Dept']) + ' '*(5-len(str(dd.loc[r,'Dept'])))
            pp  = ' '*(4-len(str(dd.loc[r,'PhysP']))) + str(dd.loc[r,'PhysP'])
            pf  = ' '*(4-len(str(dd.loc[r,'PhysFE']))) + str(dd.loc[r,'PhysFE'])
            op  = ' '*(4-len(str(dd.loc[r,'OnP'])))  + str(dd.loc[r,'OnP'])
            of  = ' '*(4-len(str(dd.loc[r,'OnFE'])))   + str(dd.loc[r,'OnFE'])
            dept = f'{dept}{dpt}[{pp}|{pf}|{op}|{of}]\n'
        dept = dept + '\n'
    
    total = str()
    if d in ('D[0-9]%','%'):
        pp  = ' '*(4-len(str(dy.loc[0,'PhysP'])))  + str(dy.loc[0,'PhysP'])
        pf  = ' '*(4-len(str(dy.loc[0,'PhysFE']))) + str(dy.loc[0,'PhysFE'])
        op  = ' '*(4-len(str(dy.loc[0,'OnP'])))    + str(dy.loc[0,'OnP'])
        of  = ' '*(4-len(str(dy.loc[0,'OnFE'])))   + str(dy.loc[0,'OnFE'])
        total = f'Total[{pp}|{pf}|{op}|{of}]'
    
    header = f"     [  P | FE | oP | oFE]"
    summary = f"<b><u>{grpdept} Picking > FE</u></b>\n\n<pre>{header}\n\n{member}{group}{dept}{total}</pre>"
    summary = re.sub(r'\.0',r'  ',summary) # Replaces '.0' with empty space
    summary = re.sub(r'(\D)0([^.])',r'\1-\2',summary)   # Replaces lone '0' with '-'
    print(">>>Return")
    return summary


def test1(): # IT FUNCTIONS
    print(f"\n>>>test1")
    print(">>>Return")
    return "[D1 Va](https://drive.google.com/drive/folders/1xZ_VjGcOPp-xZmRtnlXpfBoQTMuE7sB4?usp=drive_link)\n[G1 Janel - Akot 🌟](https://docs.google.com/spreadsheets/d/1BqLj6p_Tw220zDs3w6s7JlVnZSiTFsWO3NLvnrk4W5M/edit?usp=drive_link)\n[G2 AJ - Natasha](https://docs.google.com/spreadsheets/d/1-Vw04M9YWeaEeLYN5fEKhiwj_Tl77jkjyq47HlMXAPs/edit?usp=drive_link)\n[G3 Karen - Mycah](https://docs.google.com/spreadsheets/d/1qXpYHxMUauxvLB1wCF1npw4Ol_1f4J7O5TwGc-R73SI/edit?usp=drive_link)\n[G4 Rohit - Ku Mo ❤️](https://docs.google.com/spreadsheets/d/1VTTUwilcpUUUuEsnbS1gaYMlY6tsxkyGogEoXcwmKq8/edit?usp=drive_link)\n\n[D2 Lun](https://drive.google.com/drive/folders/1dv0hvgh955L3AG0Bj9YTo8X76aTAhkHT?usp=drive_link)\n[G5 Wei Kin - Kiana 🌟](https://docs.google.com/spreadsheets/d/1HfzGRBESpDARQdVltQM5DtWA0EnSh51FnNxuRQ36iKc/edit?usp=drive_link)\n[G6 Priscilla - Vanessa ❤️](https://docs.google.com/spreadsheets/d/1l0zuKDcvGPMoaoiLbmwMjqyu-i0oI2LhNs59TOaamQA/edit?usp=drive_link)\n[G7 Kupa - Iokapeta ❤️](https://docs.google.com/spreadsheets/d/1l8qDSt-YDqmShvGwq91_RwNcguLOj9kkaqPRq6TF8dc/edit?usp=drive_link)\n[G8 Donia - Doreen](https://docs.google.com/spreadsheets/d/1zGLftSi4ldy1FzQ67ofeZdVE0O-iE9QGK4YGhO4Ciow/edit?usp=drive_link)\n\n[D3 King](https://drive.google.com/drive/folders/12Lx7EHVoUuciFeSm6MdT6qLx5hAuPgMP?usp=drive_link)\n[G9 Trucilla - Jhanice ❤️](https://docs.google.com/spreadsheets/d/13BkTDU5q0vS-_EUbet0H2ZxFFWQ02wvtkW0XUQEHb1Q/edit?usp=drive_link)\n[G10 Mary - Nic ❤️](https://docs.google.com/spreadsheets/d/1gJrP6ap3Dl0Lo9fK_72fvXhDCvxEHf_vMtds0HCco5g/edit?usp=drive_link)\n[G11 Aman - Yazmin ❤️](https://docs.google.com/spreadsheets/d/1gr1LMXtbshQ3MH7-mJH4ZLuKLgHvP2OJaZ38YRNDOpQ/edit?usp=drive_link)\n[G12 Alliza - Rachel 🌟](https://docs.google.com/spreadsheets/d/19bOGWcnArmwQUtfHEMb87dHnV-rnQ_LNNjtvbZlb2uE/edit?usp=drive_link)\n\n[D4 Nicola](https://drive.google.com/drive/folders/1JY318Dc_bWLj1jQwRQmsdF92AW_WqvUs?usp=drive_link)\n[G13 Rejie - Malu ❤️](https://docs.google.com/spreadsheets/d/1kJKvK5RT_S-A2n4GHBVu5_Ne_BC6Y6QjgpCwQtdxdJ4/edit?usp=drive_link)\n[G14 Lamy - Riz ❤️](https://docs.google.com/spreadsheets/d/1wceJg6hoghi2fwKRZXyQapcdp9YJ7rUD0ktJYU8y4Hg/edit?usp=drive_link)\n[G15 Mayom - Bianca 🌟](https://docs.google.com/spreadsheets/d/1gdv8_WSbu1i0P4Ffsp6QlV3HsSaCeXbMYOGQx3VSP3Q/edit?usp=drive_link)\n[G16 Cheyanne - Rachel ❤️](https://docs.google.com/spreadsheets/d/1jtDpQHdX2iOmGiv8g6KxIg4t1vsrOT5Y_pZt3ihiuDI/edit?usp=drive_link)\n\n[D5 Chelley](https://drive.google.com/drive/folders/1JY318Dc_bWLj1jQwRQmsdF92AW_WqvUs?usp=drive_link)\n[G17 Sosna - Ara ❤️](https://docs.google.com/spreadsheets/d/1qL5RbKq4X3UepKg9Tec9PsfG5l_E2YB6ICFxb9WaUGw/edit?usp=drive_link)\n[G18 Pamela - Tina ❤️](https://docs.google.com/spreadsheets/d/1fPWL4Fl7Z9iBDPFghlpogMAASK-8vCKi7zsB_zkhhTo/edit?usp=drive_link)\n[G19 Victoria - Josh ❤️](https://docs.google.com/spreadsheets/d/1TBwsSCREBGqGourVm_JadMGnufB_aPaMtMJvdxvSe54/edit?usp=drive_link)\n[G20 Matt K - Gabriel 🌟❤️](https://docs.google.com/spreadsheets/d/1hy9Kpf-k0nQAuHRrGz8TMGsSQXS1AmRcknaWQRDvPGk/edit?usp=drive_link)"

def test2(): # IT FUNCTIONS
    print(f"\n>>>test2")

    print(">>>Return")
    return "[D6 James](https://drive.google.com/drive/folders/1DQ0TK8j0PcKCjPDRCh6CpXN0C9G4vww-?usp=drive_link)\n[G21 Melvin - Flavi](https://docs.google.com/spreadsheets/d/1UAgd22ec2U9gHlml8rq3fiZw3mcsM4byV6Jnk883If0/edit?usp=drive_link)\n[G22 Sindy - Carys 🌟](https://docs.google.com/spreadsheets/d/1WPldJVSASulBAkgU-O7bc1smOtPYi1YYgnatY9UDvk4/edit?usp=drive_link)\n[G23 Maria - Charlotte](https://docs.google.com/spreadsheets/d/1CPkxTxHun4SgqBhwhdXMz9QVwCe1cHSZlN7L-yydLOc/edit?usp=drive_link)\n[G24 Vivian - Zephaniah❤️](https://docs.google.com/spreadsheets/d/1ZVzJBEwZrTGhVkJ1GYHl2IJ3EoJxFWuCVEUWoV-JVi4/edit?usp=drive_link)\n\n[D7 Kim](https://drive.google.com/drive/folders/1Ljt6hunDOWqeVJSMPRK6gHtWTHP2xQJv?usp=drive_link)\n[G25 Shiv - Tiam](https://docs.google.com/spreadsheets/d/1MmSyc111yFDtkpnkzC9wlkgkYkavYbQLMGRApKqHRKI/edit?usp=drive_link)\n[G26 Kathleen - Richard](https://docs.google.com/spreadsheets/d/1J3Di_todMI2Ax7J3Sn4eapwFRV0CyEbcfR2Hz1AiIBU/edit?usp=drive_link)\n[G27 Shaun - Janice](https://docs.google.com/spreadsheets/d/16rPrPDXVKyNJCtFXtbNEZyGpATx9p_DESya9h8diNx4/edit?usp=drive_link)\n[G28 Marielle - Sian 🌟❤️](https://docs.google.com/spreadsheets/d/1PoKIH4XjfKBPQQdjNLffX9TDG4pBwcr0v0aoelsrUnQ/edit?usp=drive_link)\n\n[D8 Christian](https://drive.google.com/drive/folders/1I6phtHFzs4VAOC526dgdpBUXzi70GXLH?usp=drive_link)\n[G29 Zindzi - Cherry 158 ❤️](https://docs.google.com/spreadsheets/d/1adoNCuOqs_sKlbBMl7I7jrtOVMJIPhXwSrkNV5OgppU/edit?usp=drive_link)\n[G30 John L - James](https://docs.google.com/spreadsheets/d/1az9JHj2LtLLlFHEs-CgZqKIH_XPLNJ4EAOktmvO8uJY/edit?usp=drive_link)\n[G31 Tam - Noah](https://docs.google.com/spreadsheets/d/1aNyl6GjFSe0tExdDhZF6_fc7wkuv1mmV2yXhDAtqSYc/edit?usp=drive_link)\n[G32 Chen Yee - Joshmar 🌟](https://docs.google.com/spreadsheets/d/14__SWTLgOBhLO-t634n0gnOW7lhAfW8TLfb1MfPiLS8/edit?usp=drive_link)\n\n[D9 Nahom](https://drive.google.com/drive/folders/1mgPLQbH9Yp451ZMMyfFog56SwKvMwNAc?usp=drive_link)\n[G33 Za Duh - Kaitu’u](https://docs.google.com/spreadsheets/d/1utd4bbPrLdJsYUDle9zKxGvNE8uxHr5SClPTgVDd958/edit?usp=drive_link)\n[G34 Genesis - Nelson 🌟](https://docs.google.com/spreadsheets/d/12QRCrRXq3_oGGYwW7tgOLh2ahKxb4icYvhKdiN_G5Wo/edit?usp=drive_link)\n[G35 Jeice - Cates](https://docs.google.com/spreadsheets/d/1klefvcXSXCHQjMlCuOvuxbHFHKPHqqMaItV5gUsNCXs/edit?usp=drive_link)\n[G36 Zia - Cardin❤️](https://docs.google.com/spreadsheets/d/1USrPxVlFaTK4JM_ofal7hGJvUvOuL3GQm_ZY4AH7nYE/edit?usp=drive_link)\n\n[D10 Hayden](https://drive.google.com/drive/folders/1Ik3XlftMrAyABj6ZG1BkdeMeYWaS91df?usp=drive_link)\n[G37 Mikko - Moana ❤️](https://docs.google.com/spreadsheets/d/1gSMqWSnN6okc38MOdQSzlljWHIxcIUOIqnHb3lrY0Fo/edit?usp=drive_link)\n[G38 Erica - Ivy ❤️](https://docs.google.com/spreadsheets/d/1Ni7D-pc0B6VfJJwHVysOSAYBT4Z9cHYYWIE0VFdrrrs/edit?usp=drive_link)\n[G39 Monica - Thao 🌟](https://docs.google.com/spreadsheets/d/1kcsiVPeoXplAfkriu7A80Unx3NLNEzh7lT7n58GYrPA/edit?usp=drive_link)\n[G40 Seena - Bez ❤️](https://docs.google.com/spreadsheets/d/1I9u_7KDfJBtKbbHjrOVvoFYTkT51ml133q_Yzb2kzHc/edit?usp=drive_link)\n\n[D11 Jade](https://drive.google.com/drive/folders/1pfWYyhw2kmVvcIij5Qar4ra-GzxUKBTc?usp=drive_link)\n[G41 Janice - Evan❤️](https://docs.google.com/spreadsheets/d/1dmrec5M7tsw3L-ebcwslZ-g4A8Fsfkzlv0_Qg92FbGQ/edit?usp=drive_link)\n[G42 Dilan - Juma❤️](https://docs.google.com/spreadsheets/d/1MjItYN8e-iucmSNOII1Kjkb_eAxUga_Sd_99GKfY0j8/edit?usp=drive_link)\n[G43 Micah - Larmay🌟❤️](https://docs.google.com/spreadsheets/d/1s6wT7diqG-pMEz52LwLKuK3uJLAlr9MRf0tOIoECMbk/edit?usp=drive_link)\n[G44 Elijah - Mia❤️](https://docs.google.com/spreadsheets/d/183wcSKMbsZxiIjIeRP09tFoMZlZqWReooYNTWHYFMfM/edit?usp=drive_link)"



    # return datetime.now(ZoneInfo("Australia/Melbourne")).strftime("%a %d %b, %I:%M %p")



def ctmissionnew(season, leaf, bbt, access, d, g, ct, plus, showgroup): # BB FUNCTIONS
    print(f"\n>>>ctmissionnew: season={season}, leaf={leaf}, bbt={bbt}, access={access}, d={d}, g={g}, ct={ct}, plus={plus}, showgroup={showgroup}")
    g = g if access in ('Group','CUL') else '%'
    d = d.capitalize().replace('d','D')
    grpdept = g.capitalize() if access in ('Group','CUL') else d.replace('D[0-9]%','Youth').replace('Mw[0-9]%','MW').replace('24', '24 Dept').replace('%', 'Church')

    q = f"SELECT * FROM CTMissionNew2('{season}', {leaf}, {bbt}, '{access}', '{d}', '{g}', 0)"
    q_grp = f"SELECT * FROM CTMissionNew2('{season}', {leaf}, {bbt}, '{access}', '{d}', '{g}', 1)"
    print(q)
    with odbc.connect(conn_str) as conn:
        dq = pd.read_sql(q, conn)
        dg = pd.read_sql(q_grp, conn)
    dq.columns = ['Dept','Total','TGW','Member','X','P','FE','CCT']
    dq.replace(r' Dept',r'', regex = True, inplace = True)
    if showgroup == 1:
        dg.columns = ['Dept','Total','TGW','Member','X','P','FE','CCT']
        dg.replace(r' Dept',r'', regex = True, inplace = True)
        
    dept = str()

    if plus == 0:  
        for r in range(len(dq)):
            dp =   str(dq.loc[r,'Dept'][:9]) + ' '*(9-len(str(dq.loc[r,'Dept'])))
            tt  = ' '*(4-len(str(dq.loc[r,'Total'])))   + str(dq.loc[r,'Total'])
            tg  = ' '*(3-len(str(dq.loc[r,'TGW'])))     + str(dq.loc[r,'TGW'])
            mm  = ' '*(3-len(str(dq.loc[r,'Member'])))  + str(dq.loc[r,'Member'])
            np  = ' '*(3-len(str(dq.loc[r,'X'])))       + str(dq.loc[r,'X'])
            pk  = ' '*(3-len(str(dq.loc[r,'P'])))       + str(dq.loc[r,'P']) # P only, without FE and CCT
            fe  = ' '*(3-len(str(dq.loc[r,'FE'])))      + str(dq.loc[r,'FE']) # FE only, without CCT
            cct = ' '*(3-len(str(dq.loc[r,'CCT'])))     + str(dq.loc[r,'CCT'])
            dept = f'{dept}{dp}[{tt}|{tg}|{mm}|{np}|{pk}|{fe}|{cct}]\n'
        dept = dept + '\n'
    else:
        for r in range(len(dq)):
            str_pk  = str(dq.loc[r,'P'] + dq.loc[r,'FE'] + dq.loc[r,'CCT'])
            str_fe  = str(dq.loc[r,'FE'] + dq.loc[r,'CCT'])
            dp =   str(dq.loc[r,'Dept'][:9]) + ' '*(9-len(str(dq.loc[r,'Dept'])))
            tt  = ' '*(4-len(str(dq.loc[r,'Total'])))   + str(dq.loc[r,'Total'])
            tg  = ' '*(3-len(str(dq.loc[r,'TGW'])))     + str(dq.loc[r,'TGW'])
            mm  = ' '*(3-len(str(dq.loc[r,'Member'])))  + str(dq.loc[r,'Member'])
            np  = ' '*(3-len(str(dq.loc[r,'X'])))       + str(dq.loc[r,'X'])
            pk  = ' '*(3-len(str_pk))                   + str_pk # Sum of P, FE and CCT
            fe  = ' '*(3-len(str_fe))                   + str_fe # Sum of FE and CCT
            cct = ' '*(3-len(str(dq.loc[r,'CCT'])))     + str(dq.loc[r,'CCT'])
            dept = f'{dept}{dp}[{tt}|{tg}|{mm}|{np}|{pk}|{fe}|{cct}]\n'
        dept = dept + '\n'

    grp = str()
    if showgroup == 1:
        if plus == 0:  
            for r in range(len(dg)):
                dp =   str(dg.loc[r,'Dept'][:9]) + ' '*(9-len(str(dg.loc[r,'Dept'])))
                tt  = ' '*(4-len(str(dg.loc[r,'Total'])))   + str(dg.loc[r,'Total'])
                tg  = ' '*(3-len(str(dg.loc[r,'TGW'])))     + str(dg.loc[r,'TGW'])
                mm  = ' '*(3-len(str(dg.loc[r,'Member'])))  + str(dg.loc[r,'Member'])
                np  = ' '*(3-len(str(dg.loc[r,'X'])))       + str(dg.loc[r,'X'])
                pk  = ' '*(3-len(str(dg.loc[r,'P'])))       + str(dg.loc[r,'P']) # P only, without FE and CCT
                fe  = ' '*(3-len(str(dg.loc[r,'FE'])))      + str(dg.loc[r,'FE']) # FE only, without CCT
                cct = ' '*(3-len(str(dg.loc[r,'CCT'])))     + str(dg.loc[r,'CCT'])
                grp = f'{grp}{dp}[{tt}|{tg}|{mm}|{np}|{pk}|{fe}|{cct}]\n'
            grp = grp + '\n'
        else:
            for r in range(len(dg)):
                str_pk  = str(dg.loc[r,'P'] + dg.loc[r,'FE'] + dg.loc[r,'CCT'])
                str_fe  = str(dg.loc[r,'FE'] + dg.loc[r,'CCT'])
                dp =   str(dg.loc[r,'Dept'][:9]) + ' '*(9-len(str(dg.loc[r,'Dept'])))
                tt  = ' '*(4-len(str(dg.loc[r,'Total'])))   + str(dg.loc[r,'Total'])
                tg  = ' '*(3-len(str(dg.loc[r,'TGW'])))     + str(dg.loc[r,'TGW'])
                mm  = ' '*(3-len(str(dg.loc[r,'Member'])))  + str(dg.loc[r,'Member'])
                np  = ' '*(3-len(str(dg.loc[r,'X'])))       + str(dg.loc[r,'X'])
                pk  = ' '*(3-len(str_pk))                   + str_pk # Sum of P, FE and CCT
                fe  = ' '*(3-len(str_fe))                   + str_fe # Sum of FE and CCT
                cct = ' '*(3-len(str(dg.loc[r,'CCT'])))     + str(dg.loc[r,'CCT'])
                grp = f'{grp}{dp}[{tt}|{tg}|{mm}|{np}|{pk}|{fe}|{cct}]\n'
            grp = grp + '\n'

    totalrow = 'Total' if d == '%' else grpdept

    if access in ('Group','CUL'):
        mgd = 'Member'
    elif access in ('IT','EDU','All','%','D[0-9]%'):
        mgd = 'Dept  '
    else:
        mgd = 'Group '

    standard = {(1,1): 'Leaf + BBT',
                (1,0): 'Leaf',
                (0,1): 'BBT'}[(leaf, bbt)]

    p_std = {0: {'note': "Note: Each of 4 BB categories are <b>mutually exclusive</b>",
                 'header': '   [ Tot|TGW|Mem|  X|  P| FE|CCT]'},
             1: {'note': "Note: BB milestones are <b>cumulative</b>",
                 'header': '   [ Tot|TGW|Mem|  X| P+|FE+|CCT]'}}[plus]
    
    note = p_std['note']
    header = p_std['header']

    summary = f"{grp}{dept}</pre>" # Not putting header yet, so re.sub does not affect the "0 P"
    summary = re.sub(r'\.0',r'  ',summary) # Replaces '.0' with empty space
    summary = re.sub(r'(\D)0([^.])',r'\1-\2',summary)   # Replaces lone '0' with '-'
    summary = re.sub(totalrow,f"\n{totalrow}",summary)
    summary = f"<b><u>{grpdept} CT Mission</u></b>\n<i>Standard = {standard}\n{ct} CT\n{note}\n</i>\n<pre>{mgd}{header}\n\n{summary}"
    print(">>>Return")
    return summary






def julymissionnew(season, leaf, bbt, access, d, g, ct, showgroup): # BB FUNCTIONS
    print(f"\n>>>julymissionnew: season={season}, leaf={leaf}, bbt={bbt}, access={access}, d={d}, g={g}, ct={ct}, showgroup={showgroup}")
    g = g if access in ('Group','CUL') else '%'
    d = d.capitalize().replace('d','D')
    grpdept = g.capitalize() if access in ('Group','CUL') else d.replace('D[0-9]%','Youth').replace('Mw[0-9]%','MW').replace('24', '24 Dept').replace('%', 'Church')

    q = f"SELECT * FROM JulyMissionNew2('{season}', {leaf}, {bbt}, '{access}', '{d}', '{g}', 0)"
    q_grp = f"SELECT * FROM JulyMissionNew2('{season}', {leaf}, {bbt}, '{access}', '{d}', '{g}', 1)"
    print(q)
    with odbc.connect(conn_str) as conn:
        dq = pd.read_sql(q, conn)
        dg = pd.read_sql(q_grp, conn)
    dq.columns = ['Dept','Total','TGW','Member','X','IBB','ABB']
    dq.replace(r' Dept',r'', regex = True, inplace = True)
    if showgroup == 1:
        dg.columns = ['Dept','Total','TGW','Member','X','IBB','ABB']
        dg.replace(r' Dept',r'', regex = True, inplace = True)
        
    dept = str()

    for r in range(len(dq)):
        dp =   str(dq.loc[r,'Dept'][:9]) + ' '*(9-len(str(dq.loc[r,'Dept'])))
        tt  = ' '*(4-len(str(dq.loc[r,'Total'])))   + str(dq.loc[r,'Total'])
        tg  = ' '*(3-len(str(dq.loc[r,'TGW'])))     + str(dq.loc[r,'TGW'])
        mm  = ' '*(3-len(str(dq.loc[r,'Member'])))  + str(dq.loc[r,'Member'])
        xb  = ' '*(3-len(str(dq.loc[r,'X'])))       + str(dq.loc[r,'X'])
        ib  = ' '*(3-len(str(dq.loc[r,'IBB'])))     + str(dq.loc[r,'IBB']) # IBB only, without FE and CCT
        ab  = ' '*(3-len(str(dq.loc[r,'ABB'])))     + str(dq.loc[r,'ABB']) # ABB only, without FE and CCT
        dept = f'{dept}{dp}[{tt}|{tg}|{mm}|{xb}|{ib}|{ab}]\n'
    dept = dept + '\n'

    grp = str()
    if showgroup == 1:
        for r in range(len(dg)):
            dp =   str(dg.loc[r,'Dept'][:9]) + ' '*(9-len(str(dg.loc[r,'Dept'])))
            tt  = ' '*(4-len(str(dg.loc[r,'Total'])))   + str(dg.loc[r,'Total'])
            tg  = ' '*(3-len(str(dg.loc[r,'TGW'])))     + str(dg.loc[r,'TGW'])
            mm  = ' '*(3-len(str(dg.loc[r,'Member'])))  + str(dg.loc[r,'Member'])
            xb  = ' '*(3-len(str(dg.loc[r,'X'])))       + str(dg.loc[r,'X'])
            ib  = ' '*(3-len(str(dg.loc[r,'IBB'])))     + str(dg.loc[r,'IBB']) # IBB only, without FE and CCT
            ab  = ' '*(3-len(str(dg.loc[r,'ABB'])))     + str(dg.loc[r,'ABB']) # ABB only, without FE and CCT
            grp = f'{grp}{dp}[{tt}|{tg}|{mm}|{xb}|{ib}|{ab}]\n'
        grp = grp + '\n'

    totalrow = 'Total' if d == '%' else grpdept

    if access in ('Group','CUL'):
        mgd = 'Member'
    elif access in ('IT','EDU','All','%','D[0-9]%'):
        mgd = 'Dept  '
    else:
        mgd = 'Group '

    standard = {(1,1): 'Leaf + BBT',
                (1,0): 'Leaf',
                (0,1): 'BBT'}[(leaf, bbt)]
   
    note = 'X = No picking\nIBB = Only inactive picking/BBs\nABB = At least 1 NP/ABB/CCT_Active'
    header = '   [ Tot|TGW|Mem|  X|IBB|ABB]'

    summary = f"{grp}{dept}</pre>" # Not putting header yet, so re.sub does not affect the "0 P"
    summary = re.sub(r'\.0',r'  ',summary) # Replaces '.0' with empty space
    summary = re.sub(r'(\D)0([^.])',r'\1-\2',summary)   # Replaces lone '0' with '-'
    summary = re.sub(totalrow,f"\n{totalrow}",summary)
    summary = f"<b><u>{grpdept} 22 July Mission</u></b>\n<i>Pickings as of 28 June\n\nStandard = {standard}\n{ct} CT\n\n{note}</i>\n\n<pre>{mgd}{header}\n\n{summary}"
    print(">>>Return")
    return summary





def ctmission(access): # BB FUNCTIONS # REPLACED WITH CTMISSIONNEW
    print(f"\n>>>ctmission: access={access}")
    
    d = '%' if access in ('All','IT', 'EDU') else access.capitalize().replace('d','D')
    conn = odbc.connect(conn_str)
    q = f"CTMission '{d}'"
    print(q)
    dq = pd.read_sql(q, conn)
    dq.columns = ['Dept','Total','TGW','Member','0 P','1 P+','1 FE+']
    dq.replace(r' Dept',r'', regex = True, inplace = True)
    conn.cursor().close()
        
    dept = str()  
    for r in range(len(dq)):
        dp =   str(dq.loc[r,'Dept'][:9]) + ' '*(9-len(str(dq.loc[r,'Dept'])))
        tt  = ' '*(4-len(str(dq.loc[r,'Total'])))   + str(dq.loc[r,'Total'])
        tg  = ' '*(3-len(str(dq.loc[r,'TGW'])))     + str(dq.loc[r,'TGW'])
        mm  = ' '*(3-len(str(dq.loc[r,'Member'])))  + str(dq.loc[r,'Member'])
        np  = ' '*(3-len(str(dq.loc[r,'0 P'])))     + str(dq.loc[r,'0 P'])
        pk  = ' '*(3-len(str(dq.loc[r,'1 P+'])))    + str(dq.loc[r,'1 P+'])
        fe  = ' '*(3-len(str(dq.loc[r,'1 FE+'])))   + str(dq.loc[r,'1 FE+'])
        dept = f'{dept}{dp}[{tt}|{tg}|{mm}|{np}|{pk}|{fe}]\n'
    dept = dept + '\n'

    totalrow = 'Total' if access in ('All','IT','EDU') else d

    summary = f"{dept}</pre>" # Not putting header yet, so re.sub does not affect the "0 P"
    summary = re.sub(r'\.0',r'  ',summary) # Replaces '.0' with empty space
    summary = re.sub(r'(\D)0([^.])',r'\1-\2',summary)   # Replaces lone '0' with '-'
    summary = re.sub(totalrow,f"\n{totalrow}",summary)
    summary = f"<b><u>CT Mission</u></b>\n\n<pre>Dept     [ Tot|TGW|Mem|0 P|1P+|FE+]\n\n{summary}"
    print(">>>Return")
    return summary




def ctbbtmission(access): # BBT FUNCTIONS
    print(f"\n>>>ctbbtmission: access={access}")
    
    d = '%' if access in ('All','IT', 'EDU') else access.capitalize().replace('d','D')
    conn = odbc.connect(conn_str)
    q = f"CTBbtMission '{d}'"
    print(q)
    dq = pd.read_sql(q, conn)
    dq.columns = ['Dept','Total','TGW','Member','0 P','1 P+','1 FE+']
    dq.replace(r' Dept',r'', regex = True, inplace = True)
    conn.cursor().close()
        
    dept = str()
    for r in range(len(dq)):
        dp =   str(dq.loc[r,'Dept'][:9]) + ' '*(9-len(str(dq.loc[r,'Dept'])))
        tt  = ' '*(3-len(str(dq.loc[r,'Total'])))   + str(dq.loc[r,'Total'])
        tg  = ' '*(3-len(str(dq.loc[r,'TGW'])))     + str(dq.loc[r,'TGW'])
        mm  = ' '*(2-len(str(dq.loc[r,'Member'])))  + str(dq.loc[r,'Member'])
        np  = ' '*(3-len(str(dq.loc[r,'0 P'])))     + str(dq.loc[r,'0 P'])
        pk  = ' '*(2-len(str(dq.loc[r,'1 P+'])))    + str(dq.loc[r,'1 P+'])
        fe  = ' '*(3-len(str(dq.loc[r,'1 FE+'])))   + str(dq.loc[r,'1 FE+'])
        dept = f'{dept}{dp}[{tt}|{tg}|{mm}|{np}|{pk}|{fe}]\n'
    dept = dept + '\n'

    totalrow = 'Total' if access in ('All','IT','EDU') else d

    summary = f"{dept}</pre>" # Not putting header yet, so re.sub does not affect the "0 P"
    summary = re.sub(r'\.0',r'  ',summary) # Replaces '.0' with empty space
    summary = re.sub(r'(\D)0([^.])',r'\1-\2',summary)   # Replaces lone '0' with '-'
    summary = re.sub(totalrow,f"\n{totalrow}",summary)
    summary = f"<b><u>CT BBT Mission</u></b>\n\n<pre>Dept     [BBT|TGW|Mm|0 P|1P| FE]\n\n{summary}"
    summary = summary.replace('D[--9]%','\nYouth  ').replace('MW[--9]%','\MW  ')
    print(">>>Return")
    return summary








def bbmission(g, d, standard, ct, access): # BB FUNCTIONS, BBT FUNCTIONS
    print(f"\n>>>bbmission: g={g}, d={d}, standard={standard}, ct={ct}, access={access}")
    views = {'bbt':'FnBbtSE','leaf':'FnLeafSE','all':'FnSE'}
    view = views[standard]
    r = {'Physical + Online':'%','Physical':'Melbourne','Online':'Online'}[ct]
    
    name = 'BBTCode' if access in ('Group','CUL') else 'BBTGrp'
        
    g = g if access in ('Group','CUL') else '%'
    d = d.capitalize().replace('d','D')
    grpdept = g.capitalize() if access in ('Group','CUL') else d.replace('D[0-9]%','Youth')
    
    conn = odbc.connect(conn_str)
    bb_mem = f"SELECT Dept, Grp, {name}, X, P, FE, SE FROM {view}('{r}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}' ORDER BY GID, {name}".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    bb_group = f"SELECT Grp, SUM(X)X, SUM(AchP)P, SUM(AchFE)FE, SUM(AchSE)SE FROM {view}('{r}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}' GROUP BY Grp, GID ORDER BY GID".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    bb_dept = f"SELECT Dept, SUM(X)X, SUM(AchP)P, SUM(AchFE)FE, SUM(AchSE)SE FROM {view}('{r}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}' GROUP BY Dept, DID ORDER BY DID".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    bb_youth = f"SELECT SUM(X)X, SUM(AchP)P, SUM(AchFE)FE, SUM(AchSE)SE FROM {view}('{r}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}'".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    seasons = f"SELECT SeasonName FROM EVSeason WHERE GETDATE() BETWEEN StartDate AND EndDate AND Region LIKE '{r}'"

    print(bb_group)
    
    dm = pd.read_sql(bb_mem, conn)
    dg = pd.read_sql(bb_group, conn)
    dd = pd.read_sql(bb_dept, conn)
    dy = pd.read_sql(bb_youth, conn)
    ds = pd.read_sql(seasons, conn)
    dm.columns = ['Dept','Grp','BBT','X','P','FE','SE']
    dg.columns = ['Grp','X','P','FE','SE']
    dd.columns = ['Dept','X','P','FE','SE']
    dy.columns = ['X','P','FE','SE']
    ds.columns = ['SeasonName']
        
    conn.cursor().close()

    seasonlist = ds['SeasonName'].str.cat(sep=', ').replace('Yr 43 ','').replace('Feb CT Online','FebONL').replace('Feb CT','Feb').replace('Apr CT Online ','AprONL').replace('Apr CT','Apr').replace('Apr SE CT','AprMW')

    member = str()
    if not d.endswith('D[0-9]%'):
        for r in range(len(dm)):
            bbt =   str(dm.loc[r,'BBT'][:5]) + ' '*(5-len(str(dm.loc[r,'BBT'])))
            x = ' '*(3-len(str(dm.loc[r,'X']))) + str(dm.loc[r,'X'])
            p  = ' '*(3-len(str(dm.loc[r,'P']))) + str(dm.loc[r,'P'])
            f  = ' '*(3-len(str(dm.loc[r,'FE']))) + str(dm.loc[r,'FE'])
            s  = ' '*(3-len(str(dm.loc[r,'SE']))) + str(dm.loc[r,'SE'])
            member = f'{member}{bbt}[{x}|{p}|{f}|{s}]\n'        
        member = member + '\n'
            
    group = str() 
    for r in range(len(dg)):
        grp =   str(dg.loc[r,'Grp'][:5]) + ' '*(5-len(str(dg.loc[r,'Grp'])))
        x = ' '*(3-len(str(dg.loc[r,'X']))) + str(dg.loc[r,'X'])
        p  = ' '*(3-len(str(dg.loc[r,'P']))) + str(dg.loc[r,'P'])
        f  = ' '*(3-len(str(dg.loc[r,'FE']))) + str(dg.loc[r,'FE'])
        s  = ' '*(3-len(str(dg.loc[r,'SE']))) + str(dg.loc[r,'SE'])
        group = f'{group}{grp}[{x}|{p}|{f}|{s}]\n'
    group = group + '\n'
            
    dept = str()  
    if access not in ('Group','CUL'):  
        for r in range(len(dd)):
            dpt =   str(dd.loc[r,'Dept'][:5]) + ' '*(5-len(str(dd.loc[r,'Dept'])))
            x = ' '*(3-len(str(dd.loc[r,'X']))) + str(dd.loc[r,'X'])
            p  = ' '*(3-len(str(dd.loc[r,'P']))) + str(dd.loc[r,'P'])
            f  = ' '*(3-len(str(dd.loc[r,'FE']))) + str(dd.loc[r,'FE'])
            s  = ' '*(3-len(str(dd.loc[r,'SE']))) + str(dd.loc[r,'SE'])
            dept = f'{dept}{dpt}[{x}|{p}|{f}|{s}]\n'
        dept = dept + '\n'
        
    total = str()
    if d in ('D[0-9]%','%'):
        x = ' '*(3-len(str(dy.loc[0,'X']))) + str(dy.loc[0,'X'])
        p  = ' '*(3-len(str(dy.loc[0,'P']))) + str(dy.loc[0,'P'])
        f  = ' '*(3-len(str(dy.loc[0,'FE']))) + str(dy.loc[0,'FE'])
        s  = ' '*(3-len(str(dy.loc[0,'SE']))) + str(dy.loc[0,'SE'])
        total = f'Total[{x}|{p}|{f}|{s}]'
    
    summary = f"<b><u>{grpdept} BB Mission</u></b>\n<i>Standard = {standard.capitalize().replace('All','Leaf + BBT')}\n{ct} CT\n{seasonlist}</i>\n\n<pre>     [ X | P | FE| SE]\n\n{member}{group}{dept}{total}</pre>"
    summary = re.sub(r'\.0',r'  ',summary) # Replaces '.0' with empty space
    summary = re.sub(r'(\D)0([^.])',r'\1-\2',summary)   # Replaces lone '0' with '-'
    print(">>>Return")
    return summary




def svcabs(gd,svctype,filt): # MT FUNCTIONS
    print(f"\n>>>svcabs: gd={gd}, svctype={svctype}, filt={filt}")
    # THIS FUNCTION IS WRITTEN IN MARKDOWNV2, NOT HTML LIKE ALL OTHER FUNCTIONS.
    # (TECHNICALLY MOST OF IT IS HTML EXCEPT <pre>Absentees AND <pre>Not_Reported, BUT MAIN.PY WILL CONVERT IT TO MARKDOWNV2)
    # THE REASON FOR THIS IS THAT ONLY MARKDOWNV2 ALLOWS CUSTOM CODE BLOCK LABELS.
    # TO SET PARSE MODE TO MARKDOWNV2, ENSURE RESPONSES.PY RETURNS STRING "MARKDOWNV2" IN FRONT OF THIS FUNCTION'S RETURN

    gd = gd.capitalize()
    svctype = svctype.capitalize()
          
    conn = odbc.connect(conn_str)   

    query_abs = f"SELECT Dept, Grp, MemberCode FROM CodeyServiceAbsentees('{svctype}') WHERE Attendance = 'Abs' AND {filt} LIKE '{gd}'"
    query_nr  = f"SELECT Dept, Grp, MemberCode FROM CodeyServiceAbsentees('{svctype}') WHERE Attendance = 'NoReport' AND {filt} LIKE '{gd}'"

    print(query_abs)

    dAB = pd.read_sql(query_abs, conn)                
    dNR = pd.read_sql(query_nr, conn)

    dAB.columns = ['Dept','Grp','MemberCode']
    dNR.columns = ['Dept','Grp','MemberCode']

    conn.cursor().close()
    ab = "" # "<i><b><u>Absentees</u></b></i>\n"
    nr = "" # "<i><b><u>Not Reported</u></b></i>\n"

    if len(dAB) == 0:
        ab = f"{ab}<b>Absentees</b>\n<i>No Members</i>"
    else:
        ab = f"{ab}<pre>Absentees\n"
        for r in range(len(dAB)):
            ab = f"{ab}{r+1}.{' '*(3-len(str(r+1)))}{dAB.loc[r,'Dept']} {dAB.loc[r,'Grp']} {dAB.loc[r,'MemberCode']}\n"
        ab = f"{ab}</pre>"

    if len(dNR) == 0:
        nr = f"{nr}<b>Not Reported</b>\n<i>No Members</i>"
    else:
        nr = f'{nr}<pre>NotReported\n'
        for r in range(len(dNR)):
            nr = f"{nr}{r+1}.{' '*(3-len(str(r+1)))}{dNR.loc[r,'Dept']} {dNR.loc[r,'Grp']} {dNR.loc[r,'MemberCode']}\n"
        nr = f"{nr}</pre>"

    result = f"<b>{gd} {svctype} Service Absentee List</b>\n\n{ab}\n{nr}"
    result = re.sub(r'\.0',r'',result)
    result = re.sub(r' \(\)',r'',result)
    result = re.sub(r'\((\d+)\)', r'(G\1)', result)
    result = re.sub(r'\[1\] ', r'', result)
    print(">>>Return")
    return result



def eduabs(gd,edutype,filt): # EDU FUNCTIONS
    print(f"\n>>>eduabs: gd={gd}, edutype={edutype}, filt={filt}")
    # THIS FUNCTION IS WRITTEN IN MARKDOWNV2, NOT HTML LIKE ALL OTHER FUNCTIONS.
    # (TECHNICALLY MOST OF IT IS HTML EXCEPT <pre>Absentees AND <pre>Not_Reported, BUT MAIN.PY WILL CONVERT IT TO MARKDOWNV2)
    # THE REASON FOR THIS IS THAT ONLY MARKDOWNV2 ALLOWS CUSTOM CODE BLOCK LABELS.
    # TO SET PARSE MODE TO MARKDOWNV2, ENSURE RESPONSES.PY RETURNS STRING "MARKDOWNV2" IN FRONT OF THIS FUNCTION'S RETURN

    gd = gd.capitalize()
    edutype = edutype.capitalize()
          
    conn = odbc.connect(conn_str)   
    
    EMOJI_MAP = {
        'present':  '✅',
        'absent':   '❌',
        'locked':   '🔒',
        'open':     '⬜️',
    }

    def map_prs(val, locked=False, open_=False):
        print(f"\n>>>map_prs: val={val}, locked={locked}, open_={open_}")
        if val:
            print(">>>Return")
            return EMOJI_MAP['present']
        if locked:
            print(">>>Return")
            return EMOJI_MAP['locked']
        if open_:
            print(">>>Return")
            return EMOJI_MAP['open']
        print(">>>Return")
        return EMOJI_MAP['absent']

    query_abs = f"SELECT Dept, Grp, MemberCode FROM CodeyEduAbsentees('{edutype}') WHERE Attendance = 'Abs' AND {filt} LIKE '{gd}'"
    query_nr  = f"SELECT Dept, Grp, MemberCode FROM CodeyEduAbsentees('{edutype}') WHERE Attendance = 'NoReport' AND {filt} LIKE '{gd}'"

    print(query_abs)

    dAB = pd.read_sql(query_abs, conn)                
    dNR = pd.read_sql(query_nr, conn)

    dAB.columns = ['Dept','Grp','MemberCode']
    dNR.columns = ['Dept','Grp','MemberCode']

    conn.cursor().close()
    ab = "" # "<i><b><u>Absentees</u></b></i>\n"
    nr = "" # "<i><b><u>Not Reported</u></b></i>\n"

    if len(dAB) == 0:
        ab = f"{ab}<i>No Members</i>"
    else:
        ab = f"{ab}<pre>Absentees\n"
        for r in range(len(dAB)):
            ab = f"{ab}{r+1}.{' '*(3-len(str(r+1)))}{dAB.loc[r,'Dept']} {dAB.loc[r,'Grp']} {dAB.loc[r,'MemberCode']}\n"
        ab = f"{ab}</pre>"

    if len(dNR) == 0:
        nr = f"{nr}<i>No Members</i>"
    else:
        nr = f'{nr}<pre>NotReported\n'
        for r in range(len(dNR)):
            nr = f"{nr}{r+1}.{' '*(3-len(str(r+1)))}{dNR.loc[r,'Dept']} {dNR.loc[r,'Grp']} {dNR.loc[r,'MemberCode']}\n"
        nr = f"{nr}</pre>"

    result = f"*<b>{gd} {edutype} Edu Absentee List</b>*\n\n{ab}\n{nr}"
    result = re.sub(r'\.0',r'',result)
    result = re.sub(r' \(\)',r'',result)
    result = re.sub(r'\((\d+)\)', r'(G\1)', result)
    result = re.sub(r'\[1\] ', r'', result)
    print(">>>Return")
    return result

    
# --- Kamau Adjustment #2/3 Start for Unicode Issue
def map_emoji(val, col=None): # EDU FUNCTIONS
    mapping = {
        1: '✅',
        2: '🔒',
        3: '⬜️',
        0: '❌',
    }
    return mapping.get(int(val), '❌')
# --- Kamau Adjustment #1/3 End





def hspreport(g, d, access): # EDU FUNCTIONS
    print(f"\n>>>hspreport: g={g}, d={d}, access={access}")
    
    g = g if access  in ('Group','GGN') else '%'
    print(f"Group Filter: {g}")
    d = d.capitalize().replace('d','D')
    print(f"Dept Input: {d}")

    deptfilter = f"Dept LIKE '{d}'".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")

    print(f"Dept Filter: {deptfilter}")

    if access.lower() in ['it','all','edu','d[0-9]%','mw','mw[0-9]%','24']:
        deptfilter = {
            "d[0-9]%": "Dept LIKE 'D[0-9]%' OR Dept = 'InnerSFT'",
            "mw": "Dept IN ('Men','Women')",
            "mw[0-9]%": "Dept IN ('Men','Women')",
            "24": "Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')"
        }.get(d.lower(), deptfilter)

    print(f"New Dept Filter: {deptfilter}")

    grpdept = g.capitalize() if access in ('Group','GGN') else d.replace('D[0-9]%','Youth').replace('Mw','MW').replace('24','24 Dept').replace('%','Church')
    
    conn = odbc.connect(conn_str)
    
    # --- Kamau Adjustment #2/3 Start for Unicode Issue

    # hsp_mem = f"""
    # WITH Days AS
    # (SELECT CONVERT(DATE, SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')TD,
    #     StartDate W1,
    #     DATEADD(DAY,2,StartDate)F1,
    #     DATEADD(DAY,6,StartDate)T2,
    #     DATEADD(DAY,9,StartDate)F2,
    #     DATEADD(DAY,10,StartDate)S2,
    #     DATEADD(DAY,11,StartDate)U2
    #     FROM NewEduGroupTable
    #     WHERE CONVERT(DATE, SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time') BETWEEN StartDate AND EndDate)
    # SELECT MemberCode,
    #     CASE WHEN WedPrs != 0 THEN N'✅' ELSE N'❌' END WedPrs,
    #     CASE WHEN Fri1Prs != 0 THEN N'✅' WHEN (SELECT TD FROM Days) < (SELECT F1 FROM Days) THEN N'🔒' ELSE N'❌' END Fri1Prs,
    #     CASE WHEN DropInPrs != 0 THEN N'✅' WHEN (SELECT TD FROM Days) < (SELECT T2 FROM Days) THEN N'🔒' WHEN (SELECT TD FROM Days) < (SELECT S2 FROM Days) THEN N'⬜️' ELSE N'❌' END DropInPrs,
    #     CASE WHEN Fri2Prs != 0 THEN N'✅' WHEN (SELECT TD FROM Days) < (SELECT F2 FROM Days) THEN N'🔒' ELSE N'❌' END Fri2Prs,
    #     CASE WHEN ISNULL(VidSubmitted,0) != 0 THEN N'✅' WHEN (SELECT TD FROM Days) < (SELECT F2 FROM Days) THEN N'⬜️' ELSE N'❌' END VidSubmitted,
    #     CASE WHEN ISNULL(ExamScore,0) != 0 THEN N'✅' WHEN (SELECT TD FROM Days) < (SELECT U2 FROM Days) THEN N'🔒' ELSE N'❌' END ExamScore
    # FROM HSPMemberCodey
    # WHERE Dept LIKE '{d}'
    #     AND Grp LIKE '{g}'
    # ORDER BY Pos, MemberCode
    # """
    # print("Member Query:")
    # print(hsp_mem)
    
    
    hsp_mem = f"""
    WITH Days AS
    (SELECT CONVERT(DATE, SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')TD,
        StartDate W1,
        DATEADD(DAY,2,StartDate)F1,
        DATEADD(DAY,6,StartDate)T2,
        DATEADD(DAY,9,StartDate)F2,
        DATEADD(DAY,10,StartDate)S2,
        DATEADD(DAY,11,StartDate)U2
        FROM NewEduGroupTable
        WHERE CONVERT(DATE, SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time') BETWEEN StartDate AND EndDate)
    SELECT MemberCode,
        CASE WHEN WedPrs   != 0 THEN 1 ELSE 0 END WedPrs,
        CASE WHEN Fri1Prs  != 0 THEN 1
            WHEN (SELECT TD FROM Days) < (SELECT F1 FROM Days) THEN 2
            ELSE 0 END Fri1Prs,
        CASE WHEN DropInPrs != 0 THEN 1
            WHEN (SELECT TD FROM Days) < (SELECT T2 FROM Days) THEN 2
            WHEN (SELECT TD FROM Days) < (SELECT S2 FROM Days) THEN 3
            ELSE 0 END DropInPrs,
        CASE WHEN Fri2Prs  != 0 THEN 1
            WHEN (SELECT TD FROM Days) < (SELECT F2 FROM Days) THEN 2
            ELSE 0 END Fri2Prs,
        CASE WHEN ISNULL(VidSubmitted,0) != 0 THEN 1
            WHEN (SELECT TD FROM Days) < (SELECT F2 FROM Days) THEN 3
            ELSE 0 END VidSubmitted,
        CASE WHEN ISNULL(ExamScore,0)    != 0 THEN 1
            WHEN (SELECT TD FROM Days) < (SELECT U2 FROM Days) THEN 2
            ELSE 0 END ExamScore,
        CASE WHEN ISNULL(PodcastPrs,0) != 0 THEN 1
            WHEN (SELECT TD FROM Days) < (SELECT F2 FROM Days) THEN 3
            ELSE 0 END PodcastPrs
    FROM HSPMemberCodey
    WHERE {deptfilter}
        AND Grp LIKE '{g}'
    ORDER BY Pos, MemberCode
    """

    # print("Member Query:")
    # print(hsp_mem)
    
    # --- Kamau Adjustment #2/3 End
    
    hsp_group = f"""
    SELECT Grp, WedPrs, Fri1Prs, DropInPrs, Fri2Prs, VideoSubmit, ExamSubmit, PodcastPrs, Members
    FROM HSPCodey
    WHERE {deptfilter.replace("Dept IN ('Men','Women')","Grp LIKE 'MW[0-9]%'")}
        AND Grp LIKE '{g}'
    ORDER BY GID
    """
    # print("Group Query:")
    print(hsp_group)
    
    hsp_dept = f"""
    SELECT Dept, SUM(WedPrs)WedPrs, SUM(Fri1Prs)Fri1Prs, SUM(DropInPrs)DropInPrs, SUM(Fri2Prs)Fri2Prs,
        SUM(VideoSubmit)VideoSubmit, SUM(ExamSubmit)ExamSubmit, SUM(PodcastPrs)PodcastPrs, SUM(Members)Total
    FROM HSPCodey
    WHERE {deptfilter}
        AND Grp LIKE '{g}'
    GROUP BY Dept, DID
    ORDER BY DID
    """
    # print("Department Query:")
    # print(hsp_dept)
    
    hsp_total = f"""
    SELECT SUM(WedPrs)WedPrs, SUM(Fri1Prs)Fri1Prs, SUM(DropInPrs)DropInPrs, SUM(Fri2Prs)Fri2Prs,
        SUM(VideoSubmit)VideoSubmit, SUM(ExamSubmit)ExamSubmit, SUM(PodcastPrs)PodcastPrs, SUM(Members)Total
    FROM HSPCodey
    WHERE {deptfilter}
        AND Grp LIKE '{g}'
    """
    # print("Total Query:")
    # print(hsp_total)
       
    dm = pd.read_sql(hsp_mem, conn)
    dg = pd.read_sql(hsp_group, conn)
    dd = pd.read_sql(hsp_dept, conn)
    dy = pd.read_sql(hsp_total, conn)

    # print(dm) # This prints the raw dataframe, not the string that will be returned

    dm.columns = ['Member','WD','F1','DI','F2','VS','EX','PC']
    dg.columns = ['Grp','WD','F1','DI','F2','VS','EX','PC','TT']
    dd.columns = ['Dept','WD','F1','DI','F2','VS','EX','PC','TT']
    dy.columns = ['WD','F1','DI','F2','VS','EX','PC','TT']


    # --- Kamau Adjustment #3/3 Start for Unicode Issue
    for col in ['WD', 'F1', 'DI', 'F2', 'VS', 'EX', 'PC']:
        dm[col] = dm[col].apply(map_emoji)
    # --- Kamau Adjustment #3/3 End
    
    dd.replace(r' Dept',r'', regex = True, inplace = True)
    
    conn.cursor().close()

    member = str()
    if access in ('Group','GGN'):
        member = '1⃣2⃣3⃣4⃣5⃣6⃣7⃣\n'
        for r in range(len(dm)):
            mem = str(dm.loc[r,'Member'][:5]) + ' '*(5-len(str(dm.loc[r,'Member'][:5])))
            wp  = str(dm.loc[r,'WD'])
            f1  = str(dm.loc[r,'F1'])
            di  = str(dm.loc[r,'DI'])
            f2  = str(dm.loc[r,'F2'])
            vs  = str(dm.loc[r,'VS'])
            ex  = str(dm.loc[r,'EX'])
            pc  = str(dm.loc[r,'PC'])
            member = f'{member}{wp}{f1}{di}{f2}{vs}{ex}{pc}{mem}\n'        
        member = f'</pre>{member}\n'
    
    s = 2 if access in ('Group','GGN') else 3  
    group = str()
    for r in range(len(dg)):
        grp =   str(dg.loc[r,'Grp'][:5]) + ' '*(5-len(str(dg.loc[r,'Grp'])[:5]))
        wp  = ' '*(s-len(str(dg.loc[r,'WD']))) + str(dg.loc[r,'WD'])
        f1  = ' '*(s-len(str(dg.loc[r,'F1']))) + str(dg.loc[r,'F1'])
        di  = ' '*(s-len(str(dg.loc[r,'DI']))) + str(dg.loc[r,'DI'])
        f2  = ' '*(s-len(str(dg.loc[r,'F2']))) + str(dg.loc[r,'F2'])
        vs  = ' '*(s-len(str(dg.loc[r,'VS']))) + str(dg.loc[r,'VS'])
        ex  = ' '*(s-len(str(dg.loc[r,'EX']))) + str(dg.loc[r,'EX'])
        pc  = ' '*(s-len(str(dg.loc[r,'PC']))) + str(dg.loc[r,'PC'])
        tt  = ' '*(s-len(str(dg.loc[r,'TT']))) + str(dg.loc[r,'TT'])
        group = f'{group}{grp}[{wp}|{f1}|{di}|{f2}|{vs}|{ex}|{pc}|{tt}]\n' if access not in ('Group','GGN') else f'<b>{group}[{wp}|{f1}|{di}|{f2}|{vs}|{ex}|{pc}]</b>\n(<i>{tt} members)</i><pre>\n'
    group = group + '\n'
      
    dept = str()  
    if access not in ('Group','GGN','24'):
        for r in range(len(dd)):
            dpt =   str(dd.loc[r,'Dept'])[:5] + ' '*(5-len(str(dd.loc[r,'Dept'])[:5]))
            wp  = ' '*(3-len(str(dd.loc[r,'WD']))) + str(dd.loc[r,'WD'])
            f1  = ' '*(3-len(str(dd.loc[r,'F1']))) + str(dd.loc[r,'F1'])
            di  = ' '*(3-len(str(dd.loc[r,'DI']))) + str(dd.loc[r,'DI'])
            f2  = ' '*(3-len(str(dd.loc[r,'F2']))) + str(dd.loc[r,'F2'])
            vs  = ' '*(3-len(str(dd.loc[r,'VS']))) + str(dd.loc[r,'VS'])
            ex  = ' '*(3-len(str(dd.loc[r,'EX']))) + str(dd.loc[r,'EX'])
            pc  = ' '*(3-len(str(dd.loc[r,'PC']))) + str(dd.loc[r,'PC'])
            tt  = ' '*(3-len(str(dd.loc[r,'TT']))) + str(dd.loc[r,'TT'])
            dept = f'{dept}{dpt}[{wp}|{f1}|{di}|{f2}|{vs}|{ex}|{pc}|{tt}]\n'
        dept = dept + '\n'
    
    total = str()
    if d in ('D[0-9]%','%','Mw','24'):
        wp  = ' '*(3-len(str(dy.loc[0,'WD']))) + str(dy.loc[0,'WD'])
        f1  = ' '*(3-len(str(dy.loc[0,'F1']))) + str(dy.loc[0,'F1'])
        di  = ' '*(3-len(str(dy.loc[0,'DI']))) + str(dy.loc[0,'DI'])
        f2  = ' '*(3-len(str(dy.loc[0,'F2']))) + str(dy.loc[0,'F2'])
        vs  = ' '*(3-len(str(dy.loc[0,'VS']))) + str(dy.loc[0,'VS'])
        ex  = ' '*(3-len(str(dy.loc[0,'EX']))) + str(dy.loc[0,'EX'])
        pc  = ' '*(3-len(str(dy.loc[0,'PC']))) + str(dy.loc[0,'PC'])
        tt  = ' '*(3-len(str(dy.loc[0,'TT']))) + str(dy.loc[0,'TT'])
        total = f'Total[{wp}|{f1}|{di}|{f2}|{vs}|{ex}|{pc}|{tt}]'
    now = datetime.now(ZoneInfo("Australia/Melbourne")).strftime("%a %d %b, %I:%M %p")
    # now = datetime.now(ZoneInfo("Australia/Melbourne")).strftime('%a %d %b, %I:%M %p')
    header = f"<b><u>{grpdept} HSP EDU REPORTING</u></b>\n<i>{now}</i>\n\n"
    header = header if access not in ('Group','GGN') else f"{header}1⃣ Wed\n2⃣ Friday 1\n3⃣ Drop-in \n4⃣ Friday 2\n5⃣ Video Submission\n6⃣ Exam\n7⃣ Podcast\n\n🔒Reporting Not Open\n⬜️Reporting Open\n❌Absent\n✅Attend\n\n"
    columns = '' if access in ('Group','GGN') else '     [WED|FR1|DPN|FR2|VID|EXM|PDC|TOT]\n\n'
    table = f"<pre>{columns}{member}{group}{dept}{total}</pre>"
    table = re.sub(r'\.0',r'  ',table) if access not in ('Group','GGN') else table # Replaces '.0' with empty space
    table = re.sub(r'(\D)0([^.])',r'\1-\2',table) if access not in ('Group','GGN') else table   # Replaces lone '0' with '-'
    summary = f"{header}{table}"
    print(">>>Return")
    return summary


























def memberpp(timerange,g,sid,ss,access): # BBT FUNCTIONS
    print(f"\n>>>memberpp: timerange={timerange}, g={g}, sid={sid}, ss={ss}, access={access}")
    
    name = 'Member' if access == 'IT' else 'MemberCode'
  
    timevalues = {'today':     ['SELECT dbo.today()', 'SELECT dbo.tomorrow()', 'Today'],
                  'yesterday': ['SELECT dbo.yesterday()', 'SELECT dbo.today()', 'Yesterday'],
                  'week':      ['SELECT dbo.weekstart()', 'SELECT dbo.nextweekstart()', 'This Week'],
                  'lastweek':  ['SELECT dbo.lastweekstart()', 'SELECT dbo.weekstart()', 'Last Week'],
                  'season':    [f"'{ss}'", 'SELECT dbo.tomorrow()', 'EV Season'],
                  'lastseason':    [f"'{ss}'", 'SELECT dbo.tomorrow()', 'EV Season']}
   
    s,e,title = timevalues[timerange]
        
    memberQ = f"SELECT {name}, PP FROM CodeyPP('{sid}', ({s}), ({e})) WHERE Grp LIKE '{g}'"
    totalQ  = f"SELECT SUM(PP)PP FROM CodeyPP('{sid}', ({s}), ({e})) WHERE Grp LIKE '{g}'"
    print(memberQ)
    
    with odbc.connect(conn_str) as conn:
        dm = pd.read_sql(memberQ, conn)
        dt = pd.read_sql(totalQ, conn)

    dm.columns = ['Member','PP']
    dt.columns = ['PP']
    g = g.capitalize()
    g = re.sub(r'(¹|²)g([0-9]*)',r'\1G\2',g)
    if len(dm) == 0:
        print(">>>Return")
        return "No members found"
    else:  
        member = str()
        
        for r in range(len(dm)):
            mem = str(dm.loc[r,'Member'])[:8] + ' '*(8-len(str(dm.loc[r,'Member'])[:8]))
            pp     = ' '*(3-len(str(dm.loc[r,'PP']))) + str(dm.loc[r,'PP'])      
            member = f'{member}{mem}[{pp}]\n'
            
        pp     = ' '*(3-len(str(dt.loc[0,'PP']))) + str(dt.loc[0,'PP'])
        
        total = f'Total   [{pp}]'
        
        member = f'<b><u>{g} PP : {title}</u></b>\n\n<pre>Member  [PP ]\n\n{member}\n{total}</pre>'
        member = re.sub(r'\.0',r'  ',member) # Replaces '.0' with empty space
        member = re.sub(r'(\D)0([^.])',r'\1-\2',member)   # Replaces lone '0' with '-'
        print(">>>Return")
    return member
    

# UNIVERSAL DEPT PP FUNCTION:

def deptpp(task,timerange,d,sid,ss,access): # BBT FUNCTIONS
    print(f"\n>>>deptpp: task={task}, timerange={timerange}, d={d}, sid={sid}, ss={ss}, access={access}")
    
    displayGroups = False if task == 'dept' and access in ('All','IT','EDU') else True
    topleft = 'Grp ' if displayGroups == True else 'Dept'
    
    if task == 'dept':
        task = 'youth'
    
    taskvalues = {'youth' : [''       , ''            ],
                  'tgw'   : [' TGW'   , " AND Title IN ('TJN','GYJN')"],
                  'member': [' Member', " AND (Title IS NULL OR Title NOT IN ('TJN','GYJN'))"]}
    tasktitle = taskvalues[task][0]
    taskQ = taskvalues[task][1]
  
    if timerange in {'today','yesterday'}:
        spc = [6,5,4,4,4,4,f'{topleft}  [PP  ]',   'Total ']
    if timerange in {'week','lastweek'}:
        spc = [5,5,5,4,4,4,f'{topleft} [PP  ]',   'Total']
    if timerange == 'season':
        spc = [4,6,6,5,5,5,f'{topleft}[ PP  ]','Tot ']   

    timevalues = {'today':     ['SELECT dbo.today()', 'SELECT dbo.tomorrow()', 'Today'],
                  'yesterday': ['SELECT dbo.yesterday()', 'SELECT dbo.today()', 'Yesterday'],
                  'week':      ['SELECT dbo.weekstart()', 'SELECT dbo.nextweekstart()', 'This Week'],
                  'lastweek':  ['SELECT dbo.lastweekstart()', 'SELECT dbo.weekstart()', 'Last Week'],
                  'season':    [f"'{ss}'", 'SELECT dbo.tomorrow()', 'EV Season']}
    
    s,e,timetitle = timevalues[timerange]
       
    memberQ = f"SELECT Grp, SUM(PP)PP FROM CodeyPP('{sid}', ({s}), ({e})) WHERE Dept LIKE '{d}'{taskQ} GROUP BY Grp, GID ORDER BY GID".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    deptQ   = f"SELECT Dept, SUM(PP)PP FROM CodeyPP('{sid}', ({s}), ({e})) WHERE Dept LIKE '{d}'{taskQ} GROUP BY Dept, DID ORDER BY DID".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")  
    totalQ  = f"SELECT SUM(PP)PP FROM CodeyPP('{sid}', ({s}), ({e})) WHERE Dept LIKE '{d}'{taskQ}".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    print(memberQ)

    with odbc.connect(conn_str) as conn:
        dm = pd.read_sql(memberQ, conn)
        dd = pd.read_sql(deptQ, conn)
        dt = pd.read_sql(totalQ, conn)

    dm.columns = ['Grp','PP']
    dd.columns = ['Dept','PP']
    dt.columns = ['PP']
    dd.replace(r' Dept',r'', regex = True, inplace = True)
    
    group = str()
    
    if displayGroups:
        for r in range(len(dm)):
            grp = str(dm.loc[r,'Grp']) + ' '*(spc[0]-len(str(dm.loc[r,'Grp'])))
            pp = ' '*(spc[3]-len(str(dm.loc[r,'PP']))) + str(dm.loc[r,'PP'])
            group = f'{group}{grp}[{pp}]\n'
        group = group + '\n'

    dept = str()    
    for r in range(len(dd)):
        dpt = str(dd.loc[r,'Dept']) + ' '*(spc[0]-len(str(dd.loc[r,'Dept'])))
        pp = ' '*(spc[3]-len(str(dd.loc[r,'PP']))) + str(dd.loc[r,'PP'])
        dept = f'{dept}{dpt}[{pp}]\n'
    dept = dept + '\n'

    if d in ('D[0-9]%','%'):
        pp = ' '*(spc[3]-len(str(dt.loc[0,'PP']))) + str(dt.loc[0,'PP'])
        total = f'{spc[7]}[{pp}]\n'
    else:
        total = str()
        
    depttitle = d.replace('D[0-9]%','Youth').replace('Mw[0-9]%','MW').replace('24', '24 Dept').replace('%', 'Church')

    fmp = f"<b><u>{depttitle}{tasktitle} FMP : {timetitle}</u></b>\n\n<pre>{spc[6]}\n\n{group}{dept}{total}</pre>"
    fmp = re.sub(r'\.0',r'  ',fmp) # Replaces '.0' with empty space
    fmp = re.sub(r'(\D)0([^.])',r'\1-\2',fmp)   # Replaces lone '0' with '-'
    print(">>>Return")
    return fmp



def taskpp(task,timerange,d,sid,ss,access): # BBT FUNCTIONS
    print(f"\n>>>taskpp: task={task}, timerange={timerange}, d={d}, sid={sid}, ss={ss}, access={access}")

    name = 'MemberFull' if access == 'IT' else 'MemberInitial'
        
    taskvalues = {'gyjn': [' GYJN'   , " AND Title = 'GYJN'"],
                  'oev' : [' OEV TJN', " AND Task = 'OEV'"],
                  'iev' : [' IEV TJN', " AND Task = 'IEV'"],
                  'edu' : [' EDU TJN', " AND Task = 'EDU'"],
                  'sv'  : [' SV TJN' , " AND Task = 'SV'"]}
    tasktitle = taskvalues[task][0]
    taskquery = taskvalues[task][1]
    
    if access == 'IT':
        if timerange in {'today','yesterday'}:
            spc = [10,4,4,4,4,4,'TGW       [PP  ]','Total     ']
        elif timerange in {'week','lastweek'}:
            spc = [9,5,4,4,4,4,'TGW      [PP  ]','Total    ']
        elif timerange == 'season':
            spc = [8,5,5,4,4,4,'TGW     [PP  ]','Total   ']
    else:
        if timerange in {'today','yesterday'}:
            spc = [7,4,4,4,4,4,'TGW    [PP  ]',  'Total  ']
        elif timerange in {'week','lastweek'}:
            spc = [7,5,4,4,4,4,'TGW    [PP  ]', 'Total  ']
        elif timerange == 'season':
            spc = [7,5,5,4,4,4,'TGW    [PP  ]','Total  ']

    timevalues = {'today':     ['SELECT dbo.today()', 'SELECT dbo.tomorrow()', 'Today'],
                  'yesterday': ['SELECT dbo.yesterday()', 'SELECT dbo.today()', 'Yesterday'],
                  'week':      ['SELECT dbo.weekstart()', 'SELECT dbo.nextweekstart()', 'This Week'],
                  'lastweek':  ['SELECT dbo.lastweekstart()', 'SELECT dbo.weekstart()', 'Last Week'],
                  'season':    [f"'{ss}'", 'SELECT dbo.tomorrow()', 'EV Season']}
    
    s,e,timetitle = timevalues[timerange]
       
    baseQ   = f"{name}, PP FROM CodeyPP('{sid}', ({s}), ({e})) s WHERE Dept LIKE '{d}'{taskquery}".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    memberQ = f"SELECT Grp, {baseQ} ORDER BY GID"
    deptQ   = f"SELECT Dept, SUM(PP)PP FROM (SELECT Dept, DID, {baseQ})b GROUP BY Dept, DID ORDER BY DID"
    totalQ  = f"SELECT SUM(PP)PP FROM CodeyPP('{sid}', ({s}), ({e})) s WHERE Dept LIKE '{d}'{taskquery}".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'Mw[0-9]%'","Grp LIKE 'MW[0-9]%'")
    
    print(deptQ)
    
    with odbc.connect(conn_str) as conn:
        dm = pd.read_sql(memberQ, conn)
        dd = pd.read_sql(deptQ, conn)
        dt = pd.read_sql(totalQ, conn)
    
    dm.columns = ['Grp','Member','PP']
    dd.columns = ['Dept','PP']
    dt.columns = ['PP']
    dd.replace(r' Dept',r'', regex = True, inplace = True)

    group = str()
    for r in range(len(dm)):
        mem = f"{dm.loc[r,'Member'][:spc[0]]}{' '*(spc[0]-len(dm.loc[r,'Member'][:spc[0]]))}"
        pp = ' '*(spc[3]-len(str(dm.loc[r,'PP']))) + str(dm.loc[r,'PP'])
        group = f'{group}{mem}[{pp}]\n'
    group = group + '\n'

    dept = str()    
    for r in range(len(dd)):
        dpt = str(dd.loc[r,'Dept']) + ' '*(spc[0]-len(str(dd.loc[r,'Dept'])[:spc[0]]))
        pp = ' '*(spc[3]-len(str(dd.loc[r,'PP']))) + str(dd.loc[r,'PP'])
        dept = f'{dept}{dpt}[{pp}]\n'
    dept = dept + '\n'

    total = str()
    if d in ('D[0-9]%','%'):
        pp = ' '*(spc[3]-len(str(dt.loc[0,'PP']))) + str(dt.loc[0,'PP'])
        total = f'{spc[7]}[{pp}]\n'
        
    depttitle = d.replace('D[0-9]%','Youth').replace('Mw[0-9]%','MW').replace('24', '24 Dept').replace('%', 'Church')

    fmp = f"<b><u>{depttitle}{tasktitle} PP : {timetitle}</u></b>\n\n<pre>{spc[6]}\n\n{group}{dept}{total}</pre>"
    fmp = re.sub(r'\.0',r'  ',fmp) # Replaces '.0' with empty space
    fmp = re.sub(r'(\D)0([^.])',r'\1-\2',fmp)   # Replaces lone '0' with '-'
    print(">>>Return")
    return fmp




def memberbbt(timerange,g,sid,ss,access): # BBT FUNCTIONS
    print(f"\n>>>memberbbt: timerange={timerange}, group={g}, sid={sid}, seasonstart={ss}, access={access}")
    
    name = 'Member' if access == 'IT' else 'MemberCode'
  
    timevalues = {'today':     ['SELECT dbo.today()', 'SELECT dbo.tomorrow()', 'Today'],
                  'yesterday': ['SELECT dbo.yesterday()', 'SELECT dbo.today()', 'Yesterday'],
                  'week':      ['SELECT dbo.weekstart()', 'SELECT dbo.nextweekstart()', 'This Week'],
                  'lastweek':  ['SELECT dbo.lastweekstart()', 'SELECT dbo.weekstart()', 'Last Week'],
                  'season':    [f"'{ss}'", 'SELECT dbo.tomorrow()', 'EV Season'],
                  'lastseason':    [f"'{ss}'", 'SELECT dbo.tomorrow()', 'EV Season']}
   
    s,e,title = timevalues[timerange]
        
    memberQ = f"SELECT {name}, PP, P, FE, CL, CT FROM CodeyFMPPPBBT('{sid}', ({s}), ({e})) WHERE Grp LIKE '{g}'"
    totalQ  = f"SELECT SUM(PP)PP, SUM(P)P, SUM(FE)FE, SUM(CL)CL, SUM(CT)CT FROM CodeyFMPPPBBT('{sid}', ({s}), ({e})) WHERE Grp LIKE '{g}'"
    print(memberQ)
    
    with odbc.connect(conn_str) as conn:
        dm = pd.read_sql(memberQ, conn)
        dt = pd.read_sql(totalQ, conn)

    dm.columns = ['Member','PP','P','FE','CL','CT']
    dt.columns = ['PP','P','FE','CL','CT']
    g = g.capitalize()
    g = re.sub(r'(¹|²)g([0-9]*)',r'\1G\2',g)
    if len(dm) == 0:
        print(">>>Return")
        return "No members found"
    else:  
        member = str()
        
        for r in range(len(dm)):
            mem = str(dm.loc[r,'Member'])[:8] + ' '*(8-len(str(dm.loc[r,'Member'])[:8]))
            pp = ' '*(4-len(str(dm.loc[r,'PP']))) + str(dm.loc[r,'PP'])
            p  = ' '*(4-len(str(dm.loc[r,'P'])))  + str(dm.loc[r,'P'])
            fe = ' '*(3-len(str(dm.loc[r,'FE']))) + str(dm.loc[r,'FE'])
            cl = ' '*(3-len(str(dm.loc[r,'CL']))) + str(dm.loc[r,'CL'])
            ct = ' '*(3-len(str(dm.loc[r,'CT']))) + str(dm.loc[r,'CT'])
            
            member = f'{member}{mem}[{pp}|{p}|{fe}|{cl}|{ct}]\n'
            
        pp = ' '*(4-len(str(dt.loc[0,'PP']))) + str(dt.loc[0,'PP'])
        p  = ' '*(4-len(str(dt.loc[0,'P'])))  + str(dt.loc[0,'P'])
        fe = ' '*(3-len(str(dt.loc[0,'FE']))) + str(dt.loc[0,'FE'])
        cl = ' '*(3-len(str(dt.loc[0,'CL']))) + str(dt.loc[0,'CL'])
        ct = ' '*(3-len(str(dt.loc[0,'CT']))) + str(dt.loc[0,'CT'])

        total = f'Total   [{pp}|{p}|{fe}|{cl}|{ct}]'
        
        member = f'<b><u>{g} BBT : {title}</u></b>\n\n<pre>Member  [PP  | P  |FE |CL |CCT]\n\n{member}\n{total}</pre>'
        member = re.sub(r'\.0',r'  ',member) # Replaces '.0' with empty space
        member = re.sub(r'(\D)0([^.])',r'\1-\2',member)   # Replaces lone '0' with '-'
        print(">>>Return")
        return member





def deptbbt(task,timerange,d,sid,ss,access): # BBT FUNCTIONS
    print(f"\n>>>deptbbt: task={task}, timerange={timerange}, dept={d}, sid={sid}, seasonstart={ss}, access={access}")
    
    displayGroups = False if task == 'dept' and access in ('All','IT','EDU') else True
    topleft = 'Grp ' if displayGroups == True else 'Dept'

    if timerange in {'today','yesterday'}:
        spc = [6,5,4,4,4,4,f'{topleft}  [ PP  | P  |FE  |CL  |CT  ]',   'Total ']
    if timerange in {'week','lastweek'}:
        spc = [5,5,5,4,4,4,f'{topleft} [ PP  |  P  |FE  |CL  |CT  ]',   'Total']
    if timerange == 'season':
        spc = [4,6,6,5,5,5,f'{topleft}[  PP  |   P  | FE  | CL  | CT  ]','Tot ']

    timevalues = {'today':   ['SELECT dbo.today()', 'SELECT dbo.tomorrow()', 'Today'],
                'yesterday': ['SELECT dbo.yesterday()', 'SELECT dbo.today()', 'Yesterday'],
                'week':      ['SELECT dbo.weekstart()', 'SELECT dbo.nextweekstart()', 'This Week'],
                'lastweek':  ['SELECT dbo.lastweekstart()', 'SELECT dbo.weekstart()', 'Last Week'],
                'season':    [f"'{ss}'", 'SELECT dbo.tomorrow()', 'EV Season']}
    
    s,e,timetitle = timevalues[timerange]
    
    memberQ = f"SELECT Grp, SUM(F)F, SUM(M)M, SUM(PP)PP, SUM(P)P, SUM(FE)FE FROM CodeyFMPPP('{sid}', ({s}), ({e})) WHERE Dept LIKE '{d}' GROUP BY Grp, GID ORDER BY GID".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'MW[0-9]%'","Grp LIKE 'MW[0-9]%'")
    deptQ   = f"SELECT Dept, SUM(F)F, SUM(M)M, SUM(PP)PP, SUM(P)P, SUM(FE)FE FROM CodeyFMPPP('{sid}', ({s}), ({e})) WHERE Dept LIKE '{d}' GROUP BY Dept, DID ORDER BY DID".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'MW[0-9]%'","Grp LIKE 'MW[0-9]%'")
    totalQ  = f"SELECT SUM(F)F, SUM(M)M, SUM(PP)PP, SUM(P)P, SUM(FE)FE FROM CodeyFMPPP('{sid}', ({s}), ({e})) WHERE Dept LIKE '{d}'".replace("Dept LIKE '24'","Dept = 'SFT' OR Grp IN ('Serving','Culture','GD','HWPL')").replace("Dept LIKE 'MW[0-9]%'","Grp LIKE 'MW[0-9]%'")
    print(memberQ)

    with odbc.connect(conn_str) as conn:
        dm = pd.read_sql(memberQ, conn)
        dd = pd.read_sql(deptQ, conn)
        dt = pd.read_sql(totalQ, conn)

    dm.columns = ['Grp','F','M','PP','P','FE']
    dd.columns = ['Dept','F','M','PP','P','FE']
    dt.columns = ['F','M','PP','P','FE']
    dd.replace(r' Dept',r'', regex = True, inplace = True)
    
    group = str()
    
    if displayGroups:
        for r in range(len(dm)):
            grp = str(dm.loc[r,'Grp'])[:spc[0]] + ' '*(spc[0]-len(str(dm.loc[r,'Grp'])[:spc[0]]))
            f  = ' '*(spc[1]-len(str(dm.loc[r,'F'])))  + str(dm.loc[r,'F'])
            m  = ' '*(spc[2]-len(str(dm.loc[r,'M'])))  + str(dm.loc[r,'M'])
            pp = ' '*(spc[3]-len(str(dm.loc[r,'PP']))) + str(dm.loc[r,'PP'])
            p  = ' '*(spc[4]-len(str(dm.loc[r,'P'])))  + str(dm.loc[r,'P'])
            fe = ' '*(spc[5]-len(str(dm.loc[r,'FE']))) + str(dm.loc[r,'FE'])
            group = f'{group}{grp}[{f}|{m}|{pp}|{p}|{fe}]\n'
        group = group + '\n'

    dept = str()    
    for r in range(len(dd)):
        dpt = str(dd.loc[r,'Dept'][:spc[0]]) + ' '*(spc[0]-len(str(dd.loc[r,'Dept'][:spc[0]])))
        f  = ' '*(spc[1]-len(str(dd.loc[r,'F'])))  + str(dd.loc[r,'F'])
        m  = ' '*(spc[2]-len(str(dd.loc[r,'M'])))  + str(dd.loc[r,'M'])
        pp = ' '*(spc[3]-len(str(dd.loc[r,'PP']))) + str(dd.loc[r,'PP'])
        p  = ' '*(spc[4]-len(str(dd.loc[r,'P'])))  + str(dd.loc[r,'P'])
        fe = ' '*(spc[5]-len(str(dd.loc[r,'FE']))) + str(dd.loc[r,'FE'])
        dept = f'{dept}{dpt}[{f}|{m}|{pp}|{p}|{fe}]\n'
    dept = dept + '\n'

    if d in ('D[0-9]%','%'):
        f  = ' '*(spc[1]-len(str(dt.loc[0,'F'])))  + str(dt.loc[0,'F'])
        m  = ' '*(spc[2]-len(str(dt.loc[0,'M'])))  + str(dt.loc[0,'M'])
        pp = ' '*(spc[3]-len(str(dt.loc[0,'PP']))) + str(dt.loc[0,'PP'])
        p  = ' '*(spc[4]-len(str(dt.loc[0,'P'])))  + str(dt.loc[0,'P'])
        fe = ' '*(spc[5]-len(str(dt.loc[0,'FE']))) + str(dt.loc[0,'FE'])
        total = f'{spc[7]}[{f}|{m}|{pp}|{p}|{fe}]\n'
    else:
        total = str()
        
    depttitle = d.replace('D[0-9]%','Youth').replace('MW[0-9]%','MW').replace('24', '24 Dept').replace('%', 'Church')

    fmp = f"<b><u>{depttitle} BBT : {timetitle}</u></b>\n\n<pre>{spc[6]}\n\n{group}{dept}{total}</pre>"
    fmp = re.sub(r'\.0',r'  ',fmp) # Replaces '.0' with empty space
    fmp = re.sub(r'(\D)0([^.])',r'\1-\2',fmp) # Replaces lone '0' with '-'
    print(">>>Return")
    return fmp