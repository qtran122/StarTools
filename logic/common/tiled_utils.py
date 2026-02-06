'''Common tiled functions that are generally useful for all Tiling-related scripts.'''

import base64
import zlib
import numpy
import copy
import xml.etree.ElementTree as ET
import logic.common.log_utils as log

#--------------------------------------------------#
'''Base64 string <-> Array'''
    

def DecodeIntoTiles2d(encoded_str, row_width, encoding_used = None):
    '''All-purpose Decode to Tiles2d function that will delegate which decoding Fn to use'''
    if encoding_used == 'csv':
        return DecodeCSVIntoTiles2d(encoded_str, row_width)
    else:
        # The only other supported encoding is 'base64 zlib'
        return DecodeBase64ZlibIntoTiles2d(encoded_str, row_width)



def EncodeToTiledFormat(tiles2d, encoding_used = None):
    if encoding_used == 'csv':
        return EncodeIntoCsv(tiles2d)
    else:
        # The only other supported encoding is 'base64 zlib'
        return EncodeIntoZlibString64(tiles2d)



def DecodeBase64ZlibIntoTiles2d(encoded_str, row_width):
    '''
    Takes a TILED layer encoded string and converts it into a tiles2d
      encoded_str - string containing a layer's 'data' in TILED, zlib-encoded and base64-compressed
      row_width - integer indicating number of cells each row should contain
      tiles2d - 2d array of Tile IDs, first row is at top
      >>> DecodeBase64ZlibIntoTiles2d("eAENw4cNACAMAKA66/r/XiGhRES12R1O0+X2eH1+BeAATw==", 4)
      >>> [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]
    '''

    # Convert the base64 string to a numpy array (uint32)
    decoded_data = base64.b64decode(encoded_str)
    decompressed_data = zlib.decompress(decoded_data)
    array = numpy.frombuffer(decompressed_data, dtype=numpy.uint32)

    # Reshape the array to the desired dimensions
    tiles2d = array.reshape(-1, row_width)
    return tiles2d.tolist()



def DecodeCSVIntoTiles2d(csv_str, row_width):
    '''Does same thing as 'DecodeBase64ZlibIntoTiles2d', except it works on CSV data strings '''
    numbers = [int(num_str) for num_str in csv_str.split(',')]
    result = []
    for i in range(0, len(numbers), row_width):
        result.append(numbers[i:i+row_width])
    return result
    


def EncodeIntoZlibString64(tiles2d):
    '''
    Takes a TILED layer encoded string and converts it into a tiles2d
      tiles2d - 2d array of Tile IDs, first row is at top
      encoded_str - string containing a layer's 'data' in TILED, zlib-encoded and base64-compressed
      >>> EncodeIntoZlibString64([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]])
      >>> "eAENw4cNACAMAKA66/r/XiGhRES12R1O0+X2eH1+BeAATw=="
    '''
    # Convert: tiles2d array -> numpy array (uint32) -> bytes -> zlib string -> base64 string
    np_array = numpy.array(tiles2d, dtype=numpy.uint32)
    array_bytes = np_array.tobytes()
    compressed_data = zlib.compress(array_bytes)
    encoded_str = base64.b64encode(compressed_data).decode()

    return encoded_str
    
    
    
def EncodeIntoCsv(tiles2d):
    '''Similar to EncodeIntoZlibString64, except it generates a CSV string'''
    flattened_list = [str(num) for row in tiles2d for num in row]
    encoded_str = ', '.join(flattened_list)
    return encoded_str



#--------------------------------------------------#
'''Tiles2D Utilities'''

def PrintTiles2d(tiles2d, multi_line=False):
    '''Prints a tiles2d (2d array of tile IDs). If multi_line is specified, will space out each row.'''
    if multi_line:
         print('\n'.join(f"[{', '.join(map(str, row))}]" for row in tiles2d))
    else:
        print('[' + ', '.join('[' + ', '.join(str(x) for x in row) + ']' for row in tiles2d) + ']')




