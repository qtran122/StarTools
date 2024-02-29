'''
PatternMatcher is a convenience module that scans the entire level for matching patterns.

It loads a playdo object, then scans the requested tilelayer to create the requested objects.


USAGE EXAMPLE:
    import logic.pattern.pattern_matcher as PM
    pattern_matcher_bb = PM.PatternMatcher()
    pattern_matcher_bb.LoadPattern("breakable_blocks_pattern.xml")
    pattern_matcher_bb.FindAndCreate(playdo, "_BB_input", "collisions_BB_output", allow_overlap = False)
    
'''

import os
import toml
import xml.etree.ElementTree as ET
import logic.common.log_utils as log
import logic.common.file_utils as file_utils
import logic.common.tiled_utils as tiled_utils


#--------------------------------------------------#
'''Class Initialization'''

class PatternMatcher():
    '''The convenience class to aid performing operations upon a TILED level XML file'''

    def __init__(self):
        self.pattern_tiles = {} # maps a pattern_name to a 2D list of ints (tile_ids)
        self.pattern_objects = {} # maps a pattern_name to a tuple (object_to_copy, x_offset, y_offset)
        log.Info(f"-- pattern_matcher.py : initialized ...")



#--------------------------------------------------#
    '''Public Functions'''

    def FindAndCreate(self, playdo, tile_layer_name, objects_layer_to_create, allow_overlap = True, discard_old = True):
        '''<FILL IN DESCRIPTION>'''
        
        # Get the target tile layer that will be searched for pattern matches
        target_tiles2d = playdo.GetTiles2d(tile_layer_name)
        if target_tiles2d is None:
            return
        
        # Get the target object group into which new generated objects will be added
        objects_group = playdo.GetObjectGroup(objects_layer_to_create, discard_old)
        
        # Get a HASH of the target tile layer for quick checking
        target_tiles_hash = playdo.GetTilesHashSet(tile_layer_name)
        
        for pattern_name, query_tiles2d in self.pattern_tiles.items():
            object_group_to_copy, rows_trimmed, cols_trimmed  = self.pattern_objects[pattern_name]
            
            # If a quick hash check fails, skip the more expensive pattern match search
            if not self._Possibility4MatchExists(target_tiles_hash, query_tiles2d):
                continue
            
            # Search for patterns
            locations_to_add = self._FindPatternInTileMap(target_tiles2d, query_tiles2d, allow_overlap)
            log.Info(f"-- pattern_matcher.py : {pattern_name} found {len(locations_to_add)} matches!")
            
            # Copy object(s) to wherever there was a pattern match
            for location in locations_to_add:
                for pattern_obj in object_group_to_copy:
                    offset_x = float(pattern_obj.get('x')) - cols_trimmed * playdo.tile_height
                    offset_y = float(pattern_obj.get('y')) - rows_trimmed * playdo.tile_width
                    object_copy = ET.fromstring(ET.tostring(pattern_obj))
                    object_copy.set('x', str(location[0] * playdo.tile_width + offset_x))
                    object_copy.set('y', str(location[1] * playdo.tile_height + offset_y))
                    objects_group.append(object_copy)
    
    def FindAndCreateAll(self, playdo, objects_layer_to_create, allow_overlap = True):
        '''Performs FindAndCreateon all ALL "visible" tile layers (layers starting with "bg_" or "fg_")'''
        tile_layers_to_search = []
        for layer in playdo.level_root.findall('layer'):
            tile_layer_name = layer.get('name')
            if tile_layer_name.startswith("bg_") or tile_layer_name.startswith("fg_"):
                tile_layers_to_search.append(tile_layer_name)
        
        if len(tile_layers_to_search) == 0:
            return
            
        # Perform FindAndCreate on the first name in the list. When we do, discard all the contents of the old layer
        self.FindAndCreate(playdo, tile_layers_to_search[0], objects_layer_to_create, allow_overlap = True, discard_old = True)
        
        # Perform FindAndCreate on the rest of the list. This time, do NOT discard the contents
        for  layer_name in tile_layers_to_search[1:]:
            self.FindAndCreate(playdo, layer_name, objects_layer_to_create, allow_overlap = True, discard_old = False)



