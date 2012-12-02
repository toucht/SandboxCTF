#!/usr/bin/env python
from api import commands
from api import gameinfo
from api.vector2 import *
from touchutils import *
import datetime
class Team(object):
    COMMAND_WAIT = 0
    COMMAND_ATTACK = 4
    COMMAND_DEFEND = 1
    COMMAND_CHARGE = 5
    COMMAND_FLANK = 3
    COMMAND_EMERDEF = 16
    COMMAND_EMERATT = 17
    
    def __init__(self,bots,commander):
        self.state = Team.COMMAND_WAIT
        self.bots = bots
        self.commander = commander
        self.curtactic = None
        self.commandIssued = datetime.datetime.now()
    def setBots(self,bots):
        self.bots = bots
    
    def hasFlag(self):
        for bot in self.bots:
            if bot.flag:
                return True
        return False
     
    def executeCommand(self,command,tactic,pos):
        """ Executes the command given using the tactic. and the given position.
        """
        if command >= self.state:
            #EXECUTE THE COMMANDS IN THE TACTIC
            self.commandIssued = datetime.datetime.now()
            self.curtactic = tactic
            tactic.exe(self.bots,pos)
            self.state = command
    
    def tick(self):
        """A tick functoin so the team can update information about itself
        """
        if self.curtactic:
            self.curtactic.tick()
            if self.curtactic.isFinished:
                #for bot in self.bots:
                    #set bot to defend position facing in current direction
                #self.commander.issue(commands.Defend,bot,facingDirection=bot.facingDirection,description ="waiting command")
                if self.state != Team.COMMAND_DEFEND:
                    self.state = Team.COMMAND_WAIT
                self.curtactic = None
                
    def isExecutingTactic(self):
        """Indicates whether the team is currently executing a tactic or not.
        """
        if self.curtactic:
            return not self.curtactic.isFinished
        return False
    
    def numBotsAlive(self):
        """ Returns the number of bots alive that are a part of this team.
        """
        count = 0
        for bot in self.bots:
            if bot.health > 0:
                count = count + 1
        return count
    
    def getBotsAlive(self):
        """ Returns a list of alive bots on this team
        """
        return [b for b in self.bots if b.health > 0]
    
    def getBotsDead(self):
        """ Returns a list of dead bots on this team
        """
        return [b for b in self.bots if b.health > 0]
    
    def removeDeadBots(self):
        """ Removes the dead bots from this team and returns them in a list.
        """
        deadbots = []
        for bot in self.bots[:]:
            if bot.health < 1:
                self.bots.remove(bot)
                deadbots.append(bot)
        return deadbots
    
    def getTeamPosition(self):
        """ Gets the average position of the bots on this team.
        """
        ret = Vector2(0,0)
        for bot in self.bots:
            ret = ret + bot.position
        ret = ret / float(len(self.bots))
        return ret



###################################### Tactics ################################
class Tactic(object):
    """ A base class that defines the basic structure of how a tactic is executed.
    """
    def __init__(self,commander):
        self.commands = []
        self.commander = commander
        self.bots = []
        self.isFinished = False
        self.target = Vector2(0,0)
    def exe(self,bots,pos):
        self.bots = bots
        self.target = pos
        if len(self.commands) > 0:
            self.runTactic()
    def runTactic(self):
        if len(self.commands) > 1:
            #command = self.commands.pop()
            pass
        else:
            self.isFinished = True
    def tick(self):
        exeNext = False
        
        #Alright there is a command to execute lets see if we should move to it.
        for bot in self.bots:
            if bot.state == gameinfo.BotInfo.STATE_DEFENDING or bot.state == gameinfo.BotInfo.STATE_IDLE:
                exeNext = True
        if exeNext:
            if len(self.commands) > 0:
                self.runTactic()
            else:
                self.isFinished = True
class MaxVisionTactic(Tactic):
    """ A base class for a set of tactics where the bots move in such a way where they cover as much of 
        a 360 range of view as they possibly can
    """
    def __init__(self,commander):
        super(MaxVisionTactic,self).__init__(commander)
        self.viewAngle = commander.level.FOVangle
    def getLookAtDirs(self,forward):
        facingDirection = forward
        botLookDirs = []
        if len(self.bots) > 0:
            facingDirection = forward
            botLookDirs.append(facingDirection)
        if len(self.bots) > 1:
            #rotate bot backwards
            botLookDirs.pop()
            rot = RotationMatrix(self.viewAngle/2*-1)
            botFaceDir = rot.rotateVector(facingDirection)
            botLookDirs.append(Vector2(botFaceDir.x, botFaceDir.y))
            rot.updateRotationMatrix(self.viewAngle*.9)
            for i in range(1,len(self.bots)):
                botFaceDir = rot.rotateVector(botFaceDir)
                botLookDirs.append(Vector2(botFaceDir.x, botFaceDir.y))
        return botLookDirs
        
class StraightAttackTactic(MaxVisionTactic):
    def __init__(self,commander):
        super(StraightAttackTactic,self).__init__(commander)
        self.commands.append(commands.Attack)
    def runTactic(self):
        if not self.isFinished and len(self.bots) > 0:
            #calculate the look position of bots
            command = self.commands.pop()
            botLookDirs = self.getLookAtDirs(self.target-self.bots[0].position)
            for i in range(len(self.bots)):
                    self.commander.issue(command,self.bots[i],target=self.target,description="Attack",lookAt=self.target)

class StraightMoveTactic(MaxVisionTactic):
    def __init__(self,commander):
        super(StraightMoveTactic,self).__init__(commander)
        self.commands.append(commands.Move)
    def runTactic(self):
        if not self.isFinished:
            #calculate the look position of bots
            command = self.commands.pop()
            #botLookDirs = self.getLookAtDirs(self.target-self.bots[0].position)
            for i in range(len(self.bots)):
                    self.commander.issue(command,self.bots[i],target=self.target,description="Move")
    
class CautiousDefendTactic(MaxVisionTactic):
    def __init__(self,commander):
        super(CautiousDefendTactic,self).__init__(commander)
        self.commands.append(commands.Defend)
        self.commands.append(commands.Attack)
    def runTactic(self):
        if not self.isFinished:
            #calculate the look position of bots
            command = self.commands.pop()
            botLookDirs = self.getLookAtDirs(self.commander.game.enemyTeam.flagSpawnLocation - self.commander.game.team.flagSpawnLocation)
            for i in range(len(self.bots)):
                direc = botLookDirs[i]
                if command == commands.Defend:
                    self.commander.issue(command,self.bots[i],facingDirection=direc,description="Defend")
                elif command == commands.Move:
                    self.commander.issue(command,self.bots[i], target=self.target,description="Moving to defend")


class StraightDefendTactic(MaxVisionTactic):                
    def __init__(self,commander):
        super(StraightDefendTactic,self).__init__(commander)
        self.commands.append(commands.Defend)
        self.commands.append(commands.Move)
    def runTactic(self):
        if not self.isFinished:
            #calculate the look position of bots
            command = self.commands.pop()
            botLookDirs = self.getLookAtDirs(self.commander.game.enemyTeam.flagSpawnLocation - self.commander.game.team.flagSpawnLocation)
            for i in range(len(self.bots)):
                direc = botLookDirs[i]
                if command == commands.Defend:
                    self.commander.issue(command,self.bots[i],facingDirection=direc,description="Defend")
                elif command == commands.Move:
                    self.commander.issue(command,self.bots[i], target=self.target,description="Moving to defend")

            