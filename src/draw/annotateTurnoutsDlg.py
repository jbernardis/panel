import wx

def buildKey(r, c):
	return "r%02dc%02d" % (r, c)
		

class AnnotateTurnoutsDlg(wx.Dialog):
	def __init__(self, parent, tolist):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Turnout Annotation")
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		self.parent = parent
		self.annotations = self.parent.annotations["turnouts"]
		
		sz = wx.BoxSizer(wx.VERTICAL)
		sz.AddSpacer(20)
		font = wx.Font(70, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		
		self.coords = [x.getPos() for x in tolist]
		validKeys = []
		for c, r in self.coords:
			k = buildKey(r, c)
			validKeys.append(k)
			if k not in self.annotations:
				self.annotations[k] = {"label": "", "row": r, "col": c, "offsetr": 0, "offsetc": 0}
			
		invalidKeys = []	
		for k in self.annotations:
			if k not in validKeys:
				invalidKeys.append(k)
				
		if len(invalidKeys) > 0:
			for k in invalidKeys:
				del(self.annotations[k])
				
		self.toList = ["r: %2d  c: %2d" % (x[1], x[0]) for x in self.coords]
		
		self.lbTurnouts = wx.ListBox(self, wx.ID_ANY, choices=self.toList, style=wx.LB_SINGLE)
		self.lbTurnouts.SetFont(font)
		self.Bind(wx.EVT_LISTBOX, self.onListBox, self.lbTurnouts)

		if len(self.coords) > 0:
			self.lbTurnouts.SetSelection(0)
			col = self.coords[0][0]
			row = self.coords[0][1]
			self.parent.canvas.setCursorAt(row, col)
			self.currentKey = buildKey(row, col)
			label = self.annotations[self.currentKey]["label"]
			offr = self.annotations[self.currentKey]["offsetr"]
			offc = self.annotations[self.currentKey]["offsetc"]
		else:
			label = ""
			offr = 0
			offc = 0
			self.self.currentKey = None
			
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
			
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(self.lbTurnouts)
		hsz.AddSpacer(10)
		
		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.Add(wx.StaticText(self, wx.ID_ANY, "Label:"))
		vsz.Add(self.tcLabel)
		vsz.AddSpacer(20)
		vsz.Add(wx.StaticText(self, wx.ID_ANY, "Row Offset:"))
		vsz.Add(self.scOffsetR)
		vsz.AddSpacer(20)
		vsz.Add(wx.StaticText(self, wx.ID_ANY, "Column Offset:"))
		vsz.Add(self.scOffsetC)
		
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
		dx = self.lbTurnouts.GetSelection()
		if dx == wx.NOT_FOUND:
			return
		
		col = self.coords[dx][0]
		row = self.coords[dx][1]
		self.parent.canvas.setCursorAt(row, col)

		k = buildKey(row, col)
		lbl = self.annotations[k]["label"]
		offr = self.annotations[k]["offsetr"]						
		offc = self.annotations[k]["offsetc"]						
		self.currentKey = k
		
		self.tcLabel.SetValue(lbl)
		self.scOffsetR.SetValue(offr)
		self.scOffsetC.SetValue(offc)
		
	def onTextLabel(self, _):
		if self.currentKey:
			self.annotations[self.currentKey]["label"] = self.tcLabel.GetValue()

	def onSpinOffsetR(self, _):
		if self.currentKey:
			self.annotations[self.currentKey]["offsetr"] = self.scOffsetR.GetValue()

	def onSpinOffsetC(self, _):
		if self.currentKey:
			self.annotations[self.currentKey]["offsetc"] = self.scOffsetC.GetValue()

		
	def onClose(self, _):
		self.EndModal(wx.ID_CANCEL)

		
