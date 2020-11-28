#!/bin/env python


import os
import inspect
import wx

from bitmaps import BitMaps
from szpallette import SzPallette
from szcanvas import SzCanvas, PENDING_ROW_DELETE, PENDING_ROW_INSERT, PENDING_COL_DELETE, PENDING_COL_INSERT
from pallettemap import PalletteMap

PANEL = (50, 10)
cmdFolder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))

MENU_FILE_SAVE = 101
MENU_FILE_SAVEAS = 102
MENU_FILE_OPEN = 103
		
class MyFrame(wx.Frame):
	def __init__(self):

		wx.Frame.__init__(self, None, wx.ID_ANY, "", size=(100, 100))
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		self.currentFile = None
		self.modified = False
		
		self.statusBar = self.CreateStatusBar(2)
		
		menuBar = wx.MenuBar()

		# 1st menu from left
		menuFile = wx.Menu()
		menuFile.Append(MENU_FILE_OPEN, "Open", "Open an array file")
		menuFile.Append(MENU_FILE_SAVE, "Save", "Save to current array file")
		menuFile.Append(MENU_FILE_SAVEAS, "Save As", "Save to a specified array file")
		menuBar.Append(menuFile, "File")
		
		self.SetMenuBar(menuBar)

		self.Bind(wx.EVT_MENU, self.menuFileOpen, id=MENU_FILE_OPEN)
		self.Bind(wx.EVT_MENU, self.menuFileSave, id=MENU_FILE_SAVE)
		self.Bind(wx.EVT_MENU, self.menuFileSaveAs, id=MENU_FILE_SAVEAS)

		
		self.bmps = BitMaps(os.path.join(cmdFolder, "bitmaps"))
		pm = PalletteMap(self.bmps)
		self.pallettes = {
			'master':   pm.getPalletteMaster(),
			'general':  pm.getPalletteGeneral(),
			'signal':   pm.getPalletteSignal(),
			'track':     pm.getPalletteTrack(),
			'turnout':   pm.getPalletteTurnout()
			}
		
		self.szPal = SzPallette(self, self.pallettes, self.bmps)
		
		self.szCanvas = SzCanvas(self, self.pallettes, self.bmps)
		
		sz = wx.BoxSizer(wx.HORIZONTAL)
		sz.AddSpacer(20)
		sz.Add(self.szPal)
		sz.AddSpacer(50)
		sz.Add(self.szCanvas)
		sz.AddSpacer(20)
		
		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(20)
		vsz.Add(sz)
		vsz.AddSpacer(20)
		
		self.SetSizer(vsz)
		self.Fit()
		self.szCanvas.setCursor()
		self.setWindowTitle()
		
	def onRowInsert(self, _):
		self.setStatusBar("select row to insert before")
		self.szCanvas.setPendingOperation(PENDING_ROW_INSERT)
		
	def onRowDelete(self, _):
		self.setStatusBar("select row to delete")
		self.szCanvas.setPendingOperation(PENDING_ROW_DELETE)
		
	def onColInsert(self, _):
		self.setStatusBar("select column to insert before")
		self.szCanvas.setPendingOperation(PENDING_COL_INSERT)
		
	def onColDelete(self, _):
		self.setStatusBar("select column to delete")
		self.szCanvas.setPendingOperation(PENDING_COL_DELETE)
		
	def onOperationCancel(self, _):
		self.setStatusBar("")
		self.szCanvas.setPendingOperation(None)
		
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
			self.getOutputFile()
	
	def menuFileSaveAs(self, _):
		self.getOutputFile()
		
	def getOutputFile(self):
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
		d = self.szCanvas.getData()
		with open(path, "w") as fp:
			for r in d:
				fp.write("".join(r) + "\n")
				
		self.currentFile = path
		self.modified = False
		self.setWindowTitle()	
		self.setStatusBar("File %s saved" % self.currentFile)
				
	def menuFileOpen(self, _):
		if self.modified:
			print("warn about losing changes")
			
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
		self.szCanvas.loadCanvas(mapArray)
		
	def getCurrentTool(self):
		return self.szPal.getCurrentTool()
	
	def setStatusBar(self, txt, field=0):
		self.statusBar.SetStatusText(txt, field)
		
	def onClose(self, _):
		if self.modified:
			print("warn about losing changes")
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
