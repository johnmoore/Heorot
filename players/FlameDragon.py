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
from creatures import Dragon
import mpi

class FlameDragon(Dragon):
	def action(self):
		mpi.send([self.Actions.GetBreath, []], 0)
		(result, code) = mpi.recv(0)[0]
		print mpi.rank, "] I have", result,"breath power."
		mpi.send([self.Actions.BreatheFire, [10]], 0)
		(result, code) = mpi.recv(0)[0]
		if (result == 1):
			print mpi.rank, "] fire breathing attack succeeded!"
		else:
			if (code == self.ResultCodes.game_over):
				print mpi.rank, "] fire breathing attack failed because the game was over"
			elif (code == self.ResultCodes.not_enough_breath):
				print mpi.rank, "] fire breathing attack failed because we were out of breath"
			elif (code == self.ResultCodes.invalid_breathing_direction):
				print mpi.rank, "] can only breath fire straight"
		mpi.send([self.Actions.SetFlyingDirection, [self.Direction.East]], 0)
		(result, code) = mpi.recv(0)[0]
		if (code == self.ResultCodes.success):
			print mpi.rank, "] set direction!"
		elif (code == self.ResultCodes.invalid_flying_direction):
			print mpi.rank, "] I can't fly that way!"
		mpi.send([self.Actions.GetFlyingDirection, []], 0)
		(dir, code) = mpi.recv(0)[0]
		mpi.send([self.Actions.GetFlyingPosition, []], 0)
		(pos, code) = mpi.recv(0)[0]
		if (code == self.ResultCodes.success):
			print mpi.rank, "] I am flying", self.Direction.ToString(dir), "at", "(", pos.x, ",", pos.y, ")"
			print mpi.rank, "] Where is (5, 5)? In relation to me, approx.: ", self.Direction.ToString(pos.toward(self.Position(5, 5)))
		elif (code == self.ResultCodes.game_over):
			print mpi.rank, "] I failed to get my flying position because the game was over"
		print mpi.rank, "] Attempting to fly 2 spaces"
		mpi.send([self.Actions.Fly, [1]], 0)
		(result, code) = mpi.recv(0)[0]
		if (code == self.ResultCodes.success):
			print mpi.rank, "] flying successful"
		elif (code == self.ResultCodes.invalid_flight_path):
			print mpi.rank, "] flying unsuccessful, I must have flown off the board or attempted to fly too far at once"
		elif (code == self.ResultCodes.collision):
			print mpi.rank, "] I collided"
		elif (code == self.ResultCodes.game_over):
			print mpi.rank, "] could not fly because game over"
		elif (code == self.ResultCodes.slain):
			print mpi.rank, "] could not fly because I have been slain"