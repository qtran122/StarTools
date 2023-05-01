'''Utility class for reading a level file specifically'''

import zlib
import base64
import numpy

from logic.common import file_utils as fu

# pylint: disable
# pylint: disable = W0312
# pylint: disable = W0105
'''
W0312  Mixed indentation
W0105  Comment blocks

'''

#==================================================#

'''User's Interface'''

def read_level(level_name):
	'''Read the level, then store all data locally'''
	level_data_str = read_file(level_name)

	global level_data_tags
	level_data_tags = extract_tags(level_data_str)
	num = len(level_data_tags)
	_set_meta()

	_print(f"~End of extracting {num} tags from level~")



def _set_meta():
	'''Set basic properties of the map'''
	global level_w
	global level_h
	level_w = int(get_property_value("map","width"))
	level_h = int(get_property_value("map","height"))
	_print(f"~Level Dimension is {level_w} x {level_h}~")



def get_all_visible_tilelayers():
	'''Return tile layers visible IN-GAME, not in editor'''
	result = []
	for num, tag in enumerate(level_data_tags):
		curr_layer_name = tag.get_value_of("layer", "name")
		is_visible_layer = ( curr_layer_name.find("fg") == 0 )
		is_visible_layer = is_visible_layer or ( curr_layer_name.find("bg") == 0 )
		is_visible_layer = is_visible_layer or ( curr_layer_name.find("_placeholder") == 0 )
		if is_visible_layer:
#			_print(curr_layer_name)
			tilelayer_tag_num = num+1
			while not level_data_tags[tilelayer_tag_num].tag_name == TILELAYER_TAG:
				tilelayer_tag_num += 1

			tilelayer_data = level_data_tags[tilelayer_tag_num].prop_list[0][1]
#			_print(level_data_tags[tilelayer_tag_num].tag_name)
#			_print(tilelayer_data)
			_1D_array = _zlib_to_array(tilelayer_data)
			_2D_array = _1D_to_2D(_1D_array, level_w)
			result.append(_2D_array)
#			break
#	print(result)
	return result



def _zlib_to_array(tilelayer_data):
	compressed_data = tilelayer_data
	decoded_data = base64.b64decode(compressed_data)
	decompressed_data = zlib.decompress(decoded_data)
#	print(decompressed_data)
	return numpy.frombuffer(decompressed_data, dtype = numpy.uint32)

def _1D_to_2D(array1, width):
	array2 = []
	array_row = []
	for num, datum in enumerate(array1):
		array_row.append(datum)
		if num % width == width-1:
#			print(array_row)
			array2.append(array_row)
			array_row = []
#			print(array_row)

	return array2




def get_layer(layer_name):
	'''Search in all the tags for a layer with matching name, then return compressed data'''
	for num, tag in enumerate(level_data_tags):
		curr_layer_name = tag.get_value_of("layer", "name")
		if curr_layer_name == layer_name:
			layer_data = level_data_tags[num+2].prop_list[0][1]
			# TODO: Allow uncompressed input as well by concatenating data
			return layer_data
	return ""



def get_property_value(t_value, p_name):
	'''For matching tag (t_value), obtain data of any requested property (p_name)'''
	for tag in level_data_tags:
		p_value = tag.get_value_of(t_value, p_name)
		if p_value != "":
			return p_value
	return ""



def extract_level_data(level_name, layer_name):
	'''Read and return "certain data" of a level?'''
	read_level(level_name)
	return get_layer(layer_name)

def extract_level_data_array(level_name, layer_name):
	'''Read and return "certain data" of a level?'''
	read_level(level_name)
	str = get_layer(layer_name)

	compressed_data = str
	decoded_data = base64.b64decode(compressed_data)
	decompressed_data = zlib.decompress(decoded_data)

#	print( numpy.frombuffer(decompressed_data, dtype = numpy.uint32) )

#	return decompressed_data
	return numpy.frombuffer(decompressed_data, dtype = numpy.uint32)



def get_level_tag(level_name):
	'''Read and return all tags of a level'''
	read_level(level_name)
	return level_data_tags



def print_tags_all():
	'''Print all the tags provided'''
	_print("\n\tPrinting all tags...")
	for tag in level_data_tags:
#		_print_tag_single(tag)
		tag.print()
	_print("")




#`
class TiledData:
	'''Object Class for storing the data of each tag'''
	def __init__(self, tag_name, prop_list, hierarchy):
		self.hierarchy = hierarchy
		self.tag_name = tag_name
		self.prop_list = prop_list

	def is_end_tag(self):
		'''Return true if is end tag'''
		return (self.tag_name == TILELAYER_TAG or self.tag_name[0] == "/")



	def print(self):
		'''Print individual tag'''
		tag_str = f"  {self.hierarchy}  {self.tag_name}\t"
		for prop in self.prop_list:
			tag_str += f"    [{prop[0]}:{prop[1]}]"
		print(tag_str)



	def get_value_of(self, tag_name, property_name):
		'''Return non-empty value only if tag is matching AND contains property'''
		if self.tag_name != tag_name:
			return ""
		property_value = ""
		for prop in self.prop_list:
#			print(prop)
			if prop[0] == property_name:
				property_value = prop[1]
				break
		return property_value

	def set_value_of(self, tag_name, property_name, property_value):
		'''Set value of property only if tag is matching AND contains property'''
		if self.tag_name != tag_name:
			return False
		for prop in self.prop_list:
			if prop[0] == property_name:
				prop[1] = property_value
				break
		return True





	def get_string(self):
		'''Return the string represented in XML file'''
		level_str = ""
