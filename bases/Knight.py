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

class Knight(creature.Creature):
	
	def __init__(self, proc):
		creature.Creature.__init__(self, proc)
		self.power = 20
		while not (self.Facing == creature.Direction.North or self.Facing == creature.Direction.East or self.Facing == creature.Direction.South or self.Facing == creature.Direction.West):
			self.Facing = creature.Direction.randomDir()

	#Overrides
	def Attack(self, power, direction):
		print self.proc, "] attempting to shoot a bow with",power,"arrows", "to the", creature.Direction.ToString(direction)
		if (self.power >= power):
			self.power -= power
			self.AddPayload(2)
			return (1, self.ResultCodes.success)
		else:
			self.AddPayload(2)
			return (0, self.ResultCodes.not_enough_power)
	
	def SetFacing(self, facing):
		print self.proc, "] setting horse's facing to", creature.Direction.ToString(facing)
		if (facing == creature.Direction.North or facing == creature.Direction.East or facing == creature.Direction.South or facing == creature.Direction.West):
			self.Facing = facing
			self.AddPayload(1)
			return (1, self.ResultCodes.success)
		else:
			self.AddPayload(1)
			return (0, self.ResultCodes.invalid_facing)
	
	def Move(self, spaces):
		if (spaces > 2 or spaces< 1):
			self.AddPayload(2)
			return (0, self.ResultCodes.invalid_move)
		return creature.Creature.Move(self, spaces) #call base class now