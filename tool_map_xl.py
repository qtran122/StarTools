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
from openpyxl.styles import PatternFill, Alignment, Font

#---------------------------------------------------------------------#
#-------------------- [Adjustable Configurations] --------------------#

# In-editor object layers for nodes & routes
level_name_input = "map_simplified.xml"
path_t           =  "/Users/Jimmy/Desktop/whale_map.xlsx"      # TY's path
path_q           = r"C:\Users\qtran\Desktop\whale_map.xlsx"    # Quang's path
filepath_output  = path_q

# XML Configurations
layer_name = "BG"

# Spreadsheet Format
column_width = 30    # (in pixels) Width of each column in the spreadsheet

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
	logic(playdo, filepath_output)

#------------------------------------------------------------#
#-------------------- [Public Functions] --------------------#

def logic(playdo, filepath_output):
	'''
	 Reads the XML and output a XLSX spreadsheet in the designated filepath
	'''
	log.Must(f'  Reading the map data...')

	# Map data
	num_row = playdo.map_height
	num_col = playdo.map_width
	min_x = num_col+1
	min_y = num_row+1
	max_x = 0
	max_y = 0

	# Initialise the array
	empty_id = -1
	map_simple = [[empty_id for _ in range(num_col)] for _ in range(num_row)]

	# Check each cell in Tiled
	# The color data and max/min range is recorded, latter is shown as message
	tiles2d = playdo.GetTiles2d(layer_name)
	list_key = list(dict_id_to_hex.keys())
	for i in range(num_row):
		for j in range(num_col):
			if not tiles2d[i][j] in list_key: continue
			if min_x > j: min_x = j
			if min_y > i: min_y = i
			if max_x < j: max_x = j + 1
			if max_y < i: max_y = i + 1
			for key, value in dict_id_to_hex.items():
				if tiles2d[i][j] != key: continue
				map_simple[i][j]  = list_key.index(key)
	log.Must(f"   Map W: {num_col}, Map H: {num_row}")
	log.Must(f"    Min X: {min_x}, Min Y: {min_y}")
	log.Must(f"    Max X: {max_x}, Max Y: {max_y}")

	wb = openpyxl.Workbook()
	ws = wb.active

	# Create the new XLSX file with all the colors
	ExportXlsx(ws, map_simple, min_x, min_y, max_x, max_y)
	AddFreezeLabel(ws, max_y - min_y) # Add a column & row to the left & top side respectively
	ResizeColumns(ws)                 # Resize all columns to smaller width

	# Save spreadsheet to filepath
	log.Must('')
	log.Must(f"  Exporting at : f{filepath_output}")
	log.Must(f"   Rows: {ws.max_row}, Columns: {ws.max_column}")
	wb.save(filepath_output)

	log.Must('')



#------------------------------------------------------------#
#-------------------- [Helper Functions] --------------------#

def AddFreezeLabel(ws, num_rows):
	'''
	  Add Number & Syntax to the top row & left column, then freeze them
	'''

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



def ExportXlsx(ws, map_simple, min_x, min_y, max_x, max_y):
	'''
	 This exports the XLSX based on the recorded coloring data
	'''
	# Creates an array for just the color hex values
	list_fill = []
	for key, value in dict_id_to_hex.items():
		list_fill.append( PatternFill(start_color = value, end_color = value, fill_type="solid") )
	list_fill.append( PatternFill(fill_type=None) )

	# Enter data to corresponding cells based on map data
	num_row = len(map_simple)
	num_col = len(map_simple[0])
	for row in range(num_row):
		if row < min_y: continue
		for col in range(num_col):
			if col < min_x: continue
			if map_simple[row][col] < 0: continue
			new_x = col + 1 - min_x
			new_y = row + 1 - min_y
			fill_id = map_simple[row][col]
			ws.cell(row = new_y, column = new_x, value = " ").fill = list_fill[fill_id]

	# Set the default BG Color for the "unedited cells" and "out of bound cells"
	bg_fill    = PatternFill( start_color = bg_hex,     end_color = bg_hex,     fill_type="solid" )
	black_fill = PatternFill( start_color = unused_hex, end_color = unused_hex, fill_type="solid" )
	for row in ws.iter_rows(min_row = 1, max_row = max_y+1):
		for cell in row:
			if cell.fill.fill_type in (None, "none"): cell.fill = bg_fill
	for row in ws.iter_rows(min_row = max_y-min_y+2, max_row = 1000):	# NOTE Somehow this line crops sheet to 273 rows
#	for row in ws.iter_rows(min_row = max_y-min_y+1, max_row = max_y-min_y+1):
		for cell in row: cell.fill = black_fill
#	for row in ws.iter_rows(min_row = max_y-min_y+2, max_row = 1000):
#		for cell in row: cell.fill = black_fill

def PrintInConsole(map_simple, empty_id):
	'''
	 Prints the map data on console instead
	 For debugging, and in case want to switch over to the "copy-paste plain text" method
	'''
	num_row = len(map_simple)
	num_col = len(map_simple[0])
	print_msg = ""
	for i in range(num_row):
		for j in range(num_col):
			if map_simple[i][j] == empty_id: print_msg += " "
#			else:                            print_msg += "x"
#			else:                            print_msg += map_simple[i][j][0]
#			else:                            print_msg += map_simple[i][j] // 10
			else:                            print_msg += f"{map_simple[i][j]}"
			print_msg += " "
		print_msg += "\n"
	log.Must(print_msg)



def ResizeColumns(ws):
	'''
	 Resize the column width so it's easier to fit into the screen
	'''
	for col in ws.columns:
		column_letter = col[0].column_letter
		ws.column_dimensions[column_letter].width = column_width / 7    # Function uses "character" as measurement, each ~7px





#--------------------------------------------------#

main()










# End of File