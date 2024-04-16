'''Common tiled functions that are generally useful for all Tiling-related scripts.'''

import base64
import zlib
import numpy



#--------------------------------------------------#
'''Base64 string <-> Array'''

def DecodeIntoTiles2d(encoded_str, row_width):
    '''
    Takes a TILED layer encoded string and converts it into a tiles2d
      encoded_str - string containing a layer's 'data' in TILED, zlib-encoded and base64-compressed
      row_width - integer indicating number of cells each row should contain
      tiles2d - 2d array of Tile IDs, first row is at top
      >>> DecodeIntoTiles2d("eAENw4cNACAMAKA66/r/XiGhRES12R1O0+X2eH1+BeAATw==", 4)
      >>> [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]
    '''

    # Convert the base64 string to a numpy array (uint32)
    decoded_data = base64.b64decode(encoded_str)
    decompressed_data = zlib.decompress(decoded_data)
    array = numpy.frombuffer(decompressed_data, dtype=numpy.uint32)

    # Reshape the array to the desired dimensions
    tiles2d = array.reshape(-1, row_width)
    return tiles2d.tolist()



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
'''Object Properties'''

def GetPolyPoints( input_string ):
    '''Convert string into list of tuples: [ (x1,y1), (x2,y2), ... ]'''
    point_strings = input_string.split()
    point_pair_strings = [point_string.split(',') for point_string in point_strings]
    poly_points = [(float(x), float(y)) for x, y in point_pair_strings]
    return poly_points


#--------------------------------------------------#










# end of file