#gameexec.py is based off the Matt Eastman Message Passing Interface (MEMPI) available at http://www.cct.lsu.edu/~sbrandt/mempi/

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

#! /usr/bin/env python
import os
import subprocess
import sys

if len(sys.argv) >= 3 and sys.argv[1] == '-players' and sys.argv[2].isdigit():
	size = (int(sys.argv[2]) * 2) + 1
	args = "python game.py"

else:
	print >>sys.stderr, 'Usage: gameexec -players <num of players>'
	sys.exit(1)

base_port = 10000
procs = []

for rank in range(size):
	os.environ['CCT_MPI_PARAMS'] = '%d,%d,%d' % (rank, size, base_port)
	proc = subprocess.Popen(args)
	procs.append(proc)

for proc in procs:
	proc.wait()
