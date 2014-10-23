
#!/usr/bin/python

class Server():
    def __init__(self, hostname, serverid, joburl):
        self.name = hostname 
        self.id = serverid
        self.disposition = ''
        self.url = joburl

