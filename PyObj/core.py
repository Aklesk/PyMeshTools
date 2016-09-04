import pdb

# We'll be using this to simplify lookups by giving everything an ID
def idGen():
	num = 0
	while True:
		yield "aA3mZ4%s" % str(num)
		num += 1

# Vert class
class Vert:
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
		# NOTE: DO NOT USE SELF.FACES. IT WILL BE UNDEFINED. USE GETFACES INSTEAD.
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
		return [v for k, v in self.faceObj.items()]
		
	def getLines(self):
		return
		
	# TODO: Add check not delete any faces which still have three good vertices
	def delete(self):
		del self.pyObj.vertObj[self.i]
		for face in self.getFaces():
			face.delete()
		self.i = -1
	

	
# Face class
# Note that 
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
			
	def getVerts(self):
		return self.verts
		
	# TODO: Add check to make sure no vertices are orphaned
	def delete(self):
		del self.pyObj.faceObj[self.i]
		for vert in self.getVerts():
			if self.i in vert.faceObj:
				del vert.faceObj[self.i]
		self.i = -1
		
		
# PyObj class
class run:
	vertObj = {} # We want a dictionary here for fast lookups - don't want to be using find all the time.
	faceObj = {} # We want a dictionary here for fast lookups - don't want to be using find all the time.
	idGen = idGen()
	
	
	# This returns unique (for the session, not globally) IDs using the idGen generator
	def getID(self):
		return self.idGen.next()
		
		
	# This returns an unordered list of verts
	def getVerts(self):
		return [val for key, val in self.vertObj.items()]
		
		
	# This returns an unordered list of faces
	def getFaces(self):
		return [val for key, val in self.faceObj.items()]
	
	
	# This creates a new vertex, and returns the result
	def newVert(self, x, y, z, i=0):
		v = Vert(self, x, y, z, i)
		self.vertObj[v.i] = v
		return v
		
		
	# This creates a new face, and returns the result
	def newFace(self, verts):
		f = Face(self, verts)
		self.faceObj[f.i] = f
		return f
		
	
	# This imports an OBJ file into PyObj for processing
	def importFile(self, path):
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
			self.newFace([self.vertObj[int(v)] for v in f.split(" ")])
		print("Processed %s faces." % len(self.getFaces()))
		
		
		# Import complete!		
		file.close()
		print("File read complete.")
		
		
	# This exports whatever the currently loaded OBJ looks like
	def exportFile(self, path):
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
		print("Slicing model in Y axis at height %s" % str(height))
		
		
		# Create a list of faces that bisect the slice plane
		sliceFaces = []
		for i, face in enumerate(self.getFaces()):
			sides = {"below": 0, "above": 0}
			
			for vert in face.getVerts():
				if vert.y < height:
					sides["below"] = 1
				elif vert.y >= height:
					sides["above"] = 1
					
				if sides["below"] == 1 and sides["above"] == 1:
					sliceFaces.append(face)
		
		# Perform the slice by deleting all verts and faces below the plane
		for i, vert in enumerate(self.getVerts()):
			if vert.y < height:
				vert.delete()
				
		# We want to fill in the holes left by the slice, so collect a list of all new verts
		allNewVerts = []
				
		# Re-build faces along the slice line to make the model clean, using the list of bisecting slice faces
		for face in sliceFaces:
			
			# For a slice function like this, we need to deal with triangles only. At the moment that involves triangulation
			# TODO: Implement triangulation
			if len(face.getVerts()) > 3:
				raise Exception("Slice function cannot currently deal with Ngons")
				
			
			# Deal with this triangle as a list of lines in order (to preserve normals)
			lines = []
			for i, vert in enumerate(face.getVerts()):
				if i != (len(face.getVerts()) - 1):
					lines.append([vert, face.getVerts()[i+1]])
				else:
					lines.append([vert, face.getVerts()[0]])
					
						
			# Shorten the lines to the slice plane
			for i, line in enumerate(lines):
				
				# One of the lines will either be entirely above or below the slice plane
				# If it's entirely above or below, ignore it.
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
							
							# Create our new vertex
							newVert = self.newVert(
								(otherVert.x + ((vert.x - otherVert.x) * scale)),
								(otherVert.y + ((vert.y - otherVert.y) * scale)),
								(otherVert.z + ((vert.z - otherVert.z) * scale))
							)
							
							# And replace the current deleted vertex with the new one
							del line[i]
							line.insert(i, newVert)
							
			# We've now finished processing our lines and can use them to re-build a new polygon.
			
			newVerts = []
			for line in lines:
				# Only process if we haven't deleted the line.
				if len(line) != 0:
					if line[0] not in newVerts:
						newVerts.append(line[0])
						allNewVerts.append(line[0])
					newVerts.append(line[1])
					allNewVerts.append(line[1])
			self.newFace(newVerts)
				
		print("Slice finished")