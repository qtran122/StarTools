'''
Standalone module for swapping 2 layers of a LEVEL XML by using a 3rd layer as input

SETUP EXAMPLE:
    Level XML should have 3 tile layers that appear like below.
    Note, the layer names determine which layers will be operated on.
    - fg_ground                     # This is a tile layer to be swapped
    - fg mesh                       # This is the other tile layer to be swapped
    - SWAP # fg mesh # fg_ground    # this is the 3rd layer - it specifies the layers to swap

USAGE EXAMPLE:
    playdo = level_playdo.LevelPlayDo("j24.xml")
    result = swapper.Swap(playdo)
    if result: playdo.Write()
'''

import logic.common.log_utils as log

def Swap(level_playdo):
    # The main function to use to swap chunks of two tile layers(assuming level is setup correctly)
    
    # Retrieve the swap input name
    tile_layer_names = level_playdo.GetAllTileLayerNames()
    swap_layer_name = _GetSwapTileLayerName(tile_layer_names)
    if swap_layer_name is None: return False
        
    # Unpack and Extract the names of the swap layers and all of the needed tiles2d data
    extract_result, tiles2d_swap, layer_name_A, tiles2d_A, layer_name_B, tiles2d_B = (
        _ExtractData(level_playdo, swap_layer_name))
    if not extract_result : return False

    # Perform the actual swap on the two tiles2d's
    _SwapTiles2dData(tiles2d_swap, tiles2d_A, tiles2d_B)
    
    # Commit the tile2d changes into the Level Playdo
    level_playdo.SetTiles2d(layer_name_A, tiles2d_A)
    level_playdo.SetTiles2d(layer_name_B, tiles2d_B)
    
    return True # Return true for success



def _SwapTiles2dData(tiles2d_swap, tiles2d_A, tiles2d_B):
    # Swaps the tile IDs of tiles2d_A & tiles2d_B given found entries in tiles2d_swap
    map_height = len(tiles2d_A)
    map_width  = len(tiles2d_A[0])
    
    log.Info(f"-- tile_swapper.py : detected map height {map_height}")
    log.Info(f"-- tile_swapper.py : detected map width {map_width}")
    
    num_tiles_swapped = 0
    for i in range(map_height):
        for j in range(map_width):
            if tiles2d_swap[i][j] != 0:
                temp_val = tiles2d_A[i][j]
                tiles2d_A[i][j] = tiles2d_B[i][j]
                tiles2d_B[i][j] = temp_val
                num_tiles_swapped += 1
    
    print(f"-- tile_swapper.py : swapped {num_tiles_swapped} tiles!")



def _ExtractData(level_playdo, swap_layer_name):
    # Extract the names of the tile layers to be swapped
    split_names = swap_layer_name.split("#")
    layer_name_A = split_names[1].strip()
    layer_name_B = split_names[2].strip()
    
    # Retrieve the tiles2D data for the three layers
    tiles2d_swap = level_playdo.GetTiles2d(swap_layer_name)
    tiles2d_A = level_playdo.GetTiles2d(layer_name_A)
    tiles2d_B = level_playdo.GetTiles2d(layer_name_B)
    
    # Confirm successful retrieval of tiles2d data for the two layers to be swapped
    extraction_result = True
    if tiles2d_A is None:
        log.Must(f"-- tile_swapper.py : specified a tile layer '{layer_name_A}' that does not exist!")
        extraction_result = False
    if tiles2d_B is None:
        log.Must(f"-- tile_swapper.py : specified a tile layer '{layer_name_B}' that does not exist!")
        extraction_result = False
    
    return (extraction_result, tiles2d_swap, layer_name_A, tiles2d_A, layer_name_B, tiles2d_B)


def _GetSwapTileLayerName(tile_layer_names):
    '''Given a list of tile layer names, returns the name of the swap layer. Returns NONE on error'''
    swap_layers = []
    for layer_name in tile_layer_names:
        log.Extra(f"-- tile_swapper.py : found tile layer name : {layer_name}")
        if layer_name.lower().startswith("swap"):
            swap_layers.append(layer_name)
    
    # There must be 1 and only 1 swap layer. If multiple are found, inform of the error
    if len(swap_layers) == 0:
        log.Must("-- tile_swapper.py : SWAP layer not found! The level XML must contain a tile layer that "
            + "is named 'SWAP # X # Y' where X and Y are the names of two other tile layers to be swapped.")
        return None
    elif len(swap_layers) > 1:
        log.Must("-- tile_swapper.py : Multiple SWAP layers were found! The level XML must contain only 1 swap layer.")
        log.Must("-- tile_swapper.py : SWAP layers detected: " + ', '.join(swap_layers))
        return None
    else:
        log.Info(f"-- tile_swapper.py : found swap layer : {swap_layers[0]}")
        return swap_layers[0]