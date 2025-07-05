'''
Main logic for cli_nav.py

Requires installing shapely with the following command:
	pip install shapely

USAGE EXAMPLE:
    navigation.logic(playdo, passed_arguments)
'''

import math
import xml.etree.ElementTree as ET
from shapely.geometry import LineString, Polygon

import logic.common.log_utils as log
import logic.common.tiled_utils as tiled_utils

#--------------------------------------------------#
'''Variables'''



'''Default values for the CLI-passed arguments'''
# In-editor object layers for nodes & routes
layer_name_node  = "_nav_nodes"
layer_name_route = "_nav_routes"


# All objects in this layer cannot be passed through
# OWP/polylines are currently ignored, TODO mark as impassable?
layer_name_collision = "collisions"


# All objects across all object layers with the following names
#  are treated as collision that may potentially block routes
list_object_name = [
]


# Threshold value for determining redundant routes
threshold_redundance = 0.9





'''Other Variables'''
OBJ_NAME_EXPORT = "ROUTE_DATA"
LAYER_NAME_EXPORT = "meta"

list_nodes = []		# (int, int) for coordinates
list_polygon1 = []	# (vertex1, vertex2, ...), where vertex = (int, int) for coordinates
list_polygon2 = []	#  ^

list_route = []	# [ (int, int) ], where each int keeps track of the node ID
list_dist = []	# [ float ]

is_route_closed = []	# [ bool ], for keepsing track of whether the route can be possible
is_route_overlap = []	# [ bool ], for keepsing track of redundant routes





#--------------------------------------------------#
'''Public Functions'''

def logic(playdo, passed_arguments):
	log.Must("Constructing paths...")
	_SetCliArgumentsToGlobal(passed_arguments)

	_ParseLevel(playdo)
	_CheckAllRoutes()
	_CheckRedundantRoutes()
	_VisualiseNodesAndRoutes(playdo)
	_ExportCondenseData(playdo)

	log.Must("~~End of All Procedures~~")



def _SetCliArgumentsToGlobal(passed_arguments):
	global layer_name_node
	global layer_name_route
	global layer_name_collision
	global list_object_name
	global threshold_redundance

	layer_name_node      = passed_arguments[0]
	layer_name_route     = passed_arguments[1]
	layer_name_collision = passed_arguments[2]
	list_object_name     = passed_arguments[3]
	threshold_redundance = passed_arguments[4]





#--------------------------------------------------#
'''WS'''










#--------------------------------------------------#
'''Parsing the Level'''

def _ParseLevel(playdo):
	log.Must(f"  Checking for nodes & collisions in level...")


	# Register all collision objects
	list_collision1 = []	# Temp array - Solid Collision
	list_collision2 = []	# Temp array - Potential Collision, e.g. BB
	list_object_layers = playdo.GetAllObjectgroup()
	for layer in list_object_layers:
		# Nodes
		if layer.get('name') == layer_name_node:
			for obj in layer: list_nodes.append( (int(obj.get("x")), int(obj.get("y"))) )

		# Solid Collision
		if layer.get('name') == layer_name_collision:
			for obj in layer: list_collision1.append(obj)

		# Variable Collision, e.g. BB
		if not layer.get('name').startswith('objects'): continue
		for obj in layer:
			if obj.get('name') in list_object_name:
				list_collision2.append(obj)
	log.Info(f"    {len(list_nodes)} nodes found in \"{layer_name_node}\"")
	log.Info(f"    {len(list_collision1)} collision found")
	log.Info(f"    {len(list_collision2)} objects found")


	# Convert collisions into polygon for later uses
	log.Info(f"  Converting collision objects into vertices & polygon...")
	for obj in list_collision1:
		vertices = tiled_utils.GetVerticesFromObject(obj)
		if len(vertices) <= 2: continue
		polygon = Polygon(vertices)
		list_polygon1.append(polygon)
		log.Extra(f"    {len(vertices)} pts - {vertices}")

	log.Info(f"  Converting BB objects into vertices & polygon...")
	for obj in list_collision2:
		vertices = tiled_utils.GetVerticesFromObject(obj)
		if len(vertices) <= 2: continue
		polygon = Polygon(vertices)
		list_polygon2.append(polygon)
		log.Extra(f"    {len(vertices)} pts - {vertices}")





#--------------------------------------------------#
'''Calculation'''

def _CheckAllRoutes():
	log.Must(f"  Checking for viable paths with {len(list_nodes)} nodes...")

	count_node = len(list_nodes)
	for i in range(count_node):
		end_point = list_nodes[i]
		for j in range(i):
			start_point = list_nodes[j]
			line = LineString([start_point, end_point])
			# TODO makes the scanning line "thick"?

			# This checks if line intersects with any solid collision
			if _CheckIntersectAnyPolygon(line, list_polygon1): continue
			log.Extra(f"    {j},{i} - ({start_point} , {end_point})")
			list_route.append((j,i))

			# This checks if line intersects with any movable objects
			is_route_closed.append(_CheckIntersectAnyPolygon(line, list_polygon2))

	log.Info(f"    Total of {len(list_route)} routes are viable")
	log.Info(f"     Among them, {sum(is_route_closed)} may be obstructed by BB, etc.")

def _CheckIntersectAnyPolygon(line, list_curr_polygon):
	for polygon in list_curr_polygon:
		if polygon.intersects(line): return True
	return False;





