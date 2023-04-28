"""Placeholder for a future module idea.

A transformer module that takes a LevelPlayDo object as input, and 
performs operations upon it to add glowing animated tile natty marks. 

Natty Marks Logic will search through a LevelPlayDo's graphical tile layers and 
record which tile coordinates have natty marks. It will then choose a random selection
of them to be complemented with an animated tile that will glow, fading in and out.
It will then create a new object layer titled "objects_natty_marks" and add it to LevelPlayDo.

An example usage of natty_marks_logic would be as follows:

    import natty_marks_logic as natty_marks
    
    playdo = LevelPlayDo("star_ilid/levels/g03.xml")    # Read a tiled xml and create a playdo
    natty_marks.set_natty_marks(playdo)                 # Adds natty marks
    playdo.write()                                      # Write back our changes to the tiled xml
"""
