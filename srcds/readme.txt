How to add methods:

Documentation is in /extendedstats/methods/default.py

How to access data:

import extendedstats.extendedstats as extendedstats
myplayerdata = extendedstats.getPlayer(myplayersteamid)

IMPORTANT: Do not access the data dictionary directly, as some values are out of sync in that case.

Addons:

Documentation is in /extendedstats/addons/default.py

Addons need to be placed in /extendedstats/addons/ and must be python files.
You must import extendedstats.extendedstats as exendedstats in your addon file!
Addons MUST have a new_player dict! This one defines the keys and default values of the data
your addon will provide to prevent key errors.
If you want so submit data to extendedstats using this addon create a method called load().
In this method you should register all events you want to listen using following method:
extendedstats.registerEvent(addonname,eventname,callback)
	-addonname (string): Name of your addon. If your filename is someaddon.py it would be someaddon
	-eventname (string): For player_death this would be 'player_death'
	-callback (mehtod): The method in your script that should be called
To submit data to extendedstats in your addon use:
extendedstats.data[steamid][key] = value