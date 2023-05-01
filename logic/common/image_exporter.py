'''Utility class for reading a level file specifically'''

#import __base as b
#import _common.__base as b
from logic.common import file_utils as b

from PIL import Image
import PIL

# pylint: disable
# pylint: disable = W0312
# pylint: disable = W0105
'''
W0312  Mixed indentation
W0105  Comment blocks

'''

#==================================================#

'''Constant Variables'''

DIR_TILESHEET = "input/tiles.png"

DEBUG_IE = False
PPU = 16

DEBUG_H = 128 # Reduce for faster tilesheet-loading
DEBUG_W = 128 # Reduce for faster tilesheet-loading; DOING SO WOULD FAIL IN PRINTING LEVEL

'''Local Variables
#	tilesheet_data [x][y] [px][py]
	global layer_image
	global result_image
'''



#==================================================#

'''User's Interface'''



def load_tilesheet():
	'''...'''
	global PPU
	global tilesheet_data
	
	sheet_file = Image.open(DIR_TILESHEET)
	sheet_pixel = sheet_file.load()

	sheet_w = (int)( sheet_file.size[0] / PPU )
	sheet_h = (int)( sheet_file.size[1] / PPU )

	# TBD: These make debugging faster
	if True:
		sheet_w = DEBUG_W
		sheet_h = DEBUG_H

	tilesheet_data = []
	tile_count = 0
	for y in range(sheet_h):
		for x in range(sheet_w):
			index = x + y* sheet_w
			tilesheet_data.append( get_tile_img(sheet_pixel, x, y) )
			tile_count += 1
#			if DEBUG_IE:
#				tilesheet_data[index].save( f"temp/{index}.png" )

#	__set_tilesheet_orientation()
#	for tile_or in range(8):
#		_debug_print_sheet(tile_or)

	b._print(f"~Total of {tile_count} tiles loaded in Tilesheet ({sheet_w} x {sheet_h})~")



def __set_tilesheet_orientation():
	'''(Obsolete) This pre-ready duplicates of current tilesheet in all 8 orientations'''
	global tilesheet_data
	global tilesheet_data2
	tilesheet_data2 = []

	for tile_or in range(8):
		or_tuple = _or_to_tuple(tile_or)
		or_H = or_tuple[0]
		or_V = or_tuple[1]
		or_D = or_tuple[2]
#		print(f"{tile_or}: {or_H}, {or_V}, {or_D}")

		temp_sheet = []
		for base_image in tilesheet_data:
			temp_image = Image.new('RGBA', (PPU, PPU))
			curr_image = Image.new('RGBA', (PPU, PPU))
			_copy_image_to(base_image, temp_image)
			_copy_image_to(base_image, curr_image)
			_apply_or(temp_image, curr_image, or_tuple)
			temp_sheet.append(curr_image)
		tilesheet_data2.append(temp_sheet)



def _apply_or(temp_image, curr_image, or_tuple):
	temp_pixel = temp_image.load()
	curr_pixel = curr_image.load()
	if or_tuple[2]:
		_apply_or_D(temp_pixel, curr_pixel)
		_copy_image_to(temp_image, curr_image)
	if or_tuple[1]:
		_apply_or_V(temp_pixel, curr_pixel)
		_copy_image_to(temp_image, curr_image)
	if or_tuple[0]:
		_apply_or_H(temp_pixel, curr_pixel)
		_copy_image_to(temp_image, curr_image)

def _apply_or_D(temp_pixel, curr_pixel):
	for x in range(PPU):
		for y in range(PPU):
			temp_pixel[x,y] = curr_pixel[y,x]

def _apply_or_V(temp_pixel, curr_pixel):
	for x in range(PPU):
		for y in range(PPU):
			temp_pixel[x,y] = curr_pixel[x,PPU-1-y]

def _apply_or_H(temp_pixel, curr_pixel):
	for x in range(PPU):
		for y in range(PPU):
			temp_pixel[x,y] = curr_pixel[PPU-1-x,y]





def _copy_image_to(temp_image, curr_image):
	image_w = temp_image.size[0]
	image_h = temp_image.size[1]
	temp_pixel = temp_image.load()
	curr_pixel = curr_image.load()
	for x in range(image_w):
		for y in range(image_h):
			curr_pixel[x,y] = temp_pixel[x,y]





def _or_to_tuple(tile_or):
	or_H = int((tile_or / 4 % 2)) == 1
	or_V = int((tile_or / 2 % 2)) == 1
	or_D = int((tile_or / 1 % 2)) == 1
	return [or_H, or_V, or_D]