#--------------------------------------------------#
    '''Search?'''

    def _Possibility4MatchExists(self, tiles2d_hash, tiles2d_query):
        '''Quick checks tiles2d_query contents vs a hash of the tilemap being searched to ensure the possibility for
        a match exists. If there is no chance, we escape the more expensive future _FindPatternInTileMap call'''
        for tile_row in tiles2d_query:
            for tile_id in tile_row:
                if tile_id not in tiles2d_hash:
                    return False
        return True

    def _FindPatternInTileMap(self, tiles2d_to_search, tiles2d_query, allow_overlap):
        '''Searches a tiles2d tilemap for a specific pattern.

        :param tiles2d_to_search: 2d array of tile IDs (represents a tilemap layer). We will search it for matches
        :param tiles2d_query: smaller 2d array of tile IDs (represents pattern we'll be searching for)
        :return: A list of (x, y) tuples where the top-left corner of the pattern was found.
        '''
        # Calculate the dimensions of the tilemap and the tiles2d_query pattern.
        tilemap_height = len(tiles2d_to_search)
        tilemap_width = len(tiles2d_to_search[0])
        query_height = len(tiles2d_query)
        query_width = len(tiles2d_query[0])

        # Ensure the tiles2d_query can fit within the tilemap.
        if query_width > tilemap_width or query_height > tilemap_height:
            raise Exception("-- pattern_matcher.py : _FindPatternInTileMap() " + 
                "Error! Query is bigger than tilemap!")

        # Helper Fn to check if the query matches the tilemap at a specific location.
        def is_match(x, y):
            for dy in range(query_height):
                for dx in range(query_width):
                    if tiles2d_query[dy][dx] == 0:
                        continue
                    if tiles2d_to_search[y + dy][x + dx] != tiles2d_query[dy][dx]:
                        return False
                        
            # If overlapping matches are not allowed, Zero OUT searched tiles on match
            if not allow_overlap:
                for dy in range(query_height):
                    for dx in range(query_width):
                        if tiles2d_query[dy][dx] != 0:
                            tiles2d_to_search[y + dy][x + dx] = 0 
            return True

        # Search for the tiles2d_query pattern in the tilemap.
        matches = []
        for y in range(tilemap_height - query_height + 1):
            for x in range(tilemap_width - query_width + 1):
                if is_match(x, y):
                    matches.append((x, y))

        return matches



#--------------------------------------------------#
    '''Pattern'''

    def LoadPattern(self, pattern_file_path):
        '''Load a 'pattern' to be searched for AND the objects to generate should a match be found.
           Underneath, a pattern is a tiles2d (aka 2D array of tile ids)
           
           The objects aren't created until pattern_matcher.FindAndCreate() is called.
           ... <FILL IN>
        '''
        if (not os.path.exists(pattern_file_path)):
            raise Exception(f"Pattern {pattern_file_path} was requested, but it does not exist!")
        
        tree = ET.parse(pattern_file_path)
        root = tree.getroot()
        
        # Check pattern file to ensure it's in the right format
        self._ValidatePattern(root, pattern_file_path)
        
        for layer in root.findall('layer'):
            data = layer.find('data')
            pattern_width = int(root.get('width'))
            encoded_string = data.text.strip()
            tiles2d = tiled_utils.DecodeIntoTiles2d(encoded_string, pattern_width)
            tiles2d, rows_trimmed, cols_trimmed = tiled_utils.TrimTiles2d(tiles2d)
            
            matching_obj_group = None
            tile_layer_name = layer.get('name')
            for object_group in root.findall('objectgroup'):
                if object_group.get('name') == tile_layer_name:
                    matching_obj_group = object_group
                    break
            
            # Add tiles2d pattern & corresponding objects into internal structures for later matching
            key_name = file_utils.StripFilename(pattern_file_path) + '_' + tile_layer_name
            self.pattern_tiles[key_name] = tiles2d
            self.pattern_objects[key_name] = (matching_obj_group, rows_trimmed, cols_trimmed)
            
            #log.Info("----------- pattern -----------")
            #tiled_utils.PrintTiles2d(tiles2d, True)
            log.Extra("-- pattern_matcher.py : LOADED pattern " + key_name + "...")
        
    def _ValidatePattern(self, pattern_root, pattern_file_name):
        ''' Check pattern file superficially to ensure they are properly formatted.
        
            Namely, this checks that there's an equal number of layers and object groups. And
            that they are uniquely paired (each tile layer shares its name with one object group)
        '''
        # Extracting layers and objectgroups
        layers = pattern_root.findall('layer')
        objectgroups = pattern_root.findall('objectgroup')

        # 1. Check if there are an equal number of objectgroups and layers
        if len(layers) != len(objectgroups):
            raise Exception(f"Error in '{pattern_file_name}' detected! Number of objectgroups & layers must be equal!")

        # 2. Check no layers share the same name
        layer_names = [layer.get('name') for layer in layers]
        layer_names_set = set(layer_names)
        if len(layer_names) != len(layer_names_set):
            raise Exception(f"Error in '{pattern_file_name}' detected! Tile layers should not have duplicate names!")

        # 3. Check no objectgroups share the same name
        objectgroup_names = [objectgroup.get('name') for objectgroup in objectgroups]
        if len(objectgroup_names) != len(set(objectgroup_names)):
            raise Exception(f"Error in '{pattern_file_name}' detected! Objectgroups should not have duplicate names!")
        
        # 4. Check if each objectgroup has a name that matches with a layer
        for name in objectgroup_names:
            if name not in layer_names:
                raise Exception(f"Error in '{pattern_file_name}' detected! " + 
                    f"Objectgroup '{name}' does not match with any tile layer name.")

        # 5. Check if each objectgroup has at least one object
        for objectgroup in objectgroups:
            if len(objectgroup.findall('object')) == 0:
                raise Exception(f"Error in '{pattern_file_name}' detected! " + 
                    f"Objectgroup '{objectgroup.get('name')}' does not contain any objects.")



#--------------------------------------------------#










# end of file