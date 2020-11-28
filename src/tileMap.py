from tileTypes import SimpleTile, TrackTile, RevTrackTile, TurnoutTile, SignalTile

class TileMap:
	def __init__(self, bmpRoot):
		self.bmpRoot = bmpRoot
		self.buildMap()
	
	def isTurnout(self, tid):
		return self.tmap[tid].isTurnout()
	
	def isSignal(self, tid):
		return self.tmap[tid].isSignal()
	
	def getTileType(self, tid):
		return self.tmap[tid]
		
	def buildMap(self):
		self.tmap = {}
		self.tmap['.'] = SimpleTile(self.bmpRoot.empty)
		
		self.tmap['a'] = RevTrackTile(self.bmpRoot.track.straight, [[-1, 0], [1, 0]])
		self.tmap['b'] = TrackTile(self.bmpRoot.track.vertical, [])
		self.tmap['c'] = TrackTile(self.bmpRoot.track.diagright, [[-1, -1], [1, 1]])
		self.tmap['d'] = TrackTile(self.bmpRoot.track.diagleft, [[-1, 1], [1, -1]])

		self.tmap['e'] = TrackTile(self.bmpRoot.track.turnlefteast, [[-1, 0], [1, -1]])
		self.tmap['f'] = TrackTile(self.bmpRoot.track.turnleftwest, [[-1, 1], [1, 0]])
		self.tmap['g'] = TrackTile(self.bmpRoot.track.turnrighteast, [[-1, 0], [1, 1]])
		self.tmap['h'] = TrackTile(self.bmpRoot.track.turnrightwest, [[-1, -1], [1, 0]])

		self.tmap['i'] = TrackTile(self.bmpRoot.track.turnleftup, [])
		self.tmap['j'] = TrackTile(self.bmpRoot.track.turnrightup, [])
		self.tmap['k'] = TrackTile(self.bmpRoot.track.turnleftdown, [])
		self.tmap['l'] = TrackTile(self.bmpRoot.track.turnrightdown, [])

		self.tmap['m'] = TrackTile(self.bmpRoot.track.eoblefteast, [])
		self.tmap['n'] = TrackTile(self.bmpRoot.track.eobleftwest, [])
		self.tmap['o'] = TrackTile(self.bmpRoot.track.eobrighteast, [])
		self.tmap['p'] = TrackTile(self.bmpRoot.track.eobrightwest, [])

		self.tmap['q'] = TrackTile(self.bmpRoot.track.eobleftup, [])
		self.tmap['r'] = TrackTile(self.bmpRoot.track.eobrightup, [])
		self.tmap['s'] = TrackTile(self.bmpRoot.track.eobleftdown, [])
		self.tmap['t'] = TrackTile(self.bmpRoot.track.eobrightdown, [])

		self.tmap['u'] = TrackTile(self.bmpRoot.track.eobwest, [[0, 0], [1, 0]])
		self.tmap['v'] = TrackTile(self.bmpRoot.track.eobeast, [[-1, 0], [0, 0]])
		self.tmap['w'] = TrackTile(self.bmpRoot.track.eobup, [])
		self.tmap['x'] = TrackTile(self.bmpRoot.track.eobdown, [])

		self.tmap['2'] = TurnoutTile(self.bmpRoot.track.tolefteast, [[-1, 0], [1, 0], [1, -1]])
		self.tmap['3'] = TurnoutTile(self.bmpRoot.track.toleftwest, [[-1, 0], [1, 0], [-1, 1]])
		self.tmap['4'] = TurnoutTile(self.bmpRoot.track.torighteast, [[-1, 0], [1, 0], [1, 1]])
		self.tmap['5'] = TurnoutTile(self.bmpRoot.track.torightwest, [[-1, 0], [1, 0], [-1, -1]])
		
		self.tmap['0'] = SignalTile(self.bmpRoot.signals.east, [1, -1], True)
		self.tmap['1'] = SignalTile(self.bmpRoot.signals.west, [-1, 1], False)
		
		return self.tmap
