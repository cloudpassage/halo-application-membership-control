#Script to run configuration scans across a source group, and move all compliant hosts to the destination group
This script runs against the Halo API and causes all configuration-compliant hosts in the source group to be moved to the destination group.

##Before We Begin
Please have a look at the config.conf file.  You will need to set your clientid and clientsecret or the script simply won't work.
Command line execution looks like this: 
hamc.py -s SOURCE_GROUP -d DESTINATION_GROUP


###Step by Step
Download all the files here into the same location and make sure that hamc.py is executable.
Edit config.conf to set your API key and secret, as well as any other values you need.  


####Here’s a breakdown of the files you see here:

* **hamc.py**   	            			Run this one.

* **server.py**		                        Contains Server object definition 

* **api.py**		                        Contains functions that hit the API 

* **config.conf**                           Contains configuration variables

* **fn.py**                                 Contains general functions

* **README.md**                             This file 

