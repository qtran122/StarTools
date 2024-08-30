'''
Command-Line Tool for recreating rotated objects after removing the rotation value,
  while retaining the same coordinates as before the removal.
    
USAGE EXAMPLE:
    python cli_unrotate.py _unrotate --v 2

'''
import argparse
import logic.common.file_utils as file_utils
import logic.common.log_utils as log
import logic.common.level_playdo as play
import logic.standalone.unrotator as unrotator

#--------------------------------------------------#
'''Variables'''
# Delete section if unneeded



#--------------------------------------------------#
'''Main'''

arg_description = 'Process a tiled level XML and <TBA>'
arg_description = 'Process a tiled level XML and remove rotation attributes in objects'
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

    # Main Logic
    unrotator.Unrotate(playdo)

    # Flush changes to File!
    playdo.Write()





#--------------------------------------------------#

main()










# End of File