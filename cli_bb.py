""" DEPRECATED!! TOSS THIS FILE
"""
import argparse
import logic.common.level_playdo as play
import logic.common.file_utils as file_utils
import logic.pattern.pattern_matcher as PM

# Use argparse to get the filename & other optional arguments from the command line
parser = argparse.ArgumentParser(description='Process a tiled level XML and add BB + reef objects to a "_BB" layer.')
parser.add_argument('filename', type=str, help='Name of the tiled level XML to add BB & reef objects to')
parser.add_argument('--output', type=str, default='collisions_BB', help='Name of the objects output layer')
parser.add_argument('--input', type=str, default='_BB', help='Name of the graphic tile layer to generate BBs for')
parser.add_argument('--v', type=int, choices=[0, 1, 2], default=1, help='Verbosity level: 0 = silent. 2 = verbose')
args = parser.parse_args()

# Use a playdo to read/process the XML
playdo = play.LevelPlayDo(file_utils.GetLevelRoot() + args.filename)

# Create a PatternMatcher and load in the patterns it'll scan for
pattern_matcher = PM.PatternMatcher()
pattern_root = file_utils.GetPatternRoot()
pattern_matcher.LoadPattern(pattern_root + "breakables.xml")
pattern_matcher.LoadPattern(pattern_root + "reef1.xml")
pattern_matcher.LoadPattern(pattern_root + "reef2.xml")
pattern_matcher.LoadPattern(pattern_root + "reef3.xml")
pattern_matcher.LoadPattern(pattern_root + "reef4.xml")
pattern_matcher.LoadPattern(pattern_root + "reef5.xml")

# Look for matches. This will mold the playdo
pattern_matcher.FindAndCreate(playdo, args.input, args.output)

# Flush changes to File!
playdo.Write()
