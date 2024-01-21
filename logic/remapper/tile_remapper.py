'''A convenience module for reskinning levels'''
import copy
import xml.etree.ElementTree as ET
import logic.common.tiled_utils as tiled_utils

class TileRemapper():
    '''The convenience class to aid performing remap operations upon a TILED level XML file'''
    def __init__(self):
        self.A_to_B_map = {} # maps tile ID to another tile ID
        self.B_to_A_map = {} # maps tile ID to another tile ID (reversed direction)
        
    def LoadPattern(self, pattern_file_path):
        '''Load a 'pattern' to be ...
           ... <FILL IN>
        '''
        # Extract XML root and validate pattern has correct format (2 tile layers, no object groups)
        tree = ET.parse(pattern_file_path)
        root = tree.getroot()
        map_width = int(root.get('width'))        
        self._ValidatePattern(root, pattern_file_path)
        
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
                if tile_id_A == 0 or  tile_id_B == 0:
                    continue
                for _ in range(4):
                    # bind the tile IDs bi-directionally to their respective maps
                    self.A_to_B_map[tile_id_A] = tile_id_B
                    self.B_to_A_map[tile_id_B] = tile_id_A
                    # bind the tile IDs again, but flipped
                    self.A_to_B_map[tiled_utils.FlipTileId(tile_id_A)] = tiled_utils.FlipTileId(tile_id_B)
                    self.B_to_A_map[tiled_utils.FlipTileId(tile_id_B)] = tiled_utils.FlipTileId(tile_id_A)
                    # Rotate the tile IDs
                    tile_id_A = tiled_utils.RotateTileId(tile_id_A)
                    tile_id_B = tiled_utils.RotateTileId(tile_id_B)
                    # After 4 iterations, we have captured all 8 possible orientations of a tile
        
    def Remap(self, playdo):
        all_tile_layers = playdo.level_root.findall('layer')
        
        for tile_layer in all_tile_layers:
            old_data = tile_layer.find('data').text.strip()
            tiles2d = tiled_utils.DecodeIntoTiles2d(old_data, playdo.map_width)
            
            # Make two copies of the tile layer being remapped
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
                tile_layer.find('data').text = tiled_utils.EncodeIntoZlibString64(tiles2d_AB)
                print(f"-- tile_remapper.py : layer {tile_layer.get('name')} remapped {count_remapped_A_to_B} tiles!")
            else:
                tile_layer.find('data').text = tiled_utils.EncodeIntoZlibString64(tiles2d_BA)
                print(f"-- tile_remapper.py : layer {tile_layer.get('name')} remapped {count_remapped_B_to_A} tiles!")
            
    def _ValidatePattern(self, pattern_root, pattern_file_name):
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
