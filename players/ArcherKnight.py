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
from creatures import Knight
import mpi

class ArcherKnight(Knight):
	def action(self):
		mpi.send([self.Actions.GetArrows, []], 0)
		(result, code) = mpi.recv(0)[0]
		print mpi.rank, "] I have", result,"arrows."
		mpi.send([self.Actions.FireBow, [10, self.Direction.randomDir()]], 0)
		(result, code) = mpi.recv(0)[0]
		if (result == 1):
			print mpi.rank, "] firing bow attack succeeded!"
		else:
			if (code == self.ResultCodes.game_over):
				print mpi.rank, "] firing bow attack failed because the game was over"
			elif (code == self.ResultCodes.not_enough_arrows):
				print mpi.rank, "] firing bow attack failed because we were out of arrows"
			elif (code == self.ResultCodes.invalid_bow_direction):
				print mpi.rank, "] could not aim bow in that direction"
		mpi.send([self.Actions.FaceHorse, [self.Direction.West]], 0)
		(result, code) = mpi.recv(0)[0]
		if (code == self.ResultCodes.success):
			print mpi.rank, "] set horse's direction!"
		elif (code == self.ResultCodes.invalid_horse_facing):
			print mpi.rank, "] I can't face my horse that way!"
		mpi.send([self.Actions.GetHorseFacing, []], 0)
		(dir, code) = mpi.recv(0)[0]
		mpi.send([self.Actions.GetHorsePosition, []], 0)
		(pos, code) = mpi.recv(0)[0]
		if (code == self.ResultCodes.success):
			print mpi.rank, "] My horse is faced", self.Direction.ToString(dir), "at", "(", pos.x, ",", pos.y, ")"
			print mpi.rank, "] Where is (5, 5)? In relation to me, approx.: ", self.Direction.ToString(pos.toward(self.Position(5, 5)))
		elif (code == self.ResultCodes.game_over):
			print mpi.rank, "] I failed to get my horse's position because the game was over"
		print mpi.rank, "] Attempting to ride horse 2 spaces"
		mpi.send([self.Actions.RideHorse, [2]], 0)
		(result, code) = mpi.recv(0)[0]
		if (code == self.ResultCodes.success):
			print mpi.rank, "] horse trodded successfully"
		elif (code == self.ResultCodes.invalid_horse_path):
			print mpi.rank, "] horse trodded unsuccessfully, he must have run off the board or attempted to move too far at once"
		elif (code == self.ResultCodes.collision):
			print mpi.rank, "] I collided"
		elif (code == self.ResultCodes.game_over):
			print mpi.rank, "] could not ride horse because game over"
		elif (code == self.ResultCodes.defeated):
			print mpi.rank, "] could not ride horse because I have been defeated"