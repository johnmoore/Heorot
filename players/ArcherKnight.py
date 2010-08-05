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
		mpi.send([self.Actions.FireBow, [10]], 0)
		(result, code) = mpi.recv(0)[0]
		if (result == 1):
			print mpi.rank, "] firing bow attack succeeded!"
		else:
			if (code == self.ResultCodes.game_over):
				print mpi.rank, "] firing bow attack failed because the game was over"
			elif (code == self.ResultCodes.not_enough_arrows):
				print mpi.rank, "] firing bow attack failed because we were out of arrows"