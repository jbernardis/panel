import wx

VISIBLELABELS = 10

class LabelsCtrl(wx.ListCtrl):	
	def __init__(self, parent, bmps, labels):
		
		f = wx.Font(12,  wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		dc = wx.ScreenDC()
		dc.SetFont(f)
		fontHeight = dc.GetTextExtent("Xy")[1]

		colWidths = [240, 80, 80, 80, 80]
		colTitles = ["Text", "Column", "X Adj", "Row", "Y Adj"]
		
		totwidth = 20;
		for w in colWidths:
			totwidth += w
		
		wx.ListCtrl.__init__(self, parent, wx.ID_ANY, size=(totwidth, fontHeight*(VISIBLELABELS+1)),
			style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_HRULES|wx.LC_VRULES|wx.LC_SINGLE_SEL
			)

		self.parent = parent	
		self.bmps = bmps
		self.labels = labels	
		
		self.selectedItem = None
		self.il = wx.ImageList(16, 16)
		self.il.Add(self.bmps.selected)
		self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

		self.attr1 = wx.ItemAttr()
		self.attr1.SetBackgroundColour(wx.Colour(218, 238, 193))

		self.attr2 = wx.ItemAttr()
		self.attr2.SetBackgroundColour(wx.Colour(187, 203, 158))

		self.SetFont(f)
		for i in range(len(colWidths)):
			self.InsertColumn(i, colTitles[i])
			self.SetColumnWidth(i, colWidths[i])
		
		self.SetItemCount(len(self.labels))
		
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.doListSelect)
		self.parent.setSelected(False, None, None)

	def doListSelect(self, evt):
		self.assertSelect(evt.GetIndex())
		
	def assertSelect(self, sx):
		x = self.selectedItem
		self.selectedItem = sx
		self.parent.setSelected(True, self.labels[sx]["col"], self.labels[sx]["row"])
		if x is not None:
			self.RefreshItem(x)
		
	def OnGetItemText(self, item, col):
		if col == 0:
			return self.labels[item]["label"]
		elif col == 1:
			return "%3d" % self.labels[item]["col"]
		elif col == 2:
			return "%3d" % self.labels[item]["adjx"]
		elif col == 3:
			return "%3d" % self.labels[item]["row"]
		elif col == 4:
			return "%3d" % self.labels[item]["adjy"]
		else:
			return "??"

	def OnGetItemImage(self, item):
		if item == self.selectedItem:
			return 0
		else:
			return -1
	
	def OnGetItemAttr(self, item):
		if item % 2 == 0:
			return self.attr1
		else:
			return self.attr2
	
	def deleteItem(self):
		if self.selectedItem is None:
			return
		
		if self.selectedItem > len(self.labels):
			return
		
		del self.labels[self.selectedItem]
		self.selectedItem = None
		self.parent.setSelected(False, None, None)
		
		self.SetItemCount(len(self.labels))
		
	def addItem(self, text, col, ax, row, ay):
		self.labels.append({"label": text, "col": col, "adjx": ax, "row": row, "adjy": ay})
		n = len(self.labels)
		self.assertSelect(n-1)
		self.parent.setSelected(True, col, row)
		self.parent.setModified(True)
		self.SetItemCount(n)
		
	def getSelectedIndex(self):
		if self.selectedItem is None:
			return None
		
		if self.selectedItem > len(self.labels):
			return None
		
		return self.selectedItem
# 		
# 	def modifySelectedItem(self, cx, cy, r):
# 		if self.selectedItem is None:
# 			return None
# 		
# 		if self.selectedItem > len(self.circles):
# 			return None
# 		
# 		self.circles[self.selectedItem] = [[cx, cy], r]
# 		self.RefreshItem(self.selectedItem)


