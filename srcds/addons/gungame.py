# Gungame eXtendedStats Addon version 1.0 by Ojii
from extendedstats import extendedstats # Import eXtended Stats
import es, path

GGP = path.path(es.getAddonPath('gungame'))

if GGP.isdir(): # check if gungame is present on the server
    new_player = {
        'gg_level': 0,
        'gg_win': 0,
    }

# This method will be called when eXtended Stats is loaded
# It is used to register events used in this addon
def load():
    if GGP.isdir(): # check if gungame is present on the server
        # the registerEvent function registers an event to a function in this addon
        # The first argument is a string and should be the name of this file without the extension
        # The second argument is a string and shoud be the name of the even to register
        # The last argument is the function which should be called on that event
        extendedstats.registerEvent('gungame','gg_levelup',gungame_level)
        extendedstats.registerEvent('gungame','gg_leveldown',gungame_level)
        extendedstats.registerEvent('gungame','gg_win',gungame_winner)
        # Client and Saycommands can be registred using registerCommand
        # By default both a client and a say command are registred, where the saycommand is prefixed with !
        # The first argument is the command name
        # The second argument is the name of your addon (the filename without extension)
        # The third argument is the method which should be called
        # The optional fourth argument is True by default. If False, no clientcommand will be registred
        # The optional fifth argument is True by default. If False, no saycommand will be registred.
        # The optional sixth argument is the saycommand prefix. By default it's '!'.
        extendedstats.registerCommand('ggwon','gungame',ggwon_command)
    else:
        extendedstats.dbg( 'XS:GG: No gungame files found')
    
# This method will be called on gg_levelup and gg_leveldown event
# The event_var (or here: ev) argument is like in normal events
def gungame_level(ev):
    # IMPORTANT: Always check if your user is a bot!!!
    if not es.isbot(ev['userid']):
        extendedstats.data[ev['steamid']]['gg_level'] += int(ev['old_level']) - int(ev['new_level'])

def gungame_winner(ev):
    # IMPORTANT: Always check if your user is a bot!!!
    if not es.isbot(ev['userid']):
        extendedstats.data[ev['steamid']]['gg_win'] += 1
        
def ggwon_command(userid,arguments):
        es.tell(userid,'You have won GunGame %s times' % extendedstats.data[es.getplayersteamid(userid)]['gg_win'])
