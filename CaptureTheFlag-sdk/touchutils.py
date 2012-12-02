'''
Created on Dec 2, 2012

@author: scottlooze
'''
import math
from api.vector2 import Vector2

class RotationMatrix(object):
    def __init__(self,deg):
        self.rowa = Vector2(math.cos(deg),-1*math.sin(deg))
        self.rowb = Vector2(-math.sin(deg),math.cos(deg));
    
    def rotateVector(self,vec):
        x = self.rowa.dotProduct(vec)
        y = self.rowb.dotProduct(vec)
        return Vector2(x,y)
    def updateRotationMatrix(self,angle):
        self.rowa = Vector2(math.cos(angle),math.sin(angle))
        self.rowb = Vector2(-1*math.sin(angle),math.cos(angle));