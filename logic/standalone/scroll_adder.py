'''
TBA


USAGE EXAMPLE:
    scroll_adder.AddScroll(playdo, input_layer, output_layer, default_values)
'''

import logic.common.log_utils as log
import logic.common.tiled_utils as tiled_utils

#--------------------------------------------------#
'''Variables'''

DEFAULT_COLOR = 'ffffff/1'    # In-Game View
DEFAULT_OPACITY = '0.4'        # In-Editor View

# TODO Eventually be setting these in the CLI instead
# Default values for the configurations
config_add_transparency = True
config_color = DEFAULT_COLOR
config_opacity = DEFAULT_OPACITY
config_backup_scroll2 = not True
config_ = True





#--------------------------------------------------#
'''Scroll 2 very scuffed code'''

def AddScroll2(playdo):
    '''Main Logic, for Scroll 2, also very rough'''
    log.Info("\nScanning all tilelayers to check if Scroll2 values need to be added...")
    count = 0

    # Get all tilelayer as objects, put into a single list
    list_all_tilelayer_object = []
    for layer_name in playdo.GetAllTileLayerNames():
        list_all_tilelayer_object.append( playdo.GetTilelayerObject(layer_name) )

    # Check if any layer need to add Scroll 2 values
    #   e.g. has only the old Scroll 1 values
    log.Info(f"  Scanning {len(list_all_tilelayer_object)} tilelayers...")
    for obj in list_all_tilelayer_object:
        properties = obj.find("properties")
        if properties == None: continue

        # Check if scroll2 is needed
        # Cannot use GetPropertyFromObject() because it never returns None
        has_scroll2 = False
        add_x, add_y, scroll_x, scroll_y = 0,0,0,0
        for property in properties:
            if property.get("name") == "scroll2":
                has_scroll2 = True
        if not has_scroll2: continue

        # Fetch old Scroll 1 values and process
        add_x = tiled_utils.GetPropertyFromObject(obj, "add_x")
        add_y = tiled_utils.GetPropertyFromObject(obj, "add_y")
        scroll_x = tiled_utils.GetPropertyFromObject(obj, "scroll_x")
        scroll_y = tiled_utils.GetPropertyFromObject(obj, "scroll_y")

        # Set the new Scroll 2 values to layer
        SetScroll2ToObject( obj, add_x, add_y, scroll_x, scroll_y )

    log.Info(f"~~End of All Procedures~~\n")
    return

# TODO relocate below
def SetScroll2ToObject( obj, add_x, add_y, scroll_x, scroll_y ):
    '''Input the old Scroll 2 values, add the new for Scroll 2 for in-editor view'''

    # Convert values into float, from either string or None (when no value is specified)
    add_x = ToNum2(add_x)
    add_y = ToNum2(add_y)
    scroll_x = ToNum2(scroll_x)
    scroll_y = ToNum2(scroll_y)
    layer_height = ToNum2(obj.get("height"))

    # Conversion formula
    factor_x = 1 - scroll_x
    factor_y = 1 - scroll_y
    offset_x = 16 * add_x
    offset_y = -16 * ( add_y + layer_height * scroll_y )

    # Set the Scroll2 values
    obj.set('parallaxx', str(factor_x) )
    obj.set('parallaxy', str(factor_y) )
    obj.set('offsetx', str(offset_x) )
    obj.set('offsety', str(offset_y) )

    # Set backup values
    #   When level is resized, Tiled may delete any existing Scroll 2 values
    #   Backing them up in Custom Property allow them to be easily restored later
    if not config_backup_scroll2: return
    tiled_utils.SetPropertyOnObject(obj, 'zbackup_parallaxx', str(factor_x))
    tiled_utils.SetPropertyOnObject(obj, 'zbackup_parallaxy', str(factor_y))
    tiled_utils.SetPropertyOnObject(obj, 'zbackup_offsetx', str(offset_x))
    tiled_utils.SetPropertyOnObject(obj, 'zbackup_offsety', str(offset_y))

# TODO relocate and rename, maybe merge with the other ToNum function?
def ToNum2(value):
#    print(value)
    if value == None: return 0
    return float(value)





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
#    tiles2d_new = tiled_utils.CopyXMLObject(tiles2d)    # Technically not an object
    map_height = len(tiles2d)
    map_width  = len(tiles2d[0])

    # Register the property values
    scroll_x, scroll_y, add_x, add_y = default_values
    scroll_x, scroll_y = ExtractScrollFromName( applicable_layer_name, input_prefix )
    log.Info(f"  Scroll Values: {scroll_x}, {scroll_y}")
#    add_x = ToNum( GetProperty( tilelayer_obj, 'add_x', add_x ) )
#    add_y = ToNum( GetProperty( tilelayer_obj, 'add_y', add_y ) )
    add_x = 0
    add_y = 0
    add_y -= map_height * scroll_y

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



    # Create the list of properties to be added to output tilelayer (in-game view)
    list_properties = []
    list_properties.append( ('add_x', str(add_x)) )
    list_properties.append( ('add_y', str(add_y)) )
    list_properties.append( ('scroll_x', str(scroll_x)) )
    list_properties.append( ('scroll_y', str(scroll_y)) )
    if config_add_transparency:
        list_properties.append( ('color', config_color) )

    # Create the list of info for the output tilelayer tile (in-editor view)
    list_info = []
    list_info.append( ('opacity', config_opacity) )
    list_info.append( ('offsetx', str(16 * add_x)) )
    list_info.append( ('offsety', str(16 * (add_y + map_height * scroll_y))) )
    # TODO check if 1-scroll_x is ok
    list_info.append( ('parallaxx', str(1/multiplier_x)) )
    list_info.append( ('parallaxy', str(1/multiplier_y)) )
    # Tiled automatically clean up the data if any of the value is same as default,
    #   e.g. offset == 0 or parallax == 1

    # Create the output tilelayer
    log.Info(f"  Creating output layer \'{output_layer}\'...")
    tiled_utils.AddTilelayer( playdo, output_layer, tiles2d_new, list_properties, list_info )

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