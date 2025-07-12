'''
Command-Line Tool for creating routes in levels.
Level needs to have an object layer set with nodes first.
	
USAGE EXAMPLE:
	python cli_nav.py z01 --v 0
	clear; python cli_nav.py _nav_test --v 2

'''
import argparse
import logic.common.file_utils as file_utils
import logic.common.log_utils as log
import logic.common.level_playdo as play
import logic.standalone.navigation as main_logic

#--------------------------------------------------#
'''Adjustable Configurations'''

# In-editor object layers for nodes & routes
layer_name_node  = "navigation"
layer_name_route = "navigation"


# All objects in this layer cannot be passed through
# OWP/polylines are currently ignored, TODO mark as impassable?
layer_name_collision = "collisions"


# All objects across all object layers with the following names
#  are treated as collision that may potentially block routes
list_object_name = [
	"relic_block", 
	"rare"
]

# Threshold value for determining redundant routes
threshold_redundance = 0.9

# Exported Object & Layer
obj_name_default = "TRAVEL_ROUTES_MAP"
layer_name_export = "navigation"





# Passing configurations to logic
passed_arguments = (
	layer_name_node, 
	layer_name_route, 
	layer_name_collision, 
	list_object_name, 
	threshold_redundance, 
	obj_name_default, 
	layer_name_export
)





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
	args = parser.parse_args()
	log.SetVerbosityLevel(args.v)

	# Use a playdo to read/process the XML
	playdo = play.LevelPlayDo(file_utils.GetFullLevelPath(args.filename))

	# Main Logic
	main_logic.logic(playdo, passed_arguments)

	# Flush changes to File!
	playdo.Write()





#--------------------------------------------------#

main()










# End of File