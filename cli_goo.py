""" Command-Line Interface Tool to create goo ATs that match with goo "simplex" tiles.
    This helps expedite the process of setting goo ATs. It sets the exact location with
    correct offset, flippness, and rotation.
    
    USAGE EXAMPLE: "python cli_goo.py l27"
"""
import argparse
import random
import logic.common.log_utils as log
import logic.common.level_playdo as play
import logic.common.file_utils as file_utils
import logic.pattern.pattern_matcher as PM

# Use argparse to get the filename & other optional arguments from the command line
parser = argparse.ArgumentParser(description='Search a level for the layer _goo_ATs & add corresponding goo ATs.')
parser.add_argument('filename', type=str, help='Name of the tiled level XML to goo ATs objects to')
parser.add_argument('--v', type=int, choices=[0, 1, 2], default=1, help='Verbosity level: 0 = silent. 2 = verbose')
args = parser.parse_args()

log.SetVerbosityLevel(args.v)

# Use a playdo to read/process the XML
playdo = play.LevelPlayDo(file_utils.GetFullLevelPath(args.filename))

# Create a PatternMatcher and load in the patterns it'll scan for
templates = ["goo_flat_3", "goo_flat_2", "goo_flat_1", "goo_slope_4", "goo_slope_2", "goo_slope_1"]

pattern_matcher = PM.PatternMatcher()
for pattern_file in templates:
    file_path = file_utils.GetPatternRoot() + f"{pattern_file}.xml"
    pattern_matcher.LoadPattern(file_path)

# Look for matches. We search all visible tile layers
pattern_matcher.FindAndCreate(playdo, "_goo_ATs", "objects_goo_ATs", allow_overlap = False)

# Flush changes to File!
playdo.Write()
