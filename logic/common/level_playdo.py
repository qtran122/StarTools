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
        
        # Map for tile_layer_name to a tiles2d (A 2d array of tile IDs). This is created & cached w/ GetTilemapAs2DList()
        self._2D_tiles_map = {}
        
        # Map for tile_layer_name to a Hashset (for quick checking tile matches). This is created & cached w/  GetTilemapAs2DList()
        self._2D_tiles_hash = {}
        
        print(f"-- level_playdo.py : initialized {file_name} ...")



    def GetTiles2d(self, tile_layer_name):
        '''Retrieves Tiles2D by name (2D array of Tile Ids).
        
        If 'NONE' is provided for tile_layer_name, then retrieves the first Tiles2D found
        '''
        if tile_layer_name in self._2D_tiles_map:
            return self._2D_tiles_map[tile_layer_name]
        
        for layer in self.level_root.findall('layer'):
            if tile_layer_name is None or layer.get('name') == tile_layer_name:
                if tile_layer_name is None:
                    tile_layer_name = layer.get('name')
                data = layer.find('data').text.strip()
                tile_2d_map = tiled_utils.DecodeIntoTiles2d(data, self.map_width)
                self._2D_tiles_map[tile_layer_name] = tile_2d_map
                
                # Create the cache for quick-checking matches in the future
                self._2D_tiles_hash[tile_layer_name] = set()
                for tile_row in tile_2d_map:
                    self._2D_tiles_hash[tile_layer_name].update(tile_row)
                
                return tile_2d_map
        
        return None



    def GetTilesHashSet(self, tile_layer_name):
        #print(f"-- level_playdo.py : GetTilemapAsHashSet {tile_layer_name}")
        if tile_layer_name not in self._2D_tiles_hash:
            raise Exception(f"level_playdo.py : tile_layer hashset '{tile_layer_name}' was requested, but does not exist! " +
                "Call GetTilemapAs2DList() first - that will force its creation.")
        return self._2D_tiles_hash[tile_layer_name]



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



    def Write(self):
        '''Stamps the Playdo back into an XML file and writes to disk'''
        print(f"-- level_playdo.py : flushing changes...")
        self.my_xml_tree.write(self.full_file_name)


        
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