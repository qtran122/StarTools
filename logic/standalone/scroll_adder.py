'''
TBA


USAGE EXAMPLE:
	scroll_adder.AddScroll(playdo, input_layer, output_layer, default_values)
'''

import logic.common.log_utils as log
import logic.common.tiled_utils as tiled_utils

#--------------------------------------------------#
'''Variables'''

# Default values for the configurations
config_add_transparency = True
config_ = True

DEFAULT_COLOR = 'ffffff/0.7'




#--------------------------------------------------#
'''Public Functions'''

def AddScroll(playdo, input_prefix, output_layer, default_values):
	'''Main Logic'''
	log.Info("\nAdjusting tilelayer when added scrolling values...")

	# Detect the correct tilelayer to be processed
	list_all_layer_name = playdo.GetAllTileLayerNames()
	applicable_layer_name = None
	for name in list_all_layer_name:
		if not name.startswith( input_prefix ): continue
		applicable_layer_name = name
		break
	if applicable_layer_name == None: return
	log.Info(f"  Layer \"{applicable_layer_name}\" will be processed")

	# Fetch the input tilelayer
	tilelayer_obj = playdo.GetTilelayerObject(applicable_layer_name)
	tiles2d = playdo.GetTiles2d(applicable_layer_name)
	tiles2d_new = tiled_utils.MakeTiles2D(tiles2d)
#	tiles2d_new = tiled_utils.CopyXMLObject(tiles2d)	# Technically not an object
	map_height = len(tiles2d)
	map_width  = len(tiles2d[0])

	# Register the property values
	scroll_x, scroll_y, add_x, add_y = default_values
	scroll_x, scroll_y = ExtractScrollFromName( applicable_layer_name, input_prefix )
	log.Info(f"  Scroll Values: {scroll_x}, {scroll_y}")
	add_x = ToNum( GetProperty( tilelayer_obj, 'add_x', add_x ) )
	add_y = ToNum( GetProperty( tilelayer_obj, 'add_y', add_y ) )
	add_y -= map_height * scroll_y

	# Create the list of properties to be added to output tilelayer
	list_properties = []
	list_properties.append( ('scroll_x', str(scroll_x)) )
	list_properties.append( ('scroll_y', str(scroll_y)) )
	list_properties.append( ('add_x', str(add_x)) )
	list_properties.append( ('add_y', str(add_y)) )
	if config_add_transparency:
		list_properties.append( ('color', DEFAULT_COLOR) )

	# Process tilelayer data (tiles2d)
	multiplier_x = 1 / ( 1 - scroll_x )
	multiplier_y = 1 / ( 1 - scroll_y )
	for i in range(map_height):
		ref_y = int( i * multiplier_y )
		if ref_y >= map_height: continue
		for j in range(map_width):
			ref_x = int( j * multiplier_x )
			if ref_x >= map_width: continue
			tiles2d_new[i][j] = tiles2d[ref_y][ref_x]

	# Create the output tilelayer
	log.Info(f"  Creating output layer \'{output_layer}\'...")
	tiled_utils.AddTilelayer( playdo, output_layer, tiles2d_new, list_properties )

	log.Info(f"~~End of All Procedures~~\n")





#--------------------------------------------------#
'''Utility'''

def ExtractScrollFromName( layer_name, input_prefix ):
	'''
	(overrides default values)
	Return 2 float values from layer name string
	  e.g.
		_scroll          -> (  0,    0)
		_scroll_         -> (  0,    0)
		_scroll_0.1      -> (0.1,  0.1)
		_scroll_0.1_-0.2 -> (0.1, -0.2)
	'''

	# Remove unnecessary characters
	trimmed_str = layer_name.replace( input_prefix, "" )
	if len(trimmed_str) <= 0: return (0,0)
	if trimmed_str[0] == '_': trimmed_str = trimmed_str[1:]
	if len(trimmed_str) <= 0: return (0,0)

	# Extract values from the remaining string
	value_tuple = trimmed_str.split('_')
	value1, value2 = 0, 0
	if len(value_tuple) <= 1:
		value1 = float( value_tuple[0] )
		value2 = value1
	else:
		value1 = float( value_tuple[0] )
		value2 = float( value_tuple[1] )
	return ( value1, value2 )



def GetProperty(obj, prop_name, default_value = ''):
	'''Return the property value from an object, or the default value if there's none'''
	value = tiled_utils.GetPropertyFromObject( obj, prop_name )
	if value == '': value = default_value
	return value



def ToNum( value ):
	'''Convert property values to either int or float'''
	# Return int if decimal places not needed
	try:
		if float(value) == int(value): return int(value)
	except ValueError: None

	# Return float if is a number
	try:
		return float(value)
	except ValueError: None

	# Return string if cannot be converted
	return value_str





#--------------------------------------------------#










# End of File