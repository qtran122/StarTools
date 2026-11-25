'''
Command-Line Tool for reading a simplified map XML, then creates a XLSX file at desktop
The new XLSX contains the coloring data from the XML, and can then be imported into Google Sheet
	
USAGE EXAMPLE:
	cd /Users/Jimmy/20-GitHub/StarTools
	clear; python tool_map_xl.py
'''
import argparse
import logic.common.log_utils as log
import logic.common.file_utils as file_utils
import logic.common.level_playdo as play

from pathlib import Path
import openpyxl
from openpyxl.styles import PatternFill, Alignment, Font, Border, Side
import subprocess
import time
import os
from datetime import datetime

#---------------------------------------------------------------------#
#-------------------- [Adjustable Configurations] --------------------#

# In-editor object layers for nodes & routes
level_name_input = "map_simplified.xml"
level_name_input = "map_planning.xml"
level_name_input = "map_export_xlsx.xml"
path_t           =  "/Users/Jimmy/Desktop/whale_map.xlsx"      # TY's path
path_q           = r"C:\Users\qtran\Desktop\whale_map.xlsx"    # Quang's path
filepath_output  = path_q

mode_export = 1    # 1: Export color in XLSX, 2: Export name in TXT

# XML Configurations
layer_name_color   = "FILL"
layer_name_icon    = "ICON"
layer_name_biome   = "_room_letter"
layer_name_number  = "_room_num_all"
layer_name_border1 = "_map_grid_LR"
layer_name_border2 = "_map_grid_DU"

# Spreadsheet Format
column_width = 30    # (in pixels) Width of each column in the spreadsheet

grid_thickness = 'thick'   # 'thin' 'thick'
grid_color_1   = 'FFFFFF' # Wall
grid_color_2   = '888888' # Door
dict_grid_to_id = {
	"wall_l": 400+1,
	"door_l": 528+1,
	"wall_u": 273+1,
	"door_u": 274+1,
}

room_color_save = '00FFFF' # Save rooms - Cyan
room_color_warp = '32CD32' # Warp rooms - Lime Green
dict_room_to_id = {
	"warp": [145+1,],
	"save": [144+1,146+1,148+1,149+1,],
}

bg_hex     = "0076a3"    # dict_id_to_hex[411+1]
unused_hex = "000000"
dict_id_to_hex = {
	 16+1:"6858d0",
	 17+1:"b961e9",
	 18+1:"f8ca34",
	 19+1:"34d9c1",
	 20+1:"80c84f",
	 21+1:"5299f6",
	 22+1:"ef71cd",
	 23+1:"c78855",
	 24+1:"eb2a67",
	 25+1:"ff0000",

	154+1:"444444",
	155+1:"868686",
	156+1:"c4c4c4",
	157+1:"ffffff",
	158+1:"fefeff",
	159+1:"fdffff",

	283+1:"1b1464",
	284+1:"440e62",
	410+1:"00746b",
	411+1:"0076a3",
	412+1:"004a80",
	538+1:"8c6239",
	539+1:"362f2d",
	540+1:"7b0046",
}

dict_id_to_num    = {}
dict_id_to_letter = {}




#------------------------------------------------#
#-------------------- [Main] --------------------#

arg_description = 'Process a simplified map XML and export a XLSX with colors'
arg_help2 = 'Controls the amount of information displayed to screen. 0 = nearly silent, 2 = verbose'

def main():
	# Use argparse to get the filename & other optional arguments from the command line
	parser = argparse.ArgumentParser(description = arg_description)
	parser.add_argument('--v', type=int, choices=[0, 1, 2], default=1, help = arg_help2)
	args = parser.parse_args()
	log.SetVerbosityLevel(args.v)

	# Check if address exists, exit and do nothing if so
	output_folder = filepath_output
	if '/'  in output_folder: output_folder = output_folder.replace(filepath_output.split('/')[-1], "")
	if '\\' in output_folder: output_folder = output_folder.replace(filepath_output.split('\\')[-1], "")
#	log.Must(f"  Output: {output_folder}\n")
	if not Path(output_folder).exists():
		log.Must(f"  Output: {output_folder}\n")
		log.Must( "  Output path does not exist!")
		log.Must( "   Make sure you are setting the correct path inside the .py file")
		log.Must("")
		return

	# Use a playdo to read/process the XML
	playdo = play.LevelPlayDo(file_utils.GetFullLevelPath(level_name_input))
	if   mode_export == 1: ExportMapColorInXlsx(playdo, filepath_output)
	elif mode_export == 2: ExportRoomNamesInTxt(playdo)
	else: log.Must("[EROOR] - Export Mode invalid, please go to the .py file to change")

#------------------------------------------------------------#
#-------------------- [Public Functions] --------------------#

