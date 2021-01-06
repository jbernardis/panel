import wx
import json
from panel import Panel

class MyFrame(wx.Frame):
	def __init__(self, cfgfn):
		wx.Frame.__init__(self, None, wx.ID_ANY, "Dispatcher", size=(100, 100), style=0)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		with open(cfgfn, "r") as fp:
			try:
				self.config = json.load(fp)
			except IOError:
				print("Unable to open configuration file: %s" % cfgfn)
				return False

		self.panels = {}
		n = 0
		psz = wx.BoxSizer(wx.HORIZONTAL)
		psz.AddSpacer(20)
		first = True
		self.activePanel = None
		for p in self.config:
			err = False
			if not "title" in p.keys():
				print("Missing \"title\" in configuration file for entry %d" % n)
				err = True
			if not "filename" in p.keys():
				print("Missing \"filename\" in configuration file for entry %d" % n)
				err = True
				
			if err:
				print("  skipping ...")
			else:
				pnl = Panel(p)
				self.panels[p["title"]] = pnl
				if first:
					first = False
					self.activePanel = pnl
					
				b = wx.Button(self, wx.ID_ANY, p["title"])
				b.MyPanel = pnl
				self.Bind(wx.EVT_BUTTON, self.onPanelButton, b)
				psz.Add(b)
				psz.AddSpacer(10)
				
			n += 1
			
		psz.AddSpacer(20)
			
		sz = wx.BoxSizer(wx.VERTICAL)
		sz.AddSpacer(20)
		sz.Add(psz)
		
		sz.AddSpacer(10)
		b = wx.Button(self, wx.ID_ANY, "Action")
		self.Bind(wx.EVT_BUTTON, self.onAction, b)
		sz.Add(b)
		
		sz.AddSpacer(10)
		b = wx.Button(self, wx.ID_ANY, "Exit")
		self.Bind(wx.EVT_BUTTON, self.onClose, b)
		sz.Add(b)
		
		sz.AddSpacer(20)
		
		self.SetSizer(sz)
		self.Fit()
		wsize = self.GetSize()
		self.SetPosition((0, 0))
		for p in self.panels.values():
			p.SetPosition((0, wsize[1]))
			
		if len(self.panels) == 0:
			print("No panels loaded")
		else:
			self.activePanel.Show()			
		
	def onPanelButton(self, evt):
		pnl = evt.GetEventObject().MyPanel
		if self.activePanel == pnl:
			return 
		
		if self.activePanel is not None:
			self.activePanel.Hide()

		pnl.Show()
		self.activePanel = pnl
		
	def onAction(self, _):
		print("action")
		self.panels["Nassau"].emulateSignalClick("2")
		self.panels["Port"].emulateTurnoutClick("6")
			
	def onClose(self, _):
		for p in self.panels.values():
			try:
				p.Hide()
			except:
				pass
			try:
				p.Destroy()
			except:
				pass
			
		try:
			self.Hide()
		except:
			pass
		
		try:
			self.Destroy()
		except:
			pass

	
if __name__ == '__main__':
	class App(wx.App):
		def OnInit(self):
			f = MyFrame("panels.json")
			f.Show()
			return True


	app = App(False)
	app.MainLoop()
