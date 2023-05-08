'''Testing file for choosing the default filepath (root) based on user's machines'''
import toml
import os
from logic.common import utils_file

#--------------------------------------------------#
'''Child Test Functions'''

def test_s1():
	'''Test the join function'''
	list_s = ["line1", "line2"]
	print(list_s)
	print('\n'.join(list_s))
#	utils_file._print_list(list_s)
	utils_file.print_linebreak()

def test_s2():
	'''Test the File I/O function'''
	list_s2 = utils_file.read_file("input/test_list_string.txt")
	list_s2.append("Added line")
#	print(list_s2)
#	print('\n'.join(list_s2))
	utils_file._print_list(list_s2)
	utils_file.write_file("input/test_output.txt", list_s2)
	utils_file.print_linebreak()

def test_s3():
	'''Test the Deflate function'''
	list_s3 = utils_file.read_file("input/test_list_string.txt")
#	utils_file._print_list(list_s3)
	list_s3.append("")
	list_s3.append("> sandwiched by empty lines <")
	list_s3.append("")
	list_s3.append("")
	list_s3.append("eof")
	list_s3b = utils_file.deflate(list_s3)

	utils_file.print_linebreak()
	utils_file._print_list(list_s3)
	utils_file.print_linebreak()
	utils_file._print_list(list_s3b)
	utils_file.print_linebreak()



#--------------------------------------------------#
'''Main Function'''

def main():
	'''Test out various alternate printing functions'''

	list_i = [0, 1, 2]
	print(list_i)

	test_s1()
	test_s2()
	test_s3()



#--------------------------------------------------#










# End of File