def _CheckRedundantRoutes():
	'''
	If taking a route doesn't reduce travel distance by 10% compared to taking any "2 other routes",
	 it is considered "redundant" and can be replaced with said 2 other routes instead
	'''
	log.Must(f"  Checking for paths being redundant...")

	# Calculate the length of all routes beforehand
	for route in list_route:
		pt_beg = list_nodes[ route[0] ]
		pt_end = list_nodes[ route[1] ]
		list_dist.append( math.dist(pt_beg, pt_end) )


	# Check through all combinations of routes
	# Redundant routes must form a triangle with the other 2 routes replacing it
	# When a triangle is found, compare the lengths
	count_route = len(list_route)
	for i in range(count_route):
		is_route_overlap.append(False)
		for j in range(i):
			for k in range(j):
				if not _IsTriangle( [list_route[i], list_route[j], list_route[k]] ): continue

				dist1 = list_dist[i]
				dist2 = list_dist[j]
				dist3 = list_dist[k]
				longest_dist = _IsLongestSideRedundant(dist1, dist2, dist3)
				if longest_dist < 0: continue
				elif longest_dist == dist1: is_route_overlap[i] = True
				elif longest_dist == dist2: is_route_overlap[j] = True
				elif longest_dist == dist3: is_route_overlap[k] = True
	log.Info(f'    Total of {sum(is_route_overlap)} routes are found redundant')



def _IsLongestSideRedundant(s1, s2, s3):
	'''(AI) Returns -1 if no redundant side, otherwise returns length of longest side'''

	# Find the longest side, and sum of the other 2
	longest = max(s1, s2, s3)
	if longest == s1:   sum_others = s2 + s3
	elif longest == s2: sum_others = s1 + s3
	else:               sum_others = s1 + s2
	
	# Compare the two values with a threshold value
	if threshold_redundance > longest / sum_others: return -1
	return longest



def _IsTriangle(tuples):
	'''(AI) Checks if 3 routes can form a triangle by counting if each node appears exactly twice'''

	# Count occurrences of each number
	count = {}
	for t in tuples:
		for num in t: count[num] = count.get(num, 0) + 1

	# Check if each number appears exactly twice
	for value in count.values():
		if value != 2: return False
	return True





#--------------------------------------------------#
'''Visualisation'''

def _VisualiseNodesAndRoutes(playdo):
	'''Apply in-editor changes such that it's easier to visualise the relation between nodes and routes'''
	log.Must(f"  Naming and coloring nodes & routes for visualisation...")

	# Color nodes green and assign number, iff nothing is assigned yet
	layer_node  = playdo.GetObjectGroup(layer_name_node,  False)
	for i in range(len(layer_node)):
		node = layer_node[i]
		if node.get("name") == None: node.set("name", str(i))
		if node.get("type") == None: node.set("type", "3")

	# Color nodes green and assign number, iff nothing is assigned yet
	layer_route = playdo.GetObjectGroup(layer_name_route, True)
	for i in range(len(list_route)):
		pt_beg = list_nodes[ list_route[i][0] ]
		pt_end = list_nodes[ list_route[i][1] ]
		attributes = {
			'id': "0", # TODO?
			'name' : str(i), 
			'type' : "4", 
			'x': "0",
			'y': "0"
		}
		new_route_obj = ET.Element('object', attributes)
		str_polypoint = f"{pt_beg[0]},{pt_beg[1]} {pt_end[0]},{pt_end[1]}"
		tiled_utils.SetPolyPointsOnObject( new_route_obj, str_polypoint )

		if is_route_closed[i]:  new_route_obj.set('type', "1")
		if is_route_overlap[i]: new_route_obj.set('type', "0")

		layer_route.append(new_route_obj)





#--------------------------------------------------#
'''Export'''

def _ExportCondenseData(playdo):
	'''
	This exports an object that contains all the necessary data needed for Unity
	  to perform path-searching for the node navigation feature.
	   - Node coordinates
	   - Route, the 2 start-/end-point nodes
	   -  ^^^   whether it's a maybe-route
	   -  ^^^   path-length? TBD

	Object overwrites itself each time the program is run
	Object is placed in an empty new layer if target layer is not found
	'''
	log.Must(f"  Exporting data in condensed form for Unity-parsing...")

	# Create new object
	temp_list = playdo.GetAllObjectsWithName(OBJ_NAME_EXPORT)
	new_data_obj = None
	if len(temp_list) == 0:
		log.Info(f"    Creating new meta object...")
		new_data_obj = ET.Element('object', {})
		playdo.GetObjectGroup(LAYER_NAME_EXPORT, False).append(new_data_obj)
	else:
		new_data_obj = temp_list[0]
		new_data_obj.clear()


	# Set attributes
	attributes = {
		'id': "0", 
		'name': OBJ_NAME_EXPORT, 
		'type': "9", 
		'x': "-32",
		'y': "0", 
		'width': "16",
		'height': "16"
	}
	for key, value in attributes.items(): new_data_obj.set(key, value)


	# Add node data as properties
	for i in range(len(list_nodes)):
		new_name = f"node_{i}"
		str_vertices = f"{list_nodes[i][0]},{list_nodes[i][1]}"
		tiled_utils.SetPropertyOnObject(new_data_obj, new_name, str_vertices)

	# Add route data as properties
	for i in range(len(list_route)):
		if is_route_overlap[i]: continue	# Skip entirely if is redundant
		new_name = f"route_{i}"
		str_vertices = f"{list_route[i][0]},{list_route[i][1]}"
		if is_route_closed[i]: str_vertices += f",{is_route_closed[i]}"	# Add extra for Maybe-Routes
		tiled_utils.SetPropertyOnObject(new_data_obj, new_name, str_vertices)

	log.Must(f"    Data exported successfully")





#--------------------------------------------------#










# End of File