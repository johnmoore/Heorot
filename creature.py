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
import random
from collections import deque

#Result definitions
class EnumResultCodes(object):
	success = 1
	
	#errors
	defeated = -1
	game_over = 0
	not_enough_power = 2
	invalid_facing = 3
	invalid_command = 4
	invalid_move = 5
	collision = 6
	invalid_arguments = 7
	invalid_attack_direction = 8

#Helper classes
class CreatureMove(object):
	__ActionString = ""
	
	def __init__(self, str):
		self.__ActionString = str
		
	def GetActionString(self):
		return self.__ActionString
		
class CreaturePos(object):
	x = 0
	y = 0
	
	def __init__(self):
		self.x = 0
		self.y = 0
	
	def __init__(self, x, y):
		self.x = x
		self.y = y

	def toward(self, pos):
		dx = pos.x-self.x;
		dy = pos.y-self.y;
		adx = abs(dx)
		ady = abs(dy)
		if (2*adx < ady):
			dx = 0
		elif (2*ady < adx):
			dy = 0;
		if(dx < -1):
			dx = -1;
		if(dx > 1):
			dx = 1;
		if(dy < -1):
			dy = -1;
		if(dy > 1):
			dy = 1;
		if(dx == Direction.North[0] and dy == Direction.North[1]):
			return Direction.North;
		if(dx == Direction.South[0] and dy == Direction.South[1]):
			return Direction.South;
		if(dx == Direction.East[0] and dy == Direction.East[1]):
			return Direction.East;
		if(dx == Direction.West[0] and dy == Direction.West[1]):
			return Direction.West;
		if(dx == Direction.NorthEast[0] and dy == Direction.NorthEast[1]):
			return Direction.NorthEast;
		if(dx == Direction.NorthWest[0] and dy == Direction.NorthWest[1]):
			return Direction.NorthWest;
		if(dx == Direction.SouthEast[0] and dy == Direction.SouthEast[1]):
			return Direction.SouthEast;
		if(dx == Direction.SouthWest[0] and dy == Direction.SouthWest[1]):
			return Direction.SouthWest;
		return 0

class Direction(object):
	East = (1,0)
	SouthEast = (1,1)
	South = (0,1)
	SouthWest = (-1,1)
	West = (-1,0)
	NorthWest = (-1,-1)
	North = (0,-1)
	NorthEast = (1,-1)
	
	@staticmethod
	def randomDir():
		DirectionList = [Direction.East, Direction.SouthEast, Direction.South, Direction.SouthWest, Direction.West, Direction.NorthWest, Direction.North, Direction.NorthEast]
		return random.choice(DirectionList)
	
	@staticmethod
	def ToString(dir):
		if (dir == Direction.East):
			return "East"
		elif (dir == Direction.SouthEast):
			return "SouthEast"
		elif (dir == Direction.South):
			return "South"
		elif (dir == Direction.SouthWest):
			return "SouthWest"
		elif (dir == Direction.West):
			return "West"
		elif (dir == Direction.NorthWest):
			return "NorthWest"
		elif (dir == Direction.North):
			return "North"
		elif (dir == Direction.NorthEast):
			return "NorthEast"
		return 0
	
	@staticmethod
	def FromString(str):
		if (str == "East"):
			return Direction.East
		elif (str == "SouthEast"):
			return Direction.SouthEast
		elif (str == "South"):
			return Direction.South
		elif (str == "SouthWest"):
			return Direction.SouthWest
		elif (str == "West"):
			return Direction.West
		elif (str == "NorthWest"):
			return Direction.NorthWest
		elif (str == "North"):
			return Direction.North
		elif (str == "NorthEast"):
			return Direction.NorthEast
		return 0
		
	@staticmethod
	def Equals(dir1, dir2):
		if (Direction.ToString(dir1) == Direction.ToString(dir2)):
			return 1
		else:
			return 0
