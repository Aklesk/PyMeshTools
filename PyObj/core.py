from math import fabs

# We'll be using this to simplify lookups by giving everything an ID
def idGen():
	"""Generator for an ID locally unique to this session."""
	num = 0
	while True:
		yield "aA3mZ4%s" % str(num)
		num += 1

# Vert class
class Vert:
	"""Store attributes and functions for working with a single vertex and related geometry."""
	def __eq__(self, other):
		return self.i == other.i
		
	def __init__(self, pyObj, x, y, z, i=0, faces=0):	
		# Validate the inputs
		if not isinstance(pyObj, run):
			raise Exception("New verts cannot be created directly - use newVert")
		if not type(x) == float:
			raise Exception("X coordinate must be float")
		if not type(y) == float:
			raise Exception("Y coordinate must be float")
		if not type(z) == float:
			raise Exception("Z coordinate must be float")
		if not type(i) == int:
			raise Exception("Vertex index must be int")
		if not faces == 0 and not type(faces) == list:
			raise Exception("Faces must be a list")
		if not faces == 0:
			for face in faces:
				if not isinstance(face, Face):
					raise Exception("Invalid face given to Vertex")
			
		# If i is 0, assign it a new ID
		if i == 0:
			i = pyObj.getID()
			
		# Load faces into an object for easy lookup (order does not matter here)
		self.faceObj = {}
		if not faces == 0:
			for face in faces:
				self.faceObj[face.i] = face
			
		self.x = x
		self.y = y
		self.z = z
		self.i = i
		self.pyObj = pyObj
		
	def getFaces(self):
		"""Return a list of face classes that include this vertex."""
		return [v for k, v in self.faceObj.items()]
	
	# Note that these lines will not be directional as they are not tied to a face
	def getLines(self):
		"""Return a list of line classes that terminate at this vertex."""
		lines = []
		for face in self.getFaces():
			lines.extend(face.getLines())
			
		# Filter unrelated lines, keeping only lines to and from this vert
		lines = [l for l in lines if l[0] == self or l[1] == self]
		
		# Filter out duplicate lines
		filteredLines = []
		for line in lines:
			if (len(
			[l for l in filteredLines if l[0] == line[0] and l[1] == line[1]]
			) == 0
			and
			len(
			[l for l in filteredLines if l[1] == line[0] and l[0] == line[1]]
			) == 0):
				filteredLines.append(line)
		
		return filteredLines
	
	# This checks to see if this vert is on a border by seeing if there are any border edges near.
	def isBorder(self):
		"""If this vertex part of a non-manifold geometry border return True, otherwise return False."""
		# The only way to determine a border line is one that is touching only one face.
		# We can check this simply by listing all lines on adjacent faces. The border edges
		# are the ones that involve this vert, but show up only once.
		faceLines = []
		for face in self.getFaces():
			faceLines.extend(face.getLines())
			
		# First filter out any lines that don't involve this vertex
		faceLines = [l for l in faceLines if l[0] == self or l[1] == self]
		
		# Now filter out any lines that appear twice
		borderLines = []
		for line in faceLines:
			matches = []
			matches.extend([l for l in faceLines if l[0] == line[0] and l[1] == line[1]])
			matches.extend([l for l in faceLines if l[1] == line[0] and l[1] == line[0]])
			if len(matches) == 1:
				borderLines.append(line)
		
		if len(borderLines) > 0:
			return True
		else:
			return False
		
	# TODO: Add check not delete any faces which still have three good vertices
	def delete(self):
		"""Delete this vertex and all faces that included it."""
		if self.i != -1: # Don't delete self more than once
			i = self.i
			self.i = -1
			del self.pyObj.vertObj[i]
			for face in self.getFaces():
				face.delete()
	

	
