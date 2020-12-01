import wx
from tileTypes import LEFT, RIGHT, STYPE_GREEN, STYPE_RED
 	
class RRSignal: 
	def __init__(self, sid, tileType, r, c, bmp, cb):
		self.sid = sid
		self.tileType = tileType
		self.row = r
		self.col = c
		self.bmp = bmp
		self.cb = cb
		self.eastbound = tileType.isEast()
		
		self.bmp.Bind(wx.EVT_LEFT_DOWN, self.onClick)
		self.bmp.Bind(wx.EVT_RIGHT_DOWN, self.onRightClick)
		self.red = True
		
	def setRed(self, flag=True):
		self.red = flag
		self.bmp.SetBitmap(self.tileType.getBmp(STYPE_RED if self.red else STYPE_GREEN))
		
	def isRed(self):
		return self.red
	
	def isEast(self):
		return self.eastbound
	
	def getBlockStart(self):
		startTile = self.tileType.getStartTile()
		return self.row+startTile[1], self.col + startTile[0]

	def onClick(self, evt):
		self.cb(self, LEFT)
		
	def onRightClick(self, evt):
		self.cb(self, RIGHT)
