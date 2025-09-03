'''
Logic module for creating waterfall objects.
Required input: Template XML, Level XML with valid tilelayer name & tiles

USAGE EXAMPLE:
    list_waterfall = waterfall.ScanForWaterFalls(playdo)
    waterfall.CreateWaterfalls(playdo_template, playdo, list_waterfall)
'''

import copy # TBD
import logic.common.log_utils as log
import logic.common.tiled_utils as tiled_utils

#--------------------------------------------------#
'''Variables'''

# Template settings
LIST_WATERFALL_TILE_ID = [2560, 2561, 2562, 2563]



# Session settings
LAYER_SORT_DIFF = 10    # Difference of sort_value between consecutive tilelayers
LAYER_SORT_ADDON = 5    # Difference of sort_value between waterfalls and tilelayers
BLOCKOUT_PREFIX = "_FALLS_"    # Prefix of tilelayers with waterfall blockout, followed by theme
NEW_OBJECT_LAYER_NAME = "objects_waterfall_auto"





#--------------------------------------------------#
'''Public Functions'''

def ScanForWaterFalls(playdo):
    '''
    Returns a list of tuples, where each tuple contains the data needed to create a waterfall.
    Each tuple contains the following data: (start_position, end_position, sort_layer, theme)
     - start_position - a tuple of x,y coordinates signifying where the waterfall starts
     - length - the number of tiles between starting and ending positions
     - thickness - the thickness of waterfalls based on tile id
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
        end_pos = (start_pos[0], start_pos[1] + waterfall[1])

        thickness = waterfall[2]
        sort_str = waterfall[3]
        theme = waterfall[4]
        if not theme in dictionary_waterfall:
            log.Must(f'WATERFALL TEMPLATE NOT FOUND - \'{theme}\'')
            continue
        log.Extra(f'    - {theme} at ({start_pos[0]}, {start_pos[1]})')
        polypoint_str = MakePolypoints( (start_pos, end_pos), True, start_pos )

        # Modify water_line from template
        new_obj = CopyXMLObject( dictionary_waterfall[theme] )
        new_obj.set( "x", str(start_pos[0]*16) )
        new_obj.set( "y", str(start_pos[1]*16) )
        tiled_utils.SetPolyPointsOnObject( new_obj, polypoint_str )
        tiled_utils.SetPropertyOnObject( new_obj, "thickness", str(thickness) )
        tiled_utils.SetPropertyOnObject( new_obj, "_sort", sort_str )

        # Add env_particles if exists
        particle_obj = None
        if theme in dictionary_particles:
            particle_obj = CopyXMLObject( dictionary_particles[theme] )
            end_pos_x = start_pos[0] - float(particle_obj.get('width'))/2 / 16
            end_pos_y = start_pos[1] + waterfall[1]
            particle_obj.set( "x", str(end_pos_x*16) )
            particle_obj.set( "y", str(end_pos_y*16) )

        # Add to level
        new_objectgroup.append( new_obj )
        if particle_obj != None:
            new_objectgroup.append( particle_obj )
        count_new += 1

    log.Info(f'Total of {count_new} waterfalls created')




#--------------------------------------------------#
'''Utility for Scanning'''

def _MakeListOfWaterfallCoordinates(tiles2d):
    '''
        Process the tile2D, then find the coordinates and thickness of each waterfall
        This assumes all waterfalls are vertical, i.e. no horizontal or diagonal waterfall
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
            curr_or = tiles2d[i][j] >> 29
            curr_id = tiles2d[i][j] - (curr_or << 29) - 1
            if not curr_id in LIST_WATERFALL_TILE_ID: continue

            # Check all connected tile
            waterfall_len = 1
            for i2 in range(map_height):    # TODO find better way to iterate?
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

            # TODO Check if this waterfall can merge into any existing one
            #   this allows waterfall with thickness greater than 1
            # TODO horizontal waterfall?

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
'''Utility To Be Relocated'''
# The functions are kept here for now for easily code-inspection
# TODO Both functions will be moved to tiled_utils once they are finalised



# Moving this to tiled_utils allow us to not import the "copy" module every time in our logic file
def CopyXMLObject(obj):
    '''Deep-copy an XML objects, mostly for making new objects from a duplicated template'''
    return copy.deepcopy(obj)



# Planned to be used for collision polygons as well
def MakePolypoints( list_pos, is_reversed = False, polygon_xy = (0,0) ):
    '''
    Converts coordinates (list of tuples of 2 int), into polypoint (string)
    Inputs are in Tiled units, output are in pixel units.
      e.g. (4,2), (0, 8) => "64,32 0,128"
    If is_reversed, the order of vertices is reversed
    By default, output Polygon is assumed to be at x = 0 and y = 0
      Set polygon_xy = list_pos[0] for output string to start with 0,0
    '''

    polypoint_str = ''
    for i,pos in enumerate(list_pos):
        # Choose the current vertex
        curr_pos = pos
        if is_reversed: curr_pos = list_pos[len(list_pos)-1 - i]

        # Add vertex's position to string
        pos_x = curr_pos[0] - polygon_xy[0]
        pos_y = curr_pos[1] - polygon_xy[1]

        # Convert to Tiled unit, rounded to nearest int, i.e. pixel unit
        pos_x = int(pos_x * 16)
        pos_y = int(pos_y * 16)
        polypoint_str += f'{str(pos_x)},{str(pos_y)} '

    # Trim last character in string
    polypoint_str = polypoint_str[:-1]

    log.Extra(f'      - {list_pos} -> \"{polypoint_str}\"')
    return polypoint_str





#--------------------------------------------------#










# End of File