# Face class
class Face:
	def __eq__(self, other):
		return self.i == other.i
		
	def __init__(self, pyObj, verts):
		# Validate the inputs
		if not isinstance(pyObj, run):
			raise Exception("New faces cannot be created directly - use newFace")
		if not type(verts) == list:
			raise Exception("Face accepts only a list of Verts")
		for v in verts:
			if not isinstance(v, Vert):
				raise Exception("Invalid vertex given to Face")
		
		self.verts = verts
		self.pyObj = pyObj
		self.i = pyObj.getID()
		
		# Make sure we're associated with the verts.
		for vert in self.verts:
			vert.faceObj[self.i] = self
			
	# Note that these lines will be directional based on normals
	def getLines(self):
		"""Return list of lines in the form [startVertex, endVertex], so as to preserve direction."""
		lines = []
		for i, vert in enumerate(self.getVerts()):
			if i != (len(self.getVerts()) - 1):
				lines.append([vert, self.getVerts()[i+1]])
			else:
				lines.append([vert, self.getVerts()[0]])
		return lines
	
	def getVerts(self):
		"""Return all vertices that make up this face."""
		return self.verts
		
	def delete(self):
		"""Delete this face and any resulting orphan vertices."""
		if self.i != -1: # Don't delete self twice
			i = self.i
			self.i = -1
			del self.pyObj.faceObj[i]
			for vert in self.getVerts():
				if i in vert.faceObj: # Clean this out of any vertex association lists
					del vert.faceObj[i]
				if len(vert.getFaces()) == 0: # check if vertex is orphan now
					vert.delete()
			
		
	def triangulate(self):
		"""Triangulate this face and return the resulting new faces."""
		self.delete()
		verts = self.getVerts()
		newFaces = []
		while len(verts) > 2:
			newFaces.append(self.pyObj.newFace([verts[0], verts[1], verts[2]]))
			del verts[1]
		return newFaces
		
