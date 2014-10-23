#!/usr/bin/python
#
# DON'T FORGET TO SET THE API KEY/SECRET.



import urllib
import httplib
import base64
import json
import urlparse
import sys

def apihit(host,conntype,authtoken,queryurl,reqbody):
    retdata = ''
    connection = httplib.HTTPSConnection(host)
    tokenheader = {"Authorization": 'Bearer ' + authtoken, "Content-type": "application/json", "Accept": "text/plain"}
    if conntype == "GET":
        connection.request(conntype, queryurl, '', tokenheader)
    else:
        connection.request(conntype, queryurl, json.dumps(reqbody), tokenheader)
    response = connection.getresponse()
    respbody = response.read()
    try:
        jsondata = respbody.decode()
        retdata = json.loads(jsondata)
    except:
        retdata = respbody.decode()
    connection.close()
    return retdata

def get_scan_results(host,authtoken,node_id):
    queryurl = '/v1/servers/'+str(node_id)+'/sca'
    results = apihit(host, 'GET', authtoken, queryurl, '')
    return results["scan"]["status"]

def server_move(host,authtoken,node_id,d_groupid):
    reqbody= {"server":{"group_id":d_groupid}}
    queryurl = '/v1/servers/'+str(node_id)
    resp = apihit(host, 'PUT', authtoken, queryurl, reqbody)
    if resp != '':
        print "Taking a ride on the failboat... failed to move server to new group"
        sys.exit(2)
    return True

def start_server_scan(host,authtoken,serverid):
    reqbody = {"scan":{"module":"sca"}}
    queryurl = '/v1/servers/'+str(serverid)+'/scans'
    respjson = apihit(host, 'POST', authtoken, queryurl, reqbody)
    joburl = respjson["command"]["url"]
    return joburl

def get_server_list(host,authtoken,groupid):
    queryurl = "/v1/groups/"+groupid+"/servers"
    jsondata = apihit(host,"GET", authtoken, queryurl, '')
    return jsondata

def get_group_id(host,authtoken,groupname):
    queryurl = "/v1/groups"
    jsondata = apihit(host,"GET", authtoken, queryurl, '')
    for g in jsondata["groups"]:
        if g["name"] == groupname:
            groupid = g["id"]
            return groupid
        else:
            continue
    #if we get to this point, there wasn't a match
    print "No matching group found: ",groupname
    sys.exit()

def get_authtoken(host,clientid,clientsecret):
    # Get the access token used for the API calls.
    connection = httplib.HTTPSConnection(host)
    authstring = "Basic " + base64.b64encode(clientid + ":" + clientsecret)
    header = {"Authorization": authstring}
    params = urllib.urlencode({'grant_type': 'client_credentials'})
    connection.request("POST", '/oauth/access_token', params, header)
    response = connection.getresponse()
    jsondata =  response.read().decode()
    data = json.loads(jsondata)
    if 'read+write' not in data['scope']:
        print "This script requires RW api access.  Exiting"
        sys.exit(2)
    key = data['access_token']
    connection.close()
    return key


def check_command(authtoken,url,host):
    parsedurl = urlparse.urlparse(url)
    checkpath = parsedurl.path
    checkresponse = apihit(host,"GET", authtoken, checkpath, '')
    return checkresponse
