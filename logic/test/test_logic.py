"""A test module to see examples of import and toml in action!"""

from logic.common import math_utils  # this line serves as an example of how to import
from logic.common import file_utils as fu
from logic.common import level_reader as lr
from logic.common import level_writer as lw
from logic.common import image_exporter as ie


def perform_import_example(num1):
    """Currently, this is just a placeholder to show how we can import correctly.
    
    Note how we import math_utils and then successfully use its functions
    """

    print ("-- test_logic.py : perform_import_example()")
    return math_utils.add_one(num1)
    

def demo_toml():
	# TOML DEMO
	fu.debug_root("input/root_dir.toml")
	input_path = fu.get_first_valid_root("input/root_dir.toml")
#	print(input_path)
	return input_path

def demo_fileIO(input_filename):
	# File I/O
	lr.read_level(input_filename)

def demo_old_pytool(output_path):
	# Old Pytools DEMO
	ie.load_tilesheet()
	list_tilelayer = lr.get_all_visible_tilelayers()
	ie.print_level_image( output_path, list_tilelayer )




