from extendedstats import extendedstats
import es, path

scfg = extendedstats.scfg

GG = extendedstats.addonIsLoaded('gungame')
if not GG:
    GG = str(es.ServerVar('sm_gungame_enabled')) == '1'

if GG: # check if gungame is present on the server
    columns = [
        ('gg_level','INTEGER DEFAULT 0'),
        ('gg_win','INTEGER DEFAULT 0'),
    ]
    extendedstats.players.addColumns(columns)

def load():
    if GG:
        extendedstats.registerCommand(scfg.command_gungame_ggwon,'gungame',ggwon_command)
        extendedstats.loadEvents('gungame')
    else:
        extendedstats.dbg( 'XS:GG: No gungame files found')
        
def ggwon_command(userid,arguments):
    if str(userid) in extendedstats.pending:
        es.tell(userid,extendedstats.text.getSimple('messages','sorry_pending'))
        return
    es.tell(userid,text.getCmdString(es.getplayersteamid(userid),'ggwon','__standard__',0,0,0))
