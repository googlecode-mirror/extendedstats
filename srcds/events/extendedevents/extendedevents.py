import es, vecmath
from extendedstats import extendedstats

default = {
    'notify_longestjump':'1',
    'notify_longestjump_all': '0',
}
dcfg = extendedstats.addonDynCfg('extendedevents',default)

def load():
    extendedstats.dbg('XS: loading extendedevents events...')

def player_land(ev):
    if not es.isbot(ev['userid']):
        data = extendedstats.data
        steamid = extendedstats.sid(ev)
        extendedstats.dbg('player land')
        pos = vecmath.vector(es.getplayerlocation(ev['userid']))
        startpos = extendedstats.players.query(steamid,'jump_startpos')
        if startpos:
            distance = vecmath.distance(pos, vecmath.vector(startpos))
            extendedstats.players.add(steamid,'jump_distance',distance)
            if distance > extendedstats.players.query(steamid,'jump_longest'):
                extendedstats.players.update(steamid,'jump_longest',distance)
                if dcfg['notify_longestjump'] == '1':
                    name = extendedstats.getName(steamid)
                    rank,allplayers = extendedstats.getRank(steamid,'jump_longest')
                    rSteamid, rDistance = extendedstats.getToplist(1,'jump_longest')[0]
                    rName = extendedstats.getName(rSteamid)
                    if dcfg['notify_longestjump_all'] == '1':
                        es.msg('%s just broke his record of his longest jump. His new record is: %.2f meters!' % (name,distance*0.01905))
                        es.msg('He is ranked %s of %s now. Longest jump overall is %.2f meters by %s' % (rank,allplayers,rDistance,rName))
                    else:
                        es.tell(ev['userid'],'You just broke your record of your longest jump! Your new record is: %.2f meters!' % (distance*0.01905))
                        es.tell(ev['userid'],'You are now ranked %s of %s. Longest jump overall is %.2f meters by %s' % (rank,allplayers,rDistance,rName))
            extendedstats.players.update(steamid,'jump_startpos',None) 

def player_money(ev):
    if not es.isbot(ev['userid']):
        extendedstats.dbg( 'player money')
        extendedstats.players.add(extendedstats.sid(ev),'money',int(ev['change_amount']))
        
def weapon_purchase(ev):
    if not es.isbot(ev['userid']):
        extendedstats.dbg( 'weapon purchase')
        steamid = extendedstats.sid(ev)
        weapon = ev['weapon']
        if 'bought_%s' in extendedstats.players.columns:
            extendedstats.players.increment(steamid,'bought_%s' % weapon)
            extendedstats.weapons.increment(weapon,'bought')
        else:
            extendedstats.dbg('custom weapon, not in database...')

def dod_flag_captured(ev):
    for userid in ev['cappers'].split(','):
        steamid = es.getplayersteamid(userid)
        extendedstats.players.increase(increment,'dod_captures')