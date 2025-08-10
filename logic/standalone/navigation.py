'''
Main logic for cli_nav.py

Requires installing shapely with the following command:
	pip install shapely

USAGE EXAMPLE:
    navigation.logic(playdo, passed_arguments)
'''

import time
import math
import xml.etree.ElementTree as ET
from shapely.geometry import LineString, Polygon

import logic.common.log_utils as log
import logic.common.tiled_utils as tiled_utils

#--------------------------------------------------#
'''Variables'''



'''Local Variables'''
cli_arguments = []
cli_configs = []

list_nodes = []		# (x-pos, y-pos, node-thickness), measured in pixels (i.e. int)
list_polygon1 = []	# (vertex1, vertex2, ...), where vertex = (int, int) for coordinates
list_polygon2 = []	#  ^

list_route = []	# [ (int, int) ], where each int keeps track of the node ID
list_dist = []	# [ float ]

is_route_closed = []	# [ bool ], for keepsing track of whether the route can be possible
is_route_overlap = []	# [ bool ], for keepsing track of redundant routes



'''Constants & Configurations'''
CONFIG_ROUTE_THICKNESS = True	# Whether the meta-data calculate the length of each route
CONFIG_SHOW_REDUNDANT  = False	# Whether redundant routes are shown
CONFIG_PRINT_NODE      = False	# Whether meta-data for nodes are generated

default_exported_attribtue = {
	'id': "0", 
	'type': "9", 
	'x': "0",
	'y': "-80", 
	'width': "64",
	'height': "64"
}





#--------------------------------------------------#
'''Public Functions'''

def SetConfigs(passed_configurations):
	for arg in passed_configurations: cli_configs.append(arg)



def logic(playdo, passed_arguments):
	log.Extra("")
	log.Must("Constructing paths from provided nodes...")
	start_time = time.time()

	for arg in passed_arguments: cli_arguments.append(arg)
	_ParseLevel(playdo)
	_CheckAllRoutes()
	_CheckRedundantRoutes()
	_VisualiseNodesAndRoutes(playdo)
	_ExportCondenseData(playdo)

	log.Must(f"~~End of All Procedures~~ ({round( time.time()-start_time, 3 )}s)")
	log.Extra("")





#--------------------------------------------------#
'''Parsing the Level'''

def _ParseLevel(playdo):
	log.Must(f"  Checking for nodes & collisions in level...")
	layer_name_node      = cli_arguments[0]
	layer_name_collision = cli_arguments[2]
	list_object_name     = cli_arguments[3]
	config_ignore_owp = cli_configs[1]

	# Register all collision objects
	list_duplicate  = []	# Temp array - Duplicated Nodes, would be automatically deleted
	list_collision1 = []	# Temp array - Solid Collision
	list_collision2 = []	# Temp array - Potential Collision, e.g. BB
	list_object_layers = playdo.GetAllObjectgroup()
	for layer in list_object_layers:
		# Nodes & "Manual Blockage"
		if layer.get('name') == layer_name_node:
			for obj in layer:
				# All ellipses are treated as nodes,
				#  polylines, 0-width and 0-height rectangles are ignored,
				#  otherwise everything else are treated as solid collision
				if obj.find('ellipse') is None:
					if obj.find('polyline') is not None: continue
					list_collision1.append(obj)
					continue

				# Register new nodes' coordinates
				new_x = int(obj.get("x"))
				new_y = int(obj.get("y"))
				if 'width'  in obj.attrib: new_x += int(obj.get("width"))/2
				if 'height' in obj.attrib: new_y += int(obj.get("height"))/2

				# Update thickness
				node_size = 16/2
				if 'width'  in obj.attrib: node_size = int(obj.get("width"))/2

				# Append only if it's not already in list, i.e. no duplicates at the same coordinate
				is_duplicate = False
				for node in list_nodes:
					if node[0] == new_x and node[1] == new_y: is_duplicate = True
				if is_duplicate: list_duplicate.append(obj)
				else: list_nodes.append( (new_x, new_y, node_size) )
			for obj in list_duplicate: layer.remove(obj)

		# Solid Collision
		if layer.get('name').startswith(layer_name_collision):
			for obj in layer:
				if obj.get("name") in list_object_name:
					list_collision2.append(obj)
				else:
					list_collision1.append(obj)

		# Variable Collision, e.g. BB
		if layer.get('name').startswith('objects'):
			for obj in layer:
				if obj.get('name') in list_object_name:
					list_collision2.append(obj)

	log.Info(f"    {len(list_nodes)} nodes found in \"{layer_name_node}\"")
	log.Info(f"    {len(list_collision1)} collision found")
	log.Info(f"    {len(list_collision2)} objects found")


	# Convert collisions into polygon for later uses
	log.Info(f"  Converting collision objects into vertices & polygon...")
	for obj in list_collision1:
		if _ObjectOutOfBound(obj, playdo.map_width, playdo.map_height): continue
		vertices = tiled_utils.GetVerticesFromObject(obj)
		if obj.find('polyline') is not None:
			if not config_ignore_owp: continue
			vertices = _LineToPolygon(vertices)
		if len(vertices) < 3: continue	# Single-point object is not accepted
		polygon = Polygon(vertices)
		list_polygon1.append(polygon)
		log.Extra(f"    {len(vertices)} pts - {vertices}")

	log.Info(f"  Converting BB objects into vertices & polygon...")
	for obj in list_collision2:
		if _ObjectOutOfBound(obj, playdo.map_width, playdo.map_height): continue
		vertices = tiled_utils.GetVerticesFromObject(obj)
		if len(vertices) < 3: continue	# Single-point object is not accepted
		polygon = Polygon(vertices)
		list_polygon2.append(polygon)
		log.Extra(f"    {len(vertices)} pts - {vertices}")