def _debug_print_sheet(tile_or):
	print(f"Printing sheet {tile_or}...")

	tile_or_fin = (tile_or << 29)
	temp_level = []
	for h in range(DEBUG_H):
		temp_row = []
		for w in range(DEBUG_W):
			tile_id = w + h*DEBUG_W
			input_id = 1 + tile_id + tile_or_fin
			temp_row.append(input_id)
#			print(f"{input_id}, {tile_id}, {tile_or}")
		temp_level.append(temp_row)
	print_level_image(f"{tile_or}.png", [temp_level])





def get_tile_img(tilesheet_pixel, x, y):
	'''...'''
	global PPU

	tile_image = Image.new('RGBA', (PPU, PPU))
	tile_pixel = tile_image.load()

	base_pixel_x = x * PPU
	base_pixel_y = y * PPU
	for py in range(PPU):
		for px in range(PPU):
			tile_pixel[px,py] = tilesheet_pixel[px+base_pixel_x, py+base_pixel_y]
	return tile_image


def print_level_image(directory, list_tilelayer):
	'''...'''
	global PPU
	global layer_image
	global result_image

	b._print(f"Writing image at \"{directory}\"...")
#	print(directory)
#	print(list_tilelayer)

	num_layer = len(list_tilelayer)
	level_w = len(list_tilelayer[0][0])
	level_h = len(list_tilelayer[0])
	image_w = level_w * PPU
	image_h = level_h * PPU

#	print(f"{num_layer} layer")

	result_image = Image.new('RGBA', (image_w, image_h))
	result_pixel = result_image.load()

	for layer_id in range(num_layer):
		load_tiles(list_tilelayer[layer_id])
		apply_layer()
		b._print(f"~Layer {layer_id} printed~")

	result_image.save(directory)






def load_tiles(layer_data):
	'''...'''
	global PPU
	global layer_image
#	b._print("Setting tiles to layer...")

	level_w = len(layer_data[0])
	level_h = len(layer_data)
	image_w = level_w * PPU
	image_h = level_h * PPU
#	print(f"{level_w} x {level_h}\n")
	layer_image = Image.new('RGBA', (image_w, image_h))

	for j, row in enumerate(layer_data):
#		print(row)
		for i, col in enumerate(row):
#			print(layer_data[j][i])
			paste_tile(layer_data[j][i], i, j)

#	print(layer_data)



def paste_tile(input_id, pos_x, pos_y):
	'''...'''
	global PPU
	global tilesheet_data
	global layer_image

	if input_id <= 0:
		return

	tile_or = input_id >> 29
	tile_id = input_id - (tile_or << 29)
#	print(f"{input_id}, {tile_id}, {tile_or}")
	if input_id <= 0:
		print("Another Tilesheet detected!")
		tile_id -= 128*128
#		return

#	tile_pixel = tilesheet_data[tile_id-1].load()
	tile_pixel = __get_tile_pixel(tile_id, tile_or)
	layer_pixel = layer_image.load()

	base_pixel_x = pos_x * PPU
	base_pixel_y = pos_y * PPU
	for py in range(PPU):
		for px in range(PPU):
			layer_pixel[px+base_pixel_x, py+base_pixel_y] = tile_pixel[px,py]


def __get_tile_pixel(tile_id, tile_or):
	base_image = tilesheet_data[tile_id-1]
	temp_image = Image.new('RGBA', (PPU, PPU))
	curr_image = Image.new('RGBA', (PPU, PPU))
	_copy_image_to(base_image, temp_image)
	_copy_image_to(base_image, curr_image)
	_apply_or(temp_image, curr_image, _or_to_tuple(tile_or))
	return curr_image.load()









def apply_layer():
#	b._print("Pasting layer onto result...")
	global layer_image
	global result_image
	layer_pixel = layer_image.load()
	result_pixel = result_image.load()

	if DEBUG_IE:
		print( layer_image.size )
		print( result_image.size )

	DUMMY_COLOR = (150,200,250,50)
	for x in range(layer_image.size[0]):
		for y in range(layer_image.size[1]):
			alpha_value = layer_pixel[x,y][3]
#			print(layer_pixel[x,y][3])
#			result_pixel[x,y] = layer_pixel[x,y]
			if alpha_value == 0:
				if DEBUG_IE:
					result_pixel[x,y] = DUMMY_COLOR
				continue
			else:
				result_pixel[x,y] = layer_pixel[x,y]

#	result_image = layer_image














#==================================================#










# End of file
