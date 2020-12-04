import wx

from utilities import buildKey		

class AnnotateBlocksDlg(wx.Dialog):
	def __init__(self, parent, eoblist):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Block Annotation")
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		self.parent = parent
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
				
		self.eobList = ["r: %2d  c: %2d" % (x[1], x[0]) for x in self.coords]
		
		self.lbBlocks = wx.ListBox(self, wx.ID_ANY, choices=self.eobList, style=wx.LB_SINGLE)
		self.lbBlocks.SetFont(font)
		self.Bind(wx.EVT_LISTBOX, self.onListBox, self.lbBlocks)

		if len(self.coords) > 0:
			self.lbBlocks.SetSelection(0)
			col = self.coords[0][0]
			row = self.coords[0][1]
			self.parent.canvas.setCursorAt(row, col)
			self.currentKey = buildKey(row, col)
			blockName = self.beAnnotations[self.currentKey]["blockname"]
		else:
			blockName = ""
			self.self.currentKey = None
			
		self.tcBlockName = wx.TextCtrl(self, wx.ID_ANY, blockName, size=(125, -1))
		self.Bind(wx.EVT_TEXT, self.onTextBlockName, self.tcBlockName)
				
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(self.lbBlocks)
		hsz.AddSpacer(10)
		
		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.Add(wx.StaticText(self, wx.ID_ANY, "Block Name:"))
		vsz.Add(self.tcBlockName)
		
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
		dx = self.lbBlocks.GetSelection()
		if dx == wx.NOT_FOUND:
			return
		
		col = self.coords[dx][0]
		row = self.coords[dx][1]
		self.parent.canvas.setCursorAt(row, col)

		k = buildKey(row, col)
		lbl = self.beAnnotations[k]["blockname"]
		self.currentKey = k
		
		self.tcBlockName.SetValue(lbl)
		
	def onTextBlockName(self, _):
		if self.currentKey:
			self.modified = True
			self.beAnnotations[self.currentKey]["blockname"] = self.tcBlockName.GetValue()
			
	def getStatus(self):
		return self.modified
		
	def onClose(self, _):
		self.EndModal(wx.ID_CANCEL)

		
