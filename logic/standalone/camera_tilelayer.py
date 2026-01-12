'''
Logic module to create the tilelayer

USAGE EXAMPLE:
    main_logic.logic(playdo, passed_arguments)

'''
import time
import logic.common.log_utils as log
import logic.common.tiled_utils as tiled_utils

#--------------------------------------------------#
'''Variables'''





#--------------------------------------------------#
'''Main Function'''

def logic(playdo, frame_size, array_tile_id, layer_name):
    log.Extra("")
    log.Must(f"Creating new reference frame tilelayer : {frame_size[0]}x{frame_size[1]}")
    log.Extra("")
    start_time = time.time()

    # Create new layer
    log.Must(f" Creating Tiles2D...")
    new_tiles2d = playdo.GetBlankTiles2d()
    frame_thickness = len(array_tile_id)
    for i in range(len(array_tile_id)):
        _SetTiles2D(new_tiles2d, frame_size, (i, frame_thickness), array_tile_id[i]+1)
    log.Extra("")

    # Add the tilelayer and set its properties
    new_tilelayer = _AddTilelayerBelowMeta(playdo, layer_name, new_tiles2d)
    log.Extra("")

    # Adding property for the parallax effect
    _SetTilelayerAttributes(new_tilelayer, frame_size, frame_thickness)
    log.Extra("")

    log.Must(f"~~End of All Procedures~~ ({round( time.time()-start_time, 3 )}s)")
    log.Extra("")





#--------------------------------------------------#
'''Helper Functions'''

def _SetTiles2D(tiles2d, frame_size, thick_data, tile_id):
    log.Must(f"  Setting tiles \'{tile_id}\' at thickness {thick_data[0]+1}...")

    # Interpret data
    layer_w = frame_size[0]
    layer_h = frame_size[1]
    curr_thickness = thick_data[0]
    max_thickness  = thick_data[1]

    # Set range
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



def _SetTilelayerAttributes(new_tilelayer, frame_size, frame_thickness):
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