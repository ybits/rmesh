import sys

# Set the path to cgal-python
sys.path.insert(0, "/Users/ryan/local/PyCGAL/cgal_package-patched")

# We use recursion A LOT in here. Let's give it some space...
# Not anymore we don't...
# sys.setrecursionlimit(2000)

# Import CGAL
from CGAL.Triangulations_2 import *
from CGAL.Kernel import *

# Standard stuff we need
from xml.dom.minidom import Document
from operator import itemgetter

class RM_Rmesh():
	
	def __init__(self, data):
		self.data = data
		self.polygon = None
		self.triangulation = None
		self.quadrangulation = None
		
	def compute(self):
	
		if len(self.data) <= 0:
			return
	
		# Create our triangulation
		self.triangulation = RM_Triangulation()
		
		# Add all of our data (in this case, just points)
		self.triangulation.insert(self.data)
		
		# Compute the spanning tree
		self.triangulation.computeSpanningTree()
		
		# Create a new Quadrangulation from the triangulation
		self.quadrangulation = RM_Quadrangulation(self.triangulation)
		
		# Computer the quadrangulation
		self.quadrangulation.quadrangulate()
		
	def buildJson(self):
	
		wrapper = {}

		# Get triangulation structure
		tpoints = self.triangulation.getPointsList()
		tfaces = self.triangulation.getFacesList()
		edges = self.triangulation.rm_st.getEdges()
		stedges = []
		for e in edges:
			stedges.append([[e[0].x(), e[0].y()], [e[1].x(), e[1].y()]])
		
		# Put it together
		tri = {'points': tpoints, 'faces': tfaces, 'spanning_tree': stedges}
		
		# Get quadrangulation structure
		qpoints = self.quadrangulation.getPointsList()
		qfaces = self.quadrangulation.getFacesList()
		qsteinerPoints = self.quadrangulation.getSteinerPointsList()
		qsteinerPoints2 = self.quadrangulation.getSteinerPoints2List()
		qtriangle = self.quadrangulation.getFinalTriangle()
		
		# Put it together
		quad = {'points': qpoints, 'faces' : qfaces, 'steiner_points': qsteinerPoints, 'steiner_points2': qsteinerPoints2}
		
		#if qtriangle != None:
		#	quad['triangle'] = qtriangle
		
		# Put it ALL together
		wrapper['triangulation'] = tri
		wrapper['quadrangulation'] = quad
		
		return wrapper

class RM_TreeItem:
	
	def __init__(self, data, depth = 0, degree = 0):
		self.depth = depth;
		self.degree = 0;
		self.parent = None
		self.children = []
		self.marked = False
		self.info = ''
		self.data = data
		
	def setParent(self, tn):
		self.parent = tn.id
		self.degree = 1
		
	def getParent(self):
		return self.parent
		
	def addChild(self, tn):
		self.children.append(tn.id)
		self.degree = self.degree + 1
		
	def getChildren(self):
		return self.children
		
	def removeChild(self, tn):
 		self.children.remove(tn.id)
		self.degree = self.degree - 1
			
	def setData(self, d):
		self.data = d
		
