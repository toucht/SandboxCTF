import time
"""defines a class that stores interesting data about the match.
"""
class Telemetry(object):
    """Constructor that initializes all the data to be stored during a match"""
    EVENT_GENERIC = 0
    EVENT_END = 1
    def __init__(self):
        #TODO: initialze data structures for the beginning of a match.
        self.events = {}
    def store(self):
        print "test"
        #TODO: write a storage system whether it is writing to a log, csv, or db.
        
    def addEvent(self,event,data):
        if not self.events.has_key(event):
            self.events[event] = []
        self.events[event].append(data)
""" A subclass that stores telemetry events in a log file
"""
class LogTelemetry(Telemetry):
    def __init__(self,name):
        super(LogTelemetry,self).__init__()
        self.name = name
        
    def store(self):
        f = open(self.name,'w')
        for earrays in self.events.values():
            for event in earrays:
                f.write(event.name)
                f.write("\n")
        f.flush()
        f.close()
""" A class that defines the information associated with an event in the game.
"""
class EventData(object):
    def __init__(self,name,desc,data):
        #TODO add the fields that will be required to define an event.
        self.name = name
        self.desc = desc
        self.data = data
        self.timestamp = time.time()

