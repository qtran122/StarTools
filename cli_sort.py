'''
Command-Line Tool for setting the _sort2 property values
This includes:
 - Converting old _sort to new _sort2
 - Adjusting _sort2 to not conflict with each other
 - Renaming tilelayer to include suffix of the sort values
    
USAGE EXAMPLE:
    python cli_sort.py sf1 --v 0

'''
import argparse
import logic.common.file_utils as file_utils
import logic.common.level_playdo as play
import logic.common.log_utils as log
import logic.standalone.sort2_setter as sort_logic

#--------------------------------------------------#
'''Adjustable Configurations'''





#--------------------------------------------------#
'''Main'''

arg_description = 'Process a tiled level XML and <TBA>'
arg_help1 = 'Name of the tiled level XML'
arg_help2 = 'Controls the amount of information displayed to screen. 0 = nearly silent, 2 = verbose'

def main():
    # Use argparse to get the filename & other optional arguments from the command line
    parser = argparse.ArgumentParser(description = arg_description)
    parser.add_argument('filename', type=str, help = arg_help1)
    parser.add_argument('--v', type=int, choices=[0, 1, 2], default=1, help = arg_help2)
    parser.add_argument('--split_view', action='store_true')
    parser.add_argument('--combined_view', action='store_true')
    args = parser.parse_args()
    log.SetVerbosityLevel(args.v)

    # Scan through each level in folder directory
    # TODO replace with a loop to scan through all levels in a folder
    has_error = False

    level_name = args.filename
    playdo = play.LevelPlayDo(file_utils.GetFullLevelPath(level_name))

    # Milestone 1
    has_error, is_using_sort1 = sort_logic.ErrorCheckSortOrder(playdo)
    if has_error: return

    # Milestone 2
    has_error, bg_owp_prev_index, max_layer_count = sort_logic.RenameTilelayer(playdo)
    if has_error: return

    # Milestone 3
    has_error, dict_sortval = sort_logic.ConvertSortValueStandard(playdo, bg_owp_prev_index, max_layer_count, is_using_sort1)
    if has_error: return

    # Milestone 4
    if dict_sortval != None:
        is_split_view = args.split_view    # TODO move these 2 into the function argument below?
        is_combined_view = args.combined_view
        has_error = sort_logic.RelocateSortObjects(playdo, dict_sortval, is_split_view, is_combined_view)

    # Milestone 5
#    if dict_sortval != None:
#        has_error = sort_logic.RecolorSortObjects(playdo, dict_sortval, True)

    user_input = input(f"Commit changes to \'{level_name}\'? (Y/N) ")
    if user_input[0].lower() == 'y': playdo.Write()

    log.Must("\nReSORT Run Completed...\n")





#--------------------------------------------------#

main()










# End of File