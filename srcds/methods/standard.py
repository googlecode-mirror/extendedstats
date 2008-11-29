from extendedstats import extendedstats
import path, es, time

packagename = 'standard'

def load():
    extendedstats.registerMethod(packagename,'kdr',KDR)
    extendedstats.registerMethod(packagename,'kills',PureKills)
    extendedstats.registerMethod(packagename,'deaths',PureDeaths)
    extendedstats.registerMethod(packagename,'team_kdr',tKDR)
    extendedstats.registerMethod(packagename,'killsperminute',kpm)
    if extendedstats.addonIsLoaded('extendedevents') and extendedstats.game == 'cstrike':
        extendedstats.registerMethod(packagename,'money',money)
        extendedstats.registerMethod(packagename,'score',score)
    extendedstats.registerMethod(packagename,'damage',damage)
    
def KDR(players,steamid):
    dbg = extendedstats.dbg
    dbg('kdr calculation...')
    deaths = players.query(steamid,'deaths')
    dbg('deaths: %s' % deaths)
    kills = players.query(steamid,'kills')
    dbg('kills: %s' % kills)
    if deaths == 0:
        deaths = 1.0
        dbg('deaths are 0, setting 1.0')
        if kills == 0:
            dbg('kills are 0, returning 1.0')
            return 1.0
    kdr = float(kills) / float(deaths)
    dbg('kdr: %s (%s kills, %s deaths)' % (kdr,kills,deaths))
    return kdr
    
def PureKills(players,steamid):
    # Probably the easiest you can do
    return players.query(steamid,'kills')

def PureDeaths(players,steamid):
    return players.query(steamid,'deaths')
    
def kpm(players,steamid):
    # time is a float in seconds
    minutes = (players.query(steamid,'time') + time.time() - players.query(steamid,'sessionstart')) / 60.0
    if minutes == 0.0:
        minutes = 1.0
    return float(players.query(steamid,'kills')) / minutes

def tKDR(players,steamid):
    deaths = float(players.query(steamid,'deaths'))
    tkilled = float(players.query(steamid,'teamkilled'))
    if deaths - tkilled < 0:
        dtk = deaths -  tkilled
        dtk *= -1.0
        deaths = 1.0 / dtk
    elif deaths - tkilled > 0:
        deaths = deaths - tkilled
    else:
        deaths = 1.0
    return (float(players.query(steamid,'kills')) - float(players.query(steamid,'teamkills'))) / deaths

def score(players,steamid):
    hostages = players.query(steamid,'hostage_rescued') * 2 + players.query(steamid,'hostage_follows') - players.query(steamid,'hostage_hurt') - players.query(steamid,'hostage_killed') * 2 
    kills = players.query(steamid,'kills') + players.query(steamid,'teamkilled') - players.query(steamid,'deaths') - players.query(steamid,'teamkills') * 2 + players.query(steamid,'headshots')
    win = players.query(steamid,'win') - players.query(steamid,'lose')
    return hostages + kills + win

def money(players,steamid):
    return players.query(steamid,'money')

def damage(players,steamid):
    return players.query(steamid,'attacked_damage')
