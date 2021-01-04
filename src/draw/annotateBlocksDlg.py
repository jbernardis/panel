import wx

from utilities import buildKey		

class AnnotateBlocksDlg(wx.Dialog):
	def __init__(self, parent, bmps, eoblist, maxx):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Block Annotation")
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		self.parent = parent
		self.bmps = bmps
		self.maxx = maxx
		self.annotations = self.parent.annotations["blocks"]
		self.beAnnotations = self.annotations["blockends"]
		self.blAnnotations = self.annotations["blocks"]
		self.modified = False
		sz = wx.BoxSizer(wx.VERTICAL)
		sz.AddSpacer(20)
		font = wx.Font(70, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		
		self.coords = [x.getPos() for x in eoblist]
		validKeys = []
		for c, r in self.coords:
			k = buildKey(r, c)
			validKeys.append(k)
			if k not in self.beAnnotations:
				self.modified = True
				self.beAnnotations[k] = {"blockname": "", "row": r, "col": c}
			
		invalidKeys = []	
		for k in self.beAnnotations:
			if k not in validKeys:
				invalidKeys.append(k)
				
		if len(invalidKeys) > 0:
			self.modified = True
			for k in invalidKeys:
				del(self.beAnnotations[k])
				
		self.blockNames = []
		for k in self.beAnnotations:
			bn = self.beAnnotations[k]["blockname"]
			if bn and bn != "" and bn not in self.blockNames:
				self.blockNames.append(bn)
				if bn not in self.blAnnotations:
					self.addInitialBlock(bn)
					
		bl = list(self.blAnnotations.keys())
		for b in bl:
			if b not in self.blockNames:
				del(self.blAnnotations[b])
				
		self.eobList = ["r: %2d  c: %2d" % (x[1], x[0]) for x in self.coords]
		
		self.lbBlockEnds = wx.ListBox(self, wx.ID_ANY, choices=self.eobList, style=wx.LB_SINGLE, size=(-1, 240))
		self.lbBlockEnds.SetFont(font)
		self.Bind(wx.EVT_LISTBOX, self.onLBBlockEnds, self.lbBlockEnds)

		if len(self.coords) > 0:
			self.lbBlockEnds.SetSelection(0)
			col = self.coords[0][0]
			row = self.coords[0][1]
			self.parent.canvas.setCursorAt(row, col)
			self.currentKey = buildKey(row, col)
			self.currentBlockName = self.beAnnotations[self.currentKey]["blockname"]
			if self.currentBlockName.strip() == "":
				lrow = 0
				lcol = 0
				adjx = 0
				adjy = 0
			else:				
				lrow = self.blAnnotations[self.currentBlockName]["row"]
				lcol = self.blAnnotations[self.currentBlockName]["col"]
				adjx = self.blAnnotations[self.currentBlockName]["adjx"]
				adjy = self.blAnnotations[self.currentBlockName]["adjy"]
		else:
			self.currentBlockName = ""
			lrow = 0
			lcol = 0
			adjx = 0
			adjy = 0
			self.currentKey = None
			
		self.bUpdateDisplay = wx.BitmapButton(self, wx.ID_ANY, self.bmps.update)
		self.Bind(wx.EVT_BUTTON, self.onBUpdateDisplay, self.bUpdateDisplay)
			
		self.cbBlockName = wx.ComboBox(self, wx.ID_ANY, self.currentBlockName, choices=self.blockNames,
						style=wx.CB_DROPDOWN | wx.CB_SORT | wx.TE_PROCESS_ENTER)
		self.Bind(wx.EVT_COMBOBOX, self.onCbBlockName, self.cbBlockName)
		self.cbBlockName.Bind(wx.EVT_KILL_FOCUS, self.onKFBlockName)
				
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.Add(self.lbBlockEnds)
		vsz.AddSpacer(10)
		vsz.Add(self.bUpdateDisplay)
		hsz.Add(vsz)
		hsz.AddSpacer(10)
		
		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.Add(wx.StaticText(self, wx.ID_ANY, "Block Names:"))
		vsz.Add(self.cbBlockName)
				
		self.scRow = wx.SpinCtrl(self, wx.ID_ANY, "0")
		self.scRow.SetRange(0, 39)
		self.scRow.SetValue(lrow)
		self.Bind(wx.EVT_SPINCTRL, self.onSpinRow, self.scRow)
		self.scRow.Bind(wx.EVT_SET_FOCUS, self.onRowColSetFocus)
		
		self.scCol = wx.SpinCtrl(self, wx.ID_ANY, "0")
		self.scCol.SetRange(0, self.maxx)
		self.scCol.SetValue(lcol)
		self.Bind(wx.EVT_SPINCTRL, self.onSpinCol, self.scCol)
		self.scCol.Bind(wx.EVT_SET_FOCUS, self.onRowColSetFocus)
				
		self.scAdjX = wx.SpinCtrl(self, wx.ID_ANY, "0")
		self.scAdjX.SetRange(-100, 100)
		self.scAdjX.SetValue(adjx)
		self.Bind(wx.EVT_SPINCTRL, self.onSpinAdjX, self.scAdjX)
		
		self.scAdjY = wx.SpinCtrl(self, wx.ID_ANY, "0")
		self.scAdjY.SetRange(-100, 100)
		self.scAdjY.SetValue(adjy)
		self.Bind(wx.EVT_SPINCTRL, self.onSpinAdjY, self.scAdjY)
		
		vsz.AddSpacer(20)
		vsz.Add(wx.StaticText(self, wx.ID_ANY, "Row:"))
		vsz.Add(self.scRow)
		vsz.AddSpacer(10)
		vsz.Add(wx.StaticText(self, wx.ID_ANY, "Column:"))
		vsz.Add(self.scCol)
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
		
	def addInitialBlock(self, bn):
		self.blAnnotations[bn] = {"label": bn, "row": 0, "col": 0, "adjx" : 0, "adjy": 0}
		
	def onLBBlockEnds(self, _):
		dx = self.lbBlockEnds.GetSelection()
		if dx == wx.NOT_FOUND:
			return
		
		col = self.coords[dx][0]
		row = self.coords[dx][1]
		self.parent.canvas.setCursorAt(row, col)

		k = buildKey(row, col)
		self.currentBlockName = self.beAnnotations[k]["blockname"].strip()
		self.currentKey = k
		self.updateControls()

		self.cbBlockName.SetValue(self.currentBlockName)
		
	def onBUpdateDisplay(self, _):
		self.parent.placeBlockLabels()
		
	def updateControls(self):
		try:
			bl = self.blAnnotations[self.currentBlockName]		
			lrow = bl["row"]
			lcol = bl["col"]
			adjx = bl["adjx"]
			adjy = bl["adjy"]
			
		except KeyError:
			lrow = 0
			lcol = 0
			adjx = 0
			adjy = 0
			
		self.scRow.SetValue(lrow)
		self.scCol.SetValue(lcol)
		self.scAdjX.SetValue(adjx)
		self.scAdjY.SetValue(adjy)
		
	def onCbBlockName(self, _):
		if self.currentKey:
			self.modified = True
			self.currentBlockName = self.cbBlockName.GetValue()
			self.beAnnotations[self.currentKey]["blockname"] = self.currentBlockName
			self.updateControls()
		
	def onKFBlockName(self, evt):
		if self.currentKey:
			bn = self.cbBlockName.GetValue()
			self.currentBlockName = bn
			if bn != self.beAnnotations[self.currentKey]["blockname"]:
				self.modified = True
				if bn not in self.blockNames:
					self.blockNames.append(bn)
					self.cbBlockName.Append(bn)
					
				self.beAnnotations[self.currentKey]["blockname"] = bn
				if bn not in self.blAnnotations:
					self.addInitialBlock(bn)
		
		evt.Skip()

	def onSpinRow(self, _):
		if self.currentKey:
			self.modified = True
			row = self.scRow.GetValue()
			col = self.scCol.GetValue()
			self.blAnnotations[self.currentBlockName]["row"] = row
			
			self.parent.canvas.setCursorAt(row, col)

	def onSpinCol(self, _):
		if self.currentKey:
			self.modified = True
			row = self.scRow.GetValue()
			col = self.scCol.GetValue()
			self.blAnnotations[self.currentBlockName]["col"] = col
			
			self.parent.canvas.setCursorAt(row, col)
			
	def onRowColSetFocus(self, evt):
		if self.currentKey:
			row = self.scRow.GetValue()
			col = self.scCol.GetValue()
			self.parent.canvas.setCursorAt(row, col)
			
		evt.Skip()
			
	def onSpinAdjX(self, _):
		if self.currentKey:
			self.modified = True
			self.blAnnotations[self.currentBlockName]["adjx"] = self.scAdjX.GetValue()

	def onSpinAdjY(self, _):
		if self.currentKey:
			self.modified = True
			self.blAnnotations[self.currentBlockName]["adjy"] = self.scAdjY.GetValue()
			
	def getStatus(self):
		return self.modified
		
	def onClose(self, _):
		self.EndModal(wx.ID_CANCEL)

		
