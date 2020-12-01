#!/bin/env python

import os
import wx
import json

from bitmaps import BitMaps
from szpallette import SzPallette
from canvas import Canvas, PENDING_ROW_DELETE, PENDING_ROW_INSERT, PENDING_COL_DELETE, PENDING_COL_INSERT
from pallettemap import PalletteMap
from annotateTurnoutsDlg import AnnotateTurnoutsDlg

PANEL = (50, 10)

MENU_FILE_SAVE = 101
MENU_FILE_SAVEAS = 102
MENU_FILE_OPEN = 103

MENU_ANN_TURNOUTS = 201
MENU_ANN_SIGNALS = 202

class MyFrame(wx.Frame):
	def __init__(self):

		wx.Frame.__init__(self, None, wx.ID_ANY, "", size=(100, 100))
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		self.currentFile = None
		self.currentStart = [0, 0]
		self.currentEnd = [49, 38]
		self.modified = False
		self.annotations = {}
		
		self.statusBar = self.CreateStatusBar(2)
		
		menuBar = wx.MenuBar()

		# 1st menu from left
		menuFile = wx.Menu()
		menuFile.Append(MENU_FILE_OPEN, "Open", "Open an array file")
		menuFile.Append(MENU_FILE_SAVE, "Save", "Save to current array file")
		menuFile.Append(MENU_FILE_SAVEAS, "Save As", "Save to a specified array file")
		menuBar.Append(menuFile, "File")
		
		menuAnn = wx.Menu()
		menuAnn.Append(MENU_ANN_TURNOUTS, "Turnouts", "Annotate Turnouts")
		menuAnn.Append(MENU_ANN_SIGNALS, "Signals", "Annotate Signals")
		menuBar.Append(menuAnn, "Annotate")
		
		self.SetMenuBar(menuBar)

		self.Bind(wx.EVT_MENU, self.menuFileOpen, id=MENU_FILE_OPEN)
		self.Bind(wx.EVT_MENU, self.menuFileSave, id=MENU_FILE_SAVE)
		self.Bind(wx.EVT_MENU, self.menuFileSaveAs, id=MENU_FILE_SAVEAS)
		self.Bind(wx.EVT_MENU, self.menuAnnotateTurnouts, id=MENU_ANN_TURNOUTS)
		self.Bind(wx.EVT_MENU, self.menuAnnotateSignals, id=MENU_ANN_SIGNALS)

		
		self.bmps = BitMaps(os.path.join("..", "bitmaps"))
		pm = PalletteMap(self.bmps)
		self.pallettes = {
			'master':   pm.getPalletteMaster(),
			'general':  pm.getPalletteGeneral(),
			'signal':   pm.getPalletteSignal(),
			'track':     pm.getPalletteTrack(),
			'turnout':   pm.getPalletteTurnout()
			}
		
		self.szPal = SzPallette(self, self.pallettes, self.bmps)
		
		self.canvas = Canvas(self, self.pallettes, self.bmps)
		
		sz = wx.BoxSizer(wx.HORIZONTAL)
		sz.AddSpacer(20)
		sz.Add(self.szPal)
		sz.AddSpacer(50)
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
		if self.currentFile:
			self.fileSaveAs(self.currentFile)
		else:
			self.saveToOutputFile()
	
	def menuFileSaveAs(self, _):
		self.saveToOutputFile()
		
	def saveToOutputFile(self):
		wildcard = "Array file (*.arr)|*.arr|All files (*.*)|*.*"
		dlg = wx.FileDialog(
			self, message="Save file as ...", defaultDir=os.getcwd(),
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
		dlg = wx.FileDialog(self, message="Choose a file", defaultDir=os.getcwd(),
			defaultFile="", wildcard=wildcard,
			style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
		
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			path = dlg.GetPath()
		dlg.Destroy()
		if rc != wx.ID_OK:
			return

		self.currentFile = path
		self.modified = False
		self.setWindowTitle()	
					
		with open(path) as f:
			inlns = f.readlines()
			
		mapArray = [x.strip() for x in inlns]
		self.canvas.loadCanvas(mapArray)
		
		annFn = os.path.splitext(self.currentFile)[0] + ".json"
		with open(annFn, "r") as fp:
			try:
				self.annotations = json.load(fp)
			except IOError:
				dlg = wx.MessageDialog(self.parent, "Unable to open (%s) for reading" % path,
						'I/O Error', wx.OK | wx.ICON_INFORMATION)
				dlg.ShowModal()
				dlg.Destroy()
				self.annotations = {"turnouts": {}, "signals": {}, "blocks": {}, "labels": {} }

		
	def menuAnnotateTurnouts(self, _):
		toList = self.canvas.enumerateTurnouts()
		dlg = AnnotateTurnoutsDlg(self, toList)
		dlg.ShowModal()
		dlg.Destroy()
		self.setModified()
		
	def menuAnnotateSignals(self, _):
		sgList = self.canvas.enumerateSignals()
		print("%d signals found" % len(sgList))
		for sg in sgList:
			print(str(sg))
			
		self.canvas.addText(23, 27, "Sample Text")
		
		
	def getCurrentTool(self):
		return self.szPal.getCurrentTool()
	
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
