from extendedstats import extendedstats
import path, es

packagename = 'strange'

def load():
    if extendedstats.addonIsLoaded('extendedevents'):
        extendedstats.registerMethod(packagename,'jumpdistance',jumpdistance)
        extendedstats.registerMethod(packagename,'longestjump',longestjump)
    extendedstats.registerMethod(packagename,'falldamage',falldamage)
    
def jumpdistance(players,steamid):
    return float('%.2f'% (players.query(steamid,'jump_distance')*0.01905))

def longestjump(players,steamid):
    return players.query(steamid,'jump_longest')*0.01905

def falldamage(players,steamid):
    return players.query(steamid,'falldamage')
