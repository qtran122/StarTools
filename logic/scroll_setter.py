'''
Logic module for scroll tool:
 - Output a layer after applying scroll2
 - Output a layer with scrolling border
 - Set the "scroll2" property to output layers
 - Print in log the expected map size

USAGE EXAMPLE:
	main_logic.logic(playdo)
	raw_dict = conflict.CheckConflicts(playdo, _LIST_LIGHTING_OBJ)
	pruned_dict = conflict.PruneConflicts(playdo, conflict_dictionary)
	conflict.FixConflicts(playdo, pruned_dict)
'''

import logic.common.log_utils as log
import logic.common.tiled_utils as tiled_utils

#-------------------------------------------------------#
# -------------------- [Variables] -------------------- #

output_layer_name = "_fg_parallax"  # If you add a / in the name, the app just crashes
property_name = "scroll2"

# Layer name, the first number is the in-editor parallax values
# Having a second number means x- & y-values are different
#  "_scroll 1.05"   -> (1.05, 1.05)
#  "_scroll 1 1.05" -> (1   , 1.05)
layer_prefix = "_scroll"
split_char = " "

# The tilelayer for highlighting the border needed when setting parallax
border_marker_name = "_parallax marker"    # Layer name
border_tile_id_r   = 1039+1
border_tile_id_g   = 1037+1

# Layers automatically generated
auto_layer_names = [
	"raw_ BIOME _parallax",  # Input layer name of auto-tiling
	"_fg_parallax BIOME",    # Output layer name of auto-tiling
	border_marker_name,
]
opacity_value = "0.5"



#--------------------------------------------------------------#
# -------------------- [Public Functions] -------------------- #

def logic(playdo, scroll_x, scroll_y, make_auto_layers):
	'''TODO'''
	log.Extra('')
	log.Must(f'Creating modified layer based on the reference scroll layer...')
	log.Extra('')

	# Check which layer is being referenced, as well as the scroll values specified in layer name
	ref_name, scroll_x, scroll_y = GetLayerNameAndScroll(playdo, scroll_x, scroll_y)
	if ref_name == False: return

	# Prints in log, doesn't modify any layer
	CheckMapSize(playdo, ref_name, scroll_x, scroll_y)

	# Creates a new layer based on reference layers and the scroll values
	mult_x = ModifyScrollLayer(playdo, ref_name, scroll_x, scroll_y)

	# Create border layer - 3 tiles red that shouldn't be visible, 1 green that should be half-visible
	if mult_x < 1:
		SetBorderLayer(playdo, 4, border_tile_id_g)
		SetBorderLayer(playdo, 3, border_tile_id_r)

	# Create a blank layer, then set the scrolling properties
	log.Must('  Setting properties...')
	AddParallaxToLayer(playdo, output_layer_name, scroll_x, scroll_y, True)
	if make_auto_layers:
		for auto_name in auto_layer_names: AddParallaxToLayer(playdo, auto_name, scroll_x, scroll_y, False, True)
	log.Extra('')





#-------------------------------------------------------#
# -------------------- [Recognize] -------------------- #

def GetLayerNameAndScroll(playdo, scroll_x, scroll_y):
	'''
	 Returns a tuple value for the recognized scroll values
	  - Layer name, to be fetched the tiles2d more conveniently
	  - Scroll value in x-axis
	  - Scroll value in y-axis
	'''
	ERROR_VALUE = False, False, False

	# Check which layer is being referenced
	list_names = playdo.GetAllTileLayerNames()
	ref_name = None
	for name in list_names:
		if not name.startswith(layer_prefix): continue
		ref_name = name
		break
	if ref_name == None:
		log.Must( "  ERROR! Reference layer not found!")
		log.Must(f"    Make sure to have a layer starting with \"{layer_prefix}\", then specify scroll values")
		log.Must( "    Example: \"_scroll 1.05\" \"_scroll 1 1.05\"")
		return ERROR_VALUE

	# Skip name-checking if scroll values are overridden
	if not (scroll_x == "1" and scroll_y == "1"): return ref_name, scroll_x, scroll_y

	# Get scroll values
	temp = ref_name.replace(layer_prefix, "").split(split_char)
	if temp == ['']:
		log.Must( "  ERROR! Reference layer is not in correct name format!")
		log.Must(f"    Make sure to have a number specifying scroll values")
		log.Must( "    Example: \"_scroll 1.05\" \"_scroll 1 1.05\"")
		return ERROR_VALUE
	temp.pop(0)  # First element is always '' somehow
	scroll_x = temp[0]
	if len(temp) >= 2: scroll_y = temp[1]
	else:              scroll_y = scroll_x
	log.Must(f'  Referenced layer is \"{ref_name}\", with parallax values X = {scroll_x}, Y = {scroll_y}...')
	log.Extra('')

	return ref_name, scroll_x, scroll_y