def TrimTiles2d(tiles2d):
    '''
    Removes empty rows and columns from a Tiles2D.
      tiles2d - 2d array of Tile IDs, cells with value 0 are "empty tile"
      >>> TrimTiles2d([[0, 0, 0], [0, 1, 2], [0, 3, 4]])
      >>> [[1, 2], [3, 4]]
    '''
    start_row, end_row = len(tiles2d), 0
    start_col, end_col = len(tiles2d[0]), 0

    # Iterate over the tiles2d to find the non-empty area
    for i, row in enumerate(tiles2d):
        for j, val in enumerate(row):
            if val != 0:
                start_row = min(start_row, i)
                end_row = max(end_row, i)
                start_col = min(start_col, j)
                end_col = max(end_col, j)

    # Check if there are any non-zero elements in the tiles2d
    if start_row > end_row or start_col > end_col:
        return [], 0, 0, 0, 0  # Return an empty tiles2d and zero trimming

    # Print the number of trimmed rows and columns
    #print(f"Trimmed {start_row} row(s) from the top and {len(tiles2d) - end_row - 1} row(s) from the bottom.")
    #print(f"Trimmed {start_col} column(s) from the left and {len(tiles2d[0]) - end_col - 1} column(s) from the right.")

    # Extract the trimmed tiles2d
    trimmed_tiles2d = [row[start_col:end_col + 1] for row in tiles2d[start_row:end_row + 1]]
    
    return (trimmed_tiles2d, start_row, start_col)



#--------------------------------------------------#
'''Single-Tile manipulation (Flip & Rotate)'''

def FlipTiles2d(tiles2d):
    '''
    Flips a tiles2d horizontally (pressing [x] in Tiled)
      tiles2d - 2d array of Tile IDs, the rectangular section to flip
      >>> FlipTiles2d([[0, 1, 2], [3, 4, 5]])
      >>> [[-2, -1, -0], [-5, -4, -3]]
    '''
    # Change the cell position, then content within (e.g toggling the top 3 bits)
    flipped_tiles2d = [row[::-1] for row in tiles2d]
    return [[FlipTileId(tile_id) if tile_id != 0 else 0 for tile_id in row] for row in flipped_tiles2d]



def RotateTiles2d(tiles2d):
    '''
    Rotates a tiles2d 90˚ clockwise (pressing [z] in Tiled)
      tiles2d - 2d array of Tile IDs, the rectangular section to rotate
      >>> RotateTiles2d([[0, 1, 2], [3, 4, 5]])
      >>> [[*3,*0], [*4,*1], [*5,*2]]
    '''
    # Change the cell position, then content within (e.g toggling the top 3 bits)
    rotated_tiles2d = list(zip(*tiles2d[::-1]))
    return [[RotateTileId(tile_id) if tile_id != 0 else 0 for tile_id in row] for row in rotated_tiles2d]



def FlipTileId(tile_id):
    '''Flips one tiles horizontally (pressing [x] in Tiled), e.g. 1 -> 2147483650'''
    mask = 1 << 31
    return tile_id ^ mask



def RotateTileId(tile_id):
    '''Rotates one tiles 90˚ clockwise (pressing [z] in Tiled), e.g. 1 -> 2684354563'''

    # Extract the top 3 bits
    top_3_bits = (tile_id >> 29) & 0b111

    # Apply the transformation according to the rotate map
    rotated_bits = _ROTATE_BIT_MAP[top_3_bits]

    # Clear the top 3 bits and then set them to the transformed value
    tile_id = tile_id & 0x1FFFFFFF  # Clear the top 3 bits
    tile_id = tile_id | (rotated_bits << 29)  # Set the new top 3 bits

    return tile_id


# Maps the top 3 bit transformation patterns for TILED rotations
_ROTATE_BIT_MAP = {
    0b000: 0b101,
    0b101: 0b110,
    0b110: 0b011,
    0b011: 0b000,
    0b100: 0b111,
    0b111: 0b010,
    0b010: 0b001,
    0b001: 0b100
}



def GetTileIdPermutations(tile_id):
    '''Processes tile id & returns a list of 8 tile ids (all of the possible orientations from flipping & rotating)'''
    tile_id_list = [tile_id, FlipTileId(tile_id)]
    for _ in range(3):
        tile_id = RotateTileId(tile_id)
        tile_id_list.append(tile_id)
        tile_id_list.append(FlipTileId(tile_id))
    return tile_id_list



#--------------------------------------------------#
'''Fetch object property'''

def GetParentObject(obj, playdo):
    '''Return the parent of any XML tree object, e.g. the objectgroup for a given TILED object'''
    parent_map = {child: parent for parent in playdo.level_root.iter() for child in parent}
    parent_obj = parent_map[obj]
    return parent_obj



def GetNameFromObject( tiled_object ):
    '''Obtain the name of object'''
    obj_name = tiled_object.get('name')
    if obj_name == None: return ''    # Return empty string for nameless object to avoid crash
    return obj_name



