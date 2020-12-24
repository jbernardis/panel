import wx
BMPDIM = (20, 20)

class PalletteTile:
	def __init__(self, bmp, tid, cb):
		self.bmp = bmp
		self.tid = tid
		self.cb = cb
		self.bmp.Bind(wx.EVT_LEFT_DOWN, self.onClick)
		self.bmp.Bind(wx.EVT_RIGHT_DOWN, self.onRightClick)
		
	def onClick(self, evt):
		self.cb(self.tid, True)
		
	def onRightClick(self, evt):
		self.cb(self.tid, False)

class Pallette(wx.Panel):
	def __init__(self, parent, pallettes, bmps):
		wx.Panel.__init__(self, parent, wx.ID_ANY)	
		self.parent = parent
		self.masterPallette = pallettes['master']
		
		sz = wx.BoxSizer(wx.VERTICAL)
		sz.AddSpacer(30)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(10)
		hsz.Add(wx.StaticText(self, wx.ID_ANY, "Current Tool: "))
		self.currentToolBmp = self.masterPallette['.']
		self.bmCurrentTool = wx.StaticBitmap(self, wx.ID_ANY, self.currentToolBmp, size=BMPDIM, style=0)
		self.currentTool = '.'
		hsz.Add(self.bmCurrentTool)
		
		sz.Add(hsz)
		sz.AddSpacer(10)
		
		gbox = wx.StaticBox(self, wx.ID_ANY, " General ")
		topBorder, botBorder = gbox.GetBordersForSizer()
		bsz = wx.BoxSizer(wx.VERTICAL)
		bsz.AddSpacer(topBorder+3)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(15)

		pallette = pallettes['general']
		self.palletteTiles = []
		i = 0		
		for p in pallette.keys():
			b = wx.StaticBitmap(gbox, wx.ID_ANY, pallette[p], size=BMPDIM, style=0)
			self.palletteTiles.append(PalletteTile(b, p, self.palletteClick))
			hsz.Add(b)
			hsz.AddSpacer(3)
			i += 1
			if i % 4 == 0:
				bsz.Add(hsz)
				bsz.AddSpacer(3)
				hsz = wx.BoxSizer(wx.HORIZONTAL)
				hsz.AddSpacer(15)
				
		bsz.Add(hsz)
		bsz.AddSpacer(6)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(15)
		
		pallette = pallettes['signal']
		i = 0		
		for p in pallette.keys():
			b = wx.StaticBitmap(gbox, wx.ID_ANY, pallette[p], size=BMPDIM, style=0)
			self.palletteTiles.append(PalletteTile(b, p, self.palletteClick))
			hsz.Add(b)
			hsz.AddSpacer(3)
			i += 1
			if i % 4 == 0:
				bsz.Add(hsz)
				bsz.AddSpacer(3)
				hsz = wx.BoxSizer(wx.HORIZONTAL)
				hsz.AddSpacer(15)
				
		bsz.Add(hsz)
		
		
		bsz.AddSpacer(botBorder)
		gbox.SetSizer(bsz)
		
		sz.Add(gbox, 0, wx.EXPAND|wx.ALL, 5)
		sz.AddSpacer(20)
				
		ebox = wx.StaticBox(self, wx.ID_ANY, " Track ")
		topBorder, botBorder = ebox.GetBordersForSizer()
		bsz = wx.BoxSizer(wx.VERTICAL)
		bsz.AddSpacer(topBorder+3)
				
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(15)

		pallette = pallettes['track']
		i = 0		
		for p in pallette.keys():
			b = wx.StaticBitmap(ebox, wx.ID_ANY, pallette[p], size=BMPDIM, style=0)
			self.palletteTiles.append(PalletteTile(b, p, self.palletteClick))
			hsz.Add(b)
			hsz.AddSpacer(3)
			i += 1
			if i % 4 == 0:
				bsz.Add(hsz)
				bsz.AddSpacer(3)
				hsz = wx.BoxSizer(wx.HORIZONTAL)
				hsz.AddSpacer(15)
				
		bsz.Add(hsz)
		bsz.AddSpacer(20)
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(15)

		pallette = pallettes['turnout']
		i = 0		
		for p in pallette.keys():
			b = wx.StaticBitmap(ebox, wx.ID_ANY, pallette[p], size=BMPDIM, style=0)
			self.palletteTiles.append(PalletteTile(b, p, self.palletteClick))
			hsz.Add(b)
			hsz.AddSpacer(3)
			i += 1
			if i % 4 == 0:
				bsz.Add(hsz)
				bsz.AddSpacer(3)
				hsz = wx.BoxSizer(wx.HORIZONTAL)
				hsz.AddSpacer(15)
				
		bsz.Add(hsz)
		bsz.AddSpacer(3)
		
		bsz.AddSpacer(botBorder)
		ebox.SetSizer(bsz)
		
		sz.Add(ebox, 0, wx.EXPAND|wx.ALL, 5)

		sz.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)		
		b = wx.BitmapButton(self, wx.ID_ANY, bmps.rowinsert)
		b.SetToolTip("Insert Row")
		b.Bind(wx.EVT_BUTTON, self.parent.onRowInsert, b)
		hsz.Add(b)
		hsz.AddSpacer(10)
		b = wx.BitmapButton(self, wx.ID_ANY, bmps.rowdelete)
		b.SetToolTip("Delete Row")
		b.Bind(wx.EVT_BUTTON, self.parent.onRowDelete, b)
		hsz.Add(b)
		hsz.AddSpacer(20)
		sz.Add(hsz)
		sz.AddSpacer(10)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)		
		b = wx.BitmapButton(self, wx.ID_ANY, bmps.colinsert)
		b.SetToolTip("Insert Column")
		b.Bind(wx.EVT_BUTTON, self.parent.onColInsert, b)
		hsz.Add(b)
		hsz.AddSpacer(10)
		b = wx.BitmapButton(self, wx.ID_ANY, bmps.coldelete)
		b.SetToolTip("Delete Column")
		b.Bind(wx.EVT_BUTTON, self.parent.onColDelete, b)
		hsz.Add(b)
		hsz.AddSpacer(20)
		sz.Add(hsz)
		sz.AddSpacer(10)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)		
		b = wx.BitmapButton(self, wx.ID_ANY, bmps.cancelop)
		b.SetToolTip("Cancel pending operation")
		b.Bind(wx.EVT_BUTTON, self.parent.onOperationCancel, b)
		hsz.Add(b)
		hsz.AddSpacer(20)
		sz.Add(hsz)
		sz.AddSpacer(30)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)		
		b = wx.BitmapButton(self, wx.ID_ANY, bmps.label)
		b.SetToolTip("Place Labels")
		b.Bind(wx.EVT_BUTTON, self.parent.onPlaceLabels, b)
		hsz.Add(b)
		hsz.AddSpacer(10)		
		b = wx.BitmapButton(self, wx.ID_ANY, bmps.eraser)
		b.SetToolTip("Clear Labels")
		b.Bind(wx.EVT_BUTTON, self.parent.onClearLabels, b)
		hsz.Add(b)
		hsz.AddSpacer(20)
		sz.Add(hsz)
		sz.AddSpacer(30)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)		
		b = wx.BitmapButton(self, wx.ID_ANY, bmps.shiftleft)
		b.SetToolTip("Shift Left")
		b.Bind(wx.EVT_BUTTON, self.parent.onShiftLeft, b)
		hsz.Add(b)
		hsz.AddSpacer(10)		
		b = wx.BitmapButton(self, wx.ID_ANY, bmps.shiftright)
		b.SetToolTip("Shift Right")
		b.Bind(wx.EVT_BUTTON, self.parent.onShiftRight, b)
		hsz.Add(b)
		hsz.AddSpacer(20)
		sz.Add(hsz)
		sz.AddSpacer(30)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)		
		b = wx.BitmapButton(self, wx.ID_ANY, bmps.pageleft)
		b.SetToolTip("Page Left")
		b.Bind(wx.EVT_BUTTON, self.parent.onPageLeft, b)
		hsz.Add(b)
		hsz.AddSpacer(10)		
		b = wx.BitmapButton(self, wx.ID_ANY, bmps.pageright)
		b.SetToolTip("Page Right")
		b.Bind(wx.EVT_BUTTON, self.parent.onPageRight, b)
		hsz.Add(b)
		hsz.AddSpacer(20)
		sz.Add(hsz)
		sz.AddSpacer(30)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(sz)
		hsz.AddSpacer(20)
		self.SetSizer(hsz)
		
	def palletteClick(self, tid, left):
		if left:
			self.currentTool = tid
			self.currentToolBmp = self.masterPallette[tid]
			self.bmCurrentTool.SetBitmap(self.currentToolBmp)
			
	def getCurrentTool(self):
		return self.currentTool, self.currentToolBmp
		
		
