'''
Logic module that can create waterfall objects.


USAGE EXAMPLE:

'''

import copy
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
NEW_OBJECT_LAYER_NAME = "objects_waterfall_auto"



# DEBUG, to be deleted when done
PRINT_SCAN_OUTPUT = not True	# Toggle between True or False to print return values





#--------------------------------------------------#
'''Public Functions'''

def ScanForWaterFalls(playdo):
	'''
	Returns a list of tuples, where each tuple contains the data needed to create a waterfall.
	Each tuple contains the following data: (start_position, end_position, sort_layer, theme)
	 - start_position - a tuple of x,y coordinates signifying where the waterfall starts
	 - end_position - a tuple of x,y coordinates signifying where the waterfall ends
	 - sort_layer - a string specifying the sort layer and order of the waterfall. For example, "bg_tiles,15"
	 - theme - a string referencing the object template, e.g. "lava" or "meadow",
	     properties (e.g. color, alpha, speed) are copied from object template
	'''

	list_all_tilelayer_name = playdo.GetAllTileLayerNames()
	list_all_tiles_2d = playdo.GetAllTiles2d()
	log.Extra("")
	log.Info("Scanning for waterfalls...")

	list_all_waterfalls = []
	curr_sort_str = "bg_tiles,"
	curr_sort_num = LAYER_SORT_ADDON - LAYER_SORT_DIFF

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
	return list_all_waterfalls





def CreateWaterfalls(playdo_template, playdo, list_all_waterfalls):
	'''
	Generate new object layer that contains the new waterfall objects after process the following:
	 - XML containing the pre-made waterfall templates
	 - XML of the current level, where new waterfalls are created at
	 - list of tuples from ScanForWaterFalls()
	'''
	log.Extra("")
	log.Info("Creating waterfall obejcts...")


	# Use the name of each objectgroup as key, and the first object as value
	log.Info("  Registering waterfall templates...")
	dictionary_waterfall = {}
	dictionary_particles = {}
	for objectgroup in playdo_template.GetAllObjectgroup(False):
		# Check if the water_line object exists
		water_line_obj = None
		for object in objectgroup:
			if tiled_utils.GetNameFromObject(object) == 'water_line':
				water_line_obj = object
				break
		if water_line_obj == None: continue
#		else: continue	# DEBUG, enable this line to simulate when no template is found
		layer_name = tiled_utils.GetNameFromObject(objectgroup)
		dictionary_waterfall[layer_name] = water_line_obj

		# Check if associated env_particles object exists
		particles_obj = None
		for object in objectgroup:
			if tiled_utils.GetNameFromObject(object) == 'env_particles':
				particles_obj = object
				break
		if particles_obj != None:
			dictionary_particles[layer_name] = particles_obj

		log.Extra(f'    - {layer_name} - {dictionary_waterfall[layer_name]}')


	# Create waterfalls in a new object layer
	log.Info("  Creating new waterfall objects...")
	new_objectgroup = playdo.GetObjectGroup(NEW_OBJECT_LAYER_NAME)
	count_new = 0
	for waterfall in list_all_waterfalls:
		# Unpack info in each tuple
		start_pos = waterfall[0]
		end_pos = "0," + str(waterfall[1]*16)
#		end_pos = (start_pos[0], start_pos[1] + waterfall[1]) # DEBUG
#		end_pos_str = _MakePolypoints( start_pos, end_pos ) # DEBUG
#		if True: continue # DEBUG

		thickness = waterfall[2]
		sort_str = waterfall[3]
		theme = waterfall[4]
		if not theme in dictionary_waterfall:
			log.Must(f'WATERFALL TEMPLATE NOT FOUND - \'{theme}\'')
			continue

		# Modify water_line from template
		new_obj = copy.deepcopy( dictionary_waterfall[theme] )
		new_obj.set( "x", str(start_pos[0]*16) )
		new_obj.set( "y", str(start_pos[1]*16) )
#		tiled_utils.SetPolyPointsOnObject( new_obj, "0,0 " + end_pos ) # TBD, this causes reversed waterfall flow
		tiled_utils.SetPolyPointsOnObject( new_obj, end_pos + " 0,0" )
		tiled_utils.SetPropertyOnObject( new_obj, "thickness", str(thickness) )
		tiled_utils.SetPropertyOnObject( new_obj, "_sort", sort_str )
#		print( tiled_utils.GetPolyPointsFromObject(new_obj) ) # DEBUG

		# Add env_particles if exists
		particle_obj = None
		if theme in dictionary_particles:
			particle_obj = copy.deepcopy( dictionary_particles[theme] )
			end_pos_x = start_pos[0] - float(particle_obj.get('width'))/2 / 16
			end_pos_y = start_pos[1] + waterfall[1]
			particle_obj.set( "x", str(end_pos_x*16) )
			particle_obj.set( "y", str(end_pos_y*16) )

		# Add to level
		new_objectgroup.append( new_obj )
		if particle_obj != None:
			new_objectgroup.append( particle_obj )
		log.Extra(f'    - {theme} at ({start_pos[0]}, {start_pos[1]})')
		count_new += 1

	log.Info(f'Total of {count_new} waterfalls created')




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
			length_str = "0," + str(waterfall_len*16)	# TBD
			thickness = _GetWaterfallThickness(curr_id)
			log.Extra(f'    At ({start_x}, {start_y}), len = {length_str}, width = {thickness}')

			# Check if this waterfall can merge into any existing one
			#   this allows waterfall with thickness greater than 1
			# TODO 
			# TODO horizontal waterfall?

			# Append new waterfall to list
			list_waterfalls.append( ((start_x, start_y), length, thickness) )
#			list_waterfalls.append( ((start_x, start_y), length_str, thickness) )

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
'''Utility TODO'''

# TODO I'm planning to relocate this to tiled_utils,
# This way we don't have to import the "copy" module each time in our logic file
def _CopyXMLObject(obj):
	'''Deep-copy an XML objects, mostly for making new objects from a duplicated template'''
	return copy.deepcopy(obj)



# TBD... I tried packaging the process into its own function,
#  but it's getting annoying so I'll likely delete the entire function in the end
def _MakePolypoints( pos_beg, pos_end, is_reversed = False ):
	'''
	Converts coordinates (2 tuples of int), into polypoint (string)
	Inputs are in Tiled units, output are in pixel units.
	Inputs reset at 0,0
	  e.g. (4,2), (0, 8) => "0,0 -64,96"
	'''
	pos_beg_str = f'{str(pos_beg[0]*16)},{str(pos_beg[1]*16)}'
	pos_end_str = f'{str(pos_end[0]*16)},{str(pos_end[1]*16)}'
	if not is_reversed:
		polypoint_str = f'{pos_beg_str} {pos_end_str}'
	else:
		polypoint_str = f'{pos_end_str} {pos_beg_str}'

#	log.Extra( f'{pos_beg} & {pos_end} -> {polypoint_str}' )
	log.Extra(pos_beg)
	log.Extra(pos_end)
	log.Extra(polypoint_str)

	return polypoint_str





#--------------------------------------------------#










# End of File