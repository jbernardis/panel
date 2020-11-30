from tileTypes import TTYPE_NORMAL, TTYPE_OCCUPIED, TTYPE_ROUTED, TTYPE_EASTROUTED, TTYPE_WESTROUTED, \
				TTYPE_UPROUTED, TTYPE_DOWNROUTED, ADJ_WEST, ADJ_EAST, ADJ_REVERSED

class TrackElement:
	def __init__(self, tileType, row, col):
		self.tileType = tileType
		self.row = row
		self.col = col
		
		self.turnout = None
		
		self.occupied = False
		self.routed = False
		self.eastRouted = False
		self.westRouted = False
		self.upRouted = False
		self.downRouted = False
		
		self.reversible = tileType.isReversible()
		
		a = tileType.getAdjacent()
		if a is None:
			self.adj = None
		else:
			self.adj = [x for x in a]
		
	def setTurnout(self, to):
		self.turnout = to
		
	def isTurnout(self):
		return self.turnout is not None
	
	def isReversible(self):
		return self.reversible
		
	def setReversed(self, flag):
		if self.turnout:
			self.turnout.setReversed(flag)
			
	def isReversed(self):
		if not self.turnout:
			return False
		
		return self.turnout.isReversed()
		
	def setOccupied(self, flag):
		self.occupied = flag
		
	def isOccupied(self):
		return self.occupied
		
	def setRouted(self, flag):
		self.routed = flag
		
	def setEastRouted(self):
		self.routed = True
		self.eastRouted = True
		self.westRouted = False
		self.upRouted = False
		self.downRouted = False
		
	def setWestRouted(self):
		self.routed = True
		self.eastRouted = False
		self.westRouted = True
		self.upRouted = False
		self.downRouted = False		
		
	def setUpRouted(self):
		self.routed = True
		self.eastRouted = False
		self.westRouted = False
		self.upRouted = True
		self.downRouted = False
		
	def setDownRouted(self):
		self.routed = True
		self.eastRouted = False
		self.westRouted = False
		self.upRouted = False
		self.downRouted = True
		
	def isRouted(self):
		return self.routed or self.eastRouted or self.westRouted or self.upRouted or self.downRouted
	
	def isVertical(self):
		return self.adj[0] == [0, None] and self.adj[1] == [0, None]
		
	def getAdjacent(self, atype):
		print("adjacency options: (%s)" % str(self.adj))
		if self.adj is None:
			return None
		elif atype == ADJ_WEST:
			return [x for x in self.adj[0]]
		elif atype == ADJ_REVERSED:
			return [x for x in self.adj[2]]
		else: #atype == ADJ_EAST
			return [x for x in self.adj[1]]
		
	def getBmp(self):
		if self.occupied:
			ttype = TTYPE_OCCUPIED
		elif self.routed:
			if self.isReversible():
				if self.eastRouted:
					ttype = TTYPE_EASTROUTED
				elif self.westRouted:
					ttype = TTYPE_WESTROUTED
				elif self.upRouted:
					ttype = TTYPE_UPROUTED
				elif self.downRouted:
					ttype = TTYPE_DOWNROUTED
				else:
					print("Huh??")
					ttype = TTYPE_ROUTED
			else:
				ttype = TTYPE_ROUTED
		else:
			ttype = TTYPE_NORMAL
			
		if self.turnout:
			return self.tileType.getBmp(ttype, self.turnout.isReversed())
		else:
			return self.tileType.getBmp(ttype)
