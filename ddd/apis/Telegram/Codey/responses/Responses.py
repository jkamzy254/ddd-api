from datetime import datetime, timedelta
from .sqlcodes import SQLCodes

def bot_responses(id,tname,input_text):
    
    if input_text.lower().startswith('register'):
            i,user,pw = input_text.split('.')
            return SQLCodes.reg_new_user_request(id,tname,user,pw)
    
    uid,name,access,g,d,sid,ss = SQLCodes.teledata(id).split('/')
    original_uid,original_name = uid,name
    print(f"""TELEDATA:
          uid - {uid}
          name - {name}
          access - {access}
          g - {g}
          d - {d}
          sid - {sid}
          ss - {ss}""")
    
    user_message = str(input_text).lower().replace(' ','')
        
    if access == 'IT':
        if '|' in input_text:
            user_message,user_name = input_text.split('|')
            user_message = user_message.lower()
            uid,name,access,g,d,sid,ss = SQLCodes.namedata(user_name).split('/')
            print(f"""NAMEDATA:
          uid - {uid}
          name - {name}
          access - {access}
          g - {g}
          d - {d}
          sid - {sid}
          ss - {ss}""")
                        
    if access == 'None':
        return '-'

    
    if access in ['All','IT']:
        d = 'D[0-9]%'
        if '//' in user_message:
            try:
                command,d = user_message.split('//')
                d = d.capitalize()
                access = d
                print(f"command = {command}, d = {d}, access = {access}")
            except ValueError:
                    return 'Format error: Too many "/"s'
        elif '/' in user_message:
            try:
                command,g = user_message.split('/')
                access = 'Group' # If specific group is specified, their access for the current function reduced to Group-level
            except ValueError:
                return 'Format error: Too many "/"s'
            d,sid,ss = SQLCodes.groupinfo(g).split('/')
        else:
            command = user_message
    
    elif access in ['D1','D2','D3','D4','D5','D6','D7','D8','D9','SFT','DecSFT','Dept','M&W Dept']:
        d = access if access != 'Dept' else d
        allowed_groups = SQLCodes.deptgroup(d)
        if '/' in user_message:
            try:
                command,g = user_message.split('/')
            except ValueError:
                return 'Format error: Too many "/"s'
            d,sid,ss = SQLCodes.groupinfo(g).split('/')
            access = 'Group' # If specific group is specified, their access for the current function reduced to Group-level
            if g not in allowed_groups and user_message.lower()[:3] != 'ev/':
                return 'Sorry, this group is outside your department!'
        else:
            command = user_message

    elif access in ['Group','Israel']:
        command = user_message
        if command in ['youthtoday','youthyesterday','youthweek','youthlastweek','youthseason','depttoday','deptyesterday','deptweek','deptlastweek','deptseason','gyjntoday','gyjnyesterday','gyjnweek','gyjnlastweek','gyjnseason','oevtoday','oevyesterday','oevweek','oevlastweek','oevseason','tgwtoday','tgwyesterday','tgwweek','tgwlastweek','tgwseason','bbfull','tolfull','bblastseason','youthmxpx','bbdept']:
            return 'You are not allowed to use this function'

    SQLCodes.functionlog(original_uid, original_name, input_text, command)
    
    # if r in ('Geelong','Darwin'):
    #     r = 'Online'
        
    if command.startswith('all'):
        sid = '%'
        print(f"sid - {sid}")
        command = command[3:]
    
    if 'phonenumber' in str(user_message):
        return "Sorry, 'phonenumber' is not a recognised command. However, to check if someone has been fished before, you may enter their phone number starting with '04' e.g. <pre>0412345678</pre> :)"
    if user_message.startswith('04'):
        return SQLCodes.duplicate_check(user_message)
       
    if command == 'commands':
        if access == 'IT':
            return '<b><u>List of commands</u></b>\n<i>g = group number\nd = department\nT = today/yesterday/week/lastweek/season\n\n<b><u>FMP Fish Lists</u></b></i>\n<pre>🔹todayfish/g  🔹todaympfe/g\n🔹weekfish/g   🔹weekmpfe/g\n🔹seasonpick/g 🔹seasonfe/g\n🔹mxlist/g     🔹pxlist/g\n🔹fmlist/g</pre>\n\n<b><u><i>FMP Per Member</i></u></b>\n<pre>🔸Tfmp/g       🔸gyjnT\n🔸oevT         🔸ievT\n🔸eduT         🔸svT\n🔸fmstatus/g</pre>\n\n<b><u><i>FMP Per Group</i></u></b>\n<pre>🔺youthT       🔺tgwT\n🔺memberT      🔺deptfm\n♦️youthmxpx</pre>\n\n<b><u><i>BB Fruit Lists (Leaf Standard)</i></u></b>\n<pre>📙bbpick/g     📘bbfe/g\n📚bbstatus/g</pre>\n\n<b><u><i>BB Per Group (Leaf Standard)</i></u></b>\n<pre>🖥bbactive     🖥bbinactive\n🖥bbfull       🏛deptphone\n🌳tolfull      🌳tol</pre>\n\n<b><i><u>BB / Grp (BBT std)</u>   <u>BB Per BBT</u></i></b>\n<pre>📖bbtstatus    📖bbtstatus/d\n📖btm12status  📖btm12status/d\n📖btm13status  📖btm13status/d</pre>\n\n<b><i><u>All BB Students</u>         <u>Dept BB Students</u></i></b>\n<pre>📜bbtlist      📜bbtlist/d\n📜btm12list    📜btm12list/d\n📜btm13list    📜btm13list\n📜gyjnbbtlist  📜gyjnbbtlist/d</pre>\n\n<b><u><i>BB / Grp (BBT std)</i></u></b>\n<pre>🏛bbtdept</pre>\n\n<b><u><i>Member EV Summary</i></u></b>\n<pre>ev/id</pre>\n\n<b><u><i>Double Fish Check</i></u></b>\n<pre>📱04........</pre>'
        if access == 'All':
            return '<b><u>List of commands</u></b>\n<i>g = group number\nd = department\nT = today/yesterday/week/lastweek/season\n# = number</i>\n\n<b><u><i>FMP Per Member</i></u></b>\n<pre>🔸Tfmp/g       🔸gyjnT\n🔸oevT         🔸ievT\n🔸eduT         🔸svT\n🔸fmstatus/g</pre>\n\n<b><u><i>FMP Per Group</i></u></b>\n<pre>🔺youthT       🔺tgwT\n🔺memberT      🔺deptfm\n♦️youthmxpx</pre>\n\n<b><u><i>BB Per Group (Leaf Standard)</i></u></b>\n<pre>🖥bbactive     🖥bbinactive\n🖥bbfull       🏛deptphone\n🌳tolfull      🌳tol</pre>\n\n<b><i><u>BB / Grp (BBT std)</u>   <u>BB Per BBT</u></i></b>\n<pre>📖bbtstatus    📖bbtstatus/d\n📖btm#status   📖btm#status/d</pre>\n\n<b><u><i>BB / Grp (BBT std)</i></u></b>\n<pre>🏛bbtdept</pre>\n\n<b><u><i>Double Fish Check</i></u></b>\n<pre>📱04........</pre>'
        if access in ['D1','D2','D3','D4','D5','D6','D7','D8','D9','SFT','Dept','M&W Dept']:
            return f"<b><u>List of commands</u></b>\n<i>g = group number\nT = today/yesterday/week/lastweek/season\n# = number</i>\n\n<b><u><i>FMP Per Member</i></u></b>\n<pre>🔸Tfmp/g       🔸gyjnT\n🔸oevT         🔸ievT\n🔸eduT         🔸svT\n🔸fmstatus/g</pre>\n\n<b><u><i>FMP Per Group</i></u></b>\n<pre>🔺deptT        🔺tgwT\n🔺memberT      🔺deptfm\n♦️deptmxpx</pre>\n\n<b><u><i>BB Per Group (Leaf Standard)</i></u></b>\n<pre>🖥bbactive     🖥bbinactive\n🖥bbfull       🏛bbdept\n🌳tolfull</pre>\n\n<b><i><u>BB Per BBT</u></i></b>\n<pre>📖bbtstatus\n📖btm#status</pre>\n\n<b><u><i>Double Fish Check</i></u></b>\n<pre>📱04........</pre>"
        if access == 'Group':
            return '<b><u>List of commands</u></b>\n\n<b><i><u>FMP Per Member</u></i></b>\n<pre>🔸todayfmp     🔸yesterdayfmp\n🔸weekfmp      🔸lastweekfmp\n🔸seasonfmp    🔸fmstatus</pre>\n\n<b><i><u>Double Fish Check</u></i></b>\n<pre>📱[phonenumber]</pre>'
        if access == 'Israel':
            return '<b><u>List of commands</u></b>\n\n🔸todayfmp\n🔸yesterdayfmp\n🔸weekfmp\n🔸lastweekfmp\n🔸seasonfmp\n\n📱04........</pre>'
    
    if command in ('tfmp','youtht','deptt','gyjnt','oevt','tgwt','membert','oevt','ievt','edut','svt'):
        return f"Sorry, <i>{command}</i> is not a valid command. Try replacing the 'T' with one of: 'today', 'yesterday', 'week', 'last week' or 'season'.\nFor example: <pre>" + command.replace('tfmp','todayfmp').replace('youtht','youthtoday').replace('deptt','depttoday').replace('gyjnt','gyjntoday').replace('tgwt','tgwtoday').replace('membert','membertoday').replace('oevt','oevtoday').replace('ievt','ievtoday').replace('edut','edutoday').replace('svt','svtoday') + "</pre> :)"
    
    if command in ['todayfmp','yesterdayfmp','weekfmp','lastweekfmp','seasonfmp']:
        timerange = command[:-3]
        return SQLCodes.memberfmp(timerange,g,sid,ss,access)
        
    if command == 'fmstatus':
        return SQLCodes.fmstatus(g,access)
        
    if command == 'bblist':
        return SQLCodes.bblist(d,g,sid,access)
    
    if command == 'bbstatus':
            return SQLCodes.bbstatus(g, d, sid, access)
    
    if (command.startswith('btm') or command.startswith('bbt') or command.startswith('gyjnbbt')) and command.endswith('list'):
        if d == 'D[0-9]%' and '/' in user_message:
            i,d = user_message.split('/')
        q,i = command.split('list')
        return SQLCodes.bbtlist(q,d,g,sid,access)
        
    if command != 'bbtbtmstatus' and (command.startswith('btm') or command.startswith('bbt') or command.startswith('gyjnbbt')) and command.endswith('status'):
        if d == 'D[0-9]%' and '/' in user_message:
            i,d = user_message.split('/')
        q,i = command.split('status')
        return SQLCodes.bbtstatus(q,g,d,sid,access)
        
    if (command.startswith('btm') or command.startswith('bbt') or command.startswith('gyjnbbt')) and command.endswith('active') and not command.endswith('inactive'):
        if d == 'D[0-9]%' and '/' in user_message:
            i,d = user_message.split('/')
        q,i = command.split('active')
        return SQLCodes.bbtactive(q,g,d,access)
    
    if (command.startswith('btm') or command.startswith('bbt') or command.startswith('gyjnbbt')) and command.endswith('inactive'):
        if d == 'D[0-9]%' and '/' in user_message:
            i,d = user_message.split('/')
        q,i = command.split('inactive')
        return SQLCodes.bbtinactive(q,g,d,access)
    
    if (command.startswith('deptbtm') or command.startswith('deptbbt') or command.startswith('deptgyjnbbt')) and command.endswith('status'):
        if d == 'D[0-9]%' and '/' in user_message:
            i,d = user_message.split('/')
        q,i = command.split('status') # removing 'inactive', leaving 'deptbbt' CAN ALSO USE .removesuffix('suffix')!!!!
        i,q = q.split('dept') # removing 'dept', leaving 'bbt' (or 'btm15', 'gyjnbbt' etc.) CAN ALSO USE .removesuffix('suffix')!!!!
        return SQLCodes.deptbbtstatus(q,d,access)
    
    if (command.startswith('deptbtm') or command.startswith('deptbbt') or command.startswith('deptgyjnbbt')) and command.endswith('active') and not command.endswith('inactive'):
        if d == 'D[0-9]%' and '/' in user_message:
            i,d = user_message.split('/')
        q,i = command.split('active') # removing 'inactive', leaving 'deptbbt' CAN ALSO USE .removesuffix('suffix')!!!!
        i,q = q.split('dept') # removing 'dept', leaving 'bbt' (or 'btm15', 'gyjnbbt' etc.) CAN ALSO USE .removesuffix('suffix')!!!!
        return SQLCodes.deptbbtactive(q,d,access)
    
    if (command.startswith('deptbtm') or command.startswith('deptbbt') or command.startswith('deptgyjnbbt')) and command.endswith('inactive'):
        if d == 'D[0-9]%' and '/' in user_message:
            i,d = user_message.split('/')
        q,i = command.split('inactive') # removing 'inactive', leaving 'deptbbt' CAN ALSO USE .removesuffix('suffix')!!!!
        i,q = q.split('dept') # removing 'dept', leaving 'bbt' (or 'btm15', 'gyjnbbt' etc.) CAN ALSO USE .removesuffix('suffix')!!!!
        return SQLCodes.deptbbtinactive(q,d,access)
    
    
    
    if command == 'classtoday':
        return SQLCodes.classes(g,d,access,'today')
    if command == 'classweek':
        return SQLCodes.classes(g,d,access,'week')
    
    
    
    
    # Dept and above functions
    if access in ['D1','D2','D3','D4','D5','D6','D7','D8','D9','D10','D11','D12','D13','D14','D15','Dept','SFT','DecSFT','M&W Dept','All','IT']:
        
        for task in ['youth','dept','tgw','member','gyjn','oev','iev','edu','sv']:
            if command.startswith(task):
                # Remove the X value from the string
                timerange = command[len(task):]
                # If the rest of the string is a Y value, return X and Y
                if timerange in ['today', 'yesterday', 'week', 'lastweek', 'season']:
                    if task in ['youth','dept','tgw','member']:
                        return SQLCodes.deptfmp(task,timerange,d,sid,ss,access)
                    if task in ['gyjn','oev','iev','edu','sv']:
                        return SQLCodes.taskfmp(task,timerange,d,sid,ss,access)    
        
        if command != 'bbtbtmstatus' and (command.startswith('btm') or command.startswith('bbt') or command.startswith('gyjnbbt')) and command.endswith('status'):
            if d == 'D[0-9]%' and '/' in user_message:
                i,d = user_message.split('/')
            q,i = command.split('status')
            return SQLCodes.bbtstatus(q,d,access)
        
        if command == 'tolfull':
            return SQLCodes.tolfull(d)
        if command == 'bbfull':
            return SQLCodes.bbfull(d)
        if command == 'bbactive':
            return SQLCodes.bbactive(d)
        if command == 'deptbbactive':
            return SQLCodes.deptbbactive(d)
        if command == 'bbinactive':
            return SQLCodes.bbinactive(d)
        if command == 'deptbbinactive':
            return SQLCodes.deptbbinactive(d)
        
        if command in ['youthmxpx','deptmxpx']:
            return SQLCodes.youthmxpx(d)

        if command in ['tol','bbdept']:
            return SQLCodes.tol(d)
        
        if command == 'deptfm':
            return SQLCodes.deptfm(d)
        
        if command.startswith('approve'):
            a,userUID,telID,i = command.split('#')
            return SQLCodes.approve_new_user_request(userUID,telID)
        
        if access in ['All','IT']:
            if command == 'deptphone':
                return SQLCodes.deptphone(d)
            if command == 'bbtdeptold':
                return SQLCodes.bbtdeptold()
            if command == 'bbtdept':
                return SQLCodes.bbtdept(sid)
            if command == 'bbtbtmstatus':
                return SQLCodes.bbtbtmstatus()
            
    if access == 'IT':
        
        # Group Functions
        if command == 'todayfish':
            return SQLCodes.todayfish(g)
        if command == 'weekfish':
            return SQLCodes.weekfish(g)
        if command == 'seasonpick':
            return SQLCodes.seasonpick(g) 
        if command == 'seasonfe':
            return SQLCodes.seasonfe(g)
        if command == 'todaympfe':
            return SQLCodes.todaympfe(g)
        if command == 'weekmpfe':
            return SQLCodes.weekmpfe(g)
        if command == 'mxlist':
            return SQLCodes.mxlist(g)
        if command == 'pxlist':
            return SQLCodes.pxlist(g)
        if command == 'bbpick':
            return SQLCodes.bbpick(g)    
        if command == 'bbfe':
            return SQLCodes.bbfe(g)
        if command == 'fmlist':
            return SQLCodes.fmlist(g)

        if (command.startswith('btm') or command.startswith('bbt') or command.startswith('gyjnbbt')) and command.endswith('listold'):
            if d == 'D[0-9]%' and '/' in user_message:
                i,d = user_message.split('/')
            q,i = command.split('listold')
            return SQLCodes.bbtlistold(q,d)
        
        if command == 'ev':
            i,id = user_message.split('/')
            if access == 'IT':
                return SQLCodes.ev(id)
            if access in ['D1','D2','D3','D4','D5','D6','D7','D8','D9','DecSFT','SFT','Dept','M&W Dept']:
                idlist = SQLCodes.idlist('dept',d)
            if access == 'Group':
                idlist = SQLCodes.idlist('group',g)
            if int(id) in idlist:
                return SQLCodes.ev(id)
            else:
                return 'Sorry, you cannot access this member ID'
        if command == 'lastseasonfmp':
            return SQLCodes.lastseasonfmp(g)
        if command == 'test':
            return 'test'
             
    return "Sorry, I don't recognise that command. Please type 'commands' for a list of commands"