def GetPropertyFromObject( tiled_object, property_name ):
    '''Extract the property as string, e.g. returns "20" from GetProperty('_sort')'''
    # Check if the object has any property
    properties = tiled_object.find('properties')
    if properties == None: return ''

    # Continue searching the object's list for specific property
    for curr_property in properties.findall('property'):
        if curr_property.get('name') == property_name:
            return curr_property.get('value')
    return ''    # returning None would crash when attempted to be converted into string



def GetPolyPointsFromObject( tiled_object ):
    '''Obtain the polypoints from object (polygon or polyline) and return a list of tuples: [ (x1,y1), (x2,y2), ... ]'''

    is_polygon = False

    # Obtain data as string
    polyline_attribute = tiled_object.find('polyline')
    if polyline_attribute == None :
        polyline_attribute = tiled_object.find('polygon')
        is_polygon = True
    if polyline_attribute == None : return None
    points_string = polyline_attribute.get('points')

    # Convert string into list of tuples
    point_pair_strings = [pair.split(',') for pair in points_string.split()]
    poly_points = [(float(x), float(y)) for x, y in point_pair_strings]
    if is_polygon: poly_points.append(poly_points[0]) # For "closing" the polygon, TBD?
    return poly_points




def GetVerticesFromObject( tiled_object ):
    '''Create polypoints from rectangular objects and return a list of tuples: [ (x1,y1), (x2,y2), ... ]'''

    x = int(tiled_object.get('x'))
    y = int(tiled_object.get('y'))


    # For polygons and polylines
    polypoints = GetPolyPointsFromObject(tiled_object)
    if polypoints != None:
        new_pts = []
        for pt in polypoints: new_pts.append( (pt[0]+x, pt[1]+y) )
        return new_pts


    # Returns a single point if object has no width
    if tiled_object.get('width') == None: return [(x,y)]


    # Otherwise treat as rectangular objects
    w = int(tiled_object.get('width'))
    h = int(tiled_object.get('height'))
    pt1 = ( x  , y+h )
    pt2 = ( x+w, y+h )
    pt3 = ( x+w, y   )
    pt4 = ( x  , y   )
    return [pt1, pt2, pt3, pt4]





#--------------------------------------------------#
'''Set object property'''

# Deep-copy is needed before object copied from templates can be modified
def CopyXMLObject(obj):
    '''Deep-copy an XML objects, mostly for making new objects from a duplicated template'''
    return copy.deepcopy(obj)



def SetPropertyOnObject(tiled_object, property_name, new_value):
    '''Change the value for the requested property, add new if not exist'''
#    '''Helper function. Adds properties to a tiled object'''

    # Get the properties of object, create new one if none exists yet
    prop_elem = tiled_object.find('properties')
    if prop_elem is None:
        prop_elem = ET.SubElement(tiled_object, 'properties')

    # Change property value if it's already present
    for property in prop_elem.findall('property'):
        if property.get('name') != property_name: continue
        property.set('value', new_value)
        return

    # Add new property if it's originally absent in the tiled_obejct
    ET.SubElement(prop_elem, 'property', attrib={'name': property_name, 'value': new_value})



def SetPolyPointsOnObject( tiled_object, new_value ):
    '''Set a new polypoint value for object, create new one if none exists yet'''
    polyline_tag = tiled_object.find('polyline')
    if tiled_object.find('polyline') is None:
        polyline_tag = ET.SubElement(tiled_object, 'polyline')
    polyline_tag.set('points', new_value)



def MakePolypoints( list_pos, is_reversed = False, polygon_xy = (0,0) ):
    '''
    Converts coordinates (list of tuples of 2 int), into polypoint (string)
    Inputs are in Tiled units, output are in pixel units.
      e.g. (4,2), (0, 8) => "64,32 0,128"
    If is_reversed, the order of vertices is reversed
    By default, output Polygon is assumed to be at x = 0 and y = 0
      Set polygon_xy = list_pos[0] for output string to start with 0,0
    '''

    polypoint_str = ''
    for i,pos in enumerate(list_pos):
        # Choose the current vertex
        curr_pos = pos
        if is_reversed: curr_pos = list_pos[len(list_pos)-1 - i]

        # Add vertex's position to string
        pos_x = curr_pos[0] - polygon_xy[0]
        pos_y = curr_pos[1] - polygon_xy[1]

        # Convert to Tiled unit, rounded to nearest int, i.e. pixel unit
        pos_x = int(pos_x * 16)
        pos_y = int(pos_y * 16)
        polypoint_str += f'{str(pos_x)},{str(pos_y)} '

    # Trim last character in string
    polypoint_str = polypoint_str[:-1]

    log.Extra(f'      - {list_pos} -> \"{polypoint_str}\"')
    return polypoint_str




