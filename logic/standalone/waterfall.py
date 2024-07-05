'''
Logic module that can create waterfall objects.


USAGE EXAMPLE:

'''

import logic.common.log_utils as log
import logic.common.tiled_utils as tiled_utils

#--------------------------------------------------#
'''Variables'''

# Template settings
OBJECT_SUFFIX_FG = " fg"
OBJECT_SUFFIX_BG = " bg"


# Session settings
LAYER_SORT_DIFF = 10	# Difference of sort_value between consecutive tilelayers
LAYER_SORT_ADDON = 1	# Add to sort_value
BLOCKOUT_PREFIX = "_FALLS_"	# Prefix of tilelayers with waterfall blockout
OBJECTGROUP_PREFIX = "objects_waterfall_"



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
	log.Extra("")
	log.Info("︽ Scanning for waterfalls ︽")
	log.Extra("")

	list_all_waterfalls = []
	curr_sort_str = "bg_tiles,"
	curr_sort_num = LAYER_SORT_ADDON - LAYER_SORT_DIFF

	for tilelayer_name in list_all_tilelayer_name:
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
		if curr_sort_str.startswith("bg"): theme += OBJECT_SUFFIX_BG
		else : theme += OBJECT_SUFFIX_FG
		log.Info(f'  Creating \"{theme}\" waterfalls at \"{full_sort_str}\"')


		# Process the tile2D to find the coordinates, then add to the full list
		list_curr_waterfalls = _MakeListOfWaterfallCoordinates( playdo.GetTiles2d(tilelayer_name, True) )
		for waterfall in list_curr_waterfalls:
			list_all_waterfalls.append( (
				waterfall[0],
				waterfall[1],
				full_sort_str,
				theme
			) )

	# Debug, to be deleted
	log.Extra("\n  Printing waterfalls")
	for waterfall in list_all_waterfalls:
		for tuple_value in waterfall: log.Extra("    " + str(tuple_value))
		log.Extra("")
 
	log.Info(f'︾ Total of {len(list_all_waterfalls)} waterfalls scanned ︾')
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
'''Utility Functions'''

def _MakeListOfWaterfallCoordinates(tile2D):
	'''Process the tile2D, then find the coordinates and width of each waterfall'''

	list_waterfalls = []

	# TODO
	list_waterfalls.append( ((1,2),(3,4)) )
	list_waterfalls.append( ((5,6),(7,8)) )

	return list_waterfalls






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