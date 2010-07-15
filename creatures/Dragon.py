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

class DragonBase(object):
	fire = 0
	__mCB = -1
	
	def __init__(self, mCB=-1):
		self.fire = 100
		if (mCB >= 0):
			self.__mCB = mCB
		
	def __flamethrow(self, firepower):
		print "attacking with a flamethrow of", firepower, "firepower!"
		if(self.fire >= firepower):
			self.fire -= firepower
			print("success")
		else:
			print("not enough fire!")
		time.sleep(2)
		
	def IsInGame(self):
		mpi.send("check_in_game", 0)
		retval = mpi.recv(0)[0]['in_game']
		return retval
		
	def HandleRequests(self):
		if (self.IsInGame() == 0):
			mpi.send("exiting", 0)
			sys.exit()
		packet = mpi.recv(self.__mCB)[0]
		(func, args) = packet
		if (func == "flamethrow"):
			self.__flamethrow(args[0])
		