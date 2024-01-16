""" Command-Line Tool to auto-add ground, BBs, and skell reefs to a level. 
    
    <summary>
    
    USAGE: <FILL IN>
"""
import argparse
import logic.common.level_playdo as play
import logic.common.file_utils as file_utils
import logic.pattern.pattern_matcher as PM

# Use argparse to get the filename & other optional arguments from the command line
parser = argparse.ArgumentParser(description='Process a tiled level XML and add BB + reef objects to a "_BB" layer.')
parser.add_argument('filename', type=str, help='Name of the tiled level XML to add BB & reef objects to')
parser.add_argument('--v', type=int, choices=[0, 1, 2], default=1, help='Verbosity level: 0 = silent. 2 = verbose')
args = parser.parse_args()

# Use a playdo to read/process the XML
pattern_root = file_utils.GetPatternRoot()
playdo = play.LevelPlayDo(file_utils.GetLevelRoot() + args.filename)

# Create a PatternMatcher for "_BB" : Breakable Blocks and Skell Reefs
pattern_matcher_bb = PM.PatternMatcher()
pattern_matcher_bb.LoadPattern(pattern_root + "breakables.xml")
pattern_matcher_bb.LoadPattern(pattern_root + "reef1.xml")
pattern_matcher_bb.LoadPattern(pattern_root + "reef2.xml")
pattern_matcher_bb.LoadPattern(pattern_root + "reef3.xml")
pattern_matcher_bb.LoadPattern(pattern_root + "reef4.xml")
pattern_matcher_bb.LoadPattern(pattern_root + "reef5.xml")

# Create a PatternMatcher for "fg_raw" : Ground and Slopes
pattern_matcher_ground = PM.PatternMatcher()
pattern_matcher_ground.LoadPattern(pattern_root + "ground.xml")
pattern_matcher_ground.LoadPattern(pattern_root + "owp_flat.xml")
pattern_matcher_ground.LoadPattern(pattern_root + "owp_1x1.xml")
pattern_matcher_ground.LoadPattern(pattern_root + "owp_1x2.xml")
pattern_matcher_ground.LoadPattern(pattern_root + "owp_1x4.xml")
pattern_matcher_ground.LoadPattern(pattern_root + "slope_1x1.xml")
pattern_matcher_ground.LoadPattern(pattern_root + "slope_1x2.xml")
pattern_matcher_ground.LoadPattern(pattern_root + "slope_1x2a.xml")
pattern_matcher_ground.LoadPattern(pattern_root + "slope_1x2b.xml")
pattern_matcher_ground.LoadPattern(pattern_root + "slope_1x4.xml")
pattern_matcher_ground.LoadPattern(pattern_root + "slope_1x4a.xml")

# Perform the matching - mold the playdo
pattern_matcher_bb.FindAndCreate(playdo, "_BB", "collisions_BB", allow_repeats = False)
pattern_matcher_ground.FindAndCreate(playdo, "fg_raw", "collisions", allow_repeats = False)

# Flush changes to File!
playdo.Write()
