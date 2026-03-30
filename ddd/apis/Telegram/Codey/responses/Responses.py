from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from .sqlcodes import SQLCodes

def bot_responses(id, tname, input_text):
    pm = 'HTML@@'

    if input_text.lower().startswith('markdownv2'):
        input_text = input_text[10:].strip()
        print(f'MarkdownV2 detected. New input_text: {input_text}')
        pm = 'MarkdownV2@@'
    elif input_text.lower().startswith('markdown'):
        input_text = input_text[8:].strip()
        print(f'Markdown detected. New input_text: {input_text}')
        pm = 'Markdown@@'

    # === Early returns that DON'T need teledata ===
    if input_text.lower() == 'now':
        melbourne_tz = ZoneInfo("Australia/Melbourne")
        now = datetime.now(melbourne_tz)
        return now.strftime("%a %d %b, %I:%M %p")

    if id == 659275499:
        if input_text == 'Approve: #A0052#659275499#':
            return SQLCodes.approve_new_user_request('A0052', '659275499')
        if input_text.lower() == 'test1niheuigfyedfskj':
            return 'Markdown@@' + SQLCodes.test1()
        if input_text.lower() == 'test2dwuyidhcnekhdfs':
            return 'Markdown@@' + SQLCodes.test2()

    if input_text.lower().startswith('register'):
        i, user, pw = input_text.split('.')
        return SQLCodes.reg_new_user_request(id, tname, user, pw)

    # === Only now do we call teledata ===
    ssn = 'phys'
    uid, name, access, g, d, r, fmp_sid, fmp_ss, bb_sid, bb_ss, phys_sid, on_sid = SQLCodes.teledata(id).split('/')
    original_uid, original_name, original_access = uid, name, access
    print(f"TELEDATA: {uid}/{name}/{d}/{g} -- {access}")

    user_message = str(input_text).lower().replace(' ', '')

    if access == 'IT':
        if '|' in input_text:
            user_message, user_name = input_text.split('|')
            user_message = user_message.lower()
            uid, name, access, g, d, r, fmp_sid, fmp_ss, bb_sid, bb_ss = SQLCodes.namedata(user_name).split('/')
            print(f"USING CODEY AS: {uid}/{name}/{d}/{g} -- {access}")

    if access == 'None':
        return '-'

    if access in ['All', 'IT', 'MT', 'EDU']:
        d = f'D[0-9]%' if access not in ('MT') else '%'
        g = '%' if access in ('MT') else g
        if '//' in user_message:
            try:
                print('//')
                command, d = user_message.split('//')
                d = d.capitalize() if d.startswith('d') else d.replace('sft', 'SFT').replace('inner', 'Inner')
                d = 'D[0-9]%' if d.lower() == 'youth' else d
                d = '%' if d.lower() == 'church' else d
                access = d if access not in ('MT') else access
                print(f"command = {command}, d = {d}, access = {access}")
            except ValueError:
                return 'Format error: Too many "/"s'
        elif '/' in user_message:
            try:
                command, g = user_message.lower().split('/')
                g = g.replace('r1', '¹').replace('r2', '²').replace('g', 'G')
                access = 'Group' if access != 'MT' else 'MT'
            except ValueError:
                return 'Format error: Too many "/"s'
            d, fmp_sid, fmp_ss, bb_sid, bb_ss = SQLCodes.groupinfo(g).split('/')
        else:
            command = user_message

    elif access in ['D[0-9]%','D1','D2','D3','D4','D5','D6','D7','D8','D9','D10','D11','D12','D13','D14','D15','D16','D17','D18','D19','D20','¹D[0-9]%','²D[0-9]%','¹D1','¹D2','¹D3','¹D4','¹D5','¹D6','¹D7','¹D8','¹D9','²D1','²D2','²D3','²D4','²D5','²D6','²D7','²D8','²D9','SFT','Geelong','Dept','M&W Dept','InnerSFT','MT']:
        d = access if access != 'Dept' else d
        if '/' in user_message:
            try:
                command, g = user_message.split('/')
            except ValueError:
                return 'Format error: Too many "/"s'
            # Only call groupinfo and deptgroup when actually needed
            d, fmp_sid, fmp_ss, bb_sid, bb_ss = SQLCodes.groupinfo(g).split('/')
            allowed_groups = SQLCodes.deptgroup(access if access != 'Dept' else d)
            access = 'Group' if access != 'MT' else 'MT'
            if g.lower() not in allowed_groups and user_message.lower()[:3] != 'ev/':
                return 'Sorry, this group is outside your department!'
        else:
            command = user_message

    elif access in ['Group', 'Israel']:
        command = user_message
        if command in ['youthtoday','youthyesterday','youthweek','youthlastweek','youthseason','depttoday','deptyesterday','deptweek','deptlastweek','deptseason','gyjntoday','gyjnyesterday','gyjnweek','gyjnlastweek','gyjnseason','oevtoday','oevyesterday','oevweek','oevlastweek','oevseason','tgwtoday','tgwyesterday','tgwweek','tgwlastweek','tgwseason','bbfull','tolfull','bblastseason','youthmxpx','bbdept']:
            return 'You are not allowed to use this function'
    
    else:
        command = user_message

    SQLCodes.functionlog(original_uid, original_name, input_text, command)

    print(f"""Final parameters before command call:
          UID {original_uid} --> {uid}
          NAME: {original_name} --> {name}
          ACCESS: {original_access} --> {access} //{d} /{g}
          fmp_sid: {fmp_sid} | fmp_ss: {fmp_ss} | bb_sid: {bb_sid} | bb_ss: {bb_ss}
          phys_sid: {phys_sid} | on_sid: {on_sid}""")

    if command.startswith('all'):
        ssn = 'all'
        fmp_sid, bb_sid = '%', '%'
        print(f"""fmp_sid - {fmp_sid}
                   bb_sid - {bb_sid}""")
        command = command[3:]

    if command.startswith('sft'):
        ssn = 'sft'
        fmp_sid, bb_sid = on_sid, on_sid
        print(f"""fmp_sid - {fmp_sid}
                   bb_sid - {bb_sid}""")
        command = command[3:]

    if command.startswith('phys'):
        ssn = 'phys'
        fmp_sid, bb_sid = phys_sid, phys_sid
        print(f"""fmp_sid - {fmp_sid}
                   bb_sid - {bb_sid}""")
        command = command[4:]

    ct = {'%': 'Physical + Online', phys_sid: 'Physical', on_sid: 'Online'}[bb_sid]

    # === Everything below is unchanged ===
    if access != 'MT':
        if 'phonenumber' in str(user_message):
            return "Sorry, 'phonenumber' is not a recognised command. However, to check if someone has been fished before, you may enter their phone number starting with '04' e.g. <pre>0412345678</pre> :)"
        if user_message.startswith('04'):
            return SQLCodes.duplicate_check(user_message)

        if command == 'commands':
            return SQLCodes.commands(access)

        if command in ('tfmp','youtht','deptt','gyjnt','oevt','tgwt','membert','oevt','ievt','edut','svt'):
            return f"Sorry, <i>{command}</i> is not a valid command. Try replacing the 'T' with one of: 'today', 'yesterday', 'week', 'last week' or 'season'.\nFor example: <pre>" + command.replace('tfmp','todayfmp').replace('youtht','youthtoday').replace('deptt','depttoday').replace('gyjnt','gyjntoday').replace('tgwt','tgwtoday').replace('membert','membertoday').replace('oevt','oevtoday').replace('ievt','ievtoday').replace('edut','edutoday').replace('svt','svtoday') + "</pre> :)"

        if command in ['todayfmp','yesterdayfmp','weekfmp','lastweekfmp','seasonfmp']:
            timerange = command[:-3]
            return SQLCodes.memberfmp(timerange, g, fmp_sid, fmp_ss, access)

        if command == 'fmstatus':
            return SQLCodes.fmstatus(d, g, '2020-01-01', access)

        if command == 'bblistold':
            if access in ('All','IT','MT','EDU') and '/' not in user_message:
                return f"To avoid long lists, please specify dept with <code>//D#</code> <i>e.g. {command}//D3</i>, or group with <code>/G#</code> <i>e.g. {command}/G10</i>"
            return SQLCodes.bblistold(d, g, bb_sid, access)

        if command == 'bblistsold':
            if access in ('All','IT','MT','EDU') and '/' not in user_message:
                return f"To avoid long lists, please specify dept with <code>//D#</code> <i>e.g. {command}//D3</i>, or group with <code>/G#</code> <i>e.g. {command}/G10</i>"
            return SQLCodes.bblistsold(d, g, phys_sid, on_sid, access)

        if command == 'bblist':
            if access in ('All','IT','MT','EDU') and '/' not in user_message:
                return f"To avoid long lists, please specify dept with <code>//D#</code> <i>e.g. {command}//D3</i>, or group with <code>/G#</code> <i>e.g. {command}/G10</i>"
            return SQLCodes.bblist(d, g, bb_sid, access)

        if command == 'bblists':
            if access in ('All','IT','MT','EDU') and '/' not in user_message:
                return f"To avoid long lists, please specify dept with <code>//D#</code> <i>e.g. {command}//D3</i>, or group with <code>/G#</code> <i>e.g. {command}/G10</i>"
            return SQLCodes.bblists(d, g, phys_sid, on_sid, access)

        if command == 'pickfe':
            return SQLCodes.pickfe(g, d, access)

        if command in ('bbstatus','bbfull'):
            return SQLCodes.bbstatus(g, d, bb_sid, access)

        if command in ('bbstatus2','bbfull2'):
            return SQLCodes.bbstatus(g, d, bb_sid, access, True)

        if command.startswith('bbstatusdate'):
            dt = command.removeprefix('bbstatusdate=')
            return SQLCodes.bbstatusdate(g, d, ssn, dt, access)

        if command == 'bbactive':
            return SQLCodes.bbactive(g, d, bb_sid, access)

        if command == 'bbactive2':
            return SQLCodes.bbactive2(g, d, bb_sid, access)

        if command == 'bbinactive':
            return SQLCodes.bbinactive(g, d, bb_sid, access)

        if command == 'bblistfe':
            if access in ('All','IT','MT','EDU') and '/' not in user_message:
                return f"To avoid long lists, please specify dept with <code>//D#</code> <i>e.g. {command}//D3</i>, or group with <code>/G#</code> <i>e.g. {command}/G10</i>"
            return SQLCodes.bblistfe(d, g, bb_sid, access)

        if command == 'newbbstatus':
            return SQLCodes.newbbstatus(g, d, bb_sid, access)

        if (command.startswith('newbtm') or command.startswith('newbbt') or command.startswith('newgyjnbbt')) and command.endswith('listubb'):
            q = command.removesuffix('listubb')
            if access in ('All','IT','MT','EDU') and '/' not in user_message:
                return f"To avoid long lists, please specify dept with <code>//D#</code> <i>e.g. {command}//D3</i>, or group with <code>/G#</code> <i>e.g. {command}/G10</i>"
            return SQLCodes.bbtlistubb(q, d, g, bb_sid, access)

        if (command.startswith('newbtm') or command.startswith('newbbt') or command.startswith('newgyjnbbt')) and command.endswith('status'):
            q, i = command.split('status')
            return SQLCodes.newbbtstatus(q, g, d, bb_sid, access)

        if (command.startswith('btm') or command.startswith('bbt') or command.startswith('gyjnbbt') or command.startswith('prebbt')) and command.endswith('list'):
            q = command.removesuffix('list')
            if access in ('All','IT','MT','EDU') and '/' not in user_message:
                return f"To avoid long lists, please specify dept with <code>//D#</code> <i>e.g. {command}//D3</i>, or group with <code>/G#</code> <i>e.g. {command}/G10</i>"
            return SQLCodes.bbtlist(q, d, g, bb_sid, access)

        if (command.startswith('btm') or command.startswith('bbt') or command.startswith('gyjnbbt') or command.startswith('prebbt')) and command.endswith('listold'):
            q = command.removesuffix('listold')
            if access in ('All','IT','MT','EDU') and '/' not in user_message:
                return f"To avoid long lists, please specify dept with <code>//D#</code> <i>e.g. {command}//D3</i>, or group with <code>/G#</code> <i>e.g. {command}/G10</i>"
            return SQLCodes.bbtlistold(q, d, g, bb_sid, access)

        if command != 'bbtbtmstatus' and (command.startswith('btm') or command.startswith('bbt') or command.startswith('gyjnbbt') or command.startswith('prebbt')):
            if command.endswith('status'):
                q = command.removesuffix('status')
                return SQLCodes.bbtstatus(q, g, d, bb_sid, access, False)
            if command.endswith('status2'):
                q = command.removesuffix('status2')
                return SQLCodes.bbtstatus(q, g, d, bb_sid, access, False, True)
            if command.endswith('dept'):
                q = command.removesuffix('dept')
                return SQLCodes.bbtstatus(q, g, d, bb_sid, access, True)
            if command.endswith('dept2'):
                q = command.removesuffix('dept2')
                return SQLCodes.bbtstatus(q, g, d, bb_sid, access, True, True)

        if (command.startswith('btm') or command.startswith('bbt') or command.startswith('gyjnbbt')) and command.endswith('active') and not command.endswith('inactive'):
            q = command.split('active')
            return SQLCodes.bbtactive(q, g, d, r, access)

        if (command.startswith('btm') or command.startswith('bbt') or command.startswith('gyjnbbt')) and command.endswith('inactive'):
            q, i = command.split('inactive')
            return SQLCodes.bbtinactive(q, g, d, r, access)

        if (command.startswith('deptbtm') or command.startswith('deptbbt') or command.startswith('deptgyjnbbt')) and command.endswith('status'):
            q, i = command.split('status')
            i, q = q.split('dept')
            return SQLCodes.deptbbtstatus(q, d, r, access)

        if (command.startswith('deptbtm') or command.startswith('deptbbt') or command.startswith('deptgyjnbbt')) and command.endswith('active') and not command.endswith('inactive'):
            if d == 'D[0-9]%' and '/' in user_message:
                i, d = user_message.split('/')
            q, i = command.split('active')
            i, q = q.split('dept')
            return SQLCodes.deptbbtactive(q, d, r, access)

        if (command.startswith('deptbtm') or command.startswith('deptbbt') or command.startswith('deptgyjnbbt')) and command.endswith('inactive'):
            if d == 'D[0-9]%' and '/' in user_message:
                i, d = user_message.split('/')
            q, i = command.split('inactive')
            i, q = q.split('dept')
            return SQLCodes.deptbbtinactive(q, d, r, access)

        if command.startswith('secondedu'):
            standard = command.removeprefix('secondedu')
            standard = 'leaf' if standard == '' else standard
            if standard not in ['bbt','leaf','all','']:
                return "must select secondedu (leaf standard), secondedubbt (bbt standard) or secondeduall (leaf+bbt standard)"
            return SQLCodes.secondedu(g, d, bb_sid, standard, ct, access)

        if command == 'classtoday':
            return SQLCodes.classes(g, d, access, 'today')
        if command == 'classweek':
            return SQLCodes.classes(g, d, access, 'week')

        if command not in ('edutoday','eduyesterday','edulastweek','eduweek','eduseason') and command.startswith('edu'):
            day = command.removeprefix('edu')
            return SQLCodes.edu(day, g, d, access) if day != 'rev' else SQLCodes.edurev(g, d, access)

        if command == 'hspreport':
            return SQLCodes.hspreport(g, d, access)

        if command == 'bbtmission':
            d = '%' if access == 'EDU' else d
            return SQLCodes.bbtmission(bb_sid, d, g, 'se', ct, access)

        if command == 'bbtmissionpick':
            d = '%' if access == 'EDU' else d
            return SQLCodes.bbtmission(bb_sid, d, g, 'pick', ct, access)

        if command == 'bmt':
            d = '%' if access == 'EDU' else d
            return SQLCodes.bbtmission(bb_sid, d, g, 'tie', ct, access)

    # Dept and above functions
    if access in ['%','D[0-9]%','D1','D2','D3','D4','D5','D6','D7','D8','D9','D10','D11','D12','D13','D14','D15','D16','D17','D18','D19','D20','¹D[0-9]%','²D[0-9]%','¹D1','¹D2','¹D3','¹D4','¹D5','¹D6','¹D7','¹D8','¹D9','²D1','²D2','²D3','²D4','²D5','²D6','²D7','²D8','²D9','SFT','Geelong','Dept','M&W Dept','InnerSFT','¹','²','All','EDU','IT']:

        for task in ['youth','dept','tgw','member','gyjn','oev','iev','edu','sv']:
            if command.startswith(task):
                timerange = command[len(task):]
                if timerange in ['today','yesterday','week','lastweek','season']:
                    if task in ['youth','dept','tgw','member']:
                        return SQLCodes.deptfmp(task, timerange, d, fmp_sid, fmp_ss, access)
                    if task in ['gyjn','oev','iev','edu','sv']:
                        return SQLCodes.taskfmp(task, timerange, d, fmp_sid, fmp_ss, access)

        if command in ('youthfm','deptfm'):
            return SQLCodes.youthfm(d)
        if command == 'oldbbactive':
            return SQLCodes.oldbbactive(d)
        if command == 'deptbbactive':
            return SQLCodes.deptbbactive(d, bb_sid, access)
        if command == 'deptbbinactive':
            return SQLCodes.deptbbinactive(d, bb_sid, access)

        if command in ['youthmxpx','deptmxpx']:
            return SQLCodes.youthmxpx(d)

        if command == 'aprilmission':
            return SQLCodes.aprilmission(access)

        if command == 'aprilbbtmission':
            return SQLCodes.aprilbbtmission(access)

        if command.startswith('approve'):
            a, userUID, telID, i = command.split('#')
            return SQLCodes.approve_new_user_request(userUID, telID)

        if original_access in ['¹','²','All','EDU','IT']:
            if command == 'deptphone':
                return SQLCodes.deptphone(d)

    if original_access in ('MT','IT'):
        if command.endswith('svcabsent'):
            if '/' not in user_message:
                return "To avoid long lists, please specify dept with <code>//D#</code> <i>e.g. wedsvcabsent//D3</i>, or group with <code>/G#</code> <i>e.g. sunabsent/G10</i>"
            pm = 'MarkdownV2@@'
            filt, gd = ('Dept', d) if '//' in user_message else ('Grp', g)
            svctype = command.removesuffix('svcabsent')
            return f'{pm}{SQLCodes.svcabs(gd, svctype, filt)}'

    if original_access in ('EDU','IT'):
        if command.endswith('eduabsent'):
            if '/' not in user_message:
                return "To avoid long lists, please specify dept with <code>//D#</code> <i>e.g. moneduabsent//D3</i>, or group with <code>/G#</code> <i>e.g. moneduabsent/G10</i>"
            pm = 'MarkdownV2@@'
            filt, gd = ('Dept', d) if '//' in user_message else ('Grp', g)
            edutype = command.removesuffix('eduabsent')
            return f'{pm}{SQLCodes.eduabs(gd, edutype, filt)}'

    if original_access == 'IT':
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

        if command == 'ev':
            i, id = user_message.split('/')
            if access == 'IT':
                return SQLCodes.ev(id)
            if access in ['D[0-9]%','D1','D2','D3','D4','D5','D6','D7','D8','D9','D10','D11','D12','D13','D14','D15','D16','D17','D18','D19','D20','¹D[0-9]%','²D[0-9]%','¹D1','¹D2','¹D3','¹D4','¹D5','¹D6','¹D7','¹D8','¹D9','²D1','²D2','²D3','²D4','²D5','²D6','²D7','²D8','²D9','SFT','Geelong','Dept','M&W Dept','InnerSFT']:
                idlist = SQLCodes.idlist('dept', d)
            if access == 'Group':
                idlist = SQLCodes.idlist('group', g)
            if int(id) in idlist:
                return SQLCodes.ev(id)
            else:
                return 'Sorry, you cannot access this member ID'

    return "Sorry, I don't recognise that command. Please type 'commands' for a list of commands"