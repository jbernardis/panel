class PalletteMap:
	def __init__(self, bmpRoot):
		self.bmpRoot = bmpRoot
		self.buildPallette()
	
	def getPalletteMaster(self):
		return self.pmaster
	
	def getPalletteGeneral(self):
		return self.pgeneral
	
	def getPalletteTrack(self):
		return self.ptrack
	
	def getPalletteTurnout(self):
		return self.pturnout
		
	def getPalletteSignal(self):
		return self.psignal
		
	def buildPallette(self):
		self.pmaster = {}
		self.pgeneral = {}
		self.pgeneral['.'] = self.bmpRoot.empty
		
		self.pmaster.update(self.pgeneral)

		self.ptrack = {}		
		self.ptrack['a'] = self.bmpRoot.track.straight.normal
		self.ptrack['b'] = self.bmpRoot.track.vertical.normal
		self.ptrack['c'] = self.bmpRoot.track.diagright.normal
		self.ptrack['d'] = self.bmpRoot.track.diagleft.normal
		
		self.ptrack['e'] = self.bmpRoot.track.turnlefteast.normal
		self.ptrack['f'] = self.bmpRoot.track.turnleftwest.normal
		self.ptrack['g'] = self.bmpRoot.track.turnrighteast.normal
		self.ptrack['h'] = self.bmpRoot.track.turnrightwest.normal
		
		self.ptrack['i'] = self.bmpRoot.track.turnleftup.normal
		self.ptrack['j'] = self.bmpRoot.track.turnrightup.normal
		self.ptrack['k'] = self.bmpRoot.track.turnleftdown.normal
		self.ptrack['l'] = self.bmpRoot.track.turnrightdown.normal
		
		self.ptrack['m'] = self.bmpRoot.track.eoblefteast.normal
		self.ptrack['n'] = self.bmpRoot.track.eobleftwest.normal
		self.ptrack['o'] = self.bmpRoot.track.eobrighteast.normal
		self.ptrack['p'] = self.bmpRoot.track.eobrightwest.normal
		
		self.ptrack['q'] = self.bmpRoot.track.eobleftup.normal
		self.ptrack['r'] = self.bmpRoot.track.eobrightup.normal
		self.ptrack['s'] = self.bmpRoot.track.eobleftdown.normal
		self.ptrack['t'] = self.bmpRoot.track.eobrightdown.normal
		
		self.ptrack['u'] = self.bmpRoot.track.eobwest.normal
		self.ptrack['v'] = self.bmpRoot.track.eobeast.normal
		self.ptrack['w'] = self.bmpRoot.track.eobup.normal
		self.ptrack['x'] = self.bmpRoot.track.eobdown.normal
		self.pmaster.update(self.ptrack)
		
		self.pturnout = {}
		self.pturnout['2'] = self.bmpRoot.track.tolefteast.normal.normal
		self.pturnout['3'] = self.bmpRoot.track.toleftwest.normal.normal
		self.pturnout['4'] = self.bmpRoot.track.torighteast.normal.normal
		self.pturnout['5'] = self.bmpRoot.track.torightwest.normal.normal
		self.pmaster.update(self.pturnout)

		self.psignal = {}		
		self.psignal['0'] = self.bmpRoot.signals.east.green
		self.psignal['1'] = self.bmpRoot.signals.west.green
		self.pmaster.update(self.psignal)

