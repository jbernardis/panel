TTYPE_NORMAL = 0
TTYPE_OCCUPIED = 1
TTYPE_ROUTED = 2
TTYPE_EASTROUTED = 3
TTYPE_WESTROUTED = 4
TTYPE_UPROUTED = 5
TTYPE_DOWNROUTED = 6

STYPE_RED = 'r'
STYPE_GREEN = 'g'

ADJ_WEST = 0
ADJ_EAST = 1
ADJ_REVERSED = 2

LEFT = 'l'
RIGHT = 'r'

class SimpleTile:
	def __init__(self, bmp):
		self.bmp = bmp
		
	def getBmp(self, _):
		return self.bmp
	
	def isTurnout(self):
		return False
	
	def isSignal(self):
		return False
	
	def isReversible(self):
		return False
	
	def getAdjacent(self):
		return None

class TrackTile(SimpleTile):
	def __init__(self, nd, adj):
		self.nd = nd
		self.routed = False
		self.occupied = False
		self.reversed = False
		self.adj = adj

		SimpleTile.__init__(self, nd)
		
	def getBmp(self, ttype, basend=None):
		if basend is not None:
			base = basend
		else:
			base = self.nd
			
		if ttype == TTYPE_OCCUPIED:
			return base.occupied
		elif ttype == TTYPE_ROUTED:
			return base.routed
		elif ttype == TTYPE_EASTROUTED:
			return base.eastrouted
		elif ttype == TTYPE_WESTROUTED:
			return base.westrouted
		else: # ttype == TTYPE_NORMAL
			return base.normal
		
	def isTurnout(self):
		return False
	
	def isSignal(self):
		return False
	
	def isReversible(self):
		return False
	
	def getAdjacent(self):
		return self.adj

class RevTrackTile(TrackTile):
	def __init__(self, nd, adj):
		self.nd = nd
		TrackTile.__init__(self, nd, adj)
		
	def isReversible(self):
		return True
		
	def getBmp(self, ttype):
		if ttype in [ TTYPE_EASTROUTED, TTYPE_ROUTED ]:
			return self.nd.eastrouted
		elif ttype == TTYPE_WESTROUTED:
			return self.nd.westrouted
		elif ttype == TTYPE_DOWNROUTED:
			return self.nd.downrouted
		elif ttype == TTYPE_UPROUTED:
			return self.nd.uprouted
		else:
			return TrackTile.getBmp(self, ttype)
		
class TurnoutTile(TrackTile):
	def __init__(self, nd, adj):
		self.nd = nd
		TrackTile.__init__(self, nd, adj)
		
	def isTurnout(self):
		return True	
		
	def getBmp(self, ttype, rev=False):
		if rev:
			return TrackTile.getBmp(self, ttype, basend=self.nd.reversed)
		else:
			return TrackTile.getBmp(self, ttype, basend=self.nd.normal)
	
class SignalTile:
	def __init__(self, nd, startTile, eastbound):
		self.nd = nd
		self.startTile = startTile
		self.eastbound = eastbound
		
	def getBmp(self, stype):
		if stype == STYPE_RED:
			return self.nd.red
		else:
			return self.nd.green
	
	def isTurnout(self):
		return False
	
	def isSignal(self):
		return True
	
	def isEast(self):
		return self.eastbound
	
	def isWest(self):
		return not self.eastbound
	
	def getStartTile(self):
		return self.startTile

