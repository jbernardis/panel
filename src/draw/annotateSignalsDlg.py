import wx

from utilities import buildKey		

class AnnotateSignalsDlg(wx.Dialog):
	def __init__(self, parent, sglist):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Signal Annotation")
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		self.parent = parent
		self.annotations = self.parent.annotations["signals"]
		self.modified = False
		sz = wx.BoxSizer(wx.VERTICAL)
		sz.AddSpacer(20)
		font = wx.Font(70, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		
		self.coords = [x.getPos() for x in sglist]
		validKeys = []
		for c, r in self.coords:
			k = buildKey(r, c)
			validKeys.append(k)
			if k not in self.annotations:
				self.modified = True
				self.annotations[k] = {"label": "", "row": r, "col": c, "offsetr": 0, "offsetc": 0, "adjx": 0, "adjy": 0}
			
		invalidKeys = []	
		for k in self.annotations:
			if k not in validKeys:
				invalidKeys.append(k)
				
		if len(invalidKeys) > 0:
			self.modified = True
			for k in invalidKeys:
				del(self.annotations[k])
				
		self.sgList = ["r: %2d  c: %2d" % (x[1], x[0]) for x in self.coords]
		
		self.lbSignals = wx.ListBox(self, wx.ID_ANY, choices=self.sgList, style=wx.LB_SINGLE, size=(-1, 240))
		self.lbSignals.SetFont(font)
		self.Bind(wx.EVT_LISTBOX, self.onListBox, self.lbSignals)

		if len(self.coords) > 0:
			self.lbSignals.SetSelection(0)
			col = self.coords[0][0]
			row = self.coords[0][1]
			self.parent.canvas.setCursorAt(row, col)
			self.currentKey = buildKey(row, col)
			label = self.annotations[self.currentKey]["label"]
			offr = self.annotations[self.currentKey]["offsetr"]
			offc = self.annotations[self.currentKey]["offsetc"]
			adjx = self.annotations[self.currentKey]["adjx"]
			adjy = self.annotations[self.currentKey]["adjy"]
		else:
			label = ""
			offr = 0
			offc = 0
			adjx = 0
			adjy = 0
			self.self.currentKey = None
			
		self.bUpdateDisplay = wx.Button(self, wx.ID_ANY, "Update Display")
		self.Bind(wx.EVT_BUTTON, self.onBUpdateDisplay, self.bUpdateDisplay)
			
		self.tcLabel = wx.TextCtrl(self, wx.ID_ANY, label, size=(125, -1))
		self.Bind(wx.EVT_TEXT, self.onTextLabel, self.tcLabel)
				
		self.scOffsetR = wx.SpinCtrl(self, wx.ID_ANY, "0")
		self.scOffsetR.SetRange(-2, 2)
		self.scOffsetR.SetValue(offr)
		self.Bind(wx.EVT_SPINCTRL, self.onSpinOffsetR, self.scOffsetR)
		
		self.scOffsetC = wx.SpinCtrl(self, wx.ID_ANY, "0")
		self.scOffsetC.SetRange(-2, 2)
		self.scOffsetC.SetValue(offc)
		self.Bind(wx.EVT_SPINCTRL, self.onSpinOffsetC, self.scOffsetC)
				
		self.scAdjX = wx.SpinCtrl(self, wx.ID_ANY, "0")
		self.scAdjX.SetRange(-100, 100)
		self.scAdjX.SetValue(adjx)
		self.Bind(wx.EVT_SPINCTRL, self.onSpinAdjX, self.scAdjX)
		
		self.scAdjY = wx.SpinCtrl(self, wx.ID_ANY, "0")
		self.scAdjY.SetRange(-100, 100)
		self.scAdjY.SetValue(adjy)
		self.Bind(wx.EVT_SPINCTRL, self.onSpinAdjY, self.scAdjY)
			
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.Add(self.lbSignals)
		vsz.AddSpacer(10)
		vsz.Add(self.bUpdateDisplay)
		hsz.Add(vsz)
		hsz.AddSpacer(10)
		
		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.Add(wx.StaticText(self, wx.ID_ANY, "Label:"))
		vsz.Add(self.tcLabel)
		vsz.AddSpacer(20)
		vsz.Add(wx.StaticText(self, wx.ID_ANY, "Row Offset:"))
		vsz.Add(self.scOffsetR)
		vsz.AddSpacer(10)
		vsz.Add(wx.StaticText(self, wx.ID_ANY, "Column Offset:"))
		vsz.Add(self.scOffsetC)
		vsz.AddSpacer(20)
		vsz.Add(wx.StaticText(self, wx.ID_ANY, "X Adjustment:"))
		vsz.Add(self.scAdjX)
		vsz.AddSpacer(10)
		vsz.Add(wx.StaticText(self, wx.ID_ANY, "Y Adjustment:"))
		vsz.Add(self.scAdjY)
		
		hsz.Add(vsz)
		
		sz.Add(hsz)
		
		sz.AddSpacer(20)
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(sz)
		hsz.AddSpacer(20)
		self.SetSizer(hsz)
		self.Fit()
		
	def onListBox(self, _):
		dx = self.lbSignals.GetSelection()
		if dx == wx.NOT_FOUND:
			return
		
		col = self.coords[dx][0]
		row = self.coords[dx][1]
		self.parent.canvas.setCursorAt(row, col)

		k = buildKey(row, col)
		lbl = self.annotations[k]["label"]
		offr = self.annotations[k]["offsetr"]						
		offc = self.annotations[k]["offsetc"]						
		adjx = self.annotations[k]["adjx"]						
		adjy = self.annotations[k]["adjy"]						
		self.currentKey = k
		
		self.tcLabel.SetValue(lbl)
		self.scOffsetR.SetValue(offr)
		self.scOffsetC.SetValue(offc)
		self.scAdjX.SetValue(adjx)
		self.scAdjY.SetValue(adjy)
		
	def onBUpdateDisplay(self, _):
		self.parent.placeSignalLabels()
		
	def onTextLabel(self, _):
		if self.currentKey:
			nl = self.tcLabel.GetValue()
			if nl != self.annotations[self.currentKey]["label"]:
				print("mod label")
				self.modified = True
				self.annotations[self.currentKey]["label"] = nl

	def onSpinOffsetR(self, _):
		if self.currentKey:
			self.modified = True
			self.annotations[self.currentKey]["offsetr"] = self.scOffsetR.GetValue()

	def onSpinOffsetC(self, _):
		if self.currentKey:
			self.modified = True
			self.annotations[self.currentKey]["offsetc"] = self.scOffsetC.GetValue()
			
	def onSpinAdjX(self, _):
		if self.currentKey:
			self.modified = True
			self.annotations[self.currentKey]["adjx"] = self.scAdjX.GetValue()

	def onSpinAdjY(self, _):
		if self.currentKey:
			self.modified = True
			self.annotations[self.currentKey]["adjy"] = self.scAdjY.GetValue()
			
	def getStatus(self):
		print("returning ", self.modified)
		return self.modified
		
	def onClose(self, _):
		self.EndModal(wx.ID_CANCEL)

		