#		level_str += f"  {self.hierarchy}  "

		if not self.tag_name == TILELAYER_TAG:
			for num in range(self.hierarchy):
				level_str += " "
			level_str += f"<{self.tag_name}"
			for property in self.prop_list:
				level_str += f" {property[0]}=\"{property[1]}\""
			if self.tag_name[0] == "?":
				level_str += "?"
			level_str += ">"
		else:
			level_str += f"   {self.prop_list[0][1]}"

		return level_str







#==================================================#

'''Global Variables'''

DEBUG_IR = False
TILELAYER_TAG = "_tile"
TILELAYER_PROP = "_data"

'''
level_data_tags
curr_hierarchy
'''



#==================================================#

'''Utility - Print'''
def _print(content):
	'''Alternate print function'''
	print(f"\t{content}")

def _print_list(list_s):
	'''Print all the contents of a list of string'''
	for line in list_s:
		print(line)



#==================================================#

'''Utility - File I/O'''
def read_file(file_name):
	'''File I/O - Return a list of string'''
	file_object = open(file_name, "r")
	list_s = file_object.readlines()
	for num, line in enumerate(list_s):
		list_s[num] = line.replace("\n", "")
	file_object.close()
#	_print(f"~End of reading file \"{file_object.name}\" with {len(list_s)} lines~")
	_print(f"~End of reading file with {len(list_s)} lines~")
	return list_s



#==================================================#

'''Functions for obtaining tags from given string of a text file'''
def extract_tags(level_data_str):
	'''Extract data from string into tags'''
	level_data_tag = []
	for line in level_data_str:
		curr_tag = extract_tag_single(line)


		# TODO Fix the bug
		global debug_objectgroup
		if debug_objectgroup:
			break




#		curr_tag.print()
		if curr_tag.tag_name != "":
#			_print(curr_hierarchy)
			level_data_tag.append(curr_tag)
	return level_data_tag



def get_debug_tag(num):
	'''Placeholder/Debugging, to be deleted'''
	tag_name = f"tag{num}"
	prop_list = []
	for i in range(num):
		prop_list.append([f"p{i}", f"v{i}"])
		if i > 3:
			break
	return TiledData(tag_name, prop_list)



prev_hierarchy = 0
curr_hierarchy = 0
debug_objectgroup = False
def extract_tag_single(file_str):
	'''Extract data from a single string'''
#	print(file_str)
	global curr_hierarchy
	global prev_hierarchy

	beg_char = file_str[get_pointer_of_after(file_str, '<', 0)+1]
	end_char = file_str[len(file_str)-2]
	is_end_tag = beg_char == '/' or end_char == '/'
#	print(f"({file_str})\n  {beg_char}  {end_char}  =>  {is_end_tag}")

	ptr_beg = file_str.find('<')
	ptr_end = get_pointer_of_after(file_str, ' ', ptr_beg)
	curr_sub_string = file_str[ptr_beg+1:ptr_end]
	if DEBUG_IR:
		print(f'{ptr_beg}~{ptr_end}: {curr_sub_string}')

	if ptr_beg < 0:
		tag_name = TILELAYER_TAG
		prop_list = [[TILELAYER_PROP, file_str.strip()]]
#		curr_hierarchy -= 1
		return TiledData(tag_name, prop_list, curr_hierarchy)

	if ptr_beg < ptr_end:
		tag_name = curr_sub_string
	else:
#		is_end_tag = True
		ptr_beg = file_str.find('<')
		ptr_end = get_pointer_of_after(file_str, '>', ptr_beg)
		curr_sub_string = file_str[ptr_beg+1:ptr_end]
#		_print(curr_sub_string)
		tag_name = curr_sub_string





	# TODO Fix the bug
	global debug_objectgroup
	if debug_objectgroup:
		return TiledData(tag_name, [], curr_hierarchy)
	if tag_name == "objectgroup":
		debug_objectgroup = True
		return




	prop_list = []
	while ptr_end >= 0:
		ptr_beg = ptr_end+1
		ptr_end = get_pointer_of_after(file_str, '=', ptr_beg)
		curr_sub_string = file_str[ptr_beg:ptr_end]
		if DEBUG_IR:
			print(f'{ptr_beg}~{ptr_end}: {curr_sub_string}')
		property_name = curr_sub_string.strip()

		ptr_beg = ptr_end+2
		ptr_end = get_pointer_of_after(file_str, '\"', ptr_beg)
		curr_sub_string = file_str[ptr_beg:ptr_end]
		if DEBUG_IR:
			print(f'{ptr_beg}~{ptr_end}: {curr_sub_string}')
		property_value = curr_sub_string

		if ptr_beg < ptr_end:
			prop_list.append([property_name, property_value])
		else:
			break

	'''This part sets the hierarchy that's mostly for file-writing'''
	'''TODO: The hierarchy gets reduced 1 more than normal'''
	saved_hierarchy = prev_hierarchy
	if (beg_char == '?'):
		dummy()
#		curr_hierarchy -= 1
	elif (beg_char == '/'):
		saved_hierarchy -= 1
		curr_hierarchy -= 1
	elif (end_char == '/'):
		dummy()
#		print("Is end")
#		saved_hierarchy -= 1
#		curr_hierarchy -= 1
	elif (not end_char == "/"):
		curr_hierarchy += 1
#	_print(f"{end_char}  {curr_hierarchy}")



#	_print(tag_name)
#	_print(f"{curr_hierarchy}  {tag_name}")
	prev_hierarchy = curr_hierarchy
	return TiledData(tag_name, prop_list, saved_hierarchy)

def get_pointer_of_after(original, target, ptr_beg):
	'''Return the pointer value of a substring with a different beginning value'''
	search_range = original[ptr_beg:len(original)]
	ptr_end_in_range = search_range.find(target)
	ptr_end_real = ptr_end_in_range + ptr_beg
	return ptr_end_real




def dummy():
	'''This function does nothing'''
	x = 1



#==================================================#










# End of file
