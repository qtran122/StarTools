'''Testing file for accessing the utils_level_reader'''
import toml
import os
from logic.common import utils_file
from logic.common import utils_level_reader

#--------------------------------------------------#
'''Child Test Functions'''

def test_l1(input_file):
	'''Test reading a level'''
#	print(input_file)
	utils_level_reader.read_level(input_file)
#	utils_file.print_linebreak()




#--------------------------------------------------#
'''Main Function'''

def main():
	'''Test out various alternate printing functions'''
	input_file = utils_file.get_first_valid_root() + "d30.xml"
	input_file = "input/" + "_pytool.xml"
	test_l1(input_file)



#--------------------------------------------------#










# End of File
