""" Command-Line Interface Tool to create pearls, oysters, and shells that match their respective treasure
    tiles. This helps expedite the process of setting oysters, and particularly their angle, which when
    outside of the 8 cardinal directions, can have finnicky precise angle setting requirements.
    
    USAGE EXAMPLE: "python cli_pearls.py l26"
"""
import argparse
import random
import logic.common.level_playdo as play
import logic.common.file_utils as file_utils
import logic.pattern.pattern_matcher as PM

# Use argparse to get the filename & other optional arguments from the command line
parser = argparse.ArgumentParser(description='Search a level for natty mark tiles & add corresponding natty mark ATs.')
parser.add_argument('filename', type=str, help='Name of the tiled level XML to natty mark objects to')
parser.add_argument('--v', type=int, choices=[0, 1, 2], default=1, help='Verbosity level: 0 = silent. 2 = verbose')
args = parser.parse_args()

# Use a playdo to read/process the XML
playdo = play.LevelPlayDo(file_utils.GetFullLevelPath(args.filename))

# Create a PatternMatcher and load in the patterns it'll scan for
patterns = ["pearls0", "pearls1", "pearls2", "pearls3"]
pattern_matcher = PM.PatternMatcher()
for pattern_file in patterns:
    file_path = file_utils.GetPatternRoot() + f"{pattern_file}.xml"
    pattern_matcher.LoadPattern(file_path)

# Look for matches. We search all visible tile layers
pattern_matcher.FindAndCreate(playdo, "_pearls", "objects_pearls", allow_overlap = False)

# Flush changes to File!
playdo.Write()
