# Default eXtended Stats new_player for version 0.0.5:80
from extendedstats import extendedstats # Import eXtended Stats
import es, time

# This dict will be used to fill new players with default keys->values to prevent key not found errors.
new_player = {
    'bomb_defused': 0,
    'bomb_dropped': 0,
    'bomb_exploded': 0,
    'bomb_pickup': 0,
    'flashbang_detonate': 0,
    'hegrenade_detonate': 0,
    'hostage_follows': 0,
    'hostage_hurt': 0,
    # 'hostage_hurt_damage': 0, moved to EE4?
    'hostage_killed': 0,
    'hostage_rescued': 0,
    'hostage_stops_following': 0,
    'weapons_picked_up':{},
    'sessions': 0,
    'sessionstart': None,
    'time': 0,
    'changename': 0,
    'kills': 0,
    'kill_weapons': {},
    'deaths': 0,
    'death_weapons': {},
    'teamkills': 0,
    'teamkilled': 0,
    'headshots': 0,
    'lastseen': 0,
    'falldamage': 0.0,
    'hurt': 0,
    'attacked': 0,
    'hurt_damage': 0,
    'attacked_damage': 0,
    'jump': 0,
    'radio': 0,
    'team_1_time': 0,
    'team_2_time': 0,
    'team_3_time': 0,
    'teamchange_time': None,
    'current_team': '0',
    'win': 0,
    'lose': 0,
    'rounds': 0,
    'ban': 0,
    'smokegrenade_detonate': 0,
    'vip_escaped': 0,
    'vip_killed': 0,
    'vip_died': 0,
    'dod_sniper': 0,
    'dod_rifleman': 0,
    'dod_assault': 0,
    'dod_support': 0,
    'dod_rocket': 0,
    'dod_mg': 0,
    'dod_blocks': 0,
    'lastname': '',
    'names': {},
    'settings':{
        'method': None,
        'name': None,
    },
}

def load():
    extendedstats.registerLiveKey('time',liveTime)
    extendedstats.registerIgnoreKey('sessionstart')
    extendedstats.registerIgnoreKey('teamchange_time')
    extendedstats.registerIgnoreKey('current_team')
    extendedstats.registerIgnoreKey('settings')
    extendedstats.registerLiveKey('team_2_time',liveTeam2)
    extendedstats.registerLiveKey('team_3_time',liveTeam3)
    extendedstats.registerLiveKey('team_1_time',liveSpec)
        
def liveTime(player):
    return extendedstats.data[player]['time'] + time.time() - extendedstats.data[player]['sessionstart']
    
def liveTeam2(player):
    if es.getplayerteam(es.getuserid(player)) != 2:
        return extendedstats.data[player]['team_2_time']
    if not extendedstats.data[player]['teamchange_time'] and not extendedstats.data[player]['sessionstart']:
        return extendedstats.data[player]['team_2_time']
    if not extendedstats.data[player]['teamchange_time']:
        return extendedstats.data[player]['team_2_time'] + time.time() - extendedstats.data[player]['sessionstart']
    return extendedstats.data[player]['team_2_time'] + time.time() - extendedstats.data[player]['teamchange_time']

def liveTeam3(player):
    if es.getplayerteam(es.getuserid(player)) != 3:
        return extendedstats.data[player]['team_3_time']
    if not extendedstats.data[player]['teamchange_time'] and not extendedstats.data[player]['sessionstart']:
        return extendedstats.data[player]['team_3_time']
    if not extendedstats.data[player]['teamchange_time']:
        return extendedstats.data[player]['team_3_time'] + time.time() - extendedstats.data[player]['sessionstart']
    return extendedstats.data[player]['team_3_time'] + time.time() - extendedstats.data[player]['teamchange_time']

def liveSpec(player):
    if es.getplayerteam(es.getuserid(player)) not in [0,1]:
        return extendedstats.data[player]['team_1_time']
    if not extendedstats.data[player]['teamchange_time'] and not extendedstats.data[player]['sessionstart']:
        return extendedstats.data[player]['team_1_time']
    if not extendedstats.data[player]['teamchange_time']:
        return extendedstats.data[player]['team_1_time'] + time.time() - extendedstats.data[player]['sessionstart']
    return extendedstats.data[player]['team_1_time'] + time.time() - extendedstats.data[player]['teamchange_time']
