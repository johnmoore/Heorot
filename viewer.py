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
# along with this program.  If not, see http://www.gnu.org/licenses/

from Tkinter import *
import Tkinter
import os
import time
import threading
import math
import Queue

queue = Queue.Queue()

GAME_BORDER = 10
SQUARE_DIMENSION = 75
DIMENSION_OFFSET = 1
SHOT_DURATION = 1 #Max number of seconds a projectile should have to reach its destination

SQUARE_DIMENSION += DIMENSION_OFFSET

#Find most recent game
GameNum = 1
while (os.path.isfile("Game" + str(GameNum) + ".log")):
	GameNum += 1
GameNum -= 1

#Get a handle on our game log
f = open("Game" + str(GameNum) + ".log", "r")

#Set up initial data
firstline = f.readline() #First line contains dimension info and start time

BoardDimensions = firstline.split("CreateBoard(")[1].split(")")[0].split(",") #width x height
game_start = int(firstline.split("]")[0].split(",")[1].split(".")[0])

#Set up our GUI
top = Tkinter.Tk()
top.resizable(width=NO, height=NO) #Prevent resizing
C = Tkinter.Canvas(top, bg="white", height=(2 * GAME_BORDER) + ((SQUARE_DIMENSION + 0) * int(BoardDimensions[1])), width=(2 * GAME_BORDER) + ((SQUARE_DIMENSION + 0) * int(BoardDimensions[0])), bd=0) #Our canvas, which will contain our grid
top.title("Heorot Battlefield") #Window title
top.wm_iconbitmap("images/Heorot.ico")

players = range(0, int(BoardDimensions[2]) + 1) #Load initial player list

#Pre-load images
FileNames = {}
files = ["boom", "blank", "Dragon0", "Dragon45", "Dragon90", "Dragon135", "Dragon180", "Dragon225", "Dragon270", "Dragon315", "Knight0", "Knight45", "Knight90", "Knight135", "Knight180", "Knight225", "Knight270", "Knight315", "attack/Dragon0", "attack/Dragon45", "attack/Dragon90", "attack/Dragon135", "attack/Dragon180", "attack/Dragon225", "attack/Dragon270", "attack/Dragon315", "attack/Knight0", "attack/Knight45", "attack/Knight90", "attack/Knight135", "attack/Knight180", "attack/Knight225", "attack/Knight270", "attack/Knight315"]
for file in files:
	FileNames["images/" + str(file) + ".gif"] = PhotoImage(file = str("images/" + str(file) + ".gif"))
	label = Label(image=FileNames["images/" + str(file) + ".gif"])
	label.image = FileNames["images/" + str(file) + ".gif"] #keep a reference

game_over = 0
Booms = [] #Player slots currently exploding

#Draws the full grid
def DrawGrid():
	for x in range(GAME_BORDER, (1 * GAME_BORDER) + ((SQUARE_DIMENSION + 0) * (int(BoardDimensions[0]) - 1)) + 1, SQUARE_DIMENSION):
		for y in range(GAME_BORDER, (1 * GAME_BORDER) + ((SQUARE_DIMENSION + 0) * (int(BoardDimensions[1]) - 1)) + 1, SQUARE_DIMENSION):	
			queue.put({"cmd": "line", "args": [x, y, x + SQUARE_DIMENSION, y, x + SQUARE_DIMENSION, y + SQUARE_DIMENSION, x, y + SQUARE_DIMENSION, x, y]})
	queue.put({"cmd": "line", "args": [GAME_BORDER, GAME_BORDER, GAME_BORDER + (SQUARE_DIMENSION * int(BoardDimensions[0])), GAME_BORDER, GAME_BORDER + (SQUARE_DIMENSION * int(BoardDimensions[0])), GAME_BORDER + (SQUARE_DIMENSION * int(BoardDimensions[1])), GAME_BORDER, GAME_BORDER + (SQUARE_DIMENSION * int(BoardDimensions[1])), GAME_BORDER, GAME_BORDER]}) #Redraws the border of the outer edge of the board
	
