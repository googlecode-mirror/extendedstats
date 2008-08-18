# ExtendedEvents eXtended Stats Addon version 1.5 by Ojii
# Compatible with ExtendedEvents 4

from extendedstats import extendedstats
import es, vecmath, path

EE = extendedstats.addonIsLoaded('extendedevents')
if EE:
    colums = [
        ('money','INTEGER DEFAULT 0'),
        ('jump_distance','REAL DEFAULT 0.0'),
        ('jump_longest','INTEGER DEFAULT 0'),
    ]
    wcolumns = None
    if extendedstats.game == 'dod':
        columns += [('dod_captures','INTEGER DEFAULT 0')]
    elif extendedstats.game == 'cstrike':
        wcolumns = map(lambda x: ('bought_%s' % x,'INTEGER DEFAULT 0'),extendedstats.cstrike_weapons)
    if wcolumns:
        extendedstats.weapons.addColumns(wcolumns)
    default = {
        'notify_longestjump':'1',
        'notify_longestjump_all': '0',
    }
    extendedstats.players.addColumns(columns)
    dcfg = extendedstats.addonDynCfg('extendedevents',default)

def load():
    if EE:
        extendedstats.dbg( 'XS:EE: Registering extendedevents events')
        extendedstats.registerEvent('extendedevents','player_land',player_land)
        extendedstats.registerEvent('extendedevents','player_money',player_money)
        extendedstats.registerEvent('extendedevents','weapon_purchase',weapon_purchase)
    else:
        extendedstats.dbg( 'XS:EE: No extendedevents files found')

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

def player_money(ev):
    if not es.isbot(ev['userid']):
        extendedstats.dbg( 'player money')
        extendedstats.players.add(extendedstats.sid(ev),'money',int(ev['change_amount']))
        
def weapon_purchase(ev):
    if not es.isbot(ev['userid']):
        extendedstats.dbg( 'weapon purchase')
        steamid = extendedstats.sid(ev)
        weapon = ev['weapon']
        extendedstats.weapons.increment(steamid,'%s_bought' % weapon)
