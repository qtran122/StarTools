"""Placeholder for a future module idea.

A transformer module that takes a LevelPlayDo object as input, and performs operations
upon it to sort all the level's object layers. It will aid the neat organization of 
levels and ensure they meet the quality standard.

An example usage of organizer_logic would be as follows:

    import organizer_logic as organizer
    
    playdo = LevelPlayDo("star_ilid/levels/g03.xml")    # Read a tiled xml and create a playdo
    organizer.prettify(playdo)                          # Sorts the object layers
    playdo.write()                                      # Write back our changes to the tiled xml

Organizer will sort the object layers in this order:
    - 'meta' will be the first
    - 'collision' layers will follow after and they will be grouped in a folder
    - 'object' layers follow after, sorted alphabetically, grouped in a folder
    - 'note' layers are last
"""