#Draws a section of the grid. perimeter = 1 to draw neighboring section borders as well.
def DrawGridSection(x, y, perimeter=1):
	if (perimeter == 1):
		DrawGridSection(x + 1, y + 1, 0)
		DrawGridSection(x - 1, y - 1, 0)
		DrawGridSection(x + 1, y - 1, 0)
		DrawGridSection(x - 1, y + 1, 0)
	if (int(x) >= 0 and int(y) >= 0 and int(x) < int(BoardDimensions[0]) and int(y) < int(BoardDimensions[1])):
		x = GAME_BORDER + ((SQUARE_DIMENSION + 0) * float(x))
		y = GAME_BORDER + ((SQUARE_DIMENSION + 0) * float(y))
		queue.put({"cmd": "line", "args": [x, y, x + SQUARE_DIMENSION, y, x + SQUARE_DIMENSION, y + SQUARE_DIMENSION, x, y + SQUARE_DIMENSION, x, y]})
	queue.put({"cmd": "line", "args": [GAME_BORDER, GAME_BORDER, GAME_BORDER + (SQUARE_DIMENSION * int(BoardDimensions[0])), GAME_BORDER, GAME_BORDER + (SQUARE_DIMENSION * int(BoardDimensions[0])), GAME_BORDER + (SQUARE_DIMENSION * int(BoardDimensions[1])), GAME_BORDER, GAME_BORDER + (SQUARE_DIMENSION * int(BoardDimensions[1])), GAME_BORDER, GAME_BORDER]}) #Redraws the border of the outer edge of the board

#Sets a section image to a blank image
def ClearImg(x, y):
	Img(x, y, "images/blank.gif", "")

#Draws an image. If Facing is blank, .gif will not be appended to FilePath.
def Img(x, y, FilePath, facing="North"):
	global FileNames
	global BoardDimensions
	if (int(x) < 0 or int(y) < 0 or int(x) >= int(BoardDimensions[0]) or int(y) >= int(BoardDimensions[1])):
		return 0
	
	#Translate our coordinates into pixels
	x = GAME_BORDER + ((SQUARE_DIMENSION + 0) * float(x))
	y = GAME_BORDER + ((SQUARE_DIMENSION + 0) * float(y))
	
	#Translate our facing into rotation
	offset = 0
	if (facing == "North"):
		offset = 0
	elif (facing == "West"):
		offset = 90
	elif (facing == "South"):
		offset = 180
	elif (facing == "East"):
		offset = 270
	elif (facing == "NorthWest"):
		offset = 45
	elif (facing == "NorthEast"):
		offset = 315
	elif (facing == "SouthEast"):
		offset = 225
	elif (facing == "SouthWest"):
		offset = 135
	elif (facing == ""):
		offset = -1 #Append .gif below

	if not (offset == -1):
		queue.put({"cmd": "img", "args":[int(x) + 1, int(y) + 1, FileNames[FilePath + str(offset) + ".gif"]]})
	else:
		queue.put({"cmd": "img", "args":[int(x) + 1, int(y) + 1, FileNames[FilePath]]})

#Loads a player initially
def LoadPlayer(proc, coords, facing, type):
	global players
	Img(coords[0], coords[1], "images/" + type, facing)
	players[int(proc)] = {"coords": coords, "facing": facing, "type": type, "alive": 1}