def _LineToPolygon(vertices):
	'''Effectively thicken the polyline so it's treated as a polygon'''
	len_og = len(vertices)
	for i in range(len_og):
		new_x = vertices[len_og-i-1][0] + 0.1
		new_y = vertices[len_og-i-1][1] + 0.1
		vertices.append( (new_x, new_y) )
	return vertices

def _ObjectOutOfBound(obj, map_w, map_h):
	'''It checks the 4 corners of each object to see if they are out of bound'''
	return False # Turns out this function is not actually needed... orz

	# Invalid object
	if obj.get("x") == None or obj.get("y") == None: return True

	# Set coordinate range, this tool uses pixels instead of Tiled units
	map_w = map_w * 16
	map_h = map_h * 16

	# Coordinates is negative (top-left)
	x1 = int(obj.get("x"))
	y1 = int(obj.get("y"))
	if not( 0 < x1 and x1 < map_w ): return True
	if not( 0 < y1 and y1 < map_h ): return True

	# Coordinates is negative (bottom-right)
	if obj.get("width")  == None: return False
	if obj.get("height") == None: return False
	x2 = x1 + int(obj.get("width"))  * 16
	y2 = y1 + int(obj.get("height")) * 16
	if not( 0 < x2 and x2 < map_w ): return True
	if not( 0 < y2 and y2 < map_h ): return True

	return False





#--------------------------------------------------#
'''Calculation'''

def _CheckAllRoutes():
	log.Must(f"  Checking for viable paths with {len(list_nodes)} nodes...")

	count_node = len(list_nodes)
	for i in range(count_node):
		end_point = list_nodes[i]
		for j in range(i):
			start_point = list_nodes[j]

			# Checks if line intersects with any solid collision
			if _CheckIntersectAnyPolygon(start_point, end_point, list_polygon1): continue

			log.Extra(f"    {j},{i} - ({start_point} , {end_point})")
			list_route.append((j,i))

			# This checks if line intersects with any movable objects
			is_route_closed.append(_CheckIntersectAnyPolygon(start_point, end_point, list_polygon2))

	log.Info(f"    Total of {len(list_route)} routes are viable")
	log.Info(f"     Among them, {sum(is_route_closed)} may be obstructed by BB, etc.")

def _CheckIntersectAnyPolygon(start_point, end_point, list_curr_polygon):
	if not CONFIG_ROUTE_THICKNESS:
		line = LineString([start_point, end_point])
		for polygon in list_curr_polygon:
			if polygon.intersects(line): return True
	else:
		# Find the perpendicular between 2 points
		x_diff = end_point[0] - start_point[0]
		y_diff = end_point[1] - start_point[1]
		magnitude = math.sqrt(x_diff*x_diff + y_diff*y_diff)
		perpendicular = (y_diff/magnitude, -x_diff/magnitude)

		# Offset the nodes based on its width, this is less computational heavy than finding tangents
		pt_1a_x = start_point[0] + perpendicular[0] * start_point[2]
		pt_1a_y = start_point[1] + perpendicular[1] * start_point[2]
		pt_1b_x = start_point[0] - perpendicular[0] * start_point[2]
		pt_1b_y = start_point[1] - perpendicular[1] * start_point[2]
		pt_2a_x = end_point[0] + perpendicular[0] * end_point[2]
		pt_2a_y = end_point[1] + perpendicular[1] * end_point[2]
		pt_2b_x = end_point[0] - perpendicular[0] * end_point[2]
		pt_2b_y = end_point[1] - perpendicular[1] * end_point[2]
		pt_1a = (pt_1a_x, pt_1a_y)
		pt_1b = (pt_1b_x, pt_1b_y)
		pt_2a = (pt_2a_x, pt_2a_y)
		pt_2b = (pt_2b_x, pt_2b_y)

		# Construct the new lines that simulate a "thick route"
		line1 = LineString([pt_1a, pt_2a])
		line2 = LineString([pt_1b, pt_2b])
		for polygon in list_curr_polygon:
			if polygon.intersects(line1): return True
			if polygon.intersects(line2): return True
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
#				log.Extra(f'    {i} {j} {k} - {round(dist1)} {round(dist2)} {round(dist3)} - {round(longest_dist)}')
				if longest_dist < 0: continue
				elif longest_dist == dist1: is_route_overlap[i] = True
				elif longest_dist == dist2: is_route_overlap[j] = True
				elif longest_dist == dist3: is_route_overlap[k] = True

				continue
				if   longest_dist == dist1: log.Extra(f'{i} - {j},{k}')
				elif longest_dist == dist2: log.Extra(f'{j} - {i},{k}')
				elif longest_dist == dist3: log.Extra(f'{k} - {i},{j}')

	log.Info(f'    Total of {sum(is_route_overlap)} routes are found redundant')



