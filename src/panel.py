#!/bin/env python


import os
import inspect

from bitmaps import BitMaps
from tileMap import TileMap
from tileTypes import LEFT, RIGHT, ADJ_EAST, ADJ_WEST, ADJ_REVERSED, STYPE_RED, TTYPE_ROUTED, TTYPE_EASTROUTED, TTYPE_WESTROUTED, TTYPE_OCCUPIED, TTYPE_NORMAL
from trackelement import TrackElement

from turnout import Turnout
from rrsignal import RRSignal

import wx

BMPDIM = (20, 20)
PANEL = (50, 10)
cmdFolder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))

class MyFrame(wx.Frame):
	def __init__(self):
		

		wx.Frame.__init__(self, None, wx.ID_ANY, "Panel", size=(100, 100))
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		self.bmps = BitMaps(os.path.join(cmdFolder, "bitmaps"))
		self.tileMap = TileMap(self.bmps)
		
		with open('panel.arr') as f:
			inlns = f.readlines()
			
		self.mapArray = [x.strip() for x in inlns]
			
		if len(self.mapArray) < 1:
			print("no data in arr file")
			exit()
			
		l = len(self.mapArray[0])
		for ln in self.mapArray:
			if len(ln) != l:
				print("All lines in arr file should be the same length")
				exit()
				
		rows = len(self.mapArray)
		cols = l
		
		sz = wx.BoxSizer(wx.VERTICAL)
		
		self.panelMap = []
		self.turnouts = []
		self.signals = []
		
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
					self.signals.append([sg])
					rowMap.append([b, None])
				else:
					te = TrackElement(tileType, r, c)
					b = wx.StaticBitmap(self, wx.ID_ANY, te.getBmp(), size=BMPDIM, style=0)
					if tileType.isTurnout():
						toid = len(self.turnouts)
						to = Turnout(toid, te, b, self.clickTurnout)
						te.setTurnout(to)
						self.turnouts.append(to)
						b.SetBitmap(te.getBmp())	
					rowMap.append([b, te])

					
				rowsz.Add(b)
				
			sz.Add(rowsz)
			self.panelMap.append(rowMap)
			
		self.SetSizer(sz)
		self.Fit()
		
	def followRoute(self, rStart, cStart, rtype, eastbound=True):
		r = rStart
		c = cStart
		print("follow route starting at %d %d" % (r, c))
		print("rtype = %s" % str(rtype))
		print(eastbound)
		
		while True:
			try:
				bmp, te = self.panelMap[r][c]
			except IndexError:
				break
			
			if rtype == TTYPE_OCCUPIED:
				print("occupied")
				te.setOccupied(True)
			elif rtype == TTYPE_ROUTED:
				if te.isReversible():
					if eastbound:
						print("east routed")
						te.setEastRouted()
					else:
						print("west routed")
						te.setWestRouted()
				else:
					print("routed")
					te.setRouted(True)
			else:
				print("normal")
				te.setOccupied(False)
				te.setRouted(False)
				
			bmp.SetBitmap(te.getBmp())

			if te.isTurnout() and te.isReversed():		
				adj = te.getAdjacent(ADJ_REVERSED)
			elif eastbound:
				adj = te.getAdjacent(ADJ_EAST)
			else:
				adj = te.getAdjacent(ADJ_WEST)
				
			print("next adjacency matrix = %s" % str(adj))
				
			if adj is None:
				break
			if adj == [0, 0]:
				break
			
			c += adj[0]
			r += adj[1]
			print("next location: %d %d" % (r,c))
		
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
# 		else:
# 			self.followRoute(9, 2)
			
	def clickSignal(self, sg, lr):
		sg.setRed(not sg.isRed())
		
		r, c = sg.getBlockStart()
		
		self.followRoute(r, c, TTYPE_NORMAL if sg.isRed() else TTYPE_ROUTED, sg.isEast())
		
		
	def onClose(self, _):
		self.Destroy()

if __name__ == '__main__':
	class App(wx.App):
		def OnInit(self):
			self.frame = MyFrame()
			self.frame.Show()
			self.SetTopWindow(self.frame)
			return True


	app = App(False)
	app.MainLoop()
