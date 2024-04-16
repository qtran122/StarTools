'''
Module for searching tile IDs in a level

This is useful for when we need references and would like to know where a tile
has been used. Also good for when we suspect a tile ID has become obsoleted and
would like to confirm that no other levels are using it.

USAGE EXAMPLE:
    import logic.finder.tile_finder as tile_finder
    
    file_name = "j24.xml"
    tile_id = 657
    tile_finder.SearchFile(file_name, tile_id)
'''

import logic.common.file_utils as file_utils
import logic.common.level_playdo as play
import logic.common.log_utils as log

def SearchFileForTileIds(filename, tiles_to_search):
    '''Searches a File for select TILE IDs
      
    filename - the name of the file we want to search
    tiles_to_search - list of tile IDs we want to search. Usually this is a list of 8 tile IDs where
        the 1st entry is the tile ID & the other 7 are its permutations after flipping & rotations
    
    Returns a dictionary mapping tile_layer_name to a list of coordinates where matches were found.
    Returns an empty dictionary if no matches were found.
    Returns None if a file erred out and could not be searched
    '''
    try:
        playdo = play.LevelPlayDo(filename)
        tiles2d_map, tiles2d_hash = playdo.PreCalculateInternalTileData()
    except Exception as e:
        return None
        
    layers_containing_target = []
    search_results = {} # dict of 'layer_name' to list of coordinate tuples
    for tile_layer_name in tiles2d_hash.keys():
        playdo.GetTiles2d(tile_layer_name)
        tiles_hash = playdo.GetTilesHashSet(tile_layer_name)
        for tile_id in tiles_to_search:
            if tile_id in tiles_hash:
                _RefineSearchResult(tile_id, tile_layer_name, tiles2d_map, search_results)
                layers_containing_target.append(tile_layer_name)

    return search_results

def _RefineSearchResult(search_tile_id, tile_layer_name, tiles2d_map, search_result):
    '''
    Refines a search result so we can attach the location of a match to the layer it was 
    found. We use this when we have a hit in the tiles hash cache, and want to refine 
    the result to indicate where in the tiles specifically a tile was used.
      
    search_tile_id - the tile id we are searching
    tile_layer_name - the layer name we know it to exist in
    tiles2d_map - map of tile_layer_name to tiles2d data - obtained from playdo
    search_result - dictionary of tile_layer_name to a list of coordinates. _RefineSearchResult
        doesn't return a value, but it will update this search_result structure
    '''
    containing_tiles2d = tiles2d_map[tile_layer_name]
    
    if tile_layer_name not in search_result:
        search_result[tile_layer_name] = []
        
    for row, tile_row in enumerate(containing_tiles2d):
        for col, tile_id in enumerate(tile_row):
            if search_tile_id == tile_id:
                if tile_layer_name in search_result:
                    search_result[tile_layer_name].append((col, row))
                    
def FormatSearchResult(search_results):
    '''Formats the search_result returned from SearchFile() into a pretty printable string'''    
    master_string = ""
    for layername, coords in search_results.items():
        # Adjust the layer name to 16 characters
        layer_string = None
        if len(layername) <= 16: layer_string = f"        {layername.ljust(16)}:"
        else: layer_string = f"      {layername[:14]}..:"
        
        # Add the coordinates with a space inbetween
        for coord in coords:
            layer_string += f" {coord} "
        
        # Crop length of the coordinates to keep to one line in case it's too long
        if len(layer_string) > 100:
            layer_string = layer_string[:97] + "..."
        
        # Add a newline to delineate different tile layers
        master_string += (layer_string + "\n")
    return master_string

