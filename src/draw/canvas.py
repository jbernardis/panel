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
		print("click")
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
		
	def __str__(self):
		return "Signal %s at position: c%d r%d" % (self.char, self.pos[0], self.pos[1])
	
class Canvas(wx.Panel):
	def __init__(self, parent, pallettes, bmps):
		wx.Panel.__init__(self, parent, wx.ID_ANY)	
			
		self.SetBackgroundColour(wx.Colour(16, 16, 16))
		
		self.lastRow = -1
		self.lastCol = -1
		self.cRow = 0
		self.cCol = 0
		self.parent = parent
		self.cursor1 = bmps.cursor
		self.cursor2 = bmps.cursor2
		
		self.pendingOperation = None
		
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
			self.canvasTiles.append(canvasRow)
			hsz.AddSpacer(1)
			self.cvsz.Add(hsz)
			
		self.cvsz.AddSpacer(1)
		self.SetSizer(self.cvsz)
			
				
	def addText(self, r, c, text):
		ct = self.canvasTiles[r][c]
		b = ct.getBmp()
		p = b.GetPosition()
		t = wx.StaticText(self, wx.ID_ANY, text, pos=p)
		t.SetBackgroundColour(wx.Colour(0, 0, 0))
		t.SetForegroundColour(wx.Colour(255, 128, 20))

			
	def enumerateTurnouts(self):
		results = []
		for r in range(rowsCanvas):
			for c in range(colsCanvas):
				t = self.tileArray[r][c]
				if t in [ '2', '3', '4', '5' ]:
					results.append(Turnout(t, (c, r)))
		return results
			
	def enumerateSignals(self):
		results = []
		for r in range(rowsCanvas):
			for c in range(colsCanvas):
				t = self.tileArray[r][c]
				if t in [ '0', '1' ]:
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
		for r in self.tileArray[0:row]:
			newArr.append([x for x in r])
		for r in self.tileArray[row+1:]:
			newArr.append([x for x in r])
			
		newArr.append(['.'] * len(newArr[0]))
		self.setPendingOperation(None)
		self.loadCanvas(newArr)
		self.parent.setModified()
		#a[0:d]+[99]+a[d+1:]
		
	def doDeleteCol(self, col):
		newArr = []
		for r in self.tileArray:
			newArr.append(r[0:col] + r[col+1:] + ['.'])
		self.setPendingOperation(None)
		self.loadCanvas(newArr)
		self.parent.setModified()
		
	def doInsertRow(self, row):
		newArr = []
		for r in self.tileArray[0:row]:
			newArr.append([x for x in r])
		newArr.append(['.'] * len(newArr[0]))
		for r in self.tileArray[row:-1]:
			newArr.append([x for x in r])
			
		self.setPendingOperation(None)
		self.loadCanvas(newArr)
		self.parent.setModified()
		
	def doInsertCol(self, col):
		newArr = []
		for r in self.tileArray:
			newArr.append(r[0:col] + ['.'] + r[col:-1])
		self.setPendingOperation(None)
		self.loadCanvas(newArr)
		self.parent.setModified()

	def setCursor(self):			
		ct = self.canvasTiles[self.cRow][self.cCol]
		b = ct.getBmp()
		bx, by = b.GetPosition()
		self.bmpCursor.SetBitmap(self.currentCursor)
		self.bmpCursor.SetPosition((bx-2, by-2))
		
	def setCursorAt(self, row, col):
		ct = self.canvasTiles[row][col]
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
			
	def loadCanvas(self, cvarr):
		for r in range(rowsCanvas):
			for c in range(colsCanvas):
				nv = cvarr[r][c]
				b = self.canvasTiles[r][c].getBmp()
				self.tileArray[r][c] = nv
				b.SetBitmap(self.masterPallette[nv])
		
	def canvasClick(self, bmp, row, col, left):
		if self.pendingOperation is not None:
			if self.pendingOperation == PENDING_ROW_DELETE:
				self.doDeleteRow(row)
			elif self.pendingOperation == PENDING_ROW_INSERT:
				self.doInsertRow(row)
			elif self.pendingOperation == PENDING_COL_DELETE:
				self.doDeleteCol(col)
			elif self.pendingOperation == PENDING_COL_INSERT:
				self.doInsertCol(col)
			return
			
		self.parent.setModified()
		ct, ctb = self.parent.getCurrentTool()
		if left:
			bmp.SetBitmap(ctb)
			self.tileArray[row][col] = ct
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

			else:
				bmp.SetBitmap(ctb)
				self.tileArray[row][col] = ct
				self.lastRow = row
				self.lastCol = col
				
	def canvasHover(self, col, row):
		self.cCol = col
		self.cRow = row
		self.setCursor()
		self.parent.setStatusBar("%d : %d" % (col, row), 1)
		
	def getData(self):
		return self.tileArray
		
