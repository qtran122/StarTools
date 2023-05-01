'''
Testing file (TY)
 - I likely will be writing my own test files
    since my TextEdit crashes sometimes when loading your code... orz
'''

#==================================================#
'''Import'''

import toml
from logic.common import file_utils as fu
#	from logic.common import level_reader as lr
#	from logic.common import level_writer as lw
#	from logic.common import image_exporter as ie
from logic.test import test_logic as logic


#==================================================#

# I put main() inside a function
#  in order to comment out single lines without affecting indentation
def main():
	'''The main procedure for each CLI'''
	fu.start_procedures()

	# TOML DEMO
	fu.debug_root("input/root_dir.toml")

	# File I/O DEMO
	input_path = fu.get_first_valid_root("input/root_dir.toml")
	input_path += "d30.xml"
#	print(input_path)

	fu.end_procedures()

main()

#==================================================#










# End of File