#Shoots a projectile from player's position in dir direction dist units. If hit is 1, kills the player at who coordinates and stops there.
def do_Attack(player, power, dir, dist, hit, who):
	global players
	global Booms
	global SHOT_DURATION
	player = players[int(player)]
	if (int(player['alive']) == 0):
		pass
	interval = SHOT_DURATION / (float(dist) * 2) #Interval to pause between half-spaces while animating shot
	px = int(player['coords'][0])
	py = int(player['coords'][1])
	type = player['type']
	
	#Animate the shot by moving it gradually in half-space increments
	hit = 0
	for c in range(1, (int(dist) * 2) + 1):
		i = float(c / 2.0)
		if (i >= 0.5):
			redraw = 0
			ClearImg(px, py)
			if (i <= 1):
				Img(int(player['coords'][0]), int(player['coords'][1]), str("images/" + player['type']), player['facing']) #Redraw the player who is shooting because the projectile image has obscured it
			for PlayerNum in players:
				if not (PlayerNum == 0):
					if (abs(int(PlayerNum['coords'][0]) - float(px)) <= 1.0 and abs(int(PlayerNum['coords'][1]) - float(py)) <= 1.0):
						if not (PlayerNum['alive'] == 0):
							Img(int(PlayerNum['coords'][0]), int(PlayerNum['coords'][1]), str("images/" + PlayerNum['type']), PlayerNum['facing']) #Redraw any player who was not hit by the projectile but who may have been obscured by it
						else:
							for boom in Booms:
								(bx, by) = boom
								if (int(bx) == int(PlayerNum['coords'][0]) and int(by) == int(PlayerNum['coords'][1])):
									Img(int(PlayerNum['coords'][0]), int(PlayerNum['coords'][1]), "images/boom.gif", "") #Redraw any explosion who was not hit by the projectile but who may have been obscured by it
		if (dir == "North" and hit == 0):
			Img(px, py - 0.5, "images/attack/" + type, dir)
			(px, py) = (px, py - 0.5)
		elif (dir == "West" and hit == 0):
			Img(px - 0.5, py, "images/attack/" + type, dir)
			(px, py) = (px - 0.5, py)
		elif (dir == "South" and hit == 0):
			Img(px, py + 0.5, "images/attack/" + type, dir)
			(px, py) = (px, py + 0.5)
		elif (dir == "East" and hit == 0):
			Img(px + 0.5, py, "images/attack/" + type, dir)
			(px, py) = (px + 0.5, py)
		elif (dir == "NorthWest" and hit == 0):
			Img(px - 0.5, py - 0.5, "images/attack/" + type, dir)
			(px, py) = (px - 0.5, py - 0.5)
		elif (dir == "NorthEast" and hit == 0):
			Img(px + 0.5, py - 0.5, "images/attack/" + type, dir)
			(px, py) = (px + 0.5, py - 0.5)
		elif (dir == "SouthEast" and hit == 0):
			Img(px + 0.5, py + 0.5, "images/attack/" + type, dir)
			(px, py) = (px + 0.5, py + 0.5)
		elif (dir == "SouthWest" and hit == 0):
			Img(px - 0.5, py + 0.5, "images/attack/" + type, dir)
			(px, py) = (px - 0.5, py + 0.5)
		DrawGridSection(int(px) + 0, int(py) + 0, 1) #Redraw grid
		if (px == int(who[0]) and py == int(who[1]) and hit == 0): #Hit a player
			Img(int(px), int(py), "images/boom.gif", "")
			Booms.append((px, py))
			time.sleep(1)
			Booms.remove((px, py))
			ClearImg(int(px), int(py))
			hit = 1
		time.sleep(interval)
	if (hit == 0):
		ClearImg(px, py)
	DrawGrid()

