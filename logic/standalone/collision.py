'''
Logic module that can
 - TBA

Steps:
 1. Filter the applicable collision objects from playdo as polygons
 2. Merge all polygons that are adjacent into big simple polygons
 3. Split into smaller polygons based on methods
 4. Output polygons into a new object layer

USAGE EXAMPLE:
	main_logic.logic(playdo)
	raw_dict = conflict.CheckConflicts(playdo, _LIST_LIGHTING_OBJ)
	pruned_dict = conflict.PruneConflicts(playdo, conflict_dictionary)
	conflict.FixConflicts(playdo, pruned_dict)
'''

import os
import logic.common.log_utils as log
import logic.common.tiled_utils as tiled_utils

import shapely
from shapely.geometry import Polygon, MultiPolygon, box, Point
from shapely.ops import unary_union
import numpy as np

#-----------------------------------------------------#
#-------------------- [Variables] --------------------#

# Output
_output_folder1 = "output/"
_output_folder2 = _output_folder1 + "levels/"
_output_file    = _output_folder1 + "_merged.txt"

# Names
layer_name_big_poly = "_big_poly"
layer_name_final    = "collisions split"
layer_name_excluded = "collisions excluded"

# cli_merge_poly
layer_name_merged = "_collisions merged"
layer_name_backup = "_collisions_merged_backup"
layer_name_base   = None	# Is updated during runtime to be the "bottom-most tilelayer name"
merge_excluded_type = ['rare']
merge_excluded_name = ['break_block']
list_concave_type = []		# For logging purpose only

# Config
config_always_merge_big_poly = True



#------------------------------------------------------------#
#-------------------- [Public Functions] --------------------#

def MergePolygonsByType(playdo, allow_concave):
	'''TODO'''
	log.Must(f'  Merging collisions polygons... Concave allowed? {allow_concave}')

	convex_only = not allow_concave

	# Obtain the filtered list of XML objects
	dict_type_of_objects = _FilterCollisionWithTypes(playdo)

	# Each list of objects here will be merged into one to multiple isolated polygons
	list_new_vertices = []
#	for list_objects in list_type_of_objects:
	for type_str, list_objects in dict_type_of_objects.items():
		list_vertices = ObjectToVertices(list_objects, type_str)
		list_merged_vertices = MergeAdjacentPolygons(list_vertices, convex_only, type_str)
		for vertices in list_merged_vertices: list_new_vertices.append(vertices)

	# Exit if no collision object is filtered in; The level should be unchanged
	if layer_name_base == None:
		log.Must(f'  No collision needs to be merged. Exiting now...')
		log.Must('')
		return True

	# Log out the concave types
	if list_concave_type != []:
		log.Must(f'  WARNING! {len(list_concave_type)} sets discovered to be Concave!')
		log.Must(f'   Culprit Sets were: {list_concave_type}')

	# Move the new merged objects to existing layer
	list_new_obj = SetVerticesToObjectLayer(playdo, list_new_vertices)
	current_layer = playdo.GetObjectGroup(layer_name_base, discard_old = False, create_new = True)
	for obj in list_new_obj: current_layer.append(obj)

	# Move the already merged objects out to the backup layer
	has_backup = ( playdo.GetObjectGroup(layer_name_backup, discard_old = False, create_new = False) != None )
	backup_layer = playdo.GetObjectGroup(layer_name_backup, discard_old = False, create_new = True)
	if not has_backup: backup_layer.set('visible', '0')    # Only change if layer doesn't exist prior
	for type_str, list_objects in dict_type_of_objects.items():
		for obj in list_objects: tiled_utils.MoveObjectToNewObjectgroup(playdo, obj, backup_layer)

	log.Must('')


def _FilterCollisionWithTypes(playdo):
	'''TODO'''
	global layer_name_base
	log.Extra('')
	log.Info(f'  Filtering objects with non-empty Type attribute...')
	list_objectgroup = playdo.GetAllObjectgroup()
	dict_type = {}
	list_obj      = []
	list_excluded = []
	for layer in list_objectgroup:
		layer_name = layer.get('name')
		if not layer_name.startswith('collisions'): continue
		for obj in layer:
			# Filters out the non-applicable objects
			obj_type = obj.get('type')
			if obj_type == None: continue						# Ignore if no type is specified
			if obj_type in merge_excluded_type: continue		# Ignore if type is in excluded list
			if obj.get('name') in merge_excluded_name: continue	# Ignore if name is in excluded list
			if obj.find('polyline') != None: continue			# Ignore if not a solid polygon, e.g. OWP

			# Add objects to the dictionary
			if not obj_type in dict_type: dict_type[obj_type] = []
			dict_type[obj_type].append(obj)

			# This keeps track of which layer to output the merged polygons at
			if layer_name_base == None: layer_name_base = layer_name
	dict_type = dict(sorted(dict_type.items()))

