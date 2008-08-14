# eXtendedStats default modules for Version 0.0.1:13

# You have to import extendedstats to register your methods
from extendedstats import extendedstats
import path, es

packagename = 'default'

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
    
# This simple example shows how to build you methods
# IMPORTANT: All methods are called with a dictionary full of information about the player
# The dict's values are floats by default, just in some rare cases they're strings
# You can find a full list of keys on http://extendedstats.ojii.ch/?site=keylist
def KDR(player):
    # The following three lines are VERY IMPORTANT: Zero Division Prevention!
    deaths = 1 # We set a new variable called deaths to 1
    if player['deaths'] > 0: # If the player has died at least once
        deaths = player['deaths'] # We can set the deaths variable to the actual value
    return float(player['kills']) / float(deaths) # This all is done because we divide by deaths. Prevent your method from dividing by zero!
    
def PureKills(player):
    # Probably the easiest you can do
    return player['kills']

def PureDeaths(player):
    return player['deaths']
    
def kpm(player):
    # time is a float in seconds
    minutes = player['time'] / 60
    return player['kills'] / minutes

def tKDR(player):
    deaths = 1
    if player['deaths'] - player['teamkilled'] < 0:
        deaths = 1 / (player['deaths'] - player['teamkilled']) * -1
    elif player['deaths'] - player['teamkilled'] > 0:
        deaths = player['deaths'] - player['teamkilled']
    return (player['kills']-player['teamkills']) / deaths

def score(player):
    hostages = player['hostage_rescued'] * 2 + player['hostage_follows'] - player['hostage_hurt'] - player['hostage_killed'] * 2 
    kills = player['kills'] + player['teamkilled'] - player['deaths'] - player['teamkills'] * 2 + player['headshots']
    win = player['win'] - player['lose']
    return hostages + kills + win

def money(player):
    return player['money'] 

def damage(player):
    return player['attacked_damage']
