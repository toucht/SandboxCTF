# Your AI for CTF must inherit from the base Commander class.  See how this is
# implemented by looking at the commander.py in the ./api/ folder.
from api import Commander

# The commander can send 'Commands' to individual bots.  These are listed and
# documented in commands.py from the ./api/ folder also.
from api import commands

# The maps for CTF are layed out along the X and Z axis in space, but can be
# effectively be considered 2D.
from api import Vector2

from team import *

import datetime

# The telemetry class that collects data on the game.
# This data should be stored at the end of a run so it can be analyzed, or mined to improve the AI system.
import telemetry

class PlaceholderCommander(Commander):
    """
    Rename and modify this class to create your own commander and add mycmd.Placeholder
    to the execution command you use to run the competition.
    """
    
    def initialize(self):
        """Use this function to setup your bot before the game starts."""
        self.verbose = True    #  

    def tick(self):
        """Override this function for your own bots.  Here you can access all the information in self.game,
        which includes game information, and self.level which includes information about the level."""
        
        # make decisions for bots based on updated belief systems
        # for all bots which aren't currently doing anything
        for bot in self.game.bots_available:
            if bot.flag:
                # if a bot has the flag run to the scoring location
                flagScoreLocation = self.game.team.flagScoreLocation
                self.issue(commands.Charge, bot, flagScoreLocation, description = 'Run to my flag')
            else:
                # otherwise run to where the flag is
                enemyFlag = self.game.enemyTeam.flag.position
                self.issue(commands.Charge, bot, enemyFlag, description = 'Run to enemy flag')

    def shutdown(self):
        """Use this function to teardown your bot after the game is over, or perform an
        analysis of the data accumulated during the game."""

        pass
class TouchBalanceCommander(Commander):
    """
    A commander based off of the balance commander inside of the examples.
    This commander goes a step further and skeletons out logging and belief state capabilities.
    """
    """An example commander that has one bot attacking, one defending and the rest randomly searching the level for enemies"""

    def initialize(self):
        self.attacker = Team([],self)
        self.defender = Team([],self)
        self.waitingBots = Team(self.game.team.members,self)
        self.verbose = True

        # Calculate flag positions and store the middle.
        ours = self.game.team.flag.position
        theirs = self.game.enemyTeam.flag.position
        spawnArea = self.game.team.botSpawnArea
        self.middle = (theirs + ours) / 2.0

        # Now figure out the flaking directions, assumed perpendicular.
        d = (ours - theirs)
        self.left = Vector2(-d.y, d.x).normalized()
        self.right = Vector2(d.y, -d.x).normalized()
        self.front = Vector2(d.x, d.y).normalized()
        
        #initialize the telemetry class that keeps track of data.
        self.logger = telemetry.LogTelemetry("tstlog.log")
        
        # initialize the wait time for after defending.
        self.defenseWait = 4

    # Add the tick function, called each update
    # This is where you can do any logic and issue new orders.
    def tick(self):
        #update the belief state
        self.updateBeliefStates()
        
        #Update all of the teams
        self.updateTeams()
        
        #Execute commands for the bots
        deadbots = self.attacker.removeDeadBots()
        deadbots.extend(self.defender.removeDeadBots())
        self.waitingBots.bots.extend(deadbots)
        defenseTeamUpdate = False
        while self.attacker.numBotsAlive() < 2 and self.waitingBots.numBotsAlive() > 0 :
            # the attacker is dead we'll pick another when available
            bot = self.waitingBots.getBotsAlive()[0]
            self.attacker.bots.append(bot)
            self.waitingBots.bots.remove(bot)
        while self.defender.numBotsAlive() < 2 and self.waitingBots.numBotsAlive() > 0:
            # the attacker is dead we'll pick another when available
            bot = self.waitingBots.getBotsAlive()[0]
            self.defender.bots.append(bot)
            self.waitingBots.bots.remove(bot)
            defenseTeamUpdate = True
        
        
        if defenseTeamUpdate:
            self.defender.executeCommand(Team.COMMAND_DEFEND, StraightDefendTactic(self), self.game.team.flagSpawnLocation)
        if not self.attacker.isExecutingTactic():
            if self.attacker.hasFlag():
                self.attacker.executeCommand(Team.COMMAND_CHARGE, StraightMoveTactic(self),self.game.team.flagScoreLocation)
            else:
                target = self.game.enemyTeam.flag.position
                flank = self.getFlankingPosition(self.attacker.getTeamPosition(), target)
                if (target - flank).length() > (self.attacker.getTeamPosition() - target).length():
                    self.attacker.executeCommand(Team.COMMAND_ATTACK, StraightAttackTactic(self), target)
                else:
                    flank = self.level.findNearestFreePosition(flank)
                    self.attacker.executeCommand(Team.COMMAND_ATTACK, StraightAttackTactic(self), flank)
        timeSinceComm = datetime.datetime.now()-self.waitingBots.commandIssued
        
        if not self.waitingBots.isExecutingTactic() and timeSinceComm.seconds > self.defenseWait:
            halfBox = 0.4 * min(self.level.width, self.level.height) * Vector2(1, 1)
            target = self.level.findRandomFreePositionInBox((self.middle + halfBox, self.middle - halfBox))
            
            self.waitingBots.executeCommand(Team.COMMAND_DEFEND, CautiousDefendTactic(self), target)
    
    def updateTeams(self):
        self.attacker.tick()
        self.defender.tick()
        self.waitingBots.tick()
    def updateBeliefStates(self):
        """Update all of the belief stats that my commander hass
        """
        pass 
    def getFlankingPosition(self, pos, target):
        """ Get the flanking position of a target based on a bot.
        """
        flanks = [target + f * 16.0 for f in [self.left, self.right]]
        options = map(lambda f: self.level.findNearestFreePosition(f), flanks)
        return sorted(options, key = lambda p: (pos - p).length())[0]
    
    def shutdown(self):
        """Use this function to teardown your bot after the game is over, or perform an
        analysis of the data accumulated during the game."""
        self.logger.addEvent(telemetry.Telemetry.EVENT_GENERIC,telemetry.EventData("end","the match ended",""))
        self.logger.store()
        
    