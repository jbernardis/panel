#!/bin/env python

import os
import wx
import json

from bitmaps import BitMaps
from tileMap import TileMap
from tileTypes import LEFT, ADJ_EAST, ADJ_WEST, ADJ_REVERSED, STYPE_RED, \
		TTYPE_ROUTED, TTYPE_OCCUPIED, TTYPE_NORMAL
from trackelement import TrackElement
from turnout import Turnout
from rrsignal import RRSignal

BMPDIM = (20, 20)

class MapElement:
	def __init__(self, c, pos, label):
		self.char = c
		self.pos = pos
		self.label = label
		
	def getPos(self):
		return self.pos
	
	def samePosition(self, np):
		return np == self.pos
	# wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX | wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN

class Panel(wx.Frame):
	def __init__(self, pnl):
		wx.Frame.__init__(self, None, wx.ID_ANY, pnl["title"], size=(100, 100), style=0)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		self.bmps = BitMaps(os.path.join("..", "bitmaps"))
		self.tileMap = TileMap(self.bmps)
				
		self.fontTurnouts = wx.Font(10, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		self.colorTurnouts = wx.Colour(255, 128, 20)
		
		self.fontSignals = wx.Font(8, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		self.colorSignals = wx.Colour(255, 255, 0)
		
		self.fontBlocks = wx.Font(14, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		self.colorBlocks = wx.Colour(255, 20, 20)
		
		self.fontLabels = wx.Font(18, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		self.colorLabels = wx.Colour(255, 255, 255)

		self.loadData(pnl["filename"])
				
		rows = len(self.mapArray)
		cols = len(self.mapArray[0])
		
		sz = wx.BoxSizer(wx.VERTICAL)
		
		self.panelMap = []
		self.turnouts = []
		self.signals = []
		self.turnoutMap = {} # label to turnout map
		self.signalMap = {}  # label to signal map
		
		for r in range(rows):
			rowsz = wx.BoxSizer(wx.HORIZONTAL)
			rowMap = []
			
			for c in range(cols):
				tid = self.mapArray[r][c]
				tileType = self.tileMap.getTileType(tid)
				if tileType.isSignal():
					b = wx.StaticBitmap(self, wx.ID_ANY, tileType.getBmp(STYPE_RED), size=BMPDIM, style=0)
					sid = len(self.signals)
					sg = RRSignal(sid, tileType, r, c, b, self.clickSignal)
					lbl = self.getSignalLabel(r, c)
					if lbl is not None:
						self.signalMap[lbl] = sg
						
					self.signals.append([sg])
					rowMap.append([b, None])
				else:
					te = TrackElement(tileType, r, c)
					b = wx.StaticBitmap(self, wx.ID_ANY, te.getBmp(), size=BMPDIM, style=0)
					if tileType.isTurnout():
						toid = len(self.turnouts)
						to = Turnout(toid, te, b, self.clickTurnout)
						te.setTurnout(to)
						lbl = self.getTurnoutLabel(r, c)
						if lbl is not None:
							self.turnoutMap[lbl] = to
							
						self.turnouts.append(to)
						b.SetBitmap(te.getBmp())	
					rowMap.append([b, te])

					
				rowsz.Add(b)
				
			sz.Add(rowsz)
			self.panelMap.append(rowMap)

		self.SetSizer(sz)
		self.Fit()

		self.stLabels = []
		for to in self.annotations["turnouts"].values():
			self.placeLabel( 
				to["row"] + to["offsetr"],
				to["col"] + to["offsetc"],
				to["adjx"], to["adjy"],
				to["label"],
				font=self.fontTurnouts, fg=self.colorTurnouts)
			
		for sg in self.annotations["signals"].values():
			self.placeLabel( 
				sg["row"] + sg["offsetr"],
				sg["col"] + sg["offsetc"],
				sg["adjx"], sg["adjy"],
				sg["label"],
				font=self.fontSignals, fg=self.colorSignals)
			
		for bl in self.annotations["blocks"]["blocks"].values():
			self.placeLabel( 
				bl["row"], bl["col"],
				bl["adjx"], bl["adjy"],
				bl["label"],
				font=self.fontBlocks, fg=self.colorBlocks)
			
		for lbl in self.annotations["labels"]:
			self.placeLabel( 
				lbl["row"], lbl["col"],
				lbl["adjx"], lbl["adjy"],
				lbl["label"],
				font=self.fontLabels, fg=self.colorLabels)
	
	def emulateSignalClick(self, lbl, right=False):
		if lbl in self.signalMap.keys():
			sg = self.signalMap[lbl]
			if right:
				sg.emulateRightClick()
			else:
				sg.emulateClick()
				
			return True
		
		return False
	
	def emulateTurnoutClick(self, lbl, right=False):
		if lbl in self.turnoutMap.keys():
			to = self.turnoutMap[lbl]
			if right:
				to.emulateRightClick()
			else:
				to.emulateClick()
				
			return True
		
		return False

	def getSignalLabel(self, r, c):
		sgl = self.annotations["signals"]
		
		for sg in 	sgl.values():
			if sg["row"] == r and sg["col"] == c:
				return sg["label"]
			
		return None

	def getTurnoutLabel(self, r, c):
		tol = self.annotations["turnouts"]
		
		for to in tol.values():
			if to["row"] == r and to["col"] == c:
				return to["label"]
						
		return None
	
	def placeLabel(self, row, col, adjx, adjy, text, font=None, fg=None, bg=None):
		st = wx.StaticText(self, wx.ID_ANY, text)
		self.stLabels.append(st)
			
		b = self.panelMap[row][col][0]
		p = b.GetPosition()
		p[0] += adjx
		p[1] += adjy
		
		st.SetPosition(p)
		
		if font is None:
			st.SetFont(wx.Font(70, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
		else:
			st.SetFont(font)
		
		if fg is None:
			st.SetForegroundColour(wx.Colour(255, 128, 20))
		else:
			st.SetForegroundColour(fg)
			
		if bg is None:
			st.SetBackgroundColour(wx.Colour(0, 0, 0))
		else:
			st.SetBackgroundColour(bg)
		
	def loadData(self, basename):
		with open(os.path.join("..", basename + '.arr')) as f:
			inlns = f.readlines()
			
		arr = [x.strip() for x in inlns]
			
		if len(arr) < 1:
			print("no data in arr file")
			exit()
			
		maxl = len(arr[0])
		for ln in arr:
			maxl = max(maxl, len(ln))
			
		self.mapArray = [a + '.'*(maxl-len(a)) for a in arr]

		with open(os.path.join("..", basename + '.json'), "r") as fp:
			try:
				self.annotations = json.load(fp)
			except IOError:
				self.annotations = {"turnouts": {}, 
						"signals": {},
						"blocks": { 
							"blockends": {},
							"blocks": {} },
						"labels": {} }
		
	def tracksMesh(self, te, lastAdj):
		# return values:
		#		boolean true if tracks mesh, false otherwise
		#		direction from which the tile is entered
		#		boolean true if tile is a turnout and is entered through the reverse leg
		#		<0, 0, >0 indicating vertical movement up, none, down
		nadj = te.getAdjacent(ADJ_EAST)
		if lastAdj == nadj:
			# coming in on the east leg
			if te.isTurnout() and te.isReversed():
				revAdj = te.getAdjacent(ADJ_REVERSED)
				if nadj[0] == revAdj[0]:
					# incoming leg and reversed leg coming from the same direction
					# this is impossible
					return False, None, False, 0
				
				else:
					return True, ADJ_EAST, False, 0
			else:
				return True, ADJ_EAST, False, 0
			
		if lastAdj[0] == 0 and nadj[0] == 0 and nadj[1] is None:
			# allowance for vertical movement
			return True, ADJ_EAST, False, -lastAdj[1]
		
		nadj = te.getAdjacent(ADJ_WEST)
		if lastAdj == nadj:
			# coming in on the east leg
			if te.isTurnout() and te.isReversed():
				revAdj = te.getAdjacent(ADJ_REVERSED)
				if nadj[0] == revAdj[0]:
					# incoming leg and reversed leg coming from the same direction
					# this is impossible
					return False, None, False, 0
				
				else:
					return True, ADJ_WEST, False, 0
				
			else:
				return True, ADJ_WEST, False, 0
		
		if lastAdj[0] == 0 and nadj[0] == 0 and nadj[1] is None:
			# allowance for vertical movement
			return True, ADJ_WEST, False, -lastAdj[1]
		
		if te.isTurnout() and te.isReversed():
			nadj = te.getAdjacent(ADJ_REVERSED)
			if lastAdj == nadj:
				if nadj[0] < 0:
					return True, ADJ_WEST, True, 0
				else:
					return True, ADJ_EAST, True, 0
			
		return False, None, False, 0
		
	def findBlockByName(self, name, rtype):
		eobs = []
		for b in self.annotations["blocks"]["blockends"].values():
			if b["blockname"] == name:
				eobs.append([b["row"], b["col"]])
	
		maxCols = len(self.panelMap[0])-1
		maxRows = len(self.panelMap)-1
					
		for r, c in eobs:
			te = self.panelMap[r][c][1]	
			eadj = te.getAdjacent(ADJ_EAST)
			wadj = te.getAdjacent(ADJ_WEST)
			if eadj == [0, 0]:
				eastbound = False
			else:
				eastbound = True
			if eadj == [0, None]:
				lastAdjRow = 1
			elif wadj == [0, None]:
				lastAdjRow = -1
			else:
				lastAdjRow = None
				
			startRow = r
			startCol = c
			startEast = eastbound
			startVert = lastAdjRow
			
			lastAdj = None

			foundRoute = False			
			while True:
				entryReverse = False
				
				if c < 0 or c > maxCols:
					foundRoute = True
					break
				if r < 0 or r > maxRows:
					foundRoute = True
					break
	
				try:
					te = self.panelMap[r][c][1]
				except IndexError:
					break
				
				if lastAdj:
					mesh, tileEntry, entryReverse, _ = self.tracksMesh(te, lastAdj)
					if not mesh:
						break
					if tileEntry == ADJ_WEST:
						eastbound = True
					elif tileEntry == ADJ_EAST:
						eastbound = False
				
				
				if (not entryReverse) and te.isTurnout() and te.isReversed():		
					adj = te.getAdjacent(ADJ_REVERSED)
				elif eastbound:
					adj = te.getAdjacent(ADJ_EAST)
				else:
					adj = te.getAdjacent(ADJ_WEST)
					
				if adj is None:
					break
				if adj == [0, 0]:
					foundRoute = True
					break
				
				if adj[1] is None:
					adj[1] = lastAdjRow
				
				c += adj[0]
				r += adj[1]
				
				# set up the last adjacency matrix to match against the COMPLEMENT of this movement
				lastAdj = [-x for x in adj]
				lastAdjRow = adj[1]
				
			if foundRoute:
				self.markRoute(startRow, startCol, rtype, startEast, startVert)
				break
				
	def markRoute(self, rStart, cStart, rtype, eb=True, vert=None):
		r = rStart
		c = cStart
		eastbound = eb
		
		lastAdj = None
		lastAdjRow = vert
		
		while True:
			entryReverse = False
			vertDir = 0

			try:
				bmp, te = self.panelMap[r][c]
			except IndexError:
				break
			
			if lastAdj:
				mesh, tileEntry, entryReverse, vertDir = self.tracksMesh(te, lastAdj)
				if not mesh:
					break
				if tileEntry == ADJ_WEST:
					eastbound = True
				elif tileEntry == ADJ_EAST:
					eastbound = False
			
			if rtype == TTYPE_OCCUPIED:
				te.setOccupied(True)
			elif rtype == TTYPE_ROUTED:
				if te.isReversible():
					if vertDir != 0:
						if vertDir > 0: #moving down
							te.setDownRouted()
						else:
							te.setUpRouted()
					else:
						if eastbound:
							te.setEastRouted()
						else:
							te.setWestRouted()
				else:
					te.setRouted(True)
			else:
				te.setOccupied(False)
				te.setRouted(False)
				
			bmp.SetBitmap(te.getBmp())
			
			if (not entryReverse) and te.isTurnout() and te.isReversed():		
				adj = te.getAdjacent(ADJ_REVERSED)
			elif eastbound:
				adj = te.getAdjacent(ADJ_EAST)
			else:
				adj = te.getAdjacent(ADJ_WEST)
				
			if adj is None:
				break
			if adj == [0, 0]:
				break
			if adj[1] is None:
				adj[1] = lastAdjRow
			
			c += adj[0]
			r += adj[1]
			
			# set up the last adjacency matrix to match against the COMPLEMENT of this movement
			lastAdj = [-x for x in adj]
			lastAdjRow = adj[1]
		
	def clickTurnout(self, to, lr):
		bmp = to.getBmp()
		te = to.getTe()
		if lr == LEFT:
			if te.isRouted():
				print("not while routed")
				return 
			
			if te.isOccupied():
				print("not while occupied");
				return 
			
			if to.isReversed():
				to.setReversed(False)
				bmp.SetBitmap(te.getBmp())
			else:
				to.setReversed(True)
				bmp.SetBitmap(te.getBmp())
			
	def clickSignal(self, sg, lr):
		red = sg.isRed()
		
		r, c = sg.getBlockStart()
		te = self.panelMap[r][c][1]
		
		if red:
			# attempt to turn signal green
			# only allowed if block is not otherwise busy
			if te.isOccupied() or te.isRouted():
				print("route is busy")
				return

		red = not red		
		sg.setRed(red)
		self.markRoute(r, c, TTYPE_NORMAL if red else TTYPE_ROUTED, sg.isEast())
		
	def onClose(self, _):
		#pass
		self.Hide()
		#self.Destroy()
