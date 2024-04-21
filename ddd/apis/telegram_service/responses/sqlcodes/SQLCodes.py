import pandas as pd
import numpy as np
import pypyodbc as odbc
import re
from dotenv import load_dotenv, find_dotenv
import os
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

def deptgroup(d):
    conn = odbc.connect(conn_str)
    group_query = f"SELECT DISTINCT MemberGroup, LEN(MemberGroup)Ignore FROM MemberData WHERE GROUP_IMWY LIKE '{d}' ORDER BY LEN(MemberGroup), MemberGroup"
    ga = pd.read_sql(group_query, conn)
    ga.columns = ['Grp','Ignore']
    conn.cursor().close()
    grouplist = []
    for n in range(len(ga)):
        grouplist.append(ga.loc[n,'Grp'].lower())
    return grouplist

def maillist():
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
    return telIDs

def idlist(access,group_or_dept):
    filter = 'MemberGroup' if access == 'group' else 'Group_IMWY'
    conn = odbc.connect(conn_str)
    idtable = pd.read_sql(f"SELECT ID FROM MemberData WHERE {filter} = '{group_or_dept}'", conn)
    conn.cursor().close()
    idlist = []
    for r in range(len(idtable)):
        idlist.append(int(idtable.iloc[r,0]))
    return idlist


def functionlog(uid, name, input_text, command):
    conn = odbc.connect(conn_str)
    input_text = input_text.replace("'","''")
    command = command.replace("'","''")
    conn.cursor().execute(f"INSERT INTO CodeyFunctionLogs (UID, Name, CommandSent, FunctionName, TStamp) VALUES ('{uid}', '{name}', '{input_text}', '{command}', CONVERT(SmallDateTime, SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time'))")
    conn.commit()
    conn.cursor().close()


def teledata(id):
    conn = odbc.connect(conn_str)
    access = f"""SELECT m.Region, t.Access, m.MemberGroup, m.GrpName, m.Group_IMWY, m.Name, m.UID,
    CASE WHEN m.Group_IMWY = 'M&W Dept' THEN 'All' ELSE 'All' END AS SeasonDept, s.MemberGroup sftMemberGroup
    FROM TelegramBotData t
	LEFT JOIN MemberData m ON m.UID = t.UID
	LEFT JOIN MemberDataSFT s ON s.UID = t.UID
	WHERE TelID = {id}""" # Replace the first 'All' to m.Group_IMWY (or even just 'M&W Dept') to change M&W season back to M&W CT (change also on groupinfo function!)
    da = pd.read_sql(access, conn)
    conn.cursor().close()
    
    if len(da) == 0:
        return "None/None/None/None/None/None/None/None/None"
    else:
        return f"{da.iloc[0,0]}/{da.iloc[0,1]}/{da.iloc[0,2]}/{da.iloc[0,3]}/{da.iloc[0,4]}/{da.iloc[0,5]}/{da.iloc[0,6]}/{da.iloc[0,7]}/{da.iloc[0,8]}"

def groupinfo(g):
    conn = odbc.connect(conn_str)
    seasondata = f"""SELECT TOP 1 GrpName, Group_IMWY, Region, CASE WHEN Group_IMWY = 'M&W Dept' THEN 'All' ELSE 'All' END AS SeasonDept
    FROM MemberData m WHERE MemberGroup = '{g}'""" # Replace the first 'All' with GROUP_IMWY to change M&W season back to M&W CT (Change also on teledata function!)
    dr = pd.read_sql(seasondata, conn)
    conn.cursor().close()

    if len(dr) == 0:
        return "None/None/None/None"
    else:
        return f"{dr.iloc[0,0]}/{dr.iloc[0,1]}/{dr.iloc[0,2]}/{dr.iloc[0,3]}"
    

def duplicate_check(ph):
    conn = odbc.connect(conn_str)
    phonecheck = f"SELECT Locked FROM FruitData WHERE FishPhone = {ph} ORDER BY Locked DESC"
    
    dp = pd.read_sql(phonecheck, conn)
    
    conn.cursor().close()
    
    if len(dp) == 0:
        return 'New fish - can proceed'
    elif str(dp.iloc[0,0]) == 'Yes':
        return 'Duplicate - cannot proceed'
    else:
        return 'Fished before but proceedable'





def todayfish(g):
    conn = odbc.connect(conn_str)
    sql_fish = f"SELECT * FROM ScottTodayFish('{g}')"
    sql_pts = f"SELECT(ISNULL((SELECT SUM(F1P) FROM ScottTodayFish('{g}') WHERE F1G LIKE '{g}'),0) + ISNULL((SELECT SUM(F2P) FROM ScottTodayFish('{g}') WHERE F2G LIKE '{g}'),0)) AS Points"
    dp = pd.read_sql(sql_fish, conn)
    dp.iloc[:,2] = dp.iloc[:,2].str.replace(r'^(\d)', r'G\1')
    dp.iloc[:,5] = dp.iloc[:,5].str.replace(r'^(\d)', r'G\1')
    g = re.sub(r'^(\d)',r'G\1',g).capitalize()
    
    if len(dp) == 0:
        return "No fish found"
    else:  
        dp.columns = dp.columns.str.capitalize()
        dp['Timestamp'] = dp['Timestamp'].dt.strftime('%a %d/%m, %I:%M %p')
        dp.replace(np.nan, '', regex = True, inplace = True)
        
        pts = str(pd.read_sql(sql_pts, conn).iloc[0,0])
        conn.cursor().close()

        fish = str()
        for r in range(len(dp)):
            fish = f"{fish}<pre>🐟{r+1}.{dp.iloc[r,0]} - {dp.iloc[r,1]} ({dp.iloc[r,2]}) / {dp.iloc[r,4]} ({dp.iloc[r,5]}) — [{dp.iloc[r,7]}]</pre>\n"
        fish = f"🐠<b><u>{g} Fish Today</u></b>🐡\n\n{fish.replace('/  () ','')}\n<b>{g} Points: {pts}</b>"
        return fish
        


def weekfish(g):
    conn = odbc.connect(conn_str)
    sql_fish = f"SELECT * FROM ScottWeekFish('{g}')"
    sql_pts = f"SELECT(ISNULL((SELECT SUM(F1P) FROM ScottWeekFish('{g}') WHERE F1G LIKE '{g}'),0) + ISNULL((SELECT SUM(F2P) FROM ScottWeekFish('{g}') WHERE F2G LIKE '{g}'),0)) AS Points"
    dp = pd.read_sql(sql_fish, conn)
    dp.iloc[:,2] = dp.iloc[:,2].str.replace(r'^(\d)', r'G\1')
    dp.iloc[:,5] = dp.iloc[:,5].str.replace(r'^(\d)', r'G\1')
    g = re.sub(r'^(\d)',r'G\1',g).capitalize()
    
    if len(dp) == 0:
        return "No fish found"
    else:  
        dp.columns = dp.columns.str.capitalize()
        dp['Timestamp'] = dp['Timestamp'].dt.strftime('%a %d/%m, %I:%M %p')
        dp.replace(np.nan, '', regex = True, inplace = True)
        
        pts = str(pd.read_sql(sql_pts, conn).iloc[0,0])
        conn.cursor().close()
        
        
        
        fish = str()
        for r in range(len(dp)):
            fish = fish + '<pre>🐟' + str(r+1) + '. ' + str(dp.iloc[r,0]) + ' - ' + str(dp.iloc[r,1]) + ' (' + str(dp.iloc[r,2]) + ') / ' + str(dp.iloc[r,4]) + ' (' + str(dp.iloc[r,5]) + ') — [' + str(dp.iloc[r,7]) + ']' + '</pre>\n'
        fish = '🐠<b><u>' + str(g) + ' Fish This Week</u></b>🐡\n\n' + fish.replace('/  () ','') + '\n' + '<b>' + str(g) + ' Points: ' + pts + '</b>'
        return fish



def seasonpick(g):
    conn = odbc.connect(conn_str)
    sql_fish = f"SELECT * FROM ScottSeasonPick('{g}')"
    sql_pts = f"SELECT(ISNULL((SELECT SUM(P1P) FROM ScottSeasonPick('{g}') WHERE P1G LIKE '{g}'),0) + ISNULL((SELECT SUM(P2P) FROM ScottSeasonPick('{g}') WHERE P2G LIKE '{g}'),0)) AS Points"
    dp = pd.read_sql(sql_fish, conn)
    dp.iloc[:,2] = dp.iloc[:,2].str.replace(r'^(\d)', r'G\1')
    dp.iloc[:,5] = dp.iloc[:,5].str.replace(r'^(\d)', r'G\1')
    g = re.sub(r'^(\d)',r'G\1',g).capitalize()
    
    if len(dp) == 0:
        return "No fish found"
    else:  
        dp.columns = dp.columns.str.capitalize()
        dp['Timestamp'] = dp['Timestamp'].dt.strftime('%a %d/%m')
        dp.replace(np.nan, '', regex = True, inplace = True)
        
        pts = str(pd.read_sql(sql_pts, conn).iloc[0,0])
        conn.cursor().close()

        fish = str()
        for r in range(len(dp)):
            fish = fish + '<pre>🍊' + str(r+1) + '. ' + str(dp.iloc[r,0]) + ' - ' + str(dp.iloc[r,1]) + ' (' + str(dp.iloc[r,2]) + ') / ' + str(dp.iloc[r,4]) + ' (' + str(dp.iloc[r,5]) + ') — [' + str(dp.iloc[r,7]) + ']' + '</pre>\n'
        fish = '🍎<b><u>' + str(g) + ' Pickings This Season</u></b>🍏\n\n' + fish.replace('/  () ','') + '\n' + '<b>' + str(g) + ' Points: ' + pts + '</b>'
        return fish



def seasonfe(g):
    conn = odbc.connect(conn_str)

    sql_fish = f"SELECT * FROM ScottSeasonFE('{g}')"
    sql_pts = f"SELECT(ISNULL((SELECT SUM(L1P) FROM ScottSeasonFE('{g}') WHERE L1G LIKE '{g}'),0) + ISNULL((SELECT SUM(L2P) FROM ScottSeasonFE('{g}') WHERE L2G LIKE '{g}'),0)) AS Points"
    dp = pd.read_sql(sql_fish, conn)
    dp.iloc[:,2] = dp.iloc[:,2].str.replace(r'^(\d)', r'G\1')
    dp.iloc[:,5] = dp.iloc[:,5].str.replace(r'^(\d)', r'G\1')
    g = re.sub(r'^(\d)',r'G\1',g).capitalize()
    
    if len(dp) == 0:
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
        return fish


def todaympfe(g):
    conn = odbc.connect(conn_str)
    sql_TM = f"SELECT * FROM ScottTodayMeet('{g}')"
    sql_TM_pts = f"SELECT(ISNULL((SELECT SUM(M1P) FROM ScottTodayMeet('{g}') WHERE M1G LIKE '{g}'),0) + ISNULL((SELECT SUM(M2P) FROM ScottTodayMeet('{g}') WHERE M2G LIKE '{g}'),0)) AS Points"
    dpm = pd.read_sql(sql_TM, conn)
    dpm.iloc[:,2] = dpm.iloc[:,2].str.replace(r'^(\d)', r'G\1')
    dpm.iloc[:,5] = dpm.iloc[:,5].str.replace(r'^(\d)', r'G\1')

    sql_TP = f"SELECT * FROM ScottTodayPick('{g}')"
    sql_TP_pts = f"SELECT(ISNULL((SELECT SUM(P1P) FROM ScottTodayPick('{g}') WHERE P1G LIKE '{g}'),0) + ISNULL((SELECT SUM(P2P) FROM ScottTodayPick('{g}') WHERE P2G LIKE '{g}'),0)) AS Points"
    dpp = pd.read_sql(sql_TP, conn)
    dpp.iloc[:,2] = dpp.iloc[:,2].str.replace(r'^(\d)', r'G\1')
    dpp.iloc[:,5] = dpp.iloc[:,5].str.replace(r'^(\d)', r'G\1')

    sql_TFE = f"SELECT * FROM ScottTodayFE('{g}')"
    sql_TFE_pts = f"SELECT(ISNULL((SELECT SUM(L1P) FROM ScottTodayFE('{g}') WHERE L1G LIKE '{g}'),0) + ISNULL((SELECT SUM(L2P) FROM ScottTodayFE('{g}') WHERE L2G LIKE '{g}'),0)) AS Points"
    dpfe = pd.read_sql(sql_TFE, conn)
    dpfe.iloc[:,2] = dpfe.iloc[:,2].str.replace(r'^(\d)', r'G\1')
    dpfe.iloc[:,5] = dpfe.iloc[:,5].str.replace(r'^(\d)', r'G\1')

    conn.cursor().close()
    g = re.sub(r'^(\d)',r'G\1',g).capitalize()
    
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
    
    return meet + '\n\n' + pick + '\n\n' + fe


def weekmpfe(g):
    conn = odbc.connect(conn_str)
    sql_TM = f"SELECT * FROM ScottWeekMeet('{g}')"
    sql_TM_pts = f"SELECT (ISNULL((SELECT SUM(M1P) FROM ScottWeekMeet('{g}') WHERE M1G LIKE '{g}'),0) + ISNULL((SELECT SUM(M2P) FROM ScottWeekMeet('{g}') WHERE M2G LIKE '{g}'),0)) AS Points"
    dpm = pd.read_sql(sql_TM, conn)
    dpm.iloc[:,2] = dpm.iloc[:,2].str.replace(r'^(\d)', r'G\1')
    dpm.iloc[:,5] = dpm.iloc[:,5].str.replace(r'^(\d)', r'G\1')

    sql_TP = f"SELECT * FROM ScottWeekPick('{g}')"
    sql_TP_pts = f"SELECT (ISNULL((SELECT SUM(P1P) FROM ScottWeekPick('{g}') WHERE P1G LIKE '{g}'),0) + ISNULL((SELECT SUM(P2P) FROM ScottWeekPick('{g}') WHERE P2G LIKE '{g}'),0)) AS Points"
    dpp = pd.read_sql(sql_TP, conn)
    dpp.iloc[:,2] = dpp.iloc[:,2].str.replace(r'^(\d)', r'G\1')
    dpp.iloc[:,5] = dpp.iloc[:,5].str.replace(r'^(\d)', r'G\1')

    sql_TFE = f"SELECT * FROM ScottWeekFE('{g}')"
    sql_TFE_pts = f"SELECT (ISNULL((SELECT SUM(L1P) FROM ScottWeekFE('{g}') WHERE L1G LIKE '{g}'),0) + ISNULL((SELECT SUM(L2P) FROM ScottWeekFE('{g}') WHERE L2G LIKE '{g}'),0)) AS Points"
    dpfe = pd.read_sql(sql_TFE, conn)
    dpfe.iloc[:,2] = dpfe.iloc[:,2].str.replace(r'^(\d)', r'G\1')
    dpfe.iloc[:,5] = dpfe.iloc[:,5].str.replace(r'^(\d)', r'G\1')

    conn.cursor().close()
    g = re.sub(r'^(\d)',r'G\1',g).capitalize()
    
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
    
    return meet + '\n\n' + pick + '\n\n' + fe


# UNIVERSAL MEMBER FMP FUNCTION

def memberfmp(timerange,g,region,seasondept,access):
    
#     print(f"""
# {{
#     "timerange": "{timerange}",
#     "g": "{g}",
#     "region": "{region}",
#     "seasondept": "{seasondept}",
#     "access": "{access}"
# }}""")

    name = 'Member' if access == 'IT' else 'MemberCode'
  
    timevalues = {'today':     ['SELECT dbo.today()', 'SELECT dbo.tomorrow()', 'Today'],
                  'yesterday': ['SELECT dbo.yesterday()', 'SELECT dbo.today()', 'Yesterday'],
                  'week':      ['SELECT dbo.weekstart()', 'SELECT dbo.nextweekstart()', 'This Week'],
                  'lastweek':  ['SELECT dbo.lastweekstart()', 'SELECT dbo.weekstart()', 'Last Week'],
                  'season':    [f"SELECT dbo.ssnstart('{region}','{seasondept}')", 'SELECT dbo.tomorrow()', 'EV Season']}
   
    s,e,title = timevalues[timerange]
    
    conn = odbc.connect(conn_str)
    
    memberQ = f"SELECT {name}, F, M, P, FE FROM ScottMemberFMP((SELECT dbo.ssnid('{region}','{seasondept}')), ({s}), ({e})) WHERE Grp LIKE '{g}'"
    totalQ  = f"SELECT SUM(F)F, SUM(M)M, SUM(P)P, SUM(FE)FE FROM ScottMemberFMP((SELECT dbo.ssnid('{region}','{seasondept}')), ({s}), ({e})) WHERE Grp LIKE '{g}'"
    dm = pd.read_sql(memberQ, conn)
    dt = pd.read_sql(totalQ, conn)

    dm.columns = ['Member','F','M','P','FE']
    dt.columns = ['F','M','P','FE']
    g = re.sub(r'^(\d)',r'G\1',g).capitalize()
    if len(dm) == 0:
        return "No members found"
    else:  
        conn.cursor().close()
        member = str()
        
        for r in range(len(dm)):
            mem = str(dm.loc[r,'Member'])[:8] + ' '*(8-len(str(dm.loc[r,'Member'])[:8]))
            f      = ' '*(4-len(str(dm.loc[r,'F'])))  + str(dm.loc[r,'F'])
            m      = ' '*(4-len(str(dm.loc[r,'M'])))  + str(dm.loc[r,'M'])
            p      = ' '*(3-len(str(dm.loc[r,'P'])))  + str(dm.loc[r,'P'])
            fe     = ' '*(3-len(str(dm.loc[r,'FE']))) + str(dm.loc[r,'FE'])
            
            member = f'{member}{mem}[{f}|{m}|{p}|{fe}]\n'
            
        f      = ' '*(4-len(str(dt.loc[0,'F'])))  + str(dt.loc[0,'F'])
        m      = ' '*(4-len(str(dt.loc[0,'M'])))  + str(dt.loc[0,'M'])
        p      = ' '*(3-len(str(dt.loc[0,'P'])))  + str(dt.loc[0,'P'])
        fe     = ' '*(3-len(str(dt.loc[0,'FE']))) + str(dt.loc[0,'FE'])
        
        total = f'Total   [{f}|{m}|{p}|{fe}]'
        
        member = f'<b><u>{g} FMPFE : {title}</u></b>\n\n<pre>Member  [FF.F|MM.M|P.P|F.E]\n\n{member}\n{total}</pre>'
        member = re.sub(r'\.0',r'  ',member) # Replaces '.0' with empty space
        member = re.sub(r'(\D)0([^.])',r'\1-\2',member)   # Replaces lone '0' with '-'
        return member
    

# UNIVERSAL DEPT FMP FUNCTION:

