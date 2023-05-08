'''For initiating individual testing units'''

#--------------------------------------------------#
'''Import'''

import toml
from logic.common import utils_file
from logic.common import utils_time
from test_unit import test_root
from test_unit import test_print


#--------------------------------------------------#

def main():
	'''The main procedure for each CLI'''
	clock = utils_time.Clock() # Start the time tracking for program run

#	test_root.main()
	test_print.main()

	clock.end_procedures() # Indicate the end of a successful run, with time elapsed printed


main()

#--------------------------------------------------#










# End of File
