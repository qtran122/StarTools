'''
This file contains:
 - Header & Ending functions, for indicating the time elapsed in a successful run
 - Reader function for choose the root from TOML

'''

#==================================================#
'''Import'''

import time
import os
import toml



#==================================================#
'''Print Functions'''

str_linebreak = "=================================================="
def print_linebreak():
	print(str_linebreak)

def print_linebreak_thick():
	print("")
	print(str_linebreak)
	print("")

def _print(print_str):
	'''Alternate print function'''
	print(f"\t{print_str}")

def _print_list(list_s):
	'''Print all the contents of a list of string'''
	for line in list_s:
		print(line)



#==================================================#
'''Header & End'''

def start_procedures():
	'''Template starting function'''
	global time_beg
	time_beg = time.time()
	print("")
	print("\tCommencing procedures...")
	print_linebreak_thick()

def end_procedures():
	'''Template ending function'''
	time_end = time.time()
	time_passed = round((time_end - time_beg), 3)
	print_linebreak_thick()
	print(f"\t~End of All Procedures~ ({time_passed}s)")
	print("")



#==================================================#
'''File I/O'''

def get_first_valid_root(root_dir_toml):
	'''Return filepath based on the users' computer'''
	root_dir_args = toml.load(root_dir_toml)
	for name, root in root_dir_args.items():
		if os.path.isdir(root):
			return root + "/"
#	return "ROOT NOT FOUND"
	return ""

def debug_root(root_dir_toml):
	'''Checks the number of root and the one chosen'''
	root_dir_args = toml.load(root_dir_toml)
	_print(f"~There's a total of {len(root_dir_args)} roots detected~")
	selected = False
	for name, root in root_dir_args.items():
		print_str = ""
#		print(f"{name} : {root}")
		if not selected and os.path.isdir(root):
#			_print(" ^^^selected^^^ ")
			print_str += " -->"
			selected = True
		print_str += f"\t{name} : {root}"
		print(print_str)



#==================================================#










# End of File
