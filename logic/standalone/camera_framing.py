'''
Logic module to create the reference tilelayer to simulate the range of in-game camera
The tilelayer has parallax factor adjusted, such that the "frame" stays in the center of the editor.

USAGE EXAMPLE:
    cam_logic.AddCameraFrameToLevel(playdo, size, FRAME_TILE_IDs, LAYER_NAME)

'''
import time
import logic.common.log_utils as log
import logic.common.tiled_utils as tiled_utils

#--------------------------------------------------#
'''Variables'''





#--------------------------------------------------#
'''Main Function'''

def AddCameraFrameToLevel(playdo, frame_size, FRAME_TILE_IDs, LAYER_NAME):
    '''
     This function creates the reference tilelayer to simulate the range of in-game camera
     The tilelayer has parallax factor adjusted, such that the "frame" stays in the center of the editor.

     :param playdo:         Processed level
     :param frame_size:     Integer tuple that states the size of the empty space inside frame
     :param FRAME_TILE_IDs: Integer array for Tile IDs, of which tiles the frame is using
     :param LAYER_NAME:     String of the output tilelayer
    '''

    log.Extra("")
    log.Must(f"Creating new reference frame tilelayer : {frame_size[0]}x{frame_size[1]}")
    log.Extra("")
    start_time = time.time()

    # Create new layer
    log.Must(f" Creating Tiles2D...")
    new_tiles2d = playdo.GetBlankTiles2d()
    frame_thickness = len(FRAME_TILE_IDs)
    for i in range(len(FRAME_TILE_IDs)):
        _CreateCameraFrame(new_tiles2d, frame_size, (i, frame_thickness), FRAME_TILE_IDs[i]+1)
    log.Extra("")

    # Add the tilelayer and set its properties
    new_tilelayer = _AddTilelayerBelowMeta(playdo, LAYER_NAME, new_tiles2d)
    log.Extra("")

    # Adding property for the parallax effect
    _SetTilelayerAttributesForFrame(new_tilelayer, frame_size, frame_thickness)
    log.Extra("")

    log.Must(f"~~End of All Procedures~~ ({round( time.time()-start_time, 3 )}s)")
    log.Extra("")





#--------------------------------------------------#
'''Helper Functions'''

def _CreateCameraFrame(tiles2d, frame_size, thick_data, tile_id):
    '''
     Sets the tile ID onto the Tiles2D in a rectangular outline
    
     :param tiles2d:    2D Array that stores the tileID used in each tile of the layer
     :param frame_size: Integer tuple, same as the input argument from CLI
     :param thick_data: Integer tuple, first is current number of the frame, second is the total number
     :param tile_id:    Integer, for the tile ID used in the current "onion layer" of the frame
    '''
    log.Must(f"  Setting tiles \'{tile_id}\' at thickness {thick_data[0]+1}...")

    # Interpret data
    layer_w = frame_size[0]
    layer_h = frame_size[1]
    curr_thickness = thick_data[0]
    max_thickness  = thick_data[1]

    # Calculate range
    x_beg = max_thickness - curr_thickness - 1
    y_beg = max_thickness - curr_thickness - 1
    x_end = x_beg + layer_w + curr_thickness * 2 + 1
    y_end = y_beg + layer_h + curr_thickness * 2 + 1
    log.Extra(f"    From ({x_beg},{y_beg}) to ({x_end},{y_end})")

    # Set tiles
    for i in range(y_beg, y_end):
        tiles2d[i][x_beg] = tile_id
        tiles2d[i][x_end] = tile_id
    for j in range(x_beg, x_end):
        tiles2d[y_beg][j] = tile_id
        tiles2d[y_end][j] = tile_id
    tiles2d[y_end][x_end] = tile_id



def _AddTilelayerBelowMeta(playdo, tile_layer_name, new_tiles2d):
    # Mostly copied from the playdo class
    log.Must(f" Adding tilelayer \'{tile_layer_name}\' to level...")

    # Check if the layer already exist in level    
    tile_layer_to_rewrite = None
    for layer in playdo.level_root.findall('layer'):
        if tile_layer_name != layer.get('name'): continue
        tile_layer_to_rewrite = layer
        break

    # Create a new layer if not
    #  1. Add the tilelayer to level
    #  2. Find the insert index of the "meta" objectgroup
    #  3. Remove and reinsert layer to relocate it to that index
    if tile_layer_to_rewrite is None:
        tile_layer_to_rewrite = playdo.AddNewTileLayer(tile_layer_name, "")
        insert_index = list(playdo.level_root).index( playdo.GetObjectGroup('meta', False) )
        playdo.level_root.remove(tile_layer_to_rewrite)
        playdo.level_root.insert(insert_index, tile_layer_to_rewrite)

    # Set tiles2D to the tilelayer
    tile_layer_to_rewrite.find('data').text = tiled_utils.EncodeIntoZlibString64(new_tiles2d)
    return tile_layer_to_rewrite



def _SetTilelayerAttributesForFrame(new_tilelayer, frame_size, frame_thickness):
    log.Must(f" Setting attributes...")

    # Parallax Factor
    new_tilelayer.set("parallaxx", "0")
    new_tilelayer.set("parallaxy", "0")

    # Offsets, in pixels
    frame_w = frame_size[0]
    frame_h = frame_size[1]
    x_offset = -( frame_w/2 + frame_thickness) * 16
    y_offset = -( frame_h/2 + frame_thickness) * 16
    new_tilelayer.set("offsetx", str(x_offset))
    new_tilelayer.set("offsety", str(y_offset))





#--------------------------------------------------#










# End of File