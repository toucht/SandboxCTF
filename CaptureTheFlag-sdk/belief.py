#!/usr/bin/env python
#################### BELIEF STATES #######################
"""The base class that all belief states inherit from. Provides some organization of datastructures that will most
likely be convieinent for the sub-classes.
"""
class BeliefState(object):
    """A beliefstate structure that stores the the belief of enemy positions in a given zone on the map
    """
    def __init__(self,map):
        #from map structure create grid
        self.map = map
        self.state = []
    def updateBelief(self,levelinfo,teaminfo,enemyinfo):
        """Update the belief state based on changing game info.
        """
        pass

    def getBeliefState(self):
        """ Get the belief state which should return a 2-d array of [0,1) values. that correspond to positions on the map.
        """
        return self.state
    
class EnemyPosBelief(BeliefState):
    def updateBelief(self,levelinfo,teaminfo,enemyinfo):
        #don't propogate any beliefs for now.
        x = False
###########################################################

####################  PERSONALITY #########################

class Personality(object):
    def __init__(self,map,levelinfo):
        #pick a personality to read in from given the layout of the map
        self.offensive = .5
        self.direct = .5
        self.desperate = .1
        self.createive = .5
    def changePersonality(self):
        self.readInPersonality(1)
    
    def readInPersonality(self,num):
        #do nothing for now
        print "readinPersonality ** stub"
    
        