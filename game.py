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
from creatures import *

#for debug purposes (until we read a file)
debugclasses = ["FlameDragon", "ArcherKnight"]

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
	
def instantiate_player(player_module, CB):
	try:
		__import__("players." + player_module)
		player_classes = inspect.getmembers("players." + player_module, inspect.isclass)
	except ImportError as e:
		raise InvalidPlayerClass("Player module could not be loaded (ImportError): " + player_module)
	if (len(player_classes) > 1):
		raise InvalidPlayerClass("Player module contained more than one class.")
	else:
		try:
			return getattr(sys.modules["players." + player_module], player_module)(CB)
		except ImportError as e:
			raise InvalidPlayerClass("Player module could not be loaded (ImportError): " + player_module)

def instantiate_master(master_class, mCB):
	paths = master_class.split('.')
	modulename = '.'.join(paths[:-1])
	classname = paths[-1]
	__import__(modulename)
	return getattr(sys.modules[modulename], classname)(mCB)

board = init_board(BOARD_DIMENSION_WIDTH, BOARD_DIMENSION_HEIGHT)

#main code
if (mpi.rank == 0):
	#proc 0 runs the game
	timercount = 0
	starttime = time.time()
	
	while(time.time() <= starttime + GAME_LENGTH):
		packet = mpi.recv(mpi.ANY_SOURCE)
		(data, status) = packet
		replyto = status.source
		if (data == "check_in_game"):
			mpi.send({"in_game": 1}, replyto)
	
	for proc in range(1, mpi.size):
		mpi.send({"in_game": 0}, proc)
	
	exited = 0
	while (exited < mpi.size - 1):
		(data, status) = mpi.recv(mpi.ANY_SOURCE)
		if (data == "exiting"):
			exited += 1
	
	print("Game completed.")
else:
	if (mpi.rank % 2 == 1):
		#Odd procs are Base Classes
		master = instantiate_master(mpi.recv(mpi.rank + 1)[0], mpi.rank + 1)
		while (1==1):
			master.HandleRequests()
		
	else:
		#Even procs are student classes
		classtoload = debugclasses[(mpi.rank / 2) - 1]
		
		try:
			player = instantiate_player(classtoload, mpi.rank - 1)
		except InvalidPlayerClass as e:
			print("Invalid player class: " + e.value)
			sys.exit(0)
		mpi.send(player.__class__.__bases__[0].__module__ + "." + player.__class__.__bases__[0].__name__, mpi.rank - 1)

		while (1==1):
			if (player.IsInGame() == 0):
				mpi.send("exiting", 0)
				sys.exit()
			player.action()