def _IsLongestSideRedundant(s1, s2, s3):
	'''(AI) Returns -1 if no redundant side, otherwise returns length of longest side'''
	threshold_redundance = cli_arguments[4]

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
	layer_name_node      = cli_arguments[0]
	layer_name_route     = cli_arguments[1]

	# Color nodes green and assign number, iff nothing is assigned yet
	layer_node  = playdo.GetObjectGroup(layer_name_node,  False)
	node_id = 0	# Has to be counted separately, for skipping non-node object
	for i in range(len(layer_node)):
		node = layer_node[i]
		if node.find('ellipse') is None: continue
		node.set("name", _NodeId2Name(node_id))	# Always overwrite existing names
		node_id += 1
		if node.get("type") == None: node.set("type", "3")	# Does not overwrite existing color/type

	# Color routes green and assign number, iff nothing is assigned yet
	layer_route = playdo.GetObjectGroup(layer_name_route, False)
	for obj in list(layer_route):
		if obj.find('polyline') is None: continue	# Skip if object is not route
		layer_route.remove(obj)				# Removes all existing routes
	for i in range(len(list_route)):
		pt_beg = list_nodes[ list_route[i][0] ]
		pt_end = list_nodes[ list_route[i][1] ]
		attributes = {
			'id': "0", # TODO?
#			'name' : str(i), 
			'type' : "4", 
			'x': "0",
			'y': "0"
		}
		new_route_obj = ET.Element('object', attributes)
		str_polypoint = f"{pt_beg[0]},{pt_beg[1]} {pt_end[0]},{pt_end[1]}"
		tiled_utils.SetPolyPointsOnObject( new_route_obj, str_polypoint )

		if is_route_closed[i]:  new_route_obj.set('type', "1")
		if is_route_overlap[i]:
			if CONFIG_SHOW_REDUNDANT:
				new_route_obj.set('type', "0")
			else:
				continue

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
	obj_name_default     = cli_arguments[5]
	config_calculate_dist = cli_configs[0]

	# Add route data as properties
	obj_route = _MakeXmlObject(playdo, f"{obj_name_default}", f"_{len(list_nodes)}")
	for i in range(len(list_route)):
		if is_route_overlap[i]: continue	# Skip entirely if is redundant
		new_name = f"{_NodeId2Name(list_route[i][0])}_{_NodeId2Name(list_route[i][1])}"
		x1 = list_nodes[ list_route[i][0] ][0]
		y1 = list_nodes[ list_route[i][0] ][1]
		x2 = list_nodes[ list_route[i][1] ][0]
		y2 = list_nodes[ list_route[i][1] ][1]
		str_dist = ""
		if is_route_closed[i]: str_dist = "-"	# Negative for Maybe-Routes
		if config_calculate_dist:
			str_dist += f"{int( math.sqrt((x2 - x1)**2 + (y2 - y1)**2) / 16 + 0.5 )}"
		else:   str_dist += "100"
		tiled_utils.SetPropertyOnObject(obj_route, new_name, str_dist)
	log.Must(f"    Data for Routes exported successfully")

	if not CONFIG_PRINT_NODE: return
	# Add node data as properties
	obj_node = _MakeXmlObject(playdo, "TRAVEL_NODE_LOCATIONS")
	obj_node.set("y", "32")
	for i in range(len(list_nodes)):
		new_name = f"{i}"
		str_vertices = f"{int( list_nodes[i][0]/16 )},{int( list_nodes[i][1]/16 )}"
		tiled_utils.SetPropertyOnObject(obj_node, new_name, str_vertices)
	log.Must(f"    Data for Nodes exported successfully")



def _NodeId2Name(id):
	if id >= 100: log.Must("\n\n\n\t\tERROR! Node exceeds limit of 100!\n\n\n")
	if id < 10: return f"0{id}"
	return f"{id}"

def _MakeXmlObject(playdo, name_prefix, num_suffix):
	layer_name_export    = cli_arguments[6]

	# If there is an existing meta-data object, delete it
	obj_layer = playdo.GetObjectGroup(layer_name_export, False)
	for obj in obj_layer:
		if obj.get("name") == None: continue
		if not obj.get("name").startswith(name_prefix): continue
		obj_layer.remove(obj)
		log.Info(f"    Removing old meta-data object...")

	# Create new object, TODO just delete the old one outright, instead of replacing?
	log.Info(f"    Creating new meta-data object...")
	new_data_obj = ET.Element('object', {})
	attributes = default_exported_attribtue
	for key, value in attributes.items(): new_data_obj.set(key, value)

	# Insert the object, NEEDS to be at the top
	obj_layer.insert(0, new_data_obj)
	new_data_obj.set('name', f'{name_prefix}{num_suffix}')

	return new_data_obj





#--------------------------------------------------#










# End of File