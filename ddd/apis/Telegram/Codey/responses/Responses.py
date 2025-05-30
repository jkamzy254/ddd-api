from datetime import datetime, timedelta
from .sqlcodes import SQLCodes

def bot_responses(id,tname,input_text):
    
    if input_text.lower().startswith('register'):
            i,user,pw = input_text.split('.')
            return SQLCodes.reg_new_user_request(id,tname,user,pw)
    
    uid,name,access,g,d,r,fmp_sid,fmp_ss,bb_sid,bb_ss = SQLCodes.teledata(id).split('/')
    original_uid,original_name = uid,name
    print(f"""TELEDATA:
          uid - {uid}
          name - {name}
          access - {access}
          g - {g}
          d - {d}
          r - {r}
          fmp_sid - {fmp_sid}
          fmp_ss - {fmp_ss}
          bb_sid - {bb_sid}
          bb_ss - {bb_ss}""")
    
    user_message = str(input_text).lower().replace(' ','')
        
    if access == 'IT':
        if '|' in input_text:
            user_message,user_name = input_text.split('|')
            user_message = user_message.lower()
            uid,name,access,g,d,r,fmp_sid,fmp_ss,bb_sid,bb_ss = SQLCodes.namedata(user_name).split('/')
            print(f"""NAMEDATA:
            uid - {uid}
            name - {name}
            access - {access}
            g - {g}
            d - {d}
            r - {r}
            fmp_sid - {fmp_sid}
            fmp_ss - {fmp_ss}
            bb_sid - {bb_sid}
            bb_ss - {bb_ss}""")
                        
    if access == 'None':
        return '-'

    
    if access in ['All','IT']:
        d = f'_D[0-9]%'
        if '//r' in user_message.lower():
            try:
                print('//r')
                command,d = user_message.lower().split('//')
                d = 'r1d[0-9]%' if d == 'r1' else d
                d = 'r2d[0-9]%' if d == 'r2' else d
                d = d.replace('r1','¹').replace('r2','²').replace('d','D')
                access = d
                print(f"command = {command}, d = {d}, access = {access}")
            except ValueError:
                    return 'Format error: Too many "/"s'
        elif '//' in user_message:
            try:
                print('//')
                command,d = user_message.split('//')
                access = d
                print(f"command = {command}, d = {d}, access = {access}")
            except ValueError:
                    return 'Format error: Too many "/"s'
        elif '/' in user_message:
            try:
                command,g = user_message.lower().split('/')
                g = g.replace('r1','¹').replace('r2','²').replace('g','G')
                access = 'Group' # If specific group is specified, their access for the current function reduced to Group-level
            except ValueError:
                return 'Format error: Too many "/"s'
            d,fmp_sid,fmp_ss,bb_sid,bb_ss = SQLCodes.groupinfo(g).split('/')
        else:
            command = user_message
        print(f'after: command = {command}, g = {g}, d = {d}, access = {access}')
            
    elif access in ['¹','²']:
        d = f'{access}D[0-9]%'
        if '//' in user_message:
            try:
                print('//')
                command,d = user_message.split('//')
                d = f'{access}{d.capitalize()}'
                access = d
                print(f"command = {command}, d = {d}, access = {access}")
            except ValueError:
                    return 'Format error: Too many "/"s'
        elif '/' in user_message:
            try:
                command,g = user_message.split('/')
                g = f'{access}{g.capitalize()}'
                access = 'Group' # If specific group is specified, their access for the current function reduced to Group-level
            except ValueError:
                return 'Format error: Too many "/"s'
            d,fmp_sid,fmp_ss,bb_sid,bb_ss = SQLCodes.groupinfo(g).split('/')
        else:
            command = user_message
    
    elif access in ['¹D[0-9]%','²D[0-9]%','¹D1','¹D2','¹D3','¹D4','¹D5','¹D6','¹D7','¹D8','¹D9','²D1','²D2','²D3','²D4','²D5','²D6','²D7','²D8','²D9','SFT','Geelong','Dept','M&W Dept']:
        d = access if access != 'Dept' else d
        allowed_groups = SQLCodes.deptgroup(d)
        if '/' in user_message:
            if access[0] in ['¹','²'] and '/g' in user_message.lower():
                print('access[0] in [¹,²]')
                try:
                    command,g = user_message.split('/')
                    g = f'{access[0]}{g.capitalize()}'
                except ValueError:
                    return 'Format error: Too many "/"s'
            else:
                try:
                    command,g = user_message.split('/')
                except ValueError:
                    return 'Format error: Too many "/"s'
            d,fmp_sid,fmp_ss,bb_sid,bb_ss = SQLCodes.groupinfo(g).split('/')
            access = 'Group' # If specific group is specified, their access for the current function reduced to Group-level
            if g.lower() not in allowed_groups and user_message.lower()[:3] != 'ev/':
                return 'Sorry, this group is outside your department!'
        else:
            command = user_message

    elif access in ['Group','Israel']:
        command = user_message
        if command in ['youthtoday','youthyesterday','youthweek','youthlastweek','youthseason','depttoday','deptyesterday','deptweek','deptlastweek','deptseason','gyjntoday','gyjnyesterday','gyjnweek','gyjnlastweek','gyjnseason','oevtoday','oevyesterday','oevweek','oevlastweek','oevseason','tgwtoday','tgwyesterday','tgwweek','tgwlastweek','tgwseason','bbfull','tolfull','bblastseason','youthmxpx','bbdept']:
            return 'You are not allowed to use this function'

    SQLCodes.functionlog(original_uid, original_name, input_text, command)
    
    print(f"""Final parameters before command call:
          uid - {uid}
          name - {name}
          access - {access}
          g - {g}
          d - {d}
          r - {r}
          fmp_sid - {fmp_sid}
          fmp_ss - {fmp_ss}
          bb_sid - {bb_sid}
          bb_ss - {bb_ss}""")
    
    # if r in ('Geelong','Darwin'):
    #     r = 'Online'
        
    if command.startswith('all'):
        fmp_sid = '%'
        bb_sid = '%'
        print(f"""fmp_sid - {fmp_sid}
                   bb_sid - {bb_sid}""")
        command = command[3:]
        
    if command.startswith('sft'):
        fmp_sid, bb_sid = SQLCodes.specifyct('sft').split('/')
        print(f"""fmp_sid - {fmp_sid}
                   bb_sid - {bb_sid}""")
        command = command[3:]
        
    if command.startswith('phys'):
        fmp_sid, bb_sid = SQLCodes.specifyct('phys').split('/')
        print(f"""fmp_sid - {fmp_sid}
                   bb_sid - {bb_sid}""")
        command = command[4:]
    
    if 'phonenumber' in str(user_message):
        return "Sorry, 'phonenumber' is not a recognised command. However, to check if someone has been fished before, you may enter their phone number starting with '04' e.g. <pre>0412345678</pre> :)"
    if user_message.startswith('04'):
        return SQLCodes.duplicate_check(user_message)
       
    if command == 'commands':
        if access == 'IT':
            return '<b><u>List of commands</u></b>\n<i>g = group number\nd = department\nT = today/yesterday/week/lastweek/season\n\n<b><u>FMP Fish Lists</u></b></i>\n<pre>🔹todayfish/g  🔹todaympfe/g\n🔹weekfish/g   🔹weekmpfe/g\n🔹seasonpick/g 🔹seasonfe/g\n🔹mxlist/g     🔹pxlist/g\n🔹fmlist/g</pre>\n\n<b><u><i>FMP Per Member</i></u></b>\n<pre>🔸Tfmp/g       🔸gyjnT\n🔸oevT         🔸ievT\n🔸eduT         🔸svT\n🔸fmstatus/g</pre>\n\n<b><u><i>FMP Per Group</i></u></b>\n<pre>🔺youthT       🔺tgwT\n🔺memberT      🔺deptfm\n♦️youthmxpx</pre>\n\n<b><u><i>BB Fruit Lists (Leaf Standard)</i></u></b>\n<pre>📙bbpick/g     📘bbfe/g\n📚bbstatus/g</pre>\n\n<b><u><i>BB Per Group (Leaf Standard)</i></u></b>\n<pre>🖥bbactive     🖥bbinactive\n🖥bbfull       🏛deptphone\n🌳tolfull      🌳tol</pre>\n\n<b><i><u>BB / Grp (BBT std)</u>   <u>BB Per BBT</u></i></b>\n<pre>📖bbtstatus    📖bbtstatus/d\n📖btm12status  📖btm12status/d\n📖btm13status  📖btm13status/d</pre>\n\n<b><i><u>All BB Students</u>         <u>Dept BB Students</u></i></b>\n<pre>📜bbtlist      📜bbtlist/d\n📜btm12list    📜btm12list/d\n📜btm13list    📜btm13list\n📜gyjnbbtlist  📜gyjnbbtlist/d</pre>\n\n<b><u><i>BB / Grp (BBT std)</i></u></b>\n<pre>🏛bbtdept</pre>\n\n<b><u><i>Member EV Summary</i></u></b>\n<pre>ev/id</pre>\n\n<b><u><i>Double Fish Check</i></u></b>\n<pre>📱04........</pre>'
        if access == 'All':
            return '<b><u>List of commands</u></b>\n<i>g = group number\nd = department\nT = today/yesterday/week/lastweek/season\n# = number</i>\n\n<b><u><i>FMP Per Member</i></u></b>\n<pre>🔸Tfmp/g       🔸gyjnT\n🔸oevT         🔸ievT\n🔸eduT         🔸svT\n🔸fmstatus/g</pre>\n\n<b><u><i>FMP Per Group</i></u></b>\n<pre>🔺youthT       🔺tgwT\n🔺memberT      🔺deptfm\n♦️youthmxpx</pre>\n\n<b><u><i>BB Per Group (Leaf Standard)</i></u></b>\n<pre>🖥bbactive     🖥bbinactive\n🖥bbfull       🏛deptphone\n🌳tolfull      🌳tol</pre>\n\n<b><i><u>BB / Grp (BBT std)</u>   <u>BB Per BBT</u></i></b>\n<pre>📖bbtstatus    📖bbtstatus/d\n📖btm#status   📖btm#status/d</pre>\n\n<b><u><i>BB / Grp (BBT std)</i></u></b>\n<pre>🏛bbtdept</pre>\n\n<b><u><i>Double Fish Check</i></u></b>\n<pre>📱04........</pre>'
        if access in ['¹D[0-9]%','²D[0-9]%','¹D1','¹D2','¹D3','¹D4','¹D5','¹D6','¹D7','¹D8','¹D9','²D1','²D2','²D3','²D4','²D5','²D6','²D7','²D8','²D9','SFT','Geelong','Dept','M&W Dept']:
            return f"<b><u>List of commands</u></b>\n<i>g = group number\nT = today/yesterday/week/lastweek/season\n# = number</i>\n\n<b><u><i>FMP Per Member</i></u></b>\n<pre>🔸Tfmp/g       🔸gyjnT\n🔸oevT         🔸ievT\n🔸eduT         🔸svT\n🔸fmstatus/g</pre>\n\n<b><u><i>FMP Per Group</i></u></b>\n<pre>🔺deptT        🔺tgwT\n🔺memberT      🔺deptfm\n♦️deptmxpx</pre>\n\n<b><u><i>BB Per Group (Leaf Standard)</i></u></b>\n<pre>🖥bbactive     🖥bbinactive\n🖥bbfull       🏛bbdept\n🌳tolfull</pre>\n\n<b><i><u>BB Per BBT</u></i></b>\n<pre>📖bbtstatus\n📖btm#status</pre>\n\n<b><u><i>Double Fish Check</i></u></b>\n<pre>📱04........</pre>"
        if access == 'Group':
            return "<b><u>List of commands</u></b>\n\n<i>❗️Note: Picking numbers are for physical CT only (Or in case of SFT, online CT only). To get all CT combined result, type 'all' before command, e.g. 'allseasonfmp', 'allbblist', etc.</i>\n\n<b><u><i>FMP Per Member</i></u></b>\n<pre>🔸todayfmp     🔸yesterdayfmp\n🔸weekfmp      🔸lastweekfmp\n🔸seasonfmp    🔸fmstatus</pre>\n\n<b><u><i>BB Fruits and BBT Students</i></u></b>\n<pre>🍎bblist     📋bbstatus\n🎓bbtlist    📋bbtstatus\n📖classtoday 📖classweek</pre>\n\n<b><u><i>Double Fish Check</i></u></b>\n<pre>📱[phonenumber]</pre>"
        if access == 'Israel':
            return '<b><u>List of commands</u></b>\n\n🔸todayfmp\n🔸yesterdayfmp\n🔸weekfmp\n🔸lastweekfmp\n🔸seasonfmp\n\n📱04........</pre>'
    
    if command in ('tfmp','youtht','deptt','gyjnt','oevt','tgwt','membert','oevt','ievt','edut','svt'):
        return f"Sorry, <i>{command}</i> is not a valid command. Try replacing the 'T' with one of: 'today', 'yesterday', 'week', 'last week' or 'season'.\nFor example: <pre>" + command.replace('tfmp','todayfmp').replace('youtht','youthtoday').replace('deptt','depttoday').replace('gyjnt','gyjntoday').replace('tgwt','tgwtoday').replace('membert','membertoday').replace('oevt','oevtoday').replace('ievt','ievtoday').replace('edut','edutoday').replace('svt','svtoday') + "</pre> :)"
        
    if command in ['todayfmp','yesterdayfmp','weekfmp','lastweekfmp','seasonfmp']:
        timerange = command[:-3]
        return SQLCodes.memberfmp(timerange,g,fmp_sid,fmp_ss,access)
        
    if command == 'fmstatus':
        return SQLCodes.fmstatus(g,access)
        
    if command == 'bblist':
        return SQLCodes.bblist(d,g,bb_sid,access)
    
    if command == 'bbstatus':
            return SQLCodes.bbstatus(g, d, bb_sid, access)
    
    if command == 'bbactive':
        return SQLCodes.bbactive(g, d, bb_sid, access)
        
    if command == 'bbinactive':
            return SQLCodes.bbinactive(g, d, bb_sid, access)
        
    if command == 'newbblist':
        return SQLCodes.newbblist(d,g,bb_sid,access)
    
    if command == 'newbbstatus':
            return SQLCodes.newbbstatus(g, d, bb_sid, access)
        
    if (command.startswith('newbtm') or command.startswith('newbbt') or command.startswith('newgyjnbbt')) and command.endswith('list'):
        q = command.removesuffix('list')
        return SQLCodes.newbbtlist(q,d,g,bb_sid,access)
        
    if (command.startswith('newbtm') or command.startswith('newbbt') or command.startswith('newgyjnbbt')) and command.endswith('status'):
        q,i = command.split('status')
        return SQLCodes.newbbtstatus(q,g,d,bb_sid,access)
        
    
    if (command.startswith('btm') or command.startswith('bbt') or command.startswith('gyjnbbt')) and command.endswith('list'):
        q = command.removesuffix('list')
        return SQLCodes.bbtlist(q,d,g,bb_sid,access)
        
    if command != 'bbtbtmstatus' and (command.startswith('btm') or command.startswith('bbt') or command.startswith('gyjnbbt')):
        if command.endswith('status'):
            q = command.removesuffix('status')
            return SQLCodes.bbtstatus(q,g,d,bb_sid,access,False) # returns normal bbtstatus
        if command.endswith('dept'):
            q = command.removesuffix('dept')
            return SQLCodes.bbtstatus(q,g,d,bb_sid,access,True) # returns bbtdept (bbtstatus but without group list)

        
    if (command.startswith('btm') or command.startswith('bbt') or command.startswith('gyjnbbt')) and command.endswith('active') and not command.endswith('inactive'):
        q = command.split('active')
        return SQLCodes.bbtactive(q, g, d, r, access)
    
    if (command.startswith('btm') or command.startswith('bbt') or command.startswith('gyjnbbt')) and command.endswith('inactive'):
        q,i = command.split('inactive')
        return SQLCodes.bbtinactive(q, g, d, r, access)
    
    if (command.startswith('deptbtm') or command.startswith('deptbbt') or command.startswith('deptgyjnbbt')) and command.endswith('status'):
        q,i = command.split('status') # removing 'inactive', leaving 'deptbbt' CAN ALSO USE .removesuffix('suffix')!!!!
        i,q = q.split('dept') # removing 'dept', leaving 'bbt' (or 'btm15', 'gyjnbbt' etc.) CAN ALSO USE .removesuffix('suffix')!!!!
        return SQLCodes.deptbbtstatus(q, d, r, access)
    
    if (command.startswith('deptbtm') or command.startswith('deptbbt') or command.startswith('deptgyjnbbt')) and command.endswith('active') and not command.endswith('inactive'):
        if d == '_D[0-9]%' and '/' in user_message:
            i,d = user_message.split('/')
        q,i = command.split('active') # removing 'inactive', leaving 'deptbbt' CAN ALSO USE .removesuffix('suffix')!!!!
        i,q = q.split('dept') # removing 'dept', leaving 'bbt' (or 'btm15', 'gyjnbbt' etc.) CAN ALSO USE .removesuffix('suffix')!!!!
        return SQLCodes.deptbbtactive(q, d, r, access)
    
    if (command.startswith('deptbtm') or command.startswith('deptbbt') or command.startswith('deptgyjnbbt')) and command.endswith('inactive'):
        if d == '_D[0-9]%' and '/' in user_message:
            i,d = user_message.split('/')
        q,i = command.split('inactive') # removing 'inactive', leaving 'deptbbt' CAN ALSO USE .removesuffix('suffix')!!!!
        i,q = q.split('dept') # removing 'dept', leaving 'bbt' (or 'btm15', 'gyjnbbt' etc.) CAN ALSO USE .removesuffix('suffix')!!!!
        return SQLCodes.deptbbtinactive(q, d, r, access)
    
    
    
    if command == 'classtoday':
        return SQLCodes.classes(g,d,access,'today')
    if command == 'classweek':
        return SQLCodes.classes(g,d,access,'week')
        
    if command not in ('edutoday','eduyesterday','edulastweek','eduweek','eduseason') and command.startswith('edu'):
        day = command.removeprefix('edu')
        return SQLCodes.edu(day, g, d, access) if day != 'rev' else SQLCodes.edurev(g, d, access)
    
    
    
    
    # Dept and above functions
    if access in ['¹D[0-9]%','²D[0-9]%','¹D1','¹D2','¹D3','¹D4','¹D5','¹D6','¹D7','¹D8','¹D9','²D1','²D2','²D3','²D4','²D5','²D6','²D7','²D8','²D9','Dept','SFT','M&W Dept','¹','²','All','IT']:
        
        for task in ['youth','dept','tgw','member','gyjn','oev','iev','edu','sv']:
            if command.startswith(task):
                # Remove the X value from the string
                timerange = command[len(task):]
                # If the rest of the string is a Y value, return X and Y
                if timerange in ['today', 'yesterday', 'week', 'lastweek', 'season']:
                    if task in ['youth','dept','tgw','member']:
                        return SQLCodes.deptfmp(task,timerange,d,fmp_sid,fmp_ss,access)
                    if task in ['gyjn','oev','iev','edu','sv']:
                        return SQLCodes.taskfmp(task,timerange,d,fmp_sid,fmp_ss,access)    
        
        if command != 'bbtbtmstatus' and (command.startswith('btm') or command.startswith('bbt') or command.startswith('gyjnbbt')) and command.endswith('status'):
            q,i = command.split('status')
            return SQLCodes.bbtstatus(q,d,access)
        
        if command == 'tolfull':
            return SQLCodes.tolfull(d)
        if command == 'bbfull':
            return SQLCodes.bbfull(d)
        if command == 'oldbbactive':
            return SQLCodes.oldbbactive(d)
        if command == 'deptbbactive':
            return SQLCodes.deptbbactive(d, bb_sid, access)
        if command == 'deptbbinactive':
            return SQLCodes.deptbbinactive(d, bb_sid, access)
        
        if command in ['youthmxpx','deptmxpx']:
            return SQLCodes.youthmxpx(d)

        if command in ['tol','bbdept']:
            return SQLCodes.tol(d)
        
        if command == 'deptfm':
            return SQLCodes.deptfm(d)
        
        if command.startswith('approve'):
            a,userUID,telID,i = command.split('#')
            return SQLCodes.approve_new_user_request(userUID,telID)
        
        if access in ['¹','²','All','IT']:
            if command == 'deptphone':
                return SQLCodes.deptphone(d)
            if command == 'bbtdeptold':
                return SQLCodes.bbtdeptold()
            # if command == 'bbtdept':
            #     return SQLCodes.bbtdept(d,bb_sid)
            
            # if access in ('All','IT'):
            #     if command == 'bbtbtmstatus':
            #         return SQLCodes.bbtbtmstatus()
            
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
            q,i = command.split('listold')
            return SQLCodes.bbtlistold(q,d)
        
        if command == 'ev':
            i,id = user_message.split('/')
            if access == 'IT':
                return SQLCodes.ev(id)
            if access in ['¹D[0-9]%','²D[0-9]%','¹D1','¹D2','¹D3','¹D4','¹D5','¹D6','¹D7','¹D8','¹D9','²D1','²D2','²D3','²D4','²D5','²D6','²D7','²D8','²D9','SFT','Geelong','Dept','M&W Dept']:
                idlist = SQLCodes.idlist('dept',d)
            if access == 'Group':
                idlist = SQLCodes.idlist('group',g)
            if int(id) in idlist:
                return SQLCodes.ev(id)
            else:
                return 'Sorry, you cannot access this member ID'
        if command == 'lastseasonfmp':
            return SQLCodes.lastseasonfmp(g)
        if command.startswith('telegramuser'):
            name,id = command.removeprefix('telegramuser').split('[]')
            return SQLCodes.test_function(name,id)
             
    return "Sorry, I don't recognise that command. Please type 'commands' for a list of commands"