# PyObj class
class run:
	"""Initialization class to set up the environment for PyMeshTools to function."""
	vertObj = {} # Dictionary here for fast lookups
	faceObj = {} # Dictionary here for fast lookups
	idGen = idGen()
	
	
	# This returns unique (for the session, not globally) IDs using the idGen generator
	def getID(self):
		"""Return a locally unique ID for this session."""
		return self.idGen.next()
		
		
	# This returns an unordered list of verts
	def getVerts(self):
		"""Return an unordered list of all current verts."""
		return [val for key, val in self.vertObj.items()]
		
		
	# This returns an unordered list of faces
	def getFaces(self):
		"""Return unordered list of all current faces."""
		return [val for key, val in self.faceObj.items()]
	
	
	# This creates a new vertex, and returns the result
	def newVert(self, x, y, z, i=0):
		"""Create a new vertex with the provided x, y, a, and index provided, and return the created Vertex instance."""
		v = Vert(self, x, y, z, i)
		self.vertObj[v.i] = v
		return v
		
		
	# This creates a new face, and returns the result
	def newFace(self, verts):
		"""Create a new face from the provided list of vertices and return the created Face instance."""
		f = Face(self, verts)
		self.faceObj[f.i] = f
		return f
		
	
	# This imports an OBJ file into PyObj for processing
	def importFile(self, path):
		"""Import single OBJ file at given path into PyMeshTools for processing."""
		print("Importing file %s" % (path))
		file = open(path, 'r')
		
		
		# First read the file into memory line by line; we can't process until we have all bits filed away.
		vertLines = []
		faceLines = []

		for line in file:
			if line[0:2] == "v ":
				vertLines.append(line[2:].replace("\n", ""))
			if line[0:2] == "f ":
				faceLines.append(line[2:].replace("\n", ""))
				
		print("Data read complete. Found %s vertex entries and %s face entries." % (len(vertLines), len(faceLines)))
		
		
		# Process into proper classes - vertices first (no dependencies), then faces.
		for i, v in enumerate(vertLines):
			s = v.split(" ")
			self.newVert(float(s[0]), float(s[1]), float(s[2]), (i+1))
		print("Processed %s vertices." % len(self.getVerts()))
		
		for i, f in enumerate(faceLines):
			self.newFace([self.vertObj[int(v.split("/")[0])] for v in f.split(" ")])
		print("Processed %s faces." % len(self.getFaces()))
		
		
		# Import complete!		
		file.close()
		print("File read complete.")
		
		
	# This exports whatever the currently loaded OBJ looks like
	def exportFile(self, path):
		"""Exports an OBJ based on the data loaded into PyMeshTools."""
		print("Exporting file %s" % (path))

		file = open(path, 'w')
		file.write("# OBJ exported from PyObj by Thaumaturgy Studios\n")
		file.write("usemtl (null)\n")

		# Write each vertex, updating its index to its actual position as we go.
		for i, vert in enumerate(self.getVerts()):
			file.write("v %s %s %s\n" % (vert.x, vert.y, vert.z))
			vert.i = str(i+1)
			
		# Write each face, using the index of the vertex object.
		for face in self.getFaces():
			file.write("f %s\n" % " ".join([v.i for v in face.getVerts()]))
			
		file.close()
		print("File export complete.")
		
		
	# This slices the model in the Y axis at the specified height, and keeps everything above it
	def sliceY(self, height):
		"""Slice the data in PyMeshTools at the specified height in the Y axis, delete anything below, and fill the hole."""
		print("Slicing model in Y axis at height %s" % str(height))
		
		
		# Create a list of faces that bisect the slice plane
		sliceFaces = {}
		for i, face in enumerate(self.getFaces()):
			sides = {"below": 0, "above": 0}
			
			for vert in face.getVerts():
				if vert.y < height:
					sides["below"] = 1
				elif vert.y >= height:
					sides["above"] = 1
					
				if sides["below"] == 1 and sides["above"] == 1:
					sliceFaces[face.i] = face
					
		# The slice function can only deal with triangles, so triangulate all sliceFaces
		ngons = [f for key, f in sliceFaces.items() if len(f.getVerts()) > 3]
		for face in ngons:
			del sliceFaces[face.i]
			for f in face.triangulate():
				sliceFaces[f.i] = f
		
		# Perform the slice by deleting all verts and faces below the plane
		for i, vert in enumerate(self.getVerts()):
			if vert.y < height:
				vert.delete()
				
		# We want to fill in the holes left by the slice, so collect a list of all new verts
		allNewVerts = []
				
		# Re-build faces along the slice line to make the model clean, using the list of bisecting slice faces
		for key, face in sliceFaces.items():
			lines = face.getLines()
						
			# Shorten the lines to the slice plane
			for i, line in enumerate(lines):
				
				# One of the lines will either be entirely above or below the slice plane
				# If it's entirely above, ignore it.
				if line[0].i != -1 and line[1].i != -1:
					pass
				
				# If it's entirely below, clear data from it. Note that we cannot delete it, as this will mess up the loop.
				elif line[0].i == -1 and line[1].i == -1:
					lines[i] = []
				
				# If it's neither, it's a crossing line and we need to process it.
				else:
					for i, vert in enumerate(line):
						# If the vert has been deleted, it's in the deletion area and we need to create a new vertex at the correct coordinates
						if vert.i == -1:
							if i == 0:
								otherVert = line[1]
							else:
								otherVert = line[0]
								
							# The scale is the transform to change the current offset to the new offset that will end up on the slice plane
							scale = (height - otherVert.y)/(vert.y - otherVert.y)
							
							# now we can calculate our new XYZ
							xyz = ((otherVert.x + ((vert.x - otherVert.x) * scale)),
								(otherVert.y + ((vert.y - otherVert.y) * scale)),
								(otherVert.z + ((vert.z - otherVert.z) * scale)))
							
							# Now that we know where the vertex should go, we neet to check - is there already
							# another one there from another face?
							t = 0.00001
							matches = [v for v in allNewVerts if fabs(v.x - xyz[0]) < t and fabs(v.y - xyz[1]) < t and fabs(v.z - xyz[2]) < t ]
							if len(matches) > 0:
								newVert = matches[0]
							else:
							
								# If we need a new one, create our new vertex and add it to the newVerts list.
								newVert = self.newVert(
									(otherVert.x + ((vert.x - otherVert.x) * scale)),
									(otherVert.y + ((vert.y - otherVert.y) * scale)),
									(otherVert.z + ((vert.z - otherVert.z) * scale))
								)
								allNewVerts.append(newVert)
							
							# We've sorted out the vertex, so now replace the current deleted vertex with the new one
							del line[i]
							line.insert(i, newVert)
							
			# We've now finished processing our lines and can use them to re-build a new polygon.
			
			newVerts = []
			for line in lines:
				if len(line) != 0: # Only process if we haven't deleted the line.
					if line[0] not in newVerts:
						newVerts.append(line[0])
					if line[1] not in newVerts:
						newVerts.append(line[1])
			self.newFace(newVerts)			
				
		print("Slice finished - filling holes")

		# First we need to split the verts out into contiguous borders
		borders = []
		def borderWalk(lastVert, vert, startVert=0):
			if type(startVert) == int:
				found = [lastVert, vert]
				startVert = lastVert
			else:
				found = [vert]
			
			adjacent = {}
			for line in vert.getLines():
				for v in line:
					adjacent[v.i] = v
					
			nextVert = [v for k, v in adjacent.items() if v.isBorder() and v != lastVert and v != vert][0]

			if nextVert != startVert:
				found.extend(borderWalk(vert, nextVert, startVert))
				
			return found
		
		while len(allNewVerts) > 0:
		
			# First we need to determine direction for normals. Pick a starting place and go						
			end = 0
			for line in allNewVerts[0].getLines():
				if end == 0:
					if line[0] in allNewVerts and line[1] in allNewVerts:
						end = 1
						result = borderWalk(line[1], line[0])
						borders.append(result)
						allNewVerts = [v for v in allNewVerts if v not in result]
						self.newFace(result)