def deptfmp(task,timerange,d,region,seasondept,access):
    
    displayMembers = False if task == 'dept' and access in ('All','IT') else True
    topleft = 'Grp ' if displayMembers == True else 'Dept'
    
    if task == 'dept':
        task = 'youth'
    
    taskvalues = {'youth' : [''       , ''            ],
                  'tgw'   : [' TGW'   , ' AND Ptn < 7'],
                  'member': [' Member', ' AND Ptn = 7']}
    tasktitle = taskvalues[task][0]
    taskQ = taskvalues[task][1]
  
    if timerange in {'today','yesterday'}:
        spc = [6,5,4,4,4,f'{topleft}  [FFF.F|MM.M|PP.P|FF.E]',   'Total ']
    if timerange in {'week','lastweek'}:
        spc = [5,5,5,4,4,f'{topleft} [FFF.F|MMM.M|PP.P|FF.E]',   'Total']
    if timerange == 'season':
        spc = [4,6,6,5,5,f'{topleft}[FFFF.F|MMMM.M|PPP.P|FFF.E]','Tot ']   

    timevalues = {'today':     ['SELECT dbo.today()', 'SELECT dbo.tomorrow()', 'Today'],
                  'yesterday': ['SELECT dbo.yesterday()', 'SELECT dbo.today()', 'Yesterday'],
                  'week':      ['SELECT dbo.weekstart()', 'SELECT dbo.nextweekstart()', 'This Week'],
                  'lastweek':  ['SELECT dbo.lastweekstart()', 'SELECT dbo.weekstart()', 'Last Week'],
                  'season':    [f"SELECT dbo.ssnstart('{region}','{seasondept}')", 'SELECT dbo.tomorrow()', 'EV Season']}
    
    s,e,timetitle = timevalues[timerange]
       
    conn = odbc.connect(conn_str)
    memberQ = f"SELECT Grp, SUM(F)F, SUM(M)M, SUM(P)P, SUM(FE)FE FROM ScottMemberFMP((SELECT dbo.ssnid('{region}','{seasondept}')), ({s}), ({e})) WHERE Dept LIKE '{d}'{taskQ} GROUP BY Grp ORDER BY LEN(Grp), Grp"
    deptQ   = f"SELECT Dept, SUM(F)F, SUM(M)M, SUM(P)P, SUM(FE)FE FROM ScottMemberFMP((SELECT dbo.ssnid('{region}','{seasondept}')), ({s}), ({e})) WHERE Dept LIKE '{d}'{taskQ} GROUP BY Dept ORDER BY Dept"  
    totalQ  = f"SELECT SUM(F)F, SUM(M)M, SUM(P)P, SUM(FE)FE FROM ScottMemberFMP((SELECT dbo.ssnid('{region}','{seasondept}')), ({s}), ({e})) WHERE Dept LIKE '{d}'{taskQ}"
    dm = pd.read_sql(memberQ, conn)
    dd = pd.read_sql(deptQ, conn)
    dt = pd.read_sql(totalQ, conn)

    dm.columns = ['Grp','F','M','P','FE']
    dd.columns = ['Dept','F','M','P','FE']
    dt.columns = ['F','M','P','FE']
    dm['Grp'] = dm['Grp'].str.replace(r'^(\d)', r'G\1')
    dd.replace(r' Dept',r'', regex = True, inplace = True)

    conn.cursor().close()
    
    group = str()
    
    if displayMembers:
        for r in range(len(dm)):
            grp = str(dm.loc[r,'Grp']) + '.'*(spc[0]-len(str(dm.loc[r,'Grp'])))
            f  = ' '*(spc[1]-len(str(dm.loc[r,'F'])))  + str(dm.loc[r,'F'])
            m  = ' '*(spc[2]-len(str(dm.loc[r,'M'])))  + str(dm.loc[r,'M'])
            p  = ' '*(spc[3]-len(str(dm.loc[r,'P'])))  + str(dm.loc[r,'P'])
            fe = ' '*(spc[4]-len(str(dm.loc[r,'FE']))) + str(dm.loc[r,'FE'])
            group = f'{group}{grp}[{f}|{m}|{p}|{fe}]\n'
        group = group + '\n'

    dept = str()    
    for r in range(len(dd)):
        dpt = str(dd.loc[r,'Dept']) + '.'*(spc[0]-len(str(dd.loc[r,'Dept'])))
        f  = ' '*(spc[1]-len(str(dd.loc[r,'F'])))  + str(dd.loc[r,'F'])
        m  = ' '*(spc[2]-len(str(dd.loc[r,'M'])))  + str(dd.loc[r,'M'])
        p  = ' '*(spc[3]-len(str(dd.loc[r,'P'])))  + str(dd.loc[r,'P'])
        fe = ' '*(spc[4]-len(str(dd.loc[r,'FE']))) + str(dd.loc[r,'FE'])
        dept = f'{dept}{dpt}[{f}|{m}|{p}|{fe}]\n'

    if d == '__' :
        f  = ' '*(spc[1]-len(str(dt.loc[0,'F'])))  + str(dt.loc[0,'F'])
        m  = ' '*(spc[2]-len(str(dt.loc[0,'M'])))  + str(dt.loc[0,'M'])
        p  = ' '*(spc[3]-len(str(dt.loc[0,'P'])))  + str(dt.loc[0,'P'])
        fe = ' '*(spc[4]-len(str(dt.loc[0,'FE']))) + str(dt.loc[0,'FE'])
        total = f'\n{spc[6]}[{f}|{m}|{p}|{fe}]'
    else:
        total = str()
        
    depttitle = d.replace('__','Youth')

    fmp = f"<b><u>{depttitle}{tasktitle} FMPFE : {timetitle}</u></b>\n\n<pre>{spc[5]}\n\n{group}{dept}{total}</pre>"
    fmp = re.sub(r'\.0',r'  ',fmp) # Replaces '.0' with empty space
    fmp = re.sub(r'(\D)0([^.])',r'\1-\2',fmp)   # Replaces lone '0' with '-'
    return fmp



def taskfmp(task,timerange,d,region,seasondept,access):
    
    name = 'Member' if access == 'IT' else 'MemberInitial'
        
    taskvalues = {'gyjn': [' GYJN'   , ''            ],
                  'oev' : [' OEV TJN', ' AND Ptn < 7'],
                  'iev' : [' IEV TJN', ' AND Ptn = 7'],
                  'edu' : [' EDU TJN', ''            ],
                  'sv'  : [' SV TJN' , ''            ]}
    tasktitle = taskvalues[task][0]
    
    if access == 'IT':
        if timerange in {'today','yesterday'}:
            spc = [10,4,4,4,4,'G#|TGW    [FF.F|MM.M|PP.P|FF.E]','Total.....']
        elif timerange in {'week','lastweek'}:
            spc = [9,5,4,4,4,'G#|TGW   [FFF.F|MM.M|PP.P|FF.E]','Total....']
        elif timerange == 'season':
            spc = [8,5,5,4,4,'G#|TGW  [FFF.F|MMM.M|PP.P|FF.E]','Total...']
    else:
        if timerange in {'today','yesterday'}:
            spc = [7,4,4,4,4,'G#|TGW [FF.F|MM.M|PP.P|FF.E]',  'Total  ']
        elif timerange in {'week','lastweek'}:
            spc = [7,5,4,4,4,'G#|TGW [FFF.F|MM.M|PP.P|FF.E]', 'Total  ']
        elif timerange == 'season':
            spc = [7,5,5,4,4,'G#|TGW [FFF.F|MMM.M|PP.P|FF.E]','Total  ']

    timevalues = {'today':     ['SELECT dbo.today()', 'SELECT dbo.tomorrow()', 'Today'],
                  'yesterday': ['SELECT dbo.yesterday()', 'SELECT dbo.today()', 'Yesterday'],
                  'week':      ['SELECT dbo.weekstart()', 'SELECT dbo.nextweekstart()', 'This Week'],
                  'lastweek':  ['SELECT dbo.lastweekstart()', 'SELECT dbo.weekstart()', 'Last Week'],
                  'season':    [f"SELECT dbo.ssnstart('{region}','{seasondept}')", 'SELECT dbo.tomorrow()', 'EV Season']}
    
    s,e,timetitle = timevalues[timerange]
       
    conn = odbc.connect(conn_str)
    memberQ = f"""SELECT Grp, {name}, F, M, P, FE FROM (
    SELECT s.Grp, {name}, F, M, P, FE,
    CASE
    	WHEN Title = 'GYJN' THEN Title
    	ELSE Task
    END AS Position
    FROM ScottMemberFMP((SELECT dbo.ssnid('{region}','{seasondept}')), ({s}), ({e})) s
    LEFT JOIN TaskHigh t ON s.UID = t.UID
    WHERE Dept LIKE '{d}') p
WHERE Position LIKE '{task}'
ORDER BY LEN(Grp), Grp"""
    deptQ   = f"""SELECT Dept, SUM(F)F, SUM(M)M, SUM(P)P, SUM(FE)FE FROM (SELECT s.Dept, F, M, P, FE,
CASE
	WHEN Title = 'GYJN' THEN Title
	ELSE Task
	END AS Position
FROM ScottMemberFMP((SELECT dbo.ssnid('{region}','{seasondept}')), ({s}), ({e})) s
LEFT JOIN TaskHigh t ON s.UID = t.UID
WHERE Dept LIKE '{d}') p
WHERE Position LIKE '{task}'
GROUP BY Dept
ORDER BY Dept"""
    totalQ  = f"""SELECT SUM(F)F, SUM(M)M, SUM(P)P, SUM(FE)FE FROM (SELECT s.Dept, F, M, P, FE,
CASE
	WHEN Title = 'GYJN' THEN Title
	ELSE Task
	END AS Position
FROM ScottMemberFMP((SELECT dbo.ssnid('{region}','{seasondept}')), ({s}), ({e})) s
LEFT JOIN TaskHigh t ON s.UID = t.UID
WHERE Dept LIKE '{d}') p
WHERE Position LIKE '{task}'"""
    
    dm = pd.read_sql(memberQ, conn)
    dd = pd.read_sql(deptQ, conn)
    dt = pd.read_sql(totalQ, conn)

    dm.columns = ['Grp','Member','F','M','P','FE']
    dd.columns = ['Dept','F','M','P','FE']
    dt.columns = ['F','M','P','FE']
    dm['Grp'] = dm['Grp'].str.replace(r'^(\d)', r'G\1')
    dd.replace(r' Dept',r'', regex = True, inplace = True)

    conn.cursor().close()

    group = str()
    for r in range(len(dm)):
        grpmem = f"{dm.loc[r,'Grp']}|{dm.loc[r,'Member']}"
        grpmem = f"{grpmem[:spc[0]]}{' '*(spc[0]-len(grpmem[:spc[0]]))}"
        f  = ' '*(spc[1]-len(str(dm.loc[r,'F'])))  + str(dm.loc[r,'F'])
        m  = ' '*(spc[2]-len(str(dm.loc[r,'M'])))  + str(dm.loc[r,'M'])
        p  = ' '*(spc[3]-len(str(dm.loc[r,'P'])))  + str(dm.loc[r,'P'])
        fe = ' '*(spc[4]-len(str(dm.loc[r,'FE']))) + str(dm.loc[r,'FE'])
        group = f'{group}{grpmem}[{f}|{m}|{p}|{fe}]\n'

    dept = str()    
    for r in range(len(dd)):
        dpt = str(dd.loc[r,'Dept']) + ' '*(spc[0]-len(str(dd.loc[r,'Dept'])))
        f  = ' '*(spc[1]-len(str(dd.loc[r,'F'])))  + str(dd.loc[r,'F'])
        m  = ' '*(spc[2]-len(str(dd.loc[r,'M'])))  + str(dd.loc[r,'M'])
        p  = ' '*(spc[3]-len(str(dd.loc[r,'P'])))  + str(dd.loc[r,'P'])
        fe = ' '*(spc[4]-len(str(dd.loc[r,'FE']))) + str(dd.loc[r,'FE'])
        dept = f'{dept}{dpt}[{f}|{m}|{p}|{fe}]\n'

    if d == '__' :
        f  = ' '*(spc[1]-len(str(dt.loc[0,'F'])))  + str(dt.loc[0,'F'])
        m  = ' '*(spc[2]-len(str(dt.loc[0,'M'])))  + str(dt.loc[0,'M'])
        p  = ' '*(spc[3]-len(str(dt.loc[0,'P'])))  + str(dt.loc[0,'P'])
        fe = ' '*(spc[4]-len(str(dt.loc[0,'FE']))) + str(dt.loc[0,'FE'])
        total = f'\n{spc[6]}[{f}|{m}|{p}|{fe}]'
    else:
        total = str()
        
    depttitle = d.replace('__','Youth')

    fmp = f"<b><u>{depttitle}{tasktitle} FMPFE : {timetitle}</u></b>\n\n<pre>{spc[5]}\n\n{group}\n{dept}{total}</pre>"
    fmp = re.sub(r'\.0',r'  ',fmp) # Replaces '.0' with empty space
    fmp = re.sub(r'(\D)0([^.])',r'\1-\2',fmp)   # Replaces lone '0' with '-'
    return fmp



def youthmxpx(d):

    conn = odbc.connect(conn_str)
    exp_group = f"SELECT Grp, SUM(Mx)Mx, SUM(Px)Px FROM ScottFutureMxPx WHERE DEPT LIKE '{d}' GROUP BY Grp ORDER BY LEN(Grp),Grp"
    exp_dept = f"SELECT Dept, SUM(Mx)Mx, SUM(Px)Px FROM ScottFutureMxPx WHERE DEPT LIKE '{d}' GROUP BY Dept"
    exp_youth = f"SELECT SUM(Mx)Mx, SUM(Px)Px FROM ScottFutureMxPx WHERE DEPT LIKE '{d}'"
    
    dg = pd.read_sql(exp_group, conn)
    dd = pd.read_sql(exp_dept, conn)
    dy = pd.read_sql(exp_youth, conn)
    
    dg.columns = ['Grp','Mx','Px']
    dd.columns = ['Dept','Mx','Px']
    dy.columns = ['Mx','Px']
    dg['Grp'] = dg['Grp'].str.replace(r'^(\d)', r'G\1')
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
    
    if d == '__':
        spc = ' '*(4-len(str(dy.iloc[0,0])))
        mx = ' '*(4-len(str(dy.loc[0,'Mx']))) + str(dy.loc[0,'Mx'])
        px = ' '*(4-len(str(dy.loc[0,'Px']))) + str(dy.loc[0,'Px'])
        youth = f'\nTotal{spc}[{mx}|{px}]'
    else:
        youth = str()
        
    result = f'<b><u>Meeting and Picking Expectants: </u></b>\n\n<pre>Grp   [MM.X|PP.X]\n\n{group}\n{dept}{youth}</pre>'
    result = re.sub(r'\.0',r'  ',result) # Replaces '.0' with empty space
    result = re.sub(r'(\D)0([^.])',r'\1-\2',result)   # Replaces lone '0' with '-'
    return result


    
    
def mxlist(g):
    conn = odbc.connect(conn_str)
    dd1 = pd.read_sql(f"SELECT * FROM ScottFutureMxList WHERE ExpMeet >= DATEADD(DAY,0,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND ExpMeet < DATEADD(DAY,1,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND (L1G LIKE '{g}' OR L2G LIKE '{g}')", conn)
    dd2 = pd.read_sql(f"SELECT * FROM ScottFutureMxList WHERE ExpMeet >= DATEADD(DAY,1,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND ExpMeet < DATEADD(DAY,2,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND (L1G LIKE '{g}' OR L2G LIKE '{g}')", conn)
    dd3 = pd.read_sql(f"SELECT * FROM ScottFutureMxList WHERE ExpMeet >= DATEADD(DAY,2,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND ExpMeet < DATEADD(DAY,3,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND (L1G LIKE '{g}' OR L2G LIKE '{g}')", conn)
    dd4 = pd.read_sql(f"SELECT * FROM ScottFutureMxList WHERE ExpMeet >= DATEADD(DAY,3,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND ExpMeet < DATEADD(DAY,4,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND (L1G LIKE '{g}' OR L2G LIKE '{g}')", conn)
    dd5 = pd.read_sql(f"SELECT * FROM ScottFutureMxList WHERE ExpMeet >= DATEADD(DAY,4,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND ExpMeet < DATEADD(DAY,5,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND (L1G LIKE '{g}' OR L2G LIKE '{g}')", conn)
    dd6 = pd.read_sql(f"SELECT * FROM ScottFutureMxList WHERE ExpMeet >= DATEADD(DAY,5,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND ExpMeet < DATEADD(DAY,6,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND (L1G LIKE '{g}' OR L2G LIKE '{g}')", conn)
    dd7 = pd.read_sql(f"SELECT * FROM ScottFutureMxList WHERE ExpMeet >= DATEADD(DAY,6,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND ExpMeet < DATEADD(DAY,7,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND (L1G LIKE '{g}' OR L2G LIKE '{g}')", conn)
    conn.cursor().close()
    dd1['l1g'] = dd1['l1g'].str.replace(r'^(\d)', r'G\1')
    dd2['l1g'] = dd2['l1g'].str.replace(r'^(\d)', r'G\1')
    dd3['l1g'] = dd3['l1g'].str.replace(r'^(\d)', r'G\1')
    dd4['l1g'] = dd4['l1g'].str.replace(r'^(\d)', r'G\1')
    dd5['l1g'] = dd5['l1g'].str.replace(r'^(\d)', r'G\1')
    dd6['l1g'] = dd6['l1g'].str.replace(r'^(\d)', r'G\1')
    dd7['l1g'] = dd7['l1g'].str.replace(r'^(\d)', r'G\1')
    dd1['l2g'] = dd1['l2g'].str.replace(r'^(\d)', r'G\1')
    dd2['l2g'] = dd2['l2g'].str.replace(r'^(\d)', r'G\1')
    dd3['l2g'] = dd3['l2g'].str.replace(r'^(\d)', r'G\1')
    dd4['l2g'] = dd4['l2g'].str.replace(r'^(\d)', r'G\1')
    dd5['l2g'] = dd5['l2g'].str.replace(r'^(\d)', r'G\1')
    dd6['l2g'] = dd6['l2g'].str.replace(r'^(\d)', r'G\1')
    dd7['l2g'] = dd7['l2g'].str.replace(r'^(\d)', r'G\1')
    
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
    return f'<i><b><u>👥Meeting Expectants👥</u></b>\n. . . . Next seven days . . . .</i>\n{mx1}{mx2}{mx3}{mx4}{mx5}{mx6}{mx7}'  if len(f'{mx1}{mx2}{mx3}{mx4}{mx5}{mx6}{mx7}') != 0 else '<i>No meeting expectants in next 7 days</i>'







def pxlist(g):
    conn = odbc.connect(conn_str)
    dd1 = pd.read_sql(f"SELECT * FROM ScottFuturePxList WHERE ExpPick >= DATEADD(DAY,0,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND ExpPick < DATEADD(DAY,1,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND (L1G LIKE '{g}' OR L2G LIKE '{g}')", conn)
    dd2 = pd.read_sql(f"SELECT * FROM ScottFuturePxList WHERE ExpPick >= DATEADD(DAY,1,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND ExpPick < DATEADD(DAY,2,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND (L1G LIKE '{g}' OR L2G LIKE '{g}')", conn)
    dd3 = pd.read_sql(f"SELECT * FROM ScottFuturePxList WHERE ExpPick >= DATEADD(DAY,2,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND ExpPick < DATEADD(DAY,3,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND (L1G LIKE '{g}' OR L2G LIKE '{g}')", conn)
    dd4 = pd.read_sql(f"SELECT * FROM ScottFuturePxList WHERE ExpPick >= DATEADD(DAY,3,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND ExpPick < DATEADD(DAY,4,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND (L1G LIKE '{g}' OR L2G LIKE '{g}')", conn)
    dd5 = pd.read_sql(f"SELECT * FROM ScottFuturePxList WHERE ExpPick >= DATEADD(DAY,4,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND ExpPick < DATEADD(DAY,5,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND (L1G LIKE '{g}' OR L2G LIKE '{g}')", conn)
    dd6 = pd.read_sql(f"SELECT * FROM ScottFuturePxList WHERE ExpPick >= DATEADD(DAY,5,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND ExpPick < DATEADD(DAY,6,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND (L1G LIKE '{g}' OR L2G LIKE '{g}')", conn)
    dd7 = pd.read_sql(f"SELECT * FROM ScottFuturePxList WHERE ExpPick >= DATEADD(DAY,6,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND ExpPick < DATEADD(DAY,7,CONVERT(DATE,SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')) AND (L1G LIKE '{g}' OR L2G LIKE '{g}')", conn)
    conn.cursor().close()
    dd1['l1g'] = dd1['l1g'].str.replace(r'^(\d)', r'G\1')
    dd2['l1g'] = dd2['l1g'].str.replace(r'^(\d)', r'G\1')
    dd3['l1g'] = dd3['l1g'].str.replace(r'^(\d)', r'G\1')
    dd4['l1g'] = dd4['l1g'].str.replace(r'^(\d)', r'G\1')
    dd5['l1g'] = dd5['l1g'].str.replace(r'^(\d)', r'G\1')
    dd6['l1g'] = dd6['l1g'].str.replace(r'^(\d)', r'G\1')
    dd7['l1g'] = dd7['l1g'].str.replace(r'^(\d)', r'G\1')
    dd1['l2g'] = dd1['l2g'].str.replace(r'^(\d)', r'G\1')
    dd2['l2g'] = dd2['l2g'].str.replace(r'^(\d)', r'G\1')
    dd3['l2g'] = dd3['l2g'].str.replace(r'^(\d)', r'G\1')
    dd4['l2g'] = dd4['l2g'].str.replace(r'^(\d)', r'G\1')
    dd5['l2g'] = dd5['l2g'].str.replace(r'^(\d)', r'G\1')
    dd6['l2g'] = dd6['l2g'].str.replace(r'^(\d)', r'G\1')
    dd7['l2g'] = dd7['l2g'].str.replace(r'^(\d)', r'G\1')
    
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
    return f'<i><b><u>👥Picking Expectants</u></b>\n. . . . Next seven days . . . .</i>\n{px1}{px2}{px3}{px4}{px5}{px6}{px7}' if len(f'{px1}{px2}{px3}{px4}{px5}{px6}{px7}') != 0 else '<i>No picking expectants in next 7 days</i>'
















