"""A transformer module that takes a LevelPlayDo object as input, and performs operations upon
it to add quick auto-generated collisions. It will aid the quick proto-typing of levels.

An example usage of quick_collision_logic would be as follows:

    import quick_collision_logic as qct
    
    playdo = LevelPlayDo("star_ilid/levels/g03.xml")    # Read a tiled xml and create a playdo
    qct.create_collisions(playdo)                       # Adds auto-generated collisions to playdo
    playdo.write()                                      # Write back our changes to the tiled xml
    
"""

def create_quick_collisions(level_play_do):
    """Adds auto-generated collisions into a LevelPlayDo for quick proto-typing."""
    
    # To Be Implemented
    print("-- quick_collision_logic.py : generating...")