class LabelsDlg(wx.Dialog):
	def __init__(self, parent, bmps, maxx):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Labels")
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		self.parent = parent
		self.maxx = maxx
		self.bmps = bmps
		self.annotations = self.parent.annotations["labels"]
		self.modified = False
		
		sz = wx.BoxSizer(wx.VERTICAL)
		sz.AddSpacer(20)
		
		self.lcLabels = LabelsCtrl(self, self.bmps, self.annotations)
		sz.Add(self.lcLabels)
		sz.AddSpacer(10)
		
		bsz = wx.BoxSizer(wx.HORIZONTAL)
		bsz.AddSpacer(10)
		
		b = wx.BitmapButton(self, wx.ID_ANY, bmps.add)
		b.SetToolTip("Add New Label")
		b.Bind(wx.EVT_BUTTON, self.onAdd, b)
		self.bAdd = b
		bsz.Add(b)
		bsz.AddSpacer(20)
		
		b = wx.BitmapButton(self, wx.ID_ANY, bmps.edit)
		b.SetToolTip("Edit Selected Label")
		b.Bind(wx.EVT_BUTTON, self.onEdit, b)
		b.Enable(False)
		self.bEdit = b
		bsz.Add(b)
		bsz.AddSpacer(20)
		
		b = wx.BitmapButton(self, wx.ID_ANY, bmps.delete)
		b.SetToolTip("Delete Selected Label")
		b.Bind(wx.EVT_BUTTON, self.onDel, b)
		b.Enable(False)
		self.bDel = b
		bsz.Add(b)
		
		bsz.AddSpacer(10)
		sz.Add(bsz)
		
		sz.AddSpacer(20)
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(sz)
		hsz.AddSpacer(20)
		self.SetSizer(hsz)
		self.Fit()
		
	def setModified(self, flag=True):
		self.modified = flag
		
	def setSelected(self, flag, col, row):
		if flag:
			self.setCursorAt(row, col)
		if row is not None and col is not None:
			self.bDel.Enable(flag)
			self.bEdit.Enable(flag)
			
	def setCursorAt(self, row, col):
		self.parent.canvas.setCursorAt(row, col)
			
	def onAdd(self, _):
		ix = len(self.annotations)
		self.annotations.append({"label": "", "col": 0, "adjx": 0, "row": 0, "adjy": 0})
		dlg = LabelDlg(self, "", 0, 0, 0, 0, ix, self.maxx)
		rc = dlg.ShowModal()
		del(self.annotations[-1])
		if rc != wx.ID_OK:
			self.parent.deleteLabel(ix)
			dlg.Destroy()
			return

		text, c, ax, r, ay = dlg.getData()
		dlg.Destroy()
		
		self.lcLabels.addItem(text, c, ax, r, ay)
		self.placeLabel(len(self.annotations)-1)
		
	def updateLabel(self, lx, ldata):
		self.annotations[lx]["label"] = ldata[0]
		self.annotations[lx]["col"]   = ldata[1]
		self.annotations[lx]["adjx"]  = ldata[2]
		self.annotations[lx]["row"]   = ldata[3]
		self.annotations[lx]["adjy"]  = ldata[4]
		self.placeLabel(lx)
		
	def placeLabel(self, lx):
		self.parent.placeLabel(lx)
		
	def onEdit(self, _):
		ix = self.lcLabels.getSelectedIndex()
		if ix is None:
			return 
		lbl = self.annotations[ix]
		saveLbl = {}
		saveLbl.update(lbl)
		dlg = LabelDlg(self, lbl["label"], lbl["col"], lbl["adjx"], lbl["row"], lbl["adjy"], ix, self.maxx)
		rc = dlg.ShowModal()
		if rc != wx.ID_OK:
			self.annotations[ix].update(saveLbl)
			self.placeLabel(ix)
			dlg.Destroy()
			return 
		
		modified = dlg.getStatus()
		text, c, ax, r, ay = dlg.getData()
		dlg.Destroy()
		if not modified:
			return
		
		self.annotations[ix]["label"] = text
		self.annotations[ix]["col"]   = c
		self.annotations[ix]["adjx"]  = ax
		self.annotations[ix]["row"]   = r
		self.annotations[ix]["adjy"]  = ay
		self.placeLabel(ix)
		
	def onDel(self, _):
		ix = self.lcLabels.getSelectedIndex()
		if ix is None:
			return 

		dlg = wx.MessageDialog(self,
			"Are you sure you want to delete this label (%s)?" % self.annotations[ix]["label"],
			'Confirm Delete', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_INFORMATION)

		rc = dlg.ShowModal()
		dlg.Destroy()

		if rc != wx.ID_YES:
			return
		
		self.lcLabels.deleteItem()
		self.parent.deleteLabel(ix)
		self.setModified()
		
	def onClose(self, _):
		self.EndModal(wx.ID_CANCEL)
		
	def getStatus(self):
		return self.modified

