'''
Logic module that can
 - TBA

USAGE EXAMPLE:
	main_logic.logic(playdo)
'''

import logic.common.log_utils as log
import logic.common.file_utils as file_utils
import logic.common.tiled_utils as tiled_utils

#--------------------------------------------------#
'''Variables'''

soundmap_name = "_soundmap"    # Name of the tilelayer that stores the soundmap
output_opacity = "0.3"
output_opacity = "1.0"
output_opacity = "0.5"



#--------------------------------------------------#
'''Public Functions'''

def logic(playdo, pattern_playdo):
	'''TODO'''
	log.Must('')
	log.Must(f'Doing logic...')

	# Read pattern
	list_sound_id    = []
	list_sound_tuple = []
	list_sound_id, list_sound_tuple = GetSoundPatterns(pattern_playdo)

	# Read level
	sound_tiles2d = playdo.GetBlankTiles2d()
	list_tiles2d  = playdo.GetAllTiles2d(True)
	print(len(list_tiles2d))
	level_w = playdo.map_width
	level_h = playdo.map_height
	list_soundmaps = []
	for tiles2d in list_tiles2d:
#		sound_tiles2d = scan_tiles2d(tiles2d, sound_tiles2d, level_w, level_h, list_sound)
#		sound_tiles2d = scan_tiles2d(tiles2d, blank2d, level_w, level_h, list_sound)
		blank2d = playdo.GetBlankTiles2d()
		list_soundmaps.append(scan_tiles2d(tiles2d, blank2d, level_w, level_h, list_sound_tuple))

	# Merge the multiple soundmaps into 1
#	sound_tiles2d = MergeSoundmapByLayer(list_soundmaps, playdo.GetBlankTiles2d())
	sound_tiles2d = MergeSoundmapBySound(list_soundmaps, playdo.GetBlankTiles2d(), list_sound_id)

	# Create new layer, then set the default attributes
	has_prev_soundmap = ( soundmap_name in playdo.GetAllTileLayerNames() )
	new_layer = playdo.SetTiles2d(soundmap_name, sound_tiles2d)
	if not has_prev_soundmap: new_layer.set('opacity', output_opacity)

#	log.Extra('\n--------------------------------------------------')
	log.Must('\n--- Finished ! ---\n')



def GetSoundPatterns(pattern_playdo):
	tiles = pattern_playdo.GetTiles2d("tilesheet")
	sound = pattern_playdo.GetTiles2d("sound")
	pattern_w = pattern_playdo.map_width
	pattern_h = pattern_playdo.map_height
	list_sound_id    = []
	list_sound_tuple = []
	for row in range(pattern_h):
		for col in range(pattern_w):
			sound_id = sound[row][col]
			if sound_id == 0: continue
			tile_id = tiles[row][col]
			tuple_index = -1
			if not sound_id in list_sound_id:
				list_sound_id.append(sound_id)
				list_sound_tuple.append( (sound_id, []) )
			else:
				tuple_index = list_sound_id.index(sound_id)
			list_sound_tuple[tuple_index][1].append(tile_id)

	for index, tuple in enumerate(list_sound_tuple):
#		tuple[1] = ExtendTilesToAllOrientations(tuple[1])
		new_list = ExtendTilesToAllOrientations(tuple[1])
		list_sound_tuple[index] = ( tuple[0], new_list )

	return list_sound_id, list_sound_tuple



def GetSoundPatterns_deprec(pattern_playdo):
	list_pattern  = pattern_playdo.GetAllTiles2d()
	pattern_w = pattern_playdo.map_width
	pattern_h = pattern_playdo.map_height
	list_sound_id    = []
	list_sound_tuple = []
	for pattern in list_pattern:
		# Skip if the layer does not have a sound tile properly assigned
		sound_id = pattern[0][0]
		if sound_id == 0: continue

		# TBA
		new_list = []
#		sound_tiles2d = scan_tiles2d(tiles2d, sound_tiles2d)
		for row in range(pattern_h):
			for col in range(pattern_w):
				if row == 0 and col == 0: continue
				if pattern[row][col] == 0: continue
				for i in range(8):
					tile_id = pattern[row][col]
					new_list.append(tile_id + i * 536870912)  # For all 8 orientation
#				new_list.append(pattern[row][col])
		list_sound_id.append(sound_id)
		list_sound_tuple.append( (sound_id, new_list) )
#	print(dict)
#	return

	return list_sound_id, list_sound_tuple

def ExtendTilesToAllOrientations(list_tile_id):
	len_list = len(list_tile_id)
	for n in range(8):
		if n == 0: continue
		for i in range(len_list):
			new_id = list_tile_id[i] + n * 536870912
			list_tile_id.append(new_id)
	return list_tile_id




def MergeSoundmapBySound(list_soundmaps, new_tiles2d, list_sound_id, reverse_order = False):
	'''Combine in the order of sound id'''
	level_w = len(list_soundmaps[0][0])
	level_h = len(list_soundmaps[0])
	for soundmap in list_soundmaps:
		for row in range(level_h):
			for col in range(level_w):
				tile_id = soundmap[row][col]
				if tile_id == 0: continue

				curr_sound_id = new_tiles2d[row][col]
				if curr_sound_id != 0:
					curr_sound_index = list_sound_id.index(curr_sound_id)
					next_sound_index = list_sound_id.index(tile_id)
					if next_sound_index < curr_sound_index: continue

				new_tiles2d[row][col] = tile_id
	return new_tiles2d


def MergeSoundmapByLayer(list_soundmaps, new_tiles2d):
	'''Combine in the order of layer, i.e. higher layer overwrites bottom layers'''
	level_w = len(list_soundmaps[0][0])
	level_h = len(list_soundmaps[0])
	for soundmap in list_soundmaps:
		for row in range(level_h):
			for col in range(level_w):
				tile_id = soundmap[row][col]
				if tile_id == 0: continue
				new_tiles2d[row][col] = tile_id
	return new_tiles2d




def scan_tiles2d(scanned_tiles2d, soundmap, level_w, level_h, list_sound):
	'''This one scan it based on pattern layer order'''
	x=1

def scan_tiles2d(scanned_tiles2d, soundmap, level_w, level_h, list_sound):
	'''This one scan it based on XML layer order'''
	for row in range(level_h):
		for col in range(level_w):
			tile_id = scanned_tiles2d[row][col]
			if tile_id == 0: continue
			for tuple in list_sound:
				if not tile_id in tuple[1]: continue
				soundmap[row][col] = tuple[0]
	return soundmap




#--------------------------------------------------#
'''General Utility, to be relocated?'''

def _Indent(s, min_len):
	'''Return the same string, with consistent spacing added to the end'''
	return ( s + ' ' * (min_len-len(s)) )

def _FormatNumS2TU(num_in_str):
	'''Shortcut, for converting string (coordinates measured in pixels) intoto Tiled units'''
	if num_in_str == None: return ''
	return str(int( round(float(num_in_str))/16 ))





#--------------------------------------------------#










# End of File