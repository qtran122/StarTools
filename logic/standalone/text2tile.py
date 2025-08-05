'''
Main logic for cli_text2tile.py

USAGE EXAMPLE:
    main_logic.logic(playdo, passed_arguments)
'''
import time
import logic.common.log_utils as log
import logic.common.tiled_utils as tiled_utils

#--------------------------------------------------#
'''Variables'''



'''Local Variables'''
cli_arguments = []
list_obj_data = []	# ( (x,y), width, text_string )
dict_char_index = {}	# KVP: char - Tile ID



'''Constants & Configurations'''
config_print_dict     = False	# Whether the dictionary for character index is logged
config_draw_black     = False	# Whether to draw black tiles on space (& invalid) char
config_draw_debug     = False	# Whether to draw random tiles in the whole layer instead





#--------------------------------------------------#
'''Public Functions'''

def logic(playdo, passed_arguments):
	log.Extra("")
	log.Must("Drawing characters into tilelayer from XML objects...")
	start_time = time.time()

	for arg in passed_arguments: cli_arguments.append(arg)
	_ProcessPlaydo(playdo)
	_SetCharacterIndex()
	_MakeTilelayer(playdo)

	log.Must(f"~~End of All Procedures~~ ({round( time.time()-start_time, 3 )}s)")
	log.Extra("")





#--------------------------------------------------#
'''Parsing the Level'''

def _ProcessPlaydo(playdo):
	log.Must(f"  Processing playdo for text2file objects...")

	# CLI Arguments
	object_name          = cli_arguments[1]
	property_name_string = cli_arguments[2]

	# Register all valid objects
	list_obj = playdo.GetAllObjectsWithName(object_name)
	for obj in list_obj:
		if obj.get("width") == None: continue

		text_content = tiled_utils.GetPropertyFromObject(obj, property_name_string)
		if text_content == '': continue

		pos_x = int(obj.get("x"))
		pos_y = int(obj.get("y"))
		width = int(obj.get("width"))
		pos_x = int(pos_x/16)
		pos_y = int(pos_y/16)
		width = int(width/16)
		obj_tuple = ( (pos_x, pos_y), width, text_content )
		list_obj_data.append(obj_tuple)

	log.Info(f"    {len(list_obj_data)} valid text objects found")
	for data in list_obj_data: log.Extra(f'      {data}')





#--------------------------------------------------#
'''Setting Tile ID Index'''

def _SetCharacterIndex():
	log.Must(f"  Setting dictionary for valid characters to corresponding tile ID...")
	my_dict = {}

	# A~Z, big and small letters
	curr_id = 784+1
	for i in range(ord('a'), ord('z') + 1):
		c = chr(i)	# Small letters
		my_dict[c] = curr_id
		c = chr(i-32)	# Capital letters
		my_dict[c] = curr_id
		curr_id += 1
		if i%5 == 1: curr_id += 128-5

	# Letters
	curr_id = 0+1
	for i in range(ord('1'), ord('9') + 1):
		c = chr(i)
		my_dict[c] = curr_id
		curr_id += 1
	my_dict['0'] = 9+1

	# Additional Punctuations
	my_dict['?'] = 1425+1
	my_dict['/'] = 1426+1

	# Link it to the local variable
	global dict_char_index
	dict_char_index = my_dict
	log.Info(f'    {len(dict_char_index)} characters registered')

	if not config_print_dict: return
	for key, value in dict_char_index.items(): log.Extra(f'      {key}: {value}')





#--------------------------------------------------#
'''Export'''

def _MakeTilelayer(playdo):
	log.Must(f"  Printing characters onto playdo...")

	# CLI Arguments
	layer_name_export    = cli_arguments[0]

	# Wipe the existing layer if already exists
	new_tiles2d = playdo.GetBlankTiles2d()
	for data in list_obj_data:
		x_beg = data[0][0]
		y_beg = data[0][1]
		width = data[1]
		text  = data[2]
		text_rows = _SetTextInRows(text, width)
		log.Extra(f'    {text_rows}')

		# Paste onto tilelayer
		curr_x = x_beg
		curr_y = y_beg
		for row in text_rows:
			if curr_y > playdo.map_height-1: break
			for c in row:
				if curr_x > playdo.map_width-1: break
				if config_draw_black: new_tiles2d[curr_y][curr_x] = 265
				if c in dict_char_index:
					new_tiles2d[curr_y][curr_x] = dict_char_index[c]
				curr_x += 1
			curr_x = x_beg
			curr_y += 1
	if config_draw_debug: new_tiles2d = _DebugDrawTilelayer(new_tiles2d)
	playdo.SetTiles2d(layer_name_export, new_tiles2d)



def _SetTextInRows(text, width):
	text_rows = []
	list_words = text.split(' ')
	curr_row = ""
	for word in list_words:
		valid_row = curr_row
		curr_row += word

		# Register to array after the row is "filled"
		if len(curr_row) > width:
			text_rows.append(valid_row)
			curr_row = word + ' '
		else: curr_row += ' '
	text_rows.append(curr_row)
	return text_rows

def _DebugDrawTilelayer(new_tiles2d):
	for y in range(playdo.map_height):
		temp_id = y*128+1
		for x in range(playdo.map_width):
			new_tiles2d[y][x] = temp_id
			temp_id += 1
	return new_tiles2d





#--------------------------------------------------#










# End of File