from extendedstats import extendedstats
import path, es

packagename = 'strange'

def load():
    if extendedstats.addonIsLoaded('extendedevents'):
        extendedstats.registerMethod(packagename,'jumpdistance',jumpdistance)
        extendedstats.registerMethod(packagename,'longestjump',longestjump)
    extendedstats.registerMethod(packagename,'falldamage',falldamage)
    
def jumpdistance(player):
    return float('%.2f'% (player['jump_distance']*0.01905))

def longestjump(player):
    return player['jump_longest']*0.01905

def falldamage(player):
    return player['falldamage']
