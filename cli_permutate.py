""" Command-Line Tool to <FILL IN>

    USAGE: <FILL IN>
"""

import os
import argparse
import logic.common.level_playdo as PD
import logic.common.file_utils as file_utils
import logic.pattern.pattern_permuter as pattern_permuter

# Use argparse to get the filename from command line
parser = argparse.ArgumentParser(description='Process pattern tiled XML & auto-create all other possible permutations')
parser.add_argument('filename', type=str, help='Name of the pattern or template tiled XML for which to create variants')
parser.add_argument('--v', type=int, choices=[0, 1, 2], default=1, help='Verbosity level: 0 = silent. 2 = verbose')
args = parser.parse_args()

# Use a playdo to read/process the XML
# Note that permutate can operate on patterns and templates, so it searches the 
pattern_file = file_utils.GetFullPatternPath(args.filename)
template_file = file_utils.GetFullTemplatePath(args.filename)

pattern_exists = os.path.exists(pattern_file)
template_exists = os.path.exists(template_file)

if pattern_exists and template_exists:
    raise("There exists both a template and pattern with the same name. Names should not conflict!")

playdo = PD.LevelPlayDo(pattern_file if pattern_exists else template_file)

# Create permutations for the tile layer
pattern_permuter.CreatePermutationsOfPattern(playdo)

# Flush changes to File!
playdo.Write()