def bbtstatus(q, g, d, r, access):
        
    name = 'BBT' if access == 'IT' else 'BBTCode2'
    g = g if access == 'Group' else '%'
    d = d.capitalize()
    grpdept = re.sub(r'^(\d)',r'G\1',g).capitalize() if access == 'Group' else str(d).replace('__','Youth')
    
    i = q if q in ['bbt','gyjnbbt'] else 'btm'
    bbtvalues = {'bbt'     : ['BBT',   ""],
                 'gyjnbbt' : ['GYJN BBT',  " AND t.Title = 'GYJN'"],
                 'btm'     : [q.upper(), f" AND BtmNo = '{q[3:]}'"]}
    bbttype,query = bbtvalues[i]
    
    conn = odbc.connect(conn_str)
    bb_mem = f"SELECT Dept, Grp, {name}, pNew, pOld, bbA, cctA, bbME, cctI, pFA, bbFA, Total FROM CodeyBBTStatusMembers('{r}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}'{query} ORDER BY LEN(Grp), Grp, {name}"
    bb_group = f"SELECT Grp, SUM(pNew)pNew, SUM(pOld)pOld, SUM(bbA)bbA, SUM(cctA)cctA, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA, SUM(Total)Total FROM CodeyBBTStatusMembers('{r}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}'{query} Group BY Grp ORDER BY LEN(Grp), Grp"
    bb_dept = f"SELECT Dept, SUM(pNew)pNew, SUM(pOld)pOld, SUM(bbA)bbA, SUM(cctA)cctA, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA, SUM(Total)Total FROM CodeyBBTStatusMembers('{r}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}'{query} Group BY Dept"
    bb_youth = f"SELECT SUM(pNew)pNew, SUM(pOld)pOld, SUM(bbA)bbA, SUM(cctA)cctA, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA, SUM(Total)Total FROM CodeyBBTStatusMembers('{r}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}'{query}"
    
    dm = pd.read_sql(bb_mem, conn)
    dg = pd.read_sql(bb_group, conn)
    dd = pd.read_sql(bb_dept, conn)
    dy = pd.read_sql(bb_youth, conn)

    dm.columns = ['Dept','Grp','BBT','pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
    dg.columns = ['Grp','pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
    dd.columns = ['Dept','pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
    dy.columns = ['pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
    dm['Grp'] = dm['Grp'].str.replace(r'^(\d)', r'G\1')
    dg['Grp'] = dg['Grp'].str.replace(r'^(\d)', r'G\1')
    dd.replace(r' Dept',r'', regex = True, inplace = True)
    
    conn.cursor().close()

    member = str()
    if d != '__':
        member = '\n'
        for r in range(len(dm)):
            bbt =   str(dm.loc[r,'BBT'][:5]) + ' '*(5-len(str(dm.loc[r,'BBT'][:5])))
            pn  = ' '*(3-len(str(dm.loc[r,'pNew']))) + str(dm.loc[r,'pNew'])
            po  = ' '*(3-len(str(dm.loc[r,'pOld']))) + str(dm.loc[r,'pOld'])
            ba  = ' '*(3-len(str(dm.loc[r,'bbA'])))  + str(dm.loc[r,'bbA'])
            ca  = ' '*(3-len(str(dm.loc[r,'cctA']))) + str(dm.loc[r,'cctA'])
            bm  = ' '*(3-len(str(dm.loc[r,'bbME']))) + str(dm.loc[r,'bbME'])
            ci  = ' '*(3-len(str(dm.loc[r,'cctI']))) + str(dm.loc[r,'cctI'])
            pf  = ' '*(3-len(str(dm.loc[r,'pFA'])))  + str(dm.loc[r,'pFA'])
            bf  = ' '*(3-len(str(dm.loc[r,'bbFA']))) + str(dm.loc[r,'bbFA'])
            t   = ' '*(3-len(str(dm.loc[r,'Tot'])))  + str(dm.loc[r,'Tot'])
            member = f'{member}{bbt}[{pn}|{po}|{ba}|{ca}|{bm}|{ci}|{pf}|{bf}|{t}]\n'
            
            
    group = str()    
    for r in range(len(dg)):
        grp =   str(dg.loc[r,'Grp']) + ' '*(5-len(str(dg.loc[r,'Grp'])))
        pn  = ' '*(3-len(str(dg.loc[r,'pNew']))) + str(dg.loc[r,'pNew'])
        po  = ' '*(3-len(str(dg.loc[r,'pOld']))) + str(dg.loc[r,'pOld'])
        ba  = ' '*(3-len(str(dg.loc[r,'bbA'])))  + str(dg.loc[r,'bbA'])
        ca  = ' '*(3-len(str(dg.loc[r,'cctA']))) + str(dg.loc[r,'cctA'])
        bm  = ' '*(3-len(str(dg.loc[r,'bbME']))) + str(dg.loc[r,'bbME'])
        ci  = ' '*(3-len(str(dg.loc[r,'cctI']))) + str(dg.loc[r,'cctI'])
        pf  = ' '*(3-len(str(dg.loc[r,'pFA'])))  + str(dg.loc[r,'pFA'])
        bf  = ' '*(3-len(str(dg.loc[r,'bbFA']))) + str(dg.loc[r,'bbFA'])
        t   = ' '*(3-len(str(dg.loc[r,'Tot'])))  + str(dg.loc[r,'Tot'])
        group = f'{group}{grp}[{pn}|{po}|{ba}|{ca}|{bm}|{ci}|{pf}|{bf}|{t}]\n'
            
    dept = str()  
    if access != 'Group':  
        for r in range(len(dd)):
            dpt =   str(dd.loc[r,'Dept']) + ' '*(5-len(str(dd.loc[r,'Dept'])))
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
            
    if d == '__':
        pn  = ' '*(3-len(str(dy.loc[0,'pNew']))) + str(dy.loc[0,'pNew'])
        po  = ' '*(3-len(str(dy.loc[0,'pOld']))) + str(dy.loc[0,'pOld'])
        ba  = ' '*(3-len(str(dy.loc[0,'bbA'])))  + str(dy.loc[0,'bbA'])
        ca  = ' '*(3-len(str(dy.loc[0,'cctA']))) + str(dy.loc[0,'cctA'])
        bm  = ' '*(3-len(str(dy.loc[0,'bbME']))) + str(dy.loc[0,'bbME'])
        ci  = ' '*(3-len(str(dy.loc[0,'cctI']))) + str(dy.loc[0,'cctI'])
        pf  = ' '*(3-len(str(dy.loc[0,'pFA'])))  + str(dy.loc[0,'pFA'])
        bf  = ' '*(3-len(str(dy.loc[0,'bbFA']))) + str(dy.loc[0,'bbFA'])
        t   = ' '*(3-len(str(dy.loc[0,'Tot'])))  + str(dy.loc[0,'Tot'])
        youth = f'\nTotal[{pn}|{po}|{ba}|{ca}|{bm}|{ci}|{pf}|{bf}|{t}]'

    else:
        youth = str()
    
    summary = f"<b><u>{grpdept} {bbttype} Status Summary</u></b>\n\n<pre>     [ NP| OP| AB| CA| ME| CI| FP| FA|TOT]\n{member}\n{group}\n{dept}{youth}</pre>"
    summary = re.sub(r'\.0',r'  ',summary) # Replaces '.0' with empty space
    summary = re.sub(r'(\D)0([^.])',r'\1-\2',summary)   # Replaces lone '0' with '-'
    return summary





def deptbbtstatus(q, d, r, access):
    
    name = 'BBT' if access == 'IT' else 'BBTCode'
    d = d.capitalize()
    
    i = q if q in ['bbt','gyjnbbt'] else 'btm'
    bbtvalues = {'bbt'     : ['BBT',   ""],
                 'gyjnbbt' : ['GYJN BBT',  " AND t.Title = 'GYJN'"],
                 'btm'     : [q.upper(), f" AND BtmNo = '{q[3:]}'"]}
    bbttype,query = bbtvalues[i]
    
    conn = odbc.connect(conn_str)
    bb_dept = f"SELECT Dept, SUM(pNew)pNew, SUM(pOld)pOld, SUM(bbA)bbA, SUM(cctA)cctA, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA, SUM(Total)Total FROM CodeyBBTStatusMembers('{r}') WHERE Dept LIKE '{d}'{query} Group BY Dept"
    bb_youth = f"SELECT SUM(pNew)pNew, SUM(pOld)pOld, SUM(bbA)bbA, SUM(cctA)cctA, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA, SUM(Total)Total FROM CodeyBBTStatusMembers('{r}') WHERE Dept LIKE '{d}'{query}"
    
    dd = pd.read_sql(bb_dept, conn)
    dy = pd.read_sql(bb_youth, conn)

    dd.columns = ['Dept','pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
    dy.columns = ['pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
    dd.replace(r' Dept',r'', regex = True, inplace = True)
    
    conn.cursor().close()

    dept = str()    
    for r in range(len(dd)):
        dpt =   str(dd.loc[r,'Dept'])[:3] + ' '*(3-len(str(dd.loc[r,'Dept'])[:3]))
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
            
    if d == '__':
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
    
    summary = f"<b><u>{str(d).replace('__','Youth')} {bbttype} Status Summary</u></b>\n\n<pre>   [ NP| OP| AB| CA| ME| CI| FP| FA|TOT]\n\n{dept}{youth}</pre>"
    summary = re.sub(r'\.0',r'  ',summary) # Replaces '.0' with empty space
    summary = re.sub(r'(\D)0([^.])',r'\1-\2',summary)   # Replaces lone '0' with '-'
    return summary





def bbtactive(q, g, d, r, access):
    
    name = 'BBT' if access == 'IT' else 'BBTCode2'
    g = g if access == 'Group' else '%'
    d = d.capitalize()
    grpdept = re.sub(r'^(\d)',r'G\1',g).capitalize() if access == 'Group' else str(d).replace('__','Youth')
    
    i = q if q in ['bbt','gyjnbbt'] else 'btm'
    bbtvalues = {'bbt'     : ['BBT',   ""],
                 'gyjnbbt' : ['GYJN BBT',  " AND t.Title = 'GYJN'"],
                 'btm'     : [q.upper(), f" AND BtmNo = '{q[3:]}'"]}
    bbttype,query = bbtvalues[i]
    
    conn = odbc.connect(conn_str)
    bb_mem = f"SELECT Dept, Grp, {name}, pNew, pOld, bbA, cctA, bbME, cctI, pFA, bbFA, Total FROM CodeyBBTStatusMembers('{r}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}'{query} ORDER BY LEN(Grp), Grp, {name}"
    bb_group = f"SELECT Grp, SUM(pNew)pNew, SUM(pOld)pOld, SUM(bbA)bbA, SUM(cctA)cctA, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA, SUM(Total)Total FROM CodeyBBTStatusMembers('{r}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}'{query} Group BY Grp ORDER BY LEN(Grp), Grp"
    bb_dept = f"SELECT Dept, SUM(pNew)pNew, SUM(pOld)pOld, SUM(bbA)bbA, SUM(cctA)cctA, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA, SUM(Total)Total FROM CodeyBBTStatusMembers('{r}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}'{query} Group BY Dept"
    bb_youth = f"SELECT SUM(pNew)pNew, SUM(pOld)pOld, SUM(bbA)bbA, SUM(cctA)cctA, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA, SUM(Total)Total FROM CodeyBBTStatusMembers('{r}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}'{query}"
    
    dm = pd.read_sql(bb_mem, conn)
    dg = pd.read_sql(bb_group, conn)
    dd = pd.read_sql(bb_dept, conn)
    dy = pd.read_sql(bb_youth, conn)

    dm.columns = ['Dept','Grp','BBT','pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
    dg.columns = ['Grp','pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
    dd.columns = ['Dept','pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
    dy.columns = ['pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
    dm['Grp'] = dm['Grp'].str.replace(r'^(\d)', r'G\1')
    dg['Grp'] = dg['Grp'].str.replace(r'^(\d)', r'G\1')
    dd.replace(r' Dept',r'', regex = True, inplace = True)
    
    conn.cursor().close()

    member = str()
    if d != '__':
        member = '\n'
        for r in range(len(dm)):
            bbt =   str(dm.loc[r,'BBT'][:5]) + ' '*(5-len(str(dm.loc[r,'BBT'][:5])))
            pn  = ' '*(3-len(str(dm.loc[r,'pNew']))) + str(dm.loc[r,'pNew'])
            ba  = ' '*(3-len(str(dm.loc[r,'bbA'])))  + str(dm.loc[r,'bbA'])
            ca  = ' '*(3-len(str(dm.loc[r,'cctA']))) + str(dm.loc[r,'cctA'])
            t   = ' '*(3-len(str(dm.loc[r,'Tot'])))  + str(dm.loc[r,'Tot'])
            member = f'{member}{bbt}[{pn}|{ba}|{ca}]\n'
            
            
    group = str()
    for r in range(len(dg)):
        grp =    str(dg.loc[r,'Grp']) + ' '*(5-len(str(dg.loc[r,'Grp'])))
        pn  = ' '*(3-len(str(dg.loc[r,'pNew']))) + str(dg.loc[r,'pNew'])
        ba  = ' '*(3-len(str(dg.loc[r,'bbA'])))  + str(dg.loc[r,'bbA'])
        ca  = ' '*(3-len(str(dg.loc[r,'cctA']))) + str(dg.loc[r,'cctA'])
        group = f'{group}{grp}[{pn}|{ba}|{ca}]\n'
    
    dept = str()  
    if access != 'Group':  
        for r in range(len(dd)):
            dpt = str(dd.loc[r,'Dept'])   + ' '*(5-len(str(dd.loc[r,'Dept'])))
            pn  = ' '*(3-len(str(dd.loc[r,'pNew']))) + str(dd.loc[r,'pNew'])
            ba  = ' '*(3-len(str(dd.loc[r,'bbA'])))  + str(dd.loc[r,'bbA'])
            ca  = ' '*(3-len(str(dd.loc[r,'cctA']))) + str(dd.loc[r,'cctA'])
            dept = f'{dept}{dpt}[{pn}|{ba}|{ca}]\n'
            
    if d == '__':
        pn = ' '*(3-len(str(dy.loc[0,'pNew']))) + str(dy.loc[0,'pNew'])
        ba = ' '*(3-len(str(dy.loc[0,'bbA'])))  + str(dy.loc[0,'bbA'])
        ca = ' '*(3-len(str(dy.loc[0,'cctA']))) + str(dy.loc[0,'cctA'])
        youth = f'\nTot  [{pn}|{ba}|{ca}]\n'

    else:
        youth = str()
    
    result = f"""<b><u>{grpdept} {bbttype} Active BB Status </u></b>\n\n<pre>Grp  [ NP| AB| CA]\n{member}\n{group}\n{dept}{youth}</pre>"""
    result = re.sub(r'\.0',r'  ',result) # Replaces '.0' with empty space
    result = re.sub(r'(\D)0([^.])',r'\1-\2',result)   # Replaces lone '0' with '-'
    return result









def deptbbtactive(q, d, r, access):
        
    name = 'BBT' if access == 'IT' else 'BBTCode'
    d = d.capitalize()
    
    i = q if q in ['bbt','gyjnbbt'] else 'btm'
    
    bbtvalues = {'bbt'     : ['BBT',   ""],
                 'gyjnbbt' : ['GYJN BBT',  " AND t.Title = 'GYJN'"],
                 'btm'     : [q.upper(), f" AND BtmNo = '{q[3:]}'"]}
    bbttype,query = bbtvalues[i]
    
    conn = odbc.connect(conn_str)
    bb_dept = f"SELECT Dept, SUM(pNew)pNew, SUM(pOld)pOld, SUM(bbA)bbA, SUM(cctA)cctA, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA, SUM(Total)Total FROM CodeyBBTStatusMembers('{r}') WHERE Dept LIKE '{d}'{query} Group BY Dept"
    bb_youth = f"SELECT SUM(pNew)pNew, SUM(pOld)pOld, SUM(bbA)bbA, SUM(cctA)cctA, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA, SUM(Total)Total FROM CodeyBBTStatusMembers('{r}') WHERE Dept LIKE '{d}'{query}"
    
    dd = pd.read_sql(bb_dept, conn)
    dy = pd.read_sql(bb_youth, conn)

    dd.columns = ['Dept','pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
    dy.columns = ['pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
    dd.replace(r' Dept',r'', regex = True, inplace = True)
    
    conn.cursor().close()
    
    dept = str()    
    for r in range(len(dd)):
        dpt = str(dd.loc[r,'Dept'])   + ' '*(4-len(str(dd.loc[r,'Dept'])))
        pn  = ' '*(3-len(str(dd.loc[r,'pNew']))) + str(dd.loc[r,'pNew'])
        ba  = ' '*(3-len(str(dd.loc[r,'bbA'])))  + str(dd.loc[r,'bbA'])
        ca  = ' '*(3-len(str(dd.loc[r,'cctA']))) + str(dd.loc[r,'cctA'])
        dept = f'{dept}{dpt}[{pn}|{ba}|{ca}]\n'
            
    if d == '__':
        pn = ' '*(3-len(str(dy.loc[0,'pNew']))) + str(dy.loc[0,'pNew'])
        ba = ' '*(3-len(str(dy.loc[0,'bbA'])))  + str(dy.loc[0,'bbA'])
        ca = ' '*(3-len(str(dy.loc[0,'cctA']))) + str(dy.loc[0,'cctA'])
        youth = f'\nTot [{pn}|{ba}|{ca}]\n'

    else:
        youth = str()
    
    result = f"""<b><u>{str(d).replace('__','Youth')} {bbttype} Active BB Status </u></b>\n\n<pre>Grp [ NP| AB| CA]\n\n{dept}{youth}</pre>"""
    result = re.sub(r'\.0',r'  ',result) # Replaces '.0' with empty space
    result = re.sub(r'(\D)0([^.])',r'\1-\2',result)   # Replaces lone '0' with '-'
    return result









def bbtinactive(q, g, d, r, access):
    
    name = 'BBT' if access == 'IT' else 'BBTCode2'
    g = g if access == 'Group' else '%'
    d = d.capitalize()
    grpdept = re.sub(r'^(\d)',r'G\1',g).capitalize() if access == 'Group' else str(d).replace('__','Youth')
    
    i = q if q in ['bbt','gyjnbbt'] else 'btm'
    bbtvalues = {'bbt'     : ['BBT',   ""],
                 'gyjnbbt' : ['GYJN BBT',  " AND t.Title = 'GYJN'"],
                 'btm'     : [q.upper(), f" AND BtmNo = '{q[3:]}'"]}
    bbttype,query = bbtvalues[i]
    
    conn = odbc.connect(conn_str)
    bb_mem = f"SELECT Dept, Grp, {name}, pNew, pOld, bbA, cctA, bbME, cctI, pFA, bbFA, Total FROM CodeyBBTStatusMembers('{r}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}'{query} ORDER BY LEN(Grp), Grp, {name}"
    bb_group = f"SELECT Grp, SUM(pNew)pNew, SUM(pOld)pOld, SUM(bbA)bbA, SUM(cctA)cctA, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA, SUM(Total)Total FROM CodeyBBTStatusMembers('{r}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}'{query} Group BY Grp ORDER BY LEN(Grp), Grp"
    bb_dept = f"SELECT Dept, SUM(pNew)pNew, SUM(pOld)pOld, SUM(bbA)bbA, SUM(cctA)cctA, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA, SUM(Total)Total FROM CodeyBBTStatusMembers('{r}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}'{query} Group BY Dept"
    bb_youth = f"SELECT SUM(pNew)pNew, SUM(pOld)pOld, SUM(bbA)bbA, SUM(cctA)cctA, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA, SUM(Total)Total FROM CodeyBBTStatusMembers('{r}') WHERE Dept LIKE '{d}' AND Grp LIKE '{g}'{query}"
    
    dm = pd.read_sql(bb_mem, conn)
    dg = pd.read_sql(bb_group, conn)
    dd = pd.read_sql(bb_dept, conn)
    dy = pd.read_sql(bb_youth, conn)

    dm.columns = ['Dept','Grp','BBT','pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
    dg.columns = ['Grp','pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
    dd.columns = ['Dept','pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
    dy.columns = ['pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
    dm['Grp'] = dm['Grp'].str.replace(r'^(\d)', r'G\1')
    dg['Grp'] = dg['Grp'].str.replace(r'^(\d)', r'G\1')
    dd.replace(r' Dept',r'', regex = True, inplace = True)
    
    conn.cursor().close()

    member = str()
    if d != '__':
        member = '\n'
        for r in range(len(dm)):
            bbt =   str(dm.loc[r,'BBT'][:5]) + ' '*(5-len(str(dm.loc[r,'BBT'][:5])))
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
    if access != 'Group':    
        for r in range(len(dd)):
            dpt = str(dd.loc[r,'Dept'])   + ' '*(5-len(str(dd.loc[r,'Dept'])))
            po  = ' '*(3-len(str(dd.loc[r,'pOld']))) + str(dd.loc[r,'pOld'])
            bm  = ' '*(3-len(str(dd.loc[r,'bbME']))) + str(dd.loc[r,'bbME'])
            ci  = ' '*(3-len(str(dd.loc[r,'cctI']))) + str(dd.loc[r,'cctI'])
            pf  = ' '*(3-len(str(dd.loc[r,'pFA'])))  + str(dd.loc[r,'pFA'])
            bf  = ' '*(3-len(str(dd.loc[r,'bbFA']))) + str(dd.loc[r,'bbFA'])
            dept = f'{dept}{dpt}[{po}|{bm}|{ci}|{pf}|{bf}]\n'
            
    if d == '__':
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
    return result








def deptbbtinactive(q, d, r, access):
    
    name = 'BBT' if access == 'IT' else 'BBTCode'
    d = d.capitalize()
    
    i = q if q in ['bbt','gyjnbbt'] else 'btm'
    bbtvalues = {'bbt'     : ['BBT',   ""],
                 'gyjnbbt' : ['GYJN BBT',  " AND t.Title = 'GYJN'"],
                 'btm'     : [q.upper(), f" AND BtmNo = '{q[3:]}'"]}
    bbttype,query = bbtvalues[i]
    
    conn = odbc.connect(conn_str)
    bb_dept = f"SELECT Dept, SUM(pNew)pNew, SUM(pOld)pOld, SUM(bbA)bbA, SUM(cctA)cctA, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA, SUM(Total)Total FROM CodeyBBTStatusMembers('{r}') WHERE Dept LIKE '{d}'{query} Group BY Dept"
    bb_youth = f"SELECT SUM(pNew)pNew, SUM(pOld)pOld, SUM(bbA)bbA, SUM(cctA)cctA, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA, SUM(Total)Total FROM CodeyBBTStatusMembers('{r}') WHERE Dept LIKE '{d}'{query}"
    
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
            
    if d == '__':
        bm = ' '*(3-len(str(dy.loc[0,'bbME']))) + str(dy.loc[0,'bbME'])
        po = ' '*(3-len(str(dy.loc[0,'pOld']))) + str(dy.loc[0,'pOld'])
        ci = ' '*(3-len(str(dy.loc[0,'cctI']))) + str(dy.loc[0,'cctI'])
        pf = ' '*(3-len(str(dy.loc[0,'pFA'])))  + str(dy.loc[0,'pFA'])
        bf = ' '*(3-len(str(dy.loc[0,'bbFA']))) + str(dy.loc[0,'bbFA']) 
        youth = f'\nTot [{po}|{bm}|{ci}|{pf}|{bf}]\n'

    else:
        youth = str()
    
    result = f"""<b><u>{str(d).replace('__','Youth')} {bbttype} Inactive BB Status </u></b>\n\n<pre>Grp [ OP| ME| CI| FP| FA]\n\n{dept}{youth}</pre>"""
    result = re.sub(r'\.0',r'  ',result) # Replaces '.0' with empty space
    result = re.sub(r'(\D)0([^.])',r'\1-\2',result)   # Replaces lone '0' with '-'
    return result





def bblist(d,g,r,access):
    d = d.capitalize()
    g = '%' if access != 'Group' else g
    gd = re.sub(r'^(\d)',r'G\1',g).capitalize() if access == 'Group' else str(d).replace('__','Youth')
    
    query = f"FROM CodeyBBList('{r}') c LEFT JOIN TaskHigh t ON t.UID = c.BBTID WHERE (L1G LIKE '{g}' OR L2G LIKE '{g}') AND (L1D LIKE '{d}' OR L2D LIKE '{d}')"
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
        
    if access == 'Group':
        pts = [dNP['Points'].sum(), dOP['Points'].sum(), dAB['Points'].sum(), dIM['Points'].sum(), dIF['Points'].sum(), dFP['Points'].sum(), dAC['Points'].sum(), dIC['Points'].sum()]
        pt = 'Points'
    elif d != '__':
        pts = [dNP['DPoints'].sum(), dOP['DPoints'].sum(), dAB['DPoints'].sum(), dIM['DPoints'].sum(), dIF['DPoints'].sum(), dFP['DPoints'].sum(), dAC['DPoints'].sum(), dIC['DPoints'].sum()]
        pt = 'DPoints'
    else:
        pts = [len(dNP),len(dOP),len(dAB),len(dIM),len(dIF),len(dFP),len(dAC),len(dIC)]
        
    if len(dNP) == 0:
        np = ''
    else:
        np = f"<i><b><u>New Picking ({pts[0]} Pt)</u></b></i>\n<pre>"
        for r in range(len(dNP)):
            np = f"{np}💛{r+1}. [{dNP.loc[r,'LastClass']}] [{dNP.loc[r,pt] if d != '__' else '1'}] {dNP.loc[r,'FruitName'][:8]} - {dNP.loc[r,'L1N']}{dNP.loc[r,'L2N']} - {(dNP.loc[r,'BBTN'])}\n"
        np = np + '</pre>\n'
        
    if len(dOP) == 0:
        op = ''
    else:
        op = f"<i><b><u>Old Picking ({pts[1]} Pt)</u></b></i>\n<pre>"
        for r in range(len(dOP)):
            op = f"{op}⛔️{r+1}. [{dOP.loc[r,'LastClass']}] [{dOP.loc[r,pt] if d != '__' else '1'}] {dOP.loc[r,'FruitName'][:8]} - {dOP.loc[r,'L1N']}{dOP.loc[r,'L2N']} - {(dOP.loc[r,'BBTN'])}\n"
        op = op + '</pre>\n'
    
    if len(dAB) == 0:
        ab = ''
    else:
        ab = f"<i><b><u>Active BB ({pts[2]} Pt)</u></b></i>\n<pre>"
        for r in range(len(dAB)):
            ab = f"{ab}🟢{r+1}. [{dAB.loc[r,'LastClass']}] [{dAB.loc[r,pt] if d != '__' else '1'}] {dAB.loc[r,'FruitName'][:8]} - {dAB.loc[r,'L1N']}{dAB.loc[r,'L2N']} - {(dAB.loc[r,'BBTN'])} - {(dAB.loc[r,'LastTopic'])} → [{(dAB.loc[r,'NextClassDate'])}]\n"
        ab = ab + '</pre>\n'
        
    if len(dIM) == 0:
        im = ''
    else:
        im = f"<i><b><u>IBB Missed Education ({pts[3]} Pt)</u></b></i>\n<pre>"
        for r in range(len(dIM)):
            im = f"{im}🔴{r+1}. [{dIM.loc[r,'LastClass']}] [{dIM.loc[r,pt] if d != '__' else '1'}] {dIM.loc[r,'FruitName'][:8]} - {dIM.loc[r,'L1N']}{dIM.loc[r,'L2N']} - {(dIM.loc[r,'BBTN'])} - {(dIM.loc[r,'LastTopic'])} → [{(dIM.loc[r,'NextClassDate'])}]\n"
        im = im + '</pre>\n'
        
    if len(dIF) == 0:
        fa = ''
    else:
        fa = f"<i><b><u>IBB Fallen ({pts[4]} Pt)</u></b></i>\n<pre>"
        for r in range(len(dIF)):
            fa = f"{fa}⚫️{r+1}. [{dIF.loc[r,'LastClass']}] [{dIF.loc[r,pt] if d != '__' else '1'}] {dIF.loc[r,'FruitName'][:8]} - {dIF.loc[r,'L1N']}{dIF.loc[r,'L2N']} - {(dIF.loc[r,'BBTN'])} - {(dIF.loc[r,'LastTopic'])} → [{(dIF.loc[r,'NextClassDate'])}]\n"
        fa = fa + '</pre>\n'
        
    if len(dFP) == 0:
        fp = ''
    else:
        fp = f"<i><b><u>Fallen Picking ({pts[5]} Pt)</u></b></i>\n<pre>"
        for r in range(len(dFP)):
            fp = f"{fp}❌{r+1}. [{dFP.loc[r,'LastClass']}] [{dFP.loc[r,pt] if d != '__' else '1'}] {dFP.loc[r,'FruitName'][:8]} - {dFP.loc[r,'L1N']}{dFP.loc[r,'L2N']} - {(dFP.loc[r,'BBTN'])}\n"
        fp = fp + '</pre>\n'
        
    if len(dAC) == 0:
        ac = ''
    else:
        ac = f"<i><b><u>CCT ABB ({pts[6]} Pt)</u></b></i>\n<pre>"
        for r in range(len(dAC)):
            ac = f"{ac}⭐️{r+1}. [{dAC.loc[r,'LastClass']}] [{dAC.loc[r,pt] if d != '__' else '1'}] {dAC.loc[r,'FruitName'][:8]} - {dAC.loc[r,'L1N']}{dAC.loc[r,'L2N']} - {(dAC.loc[r,'BBTN'])} - {(dAC.loc[r,'LastTopic'])} → [{(dAC.loc[r,'NextClassDate'])}]\n"
        ac = ac + '</pre>\n'
        
    if len(dIC) == 0:
        ic = ''
    else:
        ic = f"<i><b><u>CCT IBB ({pts[7]} Pt)</u></b></i>\n<pre>"
        for r in range(len(dIC)):
            ic = f"{ic}⭐️{r+1}. [{dIC.loc[r,'LastClass']}] [{dIC.loc[r,pt] if d != '__' else '1'}] {dIC.loc[r,'FruitName'][:8]} - {dIC.loc[r,'L1N']}{dIC.loc[r,'L2N']} - {(dIC.loc[r,'BBTN'])} - {(dIC.loc[r,'LastTopic'])} → [{(dIC.loc[r,'NextClassDate'])}]\n"
        ic = ic + '</pre>\n'
    
    result = f"<b><u>📚{gd} BB Fruit List📚</u></b>\n\n<i>▫️Status▫️\n#. [LastClassDate] [Pts] - Fruit - L1 / L2 - BBT - LastTopic → [NextClassDate]</i>\n\n{np}{op}{ab}{im}{fa}{fp}{ac}{ic}<b><i><u>Total: {sum(pts)} Pts</u></i></b>"
    result = re.sub(r'\.0',r'',result)
    result = re.sub(r' \(\)',r'',result)
    result = re.sub(r'\((\d+)\)', r'(G\1)', result)
    result = re.sub(r'\[1\] ', r'', result)
    return result










def bbtlist(q,d,g,r,access):
    d = d.capitalize()
    i = q if q in ['bbt','gyjnbbt'] else 'btm'
    bbtvalues = {'bbt'     : ['BBT',   ""],
                 'gyjnbbt' : ['GYJN BBT',  " AND t.Title = 'GYJN'"],
                 'btm'     : [q.upper(), f" AND BtmNo = '{q[3:]}'"]}
    g = '%' if access != 'Group' else g
    gd = re.sub(r'^(\d)',r'G\1',g).capitalize() if access == 'Group' else str(d).replace('__','Youth')
    bbttype,query = bbtvalues[i]
    
    conn = odbc.connect(conn_str)   

    dNP = pd.read_sql(f"SELECT LastClass, BBTN, FruitName, L1N, L2N, LastTopic, NextClassDate FROM CodeyBBList('{r}') c LEFT JOIN TaskHigh t ON t.UID = c.BBTID WHERE NewStatus = 'New P'    AND BBTG LIKE '{g}' AND BBTD LIKE '{d}'{query} ORDER BY BBTN", conn)
    dOP = pd.read_sql(f"SELECT LastClass, BBTN, FruitName, L1N, L2N, LastTopic, NextClassDate FROM CodeyBBList('{r}') c LEFT JOIN TaskHigh t ON t.UID = c.BBTID WHERE NewStatus = 'Old P'    AND BBTG LIKE '{g}' AND BBTD LIKE '{d}'{query} ORDER BY BBTN", conn)
    dAB = pd.read_sql(f"SELECT LastClass, BBTN, FruitName, L1N, L2N, LastTopic, NextClassDate FROM CodeyBBList('{r}') c LEFT JOIN TaskHigh t ON t.UID = c.BBTID WHERE NewStatus = 'ABB'      AND BBTG LIKE '{g}' AND BBTD LIKE '{d}'{query} ORDER BY BBTN", conn)
    dIM = pd.read_sql(f"SELECT LastClass, BBTN, FruitName, L1N, L2N, LastTopic, NextClassDate FROM CodeyBBList('{r}') c LEFT JOIN TaskHigh t ON t.UID = c.BBTID WHERE NewStatus = 'IBB ME'   AND BBTG LIKE '{g}' AND BBTD LIKE '{d}'{query} ORDER BY BBTN", conn)
    dIF = pd.read_sql(f"SELECT LastClass, BBTN, FruitName, L1N, L2N, LastTopic, NextClassDate FROM CodeyBBList('{r}') c LEFT JOIN TaskHigh t ON t.UID = c.BBTID WHERE NewStatus = 'IBB FA'   AND BBTG LIKE '{g}' AND BBTD LIKE '{d}'{query} ORDER BY BBTN", conn)
    dFP = pd.read_sql(f"SELECT LastClass, BBTN, FruitName, L1N, L2N, LastTopic, NextClassDate FROM CodeyBBList('{r}') c LEFT JOIN TaskHigh t ON t.UID = c.BBTID WHERE NewStatus = 'Fallen P' AND BBTG LIKE '{g}' AND BBTD LIKE '{d}'{query} ORDER BY BBTN", conn)
    dAC = pd.read_sql(f"SELECT LastClass, BBTN, FruitName, L1N, L2N, LastTopic, NextClassDate FROM CodeyBBList('{r}') c LEFT JOIN TaskHigh t ON t.UID = c.BBTID WHERE NewStatus = 'ABB CCT'  AND BBTG LIKE '{g}' AND BBTD LIKE '{d}'{query} ORDER BY BBTN", conn)
    dIC = pd.read_sql(f"SELECT LastClass, BBTN, FruitName, L1N, L2N, LastTopic, NextClassDate FROM CodeyBBList('{r}') c LEFT JOIN TaskHigh t ON t.UID = c.BBTID WHERE NewStatus = 'IBB CCT'  AND BBTG LIKE '{g}' AND BBTD LIKE '{d}'{query} ORDER BY BBTN", conn)
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
    
    result = f"<b><u>📖{gd} {bbttype} Student List📖</u></b>\n\n<i>▫️Status▫️\n#. [LastClassDate] BBT - Student - Leaf1 / Leaf2 - LastTopic → [NextClassDate]</i>\n\n{np}{op}{ab}{im}{fa}{fp}{ac}{ic}<b><i><u>Total: {sum([len(dNP),len(dOP),len(dAB),len(dIM),len(dIF),len(dFP),len(dAC),len(dIC)])} Pts</u></i></b>"
    result = re.sub(r'\.0',r'',result)
    result = re.sub(r' \(\)',r'',result)
    result = re.sub(r'\((\d+)\)', r'(G\1)', result)
    return result




def bbtlistold(q,d):
    d = d.capitalize()
    i = q if q in ['bbt','gyjnbbt'] else 'btm'
    bbtvalues = {'bbt'     : ['BBT',   " AND BbtStatus = 'Active'"],
                 'gyjnbbt' : ['GYJN BBT',  " AND t.Title = 'GYJN'"],
                 'btm'     : [q.upper(), f" AND BtmNo = '{q[3:]}'"]}
    bbttype,query = bbtvalues[i]
    
    conn = odbc.connect(conn_str)   

    dNP = pd.read_sql(f"SELECT s.* FROM ScottBBList('%','New P')    s LEFT JOIN TaskHigh t ON t.UID = s.BBTID WHERE BBTD LIKE '{d}'{query} ORDER BY BBTN", conn)
    dOP = pd.read_sql(f"SELECT s.* FROM ScottBBList('%','Old P')    s LEFT JOIN TaskHigh t ON t.UID = s.BBTID WHERE BBTD LIKE '{d}'{query} ORDER BY BBTN", conn)
    dAB = pd.read_sql(f"SELECT s.* FROM ScottBBList('%','ABB')      s LEFT JOIN TaskHigh t ON t.UID = s.BBTID WHERE BBTD LIKE '{d}'{query} ORDER BY BBTN", conn)
    dIM = pd.read_sql(f"SELECT s.* FROM ScottBBList('%','IBB ME')   s LEFT JOIN TaskHigh t ON t.UID = s.BBTID WHERE BBTD LIKE '{d}'{query} ORDER BY BBTN", conn)
    dIF = pd.read_sql(f"SELECT s.* FROM ScottBBList('%','IBB FA')   s LEFT JOIN TaskHigh t ON t.UID = s.BBTID WHERE BBTD LIKE '{d}'{query} ORDER BY BBTN", conn)
    dFP = pd.read_sql(f"SELECT s.* FROM ScottBBList('%','Fallen P') s LEFT JOIN TaskHigh t ON t.UID = s.BBTID WHERE BBTD LIKE '{d}'{query} ORDER BY BBTN", conn)
    dAC = pd.read_sql(f"SELECT s.* FROM ScottBBList('%','ABB CCT')  s LEFT JOIN TaskHigh t ON t.UID = s.BBTID WHERE BBTD LIKE '{d}'{query} ORDER BY BBTN", conn)
    dIC = pd.read_sql(f"SELECT s.* FROM ScottBBList('%','IBB CCT')  s LEFT JOIN TaskHigh t ON t.UID = s.BBTID WHERE BBTD LIKE '{d}'{query} ORDER BY BBTN", conn)
    dNP.columns = ['FruitName','L1N','L1G','L1P','L2P','L2N','L2G','BBTN','BBTG','BBTD','BbtStatus','BtmNo','NewStatus','Points','UID','BBTID']
    dOP.columns = ['FruitName','L1N','L1G','L1P','L2P','L2N','L2G','BBTN','BBTG','BBTD','BbtStatus','BtmNo','NewStatus','Points','UID','BBTID']
    dAB.columns = ['FruitName','L1N','L1G','L1P','L2P','L2N','L2G','BBTN','BBTG','BBTD','BbtStatus','BtmNo','NewStatus','Points','UID','BBTID']
    dIM.columns = ['FruitName','L1N','L1G','L1P','L2P','L2N','L2G','BBTN','BBTG','BBTD','BbtStatus','BtmNo','NewStatus','Points','UID','BBTID']
    dIF.columns = ['FruitName','L1N','L1G','L1P','L2P','L2N','L2G','BBTN','BBTG','BBTD','BbtStatus','BtmNo','NewStatus','Points','UID','BBTID']
    dFP.columns = ['FruitName','L1N','L1G','L1P','L2P','L2N','L2G','BBTN','BBTG','BBTD','BbtStatus','BtmNo','NewStatus','Points','UID','BBTID']
    dAC.columns = ['FruitName','L1N','L1G','L1P','L2P','L2N','L2G','BBTN','BBTG','BBTD','BbtStatus','BtmNo','NewStatus','Points','UID','BBTID']
    dIC.columns = ['FruitName','L1N','L1G','L1P','L2P','L2N','L2G','BBTN','BBTG','BBTD','BbtStatus','BtmNo','NewStatus','Points','UID','BBTID']
    conn.cursor().close()
    if len(dNP) == 0:
        np = ''
    else:
        np = f"<i><b><u>New Picking ({len(dNP)} Pt)</u></b></i>\n<pre>"
        for r in range(len(dNP)):
            np = f"{np}💛{r+1}. {(dNP.loc[r,'BBTN'])[:8]} - {dNP.loc[r,'FruitName'][:8]} - {dNP.loc[r,'L1N'][:8]}{dNP.loc[r,'L2N'][:11]} ({dNP.loc[r,'L2G']})\n"
        np = np + '</pre>\n'
        
    if len(dOP) == 0:
        op = ''
    else:
        op = f"<i><b><u>Old Picking ({len(dOP)} Pt)</u></b></i>\n<pre>"
        for r in range(len(dOP)):
            op = f"{op}⛔️{r+1}. {(dOP.loc[r,'BBTN'])[:8]} - {dOP.loc[r,'FruitName'][:8]} - {dOP.loc[r,'L1N'][:8]}{dNP.loc[r,'L2N'][:11]} ({dOP.loc[r,'L2G']})\n"
        op = op + '</pre>\n'
    
    if len(dAB) == 0:
        ab = ''
    else:
        ab = f"<i><b><u>Active BB ({len(dAB)} Pt)</u></b></i>\n<pre>"
        for r in range(len(dAB)):
            ab = f"{ab}🟢{r+1}. {(dAB.loc[r,'BBTN'])[:8]} - {dAB.loc[r,'FruitName'][:8]} - {dAB.loc[r,'L1N'][:8]}{dAB.loc[r,'L2N'][:11]} ({dAB.loc[r,'L2G']})\n"
        ab = ab + '</pre>\n'
        
    if len(dIM) == 0:
        im = ''
    else:
        im = f"<i><b><u>IBB Missed Education ({len(dIM)} Pt)</u></b></i>\n<pre>"
        for r in range(len(dIM)):
            im = f"{im}🔴{r+1}. {(dIM.loc[r,'BBTN'])[:8]} - {dIM.loc[r,'FruitName'][:8]} - {dIM.loc[r,'L1N'][:8]}{dIM.loc[r,'L2N'][:11]} ({dIM.loc[r,'L2G']})\n"
        im = im + '</pre>\n'
        
    if len(dIF) == 0:
        fa = ''
    else:
        fa = f"<i><b><u>IBB Fallen ({len(dIF)} Pt)</u></b></i>\n<pre>"
        for r in range(len(dIF)):
            fa = f"{fa}⚫️{r+1}. {(dIF.loc[r,'BBTN'])[:8]} - {dIF.loc[r,'FruitName'][:8]} - {dIF.loc[r,'L1N'][:8]}{dIF.loc[r,'L2N'][:11]} ({dIF.loc[r,'L2G']})\n"
        fa = fa + '</pre>\n'
        
    if len(dFP) == 0:
        fp = ''
    else:
        fp = f"<i><b><u>Fallen Picking ({len(dFP)} Pt)</u></b></i>\n<pre>"
        for r in range(len(dFP)):
            fp = f"{fp}❌{r+1}. {(dFP.loc[r,'BBTN'])[:8]} - {dFP.loc[r,'FruitName'][:8]} - {dFP.loc[r,'L1N'][:8]}{dFP.loc[r,'L2N'][:11]} ({dFP.loc[r,'L2G']})\n"
        fp = fp + '</pre>\n'
        
    if len(dAC) == 0:
        ac = ''
    else:
        ac = f"<i><b><u>CCT ABB ({len(dAC)} Pt)</u></b></i>\n<pre>"
        for r in range(len(dAC)):
            ac = f"{ac}⭐️{r+1}. {(dAC.loc[r,'BBTN'])[:8]} - {dAC.loc[r,'FruitName'][:8]} - {dAC.loc[r,'L1N'][:8]}{dAC.loc[r,'L2N'][:11]} ({dAC.loc[r,'L2G']})\n"
        ac = ac + '</pre>\n'
        
    if len(dIC) == 0:
        ic = ''
    else:
        ic = f"<i><b><u>CCT IBB ({len(dIC)} Pt)</u></b></i>\n<pre>"
        for r in range(len(dIC)):
            ic = f"{ic}⭐️{r+1}. {(dIC.loc[r,'BBTN'])[:8]} - {dIC.loc[r,'FruitName'][:8]} - {dIC.loc[r,'L1N'][:8]}{dIC.loc[r,'L2N'][:11]} ({dIC.loc[r,'L2G']})\n"
        ic = ic + '</pre>\n'
    
    result = f"<b><u>📖{str(d).replace('__','Youth')} {bbttype} Student List📖</u></b>\n\n<i>▫️Status▫️\n#. BBT - Fruit - Leaf1 / Leaf2</i>\n\n{np}{op}{ab}{im}{fa}{fp}{ac}{ic}"
    result = re.sub(r'\.0',r'',result)
    result = re.sub(r' \(\)',r'',result)
    result = re.sub(r'\((\d+)\)', r'(G\1)', result)
    return result





def bbpick(g):
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
           
    if len(dn) == 0:
        new = ''
    else: 
        new = f"<i><b><u>New Picking ({dPts.loc['New','Pts']} pt)</u></b></i>\n"
        for r in range(len(dn)):
            new = f"{new}<pre>🟡{r+1}. [{dn.loc[r,'Points']}] {dn.loc[r,'FruitName'][:8]} - {dn.loc[r,'L1N'][:8]} ({dn.loc[r,'L1G']}){dn.loc[r,'L2N'][:11]} ({dn.loc[r,'L2G']}) - {(dn.loc[r,'BBTN'])[:8]} ({dn.loc[r,'BBTG']}) [{dn.loc[r,'P_Date']}]</pre>\n"
        new = new + '\n'
        
    if len(do) == 0:
        old = ''
    else: 
        old = f"<i><b><u>Old Picking ({dPts.loc['Old','Pts']} pt)</u></b></i>\n"
        for r in range(len(do)):
            old = f"{old}<pre>⚪️{r+1}. [{do.loc[r,'Points']}] {do.loc[r,'FruitName'][:8]} - {do.loc[r,'L1N'][:8]} ({do.loc[r,'L1G']}){do.loc[r,'L2N'][:11]} ({do.loc[r,'L2G']}) - {(do.loc[r,'BBTN'])[:8]} ({do.loc[r,'BBTG']}) [{do.loc[r,'P_Date']}]</pre>\n"
        old = old + '\n'
    
    if len(df) == 0:
        fallen = ''
    else: 
        fallen = f"<i><b><u>Fallen Picking ({dPts.loc['Fallen','Pts']} pt)</u></b></i>\n"
        for r in range(len(df)):
            fallen = f"{fallen}<pre>⚫️{r+1}. [{df.loc[r,'Points']}] {df.loc[r,'FruitName'][:8]} - {df.loc[r,'L1N'][:8]} ({df.loc[r,'L1G']}){df.loc[r,'L2N'][:11]} ({df.loc[r,'L2G']}) - {(df.loc[r,'BBTN'])[:8]} ({df.loc[r,'BBTG']}) [{df.loc[r,'P_Date']}]</pre>\n"
        fallen = fallen + '\n' 
    
    g = re.sub(r'^(\d)', r'G\1', g)
    result = f"<b><u>📙{g} Picking Status📙</u></b>\n\n<i>▫️Status▫️\n#. Fruit - Leaf1 / Leaf2 - BBT [Picking Date]</i>\n\n{new}{old}{fallen}"
    result = re.sub(r'\.0',r'',result)
    result = re.sub(r' \(\)',r'',result)
    result = re.sub(r'\((\d+)\)', r'(G\1)', result)
    result = re.sub(r'\[1\] ', r'', result)
    return result


def bbfe(g):
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
        
    g = re.sub(r'^(\d)', r'G\1', g)
    result = f"<b><u>📘{g} FE Status📘</u></b>\n\n<i>▫️Status▫️\n#. Fruit - Leaf1 / Leaf2 - BBT [FE Date]</i>\n\n{schd}{fe}{cncl}{fallen}"
    result = re.sub(r'\.0',r'',result)
    result = re.sub(r' \(\)',r'',result)
    result = re.sub(r'\((\d+)\)', r'(G\1)', result)
    result = re.sub(r'\[1\] ', r'', result)
    return result


# REPLACE "*" WITH ACTUAL COLUMN NAMES SO CAN ADD MORE COLUMNS

def bbstatus(g):
    return 'Function not available. Please use bblist for list of students'







def newbbstatus(g):
    conn = odbc.connect(conn_str)
    
    df = pd.read_sql(f"SELECT * FROM ScottNewStatus('{g}')", conn)
    df.columns = ['UID','FruitName','L1N','L1G','L2N','L2G','BBTN','BBTG','NewStatus','LastClassDate','LastTopic','NextClassDate','Points']
    
    dNP = df[df['NewStatus'] == 'NewP']
    dOP = df[df['NewStatus'] == 'Old P']
    dAB = df[df['NewStatus'] == 'ABB']
    dIM = df[df['NewStatus'] == 'IBB ME']
    dIF = df[df['NewStatus'] == 'IBB FA']
    dFP = df[df['NewStatus'] == 'Fallen P']
    dAC = df[df['NewStatus'] == 'ABB CCT']
    dIC = df[df['NewStatus'] == 'IBB CCT']
    
    dPts = pd.read_sql(f"SELECT NewStatus, SUM(Points)Pts FROM ScottNewStatus('{g}') GROUP BY NewStatus", conn)
    dPts.columns =  ['NewStatus','Pts']
    dPts.set_index('NewStatus', inplace=True)
    
    npP,opP,abP,imP,ifP,fpP,acP,icP, = 0,0,0,0,0,0,0,0
    conn.cursor().close()
               
    if len(dNP) == 0:
        np = ''
    else:
        npP = dPts.loc['New P','Pts']
        np = f"<i><b><u>New Picking ({npP} pt)</u></b></i>\n"
        for r in range(len(dNP)):
            np = f"{np}<pre>💛{r+1}. [{dNP.loc[r,'LastClassDate']}] [{dNP.loc[r,'Points']}] {dNP.loc[r,'FruitName'][:8]} - {dNP.loc[r,'L1N'][:8]} ({dNP.loc[r,'L1G']}){dNP.loc[r,'L2N'][:11]} ({dNP.loc[r,'L2G']}) - {(dNP.loc[r,'BBTN'])[:8]} ({dNP.loc[r,'BBTG']}) - {(dNP.loc[r,'LastTopic'])} → [{(dNP.loc[r,'NextClassDate'])}]</pre>\n"
        np = np + '\n'
        
    if len(dOP) == 0:
        op = ''
    else:
        opP = dPts.loc['Old P','Pts']
        op = f"<i><b><u>Old Picking ({opP} pt)</u></b></i>\n"
        for r in range(len(dOP)):
            op = f"{op}<pre>⛔️{r+1}. [{dOP.loc[r,'LastClassDate']}] [{dOP.loc[r,'Points']}] {dOP.loc[r,'FruitName'][:8]} - {dOP.loc[r,'L1N'][:8]} ({dOP.loc[r,'L1G']}){dOP.loc[r,'L2N'][:11]} ({dOP.loc[r,'L2G']}) - {(dOP.loc[r,'BBTN'])[:8]} ({dOP.loc[r,'BBTG']}) - {(dOP.loc[r,'LastTopic'])} → [{(dOP.loc[r,'NextClassDate'])}]</pre>\n"
        op = op + '\n'
    
    if len(dAB) == 0:
        ab = ''
    else:
        abP = dPts.loc['ABB','Pts']
        ab = f"<i><b><u>Active BB ({abP} pt)</u></b></i>\n"
        for r in range(len(dAB)):
            ab = f"{ab}<pre>🟢{r+1}. [{dAB.loc[r,'LastClassDate']}] [{dAB.loc[r,'Points']}] {dAB.loc[r,'FruitName'][:8]} - {dAB.loc[r,'L1N'][:8]} ({dAB.loc[r,'L1G']}){dAB.loc[r,'L2N'][:11]} ({dAB.loc[r,'L2G']}) - {(dAB.loc[r,'BBTN'])[:8]} ({dAB.loc[r,'BBTG']}) - {(dAB.loc[r,'LastTopic'])} → [{(dAB.loc[r,'NextClassDate'])}]</pre>\n"
        ab = ab + '\n'
        
    if len(dIM) == 0:
        im = ''
    else:
        imP = dPts.loc['IBB ME','Pts']
        im = f"<i><b><u>IBB Missed Education ({imP} pt)</u></b></i>\n"
        for r in range(len(dIM)):
            im = f"{im}<pre>🔴{r+1}. [{dIM.loc[r,'LastClassDate']}] [{dIM.loc[r,'Points']}] {dIM.loc[r,'FruitName'][:8]} - {dIM.loc[r,'L1N'][:8]} ({dIM.loc[r,'L1G']}){dIM.loc[r,'L2N'][:11]} ({dIM.loc[r,'L2G']}) - {(dIM.loc[r,'BBTN'])[:8]} ({dIM.loc[r,'BBTG']}) - {(dIM.loc[r,'LastTopic'])} → [{(dIM.loc[r,'NextClassDate'])}]</pre>\n"
        im = im + '\n'
        
    if len(dIF) == 0:
        fa = ''
    else:
        ifP = dPts.loc['IBB FA','Pts']
        fa = f"<i><b><u>IBB Fallen ({ifP} pt)</u></b></i>\n"
        for r in range(len(dIF)):
            fa = f"{fa}<pre>⚫️{r+1}. [{dIF.loc[r,'LastClassDate']}] [{dIF.loc[r,'Points']}] {dIF.loc[r,'FruitName'][:8]} - {dIF.loc[r,'L1N'][:8]} ({dIF.loc[r,'L1G']}){dIF.loc[r,'L2N'][:11]} ({dIF.loc[r,'L2G']}) - {(dIF.loc[r,'BBTN'])[:8]} ({dIF.loc[r,'BBTG']}) - {(dIF.loc[r,'LastTopic'])} → [{(dIF.loc[r,'NextClassDate'])}]</pre>\n"
        fa = fa + '\n'
        
    if len(dFP) == 0:
        fp = ''
    else:
        fpP = dPts.loc['Fallen P','Pts']
        fp = f"<i><b><u>Fallen Picking ({fpP} pt)</u></b></i>\n"
        for r in range(len(dFP)):
            fp = f"{fp}<pre>❌{r+1}. [{dFP.loc[r,'LastClassDate']}] [{dFP.loc[r,'Points']}] {dFP.loc[r,'FruitName'][:8]} - {dFP.loc[r,'L1N'][:8]} ({dFP.loc[r,'L1G']}){dFP.loc[r,'L2N'][:11]} ({dFP.loc[r,'L2G']}) - {(dFP.loc[r,'BBTN'])[:8]} ({dFP.loc[r,'BBTG']}) - {(dFP.loc[r,'LastTopic'])} → [{(dFP.loc[r,'NextClassDate'])}]</pre>\n"
        fp = fp + '\n'
        
    if len(dAC) == 0:
        ac = ''
    else:
        acP = dPts.loc['ABB CCT','Pts']
        ac = f"<i><b><u>CCT ABB ({acP} pt)</u></b></i>\n"
        for r in range(len(dAC)):
            ac = f"{ac}<pre>⭐️{r+1}. [{dAC.loc[r,'LastClassDate']}] [{dAC.loc[r,'Points']}] {dAC.loc[r,'FruitName'][:8]} - {dAC.loc[r,'L1N'][:8]} ({dAC.loc[r,'L1G']}){dAC.loc[r,'L2N'][:11]} ({dAC.loc[r,'L2G']}) - {(dAC.loc[r,'BBTN'])[:8]} ({dAC.loc[r,'BBTG']}) - {(dAC.loc[r,'LastTopic'])} → [{(dAC.loc[r,'NextClassDate'])}]</pre>\n"
        ac = ac + '\n'
        
    if len(dIC) == 0:
        ic = ''
    else:
        icP = dPts.loc['IBB CCT','Pts']
        ic = f"<i><b><u>CCT IBB ({icP} pt)</u></b></i>\n"
        for r in range(len(dIC)):
            ic = f"{ic}<pre>⭐️{r+1}. [{dIC.loc[r,'LastClassDate']}] [{dIC.loc[r,'Points']}] {dIC.loc[r,'FruitName'][:8]} - {dIC.loc[r,'L1N'][:8]} ({dIC.loc[r,'L1G']}){dIC.loc[r,'L2N'][:11]} ({dIC.loc[r,'L2G']}) - {(dIC.loc[r,'BBTN'])[:8]} ({dIC.loc[r,'BBTG']}) - {(dIC.loc[r,'LastTopic'])} → [{(dIC.loc[r,'NextClassDate'])}]</pre>\n"
        ic = ic + '\n'
    
    g = re.sub(r'^(\d)', r'G\1', g)
    result = f"<b><u>📚{g} BB Fruit List📚</u></b>\n\n<i>#. [LastClassDate] [Pts] - Fruit - L1(G)/L2(G) - BBT(G) - LastTopic → [NextClassDate]</i>\n\n{np}{op}{ab}{im}{fa}{fp}{ac}{ic}<b><i><u>Total: {npP+opP+abP+imP+ifP+fpP+acP+icP} Pts</u></i></b>"
    result = re.sub(r'\.0',r'',result)
    result = re.sub(r' \(\)',r'',result)
    result = re.sub(r'\((\d+)\)', r'(G\1)', result)
    result = re.sub(r'\[1\] ', r'', result)
    return result





def tol(d):
    conn = odbc.connect(conn_str)
    t = d if d != '__' else 'Total'
    header = f"🏛{str(d).replace('__','Youth')} BB Status Classification🏛" if d != '__' else '🌳Tree of Life🌳'
    bb_dept = f"""SELECT m.*, pNew, pOld, bbA, bbME, bbFA, pFA, cctA, cctI, cct, Total
FROM (
SELECT Dept, SUM(pNew)pNew, SUM(pOld)pOld, SUM(bbA)bbA, SUM(bbME)bbME, SUM(bbFA)bbFA, SUM(pFA)pFA, SUM(cctA)cctA, SUM(cctI)cctI, SUM(cctA + cctI)cct, SUM(Tot)Total
FROM ScottStatusNumbers WHERE Dept LIKE '{d}' GROUP BY Dept
UNION
SELECT '{t}' Dept, SUM(pNew)pNew, SUM(pOld)pOld, SUM(bbA)bbA, SUM(bbME)bbME, SUM(bbFA)bbFA, SUM(pFA)pFA, SUM(cctA)cctA, SUM(cctI)cctI, SUM(cctA + cctI)cct, SUM(Tot)Total
FROM ScottStatusNumbers WHERE Dept LIKE '{d}'
) s
LEFT JOIN
(SELECT Dept, SUM(NewM)mNew, SUM(OldM)mOld FROM ScottOldNewMGrp WHERE Dept LIKE '{d}' GROUP BY Dept
UNION SELECT '{t}', SUM(NewM)mNew, SUM(OldM)mOld FROM ScottOldNewMGrp WHERE Dept LIKE '{d}') m
ON m.Dept = s.Dept"""

    dd = pd.read_sql(bb_dept, conn)
    conn.cursor().close()
    dd = dd.transpose()
    dd.reset_index(inplace=True)

    rowtitles = ['Dept','NM','OM','NP','OP','AB','ME','FA','FP','CA','CI','CT','Tot']

    dept = str()
    for r in range(1,13):
        dept = f"{dept}{rowtitles[r]}{' '*(5-len(rowtitles[r]))}["
        for c in range(len(dd.columns)-1):
            dept = f"{dept}{' '*(5-len(str(dd.loc[r,c])))}{dd.loc[r,c]}|"
        dept = f"{dept}]\n"
    
    title = f"[  {d} ]" if d != '__' else '[  D1 |  D2 |  D3 |  D4 |  D5 |  D6 |  D7 |  D8 |  D9 |Total]'
        
    result = f"<b><u>{header}</u></b>\n\n<pre>Dept {title}\n\n{dept}</pre>"
    result = re.sub(r'\|]',r']',result)  # Replaces '|]' with ']'
    result = re.sub(r'\.0',r'  ',result) # Replaces '.0' with empty space
    result = re.sub(r'(\D)0([^.])',r'\1-\2',result)   # Replaces lone '0' with '-'
    result = result.replace('\nTotal','\n\nTotal').replace('\nNP','\n\nNP') # Shifts bottom Title row down one line, then separates meetings from bb statuses
    return result



def deptphone(d):
    conn = odbc.connect(conn_str)
    bb_dept1 = f"""SELECT Dept, pNew, pOld, bbA, bbME, bbFA, pFA, cctA, cctI, cct, Total
FROM (
SELECT Dept, SUM(pNew)pNew, SUM(pOld)pOld, SUM(bbA)bbA, SUM(bbME)bbME, SUM(bbFA)bbFA, SUM(pFA)pFA, SUM(cctA)cctA, SUM(cctI)cctI, SUM(cctA + cctI)cct, SUM(Tot)Total
FROM ScottStatusNumbers WHERE Dept IN ('D1','D2','D3','D4') GROUP BY Dept
) s"""
                  
    bb_dept2 = f"""SELECT Dept, pNew, pOld, bbA, bbME, bbFA, pFA, cctA, cctI, cct, Total
FROM (
SELECT Dept, SUM(pNew)pNew, SUM(pOld)pOld, SUM(bbA)bbA, SUM(bbME)bbME, SUM(bbFA)bbFA, SUM(pFA)pFA, SUM(cctA)cctA, SUM(cctI)cctI, SUM(cctA + cctI)cct, SUM(Tot)Total
FROM ScottStatusNumbers WHERE Dept IN ('D5','D6','D7','D8') GROUP BY Dept
UNION
SELECT 'Total' Dept, SUM(pNew)pNew, SUM(pOld)pOld, SUM(bbA)bbA, SUM(bbME)bbME, SUM(bbFA)bbFA, SUM(pFA)pFA, SUM(cctA)cctA, SUM(cctI)cctI, SUM(cctA + cctI)cct, SUM(Tot)Total
FROM ScottStatusNumbers WHERE Dept LIKE 'D_'
) s"""

    dd1 = pd.read_sql(bb_dept1, conn)
    dd1 = dd1.transpose()
    dd1.reset_index(inplace=True)
    
    dd2 = pd.read_sql(bb_dept2, conn)
    dd2 = dd2.transpose()
    dd2.reset_index(inplace=True)
    
    conn.cursor().close()

    rowtitles = ['Dept','NP  ','OP  ','AB  ','ME  ','FA  ','FP  ','CA  ','CI  ','CT  ','Tot ']

    dept1= str()
    dept2= str()
              
    for r in range(1,11):
        dept1 = f"{dept1}{rowtitles[r]}["
        dept2 = f"{dept2}{rowtitles[r]}["
        for c in range(len(dd1.columns)-1):
            dept1 = f"{dept1}{' '*(5-len(str(dd1.loc[r,c])))}{dd1.loc[r,c]}|"
        for c in range(len(dd2.columns)-1):
            dept2 = f"{dept2}{' '*(5-len(str(dd2.loc[r,c])))}{dd2.loc[r,c]}|"
        dept1 = f"{dept1}]\n"
        dept2 = f"{dept2}]\n"
        
    result = f"<b><u>🏛{str(d).replace('__','Youth')} BB Status Classification🏛</u></b>\n\n<pre>Dept[  D1 |  D2 |  D3 |  D4 ]\n\n{dept1}\n\nDept[  D5 |  D6 |  D7 |  D8 |Total]\n\n{dept2}</pre>"
    result = re.sub(r'\|]',r']',result)  # Replaces '|]' with ']'
    result = re.sub(r'\.0',r'  ',result) # Replaces '.0' with empty space
    result = re.sub(r'(\D)0([^.])',r'\1-\2',result)   # Replaces lone '0' with '-'
    result = result.replace('\nTot ','\n\nTot ') # Shifts bottom Title row down one line
    return result



def tolfull(d):
    
    header = f"🌳{str(d).replace('__','Youth')} Tree of Life🌳" if d != '__' else '🌳TOL Full🌳'
    conn = odbc.connect(conn_str)
    
    bb_group = f"""SELECT s.Grp, NewM mNew, OldM mOld, pNew, pOld, bbA, cctA, bbME, cctI, pFA, bbFA, Tot bbTot
FROM ScottStatusNumbers s LEFT JOIN ScottOldNewMGrp m ON s.Grp = m.Grp
WHERE s.Dept LIKE '{d}'"""
    bb_dept = f"""SELECT s.Dept, SUM(NewM)mNew, SUM(OldM)mOld, SUM(pNew)pNew, SUM(pOld)pOld,SUM(bbA)bbA, SUM(cctA)cctA, 
SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA, SUM(Tot)bbTot
FROM ScottStatusNumbers s LEFT JOIN ScottOldNewMGrp m ON s.Grp = m.Grp
WHERE s.Dept LIKE '{d}'
GROUP BY s.Dept"""
    bb_youth = f"""SELECT SUM(NewM)mNew, SUM(OldM)mOld, SUM(pNew)pNew, SUM(pOld)pOld,SUM(bbA)bbA, SUM(cctA)cctA, 
SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA, SUM(Tot)bbTot
FROM ScottStatusNumbers s LEFT JOIN ScottOldNewMGrp m ON s.Grp = m.Grp
WHERE s.Dept LIKE '{d}'"""
    
    dg = pd.read_sql(bb_group, conn)
    dd = pd.read_sql(bb_dept, conn)
    dy = pd.read_sql(bb_youth, conn)

    dg.columns = ['Grp','mNew','mOld','pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
    dd.columns = ['Dept','mNew','mOld','pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
    dy.columns = ['mNew','mOld','pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
    
    dg['Grp'] = dg['Grp'].str.replace(r'^(\d)', r'G\1')
    dd.replace(r' Dept',r'', regex = True, inplace = True)
    
    conn.cursor().close()

    separator = '|'
    
    group = str()
    for r in range(len(dg)):
        grp =    str(dg.loc[r,'Grp']) + ' '*(5-len(str(dg.loc[r,'Grp'])))
        mn  = ' '*(5-len(str(dg.loc[r,'mNew']))) + str(dg.loc[r,'mNew'])
        mo  = ' '*(6-len(str(dg.loc[r,'mOld']))) + str(dg.loc[r,'mOld'])
        pn  = ' '*(4-len(str(dg.loc[r,'pNew']))) + str(dg.loc[r,'pNew'])
        po  = ' '*(4-len(str(dg.loc[r,'pOld']))) + str(dg.loc[r,'pOld'])
        ba  = ' '*(5-len(str(dg.loc[r,'bbA'])))  + str(dg.loc[r,'bbA'])
        ca  = ' '*(5-len(str(dg.loc[r,'cctA']))) + str(dg.loc[r,'cctA'])
        bm  = ' '*(5-len(str(dg.loc[r,'bbME']))) + str(dg.loc[r,'bbME'])
        ci  = ' '*(3-len(str(dg.loc[r,'cctI']))) + str(dg.loc[r,'cctI'])
        pf  = ' '*(4-len(str(dg.loc[r,'pFA'])))  + str(dg.loc[r,'pFA'])
        bf  = ' '*(4-len(str(dg.loc[r,'bbFA']))) + str(dg.loc[r,'bbFA'])
        t   = ' '*(5-len(str(dg.loc[r,'Tot'])))  + str(dg.loc[r,'Tot'])
        
        group = f'{group}{grp}[{mn}|{mo}]   [{pn}|{po}{separator}{ba}|{ca}]   [{bm}|{ci}{separator}{pf}|{bf}]   [{t}]\n'
    
    dept = str()    
    for r in range(len(dd)):
        dpt = str(dd.loc[r,'Dept'])   + ' '*(5-len(str(dd.loc[r,'Dept'])))
        mn  = ' '*(5-len(str(dd.loc[r,'mNew']))) + str(dd.loc[r,'mNew'])
        mo  = ' '*(6-len(str(dd.loc[r,'mOld']))) + str(dd.loc[r,'mOld'])
        pn  = ' '*(4-len(str(dd.loc[r,'pNew']))) + str(dd.loc[r,'pNew'])
        po  = ' '*(4-len(str(dd.loc[r,'pOld']))) + str(dd.loc[r,'pOld'])
        ba  = ' '*(5-len(str(dd.loc[r,'bbA'])))  + str(dd.loc[r,'bbA'])
        ca  = ' '*(5-len(str(dd.loc[r,'cctA']))) + str(dd.loc[r,'cctA'])
        bm  = ' '*(5-len(str(dd.loc[r,'bbME']))) + str(dd.loc[r,'bbME'])
        ci  = ' '*(3-len(str(dd.loc[r,'cctI']))) + str(dd.loc[r,'cctI'])
        pf  = ' '*(4-len(str(dd.loc[r,'pFA'])))  + str(dd.loc[r,'pFA'])
        bf  = ' '*(4-len(str(dd.loc[r,'bbFA']))) + str(dd.loc[r,'bbFA'])
        t   = ' '*(5-len(str(dd.loc[r,'Tot'])))  + str(dd.loc[r,'Tot'])
        
        dept = f'{dept}{dpt}[{mn}|{mo}]   [{pn}|{po}{separator}{ba}|{ca}]   [{bm}|{ci}{separator}{pf}|{bf}]   [{t}]\n'
            
    if d == '__':
        mn = ' '*(5-len(str(dy.loc[0,'mNew']))) + str(dy.loc[0,'mNew'])
        mo = ' '*(6-len(str(dy.loc[0,'mOld']))) + str(dy.loc[0,'mOld'])
        pn = ' '*(4-len(str(dy.loc[0,'pNew']))) + str(dy.loc[0,'pNew'])
        po = ' '*(4-len(str(dy.loc[0,'pOld']))) + str(dy.loc[0,'pOld'])
        ba = ' '*(5-len(str(dy.loc[0,'bbA'])))  + str(dy.loc[0,'bbA'])
        ca = ' '*(5-len(str(dy.loc[0,'cctA']))) + str(dy.loc[0,'cctA'])
        bm = ' '*(5-len(str(dy.loc[0,'bbME']))) + str(dy.loc[0,'bbME'])
        ci = ' '*(3-len(str(dy.loc[0,'cctI']))) + str(dy.loc[0,'cctI'])
        pf = ' '*(4-len(str(dy.loc[0,'pFA'])))  + str(dy.loc[0,'pFA'])
        bf = ' '*(4-len(str(dy.loc[0,'bbFA']))) + str(dy.loc[0,'bbFA'])
        t  = ' '*(5-len(str(dy.loc[0,'Tot'])))  + str(dy.loc[0,'Tot'])
        
        youth = f'\nTotal[{mn}|{mo}]   [{pn}|{po}{separator}{ba}|{ca}]   [{bm}|{ci}{separator}{pf}|{bf}]   [{t}]\n'

    else:
        youth = str()
    
    result = f"""<b><u>{header}</u></b>\n\n<pre>Type [   MEETING  ]   [        ACTIVE       ]   [      INACTIVE     ]   [TOTAL]\n\nGrp  [  NM |  OM  ]   [ NP | OP {separator}  AB |  CA ]   [  ME | CI{separator} FP | FA ]   [TotBB]\n\n{group}\n{dept}{youth}</pre>"""
    result = re.sub(r'\.0',r'  ',result) # Replaces '.0' with empty space
    result = re.sub(r'(\D)0([^.])',r'\1-\2',result)   # Replaces lone '0' with '-'
    return result









def bbactive(d):
    
    conn = odbc.connect(conn_str)
    
    bb_group = f"SELECT Grp, Tot SP, pNew, bbA, cctA FROM ScottStatusNumbers WHERE Dept LIKE '{d}'"
    bb_dept = f"""SELECT Dept, SUM(Tot)SP, SUM(pNew)pNew, SUM(bbA)bbA, SUM(cctA)cctA FROM ScottStatusNumbers WHERE Dept LIKE '{d}' GROUP BY Dept"""
    bb_youth = f"""SELECT SUM(Tot)SP, SUM(pNew)pNew, SUM(bbA)bbA, SUM(cctA)cctA FROM ScottStatusNumbers WHERE Dept LIKE '{d}'"""
    
    dg = pd.read_sql(bb_group, conn)
    dd = pd.read_sql(bb_dept, conn)
    dy = pd.read_sql(bb_youth, conn)

    dg.columns = ['Grp','SP','pNew','bbA','cctA']
    dd.columns = ['Dept','SP','pNew','bbA','cctA']
    dy.columns = ['SP','pNew','bbA','cctA']
    
    dg['Grp'] = dg['Grp'].str.replace(r'^(\d)', r'G\1')
    dd.replace(r' Dept',r'', regex = True, inplace = True)
    
    conn.cursor().close()

    separator = '] ['
    
    group = str()
    for r in range(len(dg)):
        grp =    str(dg.loc[r,'Grp']) + ' '*(4-len(str(dg.loc[r,'Grp'])))
        sp  = ' '*(5-len(str(dg.loc[r,'SP'])))   + str(dg.loc[r,'SP'])
        pn  = ' '*(5-len(str(dg.loc[r,'pNew']))) + str(dg.loc[r,'pNew'])
        ba  = ' '*(5-len(str(dg.loc[r,'bbA'])))  + str(dg.loc[r,'bbA'])
        ca  = ' '*(4-len(str(dg.loc[r,'cctA']))) + str(dg.loc[r,'cctA'])
        group = f'{group}{grp}[{sp}][{pn}|{ba}|{ca}]\n'
    
    dept = str()    
    for r in range(len(dd)):
        dpt = str(dd.loc[r,'Dept'])   + ' '*(4-len(str(dd.loc[r,'Dept'])))
        sp  = ' '*(5-len(str(dd.loc[r,'SP'])))   + str(dd.loc[r,'SP'])
        pn  = ' '*(5-len(str(dd.loc[r,'pNew']))) + str(dd.loc[r,'pNew'])
        ba  = ' '*(5-len(str(dd.loc[r,'bbA'])))  + str(dd.loc[r,'bbA'])
        ca  = ' '*(4-len(str(dd.loc[r,'cctA']))) + str(dd.loc[r,'cctA'])
        dept = f'{dept}{dpt}[{sp}][{pn}|{ba}|{ca}]\n'
            
    if d == '__':
        sp = ' '*(5-len(str(dy.loc[0,'SP'])))   + str(dy.loc[0,'SP'])
        pn = ' '*(5-len(str(dy.loc[0,'pNew']))) + str(dy.loc[0,'pNew'])
        ba = ' '*(5-len(str(dy.loc[0,'bbA'])))  + str(dy.loc[0,'bbA'])
        ca = ' '*(4-len(str(dy.loc[0,'cctA']))) + str(dy.loc[0,'cctA'])
        youth = f'\nTot [{sp}][{pn}|{ba}|{ca}]\n'

    else:
        youth = str()
    
    result = f"""<b><u>{str(d).replace('__','Youth')} Active BB Status </u></b>\n\n<pre>Grp [  SP ][  NP |  AB | CA ]\n\n{group}\n{dept}{youth}</pre>"""
    result = re.sub(r'\.0',r'  ',result) # Replaces '.0' with empty space
    result = re.sub(r'(\D)0([^.])',r'\1-\2',result)   # Replaces lone '0' with '-'
    return result





def deptbbactive(d):
    
    conn = odbc.connect(conn_str)
    
    bb_group = f"SELECT Grp, Tot SP, pNew, bbA, cctA FROM ScottStatusNumbers WHERE Dept LIKE '{d}'"
    bb_dept = f"""SELECT Dept, SUM(Tot)SP, SUM(pNew)pNew, SUM(bbA)bbA, SUM(cctA)cctA FROM ScottStatusNumbers WHERE Dept LIKE '{d}' GROUP BY Dept"""
    bb_youth = f"""SELECT SUM(Tot)SP, SUM(pNew)pNew, SUM(bbA)bbA, SUM(cctA)cctA FROM ScottStatusNumbers WHERE Dept LIKE '{d}'"""
    
    dg = pd.read_sql(bb_group, conn)
    dd = pd.read_sql(bb_dept, conn)
    dy = pd.read_sql(bb_youth, conn)

    dg.columns = ['Grp','SP','pNew','bbA','cctA']
    dd.columns = ['Dept','SP','pNew','bbA','cctA']
    dy.columns = ['SP','pNew','bbA','cctA']
    
    dg['Grp'] = dg['Grp'].str.replace(r'^(\d)', r'G\1')
    dd.replace(r' Dept',r'', regex = True, inplace = True)
    
    conn.cursor().close()
    
    dept = str()    
    for r in range(len(dd)):
        dpt = str(dd.loc[r,'Dept'])   + ' '*(4-len(str(dd.loc[r,'Dept'])))
        sp  = ' '*(5-len(str(dd.loc[r,'SP'])))   + str(dd.loc[r,'SP'])
        pn  = ' '*(5-len(str(dd.loc[r,'pNew']))) + str(dd.loc[r,'pNew'])
        ba  = ' '*(5-len(str(dd.loc[r,'bbA'])))  + str(dd.loc[r,'bbA'])
        ca  = ' '*(4-len(str(dd.loc[r,'cctA']))) + str(dd.loc[r,'cctA'])
        dept = f'{dept}{dpt}[{sp}][{pn}|{ba}|{ca}]\n'
            
    if d == '__':
        sp = ' '*(5-len(str(dy.loc[0,'SP'])))   + str(dy.loc[0,'SP'])
        pn = ' '*(5-len(str(dy.loc[0,'pNew']))) + str(dy.loc[0,'pNew'])
        ba = ' '*(5-len(str(dy.loc[0,'bbA'])))  + str(dy.loc[0,'bbA'])
        ca = ' '*(4-len(str(dy.loc[0,'cctA']))) + str(dy.loc[0,'cctA'])
        youth = f'\nTot [{sp}][{pn}|{ba}|{ca}]\n'

    else:
        youth = str()
    
    result = f"""<b><u>{str(d).replace('__','Youth')} Active BB Status </u></b>\n\n<pre>Grp [  SP ][  NP |  AB | CA ]\n\n{dept}{youth}</pre>"""
    result = re.sub(r'\.0',r'  ',result) # Replaces '.0' with empty space
    result = re.sub(r'(\D)0([^.])',r'\1-\2',result)   # Replaces lone '0' with '-'
    return result








def bbinactive(d):
    
    conn = odbc.connect(conn_str)
    
    bb_group = f"""SELECT Grp, pOld, bbME, cctI, pFA, bbFA FROM ScottStatusNumbers WHERE Dept LIKE '{d}'"""
    bb_dept = f"""SELECT Dept, SUM(pOld)pOld, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA FROM ScottStatusNumbers WHERE Dept LIKE '{d}' GROUP BY Dept"""
    bb_youth = f"""SELECT SUM(pOld)pOld, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA FROM ScottStatusNumbers WHERE Dept LIKE '{d}'"""
    
    dg = pd.read_sql(bb_group, conn)
    dd = pd.read_sql(bb_dept, conn)
    dy = pd.read_sql(bb_youth, conn)

    dg.columns = ['Grp','pOld','bbME','cctI','pFA','bbFA']
    dd.columns = ['Dept','pOld','bbME','cctI','pFA','bbFA']
    dy.columns = ['pOld','bbME','cctI','pFA','bbFA']
    
    dg['Grp'] = dg['Grp'].str.replace(r'^(\d)', r'G\1')
    dd.replace(r' Dept',r'', regex = True, inplace = True)
    
    conn.cursor().close()
    
    separator = '||'
    
    group = str()
    for r in range(len(dg)):
        grp =    str(dg.loc[r,'Grp']) + ' '*(4-len(str(dg.loc[r,'Grp'])))
        po  = ' '*(4-len(str(dg.loc[r,'pOld']))) + str(dg.loc[r,'pOld'])
        bm  = ' '*(4-len(str(dg.loc[r,'bbME']))) + str(dg.loc[r,'bbME'])
        ci  = ' '*(4-len(str(dg.loc[r,'cctI']))) + str(dg.loc[r,'cctI'])
        pf  = ' '*(4-len(str(dg.loc[r,'pFA'])))  + str(dg.loc[r,'pFA'])
        bf  = ' '*(4-len(str(dg.loc[r,'bbFA']))) + str(dg.loc[r,'bbFA'])
        group = f'{group}{grp}[{po}|{bm}|{ci}{separator}{pf}|{bf}]\n'
    
    dept = str()    
    for r in range(len(dd)):
        dpt = str(dd.loc[r,'Dept'])   + ' '*(4-len(str(dd.loc[r,'Dept'])))
        po  = ' '*(4-len(str(dd.loc[r,'pOld']))) + str(dd.loc[r,'pOld'])
        bm  = ' '*(4-len(str(dd.loc[r,'bbME']))) + str(dd.loc[r,'bbME'])
        ci  = ' '*(4-len(str(dd.loc[r,'cctI']))) + str(dd.loc[r,'cctI'])
        pf  = ' '*(4-len(str(dd.loc[r,'pFA'])))  + str(dd.loc[r,'pFA'])
        bf  = ' '*(4-len(str(dd.loc[r,'bbFA']))) + str(dd.loc[r,'bbFA'])
        dept = f'{dept}{dpt}[{po}|{bm}|{ci}{separator}{pf}|{bf}]\n'
            
    if d == '__':
        bm = ' '*(4-len(str(dy.loc[0,'bbME']))) + str(dy.loc[0,'bbME'])
        po = ' '*(4-len(str(dy.loc[0,'pOld']))) + str(dy.loc[0,'pOld'])
        ci = ' '*(4-len(str(dy.loc[0,'cctI']))) + str(dy.loc[0,'cctI'])
        pf = ' '*(4-len(str(dy.loc[0,'pFA'])))  + str(dy.loc[0,'pFA'])
        bf = ' '*(4-len(str(dy.loc[0,'bbFA']))) + str(dy.loc[0,'bbFA']) 
        youth = f'\nTot [{po}|{bm}|{ci}{separator}{pf}|{bf}]\n'

    else:
        youth = str()
    
    result = f"""<b><u>{str(d).replace('__','Youth')} Inactive BB Status </u></b>\n\n<pre>Grp [ OP | ME | CI {separator} FP | FA ]\n\n{group}\n{dept}{youth}</pre>"""
    result = re.sub(r'\.0',r'  ',result) # Replaces '.0' with empty space
    result = re.sub(r'(\D)0([^.])',r'\1-\2',result)   # Replaces lone '0' with '-'
    return result




def deptbbinactive(d):
    
    conn = odbc.connect(conn_str)
    
    bb_group = f"""SELECT Grp, pOld, bbME, cctI, pFA, bbFA FROM ScottStatusNumbers WHERE Dept LIKE '{d}'"""
    bb_dept = f"""SELECT Dept, SUM(pOld)pOld, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA FROM ScottStatusNumbers WHERE Dept LIKE '{d}' GROUP BY Dept"""
    bb_youth = f"""SELECT SUM(pOld)pOld, SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA FROM ScottStatusNumbers WHERE Dept LIKE '{d}'"""
    
    dg = pd.read_sql(bb_group, conn)
    dd = pd.read_sql(bb_dept, conn)
    dy = pd.read_sql(bb_youth, conn)

    dg.columns = ['Grp','pOld','bbME','cctI','pFA','bbFA']
    dd.columns = ['Dept','pOld','bbME','cctI','pFA','bbFA']
    dy.columns = ['bbME','pOld','cctI','pFA','bbFA']
    
    dg['Grp'] = dg['Grp'].str.replace(r'^(\d)', r'G\1')
    dd.replace(r' Dept',r'', regex = True, inplace = True)
    
    conn.cursor().close()
    
    separator = '||'
    
    dept = str()    
    for r in range(len(dd)):
        dpt = str(dd.loc[r,'Dept'])   + ' '*(4-len(str(dd.loc[r,'Dept'])))
        po  = ' '*(4-len(str(dd.loc[r,'pOld']))) + str(dd.loc[r,'pOld'])
        bm  = ' '*(4-len(str(dd.loc[r,'bbME']))) + str(dd.loc[r,'bbME'])
        ci  = ' '*(4-len(str(dd.loc[r,'cctI']))) + str(dd.loc[r,'cctI'])
        pf  = ' '*(4-len(str(dd.loc[r,'pFA'])))  + str(dd.loc[r,'pFA'])
        bf  = ' '*(4-len(str(dd.loc[r,'bbFA']))) + str(dd.loc[r,'bbFA'])
        dept = f'{dept}{dpt}[{po}|{bm}|{ci}{separator}{pf}|{bf}]\n'
            
    if d == '__':
        bm = ' '*(4-len(str(dy.loc[0,'bbME']))) + str(dy.loc[0,'bbME'])
        po = ' '*(4-len(str(dy.loc[0,'pOld']))) + str(dy.loc[0,'pOld'])
        ci = ' '*(4-len(str(dy.loc[0,'cctI']))) + str(dy.loc[0,'cctI'])
        pf = ' '*(4-len(str(dy.loc[0,'pFA'])))  + str(dy.loc[0,'pFA'])
        bf = ' '*(4-len(str(dy.loc[0,'bbFA']))) + str(dy.loc[0,'bbFA']) 
        youth = f'\nTot [{po}|{bm}|{ci}{separator}{pf}|{bf}]\n'

    else:
        youth = str()
    
    result = f"""<b><u>{str(d).replace('__','Youth')} Inactive BB Status </u></b>\n\n<pre>Grp [ OP | ME | CI {separator} FP | FA ]\n\n{dept}{youth}</pre>"""
    result = re.sub(r'\.0',r'  ',result) # Replaces '.0' with empty space
    result = re.sub(r'(\D)0([^.])',r'\1-\2',result)   # Replaces lone '0' with '-'
    return result









def fmlist(g):
    conn = odbc.connect(conn_str)
    dN = pd.read_sql(f"SELECT * FROM ScottNewM('{g}') WHERE M_Status = 'NewM' ORDER BY M_TIME DESC", conn)
    dO = pd.read_sql(f"SELECT * FROM ScottNewM('{g}') WHERE M_Status = 'OldM' ORDER BY M_TIME DESC", conn)
    dPts = pd.read_sql(f"SELECT M_Status, SUM(Pts)Pts FROM ScottNewM('{g}') GROUP BY M_Status", conn)
    dN.columns = ['UID','M_TIME','FishName','M1N','M1G','M1P','M2N','M2G','M2P','P_TIME','M_Status','Pts']
    dO.columns = ['UID','M_TIME','FishName','M1N','M1G','M1P','M2N','M2G','M2P','P_TIME','M_Status','Pts']
    dPts.columns = ['M_Status','Pts']
    dN['M1G'] = dN['M1G'].str.replace(r'^(\d)', r'G\1')
    dN['M2G'] = dN['M2G'].str.replace(r'^(\d)', r'G\1')
    dO['M1G'] = dO['M1G'].str.replace(r'^(\d)', r'G\1')
    dO['M2G'] = dO['M2G'].str.replace(r'^(\d)', r'G\1')
    dN['M_TIME'] = pd.to_datetime(dN['M_TIME']).dt.strftime('%a %d/%m')
    dO['M_TIME'] = pd.to_datetime(dO['M_TIME']).dt.strftime('%a %d/%m')
    dPts.set_index('M_Status', inplace=True)
    conn.cursor().close()
    
    nPt,oPt = 0,0
    g = re.sub(r'^(\d)',r'G\1',g).capitalize()
    
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
    return result



def fmstatus(g,access):
    
    name = 'Member' if access == 'IT' else 'MemberCode'
    
    conn = odbc.connect(conn_str)                        
    dm = pd.read_sql(f"SELECT {name}, NewM, OldM FROM ScottOldNewM WHERE Grp LIKE '{g}' ORDER BY MemberCode", conn)
    dt = pd.read_sql(f"SELECT SUM(NewM)NewM, SUM(OldM)OldM FROM ScottOldNewM WHERE Grp LIKE '{g}'", conn)
    dm.columns = ['Member','NewM','OldM']
    dt.columns = ['NewM','OldM']
    g = re.sub(r'^(\d)',r'G\1',g).capitalize()
    conn.cursor().close()
    
    if len(dm) == 0:
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
        return member
    
    
    





def deptfm(d):
           
    conn = odbc.connect(conn_str)
    
    dm = pd.read_sql(f"SELECT Grp, NewM, OldM FROM ScottOldNewMGrp WHERE Dept LIKE '{d}'", conn)
    dd = pd.read_sql(f"SELECT Dept, SUM(NewM)NewM, SUM(OldM)OldM FROM ScottOldNewMGrp WHERE Dept LIKE '{d}' GROUP BY Dept", conn)
    dt = pd.read_sql(f"SELECT SUM(NewM)NewM, SUM(OldM)OldM FROM ScottOldNewMGrp WHERE Dept LIKE '{d}'", conn)

    dm.columns = ['Grp','NewM','OldM']
    dd.columns = ['Dept','NewM','OldM']
    dt.columns = ['NewM','OldM']
    dm['Grp'] = dm['Grp'].str.replace(r'^(\d)', r'G\1')
    dd.replace(r' Dept',r'', regex = True, inplace = True)

    conn.cursor().close()

    group = str()
    for r in range(len(dm)):
        grp = str(dm.loc[r,'Grp']) + ' '*(6-len(str(dm.loc[r,'Grp'])))
        nm  = ' '*(6-len(str(dm.loc[r,'NewM'])))  + str(dm.loc[r,'NewM'])
        om  = ' '*(6-len(str(dm.loc[r,'OldM'])))  + str(dm.loc[r,'OldM'])
        group = f'{group}{grp}[{nm}|{om}]\n'

    dept = str()    
    for r in range(len(dd)):
        dpt = str(dd.loc[r,'Dept']) + ' '*(6-len(str(dd.loc[r,'Dept'])))
        nm  = ' '*(6-len(str(dd.loc[r,'NewM'])))  + str(dd.loc[r,'NewM'])
        om  = ' '*(6-len(str(dd.loc[r,'OldM'])))  + str(dd.loc[r,'OldM'])
        dept = f'{dept}{dpt}[{nm}|{om}]\n'

    if d == '__' :
        nm  = ' '*(6-len(str(dt.loc[0,'NewM'])))  + str(dt.loc[0,'NewM'])
        om  = ' '*(6-len(str(dt.loc[0,'OldM'])))  + str(dt.loc[0,'OldM'])
        total = f'\nTotal [{nm}|{om}]'
    else:
        total = str()
        
    depttitle = d.replace('__','Youth')

    fmp = f"<b><u>{depttitle} FM Status</u></b>\n\n<pre>Grp   [ NewM | OldM ]\n\n{group}\n{dept}{total}</pre>"
    fmp = re.sub(r'\.0',r'  ',fmp) # Replaces '.0' with empty space
    fmp = re.sub(r'(\D)0([^.])',r'\1-\2',fmp)   # Replaces lone '0' with '-'
    return fmp








def bbfull(d):
    
    header = f"🌳{str(d).replace('__','Youth')} Tree of Life🌳"
    conn = odbc.connect(conn_str)
    
    bb_group = f"""SELECT s.Grp, pNew, pOld, bbA, cctA, bbME, cctI, pFA, bbFA, Tot bbTot
FROM ScottStatusNumbers s LEFT JOIN ScottOldNewMGrp m ON s.Grp = m.Grp
WHERE s.Dept LIKE '{d}'"""
    bb_dept = f"""SELECT s.Dept, SUM(pNew)pNew, SUM(pOld)pOld,SUM(bbA)bbA, SUM(cctA)cctA, 
SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA, SUM(Tot)bbTot
FROM ScottStatusNumbers s LEFT JOIN ScottOldNewMGrp m ON s.Grp = m.Grp
WHERE s.Dept LIKE '{d}'
GROUP BY s.Dept"""
    bb_youth = f"""SELECT SUM(pNew)pNew, SUM(pOld)pOld,SUM(bbA)bbA, SUM(cctA)cctA, 
SUM(bbME)bbME, SUM(cctI)cctI, SUM(pFA)pFA, SUM(bbFA)bbFA, SUM(Tot)bbTot
FROM ScottStatusNumbers s LEFT JOIN ScottOldNewMGrp m ON s.Grp = m.Grp
WHERE s.Dept LIKE '{d}'"""
    
    dg = pd.read_sql(bb_group, conn)
    dd = pd.read_sql(bb_dept, conn)
    dy = pd.read_sql(bb_youth, conn)

    dg.columns = ['Grp','pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
    dd.columns = ['Dept','pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
    dy.columns = ['pNew','pOld','bbA','cctA','bbME','cctI','pFA','bbFA','Tot']
    
    dg['Grp'] = dg['Grp'].str.replace(r'^(\d)', r'G\1')
    dd.replace(r' Dept',r'', regex = True, inplace = True)
    
    conn.cursor().close()

    separator = '|'
    
    group = str()
    for r in range(len(dg)):
        grp =    str(dg.loc[r,'Grp']) + ' '*(4-len(str(dg.loc[r,'Grp'])))
        pn  = ' '*(4-len(str(dg.loc[r,'pNew']))) + str(dg.loc[r,'pNew'])
        po  = ' '*(4-len(str(dg.loc[r,'pOld']))) + str(dg.loc[r,'pOld'])
        ba  = ' '*(5-len(str(dg.loc[r,'bbA'])))  + str(dg.loc[r,'bbA'])
        ca  = ' '*(4-len(str(dg.loc[r,'cctA']))) + str(dg.loc[r,'cctA'])
        bm  = ' '*(4-len(str(dg.loc[r,'bbME']))) + str(dg.loc[r,'bbME'])
        ci  = ' '*(4-len(str(dg.loc[r,'cctI']))) + str(dg.loc[r,'cctI'])
        pf  = ' '*(4-len(str(dg.loc[r,'pFA'])))  + str(dg.loc[r,'pFA'])
        bf  = ' '*(4-len(str(dg.loc[r,'bbFA']))) + str(dg.loc[r,'bbFA'])
        t   = ' '*(5-len(str(dg.loc[r,'Tot'])))  + str(dg.loc[r,'Tot'])
        
        group = f'{group}{grp}[{pn}|{po}{separator}{ba}|{ca}]   [{bm}|{ci}{separator}{pf}|{bf}]   [{t}]\n'
    
    dept = str()    
    for r in range(len(dd)):
        dpt = str(dd.loc[r,'Dept'])   + ' '*(4-len(str(dd.loc[r,'Dept'])))
        pn  = ' '*(4-len(str(dd.loc[r,'pNew']))) + str(dd.loc[r,'pNew'])
        po  = ' '*(4-len(str(dd.loc[r,'pOld']))) + str(dd.loc[r,'pOld'])
        ba  = ' '*(5-len(str(dd.loc[r,'bbA'])))  + str(dd.loc[r,'bbA'])
        ca  = ' '*(4-len(str(dd.loc[r,'cctA']))) + str(dd.loc[r,'cctA'])
        bm  = ' '*(4-len(str(dd.loc[r,'bbME']))) + str(dd.loc[r,'bbME'])
        ci  = ' '*(4-len(str(dd.loc[r,'cctI']))) + str(dd.loc[r,'cctI'])
        pf  = ' '*(4-len(str(dd.loc[r,'pFA'])))  + str(dd.loc[r,'pFA'])
        bf  = ' '*(4-len(str(dd.loc[r,'bbFA']))) + str(dd.loc[r,'bbFA'])
        t   = ' '*(5-len(str(dd.loc[r,'Tot'])))  + str(dd.loc[r,'Tot'])
        
        dept = f'{dept}{dpt}[{pn}|{po}{separator}{ba}|{ca}]   [{bm}|{ci}{separator}{pf}|{bf}]   [{t}]\n'
            
    if d == '__':
        pn = ' '*(4-len(str(dy.loc[0,'pNew']))) + str(dy.loc[0,'pNew'])
        po = ' '*(4-len(str(dy.loc[0,'pOld']))) + str(dy.loc[0,'pOld'])
        ba = ' '*(5-len(str(dy.loc[0,'bbA'])))  + str(dy.loc[0,'bbA'])
        ca = ' '*(4-len(str(dy.loc[0,'cctA']))) + str(dy.loc[0,'cctA'])
        bm = ' '*(4-len(str(dy.loc[0,'bbME']))) + str(dy.loc[0,'bbME'])
        ci = ' '*(4-len(str(dy.loc[0,'cctI']))) + str(dy.loc[0,'cctI'])
        pf = ' '*(4-len(str(dy.loc[0,'pFA'])))  + str(dy.loc[0,'pFA'])
        bf = ' '*(4-len(str(dy.loc[0,'bbFA']))) + str(dy.loc[0,'bbFA'])
        t  = ' '*(5-len(str(dy.loc[0,'Tot'])))  + str(dy.loc[0,'Tot'])
        
        youth = f'\nTot [{pn}|{po}{separator}{ba}|{ca}]   [{bm}|{ci}{separator}{pf}|{bf}]   [{t}]\n'

    else:
        youth = str()
    
    result = f"""<b><u>{header}</u></b>\n\n<pre>Type[       ACTIVE       ]   [      INACTIVE     ]   [TOTAL]\n\nGrp [ NP | OP {separator}  AB | CA ]   [ ME | CI {separator} FP | FA ]   [TotBB]\n\n{group}\n{dept}{youth}</pre>"""
    result = re.sub(r'\.0',r'  ',result) # Replaces '.0' with empty space
    result = re.sub(r'(\D)0([^.])',r'\1-\2',result)   # Replaces lone '0' with '-'
    return result




# FOR BBTDEPT --> MAKE OPTION TO CHANGE BETWEEN QUALIFIED BBT (i.e. "active"/"teaching"), BTM12, 13, ETC
# (like they just add a number like "13" to change btm number)
# AND ALLOW OPTION FOR "ALL BBTs INC. BTM"










def bbtdeptold():
    conn = odbc.connect(conn_str)
    header = "🏛BBT Status Summary🏛"
    bb_dept = f"""SELECT * FROM (
SELECT Dept, SUM(pNew)pNew, SUM(pOld)pOld, SUM(bbA)bbA, SUM(bbME)bbME, SUM(bbFA)bbFA, SUM(pFA)pFA, SUM(cctA)cctA, SUM(cctI)cctI, SUM(Total)Total
                  FROM ScottBBTStatusMembers
                  GROUP BY Dept
UNION ALL
SELECT 'Total', SUM(pNew)pNew, SUM(pOld)pOld, SUM(bbA)bbA, SUM(bbME)bbME, SUM(bbFA)bbFA, SUM(pFA)pFA, SUM(cctA)cctA, SUM(cctI)cctI, SUM(Total)Total
                  FROM ScottBBTStatusMembers
				  ) s WHERE Dept IS NOT NULL AND Dept NOT IN ('Church','SCM','OtherChurch')
				  ORDER BY CASE Dept
                  WHEN 'Serving' THEN 1 WHEN 'Culture' THEN 2 WHEN 'HWPL' THEN 3 WHEN 'SFT' THEN 4 WHEN 'Office' THEN 5
				  WHEN 'M&W Dept' THEN 6 WHEN 'MCT' THEN 7 WHEN 'Total' THEN 8 END, Dept"""
    dd = pd.read_sql(bb_dept, conn)
    conn.cursor().close()
    dd = dd.transpose()
    dd.reset_index(inplace=True)

    rowtitles = ['Dept ','NP   ','OP   ','AB   ','ME   ','FA   ','FP   ','CA   ','CI   ','Tot  ']

    dept = str()
    for r in range(1,10):
        dept = f"{dept}{rowtitles[r]}["
        for c in range(len(dd.columns)-1):
            dept = f"{dept}{' '*(3-len(str(dd.loc[r,c])))}{dd.loc[r,c]}|"
        dept = f"{dept}]\n"
    
    title = '[ D1| D2| D3| D4| D5| D6| D7| D8| D9|OTH|SFT|M&W|MCT|TOT]'
        
    result = f"<b><u>{header}</u></b>\n\n<pre>Dept {title}\n\n{dept}</pre>"
    result = re.sub(r'\|]',r']',result)  # Replaces '|]' with ']'
    result = re.sub(r'\.0',r'  ',result) # Replaces '.0' with empty space
    result = re.sub(r'(\D)0([^.])',r'\1-\2',result)   # Replaces lone '0' with '-'
    result = result.replace('\nTot','\n\nTot') # Shifts bottom Title row down one line
    return result







def bbtdept(r):
    conn = odbc.connect(conn_str)
    header = "🏛BBT Status Summary🏛"
    bb_dept = f"""SELECT * FROM (
SELECT Dept, SUM(pNew)pNew, SUM(pOld)pOld, SUM(bbA)bbA, SUM(bbME)bbME, SUM(bbFA)bbFA, SUM(pFA)pFA, SUM(cctA)cctA, SUM(cctI)cctI, SUM(Total)Total
                  FROM CodeyBBTStatusMembers('{r}')
                  GROUP BY Dept
UNION ALL
SELECT 'Total', SUM(pNew)pNew, SUM(pOld)pOld, SUM(bbA)bbA, SUM(bbME)bbME, SUM(bbFA)bbFA, SUM(pFA)pFA, SUM(cctA)cctA, SUM(cctI)cctI, SUM(Total)Total
                  FROM CodeyBBTStatusMembers('{r}')
				  ) s WHERE Dept IS NOT NULL AND Dept NOT IN ('Church','SCM','OtherChurch')
				  ORDER BY CASE Dept
                  WHEN 'Serving' THEN 1 WHEN 'Culture' THEN 2 WHEN 'HWPL' THEN 3 WHEN 'SFT' THEN 4 WHEN 'Office' THEN 5
				  WHEN 'M&W Dept' THEN 6 WHEN 'MCT' THEN 7 WHEN 'Total' THEN 8 END, Dept"""
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
    result = result.replace('\nTot','\n\nTot') # Shifts bottom Title row down one line
    return result



def bbtbtmstatus(r):
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
    return result


def whofish(ph):
    return "fished by . . ."







def ev(id):
    
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
        df['OLG'] = df['OLG'].str.replace(r'^(\d)', r'G\1')
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
        dN['OLG'] = dN['OLG'].str.replace(r'^(\d)', r'G\1')
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
        dO['OLG'] = dO['OLG'].str.replace(r'^(\d)', r'G\1')
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
        dNP['BBTG'] = dNP['BBTG'].str.replace(r'^(\d)', r'G\1')
        dNP['OLG'] = dNP['OLG'].str.replace(r'^(\d)', r'G\1')
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
        dOP['BBTG'] = dOP['BBTG'].str.replace(r'^(\d)', r'G\1')
        dOP['OLG'] = dOP['OLG'].str.replace(r'^(\d)', r'G\1')
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
        dAB['BBTG'] = dAB['BBTG'].str.replace(r'^(\d)', r'G\1')
        dAB['OLG'] = dAB['OLG'].str.replace(r'^(\d)', r'G\1')
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
        dIM['BBTG'] = dIM['BBTG'].str.replace(r'^(\d)', r'G\1')
        dIM['OLG'] = dIM['OLG'].str.replace(r'^(\d)', r'G\1')
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
        dIF['BBTG'] = dIF['BBTG'].str.replace(r'^(\d)', r'G\1')
        dIF['OLG'] = dIF['OLG'].str.replace(r'^(\d)', r'G\1')
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
        dFP['BBTG'] = dFP['BBTG'].str.replace(r'^(\d)', r'G\1')
        dFP['OLG'] = dFP['OLG'].str.replace(r'^(\d)', r'G\1')
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
        dAC['BBTG'] = dAC['BBTG'].str.replace(r'^(\d)', r'G\1')
        dAC['OLG'] = dAC['OLG'].str.replace(r'^(\d)', r'G\1')
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
        dIC['BBTG'] = dIC['BBTG'].str.replace(r'^(\d)', r'G\1')
        dIC['OLG'] = dIC['OLG'].str.replace(r'^(\d)', r'G\1')
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
    return result  
    



























# Start universalising ALL codey functions to filter by region and division (e.g. M&W) (it means every bb function must intake parameters for region and division)
# ALL bbt functions must take into account not just btm#, but bbt status (e.g. learning, active, etc.)
# Get updated list for all bbt + btm 




def lastseasonfmp(g):
    conn = odbc.connect(conn_str)
    sql_fish = f"""SELECT FishName Fish, ISNULL(l1.PREFERRED_NAME,'') L1, ISNULL(l1.MemberGroup,'') L1G, ISNULL(l2.PREFERRED_NAME,'') L2, ISNULL(l2.MemberGroup,'') L2G, ('0'+CAST(FishPhone AS VARCHAR(50))) Phone
FROM FruitData f
LEFT JOIN MemberData l1 ON l1.UID = F1_ID
LEFT JOIN MemberData l2 ON l2.UID = F2_ID
WHERE F_TIME >= '2023-07-20' AND F_TIME < '2023-09-13'
AND M_TIME IS NULL
AND (l1.MemberGroup LIKE '{g}' OR l2.MemberGroup LIKE '{g}')
ORDER BY L1, Fish"""
    sql_meet = f"""SELECT FishName Fish, ISNULL(l1.PREFERRED_NAME,'') L1, ISNULL(l1.MemberGroup,'') L1G, ISNULL(l2.PREFERRED_NAME,'') L2, ISNULL(l2.MemberGroup,'') L2G, ('0'+CAST(FishPhone AS VARCHAR(50))) Phone
FROM FruitData f
LEFT JOIN MemberData l1 ON l1.UID = Attendee_1_ID
LEFT JOIN MemberData l2 ON l2.UID = Attendee_2_ID
WHERE M_TIME >= '2023-07-20' AND M_TIME < '2023-09-13'
AND P_TIME IS NULL
AND (l1.MemberGroup LIKE '{g}' OR l2.MemberGroup LIKE '{g}')
ORDER BY L1, Fish"""
    sql_pick = f"""SELECT FruitName Fish, ISNULL(l1.PREFERRED_NAME,'') L1, ISNULL(l1.MemberGroup,'') L1G, ISNULL(l2.PREFERRED_NAME,'') L2, ISNULL(l2.MemberGroup,'') L2G, ('0'+CAST(f.FishPhone AS VARCHAR(50))) Phone
FROM BBData b
LEFT JOIN FruitData f ON b.UID = f.UID
LEFT JOIN MemberData l1 ON l1.UID = b.L1_ID
LEFT JOIN MemberData l2 ON l2.UID = b.L2_ID
WHERE Season = 38
AND b.UID NOT IN (SELECT UID FROM Report WHERE ClassDate >= '2023-07-20')
AND (l1.MemberGroup LIKE '{g}' OR l2.MemberGroup LIKE '{g}')
ORDER BY L1, Fish"""
    sql_bb = f"""SELECT FruitName Fish, ISNULL(l1.PREFERRED_NAME,'') L1, ISNULL(l1.MemberGroup,'') L1G, ISNULL(l2.PREFERRED_NAME,'') L2, ISNULL(l2.MemberGroup,'') L2G, ('0'+CAST(f.FishPhone AS VARCHAR(50))) Phone
FROM BBData b
LEFT JOIN FruitData f ON b.UID = f.UID
LEFT JOIN MemberData l1 ON l1.UID = b.L1_ID
LEFT JOIN MemberData l2 ON l2.UID = b.L2_ID
WHERE Season = 38
AND Stat_Abbr != 'CCT'
AND b.UID IN (SELECT UID FROM Report WHERE ClassDate >= '2023-07-20')
AND (l1.MemberGroup LIKE '{g}' OR l2.MemberGroup LIKE '{g}')
ORDER BY L1, Fish"""
    df = pd.read_sql(sql_fish, conn)
    dm = pd.read_sql(sql_meet, conn)
    dp = pd.read_sql(sql_pick, conn)
    db = pd.read_sql(sql_bb, conn)
    df.columns = ['Fish','L1','L1G','L2','L2G','Phone']
    dm.columns = ['Fish','L1','L1G','L2','L2G','Phone']
    dp.columns = ['Fish','L1','L1G','L2','L2G','Phone']
    db.columns = ['Fish','L1','L1G','L2','L2G','Phone']
    df['L1G'] = df['L1G'].str.replace(r'^(\d)', r'G\1')
    dm['L1G'] = dm['L1G'].str.replace(r'^(\d)', r'G\1')
    dp['L1G'] = dp['L1G'].str.replace(r'^(\d)', r'G\1')
    db['L1G'] = db['L1G'].str.replace(r'^(\d)', r'G\1')
    df['L2G'] = df['L2G'].str.replace(r'^(\d)', r'G\1')
    dm['L2G'] = dm['L2G'].str.replace(r'^(\d)', r'G\1')
    dp['L2G'] = dp['L2G'].str.replace(r'^(\d)', r'G\1')
    db['L2G'] = db['L2G'].str.replace(r'^(\d)', r'G\1')
    conn.cursor().close()
    if len(df) == 0:
        fish = "None in finding stage\n"
    else:
        fish = str()
        for r in range(len(df)):
            fish = f"{fish}<pre>🐟{r+1}.{df.loc[r,'Fish']} - {df.loc[r,'L1']} ({df.loc[r,'L1G']}) / {df.loc[r,'L2']} ({df.loc[r,'L2G']}) — {df.loc[r,'Phone']}</pre>\n"
        fish = f"<b><u>Finding Stage</u></b>\n\n{fish.replace('/  () ','')}"
        
    if len(dm) == 0:
        meet = "None in FM stage\n"
    else:
        meet = str()
        for r in range(len(dm)):
            meet = f"{meet}<pre>❤️{r+1}.{dm.loc[r,'Fish']} - {dm.loc[r,'L1']} ({dm.loc[r,'L1G']}) / {dm.loc[r,'L2']} ({dm.loc[r,'L2G']}) — {dm.loc[r,'Phone']}</pre>\n"
        meet = f"<b><u>FM Stage</u></b>\n\n{meet.replace('/  () ','')}"
        
    if len(dp) == 0:
        pick = "None in picking stage\n"
    else:
        pick = str()
        for r in range(len(dp)):
            pick = f"{pick}<pre>💚{r+1}.{dp.loc[r,'Fish']} - {dp.loc[r,'L1']} ({dp.loc[r,'L1G']}) / {dp.loc[r,'L2']} ({dp.loc[r,'L2G']}) — {dp.loc[r,'Phone']}</pre>\n"
        pick = f"<b><u>Picking Stage</u></b>\n\n{pick.replace('/  () ','')}"
        
    if len(db) == 0:
        bb = "None in bb stage\n"
    else:
        bb = str()
        for r in range(len(db)):
            bb = f"{bb}<pre>💙{r+1}.{db.loc[r,'Fish']} - {db.loc[r,'L1']} ({db.loc[r,'L1G']}) / {db.loc[r,'L2']} ({db.loc[r,'L2G']}) — {db.loc[r,'Phone']}</pre>\n"
        bb = f"<b><u>BB Stage</u></b>\n\n{bb.replace('/  () ','')}"
    
    g = re.sub(r'^(\d)',r'G\1',g).capitalize()
    result = f"<b><u>{g} September CT FMP List</u></b>\n\n{fish}\n\n{meet}\n\n{pick}\n\n{bb}"
    return result











def tempfmp(timerange,g,access):
        
    name = 'Member' if access == 'IT' else 'MemberCode'
  
    timevalues = {'today':     ['SELECT dbo.today()', 'SELECT dbo.tomorrow()', 'Today'],
                  'yesterday': ['SELECT dbo.yesterday()', 'SELECT dbo.today()', 'Yesterday'],
                  'week':      ['SELECT dbo.weekstart()', 'SELECT dbo.nextweekstart()', 'This Week'],
                  'lastweek':  ['SELECT dbo.lastweekstart()', 'SELECT dbo.weekstart()', 'Last Week'],
                  'season':    [f"'2023-10-26'", 'SELECT dbo.tomorrow()', 'SFT Season (From 26 Oct)']}
   
    s,e,title = timevalues[timerange]
    
    conn = odbc.connect(conn_str)
    
    memberQ = f"SELECT {name}, F, M, P, FE FROM SFTMemberFMP(({s}), ({e})) WHERE Grp LIKE '{g}'"
    totalQ  = f"SELECT SUM(F)F, SUM(M)M, SUM(P)P, SUM(FE)FE FROM SFTMemberFMP(({s}), ({e})) WHERE Grp LIKE '{g}'"
    dm = pd.read_sql(memberQ, conn)
    dt = pd.read_sql(totalQ, conn)

    dm.columns = ['Member','F','M','P','FE']
    dt.columns = ['F','M','P','FE']
    g = re.sub(r'^(\d)',r'G\1',g).capitalize()
    if len(dm) == 0:
        return "No members found"
    else:  
        conn.cursor().close()
        member = str()
        
        for r in range(len(dm)):
            mem = str(dm.loc[r,'Member'])[:8] + ' '*(8-len(str(dm.loc[r,'Member'])[:8]))
            f      = ' '*(4-len(str(dm.loc[r,'F'])))  + str(dm.loc[r,'F'])
            m      = ' '*(4-len(str(dm.loc[r,'M'])))  + str(dm.loc[r,'M'])
            p      = ' '*(3-len(str(dm.loc[r,'P'])))  + str(dm.loc[r,'P'])
            fe     = ' '*(3-len(str(dm.loc[r,'FE']))) + str(dm.loc[r,'FE'])
            
            member = f'{member}{mem}[{f}|{m}|{p}|{fe}]\n'
            
        f      = ' '*(4-len(str(dt.loc[0,'F'])))  + str(dt.loc[0,'F'])
        m      = ' '*(4-len(str(dt.loc[0,'M'])))  + str(dt.loc[0,'M'])
        p      = ' '*(3-len(str(dt.loc[0,'P'])))  + str(dt.loc[0,'P'])
        fe     = ' '*(3-len(str(dt.loc[0,'FE']))) + str(dt.loc[0,'FE'])
        
        total = f'Total   [{f}|{m}|{p}|{fe}]'
        
        member = f'<b><u>{g} FMPFE : {title}</u></b>\n\n<pre>Member  [FF.F|MM.M|P.P|F.E]\n\n{member}\n{total}</pre>'
        member = re.sub(r'\.0',r'  ',member) # Replaces '.0' with empty space
        member = re.sub(r'(\D)0([^.])',r'\1-\2',member)   # Replaces lone '0' with '-'
        return member





def tempdept(timerange,d):
    
    if d == '__':
        d = "__' OR Dept = 'DecSFT"
    if d == 'DecSFT':
        d = "D6' OR Dept = 'DecSFT"
    
    if timerange in {'today','yesterday'}:
        spc = [6,5,4,4,4,'Group [FFF.F|MM.M|PP.P|FF.E]',   'Total ']
    if timerange in {'week','lastweek'}:
        spc = [5,5,5,4,4,'Grp  [FFF.F|MMM.M|PP.P|FF.E]',   'Total']
    if timerange == 'season':
        spc = [4,6,6,5,5,'Grp [FFFF.F|MMMM.M|PPP.P|FFF.E]','Tot ']   

    timevalues = {'today':     ['SELECT dbo.today()', 'SELECT dbo.tomorrow()', 'Today'],
                  'yesterday': ['SELECT dbo.yesterday()', 'SELECT dbo.today()', 'Yesterday'],
                  'week':      ['SELECT dbo.weekstart()', 'SELECT dbo.nextweekstart()', 'This Week'],
                  'lastweek':  ['SELECT dbo.lastweekstart()', 'SELECT dbo.weekstart()', 'Last Week'],
                  'season':    ["'2023-10-26'", 'SELECT dbo.tomorrow()', 'SFT Season (From 26 Oct)']}
    
    s,e,timetitle = timevalues[timerange]
       
    conn = odbc.connect(conn_str)
    memberQ = f"SELECT Grp, SUM(F)F, SUM(M)M, SUM(P)P, SUM(FE)FE FROM SFTMemberFMP(({s}), ({e})) WHERE Dept LIKE '{d}' GROUP BY Grp ORDER BY LEN(Grp), Grp"
    deptQ   = f"SELECT Dept, SUM(F)F, SUM(M)M, SUM(P)P, SUM(FE)FE FROM SFTMemberFMP(({s}), ({e})) WHERE Dept LIKE '{d}' GROUP BY Dept ORDER BY Dept"  
    totalQ  = f"SELECT SUM(F)F, SUM(M)M, SUM(P)P, SUM(FE)FE FROM SFTMemberFMP(({s}), ({e})) WHERE Dept LIKE '{d}'"
    dm = pd.read_sql(memberQ, conn)
    dd = pd.read_sql(deptQ, conn)
    dt = pd.read_sql(totalQ, conn)

    dm.columns = ['Grp','F','M','P','FE']
    dd.columns = ['Dept','F','M','P','FE']
    dt.columns = ['F','M','P','FE']
    dm['Grp'] = dm['Grp'].str.replace(r'^(\d)', r'G\1')
    dd.replace(r' Dept',r'', regex = True, inplace = True)

    conn.cursor().close()

    group = str()
    for r in range(len(dm)):
        grp = str(dm.loc[r,'Grp']) + '.'*(spc[0]-len(str(dm.loc[r,'Grp'])))
        f  = ' '*(spc[1]-len(str(dm.loc[r,'F'])))  + str(dm.loc[r,'F'])
        m  = ' '*(spc[2]-len(str(dm.loc[r,'M'])))  + str(dm.loc[r,'M'])
        p  = ' '*(spc[3]-len(str(dm.loc[r,'P'])))  + str(dm.loc[r,'P'])
        fe = ' '*(spc[4]-len(str(dm.loc[r,'FE']))) + str(dm.loc[r,'FE'])
        group = f'{group}{grp}[{f}|{m}|{p}|{fe}]\n'

    dept = str()    
    for r in range(len(dd)):
        ds = str(dd.loc[r,'Dept']).replace('DecSFT','SFT')
        dpt = ds + '.'*(spc[0]-len(ds))
        f  = ' '*(spc[1]-len(str(dd.loc[r,'F'])))  + str(dd.loc[r,'F'])
        m  = ' '*(spc[2]-len(str(dd.loc[r,'M'])))  + str(dd.loc[r,'M'])
        p  = ' '*(spc[3]-len(str(dd.loc[r,'P'])))  + str(dd.loc[r,'P'])
        fe = ' '*(spc[4]-len(str(dd.loc[r,'FE']))) + str(dd.loc[r,'FE'])
        dept = f'{dept}{dpt}[{f}|{m}|{p}|{fe}]\n'

    if d in ['__',"__' OR Dept = 'DecSFT"]:
        f  = ' '*(spc[1]-len(str(dt.loc[0,'F'])))  + str(dt.loc[0,'F'])
        m  = ' '*(spc[2]-len(str(dt.loc[0,'M'])))  + str(dt.loc[0,'M'])
        p  = ' '*(spc[3]-len(str(dt.loc[0,'P'])))  + str(dt.loc[0,'P'])
        fe = ' '*(spc[4]-len(str(dt.loc[0,'FE']))) + str(dt.loc[0,'FE'])
        total = f'\n{spc[6]}[{f}|{m}|{p}|{fe}]'
    else:
        total = str()
        
    depttitle = d.replace("__' OR Dept = 'DecSFT",'SFT Grouping').replace("D6' OR Dept = 'DecSFT",'D6 + SFT')

    fmp = f"<b><u>{depttitle} FMPFE : {timetitle}</u></b>\n\n<pre>{spc[5]}\n\n{group}\n{dept}{total}</pre>"
    fmp = re.sub(r'\.0',r'  ',fmp) # Replaces '.0' with empty space
    fmp = re.sub(r'(\D)0([^.])',r'\1-\2',fmp)   # Replaces lone '0' with '-'
    return fmp




# LAST SEASON FUNCTIONS