#	print(len(dict_type))
	key_str = ''
	for key in dict_type: key_str += f'\'{key}\' '
	log.Must(f'  {len(dict_type)} sets of polygon found - {key_str}')
	for key, value in dict_type.items(): log.Info(f'    \"{key}\" : {len(value)} polygons')

	return dict_type





def logic(playdo, arguments):
	'''TODO'''
	log.Must('')
	log.Must(f'  Starting procedure...')

	# Check if Big Polygon layer exists prior
	layer = playdo.GetObjectGroup(layer_name_big_poly, discard_old = False, create_new = False)
	does_big_poly_layer_exist = (layer != None)
	log.Must('')
	log.Must(f' Big Polygon Layer exists? {does_big_poly_layer_exist}')

	# Skips checking big poly if already
	if not does_big_poly_layer_exist or config_always_merge_big_poly:
#		log.Must('')
		log.Must(f'  vvvvv New Big Polygon layer will now be created vvvvv')

	 	# Process 1 - Filter the applicable collision objects from playdo as polygons
		list_objects, list_excluded = FilterAllCollisionObjects(playdo)
		list_vertices = ObjectToVertices(list_objects)

	 	# Process 2 - Merge all polygons that are adjacent (recursively)
		list_merged_vertices = MergeAdjacentPolygons(list_vertices)
#		SetBigPolygons(playdo, list_merged_verrices, list_excluded)
		SetVerticesToObjectLayer(playdo, list_merged_vertices, layer_name_big_poly)
		if len(list_excluded) > 0:
			layer_excluded = playdo.GetObjectGroup(layer_name_excluded, discard_old = True, create_new = True)
			for obj in list_excluded: layer_excluded.append(obj)
	else:
		# TODO
		return
		list_merged_vertices = list_vertices

 	# Process 3 - Split into smaller polygons based on methods
	log.Must('')
#	list_split_vertices = SplitPolygonsByGrid(list_merged_vertices, 1)
	list_split_vertices = SplitPolygonsByGrid(list_merged_vertices, 2)

 	# Process 4 - Output polygons into a new object layer
#	MakeNewObjectLayer(playdo, list_split_vertices)
	SetVerticesToObjectLayer(playdo, list_split_vertices, layer_name_final)

	log.Must('')



#----------------------------------------------------------#
#-------------------- [Testing Ground] --------------------#

def SplitPolygonsByGrid(list_merged_verrices, grid_size_unit):
	log.Extra('')
	log.Must(f'  Splitting {len(list_merged_verrices)} objects, by grid of size {grid_size_unit}...')
	grid_size_px = grid_size_unit * 16

	list_new_vertices = []
	for vertices in list_merged_verrices:
		polygon = VerticesToPolygon(vertices)
		pieces = split_polygon_by_grid( polygon, grid_size_px )
		for polygon_piece in pieces: list_new_vertices.append(PolygonToVertices(polygon_piece))
#		print()
#		print(vertices)
#		print(f"Original polygon split into {len(pieces)} pieces.")
#		for idx, piece in enumerate(pieces[:3]):  # show bounds for first 3 pieces
#			print(f" Piece {idx+1} Bounding Box: {piece.bounds}")

	log.Must(f'   Split into a total of {len(list_new_vertices)} objects...')
	return list_new_vertices


def split_polygon_by_grid(polygon, grid_size_px = 1):
    """
    Splits a shapely polygon into pieces no larger than max_size x max_size.
    """
    # 1. Get the bounding box limits of the input polygon
    minx, miny, maxx, maxy = polygon.bounds
    
    # 2. Create grid sequences with intervals of max_size
    x_coords = np.arange(minx, maxx + grid_size_px, grid_size_px)
    y_coords = np.arange(miny, maxy + grid_size_px, grid_size_px)
    
    split_pieces = []
    
    # 3. Iterate through every cell in the grid
    for i in range(len(x_coords) - 1):
        for j in range(len(y_coords) - 1):
            # Create a 10x10 bounding box for the current grid tile
            grid_box = box(x_coords[i], y_coords[j], x_coords[i+1], y_coords[j+1])
            
            # 4. Intersect the original polygon with this box tile
            intersection_piece = polygon.intersection(grid_box)
            
            # 5. Save the piece if it contains a valid polygon structure
            if not intersection_piece.is_empty:
                # If a tile splits a complex shape into multiple separate parts,
                # flatten them out into individual single polygons.
                if isinstance(intersection_piece, MultiPolygon):
                    for sub_poly in intersection_piece.geoms:
                        if isinstance(sub_poly, Polygon) and not sub_poly.is_empty:
                            split_pieces.append(sub_poly)
                elif isinstance(intersection_piece, Polygon):
                    split_pieces.append(intersection_piece)
                    
    return split_pieces




