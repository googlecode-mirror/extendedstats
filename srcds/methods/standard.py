# eXtendedStats default modules for Version 0.0.1:13

# You have to import extendedstats to register your methods
from extendedstats import extendedstats
import path, es, time

packagename = 'standard'

# This function will be called when your method is imported.
def load():
    # To register a method, call the registerMethod() function of extendedstats
    # The first parameter is the filename of your packages, in this case default (without .py)
    # The second parameter is the name you want to give you method. Unlike this examples, try to choose something unique
    # The last parameter is the function which shall be called in your script to calculate the score
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
    # The following three lines are VERY IMPORTANT: Zero Division Prevention!
    deaths = players.query(steamid,'deaths') # We set a new variable called deaths to 1
    if deaths == 0: # If the player has died at least once
        deaths = 1.0 # We can set the deaths variable to the actual value
    return float(players.query(steamid,'kills')) / float(deaths) # This all is done because we divide by deaths. Prevent your method from dividing by zero!
    
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
