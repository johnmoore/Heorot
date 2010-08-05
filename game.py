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
import mpi
import sys
import inspect
import time
from bases import *

#for debug purposes (until we read a file)
debugclasses = ["ArcherKnight", "FlameDragon"]

#exceptions
class InvalidPlayerClass(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

#pseudoconstants
BOARD_DIMENSION_WIDTH = 3
BOARD_DIMENSION_HEIGHT = 8
GAME_LENGTH = 8

#functions
def init_board(x, y):
	return [[0 for col in range(x)] for row in range(y)]
	
def instantiate_player(player_module):
	try:
		__import__("players." + player_module)
		player_classes = inspect.getmembers("players." + player_module, inspect.isclass)
	except ImportError as e:
		raise InvalidPlayerClass("Player module could not be loaded (ImportError): " + player_module)
	if (len(player_classes) > 1):
		raise InvalidPlayerClass("Player module contained more than one class.")
	else:
		try:
			return getattr(sys.modules["players." + player_module], player_module)()
		except ImportError as e:
			raise InvalidPlayerClass("Player module could not be loaded (ImportError): " + player_module)

def instantiate_master(master_class):
	paths = master_class.split('.')
	modulename = '.'.join(paths[:-1])
	classname = paths[-1]
	__import__(modulename)
	return getattr(sys.modules[modulename], classname)()

#main code
if (mpi.rank == 0):
	#proc 0 runs the game
	players = range(0, mpi.size) #here we store the master classes; 0 is a placeholder
	board = init_board(BOARD_DIMENSION_WIDTH, BOARD_DIMENSION_HEIGHT)

	#first we need to set up our players
	for player in range(1, mpi.size):
		players[player] = instantiate_master(mpi.recv(player)[0])
	
	mpi.barrier()
	#now we run the game
	starttime = time.time()
	
	while(time.time() <= starttime + GAME_LENGTH):
		#Update our queues
		if (len(mpi._recv_queue) > 0):
			packet = mpi.recv(mpi.ANY_SOURCE)
			(data, status) = packet #data[0] is the command string, data[1] is a list of args
			if (data == "check_in_game"):
				mpi.send(1, status.source)
			else:
				player = players[status.source]
				command = data[0]
				args = data[1]
				player.QueueAction(command, args, status.source) #forward our command to the master
		#Process our queues
		for player in range(1, mpi.size):
			players[player].ProcessQueue()
	print "Game completed. Anything following will not be taken into consideration."
	#wait for our player procs to end, but first flush the queue (returns false results for attacks, blank boards)
	for player in range(1, mpi.size):
			players[player].FlushQueue()
	exited = 0
	while (exited < mpi.size - 1):
		packet = mpi.recv(mpi.ANY_SOURCE)
		(data, status) = packet
		if (data == "check_in_game"):
			mpi.send(0, status.source)
		elif (data == "exiting"):
			exited += 1
		else:
			mpi.send((0, 0), status.source) #Respond to any lingering action queue requests (0 is the game_over result code for all creatures)
	print "All procs flushed and exited."
else:
	classtoload = debugclasses[mpi.rank - 1]
		
	try:
		player = instantiate_player(classtoload)
	except InvalidPlayerClass as e:
		print("Invalid player class: " + e.value)
		sys.exit(0)

	mpi.send(player.__class__.__bases__[0].__module__.replace("creatures", "bases") + "." + player.__class__.__bases__[0].__module__.replace("creatures.", ""), 0)

	mpi.barrier()
	
	while (1==1):
		mpi.send("check_in_game", 0)
		if (mpi.recv(0)[0] == 0):
			mpi.send("exiting", 0)
			sys.exit(0)
		else:
			player.action()

