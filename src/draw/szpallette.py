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

class SzPallette(wx.BoxSizer):
	def __init__(self, parent, pallettes, bmps):
		self.parent = parent
		self.masterPallette = pallettes['master']
		wx.BoxSizer.__init__(self, wx.VERTICAL)
		self.AddSpacer(10)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(10)
		hsz.Add(wx.StaticText(self.parent, wx.ID_ANY, "Current Tool: "))
		self.currentToolBmp = self.masterPallette['.']
		self.bmCurrentTool = wx.StaticBitmap(self.parent, wx.ID_ANY, self.currentToolBmp, size=BMPDIM, style=0)
		self.currentTool = '.'
		hsz.Add(self.bmCurrentTool)
		
		self.Add(hsz)
		self.AddSpacer(10)
		
		gbox = wx.StaticBox(self.parent, wx.ID_ANY, " General ")
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
		
		self.Add(gbox, 0, wx.EXPAND|wx.ALL, 5)
		self.AddSpacer(20)
				
		ebox = wx.StaticBox(self.parent, wx.ID_ANY, " Track ")
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
		
		self.Add(ebox, 0, wx.EXPAND|wx.ALL, 5)

		self.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)		
		b = wx.BitmapButton(self.parent, wx.ID_ANY, bmps.rowinsert)
		b.SetToolTip("Insert Row")
		b.Bind(wx.EVT_BUTTON, self.parent.onRowInsert, b)
		hsz.Add(b)
		hsz.AddSpacer(10)
		b = wx.BitmapButton(self.parent, wx.ID_ANY, bmps.rowdelete)
		b.SetToolTip("Delete Row")
		b.Bind(wx.EVT_BUTTON, self.parent.onRowDelete, b)
		hsz.Add(b)
		hsz.AddSpacer(20)
		self.Add(hsz)
		self.AddSpacer(10)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)		
		b = wx.BitmapButton(self.parent, wx.ID_ANY, bmps.colinsert)
		b.SetToolTip("Insert Column")
		b.Bind(wx.EVT_BUTTON, self.parent.onColInsert, b)
		hsz.Add(b)
		hsz.AddSpacer(10)
		b = wx.BitmapButton(self.parent, wx.ID_ANY, bmps.coldelete)
		b.SetToolTip("Delete Column")
		b.Bind(wx.EVT_BUTTON, self.parent.onColDelete, b)
		hsz.Add(b)
		hsz.AddSpacer(20)
		self.Add(hsz)
		self.AddSpacer(10)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)		
		b = wx.BitmapButton(self.parent, wx.ID_ANY, bmps.cancelop)
		b.SetToolTip("Cancel pending operation")
		b.Bind(wx.EVT_BUTTON, self.parent.onOperationCancel, b)
		hsz.Add(b)
		hsz.AddSpacer(20)
		self.Add(hsz)
		
	def palletteClick(self, tid, left):
		if left:
			self.currentTool = tid
			self.currentToolBmp = self.masterPallette[tid]
			self.bmCurrentTool.SetBitmap(self.currentToolBmp)
		else:
			print("right click on (%s)" % tid)
			
	def getCurrentTool(self):
		return self.currentTool, self.currentToolBmp
		
		
