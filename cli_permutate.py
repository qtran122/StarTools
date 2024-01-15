""" Command-Line Tool to <FILL IN>

    USAGE: <FILL IN>
"""

import argparse
import logic.common.level_playdo as PD
import logic.common.file_utils as file_utils
import logic.pattern.pattern_permuter as pattern_permuter

# Use argparse to get the filename from command line
parser = argparse.ArgumentParser(description='Process pattern tiled XML & auto-create all other possible permutations')
parser.add_argument('pattern_filename', type=str, help='Name of the pattern tiled XML for which to create variants')
parser.add_argument('--v', type=int, choices=[0, 1, 2], default=1, help='Verbosity level: 0 = silent. 2 = verbose')
args = parser.parse_args()

# Use a playdo to read/process the XML
playdo = PD.LevelPlayDo(file_utils.GetPatternRoot() + args.pattern_filename)

# Create permutations for the tile layer
pattern_permuter.CreatePermutationsOfPattern(playdo)

# Flush changes to File!
playdo.Write()
