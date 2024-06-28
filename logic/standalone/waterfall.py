'''
Logic module that can create waterfall objects.


USAGE EXAMPLE:

'''

import logic.common.log_utils as log
import logic.common.tiled_utils as tiled_utils

#--------------------------------------------------#
'''Variables'''

TILELAYER_PREFIX = "_falls"

DEFAULT_SORT_FG = "fg_tiles,15"
DEFAULT_SORT_BG = "bg_tiles,5"
DEFAULT_SORT = DEFAULT_SORT_BG

DEFAULT_COLOR = "ffffff"

OBJECTGROUP_PREFIX = "objects_waterfall_"



#--------------------------------------------------#
'''Public Functions'''

def GetMetaDataFromBlockout(playdo):
	'''Obtain the tile2d and various meta data for the waterfall, based on tilelayer name
	  e.g. _falls => sort_value is DEFAULT_SORT, color is DEFAULT_COLOR
	       _falls_fg15 => sort_value is "fg_tiles,15", color is DEFAULT_COLOR
	       _falls_bg_bbccff => sort_value is DEFAULT_SORT_BG, color is "#bbccff/1f"
	'''

	''' =====[Pseudo-code]=====
	list_meta_data = []
	Get all tilelayer name
	for tilelayer in list_all_tilelayer:
		layer_name = tiled_utils.GetName ( tilelayer ) 
		if layer_name doesn't start with TILELAYER_PREFIX : continue

		layer_tuple = layer_name.split("_")
		sort_value = _ProcessSort( layer_tuple[1] )
		color_value = _ProcessColor( layer_tuple[2] )

		list_meta_data.append( tilelayer.GetTile2D(), sort_value, color_value )

	return list_meta_data
	'''

	return []


def ScanForWaterFalls(list_meta_data):
	'''...'''

	''' =====[Pseudo-code]=====

	list_waterfall_layer = []
	for tuple in list_meta_data:
		tile2d = tuple[0]
		list_of_waterfall = _MakeListOfWaterfallCoordinates( tile2d )
		list_waterfall_layer.append( list_of_waterfall )
	return list_waterfall_layer
	'''

	return None


def CreateWaterfalls(playdo, list_meta_data, list_waterfall_layer):
	'''...'''

	''' =====[Pseudo-code]=====

	for( int i = 0; i < list_meta_data.Length ; ++i )
		curr_meta_data = list_meta_data[i]
		curr_waterfall_layer = list_waterfall_layer[i]

		object_layer_name = OBJECTGROUP_PREFIX + curr_meta_data[1]
		new_object_layer = make_layer(object_layer_name)

		waterfall_color = curr_meta_data[2]

		for coordinates in curr_waterfall_layer:
			new_object = _MakeWaterfallXMLObject( coordinates, waterfall_color )
			new_object_layer.add_object( new_object )
	'''





#--------------------------------------------------#
'''Utility Functions'''


'''	TODO

def _ProcessSort

def _ProcessColor

def _MakeListOfWaterfallCoordinates

def _MakeWaterfallXMLObject



'''






#--------------------------------------------------#










# End of File