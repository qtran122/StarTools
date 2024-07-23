'''
Command-Line Tool to automatically add the following objects to a level:
 - Ground
 - BBs
 - Crystals
 - Skell reefs
 - Asteroid


USAGE EXAMPLE:
    python cli_collide.py j01
    python cli_collide.py j01 --v 2

'''
import argparse
import logic.common.log_utils as log
import logic.common.file_utils as file_utils
import logic.common.level_playdo as play
import logic.pattern.pattern_matcher as PM
import logic.remapper.tile_remapper as TM

#--------------------------------------------------#
# Pattern Lists


# Breakable Blocks and Skell Reefs
_LIST_PATTERN_BB = [
    "breakables",
    "reef1",
    "reef2",
    "reef3",
    "reef4",
    "reef5",
    "reef6"
]

# Ground and Slopes
_LIST_PATTERN_GROUND = [
    "ground",
    "owp_flat",
    "owp_1x1",
    "owp_1x2",
    "owp_1x4",
    "slope_1x1",
    "slope_1x2",
    "slope_1x2a",
    "slope_1x2b",
    "slope_1x4",
    "slope_1x4a"
]

# Crystals
_LIST_CRYSTAL = [
    "crystal_1x1",
    "crystal_1x2",
    "crystal_1x2a",
    "crystal_1x2b",
    "crystal_1x4",
    "crystal_solid",
]

# Asteroids
_LIST_ASTEROIDS = [
    "asteroid_6x3",
    "asteroid_5x2",
    "asteroid_4x3",
    "asteroid_3x2",
    "asteroid_2x2",
]



#--------------------------------------------------#
'''Main'''

ARG_DESCRIPTION = 'Process a tiled level XML and add BB + reef objects to a "_BB" layer.'
ARG_HELP1 = 'Name of the tiled level XML to add BB & reef objects to'
ARG_HELP2 = 'Controls the amount of information displayed to screen. 0 = nearly silent, 2 = verbose'



def main():
    ''' Use argparse to get the filename & other optional arguments from the command line'''
    parser = argparse.ArgumentParser(description = ARG_DESCRIPTION )
    parser.add_argument('filename', type=str, help = ARG_HELP1)
    parser.add_argument('--v', type=int, choices=[0, 1, 2], default=1, help = ARG_HELP2)
    args = parser.parse_args()
    log.SetVerbosityLevel(args.v)

    # Use a playdo to read/process the XML
    pattern_root = file_utils.GetPatternRoot()
    playdo = play.LevelPlayDo(file_utils.GetFullLevelPath(args.filename))

    # Remap rotated & flipped solid greyblocks to not have any transformation applied
    tile_remapper = TM.TileRemapper()
    tile_remapper.LoadRemapXml(file_utils.GetFullRemapPath("remap_greyblocks"), False)
    tile_remapper.Remap(playdo)

    # Create a PatternMatcher for "_BB" : Breakable Blocks and Skell Reefs
    pattern_matcher_bb = PM.PatternMatcher()
    for pattern in _LIST_PATTERN_BB:
        pattern_matcher_bb.LoadPattern(pattern_root + pattern + ".xml")

    # Create a PatternMatcher for "fg_raw" : Ground and Slopes
    pattern_matcher_ground = PM.PatternMatcher()
    for pattern in _LIST_PATTERN_GROUND:
        pattern_matcher_ground.LoadPattern(pattern_root + pattern + ".xml")

    # Create a PatternMatcher for "fg_crystal" : Crystals
    pattern_matcher_crystal = PM.PatternMatcher()
    for pattern in _LIST_CRYSTAL:
        pattern_matcher_crystal.LoadPattern(pattern_root + pattern + ".xml")

    # Create a PatternMatcher for "_asteroids" : Creates Asteroids
    pattern_matcher_asteroid = PM.PatternMatcher()
    for pattern in _LIST_ASTEROIDS:
        pattern_matcher_asteroid.LoadPattern(pattern_root + pattern + ".xml")

    # Perform the matching - mold the playdo
    pattern_matcher_bb.FindAndCreate(playdo, "_BB", "collisions_BB", allow_overlap = False)
    pattern_matcher_ground.FindAndCreate(playdo, "fg_raw", "collisions", allow_overlap = False)
    pattern_matcher_crystal.FindAndCreate(
        playdo, "fg_crystal", "collisions_crystal", allow_overlap = False)
    pattern_matcher_asteroid.FindAndCreate(
        playdo, "_asteroids", "objects_asteroids", allow_overlap = False)

    # Flush changes to File!
    playdo.Write()



#--------------------------------------------------#

main()










# End of File
