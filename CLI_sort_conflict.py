'''
Command-Line Tool for detecting objects with the same "sort value" within a level.

    
USAGE EXAMPLE:
    cd /Users/Jimmy/20-GitHub/StarTools
    clear; python CLI_sort_conflict.py j04 --v 2

'''
import argparse
import logic.common.file_utils as file_utils
import logic.common.log_utils as log
import logic.common.level_playdo as play
import logic.standalone.conflict as conflict

#--------------------------------------------------#
'''Variables'''

_LIST_LIGHTING_OBJ = [
    "AT_linear",
    "AT_radial",
    "env_particles",
    "AT_reflect",
    "AT_ray",
    "AT_bilinear"
]




#--------------------------------------------------#
'''Main'''

arg_description = 'Process a tiled level XML and ...'
arg_help1 = 'Name of the tiled level XML'
arg_help2 = 'Controls the amount of information displayed to screen. 0 = nearly silent, 2 = verbose'



def main():
    # Use argparse to get the filename & other optional arguments from the command line
    parser = argparse.ArgumentParser(description = arg_description)
    parser.add_argument('filename', type=str, help = arg_help1)
    parser.add_argument('--v', type=int, choices=[0, 1, 2], default=1, help = arg_help2)
    args = parser.parse_args()
    log.SetVerbosityLevel(args.v)

    # Use a playdo to read/process the XML
    playdo = play.LevelPlayDo(file_utils.GetFullLevelPath(args.filename))

    # ...
    raw_dict = conflict.CheckConflicts(playdo, _LIST_LIGHTING_OBJ)
#    pruned_dict = conflict.PruneConflicts(playdo, conflict_dictionary)
#    conflict.FixConflicts(playdo, pruned_dict)

    # Flush changes to File!
#    playdo.Write()



#--------------------------------------------------#

main()










# End of File