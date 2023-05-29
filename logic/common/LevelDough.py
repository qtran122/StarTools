""" LevelPlayDo is a convenience class to aid performing operations upon a TILED level XML file.

This is just an IDEA for now. I plan to discuss with you (Ty) what LevelWriter and LevelReader
are, and if they are suitable for the changes I have planned ahead.

It first reads a TILED level XML file and then creates a LevelPlayDo object which will contain all
of the level's graphical tile data and object data in a readily accessible and easily modifiable 
format. After performing operations on this easily moldable play do, we can save the changes with
LevelPlayDo's write functions.

An example usage of LevelPlayDo would be as follows:

    playdo = LevelPlayDo("star_ilid/levels/g03.xml")    # Read a tiled xml and create a playdo
    quick_collisions.create_collisions(playdo)          # Adds collisions to level playdo
    quick_doors.create_doors(playdo)                    # Adds doors to the level playdo
    organizer.prettify(playdo)                          # Sorts and group the object layers
    playdo.write()                                      # Write back our changes to the tiled xml
    
"""


class LevelPlayDo():
    """The convenience class to aid performing operations upon a TILED level XML file"""

    def __init__(self, level_xml_location):
        print("-- level_playdo.py : Creating a PlayDo for level " + level_xml_location)
        
        self.level_xml_location = level_xml_location
        # TODO: open level_xml_location and process it to fill in the below data structures
        self.level_width = 0
        self.level_height = 0
        self.graphic_tile_layers = [] #list of GraphicTileLayers
        self.object_layers = [] # list of ObjectLayers

    def get_level_width(self):
        """Returns the number width of the TILED level in tile units"""
        return self.level_width

    def get_level_height(self):
        """Returns the number height of the TILED level in tile units"""
        return self.level_height

    def get_graphical_tile_layers(self):
        """Returns a list of TileLayerObjects"""
        return self.graphic_tile_layers

    def set_graphic_tile_layers(self):
        """modifies a list of all the graphical tile layers"""
        return self.object_layers

    def write(self):
        """Stamps the Playdo back into an XML file and writes to disk"""
        print("-- level_playdo.py : flushing changes to " + self.level_xml_location)
        return None


class GraphicTileLayer():
    """Just a stub. We need to discuss what level_play_do will look like"""
    def __init__(self):
        self.layer_name = ""
        self.tiles = []
        

class ObjectLayer():
    """Just a stub. We need to discuss what level_play_do will look like"""
    def __init__(self):
        self.layer_name = ""
        self.tiles = []
