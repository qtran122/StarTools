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
config_ = True
config_ = True



#--------------------------------------------------#
'''Public Functions'''

def SetConfigurations():
	x = 1



def Unrotate(playdo):
	log.Info("\nRemoving rotation properties on objects...")


	# Register the objects with rotation properties to be fixed
	list_of_all_object = []
	list_of_all_objectgroup = playdo.GetAllObjectgroup(False)
	for objectgroup in list_of_all_objectgroup:
		# Skip if the object layer is inactive
#		print(objectgroup)
#		print( objectgroup.get("name") )
		if objectgroup.get("name")[0] == "_": continue

		# Add object to list, but only if they are rotated
		for object in objectgroup:
#			print( object.get("rotation") )
			if object.get("rotation") == None: continue
			list_of_all_object.append(object)
	log.Info(f"  Total of {len(list_of_all_object)} objects to be processed")


	# Remove rotation properties, and then update the vertex coordinates accordingly
	for object in list_of_all_object:
		# Fetch the necessary data
		center_rotation_x = float( object.get("x") )
		center_rotation_y = float( object.get("y") )
		rotation_in_degree = float( object.get("rotation") )
		old_vertices = tiled_utils.GetPolyPointsFromObject(object)

		# Process and update coordinates to new value
		center_rotation = ( center_rotation_x, center_rotation_y )
		rotation_in_radian = math.radians( rotation_in_degree )
#		new_center = rotate( (0,0), center_rotation, rotation_in_radian )
		new_poly_str = UpdateVertices(center_rotation, rotation_in_radian, old_vertices)

		# Reset rotation value
#		object.set("x", str(new_center[0]))
#		object.set("y", str(new_center[1]))
#		object.set("rotation", "0")
		object.attrib.pop("rotation")
		tiled_utils.SetPolyPointsOnObject(object, new_poly_str)

	log.Info(f"  All polylines have been fixed\n")





#--------------------------------------------------#
'''Utility'''

def UpdateVertices( center_rotation, rotation_in_radian, old_vertices ):
	'''Returns string'''

	# Apply rotation algorithm to each vertex
	new_vertices = []
	for old_vertex in old_vertices:
		new_vertex = rotate( center_rotation, old_vertex, rotation_in_radian )
		new_vertex_x, new_vertex_y = rotate(center_rotation, old_vertex, rotation_in_radian)

		# Process
		new_vertex_x = round(new_vertex[0])
		new_vertex_y = round(new_vertex[1])
		new_vertex_x /= 16
		new_vertex_y /= 16
		if new_vertices != []:
			new_vertex_x -= new_vertices[0][0]
			new_vertex_y -= new_vertices[0][1]
		new_vertices.append( (new_vertex_x, new_vertex_y) )

	# Offset all vertices, such that the first vertex is at (0,0)
#	new_vertices = []
#	for vertex in temp_vertices:
#		new_vertices.append( vertex[0] - offset[0], vertex[1] - offset[1] )

	new_vertices[0] = (0,0)



	# Convert int tuples into string
	new_vertices_str = tiled_utils.MakePolypoints(new_vertices)
#	print(new_vertices_str)
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