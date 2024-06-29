'''
Logic module that can create waterfall objects.


USAGE EXAMPLE:

'''

import logic.common.log_utils as log
import logic.common.tiled_utils as tiled_utils

#--------------------------------------------------#
'''Variables'''

FG_PREFIX = "fg"		# Prefix of fg tilelayers
BG_PREFIX = "bg"		# Prefix of bg tilelayers
BLOCKOUT_PREFIX = "_FALLS_"	# Prefix of tilelayers with waterfall blockout
OBJECTGROUP_PREFIX = "objects_waterfall_"

LAYER_SORT_DIFF = 10	# Difference of sort_value between consecutive tilelayers
LAYER_SORT_ADDON = 1	# Add to sort_value





#--------------------------------------------------#
'''Public Functions'''

def ScanForWaterFalls(playdo):
	'''
	For each applicable tilelayer:
	 - Check layer name for sort_value used
	 - Check layer name for template used
	  e.g. _FALLS_meadow => uses either the "meadow bg" or "meadow fg" template object
	 - Process the tile2D for waterfall coordinates

	Then return a list of tuples that contain all of the above informations
	  Each tuple represents a new waterfall object layer to be added
	'''

	''' =====[Pseudo-code]=====

	list_waterfall_layer = []

	Get all tilelayer objects
	Get all tilelayer names
	for tilelayer in list_all_tilelayer:
		# Check if current layer is a viable waterfall layer
		curr_layer_name = tiled_utils.GetNameFromObject ( tilelayer ) 
		if curr_layer_name doesn't start with BLOCKOUT_PREFIX : continue

		# Make the new sort_value string for property
		sort_value = _CountSortInLayer( curr_layer_name, list_all_layer_names )

		# Determines the template used, partly based on sort_value
		template_name = substitute( curr_layer_name, BLOCKOUT_PREFIX, "" )
		if sort_value starts with "fg" : template_name += " fg"
		else : template_name += " bg"

		# Process the tile2D and find the coordinates
		list_coordinates = _MakeListOfWaterfallCoordinates( get tile2D() )

		# Group all the info into a tuple, then append to the list
		list_waterfall_layer.append( (curr_layer_name, template_name, sort_value, list_coordinates) )

	return list_waterfall_layer
	'''

	return []



def CreateWaterfalls(waterfall_template, playdo, list_waterfall_layer):
	'''Read and convert each tuple in the list into a waterfalls object layer'''

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

def _CountSortInLayer( curr_layer_name, list_all_layer_names ):
	'''Return the sort_value if an object is to insert between layers
	e.g. Input - "arg" & ["bg_0", "bg_1", "arg", "bg_2", "fg_1"]
	     Output - "bg_tiles,15"
	'''

	''' =====[Pseudo-code]=====

	new_index = find index of curr_layer_name in list_all_layer_names

	sort_value = ""
	sort_num = new_index
	if list_all_layer_names[new_index-1] contains "fg":
		sort_value = "fg_tiles_"
		for( int i = 0; i < num_layer; ++i )
			if layer is bg : sort_num -= 1
			else break
	else:
		sort_value = "bg_tiles_"

	sort_value += sort_num * LAYER_SORT_DIFF + LAYER_SORT_ADDON
	return sort_value
	'''

	return ""



def _MakeListOfWaterfallCoordinates(tile2D):
	'''Process the tile2D, then find the coordinates and width of each waterfall'''

	# TODO

	return []






def _MakePolypoints( coordinates ):
	'''Converts [ (x1,y1), (x2,y2) ] into a polypoint string
	 e.g. [ (64,32), (0, 128) ] => "0,0 -64,96"
	'''

	# TODO

	return ""





# TODO relocate to tiled_utils?
def _CopyXMLObject(obj):
	'''Deep-copy an XML objects'''

	# TODO

	return obj





#--------------------------------------------------#










# End of File