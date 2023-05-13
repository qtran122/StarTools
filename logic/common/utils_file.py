'''
This file contains:
 - Custom printing funcitons
 - Reader function for choose the root from TOML

'''

#--------------------------------------------------#
'''Import & Default Constants'''

import time
import os
import toml

DEFAULT_ROOT_TOML = "input/root_dir.toml"



#--------------------------------------------------#
'''Print Functions'''

def print_linebreak(upper_spacing = 0, lower_spacing = 0, linebreak_char = '-'):
	'''Prints a divider, can add extra spacing above and/or below'''
	for spacing_count in range(upper_spacing):
		print("")
	print(linebreak_char*50)
	for spacing_count in range(lower_spacing):
		print("")

def _print(print_str):
	'''Alternate print function'''
	print(f"\t{print_str}")

def _print_list(list_s):
	'''Print all the contents of a list of string'''
	print('\n'.join(list_s))
#	for line in list_s:
#		print(line)



#--------------------------------------------------#
'''File I/O'''

def get_first_valid_root(root_dir_toml = DEFAULT_ROOT_TOML):
	'''Return filepath based on the users' computer'''
	root_dir_args = toml.load(root_dir_toml)
	for name, root in root_dir_args.items():
		if os.path.isdir(root):
			return root + "/"
	return NONE

def read_file(file_name):
	'''Returns a list of string'''
	file_object = open(file_name, "r")
	list_s = file_object.readlines()
	for num, line in enumerate(list_s):
		list_s[num] = line.replace("\n", "")
	file_object.close()
	_print(f"~End of reading file \"{file_object.name}\" with {len(list_s)} lines~")
	return list_s

def write_file(file_name, list_s):
	'''Overwrites to the file directory with the provided list of string'''
	_print(f"Overwriting file \"{file_name}\"...")
	file_object = open(file_name, "w")
	file_object.write('\n'.join(list_s))
	file_object.close()
	_print(f"~End of writing file with {len(list_s)} lines~")

def strip_suffix(og_name):
	'''Returns the filename without the ending file type (suffix)'''
	ptr = og_name.find(".")
	new_name = og_name[0:ptr]
	return new_name



#--------------------------------------------------#
'''String Operations'''

# This was previously used for writing level files in QCT
# But since we are revamping the LevelWriter anyway, this function might end up not being used...
def deflate(list_s, list_end = -1):
	'''Remove empty lines of any given list of string'''
	if list_end < 0:
		list_end = len(list_s)
	temp_s = '\n'.join(list_s)
	temp_s = temp_s.replace("\n\n","\n") # Remove odd-numbered empty lines
	temp_s = temp_s.replace("\n\n","\n") # Remove even-numbered empty lines
	# TODO: Find a way to splice a single string into a list by the character '\n'
	list_s2 = [temp_s]
	return list_s2




#--------------------------------------------------#










# End of File