class RM_SpanningTree:
	
	def __init__(self, root):
		self.list = {}
		self.index = 0
		self.root = RM_TreeItem(root, 0, 0)
		self.append(self.root)
		self.edges = []
	
	def add(self, child, parent):
		childTi = RM_TreeItem(child, parent.depth + 1, 0)
		childTi.setParent(parent)
		childTi = self.append(childTi)
		parent.addChild(childTi)
		return childTi
		
	def delById(self, id):
		ti = self.findByIndex(id)
		if ti is not None:
			#self.removeByIndex(id)
			if ti.parent is not None:
				parent = self.findByIndex(ti.parent)
				if parent is not None:
					parent.removeChild(ti)
			del self.list[ti.id]
		else:
			print "An error occured deleting node by id", id
	
	def append(self, ti):
		ti.id = self.index
		self.list[self.index] = ti
		self.index = self.index + 1
		return ti
		
	def findByIndex(self, i):
		if self.list.has_key(i):
			return self.list[i]
		return None
		
	def removeByIndex(self, i):
		if self.list.has_key(i):
			return self.delById(i)
		else:
			print "An error occured removing node", i
			#die(1)
		return None
		
	def remove(self, node):
		return self.removeByIndex(node.id)
		
	def clear(self):
		self.list.clear()
		self.index = 0
		
	def getSiblings(self, child, parent):
		siblings = []
		children = parent.getChildren()
		for c in children:
			# Is this right? Blah.
			if c != child.id:
				siblings.append(self.findByIndex(c))
		return siblings
		
	def ils(self, fx):
		counter = 0
		list = []
		list.append(self.root)
		self.ilsTraversal(list, '>', fx)
		
	def ilsTraversal(self, l, prefix, fx):
	
		if len(l) == 0:
			return
	
		length = len(l)
		for i in range(length):
			#print l[i].depth, prefix, l[i].data
			fx(l[i])
			for c in l[i].children:
				nl = []
				cNode = self.findByIndex(c)
				nl.append(cNode)
				self.ilsTraversal(nl, "-" + prefix, fx)
			
	def dfs(self, fx):
		counter = 0
		list = []
		list.append(self.root)
		self.dfsTraversal(list, '>', fx)
		
	def dfsTraversal(self, l, prefix, fx):
	
		if len(l) == 0:
			return
	
		length = len(l)
		nl = []
		for i in range(length):
			for c in l[i].children:
				cNode = self.findByIndex(c)
				nl.append(cNode)
			
		self.dfsTraversal(nl, "-" + prefix, fx)
		#print l[i].depth, prefix, l[i].data
		fx(l[i])
		
	def bfs(self, fx):
		counter = 0
		list = []
		list.append(self.root)
		self.bfsTraversal(list, '>', fx)
		
	def bfsTraversal(self, l, prefix, fx):
	
		if len(l) == 0:
			return
	
		length = len(l)
		nl = []
		for i in range(length):
			fx(l[i])
			#print l[i].depth, prefix, l[i].data
			for c in l[i].children:
				cNode = self.findByIndex(c)
				nl.append(cNode)
			
		self.bfsTraversal(nl, "-" + prefix, fx)
		
	def printOut(self):
		print self.root.data, self.root.depth
		self.printNode(self.root, '-')
		
	def printNode(self, node, prefix):
		prefix = prefix + '-'
		for c in node.children:
			cNode = self.findByIndex(c)
			print cNode.data, cNode.depth
		for c in node.children:
			cNode = self.findByIndex(c)
			self.printNode(cNode, prefix)
		prefix = prefix + '->'
		
	def getEdges(self):
		#edges = []
		#self.buildEdges(self.root, edges)
		#return edges
		return self.edges
		
	def buildEdges(self, node, edges):
		for c in node.children:
			cNode = self.findByIndex(c)
			self.insertEdge(node.data['centroid'], cNode.data['centroid'], edges)
		for c in node.children:
			cNode = self.findByIndex(c)
			self.buildEdges(cNode, edges)
			
	def insertEdge(self, p1, p2, edges):
		edge = []
		if p1 < p2:
			edge = [p1, p2]
		else:
			edge = [p2, p1]
		edges.append(edge)
		
	def sortValuesByDepth(self):
		values = self.list.values()
		values.sort(self.compareDepth)
		values.reverse()
		return values
	
	def sortListByDepth(self, direction):
		return self.sortValuesByDepth()
		
	def compareDepth(self, x, y):
		if x.depth > y.depth:
			return 1
		elif x.depth == y.depth:
			return 0
		else: # x<y
			return -1
			
