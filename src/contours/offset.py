import math 

# Given a vector (defined by 2 points) and the distance, 
# calculate a new vector that is distance away from the original 
def offsetSegment(p1, p2, d):
	# calculate vector
	v = [p2[0] - p1[0], p2[1] - p1[1]]

	# normalize vector
	v = [p/math.sqrt(v[0]**2 + v[1]**2) for p in v]

	# perpendicular unit vector
	vnp = [-v[1], v[0]]

	return [
	[ p1[0] + d*vnp[0], p1[1] + d*vnp[1] ],
	[ p2[0] + d*vnp[0], p2[1] + d*vnp[1] ],
	]

def intersection(sp):
	s1 = sp[0]
	s2 = sp[1]

	p1 = s1[0]
	p2 = s1[1]

	dx = float(p2[0]) - float(p1[0])
	dy = float(p2[1]) - float(p1[1])

	vert1 = False
	vertx = None
	try:
		m1 = float(dy)/float(dx)
		d1 = p1[1] - p1[0]*m1
	except ZeroDivisionError:
		vert1 = True
		vertx = p1[0]

	p1 = s2[0]
	p2 = s2[1]

	dx = float(p2[0]) - float(p1[0])
	dy = float(p2[1]) - float(p1[1])

	vert2 = False
	try:
		m2 = float(dy)/float(dx)
		d2 = p1[1] - p1[0]*m2
	except ZeroDivisionError:
		vert2 = True
		vertx = p1[0]

	if vert1 and not vert2:
		nx = vertx
		ny = m2 * nx + d2
	elif vert2 and not vert1:
		nx = vertx
		ny = m1 * nx + d1
	elif (vert1 and vert2) or (m1 == m2):
		# slopes are identical - just return the common point
		if s1[0] == s2[1]:
			nx = s1[0][0]
			ny = s1[0][1]
		elif s1[1] == s2[0]:
			nx = s1[1][0]
			ny = s1[1][1]
		else:
			return None
	else:
		nx = (d1-d2)/(m2-m1)
		ny = m1*nx+d1

	return (nx, ny)


def offsetPath(pts, d, closePath = False):
	if len(pts) == 2:
		return offsetSegment(pts[0], pts[1], d), True
	
	if closePath:
		segments = [offsetSegment(pts[-1], pts[0], d)]
	else:
		segments = []

	for i in range(len(pts) - 1):
		p1 = pts[i]
		p2 = pts[i+1]
		segments.append(offsetSegment(p1, p2, d))
	
	if not closePath:
		# save the initial offsets for the first and last points
		# if we are not going to close the path
		saveStart = segments[0][0]
		saveEnd = segments[-1][1]

	segpairs = []
	for i in range(len(segments) - 1):
		segpairs.append([ segments[i], segments[i+1] ])
	if closePath:
		segpairs.append([segments[-1], segments[0]])

	if not closePath:
		newPoints = [saveStart]
	else:
		newPoints = []

	rc = True		
	for sp in segpairs:
		np = intersection(sp)
		if np is None:
			rc = False
		else:
			newPoints.append(np)

	if not closePath:
		newPoints.append(saveEnd)
		
	return newPoints, rc
