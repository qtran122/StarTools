'''
Testing file (TY)
 - I likely will be writing my own test files
    since my TextEdit crashes sometimes when loading your code... orz
'''

#==================================================#
'''Import'''

import toml
from logic.common import utils_file
from logic.common import utils_time
from test_unit import test_root


#==================================================#

def main():
	'''The main procedure for each CLI'''
	clock = utils_time.Clock() # Start the time tracking for program run

	test_root.main()

	clock.end_procedures() # Indicate the end of a successful run, with time elapsed printed


main()

#==================================================#










# End of File