def MakeNewObjectLayer(playdo, list_vertices):
	SetVerticesToObjectLayer(playdo, list_vertices, layer_name_final)
	return

	log.Extra('')
	log.Must(f'  Doing stuff... {4}')

	# Big polygon objects
	layer_split_poly = playdo.GetObjectGroup(layer_name_final, discard_old = True, create_new = True)
	for vertices in list_vertices:
		obj = tiled_utils.CreateXMLObject()
		tiled_utils.SetVerticesOnObject(obj, vertices)
		layer_split_poly.append(obj)

def SetVerticesToObjectLayer(playdo, list_vertices, layer_name = None, create_new_layer = True):
	log.Extra('')
	if layer_name != None: log.Must(f'  Setting {len(list_vertices)} polygon objects from vertices... (to \"{layer_name}\" layer)')
	else:                  log.Must(f'  Creating {len(list_vertices)} polygon objects from vertices...')
	list_obj = []
	for vertices in list_vertices:
		obj = tiled_utils.CreateXMLObject()
		is_rectangle = _CheckIsRectangle(vertices)
		if is_rectangle:
#			print("Is rectangle")
			x,y,w,h = _GetRectangleData(vertices)
			tiled_utils.SetRectangleAttributeOnObject(obj, x, y, w, h)
		else:
#			print("Is polygon")
			tiled_utils.SetVerticesOnObject(obj, vertices)
		list_obj.append(obj)

	if layer_name != None and create_new_layer:
		layer = playdo.GetObjectGroup(layer_name, discard_old = True, create_new = True)
		for obj in list_obj: layer.append(obj)

	return list_obj


def _CheckIsRectangle(vertices):
	'''
	 Returns True if vertices can form an upright rectangle
	 TODO also check for tilted?
	'''
	# 1. A rectangle must have 4 distinct points
#	print(len(vertices))
#	print(vertices)
	if len(set(vertices)) != 4: return False

	p1 = vertices[0]
	p2 = vertices[1]
	p3 = vertices[2]
	p4 = vertices[3]
	points = [p1, p2, p3, p4]

	# 2. Find the center point (the average of all X and Y coordinates)
	cx = sum(p[0] for p in points) / 4
	cy = sum(p[1] for p in points) / 4

	# 3. Calculate the squared distance from each point to that center
	# (We use squared distance to avoid slow square-root math)
	distances = [((p[0] - cx)**2 + (p[1] - cy)**2) for p in points]

	# 4. Check if all 4 distances match.
	# We use a tiny threshold (1e-9) to handle floating-point math safely.
	first_distance = distances[0]
	return all(abs(d - first_distance) < 1e-9 for d in distances)

def _GetRectangleData(vertices):
	'''
	 TODO tilted rectangle?
	'''
	poly = Polygon(vertices)

	minx, miny, maxx, maxy = poly.bounds
	top_left = (minx, maxy)
	x = int(minx)
	y = int(miny)
	w = int(maxx - minx)
	h = int(maxy - miny)
	log.Info(f'   x,y,w,h : {x}, {y}, {w}, {h} ')
	return x,y,w,h


	# Find top-left vertex: minimum x, maximum y
	# Using a key that maximizes y and minimizes x: (-y, x)
	coords = list(poly.exterior.coords)[:-1]
	top_left = min(coords, key=lambda pt: (-pt[1], pt[0]))
	print(Point(top_left))  # Output: POINT (0 5)

	# 1. Get the minimum rotated (fitted) rectangle
	rot_rect = poly.minimum_rotated_rectangle

	# 2. Get the axis-aligned bounding box (polygon)
	aligned_box = poly.envelope

	# 3. Get the bounds tuple and create a box
	minx, miny, maxx, maxy = poly.bounds
	bounding_box = box(minx, miny, maxx, maxy)

	print("Rotated Rect:", rot_rect)
	print("Axis-Aligned Box:", aligned_box)







#-------------------------------------------------------#
#-------------------- [Procedure 1] --------------------#

def FilterAllCollisionObjects(playdo):
	log.Extra('')
	log.Must(f'  Filtering objects from playdo...')
	list_objectgroup = playdo.GetAllObjectgroup()
	list_obj      = []
	list_excluded = []
	for layer in list_objectgroup:
		layer_name = layer.get('name')
		if not layer_name.startswith('collisions'): continue
		for obj in layer:
			if obj.find('polyline') != None or obj.find('properties') != None:
				list_excluded.append(obj)
			else:
				list_obj.append(obj)
#	print(len(list_obj))
	return list_obj, list_excluded

