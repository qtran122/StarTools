''' Command-Line Interface Tool to create goo ATs that match with goo "simplex" tiles.
    This helps expedite the process of setting goo ATs. It sets the exact location with
    correct offset, flippness, and rotation.

    Pink simplex tiles (same as blockout) are used as input:
      Full: 1-, 2-, 3-in-a-row
      Slopes: 1x1, 1x2, 1x4
    
USAGE EXAMPLE:
    python cli_goo.py l27

'''

import argparse
import logic.common.file_utils as file_utils
import logic.common.log_utils as log
import logic.common.level_playdo as play
import logic.pattern.pattern_matcher as PM

#--------------------------------------------------#
'''Variables'''

LIST_TEMPLATE = ["goo_flat_3", "goo_flat_2", "goo_flat_1", "goo_slope_4", "goo_slope_2", "goo_slope_1"]

INPUT_TILELAYER = "_goo_ATs"
OUTPUT_OBJECTGROUP = "objects_goo_ATs"



#--------------------------------------------------#
'''Main'''

arg_description = 'Search a level for the layer _goo_ATs & add corresponding goo ATs.'
arg_help1 = 'Name of the tiled level XML to goo ATs objects to'
arg_help2 = 'Controls the amount of information displayed to screen. 0 = nearly silent, 2 = verbose'



def main():
    # Use argparse to get the filename & other optional arguments from the command line
    parser = argparse.ArgumentParser(description = arg_description)
    parser.add_argument('filename', type=str, help = arg_help1)
    parser.add_argument('--v', type=int, choices=[0, 1, 2], default=1, help = arg_help2)
    args = parser.parse_args()
    log.SetVerbosityLevel(args.v)

    # Create a PatternMatcher and load in the patterns it'll scan for
    pattern_matcher = PM.PatternMatcher()
    for pattern_file in LIST_TEMPLATE:
        file_path = file_utils.GetPatternRoot() + f"{pattern_file}.xml"
        pattern_matcher.LoadPattern(file_path)

    # Look for matches. We search all visible tile layers
    playdo = play.LevelPlayDo(file_utils.GetFullLevelPath(args.filename))
    pattern_matcher.FindAndCreate(playdo, INPUT_TILELAYER, OUTPUT_OBJECTGROUP, allow_overlap = False)

    # Flush changes to File!
    playdo.Write()



#--------------------------------------------------#

main()










# End of File