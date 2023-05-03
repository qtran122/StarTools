'''Testing file for choosing the default filepath (root) based on user's machines'''
import toml
import os
from logic.common import utils_file

#==================================================#

def main(root_dir_toml = utils_file.DEFAULT_ROOT_TOML):
	'''Checks the number of roots and highlight the chosen one'''
	if not utils_file.check_file_exist(root_dir_toml):
		return
	root_dir_args = toml.load(root_dir_toml)
	utils_file._print(f"~There's a total of {len(root_dir_args)} roots detected~")
	selected = False
	for name, root in root_dir_args.items():
		print_str = ""
		if not selected and os.path.isdir(root):
			print_str += " -->"
			selected = True
		print_str += f"\t{name} : {root}"
		print(print_str)

#==================================================#










# End of File