def ExportMapColorInXlsx(playdo, filepath_output):
	'''
	 Reads the XML and output a XLSX spreadsheet in the designated filepath
	'''
	log.Must(f'  Exporting XLSX from map data - {playdo.map_width} x {playdo.map_height}')
	wb = openpyxl.Workbook()
	ws = wb.active

	# Create the new XLSX file with all the colors
	AddColorToXlsx(ws, playdo)
	AddGridlinesToXlsx(ws, playdo)        # Add white grid lines for each room
	AddFreezeLabel(ws, playdo.map_height) # Add a column & row to the left & top side respectively
	ResizeColumns(ws)                     # Resize all columns to smaller width

	# Save spreadsheet to filepath
	log.Must('')
	log.Must(f"  Exporting at : f{filepath_output}")
	log.Must(f"   Rows: {ws.max_row}, Columns: {ws.max_column}")
	wb.save(filepath_output)

	log.Must('')



#---------------------------------------------------------#
#-------------------- [TXT Functions] --------------------#

def ExportRoomNamesInTxt(playdo):
	'''
	 Generate a TXT file that contains the room names at corresponding cell position
	 The entire content can be copy-pasted directly onto the spreadsheet, starting at top-left [B2]
	'''
	num_row = playdo.map_height
	num_col = playdo.map_width
	empty_id = -1

	# Initialise the array
	map_output = [[empty_id for _ in range(num_col)] for _ in range(num_row)]

	# Set up the dictionary : TileID -> Number, TileID -> Biome Letter
	MakeDictIdToNum()
#	for key, value in dict_id_to_num.items(): print(f"{key} : {value}")
#	for key, value in dict_id_to_letter.items(): print(f"{key} : {value}")

	# Read map data into string
	tiles2d_letter = playdo.GetTiles2d(layer_name_biome)
	tiles2d_number = playdo.GetTiles2d(layer_name_number)
	for i in range(num_row):
		for j in range(num_col):
			if     tiles2d_number[i][j] == 0:              continue
			if not tiles2d_number[i][j] in dict_id_to_num: continue
			map_output[i][j]  = dict_id_to_letter[tiles2d_letter[i][j]]
			map_output[i][j] += dict_id_to_num[   tiles2d_number[i][j]]
	log.Must(f"  Map W: {num_col}, Map H: {num_row}")
	log.Must("")

	# Export into TXT file
	_ExportMapToString(map_output, empty_id, "   ", '\t', False)

def _ExportMapToString(map_simple, empty_id, empty_char = " ", separator = " ", print_in_console = True):
	'''
	 Prints the map data on console instead
	 For debugging, and in case want to switch over to the "copy-paste plain text" method
	'''
	num_row = len(map_simple)
	num_col = len(map_simple[0])
	log.Must(f"  Exporting room names in plain text: {num_col}x{num_row}...")
	log.Must(f"")

	# Generate the string here
	print_msg = f"[B2] Copy-Paste to here ; Last Exported at {datetime.now().replace(microsecond=0)}"
	for i in range(num_row):
		for j in range(num_col):
			if map_simple[i][j] == empty_id: print_msg += empty_char
#			else:                            print_msg += "x"
#			else:                            print_msg += map_simple[i][j][0]
#			else:                            print_msg += map_simple[i][j] // 10
			else:                            print_msg += f"{map_simple[i][j]}"
			print_msg += separator
		print_msg += "\n"
	
	# Output to either Console or in a TXT file
	# NOTE Make sure to close the app first before re-running, otherwise the TXT won't update
	if print_in_console: log.Must(print_msg)
	log.Must(f"  Opening the generated TXT automatically...")
	filepath = "map_exported.txt"
#	filepath = input folder + "map_exported.rxt"
	with open(filepath, "w", encoding="utf-8") as file: file.write(print_msg)
	subprocess.run(["open", "-a", "TextEdit", filepath])
	time.sleep(1)
	os.remove(filepath)
	log.Must(f"   Generated TXT deleted")
	log.Must(f"")



