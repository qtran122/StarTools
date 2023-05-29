'''
	Utility class for reading a level file specifically
	This will be revamped in near future
'''

import zlib
import base64
import numpy

from logic.common import utils_file
from logic.common import LevelTag

# pylint: disable
# pylint: disable = W0312
# pylint: disable = W0105
'''
W0312  Mixed indentation
W0105  Comment blocks

'''

#--------------------------------------------------#
'''Global Constants & Variables'''

DEBUG_PRINT_READING = not True	# This prints the tags in console during reading for debugging
DEBUG_PRINT_AS_TAG = True	# This prints the tags in console in more human-readible way
DEBUG_PRINT_AS_STR = not True	# This prints the tags in console in XML format

# [NOTE]
#   Change these DEBUG constants to have the console print out the results
#   It's easier than looking into the functions directly if you just want to understand the structure
#   For practical use, e.g. get the size of the level, simply do get_property_value("map","width")



TILELAYER_TAG = "_tile"
TILELAYER_PROP = "_data"



'''
  (global variables)
	level_data_tags
'''



#--------------------------------------------------#
'''Initialisation'''

def read_level(level_name):
	'''Read the level, then store all data locally (to be used in other functions)'''
	global level_data_tags	# I know global is bad, but I don't know any alternatives
	level_data_str = utils_file.read_file(level_name)	 # Returns list of string
	level_data_tags = extract_tags(level_data_str)  	 # Returns list of LevelTag
	_set_meta()
	utils_file._print(f"~End of extracting {len(level_data_tags)} tags from level~")

def _set_meta():
	'''Set basic properties of the map'''
	level_w = int(get_property_value("map","width"))
	level_h = int(get_property_value("map","height"))
	_print(f"~Level Dimension is {level_w} x {level_h}~")



#--------------------------------------------------#
'''Access Functions'''

def get_property_value(t_name, p_name):
	'''For first tag with matching name, returns the requested property's value'''
	for tag in level_data_tags:
		p_value = tag.get_value_of(t_name, p_name)
		if p_value != "":
			return p_value
	return ""



# There are more functions, but removed temporarily since they aren't relevant for understanding











#--------------------------------------------------#
'''For parsing & extracting LevelTag, given strings of an XML file'''

def extract_tags(level_data_str):
	'''Extract data from list of string into list of tags'''
	level_data_tag = []
	for num, line in enumerate(level_data_str):
		curr_tag = extract_tag_single(line)
		if curr_tag.tag_name != "":
			level_data_tag.append(curr_tag)

		if len(level_data_tag) <= 1:
			continue
		level_data_tag[0].add_child(curr_tag)	# TODO set the hierarchy properly

	if DEBUG_PRINT_AS_TAG:
		level_data_tag[0].print()
	if DEBUG_PRINT_AS_STR:
		level_data_tag[0].print_str()

	return level_data_tag



def extract_tag_single(file_str, debug_print = DEBUG_PRINT_READING):
	'''Extract data from a single string'''
	if debug_print:
		print(f"\n({len(file_str)}) {file_str}")

	result_tuple = _parse_name(file_str, debug_print)
	ptr_beg_next = result_tuple[0]+1
	tag_name = result_tuple[1]
	hierarchy = result_tuple[2]
	prop_list = []

	if tag_name == TILELAYER_TAG:
		added_property = [TILELAYER_PROP, file_str.strip()]
		prop_list.append(added_property)

	has_property = ( ptr_beg_next-1 != 0 ) and (ptr_beg_next != len(file_str))
	if debug_print:
		print(f"   Has property? {has_property}")
	while has_property:
		result_tuple = _parse_property(file_str, ptr_beg_next, debug_print)
		ptr_beg_next = result_tuple[0]+2
		added_property = [result_tuple[1], result_tuple[2]]
		prop_list.append(added_property)
		has_property = (file_str[ptr_beg_next-1] == ' ')

	return LevelTag.LevelTag(tag_name, prop_list, hierarchy)



#--------------------------------------------------#
'''Extract values from a given string'''

def get_pointer_of_after(original, target, ptr_beg):
	'''Return the pointer value of a substring with a different beginning value'''
	search_range = original[ptr_beg:len(original)]
	ptr_end_in_range = search_range.find(target)
	ptr_end_real = ptr_end_in_range + ptr_beg
	return ptr_end_real

def _parse_name( file_str, debug_print = False ):
	'''Extract the value of a LevelTag's name'''
	ptr_beg = get_pointer_of_after(file_str, '<', 0)+1
	ptr_end = get_pointer_of_after(file_str, ' ', ptr_beg)
	if ptr_end < ptr_beg: 	# Tag has no property
		ptr_end = get_pointer_of_after(file_str, '>', ptr_beg)
	tag_name = file_str[ptr_beg:ptr_end]

	if (ptr_beg == 0) and (ptr_end == 0):	# Tag contains tilelayer data
		tag_name = TILELAYER_TAG

	if debug_print:
		print(f"  {ptr_beg} ~ {ptr_end} : {tag_name}")
	return [ptr_end, tag_name, ptr_beg]

def _parse_property( file_str, ptr_beg, debug_print = False ):
	'''Extract the property name & value of a LevelTag's name'''
	ptr_mid = get_pointer_of_after(file_str, '=', ptr_beg)
	ptr_end = get_pointer_of_after(file_str, '\"', ptr_mid+2)
	if ptr_end < ptr_beg: 	# Tag has no property
		ptr_end = get_pointer_of_after(file_str, '>', ptr_beg)
	prop_name = file_str[ptr_beg:ptr_mid]
	prop_value = file_str[ptr_mid+2:ptr_end]
	if debug_print:
		print(f"    {ptr_beg} ~ {ptr_mid} ~ {ptr_end} : \"{prop_name}\" = \"{prop_value}\"")
	return [ptr_end, prop_name, prop_value]



#--------------------------------------------------#
'''base64 & zlib decompression'''

def _zlib_to_array(tilelayer_data):
	'''Convert compressed string into int array that contains the raw tile_id'''
	compressed_data = tilelayer_data
	decoded_data = base64.b64decode(compressed_data)
	decompressed_data = zlib.decompress(decoded_data)
	return numpy.frombuffer(decompressed_data, dtype = numpy.uint32)

def _1D_to_2D(array1, width):
	'''Convert 1D list to 2D list, given the size of all rows'''
	array2 = []
	array_row = []
	for num, datum in enumerate(array1):
		array_row.append(datum)
		if num % width == width-1:
			array2.append(array_row)
			array_row = []
	return array2



#--------------------------------------------------#
'''Lazy shortcuts'''

def _print(content):
	'''Alternate print function'''
	utils_file._print(content)

def _print_list(list_s):
	'''Print all the contents of a list of string'''
	utils_file._print_list(list_s)



#--------------------------------------------------#










# End of file
