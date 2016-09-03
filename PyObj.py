import os
import sys
import pdb
import PyObj


# Initialize the PyObj class we'll be using for the rest of this.
po = PyObj.core.run()


# Import our OBJ
fileIn = sys.argv[sys.argv.index("--") + 1:][0]
fileOut = os.path.join(os.path.dirname(fileIn), 'output.obj')	
po.importFile(fileIn)


# Delete all vertices with a y position lower than -4.
po.sliceY(-4)


# Re-export the new file.
po.exportFile(fileOut)