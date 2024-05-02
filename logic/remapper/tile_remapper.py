'''A convenience module for reskinning levels'''
import os
import sys
import copy
import xml.etree.ElementTree as ET
import logic.common.tiled_utils as tiled_utils
import logic.common.image_utils as image_utils
import logic.common.file_utils as file_utils
import logic.common.log_utils as log

class TileRemapper():
    '''The convenience class to aid performing remap operations upon a TILED level XML file'''
    def __init__(self):
        self.A_to_B_map = {} # maps tile ID to another tile ID
        self.B_to_A_map = {} # maps tile ID to another tile ID (reversed direction)
        
    def LoadRemapXml(self, pattern_file_path):
        """Create a mapping of old tile IDs to new tile IDs to rebind the tile IDs of one level"""

        # Extract XML root and validate pattern has correct format (2 tile layers, no object groups)
        root = ET.parse(pattern_file_path)
        map_width = int(root.get('width'))
        self._ValidateRemapXml(root, pattern_file_path)
        
        # Get tilemaps of both layers
        layer_A, layer_B = root.findall('layer')
        data_A = layer_A.find('data').text.strip()
        data_B = layer_B.find('data').text.strip()
        tile_2d_map_A = tiled_utils.DecodeIntoTiles2d(data_A, map_width)
        tile_2d_map_B = tiled_utils.DecodeIntoTiles2d(data_B, map_width)
        
        # Populate the remapping dictionaries (2 are created to auto-detect ideal mapping direction)
        rows = len(tile_2d_map_A)
        cols = len(tile_2d_map_A[0])
        for i in range(rows):
            for j in range(cols):
                tile_id_A = tile_2d_map_A[i][j]
                tile_id_B = tile_2d_map_B[i][j]
                self.A_to_B_map[tile_id_A] = tile_id_B
                self.B_to_A_map[tile_id_B] = tile_id_A
                
        # Expand the remapping dictionary to include flips & rotations
        _ExpandMapBindings(self.A_to_B_map)
        _ExpandMapBindings(self.B_to_A_map)
    
    
    def LoadMigrationMap(self, new_tiles_xml, tiles_png_path):
        """Create a massive mapping of old tile IDs to new tile IDs to migrate the entire LEVELs folder"""
        
        # Extract XML root and validate new_tiles_xml has correct format (1 tile layer & correct size)
        root = ET.parse(new_tiles_xml).getroot()
        self._ValidateMigrationXml(root, new_tiles_xml, tiles_png_path)
        
        # Get size info and tiles2d data
        map_width = int(root.get('width'))
        map_height = int(root.get('height'))
        tiles_data  = root.find('layer').find('data').text.strip()
        tiles2d_map = tiled_utils.DecodeIntoTiles2d(tiles_data, map_width)
        
        # Populate the remapping dictionary & track forgotten tiles that do not exist in new mapping
        max_num_tiles = map_width * map_height
        unseen_tile_ids = {n for n in range(1, max_num_tiles + 1)}
        tile_id_B = 1
        for i in range(map_height):
            for j in range(map_width):
                tile_id_A = tiles2d_map[i][j]
                self.A_to_B_map[tile_id_A] = tile_id_B
                tile_id_B += 1
                unseen_tile_ids.discard(tile_id_A)
                
        # Expand the remapping dictionary to include flips, rotations, and the zero case
        _ExpandMapBindings(self.A_to_B_map)
        self.A_to_B_map[0] = 0
        
        # Prune forgotten tiles to only unique cases
        unseen_tile_ids = self._PruneOutRedundantTiles(unseen_tile_ids, tiles_png_path)
        
        # If forgotten tiles still exist, display them for user convenience
        if unseen_tile_ids:
            # Create a list of tuples (tile_id, Image) - that is the format needed to display a collage
            tiles_images = image_utils.SliceTileSheet(tiles_png_path)
            unseen_tiles_n_images = [(tile_id, tiles_images[tile_id - 1]) for tile_id in unseen_tile_ids] 
            image_title = "- MIGRATION : FORGOTTEN TILES ? -"
            unmatched_png_path = file_utils.GetOutputFolder() + 'migration_forgotten.png'
            image_utils.CreateTilesCollage(image_title, unseen_tiles_n_images, unmatched_png_path)
        
        return unseen_tile_ids
        
        
    def _PruneOutRedundantTiles(self, unseen_tile_ids, tiles_png_path):
        '''Takes set of tile_ids & tilesheet png path. Extracts image data to prune redundancies'''
        tiles_np_array = image_utils.SliceTileSheet(tiles_png_path, make_into_np_array = True)
        unique_unseen_tiles_hash = set()
        unique_unseen_tile_ids = []
            
        for tile_id in unseen_tile_ids:
            # Check 1 : If a tile_id is "unseen", a permutation of it may exist. So check the 
            # A_to_B map because it is expanded to include permutations (flips & rotations)
            if tile_id in self.A_to_B_map : continue
            
            # Check 2 : Next, we get a hash of image referenced by the tile ID. If it truly
            # is unique, we add it to unseen_tile_ids, and update our hash check set
            tile_hash = tiles_np_array[tile_id - 1].tobytes()            
            if tile_hash not in unique_unseen_tiles_hash:
                unique_unseen_tile_ids.append(tile_id)
                unique_unseen_tiles_hash.add(tile_hash)
        
        return unique_unseen_tile_ids
        
        
    def Remap(self, playdo):
        all_tile_layers = playdo.level_root.findall('.//layer')
        
        # TileRemapper contains 2 dicts to check which map (A_to_B or B_to_A) is more effective
        # However, when performing a large scale "tile migration", only the A_to_B map is used
        using_dual_maps = len(self.A_to_B_map) == len(self.B_to_A_map)
        
        for tile_layer in all_tile_layers:
            data_element = tile_layer.find('data')
            encoding_used = data_element.get('encoding')
            old_data = data_element.text.strip()
            tiles2d = tiled_utils.DecodeIntoTiles2d(old_data, playdo.map_width, encoding_used)
            
            if not using_dual_maps:
                # Performing Tile Migration
                
                for i in range(playdo.map_height):
                    for j in range(playdo.map_width):
                        if tiles2d[i][j] in self.A_to_B_map:
                            tiles2d[i][j] = self.A_to_B_map[tiles2d[i][j]]
                tile_layer.find('data').text = tiled_utils.EncodeToTiledFormat(tiles2d, encoding_used)
                
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
                    tile_layer.find('data').text = tiled_utils.EncodeToTiledFormat(tiles2d_AB, encoding_used)
                    log.Info(f"-- tile_remapper.py : layer {tile_layer.get('name')} remapped {count_remapped_A_to_B} tiles!")
                else:
                    tile_layer.find('data').text = tiled_utils.EncodeToTiledFormat(tiles2d_BA, encoding_used)
                    log.Info(f"-- tile_remapper.py : layer {tile_layer.get('name')} remapped {count_remapped_B_to_A} tiles!")
    
    
    def _ValidateRemapXml(self, pattern_root, pattern_file_name):
        '''Check pattern file to ensure they are properly formatted'''
        
        # Extracting all layers and objectgroups
        layers = pattern_root.findall('.//layer')
        objectgroups = pattern_root.findall('.//objectgroup')

        # 1. Check there are no objectgroups
        if len(objectgroups) != 0:
            log.Must(f"Error in '{pattern_file_name}' detected! There should be no object layers!")
            sys.exit()
            
        # 2. Check if there are 2 tilelayers
        if len(layers) != 2:
            log.Must(f"Error in '{pattern_file_name}' detected! Number of tile layers must be 2!")
            sys.exit()

    def _ValidateMigrationXml(self, root, new_tiles_xml, tiles_png_path):
        '''Check migration mapping XML & tiles png to ensure they exist & are properly formatted'''
        
        # Extracting all layers and objectgroups
        layers = root.findall('.//layer')
        objectgroups = root.findall('.//objectgroup')
        
        # 1. Ensure there are no objectgroups
        if len(objectgroups) != 0:
            log.Must(f"\nError in '{new_tiles_xml}' detected!\nThere should be no object layers!")
            sys.exit()
            
        # 2. Ensure there is just 1 tilelayer
        if len(layers) != 1:
            log.Must(f"\nError in '{new_tiles_xml}' detected!\nThere should be just 1 tile layer!")
            sys.exit()
            
        # 3. Ensure map width and map height are the correct sizes
        map_width = int(root.get('width'))
        map_height = int(root.get('height'))
        if map_width != 128 or map_height != 128:
            log.Must(f"\nMaError in new mapping file detected! Size is {map_width} x {map_height}\n" + 
            "Map size should be 128 x 128 tiles - the same size as a master tilesheet png")
            sys.exit()
            
        # 4. Check tiles_png_path exists
        if not os.path.exists(tiles_png_path):
            log.Must(f"\nError in graphics file '{tiles_png_path}'!\nGraphics PNG does not exist!")
            sys.exit()


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

