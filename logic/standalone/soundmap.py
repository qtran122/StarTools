'''
Logic module for creating the "_soundmap" tilelayer
Procedure Overview:
 - Scan the pattern playdo
 - Scan the input level
 - Make temporary new layers for each active layer, using Sound ID instead
 - Condense said new layers into 1, based on "priority" (configured inside pattern XML)
  - Can condense based on layer order instead
 - Create a new tilelayer with the condensed layer

USAGE EXAMPLE:
	main_logic.logic(playdo, pattern)
'''

import logic.common.log_utils as log
import logic.common.file_utils as file_utils
import logic.common.tiled_utils as tiled_utils

#-----------------------------------------------------#
#-------------------- [Variables] --------------------#

# Name of the tilelayer that stores the soundmap
soundmap_name = "_soundmap"

# Opacity of the output layer; Only the bottommost value will take effect
output_opacity = "0.3"
output_opacity = "1.0"
output_opacity = "0.5"



#------------------------------------------------------------#
#-------------------- [Public Functions] --------------------#

def logic(playdo, pattern_playdo):
	'''Public function of the main logic'''
	log.Extra('')
	log.Must(f'  Creating the \"{soundmap_name}\" tilelayer from active tilelayers...')

	# Read pattern
	list_sound_id    = []
	list_sound_tuple = []
	list_sound_id, list_sound_tuple = GetSoundPatterns(pattern_playdo)

	# Read through the level, create a tempoorary layer for each active tilelayer
	level_w = playdo.map_width
	level_h = playdo.map_height
	log.Must(f'    Scanning through level - {level_w} x {level_h}')
	list_tiles2d  = playdo.GetAllTiles2d(True)
	list_soundmaps = []
	for tiles2d in list_tiles2d:
		blank2d = playdo.GetBlankTiles2d()
		list_soundmaps.append(scan_tiles2d(tiles2d, blank2d, level_w, level_h, list_sound_tuple))

	# Merge the multiple soundmaps into 1
	# NOTE Tiles at the top-left of soundmap XML has higher priority
	log.Must(f'    Condensing {len(list_soundmaps)} soundmap layers into 1...')
#	sound_tiles2d = CondenseSoundmapByLayer(list_soundmaps, playdo.GetBlankTiles2d())
	sound_tiles2d = CondenseSoundmapBySound(list_soundmaps, playdo.GetBlankTiles2d(), list_sound_id)

	# Create new layer; Default attributes is set only if no such layer exists prior
	has_prev_soundmap = ( soundmap_name in playdo.GetAllTileLayerNames() )
	new_layer = playdo.SetTiles2d(soundmap_name, sound_tiles2d)
	if not has_prev_soundmap: new_layer.set('opacity', output_opacity)

	log.Extra('')
	log.Must('  ----- End of All Procedures! -----')
	log.Must('')





#-------------------------------------------------------#
#-------------------- [Pattern XML] --------------------#

def GetSoundPatterns(pattern_playdo):
	'''
	 Returns 2 lists by checking through the pattern XML:
	  - 1 list for the soundmap tiles (sound ID)
	  - 1 list for the list of tiles, each sub-list will be represented by one soundmap tile
	'''
	log.Must(f'    Scanning pattern XML of soundmap...')
	tiles = pattern_playdo.GetTiles2d("tilesheet")
	sound = pattern_playdo.GetTiles2d("sound")

	# Create the lists to be returned
	list_sound_id    = []
	list_sound_tuple = []
	pattern_w = pattern_playdo.map_width
	pattern_h = pattern_playdo.map_height
	for row in range(pattern_h):
		for col in range(pattern_w):
			# Skip tile if it's empty, i.e. not corresponding to any sound ID
			sound_id = sound[row][col]
			if sound_id == 0: continue

			# If sound ID is not registered yet, register and point to a new list
			#  Otherwise point to the existing list
			tile_id = tiles[row][col]
			tuple_index = -1  # Reminder that [-1] means the last element
			if not sound_id in list_sound_id:
				list_sound_id.append(sound_id)
				list_sound_tuple.append( (sound_id, []) )
			else:
				tuple_index = list_sound_id.index(sound_id)
			list_sound_tuple[tuple_index][1].append(tile_id)

	# Log before rotating
	log.Must(f'      {len(list_sound_id)} Sound IDs detected')
	for i in range(len(list_sound_id)):
		if len(list_sound_tuple[i][1]) <= 1: continue
		log.Info(f'        {list_sound_tuple[i][0]} : {len(list_sound_tuple[i][1])} tiles')

	# Update new list to include all 8 orientations
	log.Must(f'      Flipping tile ID...')
	for index, tuple in enumerate(list_sound_tuple):
		new_list = ExtendTilesToAllOrientations(tuple[1])
		list_sound_tuple[index] = ( tuple[0], new_list )
	return list_sound_id, list_sound_tuple

def ExtendTilesToAllOrientations(list_tile_id):
	'''Return a new list with each ID flipped/rotated into all 8 orientations'''
	len_list = len(list_tile_id)
	for n in range(8):
		if n == 0: continue
		for i in range(len_list):
			new_id = list_tile_id[i] + n * 536870912
			list_tile_id.append(new_id)
	return list_tile_id





#--------------------------------------------------------------#
#-------------------- [Tile ID Conversion] --------------------#

def scan_tiles2d(scanned_tiles2d, soundmap, level_w, level_h, list_sound):
	'''Returns a tiles2D that basically converts scanned ID into sound ID'''
	for row in range(level_h):
		for col in range(level_w):
			tile_id = scanned_tiles2d[row][col]
			if tile_id == 0: continue
			for tuple in list_sound:
				if not tile_id in tuple[1]: continue
				soundmap[row][col] = tuple[0]
	return soundmap





#---------------------------------------------------------------#
#-------------------- [Soundmap Condensing] --------------------#

def CondenseSoundmapBySound(list_soundmaps, new_tiles2d, list_sound_id, reverse_order = False):
	'''Combine in the order of sound ID, e.g. top-left ID of pattern XML overrides tiles on the right'''
	log.Must(f'      Condense Method : By Sound')
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
#					if next_sound_index < curr_sound_index: continue
					if   not reverse_order and next_sound_index < curr_sound_index: continue
					elif     reverse_order and next_sound_index > curr_sound_index: continue

				new_tiles2d[row][col] = tile_id
	return new_tiles2d


def CondenseSoundmapByLayer(list_soundmaps, new_tiles2d):
	'''Combine in the order of layer, i.e. higher layer overwrites bottom layers'''
	log.Must(f'      Condense Method : By Layer')
	level_w = len(list_soundmaps[0][0])
	level_h = len(list_soundmaps[0])
	for soundmap in list_soundmaps:
		for row in range(level_h):
			for col in range(level_w):
				tile_id = soundmap[row][col]
				if tile_id == 0: continue
				new_tiles2d[row][col] = tile_id
	return new_tiles2d





#--------------------------------------------------#










# End of File