# Known Issues #

## Missing Codec Error (Orangebox, Linux) ##

### Description ###

Following message appears in the console and/or the debug log:
```
LookupError: no codec search functions registered: can't find encoding
```

### Fix ###

Extract the contents of the addons/eventscripts/_engines/python/Lib.zip into addons/eventscripts/_engines/python/Lib/

Reference: http://forums.mattie.info/cs/forums/viewtopic.php?p=227285#227285

## Not recognizing GunGame SourceMod ##

### Description ###

GunGame SourceMod is not recognized by eXtended Stats. This is because XS is loaded before GunGame SourceMod.

### Workaround ###

Replace the autoexec.cfg line
```
es_load extendedstats
```
with
```
es_delayed 1 es_load extendedstats
```
This will delay the loading of eXtended Stats by one second, leaving enough time for GG:SM to load. Should this still not work, increase the amount of seconds the loading process is delayed.

## Lag ##

### Fix ###

Set xs\_debuglevel HIGHER than eventscripts\_debug. If you're not sure how high, take 100.