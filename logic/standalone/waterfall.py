'''
Logic module that can create waterfall objects.


USAGE EXAMPLE:

'''

import logic.common.log_utils as log
import logic.common.tiled_utils as tiled_utils

#--------------------------------------------------#
'''Variables'''

# Template settings
LIST_WATERFALL_TILE_ID = [2560, 2561, 2562, 2563]



# Session settings
LAYER_SORT_DIFF = 10	# Difference of sort_value between consecutive tilelayers
LAYER_SORT_ADDON = 5	# Difference of sort_value between waterfalls and tilelayers
BLOCKOUT_PREFIX = "_FALLS_"	# Prefix of tilelayers with waterfall blockout
OBJECTGROUP_PREFIX = "objects_waterfall_"



# DEBUG, to be deleted when done
PRINT_SCAN_OUTPUT = not True	# Switch between True or False here, this toggles the printing of return value





#--------------------------------------------------#
'''Public Functions'''

def ScanForWaterFalls(playdo):
	'''
	Returns a list of tuples, where each tuple contains the data needed to create a waterfall.
	Each tuple contains the following data: (start_position, end_position, sort_layer, theme)
	 - start_position - a tuple of x,y coordinates signifying where the waterfall starts
	 - end_position - a tuple of x,y coordinates signifying where the waterfall ends
	 - sort_layer - a string specifying the sort layer and order of the waterfall. For example, "bg_tiles,15"
	 - theme - a string referencing the object template, e.g. "lava" or "meadow", for properties such as color, alpha, and speed
	'''

	list_all_tilelayer_name = playdo.GetAllTileLayerNames()
	list_all_tiles_2d = playdo.GetAllTiles2d()
	log.Extra("")
	log.Info("Scanning for waterfalls...")

	list_all_waterfalls = []
	curr_sort_str = "bg_tiles,"
	curr_sort_num = LAYER_SORT_ADDON - LAYER_SORT_DIFF

#	for tilelayer_name in list_all_tilelayer_name:	# Doesn't work when 2 layers have same name, to be deleted
	for i in range( len(list_all_tilelayer_name) ):
		tilelayer_name = list_all_tilelayer_name[i]

		# Update the current sort string & number
		if tilelayer_name.startswith("bg"):
			curr_sort_num += LAYER_SORT_DIFF
		elif tilelayer_name.startswith("fg"):
			curr_sort_num += LAYER_SORT_DIFF
			if curr_sort_str.startswith("bg"):
				curr_sort_str = "fg_tiles,"
				curr_sort_num = LAYER_SORT_ADDON
		full_sort_str = curr_sort_str + str(curr_sort_num)
#		print(f'{tilelayer_name}\t\t{full_sort_str}')    # Debug, to be deleted
		if not tilelayer_name.startswith(BLOCKOUT_PREFIX): continue


		# Determines the template used, partly based on sort_value
		theme = tilelayer_name.replace( BLOCKOUT_PREFIX, "" )
		if curr_sort_str.startswith("bg"): theme += " bg"
		else : theme += " fg"
		log.Extra("")
		log.Info(f'  Theme: \"{theme}\", at \"{full_sort_str}\"')


		# Process the tile2D to find the coordinates, then add to the full list
		list_curr_waterfalls = _MakeListOfWaterfallCoordinates( list_all_tiles_2d[i] )
		for waterfall in list_curr_waterfalls:
			list_all_waterfalls.append( (
				waterfall[0],
				waterfall[1],
				waterfall[2],
				full_sort_str,
				theme
			) )

	# Debug, to be deleted
	if PRINT_SCAN_OUTPUT:	# Switch between True or False here, this toggles the printing of return value
		log.Extra("\n  DEBUG - Printing waterfalls")
		for waterfall in list_all_waterfalls:
			log.Extra("")
			for tuple_value in waterfall: log.Extra("    " + str(tuple_value))
		log.Extra("")
		log.Extra(list_all_waterfalls)


	log.Info(f'Total of {len(list_all_waterfalls)} waterfalls found in all layers')
	log.Extra("")
	return list_all_waterfalls





