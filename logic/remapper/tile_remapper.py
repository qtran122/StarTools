'''A convenience module for reskinning levels'''
import copy
import xml.etree.ElementTree as ET
import logic.common.tiled_utils as tiled_utils
import logic.common.image_utils as image_utils
import logic.common.file_utils as file_utils
import toml


class TileRemapper():
    '''The convenience class to aid performing remap operations upon a TILED level XML file'''
    def __init__(self):
        self.A_to_B_map = {} # maps tile ID to another tile ID
        self.B_to_A_map = {} # maps tile ID to another tile ID (reversed direction)
        
        
    def LoadRemapXml(self, pattern_file_path):
        '''Load a 'Remap' XML file. These are files that contain only 2 graphical tile layers. Also, these
        remap XML files MUST reside in the tools "input\remaps" folder
        '''
        # Extract XML root and validate pattern has correct format (2 tile layers, no object groups)
        tree = ET.parse(pattern_file_path)
        root = tree.getroot()
        map_width = int(root.get('width'))        
        self._ValidateRemapXml(root, pattern_file_path)
        
        # Get tilemaps of both layers
        layer_A, layer_B = root.findall('layer')
        data_A = layer_A.find('data').text.strip()
        data_B = layer_B.find('data').text.strip()
        tile_2d_map_A = tiled_utils.DecodeIntoTiles2d(data_A, map_width)
        tile_2d_map_B = tiled_utils.DecodeIntoTiles2d(data_B, map_width)
        
        # Populate the remapping dictionaries
        rows = len(tile_2d_map_A)
        cols = len(tile_2d_map_A[0])
        for i in range(rows):
            for j in range(cols):
                tile_id_A = tile_2d_map_A[i][j]
                tile_id_B = tile_2d_map_B[i][j]
                self.A_to_B_map[tile_id_A] = tile_id_B
                self.B_to_A_map[tile_id_B] = tile_id_A
                
        _ExpandMapBindings(self.A_to_B_map)
        _ExpandMapBindings(self.B_to_A_map)
    
    
    def LoadMigrationMap(self, old_tiles_png_path, new_tiles_png_path):
        """Creates a massive mapping of old tile IDs to new tile IDs based on image matching."""
        old_tiles_np_array = image_utils.SliceTileSheetIntoNpArray(old_tiles_png_path)
        new_tiles_np_array = image_utils.SliceTileSheetIntoNpArray(new_tiles_png_path)
        
        # Hash all new tiles and store them in a dictionary {hash_bytes : tile_id}
        new_tiles_hashmap = {tile.tobytes() : tile_id for tile_id, tile in enumerate(new_tiles_np_array, start=1)}
        
        rebind_map = {} # the final mapping authority - this is a massive mapping of old tile_id to new tile_id
        unmatched_tiles = [] # list of (tile_id, image) tuples. Stores entries that found no match in new tilesheet
        override_bindings = _ReadMigrationOverrideFile() # Map of tile_id to tile_id mappings that were entered manually
        # override_bindings will generally be used to cover cases where unmatched tiles were found
        
        for old_id, old_tile in enumerate(old_tiles_np_array, start=1):
            old_tile_hash = old_tile.tobytes()
            if old_tile_hash in new_tiles_hashmap:
                rebind_map[old_id] = new_tiles_hashmap[old_tile_hash]
            elif old_id not in override_bindings:
                # A tile is considered mismatched if it is not found in the new tiles PNG 
                # and a backup override entry was not found in the override file
                unmatched_tiles.append((old_id, image_utils.NpArrayToImage(old_tile)))
        
        # If unmatched tiles were found, inform user by generating an image for inspection
        if unmatched_tiles:
            image_title = "- TILES MIGRATION : MISMATCHES -"
            unmatched_png_path = file_utils.GetOutputFolder() + 'migration_mismatches.png'
            image_utils.CreateTilesCollage(image_title, unmatched_tiles, unmatched_png_path)
        
        # If there is an override_bindings file, generate an image of said bindings to aid user
        if override_bindings:
            image_title = "- TILES MIGRATION : BINDING OVERRIDES -"
            override_png_path = file_utils.GetOutputFolder() + 'migration_bindings.png'
            imagesA = [(t_id, image_utils.NpArrayToImage(old_tiles_np_array[t_id - 1])) for t_id in override_bindings.keys()]
            imagesB = [(t_id, image_utils.NpArrayToImage(new_tiles_np_array[t_id - 1])) for t_id in override_bindings.values()]
            image_utils.CreateTilesCollage2X(image_title, imagesA, imagesB, override_png_path)
            
        # Assemble all the data together to create the final, finalized map
        rebind_map[0] = 0 # Enter base cases. Empty tiles map to empty tiles
        rebind_map.update(override_bindings) # Add overbind entries to the final rebind map
        
        # Add mismatched tile ids to final rebind map - they default to 0 if user proceeds with migration
        for mismatched_tile_id, image in unmatched_tiles:
            rebind_map[mismatched_tile_id] = 0
        
        _ExpandMapBindings(rebind_map) # Expand mapping to include the flipped and rotated permutations
        
        # Assuming the current standard of 2048x2048 image with 16x16 pixels, this is a map of 131,072 entries!
        self.A_to_B_map = rebind_map  # Store for later use
        return len(unmatched_tiles) # Return number of unmatched tiles for CLI purposes
        
        
    def Remap(self, playdo):
        all_tile_layers = playdo.level_root.findall('layer')
        
        # TileRemapper contains 2 dicts to check which mapping (A_B or B_A) is more effective
        # However, when performing large scale "tile migration", only AB is used
        using_dual_maps = len(self.A_to_B_map) == len(self.B_to_A_map)
        using_dual_maps = True
        for tile_layer in all_tile_layers:
            data_element = tile_layer.find('data')
            encoding_used = data_element.get('encoding')
            old_data = data_element.text.strip()
            tiles2d = None
            if encoding_used == 'csv':
                tiles2d = tiled_utils.DecodeCSVIntoTiles2d(old_data, playdo.map_width)
            else:
                tiles2d = tiled_utils.DecodeIntoTiles2d(old_data, playdo.map_width)
            
            if not using_dual_maps:
                # Performing Tile Migration
                for i in range(playdo.map_height):
                    for j in range(playdo.map_width):
                        if tiles2d[i][j] in self.A_to_B_map: 
                            tiles2d[i][j] = self.A_to_B_map[tiles2d[i][j]]
                if encoding_used == 'csv':
                    tile_layer.find('data').text = tiled_utils.EncodeIntoCsv(tiles2d)
                else:
                    tile_layer.find('data').text = tiled_utils.EncodeIntoZlibString64(tiles2d)
            else:
                # Performing Tile Remap
                
                # First, make two copies of the tile layer being remapped
                tiles2d_AB = copy.deepcopy(tiles2d)
                tiles2d_BA = copy.deepcopy(tiles2d)
                count_remapped_A_to_B = 0
                count_remapped_B_to_A = 0
                
                # Subject both tile layer copies to remapping, one uses A_B mapping, the other B_A mapping
                for i in range(playdo.map_height):
                    for j in range(playdo.map_width):
                        if tiles2d[i][j] in self.A_to_B_map:
                            tiles2d_AB[i][j] = self.A_to_B_map[tiles2d[i][j]]
                            count_remapped_A_to_B += 1
                        if tiles2d[i][j] in self.B_to_A_map:
                            tiles2d_BA[i][j] = self.B_to_A_map[tiles2d[i][j]]
                            count_remapped_B_to_A += 1
                
                # Rewrite the original tile layer with the remapped data. We use whichever mapping had more matches
                if count_remapped_A_to_B == 0 and count_remapped_B_to_A == 0:
                    continue
                elif count_remapped_A_to_B > count_remapped_B_to_A:
                    if encoding_used == 'csv':
                        tile_layer.find('data').text = tiled_utils.EncodeIntoCsv(tiles2d_AB)
                    else:
                        tile_layer.find('data').text = tiled_utils.EncodeIntoZlibString64(tiles2d_AB)
                    #print(f"-- tile_remapper.py : layer {tile_layer.get('name')} remapped {count_remapped_A_to_B} tiles!")
                else:
                    if encoding_used == 'csv':
                        tile_layer.find('data').text = tiled_utils.EncodeIntoCsv(tiles2d_BA)
                    else:
                        tile_layer.find('data').text = tiled_utils.EncodeIntoZlibString64(tiles2d_BA)
                    #print(f"-- tile_remapper.py : layer {tile_layer.get('name')} remapped {count_remapped_B_to_A} tiles!")
    
    def _ValidateRemapXml(self, pattern_root, pattern_file_name):
        '''Check pattern file to ensure they are properly formatted. Mandates 2 tile layers & no object groups'''
        # Extracting layers and objectgroups
        layers = pattern_root.findall('layer')
        objectgroups = pattern_root.findall('objectgroup')

        # 1. Check there are no objectgroups
        if len(objectgroups) != 0:
            raise Exception(f"Error in '{pattern_file_name}' detected! There should be no object layers!")
            
        # 2. Check if there are 2 tilelayers
        if len(layers) != 2:
            raise Exception(f"Error in '{pattern_file_name}' detected! Number of tile layers must be 2!")