def RemovePropertyFromObject( tiled_object, property_name ):
    '''Return True if the property exists in object'''

    # Get the properties of object
    properties = tiled_object.find('properties')
    if properties is None: return False

    # Remove property if it exists
    has_property_to_be_removed = False
    for property in properties.findall('property'):
        if property.get('name') != property_name: continue
        properties.remove(property)
        has_property_to_be_removed = True
    if not has_property_to_be_removed: return False

    # If the property getting removed is the only property, add the no-op #Q property
    if len(properties) == 0:
        SetPropertyOnObject(tiled_object, '#Q', '')
    return True





#--------------------------------------------------#
'''Relocate objects'''

def MoveObjectToNewObjectgroup(playdo, obj, new_objectgroup):
    '''
     Relocate an object from any objectgroup to the destinated one.
     If the objectgroup no longer contains any object and becomes empty, objectgroup is deleted.
     If the objectgroup was previously in a folder and it no longer contains any tilelayer or objectgroup, folder is deleted.
    
     :param playdo:          A TILED level in an easily moldable state (wrapped around ElementTree + some helpers)
     :param obj:             Object to be relocated
     :param new_objectgroup: Objectgroup (as XML Object), destination of the relocation
    '''
    # Relocate
    old_objectgroup = GetParentObject(obj, playdo)
    old_objectgroup.remove(obj) 
    new_objectgroup.append(obj)
    log.Extra(f"      {obj.get('name')}    {old_objectgroup.get('name')} -> {new_objectgroup.get('name')}")

    # Delete old objectgroup if it's empty, otherwise the level might not be able to run
    if old_objectgroup.find('object') == None:
        layer_name = old_objectgroup.get('name')
        log.Extra(f'Removing objectgroup \"{layer_name}\"')
        parent_folder = GetParentObject(old_objectgroup, playdo)
        parent_folder.remove(old_objectgroup)

        # If parent layer was in a folder before removal, and folder no longer contains tilelayer/objectgroup, remove folder
        if parent_folder.tag != 'group': return
        if parent_folder.find('objectgroup') != None: return
        if parent_folder.find('layer') != None: return
        folder_name = parent_folder.get('name')
        log.Extra(f'Removing folder \"{folder_name}\"')
        root = GetParentObject(parent_folder, playdo)
        root.remove(parent_folder)
        # NOTE Is unable to delete nested folder


    
def MoveObjectgroupAfter(playdo, objectgroup, destination):
    '''
     Relocate an objectobject to right after another layer, above in in-editor view.
     Accepts either tilelayer or objectgroup.
     NOTE Unlike in the previous function, I haven't tested if the folder removal feature is working properly for this
    
     :param playdo:      A TILED level in an easily moldable state (wrapped around ElementTree + some helpers)
     :param objectgroup: Objectgroup to be relocated
     :param destination: Objectgroup or Tilelayer
    '''

    # Destination can be either objectgroup or tilelayer
    old_parent = GetParentObject(objectgroup, playdo)
    new_parent = GetParentObject(destination, playdo)
    new_id = list(new_parent).index(destination)

    old_parent.remove(objectgroup) 
    new_parent.insert(new_id+1, objectgroup)

    # If parent is a folder before removal, and folder no longer contains tilelayer/objectgroup, remove folder
    if old_parent.tag != 'group': return
    if old_parent.find('objectgroup') != None: return
    if old_parent.find('layer') != None: return
    folder_name = old_parent.get('name')
    log.Extra(f'Removing folder \"{folder_name}\"')
    root = GetParentObject(old_parent, playdo)
    root.remove(old_parent)
    # NOTE Is unable to delete nested folder



def MoveMetaObjectgroupToBottom(playdo):
    '''
     Relocated the 'meta' objectgroup to bottom of level in in-editor view.
     This aims to avoid crash when attempting to load the level, after objectgroups with lighting are relocated at various spots.
     NOTE Currently unused, to be deprecated?
    
     :param playdo:    A TILED level in an easily moldable state (wrapped around ElementTree + some helpers)
    '''

    objectgroup = playdo.GetObjectGroup('meta', False)
    parent = GetParentObject(objectgroup, playdo)
    parent.remove(objectgroup) 
    parent.insert(0, objectgroup)





#--------------------------------------------------#










# end of file