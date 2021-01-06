import wx
from tileTypes import LEFT, RIGHT

class Turnout:
	def __init__(self, tid, te, bmp, cb):
		self.tid = tid
		self.te = te
		self.bmp = bmp
		self.cb = cb
		
		self.bmp.Bind(wx.EVT_LEFT_DOWN, self.onClick)
		self.bmp.Bind(wx.EVT_RIGHT_DOWN, self.onRightClick)
		self.isRev = False
		
	def setReversed(self, flag=True):
		self.isRev = flag
		
	def isReversed(self):
		return self.isRev
		
	def getBmp(self):
		return self.bmp
	
	def getTe(self):
		return self.te

	def onClick(self, evt):
		self.cb(self, LEFT)

	def emulateClick(self):
		self.cb(self, LEFT)
		
	def onRightClick(self, evt):
		self.cb(self, RIGHT)
				
	def emulateRightClick(self):
		self.cb(self, RIGHT)