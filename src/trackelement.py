from tileTypes import TTYPE_NORMAL, TTYPE_OCCUPIED, TTYPE_ROUTED, TTYPE_EASTROUTED, TTYPE_WESTROUTED, \
				ADJ_WEST, ADJ_EAST, ADJ_REVERSED

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
		
	def setWestRouted(self):
		self.routed = True
		self.eastRouted = False
		self.westRouted = True
		
	def isRouted(self):
		return self.routed or self.eastRouted or self.westRouted
		
	def getAdjacent(self, atype):
		print("adjacency options: (%s)" % str(self.adj))
		if self.adj is None:
			return None
		elif atype == ADJ_WEST:
			return self.adj[0]
		elif atype == ADJ_REVERSED:
			return self.adj[2]
		else: #atype == ADJ_EAST
			return self.adj[1]
		
	def getBmp(self):
		if self.occupied:
			ttype = TTYPE_OCCUPIED
		elif self.routed:
			if self.isReversible():
				if self.eastRouted:
					ttype = TTYPE_EASTROUTED
				elif self.westRouted:
					ttype = TTYPE_WESTROUTED
				else:
					print("Huh??")
					ttype = TTYPE_ROUTED
			else:
				ttype = TTYPE_ROUTED
		else:
			ttype = TTYPE_NORMAL
			
		print("bmp ttype (%s)" % str(ttype))
			
		if self.turnout:
			return self.tileType.getBmp(ttype, self.turnout.isReversed())
		else:
			return self.tileType.getBmp(ttype)
