""" Command-Line Interface Tool to create anemoine objects that match with anemone "simplex" tiles.
    This helps expedite the process of setting anemones. It sets the exact location with
    correct offset, flippness, and rotation.
    
    USAGE EXAMPLE: "python cli_anemone.py wx1"
"""
import argparse
import random
import logic.common.log_utils as log
import logic.common.level_playdo as play
import logic.common.file_utils as file_utils
import logic.pattern.pattern_matcher as PM

# Use argparse to get the filename & other optional arguments from the command line
parser = argparse.ArgumentParser(description='Search a level for the layer _anemones & add corresponding anemones.')
parser.add_argument('filename', type=str, help='Name of the tiled level XML to goo ATs objects to')
parser.add_argument('--v', type=int, choices=[0, 1, 2], default=1, help='Verbosity level: 0 = silent. 2 = verbose')
args = parser.parse_args()

log.SetVerbosityLevel(args.v)

# Use a playdo to read/process the XML
playdo = play.LevelPlayDo(file_utils.GetFullLevelPath(args.filename))

# Create a PatternMatcher and load in the patterns it'll scan for
templates = ["anemone_flat", "anemone_flat_xl", "anemone_slope_1_xl", "anemone_slope_1",
             "anemone_slope_2_xl", "anemone_slope_2", "anemone_slope_4_xl", "anemone_slope_4"]

pattern_matcher = PM.PatternMatcher()
for pattern_file in templates:
    file_path = file_utils.GetPatternRoot() + f"{pattern_file}.xml"
    pattern_matcher.LoadPattern(file_path)

# Look for matches. We search all visible tile layers
pattern_matcher.FindAndCreate(playdo, "_anemones", "objects_anemones", allow_overlap = False)
pattern_matcher.FindAndCreate(playdo, "_anemones2", "objects_anemones", allow_overlap = False, discard_old = False)

# Flush changes to File!
playdo.Write()