def ObjectToVertices(list_obj, type_str = None):
	if type_str == None: log.Info(f'   Converting {len(list_obj)} objects into vertices / polypoints...')
	else:                log.Info(f'   Converting {len(list_obj)} objects into vertices / polypoints from \"{type_str}\"...')
	count = 0
	list_vertices = []
	for obj in list_obj:
		count += 1
		log.Extra(f'    Polygon {count}:')
		vertices = tiled_utils.GetVerticesFromObject(obj)
		for index, pt_tuple in enumerate(vertices):
			new_x = int(pt_tuple[0])
			new_y = int(pt_tuple[1])
			vertices[index] = (new_x, new_y)
			log.Extra(f'     {index} : {vertices[index]}')
			if new_x % 4 != 0 or new_y % 4 != 0: log.Must(f'\nWARNING! Vertex position is not snapped to grid! {vertices[index]}')
#			print(index)
		list_vertices.append(vertices)
	return list_vertices



#-------------------------------------------------------#
#-------------------- [Procedure 2] --------------------#

def MergeAdjacentPolygons(list_vertices, forced_convex = False, type_str = None):
	'''
	 Returns the list of vertices after merging all adjacent ones
	 [
	  [ (x1a,y1a), (x1b,y1b), (x1c,y1c) ],
	  [ (x2a,y2a), (x2b,y2b), (x2c,y2c), (x2d,y2d) ],
	 ]
	'''
	log.Extra('')
	if type_str == None: log.Must(f'  Merging {len(list_vertices)} polygons...')
#	else:                log.Must(f'    Merging {len(list_vertices)} polygons from \"{type_str}\"...')

	list_polygon = []
	for vertices in list_vertices:
		list_polygon.append(Polygon(vertices))
	merged_polygons = unary_union(list_polygon)

	list_new_vertices = []
	log.Info(f'    Is MultiPolygon? {merged_polygons.geom_type == "MultiPolygon"}')
	if merged_polygons.geom_type != 'MultiPolygon': merged_polygons = MultiPolygon([merged_polygons])

	# Simplify the polygons and add vertices into new array
	for polygon in merged_polygons.geoms:
		new_vertices = PolygonToVertices(polygon, forced_convex, type_str)
		list_new_vertices.append(new_vertices)
	return list_new_vertices

def PolygonToVertices(polygon, forced_convex = False, type_str = None):
	# This removes the collinear points
	polygon = polygon.simplify(0)

	# Special Case - Collinear point at first index
	# Solve by shifting vertices index by 1 before simplifying again
	coords = np.array(polygon.exterior.coords[:-1])
	shifted_coords = np.roll(coords, shift=1, axis=0)
	shifted_poly = Polygon(shifted_coords)
	polygon = shifted_poly.simplify(0)

	# If config is on, check if polygon is convex, and print if yes
	if forced_convex: 
		convex_polygon = polygon.convex_hull
		if not polygon.equals(convex_polygon):
#			log.Info(f'WARNING! Attempting to merged a concave polygon!!')
			polygon = convex_polygon
			list_concave_type.append(type_str)

	new_vertices = []
	for x, y in polygon.exterior.coords:
		pos = (int(x), int(y))
		new_vertices.append(pos)
	return new_vertices

def VerticesToPolygon(vertices):
	return Polygon(vertices)



def SetBigPolygons(playdo, list_vertices, list_excluded_objects):
	'''TODO'''
	log.Extra('')
	log.Must(f'   Setting {len(list_vertices)} polygons in layer...')

	# Big polygon objects
	SetVerticesToObjectLayer(playdo, list_vertices, layer_name_big_poly)
	'''
	layer_big_poly = playdo.GetObjectGroup(layer_name_big_poly, discard_old = True, create_new = True)
	for vertices in list_vertices:
		obj = tiled_utils.CreateXMLObject()
		tiled_utils.SetVerticesOnObject(obj, vertices)
		layer_big_poly.append(obj)
#		print('make new obj')
	'''

	# Unmodified objects
	if len(list_excluded_objects) == 0: return
	layer_excluded = playdo.GetObjectGroup(layer_name_excluded, discard_old = True, create_new = True)
	for obj in list_excluded_objects: layer_excluded.append(obj)



#-------------------------------------------------------#
#-------------------- [Procedure 3] --------------------#



#-------------------------------------------------------#
#-------------------- [Procedure 4] --------------------#



#-----------------------------------------------------------#
#-------------------- [General Utility] --------------------#
# to be relocated?

def _Indent(s, min_len):
	'''Return the same string, with consistent spacing added to the end'''
	return ( s + ' ' * (min_len-len(s)) )

def _FormatNumS2TU(num_in_str):
	'''Shortcut, for converting string (coordinates measured in pixels) intoto Tiled units'''
	if num_in_str == None: return ''
	return str(int( round(float(num_in_str))/16 ))





#--------------------------------------------------#










# End of File