def CreateWaterfalls(waterfall_template, playdo, list_waterfall_layer):
	'''
	Generate new object layer(s) that contains the new waterfall objects after process the following:
	 - XML containing the pre-made waterfall templates
	 - XML of the current level to have new waterfalls created for
	 - list of tuples from ScanForWaterFalls(); Each tuple contains coordinates, sort values, and template name
	'''

	''' =====[Pseudo-code]=====

	get all objects from waterfall_template
	dictionary_waterfall = {}
	  make a dictionary, key is object layer name & value is object itself

	for waterfall_layer in list_waterfall_layer:

		# Unpack info in each waterfall_layer
		object_layer_name = OBJECTGROUP_PREFIX + waterfall_layer[0]
		template_object = dictionary_waterfall[ waterfall_layer[1] ]
		new_sort_value = waterfall_layer[2]
		list_coordinates = waterfall_layer[3]

		# Creating the new object layer
		new_object_layer = make_layer(object_layer_name)
		for coordinates in curr_waterfall_layer:
			new_polypoint = _MakePolypoints( coordinates )

			new_object = _CopyXMLObject( template_object )
			new_object.set( "x", coordinates[0] )
			new_object.set( "y", coordinates[2] )
			new_object.SetProperty( "thickness", ??? )
			new_object.SetPolypoint( new_polypoint )

			new_object_layer.add_object( new_object )
	'''





#--------------------------------------------------#
'''Utility for Scanning'''

def _MakeListOfWaterfallCoordinates(tiles2d):
	'''
		Process the tile2D, then find the coordinates and thickness of each waterfall
		This assumes waterfall is vertical, accepts horizontal waterfall too? (TODO)
	'''
	map_height = len(tiles2d)
	map_width  = len(tiles2d[0])

	list_waterfalls = []
	is_tile_scanned = [ [False for x in range(map_width)] for y in range(map_height) ]
	for i in range(map_height):
		for j in range(map_width):
			# Skip if tile has already been scanned
			if is_tile_scanned[i][j]: continue

			# Skip if it's not a waterfall tile
			curr_or = tiles2d[i][j]	>> 29
			curr_id = tiles2d[i][j] - (curr_or << 29) - 1
			if not curr_id in LIST_WATERFALL_TILE_ID: continue
#			print(f'{tiles2d[i][j]} -> {curr_id}, {curr_or}')	# DEBUG

			# Check all connected tile
			waterfall_len = 1
			for i2 in range(map_height):	# TODO find better way to iterate?
				if i2 <= i: continue
				if tiles2d[i2][j] != tiles2d[i][j]: break
				waterfall_len += 1
				is_tile_scanned[i2][j] = True

			# Set waterfall values
			start_y = i
			start_x = j + _GetWaterfallOffsetX(curr_id, curr_or)
			length = waterfall_len
			thickness = _GetWaterfallThickness(curr_id)
			log.Extra(f'    At ({start_x}, {start_y}), len = {length}, width = {thickness}')

			# Check if this waterfall can merge into any existing one
			#   this allows waterfall with thickness greater than 1
			# TODO 

			# Append new waterfall to list
			list_waterfalls.append( ((start_x, start_y), length, thickness) )

	log.Info( f'  Total of {len(list_waterfalls)} waterfalls found' )
	return list_waterfalls



def _GetWaterfallOffsetX(curr_id, curr_or):
	'''Return float value between waterfall's starting point, and nearest grid parallel to y-axis'''
	# Skip if the waterfall is horizontal
	if curr_or == 1: return 0
	if curr_or == 3: return 0
	if curr_or == 5: return 0
	if curr_or == 7: return 0

	# If tile is flipped, measure from the other side instead
	offset = _GetWaterfallThickness(curr_id) / 2
	if curr_or == 4: offset = 1 - offset
	if curr_or == 6: offset = 1 - offset

	return offset



def _GetWaterfallThickness(curr_id):
	'''Return the thickness of tile based on ID (hard-coded)'''
	if curr_id == 2560: return 0.25
	if curr_id == 2561: return 0.5
	if curr_id == 2562: return 0.75
	if curr_id == 2563: return 1
	return 0





#--------------------------------------------------#
'''Utility for Object Creation'''

def _MakePolypoints( coordinates ):
	'''Converts coorinate (tuple of int tuples) into polypoint (string)
	 e.g. [ (64,32), (0, 128) ] => "0,0 -64,96"
	'''

	# TODO

	return ""



# TODO relocate to tiled_utils?
def _CopyXMLObject(obj):
	'''Deep-copy an XML objects, mostly for making new objects from a duplicated template'''

	# TODO

	return obj





#--------------------------------------------------#










# End of File