def CheckMapSize(playdo, ref_name, scroll_x, scroll_y):
	'''
	 No practical effect.
	 Prints out in log, of how big the level should be based on the pre-scroll sizes and scroll values
	 Also checks whether the current level is big enough. 
	'''
	ref_tiles2d = playdo.GetTiles2d(ref_name)
	level_w = playdo.map_width
	level_h = playdo.map_height
	log.Info(f"  Map Size W x H    : {level_w} x {level_h}")

	layer_w = -1
	layer_h = -1
	for i in range(level_w):
		if ref_tiles2d[0][i] != 0: continue
		layer_w = i
		break
	for i in range(level_h):
		if ref_tiles2d[i][0] != 0: continue
		layer_h = i
		break
	if layer_w == -1: layer_w = level_w
	if layer_h == -1: layer_h = level_h
	log.Info(f"    Tilelayer Size  : {layer_w} x {layer_h}")

	# Estimate new width & height
	mult_x = 1 / float(scroll_x)
	mult_y = 1 / float(scroll_y)
	new_w = int(layer_w / mult_x)
	new_h = int(layer_h / mult_y)
	is_level_big_enough = (new_w <= level_w) and (new_h <= level_h)
	log.Info(f"    Map Requirement : {new_w} x {new_h}")
	log.Info(f"      Is level big enough? {is_level_big_enough}")
	log.Extra('')



#-----------------------------------------------------------#
# -------------------- [Tiles2D Edits] -------------------- #

def ModifyScrollLayer(playdo, ref_name, scroll_x, scroll_y):
	'''
	 Edit the layer with scroll values
	'''
	# Checking the size of the room and tilelayer, for logging purpose only
	level_w = playdo.map_width
	level_h = playdo.map_height

	# Set tile ID based on how much it's scrolling / stretching
	log.Must('  Setting tile ID...')
	mult_x = 1 / float(scroll_x)
	mult_y = 1 / float(scroll_y)
	ref_tiles2d = playdo.GetTiles2d(ref_name)
	new_tiles2d = playdo.GetBlankTiles2d()
	for x in range(level_w):
		ref_x = int(x * mult_x)	+ 1
		if ref_x <  0:       continue
		if ref_x >= level_w: break
		for y in range(level_h):
			ref_y = int(y * mult_y) + 1
			if ref_y <  0:       continue
			if ref_y >= level_h: break
			new_tiles2d[y][x] = ref_tiles2d[ref_y][ref_x]
	playdo.SetTiles2d(output_layer_name, new_tiles2d)
	log.Extra('')
	return mult_x



#--------------------------------------------------------#
# -------------------- [Attributes] -------------------- #

def AddParallaxToLayer(playdo, layer_name, scroll_x, scroll_y, set_properties = False, set_opacity = False):
	'''This only adds the attributes to the layer, without affecting the Tiles2d itself'''
	new_layer = playdo.GetTilelayer(layer_name, False)
	new_layer.set("parallaxx", scroll_x)
	new_layer.set("parallaxy", scroll_y)
#	new_layer.set("offsetx", "-8") # Always shift layer by a certain amount?
#	new_layer.set("offsety", "-8")
	if set_properties: tiled_utils.SetPropertyOnObject(new_layer, "scroll2", "")
	if set_opacity:    new_layer.set("opacity", opacity_value)

	msg = f'    \"{layer_name}\"'
	if set_properties: msg += f' \t(with \"{property_name}\" property)'
	log.Info(msg)

	return new_layer



#----------------------------------------------------#
# -------------------- [Border] -------------------- #

def SetBorderLayer(playdo, thickness, tile_id):
	'''
	 Set tiles ID around the border of the level of a specific layer
	 If a layer is absent, new layer would be created.
	'''
	log.Must('  Setting border layer...')
	level_w = playdo.map_width
	level_h = playdo.map_height
	new_tiles2d = playdo.GetTiles2d(border_marker_name)
	if new_tiles2d == None: new_tiles2d = playdo.GetBlankTiles2d()

	min_x = thickness-1
	max_x = level_w - thickness
	min_y = thickness-1
	max_y = level_h - thickness

	for x in range(level_w):
		for y in range(level_h):
			if (min_x < x and x < max_x) and (min_y < y and y < max_y): continue
			new_tiles2d[y][x] = tile_id
	playdo.SetTiles2d(border_marker_name, new_tiles2d)
	log.Extra('')



#------------------------------------------------------#
# -------------------- [Template] -------------------- #










# End of File