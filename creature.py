# Heorot
# Copyright (C) 2010 John Moore
# 
# http://www.programiscellaneous.com/programming-projects/heorot-python-mpi-game/what-is-it/
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import time
import inspect
import mpi
import sys
from collections import deque

#Result definitions
class EnumResultCodes(object):
	success = 1
	
	#errors
	game_over = 0
	not_enough_power = 2

#Helper classes
class CreatureMove(object):
	__ActionString = ""
	
	def __init__(self, str):
		self.__ActionString = str
		
	def GetActionString(self):
		return self.__ActionString

#Base class	
class Creature(object):
	power = 0
	ActionQueue = []
	LastAction = 0
	Payload = 0
	Game_Over = 0
	ResultCodes = EnumResultCodes()
	
	def __init__(self):
		self.LastAction = time.time()
		self.Payload = 0
		self.ActionQueue = deque(self.ActionQueue)
		self.Game_Over = 0

	#Payload functions
	def AddPayload(self, seconds, replyto):
		print replyto, "] payload of",seconds,"seconds initiated"
		self.Payload = seconds
		self.LastAction = time.time()
	
	def PayloadFinished(self):
		if (self.LastAction + self.Payload <= time.time()):
			return 1
		else:
			return 0
	
	#Queue functions
	def FlushQueue(self):
		self.Game_Over = 1
		while (len(self.ActionQueue) > 0):
			self.ProcessQueue()
				
	def QueueAction(self, command, args, replyto):
		self.ActionQueue.append([command, args, replyto])
		self.ProcessQueue()
		
	def ProcessQueue(self):
		if (self.PayloadFinished() == 1 and len(self.ActionQueue) > 0):
			action = self.ActionQueue.popleft()
			command = action[0]
			args = action[1]
			replyto = action[2]
			#process action
			if (self.Game_Over == 1):
				mpi.send((0, self.ResultCodes.game_over), replyto) #return false because game is over
			else:
				if (command.GetActionString() == "Attack"):
					mpi.send(self.Attack(args[0], replyto), replyto)
				elif (command.GetActionString() == "GetPower"):
					mpi.send((self.power, self.ResultCodes.success), replyto)
					
	#Abstract methods
	def Attack(self, attackpower, replyto):
		pass
