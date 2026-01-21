from datetime import datetime, timedelta
from .sqlcodes import SQLCodes

def bot_responses(id,tname,input_text):

    pm = 'HTML@@' # Default parse mode

    if input_text.lower().startswith('markdownv2'):
        input_text = input_text[10:].strip() # The [10:] removes the 'markdownv2' part and .strip() removes any leading/trailing spaces
        print(f'MarkdownV2 detected. New input_text: {input_text}')
        pm = 'MarkdownV2@@'

    elif input_text.lower().startswith('markdown'):
        input_text = input_text[8:].strip() # The [8:] removes the 'markdown' part and .strip() removes any leading/trailing spaces
        print(f'Markdown detected. New input_text: {input_text}')
        pm = 'Markdown@@'

    if input_text.lower() == 'test':
        return pm + SQLCodes.markdownv2test()
    
    if input_text.lower().startswith('register'):
            i,user,pw = input_text.split('.')
            return SQLCodes.reg_new_user_request(id,tname,user,pw) # Do not add parse mode prefix for this function
    
    ssn = 'phys'
    uid,name,access,g,d,r,fmp_sid,fmp_ss,bb_sid,bb_ss,phys_sid,on_sid = SQLCodes.teledata(id).split('/')
    original_uid,original_name,original_access = uid,name,access
    print(f"""TELEDATA:
          uid - {uid}
          name - {name}
          access - {access}
          g - {g} | d - {d} | r - {r}
          fmp_sid - {fmp_sid} | fmp_ss - {fmp_ss} | bb_sid - {bb_sid} | bb_ss - {bb_ss}
          phys_sid - {phys_sid} | on_sid - {on_sid}""")
    
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
                  g - {g} | d - {d} | r - {r}
                  fmp_sid - {fmp_sid} | fmp_ss - {fmp_ss} | bb_sid - {bb_sid} | bb_ss - {bb_ss}
                  phys_sid - {phys_sid} | on_sid - {on_sid}""")
                        
    if access == 'None':
        return '-'

    
    if access in ['All','IT','MT']:
        d = f'D[0-9]%' if access != 'MT' else '%'
        g = '%' if access == 'MT' else g
        if '//r' in user_message.lower():
            try:
                print('//r')
                command,d = user_message.lower().split('//')
                d = 'r1d[0-9]%' if d == 'r1' else d
                d = 'r2d[0-9]%' if d == 'r2' else d
                d = d.replace('r1','¹').replace('r2','²').replace('d','D')
                access = d if access != 'MT' else 'MT'
                print(f"command = {command}, d = {d}, access = {access}")
            except ValueError:
                    return 'Format error: Too many "/"s'
        elif '//' in user_message:
            try:
                print('//')
                command,d = user_message.split('//')
                d = d.capitalize() if d.startswith('d') else d.replace('sft','SFT').replace('inner','Inner')
                access = d if access != 'MT' else 'MT'
                print(f"command = {command}, d = {d}, access = {access}")
            except ValueError:
                    return 'Format error: Too many "/"s'
        elif '/' in user_message:
            try:
                command,g = user_message.lower().split('/')
                g = g.replace('r1','¹').replace('r2','²').replace('g','G')
                access = 'Group' if access != 'MT' else 'MT' # If specific group is specified, their access for the current function reduced to Group-level
            except ValueError:
                return 'Format error: Too many "/"s'
            d,fmp_sid,fmp_ss,bb_sid,bb_ss = SQLCodes.groupinfo(g).split('/')
        else:
            command = user_message
        print(f'after: command = {command}, g = {g}, d = {d}, access = {access}')
            
    # elif access in ['¹','²']:
    #     d = f'{access}D[0-9]%'
    #     if '//' in user_message:
    #         try:
    #             print('//')
    #             command,d = user_message.split('//')
    #             d = f'{access}{d.capitalize()}'
    #             access = d if access != 'MT' else 'MT'
    #             print(f"command = {command}, d = {d}, access = {access}")
    #         except ValueError:
    #                 return 'Format error: Too many "/"s'
    #     elif '/' in user_message:
    #         try:
    #             command,g = user_message.split('/')
    #             g = f'{access}{g.capitalize()}'
    #             access = 'Group' if access != 'MT' else 'MT' # If specific group is specified, their access for the current function reduced to Group-level
    #         except ValueError:
    #             return 'Format error: Too many "/"s'
    #         d,fmp_sid,fmp_ss,bb_sid,bb_ss = SQLCodes.groupinfo(g).split('/')
    #     else:
    #         command = user_message
    
    elif access in ['D[0-9]%','D1','D2','D3','D4','D5','D6','D7','D8','D9','D10','D11','D12','D13','D14','D15','D16','D17','D18','D19','D20','¹D[0-9]%','²D[0-9]%','¹D1','¹D2','¹D3','¹D4','¹D5','¹D6','¹D7','¹D8','¹D9','²D1','²D2','²D3','²D4','²D5','²D6','²D7','²D8','²D9','SFT','Geelong','Dept','M&W Dept','InnerSFT','MT']:
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
            access = 'Group' if access != 'MT' else 'MT' # If specific group is specified, their access for the current function reduced to Group-level
            if g.lower() not in allowed_groups and user_message.lower()[:3] != 'ev/':
                return 'Sorry, this group is outside your department!'
        else:
            command = user_message

    elif access in ['Group','Israel']:
        command = user_message
        if command in ['youthtoday','youthyesterday','youthweek','youthlastweek','youthseason','depttoday','deptyesterday','deptweek','deptlastweek','deptseason','gyjntoday','gyjnyesterday','gyjnweek','gyjnlastweek','gyjnseason','oevtoday','oevyesterday','oevweek','oevlastweek','oevseason','tgwtoday','tgwyesterday','tgwweek','tgwlastweek','tgwseason','bbfull','tolfull','bblastseason','youthmxpx','bbdept']:
            return 'You are not allowed to use this function'

    SQLCodes.functionlog(original_uid, original_name, input_text, command)
    
    # print(f"""Final parameters before command call:
    #       uid - {uid}
    #       name - {name}
    #       access - {access}
    #       g - {g}
    #       d - {d}
    #       r - {r}
    #       fmp_sid - {fmp_sid}
    #       fmp_ss - {fmp_ss}
    #       bb_sid - {bb_sid}
    #       bb_ss - {bb_ss}""")
    
    # if r in ('Geelong','Darwin'):
    #     r = 'Online'
        
    if command.startswith('all'):
        ssn = 'all'
        fmp_sid, bb_sid = '%', '%'
        print(f"""fmp_sid - {fmp_sid}
                   bb_sid - {bb_sid}""")
        command = command[3:]
        
    if command.startswith('sft'):
        ssn = 'sft'
        fmp_sid, bb_sid = on_sid, on_sid # fmp_sid, bb_sid = SQLCodes.specifyct('sft').split('/')
        print(f"""fmp_sid - {fmp_sid}
                   bb_sid - {bb_sid}""")
        command = command[3:]
        
    if command.startswith('phys'):
        ssn = 'phys'
        fmp_sid, bb_sid = phys_sid, phys_sid # fmp_sid, bb_sid = SQLCodes.specifyct('phys').split('/')
        print(f"""fmp_sid - {fmp_sid}
                   bb_sid - {bb_sid}""")
        command = command[4:]
    
    # GYJN and above (except MT) functions:
    if access != 'MT':
        if 'phonenumber' in str(user_message):
            return "Sorry, 'phonenumber' is not a recognised command. However, to check if someone has been fished before, you may enter their phone number starting with '04' e.g. <pre>0412345678</pre> :)"
        if user_message.startswith('04'):
            return pm + SQLCodes.duplicate_check(user_message)
        
        if command == 'commands':
            return pm + SQLCodes.commands(access)
        
        if command in ('tfmp','youtht','deptt','gyjnt','oevt','tgwt','membert','oevt','ievt','edut','svt'):
            return f"Sorry, <i>{command}</i> is not a valid command. Try replacing the 'T' with one of: 'today', 'yesterday', 'week', 'last week' or 'season'.\nFor example: <pre>" + command.replace('tfmp','todayfmp').replace('youtht','youthtoday').replace('deptt','depttoday').replace('gyjnt','gyjntoday').replace('tgwt','tgwtoday').replace('membert','membertoday').replace('oevt','oevtoday').replace('ievt','ievtoday').replace('edut','edutoday').replace('svt','svtoday') + "</pre> :)"
            
        if command in ['todayfmp','yesterdayfmp','weekfmp','lastweekfmp','seasonfmp']:
            timerange = command[:-3]
            return pm + SQLCodes.memberfmp(timerange,g,fmp_sid,fmp_ss,access)
            
        if command == 'fmstatus':
            return pm + SQLCodes.fmstatus(d,g,'2020-01-01',access) # date is a dummy variable here
            
        if command == 'bblist':
            return pm + SQLCodes.bblist(d,g,bb_sid,access)
        
        
        if command == 'bblists':
            return pm + SQLCodes.bblists(d,g,phys_sid,on_sid,access)
        
        if command == 'pickfe':
            return pm + SQLCodes.pickfe(g, d, access)
        
        if command in ('bbstatus','bbfull'):
                return pm + SQLCodes.bbstatus(g, d, bb_sid, access)
        
        if command in ('bbstatus2','bbfull2'):
                return pm + SQLCodes.bbstatus(g, d, bb_sid, access, True)
        
        if command.startswith('bbstatusdate'):
            dt = command.removeprefix('bbstatusdate=')
            return pm + SQLCodes.bbstatusdate(g, d, ssn, dt, access)
        
        if command == 'bbactive':
            return pm + SQLCodes.bbactive(g, d, bb_sid, access)
        
        if command == 'bbactive2':
            return pm + SQLCodes.bbactive2(g, d, bb_sid, access)
            
        if command == 'bbinactive':
                return pm + SQLCodes.bbinactive(g, d, bb_sid, access)
            
        if command == 'newbblist':
            return pm + SQLCodes.newbblist(d,g,bb_sid,access)
        
        if command == 'newbbstatus':
                return pm + SQLCodes.newbbstatus(g, d, bb_sid, access)
            
        if (command.startswith('newbtm') or command.startswith('newbbt') or command.startswith('newgyjnbbt')) and command.endswith('list'):
            q = command.removesuffix('list')
            return pm + SQLCodes.newbbtlist(q,d,g,bb_sid,access)
            
        if (command.startswith('newbtm') or command.startswith('newbbt') or command.startswith('newgyjnbbt')) and command.endswith('status'):
            q,i = command.split('status')
            return pm + SQLCodes.newbbtstatus(q,g,d,bb_sid,access)
            
        
        if (command.startswith('btm') or command.startswith('bbt') or command.startswith('gyjnbbt')) and command.endswith('list'):
            q = command.removesuffix('list')
            return pm + SQLCodes.bbtlist(q,d,g,bb_sid,access)
            
        if command != 'bbtbtmstatus' and (command.startswith('btm') or command.startswith('bbt') or command.startswith('gyjnbbt')):
            if command.endswith('status'):
                q = command.removesuffix('status')
                return pm + SQLCodes.bbtstatus(q,g,d,bb_sid,access,False) # returns normal bbtstatus
            if command.endswith('status2'):
                q = command.removesuffix('status2')
                return pm + SQLCodes.bbtstatus(q,g,d,bb_sid,access,False,True) # returns normal bbtstatus2
            if command.endswith('dept'):
                q = command.removesuffix('dept')
                return pm + SQLCodes.bbtstatus(q,g,d,bb_sid,access,True) # returns bbtdept (bbtstatus but without group list)
            if command.endswith('dept2'):
                q = command.removesuffix('dept2')
                return pm + SQLCodes.bbtstatus(q,g,d,bb_sid,access,True,True) # returns bbtdept2 (bbtstatus2 but without group list)
            
        if (command.startswith('btm') or command.startswith('bbt') or command.startswith('gyjnbbt')) and command.endswith('active') and not command.endswith('inactive'):
            q = command.split('active')
            return pm + SQLCodes.bbtactive(q, g, d, r, access)
        
        if (command.startswith('btm') or command.startswith('bbt') or command.startswith('gyjnbbt')) and command.endswith('inactive'):
            q,i = command.split('inactive')
            return pm + SQLCodes.bbtinactive(q, g, d, r, access)
        
        if (command.startswith('deptbtm') or command.startswith('deptbbt') or command.startswith('deptgyjnbbt')) and command.endswith('status'):
            q,i = command.split('status') # removing 'inactive', leaving 'deptbbt' CAN ALSO USE .removesuffix('suffix')!!!!
            i,q = q.split('dept') # removing 'dept', leaving 'bbt' (or 'btm15', 'gyjnbbt' etc.) CAN ALSO USE .removesuffix('suffix')!!!!
            return pm + SQLCodes.deptbbtstatus(q, d, r, access)
        
        if (command.startswith('deptbtm') or command.startswith('deptbbt') or command.startswith('deptgyjnbbt')) and command.endswith('active') and not command.endswith('inactive'):
            if d == 'D[0-9]%' and '/' in user_message:
                i,d = user_message.split('/')
            q,i = command.split('active') # removing 'inactive', leaving 'deptbbt' CAN ALSO USE .removesuffix('suffix')!!!!
            i,q = q.split('dept') # removing 'dept', leaving 'bbt' (or 'btm15', 'gyjnbbt' etc.) CAN ALSO USE .removesuffix('suffix')!!!!
            return pm + SQLCodes.deptbbtactive(q, d, r, access)
        
        if (command.startswith('deptbtm') or command.startswith('deptbbt') or command.startswith('deptgyjnbbt')) and command.endswith('inactive'):
            if d == 'D[0-9]%' and '/' in user_message:
                i,d = user_message.split('/')
            q,i = command.split('inactive') # removing 'inactive', leaving 'deptbbt' CAN ALSO USE .removesuffix('suffix')!!!!
            i,q = q.split('dept') # removing 'dept', leaving 'bbt' (or 'btm15', 'gyjnbbt' etc.) CAN ALSO USE .removesuffix('suffix')!!!!
            return pm + SQLCodes.deptbbtinactive(q, d, r, access)
        
        if command.startswith('secondedu'):
            standard = command.removeprefix('secondedu')
            standard = 'bbt' if standard == '' else standard
            if standard not in ['bbt','leaf','all','']:
                return "must select secondedu (bbt standard), secondeduleaf (leaf standard) or secondeduall (leaf+bbt standard)"
            ct = {'%':'Physical + Online',phys_sid:'Physical',on_sid:'Online'}[bb_sid]
            return pm + SQLCodes.secondedu(g,d,bb_sid,standard,ct,access)
        
        if command == 'classtoday':
            return pm + SQLCodes.classes(g,d,access,'today')
        if command == 'classweek':
            return pm + SQLCodes.classes(g,d,access,'week')
        
        
        
        if command not in ('edutoday','eduyesterday','edulastweek','eduweek','eduseason') and command.startswith('edu'):
            day = command.removeprefix('edu')
            return pm + SQLCodes.edu(day, g, d, access) if day != 'rev' else pm + SQLCodes.edurev(g, d, access)
    
    
    
    
    # Dept and above functions
    if access in ['D[0-9]%','D1','D2','D3','D4','D5','D6','D7','D8','D9','D10','D11','D12','D13','D14','D15','D16','D17','D18','D19','D20','¹D[0-9]%','²D[0-9]%','¹D1','¹D2','¹D3','¹D4','¹D5','¹D6','¹D7','¹D8','¹D9','²D1','²D2','²D3','²D4','²D5','²D6','²D7','²D8','²D9','SFT','Geelong','Dept','M&W Dept','InnerSFT','¹','²','All','IT']:
        
        for task in ['youth','dept','tgw','member','gyjn','oev','iev','edu','sv']:
            if command.startswith(task):
                # Remove the X value from the string
                timerange = command[len(task):]
                # If the rest of the string is a Y value, return X and Y
                if timerange in ['today', 'yesterday', 'week', 'lastweek', 'season']:
                    if task in ['youth','dept','tgw','member']:
                        return pm + SQLCodes.deptfmp(task,timerange,d,fmp_sid,fmp_ss,access)
                    if task in ['gyjn','oev','iev','edu','sv']:
                        return pm + SQLCodes.taskfmp(task,timerange,d,fmp_sid,fmp_ss,access)    
                
        if command in ('youthfm','deptfm'):
            return pm + SQLCodes.youthfm(d)
        if command == 'oldbbactive':
            return pm + SQLCodes.oldbbactive(d)
        if command == 'deptbbactive':
            return pm + SQLCodes.deptbbactive(d, bb_sid, access)
        if command == 'deptbbinactive':
            return pm + SQLCodes.deptbbinactive(d, bb_sid, access)
        
        if command in ['youthmxpx','deptmxpx']:
            return pm + SQLCodes.youthmxpx(d)

        if command == 'febmission':
            return pm + SQLCodes.febmission(access)
        
        if command.startswith('approve'):
            a,userUID,telID,i = command.split('#')
            return pm + SQLCodes.approve_new_user_request(userUID,telID)
        
        if access in ['¹','²','All','IT']:
            if command == 'deptphone':
                return pm + SQLCodes.deptphone(d)

            if command == 'bbtmission':
                return pm + SQLCodes.bbtmission()
            # if command == 'bbtdept':
            #     return pm + SQLCodes.bbtdept(d,bb_sid)
            
            # if access in ('All','IT'):
            #     if command == 'bbtbtmstatus':
            #         return pm + SQLCodes.bbtbtmstatus()
    
    if original_access in ('MT','IT'):
        if command.endswith('absent'):
            if '/' not in user_message:
                return "To avoid long lists, please specify dept with <code>//D#</code> <i>e.g. wedabsent//D3</i>, or group with <code>/G#</code> <i>e.g. sunabsent/G10</i>"
            pm = 'MarkdownV2@@' # This function should always use MarkdownV2 as it contains custom code block labels
            filt, gd = ('Dept', d) if '//' in user_message else ('Grp', g)
            svctype = command.removesuffix('absent')
            return pm + SQLCodes.svcabs(gd,svctype,filt)
        

    if original_access == 'IT':
        
        # Group Functions
        if command == 'todayfish':
            return pm + SQLCodes.todayfish(g)
        if command == 'weekfish':
            return pm + SQLCodes.weekfish(g)
        if command == 'seasonpick':
            return pm + SQLCodes.seasonpick(g) 
        if command == 'seasonfe':
            return pm + SQLCodes.seasonfe(g)
        if command == 'todaympfe':
            return pm + SQLCodes.todaympfe(g)
        if command == 'weekmpfe':
            return pm + SQLCodes.weekmpfe(g)
        if command == 'mxlist':
            return pm + SQLCodes.mxlist(g)
        if command == 'pxlist':
            return pm + SQLCodes.pxlist(g)
        if command == 'bbpick':
            return pm + SQLCodes.bbpick(g)    
        if command == 'bbfe':
            return pm + SQLCodes.bbfe(g)
        if command == 'fmlist':
            return pm + SQLCodes.fmlist(g)

        if (command.startswith('btm') or command.startswith('bbt') or command.startswith('gyjnbbt')) and command.endswith('listold'):
            q,i = command.split('listold')
            return pm + SQLCodes.bbtlistold(q,d)
        
        if command == 'ev':
            i,id = user_message.split('/')
            if access == 'IT':
                return pm + SQLCodes.ev(id)
            if access in ['D[0-9]%','D1','D2','D3','D4','D5','D6','D7','D8','D9','D10','D11','D12','D13','D14','D15','D16','D17','D18','D19','D20','¹D[0-9]%','²D[0-9]%','¹D1','¹D2','¹D3','¹D4','¹D5','¹D6','¹D7','¹D8','¹D9','²D1','²D2','²D3','²D4','²D5','²D6','²D7','²D8','²D9','SFT','Geelong','Dept','M&W Dept','InnerSFT']:
                idlist = SQLCodes.idlist('dept',d)
            if access == 'Group':
                idlist = SQLCodes.idlist('group',g)
            if int(id) in idlist:
                return pm + SQLCodes.ev(id)
            else:
                return 'Sorry, you cannot access this member ID'

    return "Sorry, I don't recognise that command. Please type 'commands' for a list of commands"