'''
Scan the whole input level for any rotated objects, e.g. lines and polygons,
  then change its coordinates to look identicale after removing the object's rotation value.


USAGE EXAMPLE:
	unrotator.unrotate(playdo)
'''

import logic.common.log_utils as log
import logic.common.tiled_utils as tiled_utils
import math

#--------------------------------------------------#
'''Variables'''

# Default values for the configurations
config_snap_to_pixel = True
config_ = True
# Will probably delete this section? Need to discuss first





#--------------------------------------------------#
'''Public Functions'''

def SetConfigurations():
	'''
	The plan is to call this function from the CLI
	  for setting some configurations based on user's preference.
	Things like whether to snap vertices to the nearest pixels or not,
	  whether to detect certain objectgroups or read all at once, etc.

	Maybe this function won't be needed?
	Will decide whether to delete it after the discussion...
	'''

	x = 1





def Unrotate(playdo):
	'''Main Logic'''

	log.Info("\nRemoving rotation properties on objects...")

	# Register the objects with rotation properties to be fixed
	list_of_all_object = []
	list_of_all_objectgroup = playdo.GetAllObjectgroup(False)
	for objectgroup in list_of_all_objectgroup:
		# Skip if the object layer is inactive
		if not objectgroup.get("name").startswith("objects"):
			if not objectgroup.get("name").startswith("collisions"):
				continue

		# Add object to list, but only if they are rotated
		for object in objectgroup:
			if object.get("rotation") == None: continue
			list_of_all_object.append(object)

	log.Info(f"  Total of {len(list_of_all_object)} objects to be processed")



	# Remove rotation properties, and then update the vertex coordinates accordingly
	for object in list_of_all_object:
		# Process the vertices and rotation values
		old_vertices = SetFirstVertexToZero(object)
		rotation_in_degree = float( object.get("rotation") )
		rotation_in_radian = math.radians( rotation_in_degree )
		new_poly_str = UpdateVertices(rotation_in_radian, old_vertices)

		# Reset rotation value, then set the new vertices
		object.attrib.pop("rotation")
		tiled_utils.SetPolyPointsOnObject(object, new_poly_str)

	log.Info(f"  All polylines have been fixed\n")





#--------------------------------------------------#
'''Utility'''

def SetFirstVertexToZero( tiled_object ):
	'''
	This offsets all vertices such that the first vertex is at (0,0)
	 * The list of vertices are in pixels
	The new x-/y-coordinates are set directly to object,
	  while the vertices are returned as a list for later use

	e.g.
		<object x="100" y="200" rotation="180">
		 <polyline points="20,10 40,50"/>
		</object>
	->
		<object x="120" y="210" rotation="180">
		 <polyline points="0,0 20,40"/>
		</object>
	returns [ (0,0), (20,40) ]

	'''

	# Fetch vertices values from object
	old_vertices = tiled_utils.GetPolyPointsFromObject(tiled_object)
	if old_vertices == None: return None

	pos_x = float( tiled_object.get("x") )
	pos_y = float( tiled_object.get("y") )
	offset = old_vertices[0]

	# Offset x-/y-coordinates and all vertices, such that first vertex is at (0,0)
	adjusted_vertices = []
	for vertex in old_vertices:
		new_x = round(vertex[0] - offset[0])
		new_y = round(vertex[1] - offset[1])
		adjusted_vertices.append( (new_x, new_y) )
	new_pos_x = round( pos_x + offset[0] )
	new_pos_y = round( pos_y - offset[1] )


	# Set the new coordinates to object, then return the list for later processing
	tiled_object.set( "x", str(new_pos_x) )
	tiled_object.set( "y", str(new_pos_y) )
	return adjusted_vertices





def UpdateVertices( rotation_in_radian, old_vertices ):
	'''
	Takes the angle of rotation, and the list of original vertices for conversion.
	 * First vertex is assumed to be at (0,0) relative to the XML object's x-/y-coordinates
	Returns string to be direct replacement for the XML object.

	e.g.
		UpdateVertices( 1.57, [(0,0), (1,1), (1,2)] )
		  -> "0,0 -1,1, -2,1"
	'''

	# Apply rotation algorithm to each vertex
	new_vertices = []
	for old_vertex in old_vertices:
		# Rotate, round off to the nearest pixel, convert into tile-units
		new_vertex_x, new_vertex_y = rotate( (0,0), old_vertex, rotation_in_radian )
		new_vertex_x = round(new_vertex_x)
		new_vertex_y = round(new_vertex_y)
		new_vertex_x /= 16
		new_vertex_y /= 16
		new_vertices.append( (new_vertex_x, new_vertex_y) )


	# Offset all vertices, such that the first vertex is at (0,0)
	temp_vertices = new_vertices
	offset = temp_vertices[0]
	new_vertices = []
	for vertex in temp_vertices:
		new_vertices.append( (vertex[0] - offset[0], vertex[1] - offset[1]) )
	new_vertices[0] = (0,0)


	# Convert int tuples into string
	new_vertices_str = tiled_utils.MakePolypoints(new_vertices)
	return new_vertices_str





# https://stackoverflow.com/questions/34372480/rotate-point-about-another-point-in-degrees-python
def rotate(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.
    """
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy





#--------------------------------------------------#










# End of File