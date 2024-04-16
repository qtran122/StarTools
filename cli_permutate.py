'''
Command-Line Tool to permute a pattern XML file to add the 7 other variants

    Say we wish to create a new skell reef pattern xml to be added to cli_collide tool. We create 
    a new pattern file XML, add a tile layer, then add an object layer. That allows us to match one
    orientation. However, the skell reef can be flipped and rotated for a total of 8 different
    orientations. To save on the tedium of creating the 7 other orientations manally, we can use 
    cli_permutate. It will create the 7 other orientations. The 7 generated tile layers will be 
    flipped and rotated. Object layers will have the 'angle' and 'flipped' flags already added

USAGE EXAMPLE:
	python cli_permutate.py reef7 # reef7.xml has been added as an example
'''

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
