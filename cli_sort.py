'''
Command-Line Tool for setting the _sort2 property values
This includes:
 - Converting old _sort to new _sort2
 - Adjusting _sort2 to not conflict with each other
 - Renaming tilelayer to include suffix of the sort values
    
USAGE EXAMPLE:
    python cli_sort.py sf1 --v 0
    python cli_sort.py sf1 --v 0 --do_not_split
    python cli_sort.py sf1 --v 0 --combined_view
    python cli_sort.py sf1 --v 0 --sort_by_materials
    python cli_sort.py sf1 --v 0 --reveal_all_lights

'''
import argparse
import logic.common.file_utils as file_utils
import logic.common.level_playdo as play
import logic.common.log_utils as log
import logic.standalone.sort2_setter as sort_logic

#--------------------------------------------------#
'''Adjustable Configurations'''

ORDER_4_MATERIALS = ['SPRITE_UNLIT', 'SPRITE_LIT', 'OVERLAY', 'GLOW', 'WINDY']    # First entry has smallest sort number




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
    parser.add_argument('--do_not_split', action='store_true')
    parser.add_argument('--combined_view', action='store_true')
    parser.add_argument('--sort_by_materials', action='store_true')
    parser.add_argument('--reveal_all_lights', action='store_true')
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
    has_error, bg_owp_prev_index, fg_anchor_prev_index, max_layer_count = sort_logic.RenameTilelayer(playdo)
    if has_error: return

    # Milestone 3
    is_sorting_by_mat = args.sort_by_materials
    if is_using_sort1 and is_sorting_by_mat:
        log.Must('\n  WARNING! Attempting to do sort by materials when level is using sort1 standard!')
        log.Must('   Tool will now proceed without sorting by materials.\n\n')
        is_sorting_by_mat = False
    sort_logic.SetMaterialList(ORDER_4_MATERIALS)
    has_error, dict_sortval = sort_logic.ConvertSortValueStandard(playdo, bg_owp_prev_index, fg_anchor_prev_index, max_layer_count, is_using_sort1, is_sorting_by_mat)
    if has_error: return

    # Milestone 4
    if dict_sortval != None:
        is_split_view = not args.do_not_split    # TODO move these directly into the function argument below?
        is_combined_view = args.combined_view
        if is_combined_view: is_split_view = False    # Force to use combined view if specified
        reveal_all_lights = args.reveal_all_lights
        has_error = sort_logic.RelocateSortObjects(playdo, dict_sortval, is_split_view, is_combined_view, reveal_all_lights)

    user_input = input(f"Commit changes to \'{level_name}\'? (Y/N) ")
    if user_input[0].lower() == 'y': playdo.Write()

    log.Must("\nReSORT Run Completed...\n")





#--------------------------------------------------#

main()










# End of File