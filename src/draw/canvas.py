import wx
BMPDIM = (20, 20)
rowsCanvas = 39
colsCanvas = 50

PENDING_ROW_DELETE = 1
PENDING_ROW_INSERT = 2
PENDING_COL_DELETE = 3
PENDING_COL_INSERT = 4

class CanvasTile:
	def __init__(self, bmp, r, c, cbClick, cbHover):
		self.bmp = bmp
		self.row = r
		self.col = c
		self.cbClick = cbClick
		self.cbHover = cbHover
		self.bmp.Bind(wx.EVT_LEFT_DOWN, self.onClick)
		self.bmp.Bind(wx.EVT_RIGHT_DOWN, self.onRightClick)
		self.bmp.Bind(wx.EVT_MOTION, self.onMotion)
		
	def getBmp(self):
		return self.bmp
		
	def onClick(self, evt):
		self.cbClick(self.bmp, self.row, self.col, True)
		
	def onRightClick(self, evt):
		self.cbClick(self.bmp, self.row, self.col, False)
		
	def onMotion(self, evt):
		self.cbHover(self.col, self.row)

class Turnout:
	def __init__(self, c, pos):
		self.char = c
		self.pos = pos
		
	def getPos(self):
		return self.pos
		
	def __str__(self):
		return "Turnout %s at position: c%d r%d" % (self.char, self.pos[0], self.pos[1])

class Signal:
	def __init__(self, c, pos):
		self.char = c
		self.pos = pos
		
	def getPos(self):
		return self.pos
		
	def __str__(self):
		return "Signal %s at position: c%d r%d" % (self.char, self.pos[0], self.pos[1])
	
