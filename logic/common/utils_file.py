'''
This file contains:
 - Custom printing funcitons
 - Reader function for choose the root from TOML

'''

#==================================================#
'''Import & Default Constants'''

import time
import os
import toml

DEFAULT_ROOT_TOML = "input/root_dir.toml"



#==================================================#
'''Print Functions'''

def print_linebreak(upper_spacing = 0, lower_spacing = 0, linebreak_char = '='):
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
	for line in list_s:
		print(line)



#==================================================#
'''File I/O'''

def check_file_exist(filepath):
	'''Return False if file is not found, may remove since it's just one-liner'''
	return os.path.exists(filepath)

def get_first_valid_root(root_dir_toml):
	'''Return filepath based on the users' computer'''
	root_dir_args = toml.load(root_dir_toml)
	for name, root in root_dir_args.items():
		if os.path.isdir(root):
			return root + "/"
	return NONE



#==================================================#
'''Untitided'''





# DO NOT READ
# WILL TIDY, SALVAGE, OR REMOVE WHEN NEEDED


















'''Utility - Operations'''

def get_pointer_of_after(original, target, ptr_beg):
	'''Return the pointer value of a substring with a different beginning value'''
	search_range = original[ptr_beg:len(original)]
	ptr_end_in_range = search_range.find(target)
	ptr_end_real = ptr_end_in_range + ptr_beg
	return ptr_end_real



#==================================================#

'''Utility - File I/O'''

def read_file(file_name):
	'''File I/O - Return a list of string'''
	file_object = open(file_name, "r")
	list_s = file_object.readlines()
	for num, line in enumerate(list_s):
		list_s[num] = line.replace("\n", "")
	file_object.close()
	_print(f"~End of reading file \"{file_object.name}\" with {len(list_s)} lines~")
	return list_s

def write_file(file_name, content):
	'''File I/O - Print a file with the provided content string / string[]'''
	_print("Printing file...")

def strip_suffix(og_name):
	ptr = og_name.find(".")
	new_name = og_name[0:ptr]
#	_print(f"{og_name} (0:{ptr}) -> {new_name}")
	return new_name



#==================================================#

'''Star Iliad specific'''

def set_meta(filename):
	'''TODO - Change it during initialisation of child driver classes instead'''
	global dir_meta
	dir_meta = FOLDER_META + filename
	if(DEBUG_Base):
		_print(f"Current directory of meta file is set to \"{dir_meta}\"")



def read_meta(dir_meta):
	'''SI - Read the meta data and store them internally'''
	global meta_data
	meta_data = []
	temp_data = read_file(dir_meta)

	num_data = len(temp_data)
	for num, line in enumerate(temp_data):
		if( num == 0 ):
			continue
		if( len(line) == 0 ):
			num_data = num-1;
			break

		ptr_end = get_pointer_of_after(line, '\t', 0)
		meta_data.append( (line[0:ptr_end]).strip() )

		if(DEBUG_Base):
			_print(f"Extracting data from 0 to {ptr_end}...")
			_print(f"\"{meta_data[num-1]}\"")

	_print(f"~Total of {num_data} meta data registered~")
	if(not DEBUG_Base):
		_print_meta()



def get_meta():
	return meta_data

def _print_meta():
	'''Si - Print the meta data'''
	_print("Printing meta data...")
	print()
	for num, line in enumerate(meta_data):
		_print(f"Meta {num}:	\"{line}\"")
	print()








#==================================================#










# End of File