class LabelDlg(wx.Dialog):
	def __init__(self, parent, text, col, adjx, row, adjy, lx, maxx):
		if text == "":
			title = "Add New Label"
		else:
			title = "Label: %s" % text
			
		wx.Dialog.__init__(self, parent, wx.ID_ANY, title)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		self.parent = parent
		self.bmps = self.parent.bmps
		self.text = text
		self.row = row
		self.col = col
		self.adjx = adjx
		self.adjy = adjy
		self.lx = lx
		self.maxx = maxx
		self.parent.setCursorAt(self.row, self.col)
		
		self.modified = False
		
		self.tcLabel = wx.TextCtrl(self, wx.ID_ANY, text, size=(125, -1))
		self.Bind(wx.EVT_TEXT, self.onTextLabel, self.tcLabel)
				
		self.scRow = wx.SpinCtrl(self, wx.ID_ANY, "%d" % self.row)
		self.scRow.SetRange(0, 39)
		self.scRow.SetValue(self.row)
		self.Bind(wx.EVT_SPINCTRL, self.onSpinRow, self.scRow)
		
		self.scCol = wx.SpinCtrl(self, wx.ID_ANY, "0")
		self.scCol.SetRange(0, self.maxx)
		self.scCol.SetValue(self.col)
		self.Bind(wx.EVT_SPINCTRL, self.onSpinCol, self.scCol)
				
		self.scAdjX = wx.SpinCtrl(self, wx.ID_ANY, "0")
		self.scAdjX.SetRange(-100, 100)
		self.scAdjX.SetValue(self.adjx)
		self.Bind(wx.EVT_SPINCTRL, self.onSpinAdjX, self.scAdjX)
		
		self.scAdjY = wx.SpinCtrl(self, wx.ID_ANY, "0")
		self.scAdjY.SetRange(-100, 100)
		self.scAdjY.SetValue(self.adjy)
		self.Bind(wx.EVT_SPINCTRL, self.onSpinAdjY, self.scAdjY)
		
		sz = wx.BoxSizer(wx.VERTICAL)
		sz.AddSpacer(20)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(wx.StaticText(self, wx.ID_ANY, "Text:", size=(50, -1)))
		hsz.AddSpacer(10)
		hsz.Add(self.tcLabel)
		sz.Add(hsz)
		sz.AddSpacer(20)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(wx.StaticText(self, wx.ID_ANY, "Column:", size=(50, -1)))
		hsz.AddSpacer(10)
		hsz.Add(self.scCol)
		hsz.AddSpacer(20)
		hsz.Add(wx.StaticText(self, wx.ID_ANY, "X Adjustment:"))
		hsz.AddSpacer(10)
		hsz.Add(self.scAdjX)
		sz.Add(hsz)
		sz.AddSpacer(20)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(wx.StaticText(self, wx.ID_ANY, "Row:", size=(50, -1)))
		hsz.AddSpacer(10)
		hsz.Add(self.scRow)
		hsz.AddSpacer(20)
		hsz.Add(wx.StaticText(self, wx.ID_ANY, "Y Adjustment:"))
		hsz.AddSpacer(10)
		hsz.Add(self.scAdjY)
		sz.Add(hsz)
		sz.AddSpacer(20)
		
		bsz = wx.BoxSizer(wx.HORIZONTAL)
		bsz.AddSpacer(10)
		
		b = wx.BitmapButton(self, wx.ID_ANY, self.bmps.ok)
		b.SetToolTip("Save label information")
		b.Bind(wx.EVT_BUTTON, self.onOk, b)
		self.bOk = b
		bsz.Add(b)
		bsz.AddSpacer(20)
		
		b = wx.BitmapButton(self, wx.ID_ANY, self.bmps.cancel)
		b.SetToolTip("Cancel")
		b.Bind(wx.EVT_BUTTON, self.onClose, b)
		self.bCancel = b
		bsz.Add(b)
		bsz.AddSpacer(40)
		
		b = wx.BitmapButton(self, wx.ID_ANY, self.bmps.update)
		b.SetToolTip("Update display")
		b.Bind(wx.EVT_BUTTON, self.onUpdate, b)
		bsz.Add(b)
		
		bsz.AddSpacer(10)
		sz.Add(bsz)
		sz.AddSpacer(20)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(sz)
		hsz.AddSpacer(20)
		self.SetSizer(hsz)
		self.Fit()
		
	def onClose(self, _):
		if self.modified:
			dlg = wx.MessageDialog(self, "Are you sure you want to exit with unsaved changes?",
				'Unsaved Changes', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_INFORMATION)
	
			rc = dlg.ShowModal()
			dlg.Destroy()

			if rc != wx.ID_YES:
				return
			
		self.EndModal(wx.ID_CANCEL)
		
	def onOk(self, _):
		self.EndModal(wx.ID_OK)
		
	def onUpdate(self, _):
		self.parent.updateLabel(self.lx, self.getData())
		
	def onTextLabel(self, _):
		nl = self.tcLabel.GetValue()
		if nl != self.text:
			self.modified = True

	def onSpinRow(self, _):
		self.modified = True
		self.row = self.scRow.GetValue()
		self.parent.setCursorAt(self.row, self.col)

	def onSpinCol(self, _):
		self.modified = True
		self.col = self.scCol.GetValue()
		self.parent.setCursorAt(self.row, self.col)
			
	def onSpinAdjX(self, _):
		self.modified = True

	def onSpinAdjY(self, _):
		self.modified = True
			
	def getStatus(self):
		return self.modified
	
	def getData(self):
		return self.tcLabel.GetValue(), self.scCol.GetValue(), self.scAdjX.GetValue(), \
						self.scRow.GetValue(), self.scAdjY.GetValue()
		
		

