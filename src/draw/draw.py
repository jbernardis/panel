#!/bin/env python

import os
import wx
import json

from bitmaps import BitMaps
from pallette import Pallette
from canvas import Canvas, PENDING_ROW_DELETE, PENDING_ROW_INSERT, PENDING_COL_DELETE, PENDING_COL_INSERT
from pallettemap import PalletteMap
from annotateTurnoutsDlg import AnnotateTurnoutsDlg
from annotateSignalsDlg import AnnotateSignalsDlg
from annotateBlocksDlg import AnnotateBlocksDlg 
from labeldlg import LabelsDlg

from utilities import buildKey
from options import Options

PANEL = (50, 10)

MENU_FILE_NEW = 101
MENU_FILE_OPEN = 102
MENU_FILE_SAVE = 103
MENU_FILE_SAVEAS = 104
MENU_FILE_EXIT = 109

MENU_ANN_TURNOUTS = 201
MENU_ANN_SIGNALS = 202
MENU_ANN_BLOCKS = 203
MENU_ANN_LABELS = 204


class MyFrame(wx.Frame):
	def __init__(self): 

		wx.Frame.__init__(self, None, wx.ID_ANY, "", size=(100, 100))
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		self.currentFile = None
		self.currentStart = [0, 0]
		self.currentEnd = [49, 38]
		self.modified = False
		self.annotations = self.emptyAnnotations()
		self.options = Options()
		
		self.fontTurnouts = wx.Font(10, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		self.colorTurnouts = wx.Colour(255, 128, 20)
		
		self.fontSignals = wx.Font(8, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		self.colorSignals = wx.Colour(255, 255, 0)
		
		self.fontBlocks = wx.Font(14, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		self.colorBlocks = wx.Colour(255, 20, 20)
		
		self.fontLabels = wx.Font(18, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		self.colorLabels = wx.Colour(255, 255, 255)
		
		self.statusBar = self.CreateStatusBar(2)
		
		menuBar = wx.MenuBar()

		# 1st menu from left
		menuFile = wx.Menu()
		menuFile.Append(MENU_FILE_NEW, "New", "Create a new panel")
		menuFile.Append(MENU_FILE_OPEN, "Open", "Open panel files")
		menuFile.AppendSeparator()
		menuFile.Append(MENU_FILE_SAVE, "Save", "Save to current panel files")
		menuFile.Append(MENU_FILE_SAVEAS, "Save As", "Save to specified panel files")
		menuFile.AppendSeparator()
		menuFile.Append(MENU_FILE_EXIT, "Exit", "Exit Program")
		menuBar.Append(menuFile, "File")
		
		menuAnn = wx.Menu()
		menuAnn.Append(MENU_ANN_TURNOUTS, "Turnouts", "Annotate Turnouts")
		menuAnn.Append(MENU_ANN_SIGNALS, "Signals", "Annotate Signals")
		menuAnn.Append(MENU_ANN_BLOCKS, "Blocks", "Annotate Blocks")
		menuAnn.Append(MENU_ANN_LABELS, "Labels", "Define/Modify Labels")
		menuBar.Append(menuAnn, "Annotate")
		
		self.SetMenuBar(menuBar)

		self.Bind(wx.EVT_MENU, self.menuFileNew, id=MENU_FILE_NEW)
		self.Bind(wx.EVT_MENU, self.menuFileOpen, id=MENU_FILE_OPEN)
		self.Bind(wx.EVT_MENU, self.menuFileSave, id=MENU_FILE_SAVE)
		self.Bind(wx.EVT_MENU, self.menuFileSaveAs, id=MENU_FILE_SAVEAS)
		self.Bind(wx.EVT_MENU, self.onClose, id=MENU_FILE_EXIT)
		self.Bind(wx.EVT_MENU, self.menuAnnotateTurnouts, id=MENU_ANN_TURNOUTS)
		self.Bind(wx.EVT_MENU, self.menuAnnotateSignals, id=MENU_ANN_SIGNALS)
		self.Bind(wx.EVT_MENU, self.menuAnnotateBlocks, id=MENU_ANN_BLOCKS)
		self.Bind(wx.EVT_MENU, self.menuAnnotateLabels, id=MENU_ANN_LABELS)

		
		self.bmps = BitMaps(os.path.join("..", "bitmaps"))
		pm = PalletteMap(self.bmps)
		self.pallettes = {
			'master':   pm.getPalletteMaster(),
			'general':  pm.getPalletteGeneral(),
			'signal':   pm.getPalletteSignal(),
			'track':     pm.getPalletteTrack(),
			'turnout':   pm.getPalletteTurnout()
			}
		
		self.pallette = Pallette(self, self.pallettes, self.bmps, self.options)
		
		self.canvas = Canvas(self, self.pallettes, self.bmps)
		self.pallette.enableLeftButtons(not self.canvas.atRightBound())
		self.pallette.enableRightButtons(not self.canvas.atLeftBound())
		
		sz = wx.BoxSizer(wx.HORIZONTAL)
		sz.AddSpacer(20)
		sz.Add(self.pallette)
		sz.AddSpacer(20)
		sz.Add(self.canvas)
		sz.AddSpacer(20)
		
		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(20)
		vsz.Add(sz)
		vsz.AddSpacer(20)
		
		self.SetSizer(vsz)
		self.Fit()
		self.canvas.setCursor()
		self.setWindowTitle()
		
	def onRowInsert(self, _):
		self.setStatusBar("select row to insert before")
		self.canvas.setPendingOperation(PENDING_ROW_INSERT)
		
	def onRowDelete(self, _):
		self.setStatusBar("select row to delete")
		self.canvas.setPendingOperation(PENDING_ROW_DELETE)
		
	def onColInsert(self, _):
		self.setStatusBar("select column to insert before")
		self.canvas.setPendingOperation(PENDING_COL_INSERT)
		
	def onColDelete(self, _):
		self.setStatusBar("select column to delete")
		self.canvas.setPendingOperation(PENDING_COL_DELETE)
		
	def onOperationCancel(self, _):
		self.setStatusBar("")
		self.canvas.setPendingOperation(None)
		
	def pendingOpCompleted(self, row, col, delta):
		self.reKeyAnnotations(row, col, delta)
		
	def reKeyAnnotations(self, row, col, delta):
		# turnouts		
		toList = self.canvas.enumerateTurnouts()
		coords = [x.getPos() for x in toList]
		updateList = {}
		newKeys = []
		for c, r in coords:
			kNew = buildKey(r, c)
			newKeys.append(kNew)
			if row is None and c >= col:
				kOld = buildKey(r, c-delta)
				updateList[kNew] = self.annotations["turnouts"][kOld]
				updateList[kNew]["col"] = c
			elif col is None and r >= row:
				kOld = buildKey(r-delta, c)
				updateList[kNew] = self.annotations["turnouts"][kOld]
				updateList[kNew]["row"] = r
				
		kl = list(self.annotations["turnouts"].keys())
		for k in kl:
			if k not in newKeys:
				del(self.annotations["turnouts"][k])

		if len(updateList) > 0:
			self.annotations["turnouts"].update(updateList)
			self.placeTurnoutLabels()

		sgList = self.canvas.enumerateSignals()
		coords = [x.getPos() for x in sgList]
		updateList = {}
		newKeys = []
		for c, r in coords:
			kNew = buildKey(r, c)
			newKeys.append(kNew)
			if row is None and c >= col:
				kOld = buildKey(r, c-delta)
				updateList[kNew] = self.annotations["signals"][kOld]
				updateList[kNew]["col"] = c
			elif col is None and r >= row:
				kOld = buildKey(r-delta, c)
				updateList[kNew] = self.annotations["signals"][kOld]
				updateList[kNew]["row"] = r
				
		kl = list(self.annotations["signals"].keys())
		for k in kl:
			if k not in newKeys:
				del(self.annotations["signals"][k])
				
		if len(updateList) > 0:
			self.annotations["signals"].update(updateList)
			self.placeSignalLabels()

		beList = self.canvas.enumerateEOBs()
		coords = [x.getPos() for x in beList]
		updateList = {}
		newKeys = []
		for c, r in coords:
			kNew = buildKey(r, c)
			newKeys.append(kNew)
			if row is None and c >= col:
				kOld = buildKey(r, c-delta)
				updateList[kNew] = self.annotations["blocks"]["blockends"][kOld]
				updateList[kNew]["col"] = c
			elif col is None and r >= row:
				kOld = buildKey(r-delta, c)
				updateList[kNew] = self.annotations["blocks"]["blockends"][kOld]
				updateList[kNew]["row"] = r

		kl = list(self.annotations["blocks"]["blockends"].keys())
		for k in kl:
			if k not in newKeys:
				del(self.annotations["blocks"]["blockends"][k])
				
		if len(updateList) > 0:
			self.annotations["blocks"]["blockends"].update(updateList)
		
		self.placeBlockLabels()
		self.placeLabelLabels()

		
	def onPlaceLabels(self, _):
		self.placeLabels()
		
	def onClearLabels(self, _):
		self.canvas.clearAllLabels()
		
	def placeLabels(self):
		self.placeTurnoutLabels()
		self.placeSignalLabels()
		self.placeBlockLabels()
		self.placeLabelLabels()
					
	def placeTurnoutLabels(self):
		lkeys = []
		prefix = "T"
		toList = self.annotations["turnouts"]
		
		for toKey in toList.keys():
			tk = prefix + toKey
			lkeys.append(tk)
			self.canvas.placeLabel(tk,
				toList[toKey]["row"] + toList[toKey]["offsetr"],
				toList[toKey]["col"] + toList[toKey]["offsetc"],
				toList[toKey]["adjx"], toList[toKey]["adjy"],
				toList[toKey]["label"],
				font=self.fontTurnouts, fg=self.colorTurnouts)
		self.canvas.purgeUnusedLabels(lkeys, prefix)
	
	def placeSignalLabels(self):
		lkeys = []
		prefix = "S"
		sgList = self.annotations["signals"]
		for sgKey in sgList.keys():
			sk = prefix + sgKey
			lkeys.append(sk)
			self.canvas.placeLabel(sk, 
				sgList[sgKey]["row"] + sgList[sgKey]["offsetr"],
				sgList[sgKey]["col"] + sgList[sgKey]["offsetc"],
				sgList[sgKey]["adjx"], sgList[sgKey]["adjy"],
				sgList[sgKey]["label"],
				font=self.fontSignals, fg=self.colorSignals)
		self.canvas.purgeUnusedLabels(lkeys, prefix)
	
	def placeBlockLabels(self):
		lkeys = []
		prefix = "B"
		blList = self.annotations["blocks"]["blocks"]
		for blKey in blList.keys():
			bk = prefix + blKey
			lkeys.append(bk)
			self.canvas.placeLabel(bk, 
				blList[blKey]["row"], blList[blKey]["col"],
				blList[blKey]["adjx"], blList[blKey]["adjy"],
				blList[blKey]["label"],
				font=self.fontBlocks, fg=self.colorBlocks)
		self.canvas.purgeUnusedLabels(lkeys, prefix)
	
	def placeLabelLabels(self):
		lkeys = []
		prefix = "L"
		lblList = self.annotations["labels"]
		for i in range(len(lblList)):
			lbl = lblList[i]
			lk = "%s%03d" % (prefix, i)
			lkeys.append(lk)
			self.canvas.placeLabel(lk, 
				lbl["row"], lbl["col"],
				lbl["adjx"], lbl["adjy"],
				lbl["label"],
				font=self.fontLabels, fg=self.colorLabels)
		self.canvas.purgeUnusedLabels(lkeys, prefix)
		
	def placeLabel(self, lx):
		prefix = "L"
		lk = "%s%03d" % (prefix, lx)
		lbl = self.annotations["labels"][lx]
		self.canvas.placeLabel(lk, 
			lbl["row"], lbl["col"],
			lbl["adjx"], lbl["adjy"],
			lbl["label"],
			font=self.fontLabels, fg=self.colorLabels)
		
	def deleteLabel(self, ix):
		prefix = "L"
		lk = "%s%03d" % (prefix, ix)
		self.canvas.deleteLabel(lk)
		
	def onShiftLeft(self, _):
		if self.canvas.shiftCanvas(1, grow=self.pallette.allowGrowthRight()):
			self.setModified()
		self.pallette.enableRightButtons(True)
		self.pallette.enableLeftButtons(not self.canvas.atRightBound())
	
	def onShiftRight(self, _):
		if self.canvas.shiftCanvas(-1):
			self.setModified()
		self.pallette.enableRightButtons(not self.canvas.atLeftBound())
		self.pallette.enableLeftButtons(True)
	
	def onPageLeft(self, _):
		if self.canvas.shiftCanvas(40, grow=self.pallette.allowGrowthRight()):
			self.setModified()
		self.pallette.enableRightButtons(True)
		self.pallette.enableLeftButtons(not self.canvas.atRightBound())
	
	def onPageRight(self, _):
		if self.canvas.shiftCanvas(-40):
			self.setModified()
		self.pallette.enableRightButtons(not self.canvas.atLeftBound())
		self.pallette.enableLeftButtons(True)

	def setWindowTitle(self):
		t = "Panel Editor"
		if self.currentFile:
			t += (" - %s" % self.currentFile)
			
		if self.modified:
			t += " *"
			
		self.SetLabel(t)
		
	def setModified(self, flag = True):
		if self.modified == flag:
			return
		
		self.modified = flag
		self.setWindowTitle()
	
	def menuFileSave(self, _):
		if self.annotationsNotCurrent():
			return
		
		if self.currentFile:
			self.fileSaveAs(self.currentFile)
		else:
			self.saveToOutputFile()
	
	def menuFileSaveAs(self, _):
		if self.annotationsNotCurrent():
			return
		
		self.saveToOutputFile()
		
	def annotationsNotCurrent(self):
		toList = self.canvas.enumerateTurnouts()
		coords = [x.getPos() for x in toList]
		tomissing = []
		tovalid = []
		for c, r in coords:
			k = buildKey(r, c)
			if k not in self.annotations["turnouts"]:
				tomissing.append(k)
			else:
				tovalid.append(k)
				
		toextra = []
		for k in self.annotations["turnouts"]:
			if k not in tovalid:
				toextra.append(k)
				
				
		sgList = self.canvas.enumerateSignals()
		coords = [x.getPos() for x in sgList]
		sgmissing = []
		sgvalid = []
		for c, r in coords:
			k = buildKey(r, c)
			if k not in self.annotations["signals"]:
				sgmissing.append(k)
			else:
				sgvalid.append(k)
		sgextra = []
		for k in self.annotations["signals"]:
			if k not in sgvalid:
				sgextra.append(k)
				
				
		beList = self.canvas.enumerateEOBs()
		coords = [x.getPos() for x in beList]
		bemissing = []
		bevalid = []
		for c, r in coords:
			k = buildKey(r, c)
			if k not in self.annotations["blocks"]["blockends"]:
				bemissing.append(k)
			else:
				bevalid.append(k)
		beextra = []
		for k in self.annotations["blocks"]["blockends"]:
			if k not in bevalid:
				beextra.append(k)
				
				
		message = ""
		stale = False
		
		if len(toextra) > 0 or len(tomissing) > 0:
			stale = True
			message += "turnout annotations out of date:\n"
			if len(toextra) > 0:
				message += "  Annotated but not on screen: %s\n" % ",".join(toextra)
			if len(tomissing) > 0:
				message += "  On screen but not annotated: %s\n" % ",".join(tomissing)
			message += "\n"
		
		if len(sgextra) > 0 or len(sgmissing) > 0:
			stale = True
			message += "signal annotations out of date:\n"
			if len(sgextra) > 0:
				message += "  Annotated but not on screen: %s\n" % ",".join(sgextra)
			if len(sgmissing) > 0:
				message += "  On screen but not annotated: %s\n" % ",".join(sgmissing)
			message += "\n"
		
		if len(beextra) > 0 or len(bemissing) > 0:
			stale = True
			message += "clock end annotations out of date:\n"
			if len(beextra) > 0:
				message += "  Annotated but not on screen: %s\n" % ",".join(beextra)
			if len(bemissing) > 0:
				message += "  On screen but not annotated: %s\n" % ",".join(bemissing)
			message += "\n"
			
		if not stale:
			return False
		
		message += "\nSave anyway?"
		
		dlg = wx.MessageDialog(self, message, 'Annotations out of date', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)
		rc = dlg.ShowModal()
		dlg.Destroy()
		
		return rc == wx.ID_NO

		
	def saveToOutputFile(self):
		wildcard = "Array file (*.arr)|*.arr|All files (*.*)|*.*"
		dlg = wx.FileDialog(
			self, message="Save file as ...", defaultDir=self.options.LastDir(),
			defaultFile="", wildcard=wildcard, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			path = dlg.GetPath()
		dlg.Destroy()
		if rc != wx.ID_OK:
			return
		
		self.fileSaveAs(path)

	def fileSaveAs(self, path):		
		d = self.canvas.getData()
		with open(path, "w") as fp:
			for r in d:
				fp.write("".join(r) + "\n")
				
		self.currentFile = path
		dn = os.path.dirname(path)
		if dn != self.options.LastDir():
			self.options.setLastDir(dn)
			
		self.modified = False
		self.setWindowTitle()	
		self.setStatusBar("File %s saved" % self.currentFile)
		
		annFn = os.path.splitext(self.currentFile)[0] + ".json"
		with open(annFn, 'w') as f:
			json.dump(self.annotations, f, sort_keys=True, indent=4)
				
	def menuFileOpen(self, _):
		if self.modified:
			dlg = wx.MessageDialog(self, "You have unsaved changes.  Are you sure you want to open a new file?",
				'Unsaved Changes', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_INFORMATION)
	
			rc = dlg.ShowModal()
			dlg.Destroy()

			if rc != wx.ID_YES:
				return
			
		wildcard = "Array file (*.arr)|*.arr|All files (*.*)|*.*"
		dlg = wx.FileDialog(self, message="Choose a file", defaultDir=self.options.LastDir(),
			defaultFile="", wildcard=wildcard,
			style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
		
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			path = dlg.GetPath()
		dlg.Destroy()
		if rc != wx.ID_OK:
			return

		self.currentFile = path
		dn = os.path.dirname(path)
		if dn != self.options.LastDir():
			self.options.setLastDir(dn)
			
		self.modified = False
		self.setWindowTitle()	
					
		with open(path) as f:
			inlns = f.readlines()
			
		mapArray = [x.strip() for x in inlns]
		self.canvas.loadCanvas(mapArray, 0)
		self.pallette.enableLeftButtons(not self.canvas.atRightBound())
		self.pallette.enableRightButtons(not self.canvas.atLeftBound())
		
		annFn = os.path.splitext(self.currentFile)[0] + ".json"
		with open(annFn, "r") as fp:
			try:
				self.annotations = json.load(fp)
			except IOError:
				dlg = wx.MessageDialog(self.parent, "Unable to open (%s) for reading" % path,
						'I/O Error', wx.OK | wx.ICON_INFORMATION)
				dlg.ShowModal()
				dlg.Destroy()
				self.annotations = self.emptyAnnotations()

		self.canvas.clearAllLabels()
		if self.options.AutoLabel():
			self.placeLabels()
			
	def emptyAnnotations(self):
		return {"turnouts": {}, 
			"signals": {},
			"blocks": { 
				"blockends": {},
				"blocks": {} },
			"labels": {}
		}

				
	def menuFileNew(self, _):
		if self.modified:
			dlg = wx.MessageDialog(self, "You have unsaved changes.  Are you sure you want to create a new file?",
				'Unsaved Changes', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_INFORMATION)
	
			rc = dlg.ShowModal()
			dlg.Destroy()

			if rc != wx.ID_YES:
				return
			
		self.currentFile = None
		self.modified = False
		self.setWindowTitle()	
		
		cols, rows = self.canvas.getSize()
					
		mapArray = ['.' * cols] * rows
		self.canvas.loadCanvas(mapArray, 0)
		self.pallette.enableLeftButtons(not self.canvas.atRightBound())
		self.pallette.enableRightButtons(not self.canvas.atLeftBound())
		
		self.annotations = {"turnouts": {}, 
			"signals": {},
			"blocks": { 
				"blockends": {},
				"blocks": {} },
			"labels": {} }
		self.canvas.clearAllLabels()
				
		
	def menuAnnotateTurnouts(self, _):
		maxx = self.canvas.getMapSize()[0]-1
		toList = self.canvas.enumerateTurnouts()
		dlg = AnnotateTurnoutsDlg(self, self.bmps, toList, maxx)
		dlg.ShowModal()
		mod = dlg.getStatus()
		dlg.Destroy()
		if (mod):
			self.setModified()
		
	def menuAnnotateSignals(self, _):
		maxx = self.canvas.getMapSize()[0]-1
		sgList = self.canvas.enumerateSignals()
		dlg = AnnotateSignalsDlg(self, self.bmps, sgList, maxx)
		dlg.ShowModal()
		mod = dlg.getStatus()
		dlg.Destroy()
		if (mod):
			self.setModified()	
			
	def menuAnnotateBlocks(self, _):
		maxx = self.canvas.getMapSize()[0]-1
		eobList = self.canvas.enumerateEOBs()
		dlg = AnnotateBlocksDlg(self, self.bmps, eobList, maxx)
		dlg.ShowModal()
		mod = dlg.getStatus()
		dlg.Destroy()
		if (mod):
			self.setModified()	
	
	def menuAnnotateLabels(self, _):
		maxx = self.canvas.getMapSize()[0]-1
		dlg = LabelsDlg(self, self.bmps, maxx)
		dlg.ShowModal()
		mod = dlg.getStatus()
		dlg.Destroy()
		if (mod):
			self.setModified()	
		
	def getCurrentTool(self):
		return self.pallette.getCurrentTool()
	
	def setStatusBar(self, txt, field=0):
		self.statusBar.SetStatusText(txt, field)
		
	def onClose(self, _):
		if self.modified:
			dlg = wx.MessageDialog(self, "Are you sure you want to exit with unsaved changes?",
				'Unsaved Changes', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_INFORMATION)
	
			rc = dlg.ShowModal()
			dlg.Destroy()

			if rc != wx.ID_YES:
				return

		self.Hide()
		self.Destroy()

if __name__ == '__main__':
	class App(wx.App):
		def OnInit(self):
			self.frame = MyFrame()
			self.frame.Show()
			self.SetTopWindow(self.frame)
			return True


	app = App(False)
	app.MainLoop()
