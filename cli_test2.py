'''
Testing file (TY)
 - I likely will be writing my own test files
    since my TextEdit crashes sometimes when loading your code... orz
'''

#==================================================#
'''Import'''

import toml
from logic.common import file_utils as fu
from logic.common import level_reader as lr
from logic.common import level_writer as lw
from logic.common import image_exporter as ie
from logic.test import test_logic as logic


#==================================================#

# I put main() inside a function
#  in order to comment out single lines without affecting indentation
def main():
	'''The main procedure for each CLI'''
	fu.start_procedures()

	input_path = logic.demo_toml()

	fu.print_linebreak_thick()
	input_path += "d30.xml"
	output_path = logic.demo_fileIO(input_path)

	fu.print_linebreak_thick()
	output_path = "pytool_test_output.png"
	logic.demo_old_pytool(output_path)

	fu.end_procedures()

main()

#==================================================#










# End of File
