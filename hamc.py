#!/usr/bin/python
#
# This script creates user accounts, or resets passwords if they already exist.

import time
import sys
import getopt
import api
import server
import fn

def main(argv):
    config={}
    #First, we get the vars from the config file
    execfile("config.conf",config)
    config["usagetext"] = ("hamc.py -s SOURCE_GROUP -d DEST_GROUP\n",
                 "This script will iterate through all active hosts\n",
                 "in SOURCE_GROUP, and move every one that completes all\n",
                 "applicable configuration scans cleanly to DEST_GROUP.")
    serverolist = []
    # Next, we attempt to parse args from CLI, overriding vars from config file.
    try:
        opts, args = getopt.getopt(argv, "hs:d:",["s_grp=","d_grp="])
    except getopt.GetoptError:
        print config["usagetext"]
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print config["usagetext"]
            sys.exit()
        elif opt in ("-s","--s_grp"):
            config["src_grp"] = arg
        elif opt in ("-d", "--d_grp"):
            config["dst_grp"] = arg
         
    iterations = config["iterations"]
    s_grp = config["src_grp"]
    d_grp = config["dst_grp"]
    clientid = config["clientid"]
    clientsecret = config["clientsecret"]
    host = config["host"]

    # Sanity check, let's make sure that we aren't speaking crazytalk
    sanity = fn.amisane(clientid,clientsecret)
    if sanity == False:
        print "Insane in the membrane.  Crazy insane, got no keys."
        sys.exit(2)
    # Call the routine to set the autentication token
    authtoken = api.get_authtoken(host,clientid,clientsecret)
    # Determine the group ID number for source group
    s_groupid = api.get_group_id(host,authtoken,s_grp)
    # Determine the group ID number for dest group
    d_groupid = api.get_group_id(host,authtoken,d_grp)
    # Get a list of member servers
    serverlist = api.get_server_list(host,authtoken,s_groupid)
    # If there are no servers in source list, just exit
    if serverlist["servers"] == []:
        print "Source list is empty.  Exiting!"
        sys.exit()
    # Populate the server list and kick off scans...
    for s in serverlist["servers"]:
        serveridno = s["id"]
        url = api.start_server_scan(host,authtoken,serveridno)
        serverolist.append(server.Server(s["hostname"], s["id"], url))
    # All jobs submitted, notify user and check until all are done
    print "\n\n"
    print "All scan jobs have been submitted.  Now checking results.\nPlease stand by..."
    for i in xrange(1, iterations):
        if i % 20 == 0:
            print "Renewing API key after 10 mins"
            authtoken = api.get_authtoken(host,clientid,clientsecret)
        totalservers,serversdone = fn.get_job_status(serverolist)
        if totalservers == serversdone:
            fn.exit_routine(serverolist)
        print "Waiting on jobs to finish..."
        time.sleep(30)
        print serversdone ," of " , totalservers , " have finished."
        i = i+1
        for node in serverolist:
            # If the checkstatus is set, move along.  This is not the job you're looking for.
            if node.disposition != '':
                continue
            else:
                result = fn.process_check_command(str(node.url),str(authtoken),str(host),str(node.id))
                print "Server: ",node.name," Job status: ",result
                if result == "completed_clean":
                    print "Server ",node.name,"cleanly completed all scans!"
                    print "Moving server to the destination group"
                    move_success = api.server_move(host,authtoken,node.id,d_groupid)
                    if move_success == False:
                        print "Failed to move server to destination group.  Will retry"
                    else:
                        node.disposition = 'Moved'
                if result == "completed_with_errors":
                    print "Server ",node.name,"has configuration inconsistencies!  It will not be moved."
                    node.disposition = "Dirty" 
                if result == "failed":
                    print "\nJob on ",node.name," failed!  Resubmitting"
                    node.url = api.start_server_scan(host,authtoken,node.id)

if __name__ == "__main__":
    main(sys.argv[1:])