class RM_Triangulation(Constrained_Delaunay_triangulation_2):

	def __init__(self, *args):
		Constrained_Delaunay_triangulation_2.__init__(self, *args)
		self.rm_edges = []
		self.rm_vertices = []
		self.rm_constraints = []
		self.rm_faces = []
		self.rm_st = []
		
	def computeSpanningTree(self):
		for f in self.faces:
			if not self.is_infinite(f):
				continue
		self.rm_faces = []		
		self.rm_faces.append(f)
		data = {'centroid': self. getCentroid(f), 'triangle': self.triangle(f)}
		self.rm_st = RM_SpanningTree(data)
		self.buildSpanningTree(f, self.rm_faces, self.rm_st, self.rm_st.root)	
				
	def buildSpanningTree(self, f, faces, st, parent):
	
		parents = []
		parents.append(parent)
		for k in faces:
			parent = parents.pop(0)
			for j in range(3):
				fn = k.neighbor(j)
				if self.is_infinite(fn) == False:
					if not self.inFaceList(fn, faces):
						faces.append(fn)
						data = {'centroid': self.getCentroid(fn), 'triangle': self.triangle(fn)}
						st.insertEdge(parent.data['centroid'], data['centroid'], st.edges)
						new = st.add(data, parent)
						parents.append(new)
				
	def inFaceList(self, e, l):
		for el in l:
			if el == e:
				return True
		return False
	
	def getPointsList(self):
		points = []
		for v in self.vertices:
			point = [v.point().x(), v.point().y()];
			points.append(point)
		return points;
		
	def getFacesList(self):
		faces = []
		for f in self.faces:
			if not self.is_infinite(f):
				point1 = [f.vertex(0).point().x(), f.vertex(0).point().y()]
				point2 = [f.vertex(1).point().x(), f.vertex(1).point().y()]
				point3 = [f.vertex(2).point().x(), f.vertex(2).point().y()]
				faces.append([point1, point2, point3])
		return faces
		
	def getCentroid(self, f, sides = 3):
		dx = 0
		dy = 0
		for i in range(sides):
			dx = dx + f.vertex(i).point().x()
			dy = dy + f.vertex(i).point().y()
		return Point_2(dx / sides, dy / sides)
		