#Moves player dist units in facing direction, ending at end coordinates; If collision is 1, collision at who coordinates will occur.
def do_Move(player, dist, facing, end, collision, who):
	global players
	global Booms
	if (int(players[player]['alive']) == 0):
		pass
	type = str(players[player]['type'])
	players[player]['coords'] = (int(players[player]['coords'][0]), int(players[player]['coords'][1]))
	if (int(dist) == 0):
		interval = 1
	else:
		interval = 1 / float(dist)
	
	#Move player gradually
	for i in range(1, int(dist) + 1):
		ClearImg(players[player]['coords'][0], players[player]['coords'][1])
		if (facing == "North"):
			Img(int(players[player]['coords'][0]), int(players[player]['coords'][1]) - 1, "images/" + type, facing)
			players[player]['coords'] = (int(players[player]['coords'][0]), int(players[player]['coords'][1]) - 1)
		elif (facing == "West"):
			Img(int(players[player]['coords'][0]) - 1, int(players[player]['coords'][1]), "images/" + type, facing)
			players[player]['coords'] = (int(players[player]['coords'][0]) - 1, int(players[player]['coords'][1]))
		elif (facing == "South"):
			Img(int(players[player]['coords'][0]), int(players[player]['coords'][1]) + 1, "images/" + type, facing)
			players[player]['coords'] = (int(players[player]['coords'][0]), int(players[player]['coords'][1]) + 1)
		elif (facing == "East"):
			Img(int(players[player]['coords'][0]) + 1, int(players[player]['coords'][1]), "images/" + type, facing)
			players[player]['coords'] = (int(players[player]['coords'][0]) + 1, int(players[player]['coords'][1]))
		elif (facing == "NorthWest"):
			Img(int(players[player]['coords'][0]) - 1, int(players[player]['coords'][1]) - 1, "images/" + type, facing)
			players[player]['coords'] = (int(players[player]['coords'][0]) - 1, int(players[player]['coords'][1]) - 1)
		elif (facing == "NorthEast"):
			Img(int(players[player]['coords'][0]) + 1, int(players[player]['coords'][1]) - 1, "images/" + type, facing)
			players[player]['coords'] = (int(players[player]['coords'][0]) + 1, int(players[player]['coords'][1]) - 1)
		elif (facing == "SouthEast"):
			Img(int(players[player]['coords'][0]) + 1, int(players[player]['coords'][1]) + 1, "images/" + type, facing)
			players[player]['coords'] = (int(players[player]['coords'][0]) + 1, int(players[player]['coords'][1]) + 1)
		elif (facing == "SouthWest"):
			Img(int(players[player]['coords'][0]) - 1, int(players[player]['coords'][1]) + 1, "images/" + type, facing)
			players[player]['coords'] = (int(players[player]['coords'][0]) - 1, int(players[player]['coords'][1]) + 1)
		if (int(players[player]['coords'][0]) == int(who[0]) and int(players[player]['coords'][1]) == int(who[1])): #Collision
			Img(int(who[0]), int(who[1]), "images/boom.gif", "")
			Booms.append((int(who[0]), int(who[1])))
			time.sleep(1)
			Booms.remove((int(who[0]), int(who[1])))
			ClearImg(int(who[0]), int(who[1]))
			break
		time.sleep(interval)

#Faces player in facing direction
def do_SetFacing(player, facing):
	global players
	if (int(players[player]['alive']) == 0):
		return 0
	Img(players[player]['coords'][0], players[player]['coords'][1], str("images/" + players[player]['type']), facing)
	players[player]['facing'] = facing

#Displays winner notice
def do_Winner(a1):
	w = Label(top, text="Winner: " + a1, font=("Helvetica", 20))
	w.pack()
	global game_over
	game_over = 1

#Displays survivor notice
def do_Survivors(a1):
	w = Label(top, text="Survivors: " + a1, font=("Helvetica", 20))
	w.pack()
	global game_over
	game_over = 1

#Processes interface queue
def UpdateInterface():
	C.update()
	top.update()
	top.update_idletasks()
	while not queue.empty():
		item = queue.get()
		if (item['cmd'] == "line"):
			line = C.create_line(int(item['args'][0]), int(item['args'][1]), int(item['args'][2]), int(item['args'][3]), int(item['args'][4]), int(item['args'][5]), int(item['args'][6]), int(item['args'][7]), int(item['args'][8]), int(item['args'][9]), fill="black")
		elif (item['cmd'] == "img"):
			img = C.create_image(item['args'][0], item['args'][1], anchor=NW, image=item['args'][2], state=NORMAL)
			label = Label(image=item['args'][2])
			label.image = item['args'][0] # keep a reference
	C.pack()
	top.update()
	top.update_idletasks()

