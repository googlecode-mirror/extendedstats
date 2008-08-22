##############################
###  STATIC CONFIGURATION  ###
##############################
#
### Addon Importing ###

allAddons = True # Just import all addons in the folder
addonList = [] # list of addonnames to be importet (if allAddons False)
               # list items must be string!

### Method Importing ###
allPackages = True # If true all packages will be imported, otherwise only listed
packageList =  []  # list of methodpackages to be imported (if allMethods False)
                   # list items must be string!
allMethods = True  # Just import all methods from the packages
methodList = []    # Import only selected methods

### Commands ###
# ALL MUST BE STRINGS!!!

say_command_prefix = '!' # prefix for say commands

# command names
command_rank = 'rank'
command_methods = 'methods'
command_statsme = 'statsme'
command_help = 'help'
command_settings = 'settings'
command_top = 'top'
command_commands = 'commands'

command_gungame_ggwon = 'ggwon'

command_weaponstats_weaponstats = 'weaponstats'

### Misc Settings ###

settings_menu_resend = True # BOOLEAN

default_top_x = 5 # INTEGER

### Debugging ###

debug = True # highly recommended until final release
             # Must be bool (True,False)
             # If true a logfile will be written