from math import fabs

FWIDTH = 0
FHEIGHT = 1

TABS = 0
SLOTS = 0

class face:
	def __init__(self, h, w, thk):
		self.height = h
		self.width = w
		self.thickness = thk
		self.htabtype = TABS
		self.wtabtype = TABS
		self.htabct = 0
		self.wtabct = 0
		self.htablen = 10
		self.wtablen = 10
		self.htabs = []
		self.wtabs = []
		self.hrelief = False
		self.wrelief = False
		self.rects = []
		self.circles = []
		
	def getDim(self):
		return self.width, self.height
		
	def setRectangles(self, r):
		self.rects = r[:]
		
	def setCircles(self, c):
		self.circles = c[:]
		
	def setWall(self, w):
		self.thickness = w 
		
	def setHeight(self, h):
		self.height = h
		self.calcHTabs()
		
	def calcHTabs(self):
		if self.htabct > 0:
			self.htabs = []
			step = self.height/float(self.htabct+1.0)
			loc = 0;
			for _ in range(self.htabct):
				loc += step
				self.htabs.append((loc, self.htablen))

	def setWidth(self, w):
		self.width = w 
		self.calcWTabs()
		
	def calcWTabs(self):
		if self.wtabct > 0:
			self.wtabs = []
			step = self.width/float(self.wtabct+1.0)
			loc = 0;
			for _ in range(self.wtabct):
				loc += step
				self.wtabs.append((loc, self.wtablen))
			
	def setHRelief(self):
		self.hrelief = True
		self.wrelief = False

	def setWRelief(self):
		self.hrelief = False
		self.wrelief = True

	def setNoRelief(self):
		self.hrelief = False
		self.wrelief = False
		
	def setTabType(self, horw, t):
		if horw == FWIDTH:
			self.wtabtype = t 
		else:
			self.htabtype = t 
			
	def setTabLen(self, horw, l):
		if horw == FWIDTH:
			self.wtablen = l 
			self.calcWTabs()
		else:
			self.htablen = l 
			self.calcHTabs()
		
	def setTabCount(self, horw, n):
		if horw == FWIDTH:
			self.wtabct = n 
			self.calcWTabs()
		else:
			self.htabct = n 
			self.calcHTabs()
		
	def render(self, toolrad, stepover, reversePockets, blindDepth, faceBlind, adjacentBlind):
		sides = []
		sides.append(self.renderHSide([-self.width/2.0, -self.height/2.0], [-self.width/2.0, self.height/2.0], -1, toolrad, stepover, reversePockets, blindDepth, faceBlind, adjacentBlind[0]))
		sides.append(self.renderWSide([-self.width/2.0, self.height/2.0], [self.width/2.0, self.height/2.0], 1, toolrad, stepover, reversePockets, blindDepth, faceBlind, adjacentBlind[1]))
		sides.append(self.renderHSide([self.width/2.0, self.height/2.0], [self.width/2.0, -self.height/2.0], 1, toolrad, stepover, reversePockets, blindDepth, faceBlind, adjacentBlind[2]))
		sides.append(self.renderWSide([self.width/2.0, -self.height/2.0], [-self.width/2.0, -self.height/2.0], -1, toolrad, stepover, reversePockets, blindDepth, faceBlind, adjacentBlind[3]))
		
		sxMod = len(sides)
		for sx in range(sxMod):
			sx2 = (sx+1) % sxMod

			x1 = sides[sx][-1][0]
			x2 = sides[sx2][0][0]
			
			if fabs(x1) < fabs(x2):
				sides[sx][-1][0] = x1
				sides[sx2][0][0] = x1
			else:
				sides[sx][-1][0] = x2
				sides[sx2][0][0] = x2
				
			y1 = sides[sx][-1][1]
			y2 = sides[sx2][0][1]
			
			if fabs(y1) < fabs(y2):
				sides[sx][-1][1] = y1
				sides[sx2][0][1] = y1
			else:
				sides[sx][-1][1] = y2
				sides[sx2][0][1] = y2
				
		points = [sides[0][0]]
		for s in sides:
			points.extend(s[1:])
			
		c = self.renderCircles()
		r = self.renderRects()
		return [p for p in points], [cp for cp in c], [rp for rp in r]
	
	def renderCircles(self):
		return [[x[0], x[1]] for x in self.circles]

	def renderRects(self):
		return [[x[0], x[1], x[2]] for x in self.rects]
	
	def renderHSide(self, start, end, outDir, toolrad, stepover, reversePockets, renderBl, faceBl, adjBl):
		points = []
		td = outDir*toolrad
		if self.htabct == 0:
			if self.htabtype == TABS:
				points.append([start[0]+td-outDir*self.thickness, start[1]+td])
				points.append([end[0]+td-outDir*self.thickness, end[1]-td])
			else:
				points.append([start[0]+td, start[1]+td])
				points.append([end[0]+td, end[1]-td])
		else:
			if self.htabtype == TABS:
				x = start[0]-outDir*self.thickness+td
				xp = start[0]+td
				if adjBl:
					xp -= outDir*self.thickness/2
				points.append([x, start[1]+td])
				for t in self.htabs:
					y1 = start[1]-outDir*(t[0]-t[1]/2.0)+td
					y2 = start[1]-outDir*(t[0]+t[1]/2.0)-td
					points.append([x, y1])
					if self.wrelief:
						points.append([x, y1-td])
						points.append([x, y1])
					elif self.hrelief:
						points.append([x-td, y1])
						points.append([x, y1])
					points.append([xp, y1])
					points.append([xp, y2])
					points.append([x, y2])
					if self.wrelief:
						points.append([x, y2+td])
						points.append([x, y2])
					elif self.hrelief:
						points.append([x-td, y2])
						points.append([x, y2])
				points.append([x, end[1]-td])
			else:
				x = start[0]+td
				xp = start[0]+td-outDir*self.thickness
				points.append([x, start[1]+td])
				if not(renderBl and faceBl):
					for t in self.htabs:
						y1 = start[1]-outDir*(t[0]-t[1]/2.0)-td
						y2 = start[1]-outDir*(t[0]+t[1]/2.0)+td
						if faceBl and not reversePockets:
							points.extend(self.renderPocket(x, y1, xp, y2, toolrad, stepover, reversePockets))
						points.append([x, y1])
						points.append([xp, y1])
						if self.wrelief:
							points.append([xp, y1+td])
							points.append([xp, y1])
						elif self.hrelief:
							points.append([xp-td, y1])
							points.append([xp, y1])
						points.append([xp, y2])
						if self.wrelief:
							points.append([xp, y2-td])
							points.append([xp, y2])
						elif self.hrelief:
							points.append([xp-td, y2])
							points.append([xp, y2])
						points.append([x, y2])
						if faceBl and reversePockets:
							points.extend(self.renderPocket(x, y2, xp, y1, toolrad, stepover, reversePockets))

				points.append([x, end[1]-td])
			
		return points
		
	def renderWSide(self, start, end, outDir, toolrad, stepover, reversePockets, renderBl, faceBl, adjBl):
		points = []
		td = outDir*toolrad
		if self.wtabct == 0:
			if self.wtabtype == TABS:
				points.append([start[0]-td, start[1]+td-outDir*self.thickness])
				points.append([end[0]+td, end[1]+td-outDir*self.thickness])
			else:
				points.append([start[0]-td, start[1]+td])
				points.append([end[0]+td, end[1]+td])
		else:
			if self.wtabtype == TABS:
				y = start[1]-outDir*self.thickness+td
				yp = start[1]+td
				if adjBl:
					yp -= outDir*self.thickness/2
				points.append([start[0]-td, y])
				for t in self.wtabs:
					x1 = start[0]+outDir*(t[0]-t[1]/2.0)-td
					x2 = start[0]+outDir*(t[0]+t[1]/2.0)+td
					points.append([x1, y])
					if self.hrelief:
						points.append([x1, y-td])
						points.append([x1, y])
					elif self.wrelief:
						points.append([x1+td, y])
						points.append([x1, y])
					points.append([x1, yp])
					points.append([x2, yp])
					points.append([x2, y])
					if self.hrelief:
						points.append([x2, y-td])
						points.append([x2, y])
					elif self.wrelief:
						points.append([x2-td, y])
						points.append([x2, y])
	
				points.append([end[0]+td, y])
			else:
				y = start[1]+td
				yp = start[1]+td-outDir*self.thickness
				points.append([start[0]-td, y])
				if not(renderBl and faceBl):
					for t in self.wtabs:
						x1 = start[0]+outDir*(t[0]-t[1]/2.0)+td
						x2 = start[0]+outDir*(t[0]+t[1]/2.0)-td
						if faceBl and not reversePockets:
							points.extend(self.renderPocket(x1, y, x2, yp, toolrad, stepover, reversePockets))
						points.append([x1, y])
						points.append([x1, yp])
						if self.hrelief:
							points.append([x1, yp-td])
							points.append([x1, yp])
						elif self.wrelief:
							points.append([x1-td, yp])
							points.append([x1, yp])
						points.append([x2, yp])
						if self.hrelief:
							points.append([x2, yp-td])
							points.append([x2, yp])
						elif self.wrelief:
							points.append([x2+td, yp])
							points.append([x2, yp])
						points.append([x2, y])
						if faceBl and reversePockets:
							points.extend(self.renderPocket(x2, y, x1, yp, toolrad, stepover, reversePockets))
	
				points.append([end[0]+td, y])
			
		return points
	
	def renderPocket(self, x1, y1, x2, y2, toolrad, stepover, reversePockets):
		delta = toolrad*2*stepover
		pts = []
		
		if x1 < x2:
			ya = y1
			yb = y2
			xp = x1
			while True:
				pts.append([xp, ya])
				pts.append([xp, yb])
				xp += delta
				if xp > x2:
					break
				yx = ya
				ya = yb
				yb = yx
		else:
			ya = y1
			yb = y2
			xp = x1
			while True:
				pts.append([xp, ya])
				pts.append([xp, yb])
				xp -= delta
				if xp < x2:
					break
				yx = ya
				ya = yb
				yb = yx

		pts.append([x1, y1])				
		if reversePockets:
			return pts[::-1]
		else:
			return pts
				
			
