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

def AddScroll(playdo, input_layer, output_layer, default_values):
	'''Main Logic'''
	log.Info("\nAdjusting tilelayer when added scrolling values...")

	# Fetch the input tilelayer
	tilelayer_obj = playdo.GetTilelayerObject(input_layer)
	if tilelayer_obj == None: return
	tiles2d = playdo.GetTiles2d(input_layer)
	tiles2d_new = tiled_utils.MakeTiles2D(tiles2d)
#	tiles2d_new = tiled_utils.CopyXMLObject(tiles2d)	# Technically not an object

	# Register the property values
	scroll_x, scroll_y, add_x, add_y = default_values
	scroll_x = ToNum( GetProperty( tilelayer_obj, 'scroll_x', scroll_x ) )
	scroll_y = ToNum( GetProperty( tilelayer_obj, 'scroll_y', scroll_y ) )
	add_x = ToNum( GetProperty( tilelayer_obj, 'add_x', add_x ) )
	add_y = ToNum( GetProperty( tilelayer_obj, 'add_y', add_y ) )

	# Create the list of properties to be added to output tilelayer
	list_properties = []
	list_properties.append( ('scroll_x', str(scroll_x)) )
	list_properties.append( ('scroll_y', str(scroll_y)) )
	list_properties.append( ('add_x', str(add_x)) )
	list_properties.append( ('add_y', str(add_y)) )
	if config_add_transparency:
		list_properties.append( ('color', DEFAULT_COLOR) )

	# Process tilelayer data (tiles2d)
	multiplier_x = 1 * ( 1 + scroll_x )
	multiplier_y = 1 * ( 1 + scroll_y )
	map_height = len(tiles2d)
	map_width  = len(tiles2d[0])
	for i in range(map_height):
		ref_y = int( i * multiplier_y )
		if ref_y >= map_height: continue
		for j in range(map_width):
			ref_x = int( j * multiplier_x )
			if ref_x >= map_width: continue
#			tiles2d_new[new_y][new_x] = 10
			tiles2d_new[i][j] = tiles2d[ref_y][ref_x]
#			tiles2d_new[i][j] = 10

	# Create the output tilelayer
	log.Info(f"  Creating output layer \'{output_layer}\'...")
	tiled_utils.AddTilelayer( playdo, output_layer, tiles2d_new, list_properties )

	log.Info(f"~~End of All Procedures~~\n")





#--------------------------------------------------#
'''Utility'''

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