'''A convenience module that helps to auto-generate the 7 other tile and object layers as if
   the object was rotated and flipped manually
'''
import logic.common.tiled_utils as tiled_utils
    
def CreatePermutationsOfPattern(playdo):
    print("-- pattern_permuter.py")
    
    # TODO: Validate the FILE to make sure it's in the correct format (there should only be one 
    _ValidatePattern(playdo)
    
    # Fetch the singular object_group and tiles2d from the file
    orig_tiles2d = _GetAnyTiles2d(playdo)
    orig_object_group = playdo.GetObjectGroup(None, discard_old = False)
    
    # Create 7 copies of the tile layer and object group
    tiles_2d_variants = _GenerateVariants(orig_tiles2d)
    new_pattern_names = ["1f", "2", "2f", "3", "3f", "4", "4f"]
    attrib_properties = [
        {'flip_x': ''},                         # 1f
        {'angle': '270'},                       # 2
        {'angle': '90', 'flip_x': ''},          # 2f
        {'angle': '180'},                       # 3
        {'angle': '180', 'flip_x': ''},         # 3f
        {'angle': '90'},                        # 4
        {'angle': '270', 'flip_x': ''},         # 4f
    ]
    
    for new_name, tiles_2d_var, obj_properties in zip(new_pattern_names, tiles_2d_variants, attrib_properties):
        encoded_data_str = tiled_utils.EncodeIntoZlibString64(tiles_2d_var)
        # TODO: Important to get the actual Tiled object ID? using '100' in the meanwhile
        playdo.AddNewTileLayer(new_name, encoded_data_str, '100')
        playdo.DuplicateObjectGroup(orig_object_group, new_name, obj_properties)
            

def _GetAnyTiles2d(playdo):
    '''Fetches the first tile layer. We do this since we expect there'd be just one tile layer'''
    all_tile_layer_names = playdo.GetAllTileLayerNames()
    tile_layer_name = all_tile_layer_names[0]
    return playdo.GetTiles2d(tile_layer_name)


def _GenerateVariants(tiles_2d):
    variants = []
    # first append a flipped version of the original tiles_2d
    variants.append(tiled_utils.FlipTiles2d(tiles_2d))
    # Next, Rotate 90, 180, 270 degrees. Append rotated and flipped-rotated variants
    rotated = tiles_2d
    for _ in range(3):
        rotated = tiled_utils.RotateTiles2d(rotated)
        variants.append(rotated)
        variants.append(tiled_utils.FlipTiles2d(rotated))

    return variants
    
def _ValidatePattern(playdo):
    ''' Check pattern file superficially to ensure they are properly formatted.
    
        Namely, this checks that there's just one tile layer and one object group.
    '''
    layers = playdo.level_root.findall('layer')
    objectgroups = playdo.level_root.findall('objectgroup')

    # 1. Check there's just 1 objectgroup and 1 layer
    if len(layers) != 1:
        raise Exception(f"Error in {playdo.full_file_name} detected! Number of tile layers must be 1!")

    if len(objectgroups) != 1:
        raise Exception(f"Error in {playdo.full_file_name} detected! Number of objectgroups must be 1!")
    
    # 2. Check objectgroup has at least one object
    for objectgroup in objectgroups:
        if len(objectgroup.findall('object')) == 0:
            raise Exception(f"Error in {playdo.full_file_name} detected! " + 
                f"Objectgroup '{objectgroup.get('name')}' does not contain any objects.")

    print("-- pattern_permuter.py : pattern format OK")