class RM_Quadrangulation(RM_Triangulation):

	def __init__(self, t):
		RM_Triangulation.__init__(self, t)
		self.rm_st = t.rm_st
		self.quads = []
		self.triangle = None
		self.steinerPoints = []
		self.steinerPoints2 = []
		self.rm_points = [];
	
	def quadrangulate(self):
		sl = self.rm_st.sortValuesByDepth()
	 	#for sli in sl:
		#	print sli.depth, sli.data
		for sli in sl:
			if sli.id in self.rm_st.list:
				node = self.rm_st.list[sli.id]
				#print node.depth, node.parent
				parent = self.rm_st.findByIndex(node.getParent())
				if parent == None:
					#print "case 1"
					self.processCase1(node)
				elif parent.degree == 1 or parent.degree == 2:
					#print "case 2"
					self.processCase2(node, parent)
				elif parent.degree == 3:
					self.processCase3(node, parent)

	def orientQuad(self, q):
		#print orientation(q[0], q[1], q[2])
		#print orientation(Vector_2(q[0], q[1]), Vector_2(q[1], q[2]))
		# This is some type of strange behavior. Should be either:
		# CLOCKWISE, COUNTERCLOCKWISE, or COLLINEAR 
		if orientation(q[0], q[1], q[2]) == Sign.SMALLER:
			# If we need to reorient, we start off in the form of:
			# outlier1, adjacent1, outlier2, adjacent2
			# we want:
			# outlier2, adjacent1, outlier1, adjacent2
			q.reverse()
			q0 = q.pop(0)
			q.append(q0)
			return q
		return q

	def getFacesList(self):
		faces = []
		#print self.quads
		for f in self.quads:
			point1 = [f[0].x(), f[0].y()]
			point2 = [f[1].x(), f[1].y()]
			point3 = [f[2].x(), f[2].y()]
			point4 = [f[3].x(), f[3].y()]
			faces.append([point1, point2, point3, point4])
		return faces
		
	def getPointsList(self):
		points = []
		for p in self.rm_points:
			point = [p.x(), p.y()];
			points.append(point)
		return points;
		
	def getSteinerPointsList(self):
		points = []
		for p in self.steinerPoints:
			point = [p.x(), p.y()];
			points.append(point)
		return points;
		
	def getSteinerPoints2List(self):
		points = []
		for p in self.steinerPoints2:
			point = [p.x(), p.y()];
			points.append(point)
		return points;	

	def getFinalTriangle(self):
		if self.triangle != None:
			return [self.triangle.vertex(0), self.triangle.vertex(1), self.triangle.vertex(2)]
		return None

	def processCase1(self, node):
		self.triangle = node.data['triangle']
	
	def processCase2(self, child, parent):
		#print "processing case 2"
		self.merge2(child, parent)
		self.rm_st.remove(child)
		self.rm_st.remove(parent)
		
	def processCase3(self, child, parent):
		#print "processing case 3"
		siblings = self.rm_st.getSiblings(child, parent)
		if len(siblings) != 1:
			# Error, has to be 1
			return False
		sibling = siblings[0]
		
		print "Old:", self.rm_st.list[parent.id].data['centroid'], self.rm_st.list[parent.id].data['triangle']
		
		parent = self.merge3(child, parent, sibling)
		self.rm_st.list[parent.id] = parent
		
		print "New:", self.rm_st.list[parent.id].data['centroid'], self.rm_st.list[parent.id].data['triangle']
		
		self.rm_st.remove(sibling)
		self.rm_st.remove(child)
		
		#self.rm_st.list[parent.id] = parent
		
	def merge2(self, child, parent):
		quads = []
		t1 = child.data['triangle']
		t2 = parent.data['triangle']
		adjacent = self.getAdjacentEdge(t1, t2)
		quad = []

		# Add first point, which is the outlier in the first triangle
		outlier1 = self.getOutlier(t1, adjacent)
		quad.append(outlier1)
		self.rm_points.append(outlier1)

		# Second point, first point in adjacent edge
		quad.append(adjacent[0])
		self.rm_points.append(adjacent[0])
		
		# Third point, outlier in the second triangle
		outlier2 = self.getOutlier(t2, adjacent)
		quad.append(outlier2)
		self.rm_points.append(outlier2)
		
		# Fourth point, second point in adjacent edge
		quad.append(adjacent[1])
		self.rm_points.append(adjacent[1])
		
		# Fix the orientation (CCW)
		quad = self.orientQuad(quad)
		
		if not self.isStronglyConvex(quad):
			#quads.append(quad)
			# We want to place a 4 steiner points into the interior of this quad,
			# 2 along the (former) adjent edge and one on each side of it, in order
			# to create 5 new convex quads
			
			# Work directly off of the points in the oriented quad, which are:
			# (outlier, adjacent, outlier, adjacent)
				
			# Split the adjacent edge into pieces
			splitEdges = self.splitAdjacentEdge([quad[1], quad[3]])
			
			# Steiner points 1 and 2 are pieces of the split edge
			sp1 = splitEdges[0][0]
			sp2 = splitEdges[1][0]
			
			# Outliers (these may have changed, let's be good about it)
			outlier1 = quad[0]
			outlier2 = quad[2]
			
			# Adjancent points
			adj1 = quad[1]
			adj2 = quad[3]
			
			# Outlier 1, steiner point 1
			ray1 = Ray_2(outlier1, sp1)
			# Outlier 1, steiner point2
			ray2 = Ray_2(outlier1, sp2)
			# Outlier 2, steiner point 1
			ray3 = Ray_2(outlier2, sp1)
			# Outlier 2, steiner point 2
			ray4 = Ray_2(outlier2, sp2)
			
			# Steiner points 3 and 4 are intersections of the rays from
			# the outliers through steiner points 1 and 2		
			sp3 = intersection(ray2, ray3)			
			sp4 = intersection(ray1, ray4)

			# Need to figure out if the steiner points are on the correct 
			# sides of the adjacent sement, and if not, swap 'em
			line = Line_2(adj1, adj2)
			if line.oriented_side(outlier1) != line.oriented_side(sp3) :
				sp0 = sp3
				sp3 = sp4
				sp4 = sp0
				

			# New quads are now:
			# Outlier 1, adjacent 1, sp1, sp3
			q1 = self.orientQuad([outlier1, adj1, sp1, sp3])
			
			# Outlier 1, sp3, sp2, adjacent 2
			q2 = self.orientQuad([outlier1, sp3, sp2, adj2])
			
			# Outler 2, adjacent 1, sp 1, sp4
			q3 = self.orientQuad([outlier2, adj1, sp1, sp4])
			
			# Outlier 2, sp4, sp2, adjacent 2
			q4 = self.orientQuad([outlier2, sp4, sp2, adj2])
			
			# sp1, sp2, sp3, sp4
			q5 = self.orientQuad([sp1, sp3, sp2, sp4])
			#q5 = [sp1, sp3, sp2, sp4]
			
			quads.extend([q1, q2, q3, q4, q5])
			self.steinerPoints.extend([sp1, sp2, sp3, sp4])
			#self.steinerPoints.extend([outlier2, adj1, sp1, sp4])

		else:
			quads.append(quad)
		
		quads.append(quad)
		self.quads.extend(quads)
		
	def merge3(self, child, parent, sibling):
		quads = []
		
		# Set triangles
		t1 = child.data['triangle']
		t2 = parent.data['triangle']
		t3 = sibling.data['triangle']
		
		# Adjacent edges
		adj1 = self.getAdjacentEdge(t1, t2)
		adj2 = self.getAdjacentEdge(t3, t2)

		#print adj1, adj2
		
		# Outliers
		outlier1 = self.getOutlier(t1, adj1)
		outlier2 = self.getOutlier(t3, adj2)
		
		# Find the shared vertex, and the non-shared vertices
		if adj1[0] == adj2[0]:
			sharedPoint = adj1[0]
			opposite1 = adj1[1]
			opposite2 = adj2[1]
		elif adj1[1] == adj2[0]:
			sharedPoint = adj1[1]
			opposite1 = adj1[0]
			opposite2 = adj2[1]
		elif adj1[1] == adj2[1]:
			sharedPoint = adj1[1]
			opposite1 = adj1[0]
			opposite2 = adj2[0]
		elif adj1[0] == adj2[1]:
			sharedPoint = adj1[0]
			opposite1 = adj1[1]
			opposite2 = adj2[0]	
		else:
			print "An error as occurred."
			
		# Rays are (outlier, centroid) and (outlier, opposite)
		ray1 = Ray_2(outlier1, opposite1)
		ray2 = Ray_2(outlier1, sharedPoint)
		ray3 = Ray_2(outlier2, opposite2)
		ray4 = Ray_2(outlier2, sharedPoint)
		
		# Slice the parent with both pairs of rays
		slicedTriangle1 = self.getTriangleFromRaySlice(ray1, ray2, t2)
		slicedTriangle2 = self.getTriangleFromRaySlice(ray3, ray4, t2)
		
		#print slicedTriangle1, slicedTriangle2
		
		# Get the new point from the two sliced triangles
		steinerPoint = self.getSteinerFromTriangles(slicedTriangle1, slicedTriangle2)
		
		# Testing
		#steinerPoint = parent.data['centroid']
		
		# Create the new triangle for the parent
		newTriangle = Triangle_2(opposite1, opposite2, steinerPoint)
		newCentroid = self.getCentroid(newTriangle, 3)
		
		# Quad 1
		quad1 = [outlier1, sharedPoint, parent.data['centroid'], opposite1]
		self.quads.append(self.orientQuad(quad1))
		
		# Quad 2
		quad2 = [outlier2, sharedPoint, parent.data['centroid'], opposite2]
		self.quads.append(self.orientQuad(quad2))
		
		#Steiner point is centroid of old parent (for now)
		self.steinerPoints2.append(steinerPoint)
		
		#Modify the parent
		parent.data['triangle'] = newTriangle
		parent.data['centroid'] = newCentroid
		
		return parent
		
	def modifyParent(self, child, parent, sibling):
		t1 = child.data['triangle'];
		t2 = child.data['triangle'];
		t3 = child.data['triangle'];
		sharedPoint = self.getSharedPoint(t1, t2, t3)
		
	def getOutlier(self, t, e):
		for i in range(3):
			if not self.pointInEdge(t.vertex(i), e):
				return t.vertex(i)
		return None
		
	def getSharedPoint(self, t1, t2, t3):
		adj1 = self.getAdjacentEdge(t1, t2)
		adj2 = self.getAdjacentEdge(t2, t3)
		
		if adj1[0] == adj2[0] or adj1[0] == adj2[1]:
			return adj1[0]
		else:
			return adj1[1]
	
	def getMidpoint(self, e):
		dx = (e[0].x() + e[1].x()) / 2
		dy = (e[0].y() + e[1].y()) / 2
		return Point_2(dx, dy)
		
	def splitAdjacentEdge(self, e):
		
		# Get the midpoint
		midpoint = self.getMidpoint(e)
		# Get the midpoint of the first 1/2
		mp1 = self.getMidpoint([e[0], midpoint])
		# Get the midpoint of the second 1/2
		mp2 = self.getMidpoint([e[1], midpoint])
		
		return [mp1, e[0]], [mp2, e[1]]
	
	def getTriangleFromRaySlice(self, ray1, ray2, triangle):
		int1 = intersection(ray1, triangle)
		int2 = intersection(ray2, triangle)
		
		if int1.__class__.__name__ == 'Segment_2':
			return Triangle_2(int1.vertex(0), int1.vertex(1), int2)
		elif int2.__class__.__name__ == 'Segment_2':
			return Triangle_2(int2.vertex(0), int2.vertex(1), int1)
		
		return triangle	
		
	def getSteinerFromTriangles(self, t1, t2):
		intersect = intersection(t1, t2)
		intType = intersect.__class__.__name__
		if intType == 'Point_2':
			point = intersect
		elif intType == 'Segment_2':
			point = self.getCentroid(intersect, 2)
		elif intType == 'Triangle_2':
			point = self.getCentroid(intersect, 3)
		elif intType == 'list':
			length = len(list)
			dx = 0
			dy = 0
			for i in range(length):
				dx = dx + intersect[i]
				dy = dy + intersect[i]
			point = Point_2(dx / length, dy / length)
		else:
			point = None
		return point 
			
	def getAdjacentEdge(self, t1, t2):
		edge = []
		for i in range(3):
			for j in range(3):
				if t1.vertex(i) == t2.vertex(j):
					if t1.vertex(i) not in edge :
						edge.append(t1.vertex(i))
						
		if len(edge) != 2:
			print edge, t1, t2
			exit(0)
		return edge
		
	def compareEdges(self, e1, e2):
		if e1[0] == e2[0] and e1[1] == e2[1]:
			return True
		if e1[0] == e2[1] and e1[1] == e2[0]:
			return True
		return False		
	
	def pointInEdge(self, p, e):
		if p == e[0] or p == e[1]:
			return True
		return False
		
	def buildFaceNode(self, doc, f, sides = 4):
		return RM_Triangulation.buildFaceNode(self, doc, f, sides)
	
	def getCentroid(self, f, sides = 4):
		dx = 0
		dy = 0
		for i in range(sides):
			dx = dx + f.vertex(i).x()
			dy = dy + f.vertex(i).y()
		return Point_2(dx / sides, dy / sides)
	
	def isStronglyConvex(self, q):
		if q is None:
			return False
		length = len(q)
		if length <= 3:
			return False
		mod = length
		for i in range(length):
			if not left_turn(q[i%mod], q[(i+1)%mod], q[(i+2)%mod]):
				return False
		return True
		
if __name__ == "__main__":
	import sys
	import json
	from random import *
	from CGAL.Kernel import *

	points = []
	for i in range(500):
		points.append(Point_2(randint(1, 550),randint(1, 550)))
	
	# points.append(Point_2(224, 192))
	# points.append(Point_2(94, 315))
	# points.append(Point_2(242, 418))
	# points.append(Point_2(390, 308))
	
	#p = midpoint(Point_3(224, 192, 0), Point_3(94, 315, 0))
	#print p
	
	# Create our new rmesh bohemoth
	rm = RM_Rmesh(points)

	# Compute it all! (This may take a while)
	rm.compute()

	# edges = rm.triangulation.rm_st.getEdges()
	# for e in edges:
	# 	print e

	#data = rm.buildJson()
	#print "Content-type: text/html;charset=utf-8\r\n"
	#print json.dumps(data)