#Processes the game log
def ProcessGame():
	global players #Initial, blank player list
	global game_start #Time that game actually started
	actions = [] #Where our actions will be queued
	
	#Load our actions into a list
	for line in f:
		proc = line.split(",")[0]
		action_time = int(line.split("]")[0].split(",", 1)[1].split(".")[0])
		command = line.split("] ")[1].split("(", 1)[0]
		args = line.split("(", 1)[1].split(",")
		args[len(args) - 1] = args[len(args) - 1][:len(args[len(args) - 1]) - 2]
		#Accommodate for args will have commas in themselves, such as ordered pairs of coordinates
		num_removed = 0
		for i in range(0, len(args)):
			if (args[i - num_removed].find(")") >= 0):
				args[i - 1 - num_removed] = (args[i - 1 - num_removed].replace("(", ""), args[i - num_removed].replace(")", ""))
				args.remove(args[i - num_removed])
				num_removed += 1
		#Append our action
		actions.append({"proc": proc, "time": action_time, "command": command, "args": args})
	C.update()
	top.update()
	top.update_idletasks()
	for action in actions:
		args = action['args']
		if (action['command'] == "Load"): #Load a player
			LoadPlayer(args[0], args[1], args[2], args[3])
	UpdateInterface()
			
	#Start our countdown
	v = StringVar()
	countdown_start = 3
	w = Label(top, text=str(countdown_start), font=("Helvetica", 20), textvariable=v)
	w.pack()
	for n in range (countdown_start, 0, -1):
		v.set(str(n))
		C.update()
		top.update()
		top.update_idletasks()
		time.sleep(1)
	v.set("")
	
	#Loop through actions
	start = time.time()
	time_offset = start - game_start #Accommodate for differences in time that game was run and time that it is being viewed
	global game_over
	while (game_over == 0):
		for action in actions:
			if ((time.time() - time_offset) >= action['time']):
				delay = abs((int(time.time()) - int(time_offset)) - int(action['time'])) #Amount of time to delay the action with widget.after()
				actions.remove(action) #Remove from queue
				#Queue the action's helper function with widget.after()
				args = action['args']
				if (action['command'] == "EndOfGame"): #Not implemented
					pass
				elif (action['command'] == "Winner"): #Displays "Winner" text; only called if there is a single survivor
					top.after(delay * 1000, do_Winner, str(args[0]))
				elif (action['command'] == "Survivors"): #Displays "Survivor" text; only called if more than one survivor
					survivors = ", ".join(args)
					top.after(delay * 1000, do_Survivors, survivors)
				elif (action['command'] == "Attack"): #Fires a projectile
					thread = threading.Thread(target=do_Attack, args=(int(action['proc']), args[0], args[1], args[2], args[3], args[4]))
					thread.setDaemon(True)
					thread.start()
				elif (action['command'] == "SetFacing"): #Sets a player's facing
					thread = threading.Thread(target=do_SetFacing, args=(int(action['proc']), args[0]))
					thread.setDaemon(True)
					thread.start()
				elif (action['command'] == "Move"): #Moves a player
					thread = threading.Thread(target=do_Move, args=(int(action['proc']), args[0], args[1], args[2], args[3], args[4]))
					thread.setDaemon(True)
					thread.start()
				elif (action['command'] == "Payload"): #Not implemented
					pass
				elif (action['command'] == "Killed"): #Assures that the game display will not be inaccurate if the game log is out of order
					players[int(action['proc'])]['alive'] = 0
		UpdateInterface()
DrawGrid() #Draw the initial grid
C.pack() #Pack the interface

#Start the game processor on another thread as not to interfere with the interface
ProcessGame()

#Start the interface
top.mainloop()