def MakeDictIdToNum():

	# Tile ID to Room Number
	global dict_id_to_num
	START_ID = 789+1
	WIDTH = 5
	for i in range(60):
		tile_id = START_ID + i % WIDTH + (i // WIDTH) * 128
		num_string = ""
		if i+1 < 10: num_string = "0"
		num_string += f"{i+1}"
		if i == 59: num_string = "00"
		dict_id_to_num[tile_id] = num_string
	dict_id_to_num[0] = "  "

	# Special Cases
	dict_id_to_num[1936+1] = "-natty"

	# Tile ID to Biome Letter
	global dict_id_to_letter
	START_ID = 784+1
	WIDTH = 5
	for i in range(26):
		tile_id = START_ID + i % WIDTH + (i // WIDTH) * 128
		letter_string = chr(ord('A') + i)
		dict_id_to_letter[tile_id] = letter_string
	dict_id_to_letter[0] = " "








#----------------------------------------------------------#
#-------------------- [XLSX Functions] --------------------#

def AddColorToXlsx(ws, playdo):
	'''
	 This exports the XLSX based on the recorded coloring data
	'''
	log.Must('  Adding color to XLSX...')
	num_row = playdo.map_height
	num_col = playdo.map_width

	# Creates an array for just the color hex values
	list_key = list(dict_id_to_hex.keys())
	dict_id_to_fill = {}
	for key, value in dict_id_to_hex.items(): dict_id_to_fill[key] = PatternFill(start_color = value, end_color = value, fill_type="solid")
	for ID in dict_room_to_id["save"]: dict_id_to_fill[ID] = PatternFill(start_color = room_color_save, end_color = room_color_save, fill_type="solid")
	for ID in dict_room_to_id["warp"]: dict_id_to_fill[ID] = PatternFill(start_color = room_color_warp, end_color = room_color_warp, fill_type="solid")

	# Fill color to the XLSX
	tiles2d = playdo.GetTiles2d(layer_name_color)
	if tiles2d == None: log.Must(f"  [ERROR] - Layer {layer_name_color} not found!"); return
	for i in range(num_row):
		for j in range(num_col):
#			if not tiles2d[i][j] in list_key: continue
			if not tiles2d[i][j] in dict_id_to_fill.keys(): continue
#			hex = dict_id_to_hex[tiles2d[i][j]]
#			fill = PatternFill(start_color = hex, end_color = hex, fill_type="solid")
			fill = dict_id_to_fill[tiles2d[i][j]]
			ws.cell(row = i+1, column = j+1, value = " ").fill = fill

	# Special case - Warp and Save room
	tiles2d_icon = playdo.GetTiles2d(layer_name_icon)
	for i in range(num_row):
		if tiles2d_icon == None: log.Must("   Icon layer not found, omitting check..."); break
		for j in range(num_col):
			if tiles2d[i][j] == 0: continue                          # Quick filter
			if not tiles2d[i][j] in dict_id_to_fill.keys(): continue # Safety check
			fill = dict_id_to_fill[tiles2d[i][j]]
			ws.cell(row = i+1, column = j+1, value = " ").fill = fill

	# Set the default BG Color for the "unedited cells" and "out of bound cells"
	bg_fill    = PatternFill( start_color = bg_hex,     end_color = bg_hex,     fill_type="solid" )
	black_fill = PatternFill( start_color = unused_hex, end_color = unused_hex, fill_type="solid" )
	for row in ws.iter_rows(min_row = 1, max_row = num_row+1):
		for cell in row:
			if cell.fill.fill_type in (None, "none"): cell.fill = bg_fill
	for row in ws.iter_rows(min_row = num_row+2, max_row = 1000):	# NOTE Somehow this line crops sheet to 273 rows
#	for row in ws.iter_rows(min_row = max_y-min_y+1, max_row = max_y-min_y+1):
		for cell in row: cell.fill = black_fill
#	for row in ws.iter_rows(min_row = max_y-min_y+2, max_row = 1000):
#		for cell in row: cell.fill = black_fill





def AddGridlinesToXlsx(ws, playdo):
	'''
	 TODO
	'''
	log.Must('  Adding gridlines to XLSX...')
	num_row = playdo.map_height
	num_col = playdo.map_width

	# Initialise the array
	wall_gridline = Side(style=grid_thickness, color=grid_color_1)
	door_gridline = Side(style=grid_thickness, color=grid_color_2)

	# Read map data into string
	tiles2d_lr = playdo.GetTiles2d(layer_name_border1)
	tiles2d_du = playdo.GetTiles2d(layer_name_border2)
	if tiles2d_lr == None or tiles2d_du == None:
		log.Must('   Grid layers not found, skipping operation...')
		return
	for i in range(num_row):
		for j in range(num_col):
			gridline_l = None
			gridline_u = None
			if tiles2d_lr[i][j] == dict_grid_to_id["wall_l"]: gridline_l = wall_gridline
			if tiles2d_lr[i][j] == dict_grid_to_id["door_l"]: gridline_l = door_gridline
			if tiles2d_du[i][j] == dict_grid_to_id["wall_u"]: gridline_u = wall_gridline
			if tiles2d_du[i][j] == dict_grid_to_id["door_u"]: gridline_u = door_gridline
			ws.cell(row = i+1, column = j+1).border = Border(left=gridline_l, top=gridline_u)



def AddFreezeLabel(ws, num_rows):
	'''
	  Add Number & Syntax to the top row & left column, then freeze them
	'''
	log.Must('  Adding frozen first row & column to XLSX...')
	ws.insert_cols(idx=1)
	ws.insert_rows(idx=1)

	# Top-row
	num = -1
	for col in ws.columns:
		column_letter = col[0].column_letter
		cell = ws[f"{column_letter}1"]
		cell.value     = num
		cell.font      = Font(bold=True, underline="single")
		cell.alignment = Alignment(horizontal="center", vertical="center")
		num += 1

	# Add number in left-column
	for i in range(num_rows+1):
		cell = ws[f"A{i+1}"]
		cell.value     = num_rows - i
		cell.font      = Font(bold=True, underline="single")
		cell.alignment = Alignment(horizontal="center", vertical="center")

	# Freeze first row and column
	ws[f"A1"] = ""
	ws.freeze_panes = "B2"



def ResizeColumns(ws):
	'''
	 Resize the column width so it's easier to fit into the screen
	'''
	log.Must(f'  Resizing each column to be {column_width} pixels...')
	for col in ws.columns:
		column_letter = col[0].column_letter
		ws.column_dimensions[column_letter].width = column_width / 7    # Function uses "character" as measurement, each ~7px





#--------------------------------------------------#

main()










# End of File