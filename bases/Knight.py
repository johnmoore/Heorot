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
	
	def __init__(self):
		creature.Creature.__init__(self)
		self.power = 20
		
	#Overrides
	def Attack(self, power, replyto):
		print replyto, "] attempting to shoot a bow with",power,"arrows!"
		if (self.power >= power):
			self.power -= power
			self.AddPayload(2, replyto)
			return (1, self.ResultCodes.success)
		else:
			self.AddPayload(2, replyto)
			return (0, self.ResultCodes.not_enough_power)