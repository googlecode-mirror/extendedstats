from extendedstats.extendedstats import \
dcfg,\
newconnected,\
dbg,pending,\
players,\
weapons,\
sid,\
updateTimes,\
db
import es, time, gamethread, vecmath

def load():
    dbg('XS: loading dod events...')

def server_cvar(ev):
    if ev['cvarname'] in dcfg.cvars():
        dcfg[ev['cvarname'][3:]] = ev['cvarvalue']
        
def player_connect(ev):
    newconnected.append(ev['userid'])

def player_spawn(ev):
    dbg('player_spawn')
    if not es.isbot(ev['userid']):
        steamid = es.getplayersteamid(ev['userid'])
        if not steamid:
            dbg('NO STEAM ID!!!')
            return
        if steamid == 'STEAM_ID_PENDING':
            dbg('STEAM_ID_PENDING')
            gamethread.delayedname(1, 'xs_delayed_%s' % ev['userid'], pendingCheck, kw={userid:ev['userid']})
            pending.append(ev['userid']) 
            return
        if not ev['userid'] in newconnected:
            return
        if not steamid in players:
            players.newplayer(steamid)
        if not steamid in toplist:
            toplist.newplayer(steamid)
        players.increment(steamid,'sessions')
        players.update(steamid,'sessionstart',time.time())
        players.update(steamid,'lastseen',time.time())
        players.update(steamid,'teamchange_time',time.time())
        newname = es.getplayername(ev['userid'])
        players.name(steamid,newname)
        newconnected.remove(ev['userid'])
        if ev['userid'] in pending:
            pending.remove(ev['userid'])
        dbg('player spawned: %s' % steamid)

def player_disconnect(ev):
    if ev['userid'] in newconnected:
        newconnected.remove(ev['userid'])
        if ev['userid'] in pending:
            pending.remove(ev['userid'])
        return
    if not es.isbot(ev['userid']):
        dbg( 'player disconnected: %s' % ev['userid'])
        dbg( 'finnishing player session')
        steamid = ev['networkid']
        if not steamid in players:
            return
        players.update(steamid,'lastseen',time.time())
        players.add(steamid,'time',time.time() - players.query(steamid,'sessionstart'))
        cteam = players.query(steamid,'current_team')
        if not str(cteam) == '0':
            players.add(steamid,'team_' + str(cteam) + '_time',time.time() - players.query(steamid,'teamchange_time'))
        players.update(steamid,'teamchange_time',time.time())
        players.update(steamid,'current_team',0)
        for method in methods.keys():
            toplist.update(steamid,method,methods[method](players,steamid))

def player_changename(ev):
    if not es.isbot(ev['userid']):
        dbg( 'player changed name')
        steamid = sid(ev)
        newname = ev['newname']
        players.name(steamid,newname)

def player_death(ev):
    dbg(' ')
    victimIsBot = bool(es.isbot(ev['userid']))
    victimSteamid = ev['es_steamid']
    victimTeam = ev['es_userteam']
    attackerIsBot = bool(es.isbot(ev['attacker']))
    attackerSteamid = ev['es_attackersteamid']
    attackerTeam = ev['es_attackerteam']
    wasTeamKill = True if attackerTeam == victimTeam else False
    isHeadshot = True if ev['headshot'] == '1' else False
    weapon = ev['weapon']
    dbg('player_death')
    dbg('victim: %s (%s)' % (victimSteamid,victimIsBot))
    dbg('attacker: %s (%s)' % (attackerSteamid,attackerIsBot))
    dbg('teamkill: %s (%s,%s)' % (wasTeamKill,victimTeam,attackerTeam))
    dbg('headshot: %s (%s)' % (isHeadshot,ev['headshot']))
    dbg('weapon: %s' % weapon)
    if weapon in weapons:
        weapons.increment(weapon,'kills')
    if wasTeamKill:
        dbg( 'teamkill')
        if not victimIsBot:
            players.increment(victimSteamid,'teamkilled')
        if not attackerIsBot:
            players.increment(attackerSteamid,'teamkills')
    else:
        dbg( 'kill')
        if not victimIsBot:
            players.increment(victimSteamid,'deaths')
        if not attackerIsBot:
            players.increment(attackerSteamid,'kills')
    if not victimIsBot:
        dbg( 'weapon stats (death)')
        if 'death_%s' % weapon in players.columns:
            players.increment(victimSteamid,'death_%s' % weapon)
        else:
            dbg('Custom weapon, not in database...')
    if not attackerIsBot:
        dbg( 'weapon stats (kill)')
        if 'kill_%s' % weapon in players.columns:
            players.increment(attackerSteamid,'kill_%s' % weapon)
        else:
            dbg('Custom weapon, not in database...')
        if isHeadshot:
            players.increment(attackerSteamid,'headshots')

