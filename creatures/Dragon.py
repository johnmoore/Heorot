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

class EnumResultCodes(object):
	success = 1
	
	#errors
	slain = -1
	game_over = 0
	not_enough_breath = 2
	invalid_flying_direction = 3
	invalid_command = 4
	invalid_flight_path = 5
	collision = 6
	invalid_arguments = 7
	invalid_breathing_direction = 8

class EnumActionNames(object):
	GetBreath = creature.CreatureMove("GetPower")
	BreatheFire = creature.CreatureMove("Attack")
	SetFlyingDirection = creature.CreatureMove("SetFacing")
	GetFlyingDirection = creature.CreatureMove("GetFacing")
	GetFlyingPosition = creature.CreatureMove("GetPosition")
	Fly = creature.CreatureMove("Move")

class DragonFields(object):
	ResultCodes = EnumResultCodes()
	Actions = EnumActionNames()
	Direction = creature.Direction
	Position = creature.CreaturePos