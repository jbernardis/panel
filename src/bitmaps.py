import wx
import os

class Node:
	def __init__(self):
		pass

class BitMaps:
	def __init__(self, idir):
		self.loadDir(idir, self)

	def loadDir(self, idir, parent):
		try:
			pdir = os.path.expandvars(idir)
			l = os.listdir(pdir)
		except:
			print ("Unable to get listing from directory: %s" % idir)
			return

		subdirs = []
		for f in l:
			fqp = os.path.join(pdir, f)
			if os.path.isdir(fqp):
				subdirs.append([f, fqp])
			elif f.lower().endswith(".bmp"):
				b = os.path.splitext(os.path.basename(f))[0]

				fp = os.path.join(pdir, f)
				bmp = wx.Image(fp, wx.BITMAP_TYPE_BMP).ConvertToBitmap()
				
				nm = b

				setattr(parent, nm, bmp)
			elif f.lower().endswith(".png"):
				b = os.path.splitext(os.path.basename(f))[0]

				fp = os.path.join(pdir, f)
				bmp = wx.Image(fp, wx.BITMAP_TYPE_PNG).ConvertToBitmap()
				
				nm = b

				setattr(parent, nm, bmp)
				
		for n, d in subdirs:
			nd = Node()
			setattr(parent, n, nd)
			self.loadDir(d, nd)
					