def _ExpandMapBindings(tile_to_tile_map):
    '''Takes a tile_id to tile_id map & expands it to include the flipped & rotated permutations'''
    tile_map_key_values = list(tile_to_tile_map.items())
    for tile_id_A, tile_id_B in tile_map_key_values:
        
        # Add the flipped entry
        tile_to_tile_map[tiled_utils.FlipTileId(tile_id_A)] = tiled_utils.FlipTileId(tile_id_B)
        
        for _ in range(3):
            # Rotate the Tile IDs & Add
            tile_id_A = tiled_utils.RotateTileId(tile_id_A)
            tile_id_B = tiled_utils.RotateTileId(tile_id_B)
            tile_to_tile_map[tile_id_A] = tile_id_B
            # Add the rotated entry again, but flipped
            tile_to_tile_map[tiled_utils.FlipTileId(tile_id_A)] = tiled_utils.FlipTileId(tile_id_B)
    # After 3 iterations, we have captured all 8 possible orientations of a tile
    

def _ReadMigrationOverrideFile():
    '''Retrieves the Migration "override" file. The override file contains mappings of tile_id to tile_id that we should
    use in the event of missing tile entries or if we want to override what the default image detection discovers'''
    override_file_location = file_utils.GetInputFolder() + '/migrate/override_bindings.toml'
    try:
        override_bindings = toml.load(override_file_location)
        # Convert keys to numbers. Also add 1 to the key & value because of TILED's naming convention
        converted_bindings = {int(k) + 1: v + 1 for k,v in override_bindings.items()}
        return converted_bindings
        
    except FileNotFoundError:
        return {}
    