'''
Command-Line Tool for auto-aligning water_line objects to the x-/y-axis.
    

USAGE EXAMPLE:
	python cli_water.py j08.xml
	python cli_water.py j08.xml --v 2
'''

import argparse
import logic.common.file_utils as file_utils
import logic.common.log_utils as log
import logic.common.level_playdo as play
import logic.standalone.aligner as aligner

#--------------------------------------------------#
'''Main'''

ARG_DESCRIPTION = 'Process a tiled level XML and align water_line objects.'
ARG_HELP1 = 'Name of the tiled level XML'
ARG_HELP2 = 'Verbosity level: 0 = silent. 2 = verbose'



def main():
    # Use argparse to get the filename & other optional arguments from the command line
    parser = argparse.ArgumentParser(description = ARG_DESCRIPTION)
    parser.add_argument('filename', type=str, help = ARG_HELP1)
    parser.add_argument('--v', type=int, choices=[0, 1, 2], default=1, help = ARG_HELP2)
    args = parser.parse_args()
    log.SetVerbosityLevel(args.v)
    log.Info(f'Run cli_water on level \"{args.filename}\"')

    # Use a playdo to read/process the XML
    playdo = play.LevelPlayDo(file_utils.GetFullLevelPath(args.filename))

    # Create a WaterSnapper to align water_line to x-/y-axis
    aligner.AlignWater(playdo)

    # Flush changes to File!
    playdo.Write()



#--------------------------------------------------#

main()










# End of File