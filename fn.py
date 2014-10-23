#!/usr/bin/python
import api
import sys

def amisane(apikey,apisecret):
    sanity = True
    if apikey == '':
        return False
    if apisecret == '':
        return False
    return sanity

def get_job_status(serverlist):
    totalcount = len(serverlist)
    donecount = 0
    for s in serverlist:
        if s.disposition !=  '' :
            donecount = donecount + 1
        else:
            continue
    return (totalcount,donecount)

def process_check_command(url,key,host,node_id):
    checkresults = api.check_command(key,url,host)
    #print "Check Results: ",checkresults
    try:
        if checkresults["command"]["status"] == "completed":
            serverscanresults = api.get_scan_results(host, key, node_id)
            return (serverscanresults)
        return checkresults["command"]["status"]
    except:
        print "Command check failed! "
        print "Check return information: "
        print checkresults
        sys.exit()

def exit_routine(serverolist):
    for node in serverolist:
        print "Server: ", node.name, " Disposition: ", node.disposition
    sys.exit()
