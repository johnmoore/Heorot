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
import creature

class Dragon(creature.Creature):
	
	def __init__(self, proc):
		creature.Creature.__init__(self, proc)
		self.power = 100

	#Overrides
	def Attack(self, power, direction):
		if not (creature.Direction.Equals(direction, self.Facing)): #dragons must breathe forward
			return (0, self.ResultCodes.invalid_attack_direction)
		print self.proc, "] attempting to breathe",power,"breaths of fire", "to the", creature.Direction.ToString(self.Facing)
		if (self.power >= power):
			self.power -= power
			self.AddPayload(3)
			return (1, self.ResultCodes.success)
		else:
			self.AddPayload(3)
			return (0, self.ResultCodes.not_enough_power)
	
	def SetFacing(self, facing):
		print self.proc, "] setting flying direction to", creature.Direction.ToString(facing)
		self.Facing = facing
		self.AddPayload(2)
		return (1, self.ResultCodes.success)
	
	def Move(self, spaces):
		if not (spaces == 1):
			self.AddPayload(2)
			return (0, self.ResultCodes.invalid_move)
		return creature.Creature.Move(self, spaces) #call base class now