#Base class	
class Creature(object):
	proc = -1
	power = 0
	ActionQueue = []
	LastAction = 0
	Payload = 0
	Game_Over = 0
	ResultCodes = EnumResultCodes()
	board = []
	Position = CreaturePos(0, 0)
	Facing = ""
	Defeated = 0
	
	def __init__(self, proc):
		self.LastAction = time.time()
		self.Payload = 0
		self.ActionQueue = deque(self.ActionQueue)
		self.Game_Over = 0
		ResultCodes = EnumResultCodes()
		self.board = []
		self.Position = CreaturePos(0, 0)
		self.Facing = Direction.randomDir()
		self.proc = proc
		self.Defeated = 0
		
	#Payload functions
	def AddPayload(self, seconds):
		print self.proc, "] payload of",seconds,"seconds initiated"
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
				
	def QueueAction(self, command, args):
		self.ActionQueue.append([command, args, self.proc])
		self.ProcessQueue()
		
	def ProcessQueue(self):
		if (self.PayloadFinished() == 1 and len(self.ActionQueue) > 0):
			action = self.ActionQueue.popleft()
			command = action[0]
			args = action[1]
			replyto = action[2]
			#process action
			if (self.Game_Over == 1):
				mpi.send((0, self.ResultCodes.game_over), self.proc) #return false because game is over
			elif (self.Defeated == 1):
				mpi.send((0, self.ResultCodes.defeated), self.proc)
				if not (self.Game_Over == 1):
					print self.proc, "] waiting for the game to end..."
					self.AddPayload(2)
			else:
				try:
					if (command.GetActionString() == "Attack"):
						if (len(args) == 1):
							mpi.send(self.Attack(args[0], self.Facing), self.proc)
						elif (len(args) == 2):
							mpi.send(self.Attack(args[0], args[1]), self.proc)
					elif (command.GetActionString() == "GetPower"):
						mpi.send((self.power, self.ResultCodes.success), self.proc)
					elif (command.GetActionString() == "SetFacing"):
						mpi.send(self.SetFacing(args[0]), self.proc)
					elif (command.GetActionString() == "GetFacing"):
						mpi.send((self.Facing, self.ResultCodes.success), self.proc)
					elif (command.GetActionString() == "GetPosition"):
						mpi.send((self.Position, self.ResultCodes.success), self.proc)
					elif (command.GetActionString() == "Move"):
						mpi.send(self.Move(args[0]), self.proc)
					else:
						mpi.send((0, self.ResultCodes.invalid_command), self.proc)
				except IndexError as e:
					mpi.send((0, self.ResultCodes.invalid_arguments), self.proc)
	#Modifier and accessor methods
	def SetBoard(self, board):
		self.board = board
	
	def GetBoard(self):
		return self.board
		
	def SetPosition(self, x, y):
		self.Position = CreaturePos(x, y)
		
	#Overriden or abstract methods
	def Attack(self, attackpower, direction):
		pass
	
	def SetFacing(self, facing):
		pass
	
	def Move(self, spaces):
		temppos = CreaturePos(self.Position.x, self.Position.y)
		collision = (0, (-1, -1))
		outofbounds = 0
		while (spaces > 0):
			if (self.Facing == Direction.North):
				temppos.y -= 1
			elif (self.Facing == Direction.NorthEast):
				temppos.y -= 1
				temppos.x += 1
			elif (self.Facing == Direction.East):
				temppos.x += 1
			elif (self.Facing == Direction.SouthEast):
				temppos.x += 1
				temppos.y += 1
			elif (self.Facing == Direction.South):
				temppos.y += 1
			elif (self.Facing == Direction.SouthWest):
				temppos.x -= 1
				temppos.y += 1
			elif (self.Facing == Direction.West):
				temppos.x -= 1
			elif (self.Facing == Direction.NorthWest):
				temppos.x -= 1
				temppos.y -= 1
			spaces -= 1
			try:
				if not (self.board[temppos.y][temppos.x] == ""): 
					if (temppos.x >= 0 and temppos.y >= 0): #negative indexes for our list loop back, so check
						collision = (1, (temppos.x, temppos.y))
			except IndexError as e:
				outofbounds = 1 #catches too far South and East
				break
			if (temppos.x < 0 or temppos.y < 0):
				outofbounds = 1
				break
		if (outofbounds == 1):
			self.AddPayload(2)
			return (0, self.ResultCodes.invalid_move)
		if (collision[0] == 1):
			print self.proc, "] game engine detected collision at", collision[1][0], collision[1][1]
			tempplayer = self.board[collision[1][1]][collision[1][0]]
			self.board[collision[1][1]][collision[1][0]] = ""
			tempplayer.Kill()
			self.board[self.Position.y][self.Position.x] = ""
			self.Kill()
			return (1, self.ResultCodes.collision)
		self.board[self.Position.y][self.Position.x] = ""
		self.Position = temppos
		self.board[self.Position.y][self.Position.x] = self
		self.AddPayload(2)
		return (1, self.ResultCodes.success)
	
	#Unoveridden methods
	def Kill(self):
		print self.proc, "] has been defeated"
		self.Defeated = 1