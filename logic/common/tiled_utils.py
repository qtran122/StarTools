'''Common tiled functions that are generally useful for all Tiling-related scripts.'''

import base64
import zlib
import numpy

def DecodeIntoTiles2d(encoded_str, row_width):
    '''Takes a TILED layer encoded string and converts it into a tiles2d
    
    :param encoded_str: a TILED layer's 'data'. This is an encoded string using zlib base64 compression
    :param row_width: integer indicating how many cells each row should have in the resultant tiles2d
    :returns tiles2d: A 2d array of tile IDs
    
    Example: 
    >>> DecodeIntoTiles2d("eAENw4cNACAMAKA66/r/XiGhRES12R1O0+X2eH1+BeAATw==", 4)
    >>> [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]
    '''
    
    # Decode the base64 string
    decoded_data = base64.b64decode(encoded_str)
    
    # Decompress the data using zlib
    decompressed_data = zlib.decompress(decoded_data)
    
    # Convert the decompressed data to a numpy array with type uint32
    array = numpy.frombuffer(decompressed_data, dtype=numpy.uint32)
    
    # Reshape the array to the desired dimensions
    tiles2d = array.reshape(-1, row_width)
    
    return tiles2d.tolist()
    
def EncodeIntoZlibString64(tiles2d):
    ''' Takes a tiles2d and converts it into a zlib base64 encoded string.
    
    :param tiles2d: A 2d array of tile IDs
    :returns encoded_string: a zlib base64 string
        
    Example: 
    >>> EncodeIntoZlibString64([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]])
    >>> "eAENw4cNACAMAKA66/r/XiGhRES12R1O0+X2eH1+BeAATw=="
    '''
    # Convert the input array to a numpy array with type uint32
    np_array = numpy.array(tiles2d, dtype=numpy.uint32)

    # Convert the numpy array to bytes
    array_bytes = np_array.tobytes()

    # Compress the bytes using zlib
    compressed_data = zlib.compress(array_bytes)

    # Encode the compressed data using base64
    encoded_str = base64.b64encode(compressed_data).decode()

    return encoded_str


def PrintTiles2d(tiles2d, multi_line=False):
    '''Prints a tiles2d (2d array of tile IDs). If multi_line is specified, will space out each row.'''
    if multi_line:
         print('\n'.join(f"[{', '.join(map(str, row))}]" for row in tiles2d))
    else:
        print('[' + ', '.join('[' + ', '.join(str(x) for x in row) + ']' for row in tiles2d) + ']')

def TrimTiles2d(tiles2d):
    '''Removes empty rows and columns from a Tiles2D.
    
    :param tiles2d: A 2d array of tile IDs to trim. A cell is considered empty if it is 0
        
    Example: 
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

def RotateTiles2d(tiles2d):
    '''Rotate a tiles2d 90 degrees clockwise - similar to pressing 'z' on a block of tiles in Tiled
    
    :param tiles2d: A 2d array of tile IDs to rotate.
        
    Example: 
    >>> TrimTiles2d([[0, 1], [2, 3]])
    >>> [[2684354563,2684354561], [2684354564,2684354562]]
    '''
    # rotate the position of the cells
    rotated_tiles2d = list(zip(*tiles2d[::-1]))
    # rotate the content within the cells (e.g toggling the top 3 bits)
    return [[RotateTileId(tile_id) if tile_id != 0 else 0 for tile_id in row] for row in rotated_tiles2d]

def FlipTiles2d(tiles2d):
    '''Flips a tiles2d horizontally - similar to pressing 'x' on a block of tiles in Tiled
    
    :param tiles2d: A 2d array of tile IDs to flip.
        
    Example: 
    >>> FlipTiles2d([[0, 1], [2, 3]])
    >>> [[2147483650, 2147483649], [2147483652, 2147483651]]
    '''
    # flip the position of the cells
    flipped_tiles2d = [row[::-1] for row in tiles2d]
    # flip the content within the cells (e.g. toggling the top 3 bits)
    return [[FlipTileId(tile_id) if tile_id != 0 else 0 for tile_id in row] for row in flipped_tiles2d]

def FlipTileId(tile_id):
    '''Flips one tile id according to TILED's implementation of flippedness.
    
    Example: 
    >>> FlipTileId(1)
    >>> 2147483650
    '''
    
    mask = 1 << 31
    return tile_id ^ mask
    
def RotateTileId(tile_id):
    '''Rotates one tile id according to TILED's implementation of rotation.
    
    Example: 
    >>> RotateTileId(1)
    >>> 2684354563
    '''
    
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
