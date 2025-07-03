''' LevelPlayDo is a convenience class to aid performing operations upon a TILED level XML file.

It parses a TILED XML into an ElementTree and then acts as a wrapper around said ElementTree,
creating and caching relevant meta data as they become needed. After performing operations on
this easily moldable playdo, we can save the changes with LevelPlayDo's write functions.

An example usage of LevelPlayDo would be as follows:

    playdo = LevelPlayDo("star_ilid/levels/g03.xml")    # Read a tiled xml and create a playdo
    quick_collisions.create_collisions(playdo)          # Adds collisions to level playdo
    quick_doors.create_doors(playdo)                    # Adds doors to the level playdo
    organizer.prettify(playdo)                          # Sorts and group the object layers
    playdo.write()                                      # Write back our changes to the tiled xml
    
'''
import random
import copy
import xml.etree.ElementTree as ET
import logic.common.log_utils as log
import logic.common.tiled_utils as tiled_utils



#--------------------------------------------------#

class LevelPlayDo():
    '''The convenience class to aid performing operations upon a TILED level XML file'''

    def __init__(self, file_name):
        # Parse the XML file and store the high-level root variables
        self.full_file_name = file_name
        self.my_xml_tree = ET.parse(self.full_file_name)
        self.level_root = self.my_xml_tree.getroot()
        
        # Extract map dimensions and tile size from the level
        self.map_width = int(self.level_root.get('width'))
        self.map_height = int(self.level_root.get('height'))
        self.tile_width = int(self.level_root.get('tilewidth'))
        self.tile_height = int(self.level_root.get('tileheight'))
        
        # Map for tile_layer_name to a tiles2d (A 2d array of tile IDs). This is created & cached w/ GetTiles2d()
        self._tiles2d_map = {}
        
        # Map for tile_layer_name to a Hashset (for quick checking tile matches). This is created & cached w/  GetTiles2d()
        self._tiles2d_hash = {}
        
        log.Extra(f"-- level_playdo.py : initialized {file_name} ...")


    def GetAllTileLayerNames(self):
        '''Fetches the names of all graphic tile layers and returns them as a list of strings'''
        tile_layer_names = []
        # Search using an XPath query so that tile_layers tucked within folders will not be missed
        for tile_layer in self.level_root.findall(".//layer"):
            tile_layer_name = tile_layer.get('name')
            if tile_layer_name is None:
                tile_layer_names.append('unnamed_tile_layer')
            else:
                tile_layer_names.append(tile_layer_name)
                
        log.Extra(f'-- level_playdo.py : number tile layers found : {len(tile_layer_names)}')
        return tile_layer_names



    def GetTiles2d(self, tile_layer_name, ignore_dupe_warnings = False):
        '''Retrieves Tiles2d by name (2D array of Tile Ids).
        
        tile_layer_name - the name of the tile layer in the LEVEL xml that we want to retrieve.
        ignore_dupe_warnings - technically, it's possible for multiple tile layers in a level XML
        to share the same name. In such cases, GetTiles2d returns the Tiles2D data of the 1st layer
        with matching name and will inform the client that duplicate layers exist. It's possible
        to suppress those warnings by setting this flag to true
        
        Returns 'Tiles2d'. Tiles2d presents the data in an already decoded, easily readable and
        editable format. Apply changes to the Tiles2d and write them back using SetTiles2d()
        '''
        if tile_layer_name in self._tiles2d_map:
            return self._tiles2d_map[tile_layer_name]
        
        tiles2d = None
        for layer in self.level_root.findall('.//layer'):
            if layer.get('name') == tile_layer_name:
                self._ProcessLayer(layer, tile_layer_name)
                if tiles2d is None:
                    tiles2d = self._tiles2d_map[tile_layer_name]
                    if ignore_dupe_warnings: return tiles2d
                else:
                    log.Extra(f"level_playdo.py : GetTiles2d was called for a layer '{tile_layer_name}'" + 
                        ", but multiple tile layers with that name exists!")
                
        
        if tiles2d is None:
            log.Extra(f"level_playdo.py : GetTiles2d was called for a layer '{tile_layer_name}' " + 
                "which did not exist!")
        
        return tiles2d



    def GetAllTiles2d(self):
        '''Fetches all graphic tile layers and returns them as a list of Tiles2d'''
        list_tiles2d = []
        # Search using an XPath query so that tile_layers tucked within folders will not be missed
        for layer in self.level_root.findall(".//layer"):
            data = layer.find('data').text.strip()
            tile_2d_map = tiled_utils.DecodeIntoTiles2d(data, self.map_width)
            if tile_2d_map is None: continue
            list_tiles2d.append(tile_2d_map)
        log.Extra(f'-- level_playdo.py : number tile layers found : {len(list_tiles2d)}')
        return list_tiles2d

    def GetAllObjectgroup(self, is_print = True):
        '''Fetches all object layers and returns them as a list of XML objects'''
        list_objectgroup = []
        # Search using an XPath query so that tile_layers tucked within folders will not be missed
        for objectgroup in self.level_root.findall(".//objectgroup"):
            list_objectgroup.append(objectgroup)
        if is_print:
            log.Extra(f'-- level_playdo.py : objectgroup found : {len(list_objectgroup)}')
        return list_objectgroup





    def SetTiles2d(self, tile_layer_name, new_tiles2d):
        '''Overwrites a LEVEL XML's tile layer with new data - usually after edits have been made
        
        tile_layer_name - the name of the tile layer that we want to overwrite
        new_tiles2d - A 2D array of Tile Ids that contains the edits we want to flush
        '''
        tile_layer_to_rewrite = None
        for layer in self.level_root.findall('layer'):
            if tile_layer_name == layer.get('name'):
                tile_layer_to_rewrite = layer
                break
        if tile_layer_to_rewrite is None:
            raise Exception(f"level_playdo.py : SetTiles2d was called for '{tile_layer_name}'," 
                + f" but '{tile_layer_name}' does not exist!")

        tile_layer_to_rewrite.find('data').text = tiled_utils.EncodeIntoZlibString64(new_tiles2d)


    def GetTilesHashSet(self, tile_layer_name):
        #log.Info(f"-- level_playdo.py : GetTilemapAsHashSet {tile_layer_name}")
        if tile_layer_name not in self._tiles2d_hash:
            raise Exception(f"level_playdo.py : tile_layer hashset '{tile_layer_name}' was requested," + 
            " but does not exist! Call GetTiles2d() first - that will force its creation.")
        return self._tiles2d_hash[tile_layer_name]



    def GetObjectGroup(self, object_group_name, discard_old = True):
        ''' Fetches the objectgroup with the provided name from the level element tree if it exists.
            If it does not exists, creates and returns an empty object group for editing.
            
            If NONE is provided for object_group_name, returns first object_group found
            
            If "discard_old" is specified, the object_group (if found) will be emptied
        '''
        
        # Check if object group already exists in the level. If so, return that one for editing
        
        for object_group in self.level_root.findall('objectgroup'):
            if object_group_name is None or object_group.get('name') == object_group_name:
                if (discard_old):
                    for object in object_group.findall('object'):
                        object_group.remove(object)
                return object_group
        
        # If the object group does NOT exists in the level, create a new one and return it for editing
        new_object_group = ET.SubElement(self.level_root, 'objectgroup', {'name': object_group_name})
        return new_object_group



    def DuplicateObjectGroup(self, object_group_to_copy, new_object_group_name, attrib_properties = None):
        '''Given an object group, create a copy of it into our own level root structures'''

        new_object_group = copy.deepcopy(object_group_to_copy)
        new_object_group.set('name', new_object_group_name)
        
        if attrib_properties is not None:
            for obj in new_object_group.findall('object'):
                _AddPropertiesToObject(obj, attrib_properties)
        
        self.level_root.append(new_object_group)



    def GetAllObjectsWithName(self, object_name):
        '''Searches all object groups to find objects with the given object_name'''
        objects_w_matching_names = []
        for object in self.level_root.findall(".//object"):
            if object.get('name') == object_name:
                objects_w_matching_names.append(object)
        return objects_w_matching_names



    def AddNewTileLayer(self, new_tile_layer_name, encoded_data_str, number_id = '100'):
        # create new tile layer's high and low-level attributes
        tile_layer_attributes = {
            'id': number_id, 
            'name' : new_tile_layer_name, 
            'width': str(self.map_width),
            'height': str(self.map_height)
        }
        data_attributes = {
            'encoding': 'base64', 
            'compression' : 'zlib'
        }
        new_tile_layer = ET.Element('layer', tile_layer_attributes)
        new_tile_layer_data = ET.SubElement(new_tile_layer, "data", data_attributes)
        new_tile_layer_data.text = encoded_data_str
        self.level_root.append(new_tile_layer)



    def RegexReplacePropertyValues(self, target_text, generate_replacement_fn):
        '''Searches through all objects (in all object layers) and looks for object property "values" that contain text
           matching target_text. If found, it will replace target_text with the value generated by generate_replacement_fn.
           See example usage of this function in cli_natty.py
        '''
        for elem in self.level_root.iter('property'):
            if target_text in elem.get('value', ''):
                new_number_string = generate_replacement_fn()
                elem.set('value', elem.get('value').replace(target_text, new_number_string))


    def Write(self, location = None):
        '''Stamps the Playdo back into an XML file and writes to disk'''
        if location is None:
            log.Extra(f"-- level_playdo.py : flushing changes...")
            self.my_xml_tree.write(self.full_file_name)
        else:
            log.Extra(f"-- level_playdo.py : flushing changes to new location...")
            self.my_xml_tree.write(location)



    def PreCalculateInternalTileData(self):
        '''Iterate through all the tile layers and prefill '_tiles2d_map' & '_tiles2d_hash' data
        and then returns them.
        
        Normally, these internal data structures are constructed as needed via calls to GetTiles2d()
        However, GetTiles2d has some blindspots since level names need not be unique. For example,
        if there were 2 tile layers named 'fg_raw', the first fg_raw layer would get processed, and
        it's data would fill _tiles2d_map and _tiles2d_hash. The 2nd fg_raw layer would not be
        reachable and ignored.
        
        Using PreCalculateInternalTileData ensures that the 2nd fg_raw layer will at LEAST be able
        to be processed and inputted into _tiles2d_hash. This way, when it comes to searches, we
        can at least confirm with 100% accuracy something exists (instead of missing it entirely)
        
        Returns two maps: '_tiles2d_map' & '_tiles2d_hash'
        '''
        for tile_layer in self.level_root.findall(".//layer"):
            tile_layer_name = tile_layer.get('name')
            if tile_layer_name is None:
                tile_layer_name = 'unnamed_tile_layer'
            self._ProcessLayer(tile_layer, tile_layer_name)
        
        return self._tiles2d_map, self._tiles2d_hash
    
    
    
    def _ProcessLayer(self, layer, tile_layer_name):
        '''Process a tile layer element tree object, and fill our internal data structures for future ops'''
        
        # Create and store the Tile2d map
        data = layer.find('data').text.strip()
        tile_2d_map = tiled_utils.DecodeIntoTiles2d(data, self.map_width)
        self._tiles2d_map[tile_layer_name] = tile_2d_map
        
        # Also maintain hash of the Tile Ids to facililate quicker lookups in the future
        self._tiles2d_hash[tile_layer_name] = set()
        for tile_row in tile_2d_map:
            self._tiles2d_hash[tile_layer_name].update(tile_row)
#--------------------------------------------------#
'''...'''        

def _AddPropertiesToObject(tiled_object, properties):
    '''Helper function. Adds properties to a tiled object
    '''
    prop_elem = tiled_object.find('properties')
    if prop_elem is None:
        prop_elem = ET.SubElement(tiled_object, 'properties')
    
    # Iterate through each key-value pair in the properties dictionary
    for key, value in properties.items():
        # Check if this property already exists
        existing_prop = None
        for prop in prop_elem.findall('property'):
            if prop.get('name') == key:
                existing_prop = prop
                break
        
        # Update the existing property, or create a new one if it doesn't exist
        if existing_prop is not None:
            existing_prop.set('value', value)
        else:
            new_prop = ET.SubElement(prop_elem, 'property', attrib={'name': key, 'value': value})



#--------------------------------------------------#










# end of file