class Canvas(wx.Panel):
	def __init__(self, parent, pallettes, bmps):
		wx.Panel.__init__(self, parent, wx.ID_ANY)	
			
		self.SetBackgroundColour(wx.Colour(16, 16, 16))
		self.cvarr = []
		self.offset = 0
		
		self.lastRow = -1
		self.lastCol = -1
		self.cRow = 0
		self.cCol = 0
		self.parent = parent
		self.cursor1 = bmps.cursor
		self.cursor2 = bmps.cursor2
		
		self.pendingOperation = None
		self.stLabels = {}
		self.labelPos = {}
		
		self.bmpCursor = wx.StaticBitmap(self, wx.ID_ANY, self.cursor1, size=(BMPDIM[0]+4, BMPDIM[1]+4), style=0)
		self.currentCursor = self.cursor1
		self.masterPallette = pallettes['master']
		self.cvsz = wx.BoxSizer(wx.VERTICAL)
		self.cvsz.AddSpacer(1)
		
		self.bmpCursor.Bind(wx.EVT_LEFT_DOWN, self.onClick)
		self.bmpCursor.Bind(wx.EVT_RIGHT_DOWN, self.onRightClick)
		
		self.canvasTiles = []
		
		self.tileArray = []
		
		for r in range(rowsCanvas):
			hsz = wx.BoxSizer(wx.HORIZONTAL)
			hsz.AddSpacer(1)
			tileRow = []
			canvasRow = []
			for c in range(colsCanvas):
				b = wx.StaticBitmap(self, wx.ID_ANY, self.masterPallette['.'], size=BMPDIM, style=0)
				ct = CanvasTile(b, r, c, self.canvasClick, self.canvasHover)
				tileRow.append('.')
				canvasRow.append(ct)
				hsz.Add(b, 1, wx.EXPAND|wx.ALL, 1)
				
			self.tileArray.append(tileRow)
			self.cvarr.append(tileRow)
			self.canvasTiles.append(canvasRow)
			hsz.AddSpacer(1)
			self.cvsz.Add(hsz)
			
		self.cvsz.AddSpacer(1)
		self.SetSizer(self.cvsz)

	def getSize(self):
		return colsCanvas, rowsCanvas
				
	def addText(self, r, c, text):
		ct = self.canvasTiles[r][c]
		b = ct.getBmp()
		p = b.GetPosition()
		t = wx.StaticText(self, wx.ID_ANY, text, pos=p)
		t.SetBackgroundColour(wx.Colour(0, 0, 0))
		t.SetForegroundColour(wx.Colour(255, 128, 20))

	def shiftLabels(self):
		for key in self.stLabels:
			self.adjustLabelPosition(key)		
		
	def placeLabel(self, key, row, col, adjx, adjy, text, font=None, fg=None, bg=None):
		if key in self.stLabels.keys():
			st = self.stLabels[key]
			st.SetLabel(text)
		else:
			st = wx.StaticText(self, wx.ID_ANY, text)
			self.stLabels[key] = st
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

		self.labelPos[key] = [row, col, adjx, adjy]
		self.adjustLabelPosition(key)
		
	def deleteLabel(self, key):
		if key in self.stLabels.keys():
			st = self.stLabels[key]
			st.Destroy()
			del(self.stLabels[key])
		
	def adjustLabelPosition(self, key):
		st = self.stLabels[key]
		row, col, adjx, adjy = self.labelPos[key]
		
		c = col - self.offset
		if c < 0 or c >= colsCanvas:
			st.Hide()
		else:
			st.Show()
			ct = self.canvasTiles[row][col-self.offset]
			b = ct.getBmp()
			p = b.GetPosition()
			p[0] += adjx
			p[1] += adjy
		
			st.SetPosition(p)
			st.Refresh()
		

	def purgeUnusedLabels(self, keylist, prefix):
		purgeList = []
		for k in self.stLabels.keys():
			if k.startswith(prefix) and k not in keylist:
				purgeList.append(k)
				
		for k in purgeList:
			try:
				self.stLabels[k].Destroy()
			except:
				pass
			del self.stLabels[k]
			
	def clearAllLabels(self):
		for k in self.stLabels.keys():
			try:
				self.stLabels[k].Destroy()
			except:
				pass
			
		self.stLabels = {}
			
	def enumerateTurnouts(self):
		results = []
		cols = len(self.cvarr[0])
		for r in range(rowsCanvas):
			for c in range(cols):
				t = self.cvarr[r][c]
				if t in [ '2', '3', '4', '5' ]:
					results.append(Turnout(t, (c, r)))
		return results
			
	def enumerateSignals(self):
		results = []
		cols = len(self.cvarr[0])
		for r in range(rowsCanvas):
			for c in range(cols):
				t = self.cvarr[r][c]
				if t in [ '0', '1' ]:
					results.append(Signal(t, (c, r)))
		return results

	def enumerateEOBs(self):
		results = []
		cols = len(self.cvarr[0])
		for r in range(rowsCanvas):
			for c in range(cols):
				t = self.cvarr[r][c]
				if t in [ 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x' ]:
					results.append(Signal(t, (c, r)))
		return results

	def setPendingOperation(self, task=None):
		if task is None:
			self.parent.setStatusBar("")
			self.currentCursor = self.cursor1
			self.bmpCursor.SetBitmap(self.cursor1)
		else:
			self.currentCursor = self.cursor2
			self.bmpCursor.SetBitmap(self.cursor2)
		self.pendingOperation = task
		
	def doDeleteRow(self, row):
		newArr = []
		for r in self.cvarr[0:row]:
			newArr.append([x for x in r])
		for r in self.cvarr[row+1:]:
			newArr.append([x for x in r])
			
		newArr.append(['.'] * len(newArr[0]))
		self.setPendingOperation(None)
		self.loadCanvas(newArr)
		#self.adjustLabelsRow(row, -1)
		self.parent.setModified()
		
	def doDeleteCol(self, col):
		newArr = []
		for r in self.cvarr:
			newArr.append(r[0:col+self.offset] + r[col+self.offset+1:] + ['.'])
		self.setPendingOperation(None)
		self.loadCanvas(newArr)
		#self.adjustLabelsCol(col, -1)
		self.parent.setModified()
		
	def doInsertRow(self, row):
		newArr = []
		for r in self.cvarr[0:row]:
			newArr.append([x for x in r])
		newArr.append(['.'] * len(newArr[0]))
		for r in self.cvarr[row:-1]:
			newArr.append([x for x in r])
			
		self.setPendingOperation(None)
		self.loadCanvas(newArr)
		#self.adjustLabelsRow(row, 1)
		self.parent.setModified()
		
	def doInsertCol(self, col):
		newArr = []
		for r in self.cvarr:
			newArr.append(r[0:col+self.offset] + ['.'] + r[col+self.offset:])
		self.setPendingOperation(None)
		self.loadCanvas(newArr)
		#self.adjustLabelsCol(col+self.offset, 1)
		self.parent.setModified()

	def setCursor(self):			
		ct = self.canvasTiles[self.cRow][self.cCol]
		b = ct.getBmp()
		bx, by = b.GetPosition()
		self.bmpCursor.SetBitmap(self.currentCursor)
		self.bmpCursor.SetPosition((bx-2, by-2))
		
	def setCursorAt(self, row, col):
		c = col - self.offset
		if c < 0:
			self.shiftCanvas(c)
		
		elif c >= colsCanvas:
			self.shiftCanvas(c - colsCanvas + 1)
		
		ct = self.canvasTiles[row][col-self.offset]
		b = ct.getBmp()
		bx, by = b.GetPosition()
		self.bmpCursor.SetBitmap(self.currentCursor)
		self.bmpCursor.SetPosition((bx-2, by-2))
		
	def onClick(self, _):
		ct = self.canvasTiles[self.cRow][self.cCol]
		b = ct.getBmp()
		self.canvasClick(b, self.cRow, self.cCol, True)
			
	def onRightClick(self, _):
		ct = self.canvasTiles[self.cRow][self.cCol]
		b = ct.getBmp()
		self.canvasClick(b, self.cRow, self.cCol, False)
		
	def shiftCanvas(self, delta, grow=False):
		if self.offset + delta + colsCanvas > len(self.cvarr[0]) and not grow:
			if delta > 1:
				delta = len(self.cvarr[0]) - colsCanvas - self.offset
			else:
				return False
		
		self.offset += delta
		if self.offset < 0:
			self.offset = 0
		
		rc = False
		
		if self.offset + colsCanvas > len(self.cvarr[0]):
			add = self.offset + colsCanvas - len(self.cvarr[0])
			rc = True
			for i in range(len(self.cvarr)):
				self.cvarr[i] = self.cvarr[i] + (["."] * add)
				
		self.updateCanvas()
		self.shiftLabels()
		self.updateStatus()
		return rc
	
	def atLeftBound(self):
		return self.offset == 0
	
	def atRightBound(self):
		return self.offset+colsCanvas == len(self.cvarr[0])
			
	def loadCanvas(self, cvarr, offset=None):
		if offset is not None:
			self.offset = offset
			
		self.cvarr = [[x for x in cvline] for cvline in cvarr]
		maxLen = 0;
		for l in self.cvarr:
			if len(l) > maxLen:
				maxLen = len(l)
				
		for i in range(len(self.cvarr)):
			self.cvarr[i] = (self.cvarr[i] + (["."] * maxLen))[:maxLen]
			
		self.updateCanvas()
		
	def updateCanvas(self):
		for r in range(rowsCanvas):
			for c in range(colsCanvas):
				nv = self.cvarr[r][c+self.offset]
				b = self.canvasTiles[r][c].getBmp()
				self.tileArray[r][c] = nv
				self.cvarr[r][c+self.offset] = nv
				b.SetBitmap(self.masterPallette[nv])
		
	def canvasClick(self, bmp, row, col, left):
		if self.pendingOperation is not None:
			if self.pendingOperation == PENDING_ROW_DELETE:
				self.doDeleteRow(row)
				self.parent.pendingOpCompleted(row, None, -1)
			elif self.pendingOperation == PENDING_ROW_INSERT:
				self.doInsertRow(row)
				self.parent.pendingOpCompleted(row, None, 1)
			elif self.pendingOperation == PENDING_COL_DELETE:
				self.doDeleteCol(col)
				self.parent.pendingOpCompleted(None, col+self.offset, -1)
			elif self.pendingOperation == PENDING_COL_INSERT:
				self.doInsertCol(col)
				self.parent.pendingOpCompleted(None, col+self.offset, 1)
			return
			
		self.parent.setModified()
		ct, ctb = self.parent.getCurrentTool()
		if left:
			bmp.SetBitmap(ctb)
			self.tileArray[row][col] = ct
			self.cvarr[row][col+self.offset] = ct
			self.lastRow = row
			self.lastCol = col
		else:
			if row == self.lastRow and col != self.lastCol:
				if self.lastCol < col:
					start = self.lastCol+1
					end = col
				else:
					start = col
					end = self.lastCol-1
				
				self.lastCol = col
					
				for c in range(start, end+1):
					cvt = self.canvasTiles[self.lastRow][c]
					cvt.getBmp().SetBitmap(ctb)
					self.tileArray[self.lastRow][c] = ct
					self.cvarr[self.lastRow][c+self.offset] = ct
			
			elif row != self.lastRow and col == self.lastCol:
				if self.lastRow < row:
					start = self.lastRow+1
					end = row
				else:
					start = row
					end = self.lastRow-1
				
				self.lastRow = row
					
				for r in range(start, end+1):
					cvt = self.canvasTiles[r][self.lastCol]
					cvt.getBmp().SetBitmap(ctb)
					self.tileArray[r][self.lastCol] = ct
					self.cvarr[r][self.lastCol+self.offset] = ct

			else:
				bmp.SetBitmap(ctb)
				self.tileArray[row][col] = ct
				self.cvarr[row][col+self.offset] = ct
				self.lastRow = row
				self.lastCol = col
				
	def canvasHover(self, col, row):
		self.cCol = col
		self.cRow = row
		self.setCursor()
		self.updateStatus()
		
	def updateStatus(self):
		cols = len(self.cvarr[0])
		rows = len(self.cvarr)
		self.parent.setStatusBar(
			"Screen %2d : %2d    Map: %2d : %2d (offset %d)  Full Map Size:  %2d : %2d" %
				(self.cCol, self.cRow, self.cCol+self.offset, self.cRow, self.offset, cols, rows),
			 1)
		
	def getMapSize(self):
		return len(self.cvarr[0]), len(self.cvarr)
		
	def getData(self):
		return self.cvarr
		