#    "player_death"        // a game event, name may be 32 charaters long
#    {
#        // this extends the original player_death 
#        "userid"    "short"       // user ID who died                
#        "attacker"    "short"         // user ID who killed
#        "weapon"    "string"     // weapon name killer used 
#        "weaponid"    "short"        // ID of weapon killed used
#        "damagebits"    "long"        // bits of type of damage
#        "customkill"    "short"        // type of custom kill
#        "assister"    "short"        // user ID of assister
#        "dominated"    "short"        // did killer dominate victim with this kill
#        "assister_dominated" "short"    // did assister dominate victim with this kill
#        "revenge"    "short"        // did killer get revenge on victim with this kill
#        "assister_revenge" "short"    // did assister get revenge on victim with this kill
#        "weapon_logclassname"    "string"     // weapon name that should be printed on the log
#    }
    
def player_falldamage(ev):
    if not es.isbot(ev['userid']):
        dbg( 'falldamage')
        players.add(sid(ev),'falldamage',float(ev['damage']))

def player_hurt(ev):
    victim = ev['es_steamid']
    attacker = ev['es_attackersteamid']
    weapon = ev['weapon']
    damage = int(ev['damage'])
    if weapon in weapons:
        weapons.add(weapon,'damage',float(damage))
    if not es.isbot(ev['userid']):
        dbg( 'player hurt')
        players.increment(victim,'hurt')
        players.add(victim,'hurt_damage',damage)
    if not es.isbot(ev['attacker']) and bool(int(ev['attacker'])):
        dbg( 'player hurted')
        players.increment(attacker,'attacked')
        players.add(attacker,'attacked_damage',damage)
        if 'damage_%s' % weapon in players.columns:
            players.add(attacker,'damage_%s' % weapon,damage)

def player_jump(ev):
    if not es.isbot(ev['userid']):
        dbg( 'player jumped')
        steamid = sid(ev)
        players.increment(steamid,'jump')
        vStartpos = vecmath.vector(es.getplayerlocation(ev['userid']))
        players.update(steamid,'jump_startpos',str(vStartpos))

def player_radio(ev):
    if not es.isbot(ev['userid']):
        dbg( 'player radiomsg')
        players.increment(sid(ev),'radio')

def player_team(ev):
    if not es.isbot(ev['userid']):
        dbg( 'player_team')
        steamid = sid(ev)
        if steamid:
            ot = ev['oldteam']
            nt = ev['team']
            if ot in ['1','0'] and nt in ['2','3']:
                dbg( 'spec to play')
                players.add(steamid,'team_1_time',time.time() - players.query(steamid,'teamchange_time'))
                players.update(steamid,'teamchange_time',time.time())
            if ot in ['2','3'] and nt in ['1','0']:
                dbg( 'play to spec')
                players.add(steamid,'team_%s_time' % ot,time.time() - players.query(steamid,'teamchange_time'))
                players.update(steamid,'teamchange_time',time.time())
            if ot in ['2','3'] and ot != nt:
                dbg( 'teamswitch')
                players.add(steamid,'team_%s_time' % ot,time.time() - players.query(steamid,'teamchange_time'))
                players.update(steamid,'teamchange_time',time.time())
            players.update(steamid,'current_team',nt)
        else:
            dbg( 'disconnected')

def server_addban(ev):
    if not es.isbot(ev['userid']):
        dbg( 'addban')
        if ev['networkid'] in players:
            players.increment(ev['networkid'],'ban')

def player_changeclass(ev):
    dbg( 'player changed class')
    dbg( ev['class'])
    pass

def dod_capture_blocked(ev):
    if not es.isbot(ev['userid']):
        dbg( 'capture blocked')
        players.increment(sid(ev),'dod_blocks')

def dod_round_win(ev):
    wt,lt = 'ct','t'
    dbg( 'round won')
    if ev['team'] == '2':
        wt,lt = lt,wt
    for userid in playerlib.getUseridList('#human,#%s' % wt):
        players.increment(es.getplayersteamid(userid),'win')
    for userid in playerlib.getUseridList('#human,#%s' % lt):
        players.increment(es.getplayersteamid(userid),'lose')
    dcfg.sync()
    updateTimes()
    db.commit()

def dod_bomb_exploded(ev):
    if not es.isbot(ev['userid']):
        dbg( 'bomb exploded')
        players.increment(sid(ev),'bomb_exploded')

def dod_bomb_defused(ev):
    if not es.isbot(ev['userid']):
        dbg( 'bomb defused')
        players.increment(sid(ev),'bomb_defused')
    
def es_map_start(ev):
    dcfg.sync()